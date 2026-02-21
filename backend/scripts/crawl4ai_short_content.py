#!/usr/bin/env python3
"""Re-verify short-content soft 404 resources using Crawl4AI browser rendering.

These are pages that returned <500 chars via HTTP but may be JS-heavy sites
that render properly in a real browser.

Usage:
    python scripts/crawl4ai_short_content.py --dry-run
    python scripts/crawl4ai_short_content.py --apply
"""

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

from app.services.soft_404 import detect_soft_404

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
except ImportError:
    print("crawl4ai not installed. Run: uv pip install crawl4ai")
    sys.exit(1)


def get_prod_engine():
    """Get production database engine via Railway CLI."""
    try:
        result = subprocess.run(
            ["railway", "variables", "--service", "Postgres", "--json"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            db_url = data.get("DATABASE_PUBLIC_URL", "")
            if db_url:
                return create_engine(db_url, pool_pre_ping=True)
    except Exception as e:
        print(f"Failed to get Railway DB URL: {e}")

    print("ERROR: Could not connect to production database")
    sys.exit(1)


def get_short_content_resources(eng) -> list[dict]:
    """Fetch short-content soft 404 resources."""
    with eng.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT id, title, website, link_flagged_reason
                FROM resources
                WHERE link_flagged_reason LIKE 'Soft 404:%%'
                  AND (link_flagged_reason ILIKE '%%short%%' OR link_flagged_reason ILIKE '%%tiny%%')
                  AND status = 'NEEDS_REVIEW'
                ORDER BY title
            """)
        ).all()

    return [{"id": str(r[0]), "title": r[1], "website": r[2], "reason": r[3]} for r in rows]


async def verify_url(crawler, url: str) -> dict:
    """Verify a single URL with browser rendering."""
    config = CrawlerRunConfig(
        wait_until="networkidle",
        word_count_threshold=50,
    )

    try:
        result = await crawler.arun(url=url, config=config)

        if result.success:
            title = result.metadata.get("title", "")
            markdown = result.markdown or ""
            final_url = getattr(result, "url", url)

            soft_404 = detect_soft_404(
                content=markdown,
                original_url=url,
                final_url=final_url,
                title=title,
            )

            return {
                "url": url,
                "status": "soft_404" if soft_404["is_soft_404"] else "active",
                "title": title,
                "content_length": len(markdown),
                "reason": soft_404.get("reason") if soft_404["is_soft_404"] else None,
            }
        else:
            return {
                "url": url,
                "status": "failed",
                "error": result.error_message,
                "content_length": 0,
            }
    except Exception as e:
        return {
            "url": url,
            "status": "error",
            "error": str(e),
            "content_length": 0,
        }


async def verify_batch(urls: list[str], concurrency: int = 5) -> list[dict]:
    """Verify a batch of URLs with browser rendering."""
    browser_config = BrowserConfig(
        headless=True,
        browser_type="firefox",
    )

    results = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for i in range(0, len(urls), concurrency):
            batch = urls[i : i + concurrency]
            batch_num = i // concurrency + 1
            total_batches = (len(urls) + concurrency - 1) // concurrency
            print(f"\n  Batch {batch_num}/{total_batches} ({len(batch)} URLs)...")

            tasks = [verify_url(crawler, url) for url in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            # Show progress
            for r in batch_results:
                status_icon = {"active": "✓", "soft_404": "⚠", "failed": "✗", "error": "✗"}
                icon = status_icon.get(r["status"], "?")
                print(f"    {icon} {r['url'][:60]} [{r['status']}] ({r['content_length']} chars)")

            if i + concurrency < len(urls):
                await asyncio.sleep(1)

    return results


def apply_results(eng, resources: list[dict], results: list[dict], dry_run: bool = True):
    """Apply verification results to database."""
    url_to_result = {r["url"]: r for r in results}

    active_ids = []
    still_dead_ids = []
    failed_ids = []

    for resource in resources:
        result = url_to_result.get(resource["website"])
        if not result:
            continue

        if result["status"] == "active":
            active_ids.append(resource["id"])
        elif result["status"] == "soft_404":
            still_dead_ids.append(resource["id"])
        else:
            failed_ids.append(resource["id"])

    print("\n  Results:")
    print(f"    Active (recovered): {len(active_ids)}")
    print(f"    Confirmed dead: {len(still_dead_ids)}")
    print(f"    Failed to check: {len(failed_ids)}")

    if dry_run:
        print(f"\n  [DRY RUN] Would clear flags on {len(active_ids)} active resources")
        print(f"  [DRY RUN] Would mark {len(still_dead_ids)} as inactive")
        return

    now = datetime.now(UTC)

    with eng.begin() as conn:
        if active_ids:
            conn.execute(
                text("""
                    UPDATE resources
                    SET status = 'active',
                        link_flagged_reason = NULL,
                        link_health_score = 0.9,
                        link_checked_at = :now,
                        updated_at = :now
                    WHERE id::text = ANY(:ids)
                """),
                {"ids": active_ids, "now": now},
            )
            print(f"  Cleared flags on {len(active_ids)} active resources")

        if still_dead_ids:
            conn.execute(
                text("""
                    UPDATE resources
                    SET status = 'inactive',
                        link_health_score = 0.0,
                        link_checked_at = :now,
                        updated_at = :now
                    WHERE id::text = ANY(:ids)
                """),
                {"ids": still_dead_ids, "now": now},
            )
            print(f"  Marked {len(still_dead_ids)} resources inactive")

        # Leave failed ones as NEEDS_REVIEW for manual check
        if failed_ids:
            print(f"  Left {len(failed_ids)} failed checks as NEEDS_REVIEW")


def main():
    parser = argparse.ArgumentParser(description="Re-verify short-content soft 404s with Crawl4AI")
    parser.add_argument("--apply", action="store_true", help="Apply changes to DB")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrent browser tabs")
    parser.add_argument("--output", type=str, help="Save raw results to JSON")
    args = parser.parse_args()

    dry_run = not args.apply or args.dry_run

    eng = get_prod_engine()
    resources = get_short_content_resources(eng)
    print(f"Found {len(resources)} short-content soft 404 resources")

    if not resources:
        print("Nothing to verify!")
        return

    urls = [r["website"] for r in resources if r["website"]]
    print(f"Verifying {len(urls)} URLs with browser rendering...")

    results = asyncio.run(verify_batch(urls, args.concurrency))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nRaw results saved to {args.output}")

    apply_results(eng, resources, results, dry_run)

    if dry_run:
        print("\n⚠ DRY RUN - no changes made. Use --apply to commit.")


if __name__ == "__main__":
    main()
