#!/usr/bin/env python3
"""Re-check short-content soft 404 resources with async HTTP.

Uses aiohttp with a real browser User-Agent and follows redirects
to determine if these pages are truly dead or just JS-heavy.

Usage:
    python scripts/recheck_short_content.py --dry-run
    python scripts/recheck_short_content.py --apply
"""

import asyncio
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import aiohttp
from sqlalchemy import create_engine, text

from app.services.soft_404 import detect_soft_404

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

TIMEOUT = aiohttp.ClientTimeout(total=15)


def get_prod_engine():
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
        print(f"Failed: {e}")
    sys.exit(1)


def get_resources(eng) -> list[dict]:
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


async def check_url(session: aiohttp.ClientSession, url: str) -> dict:
    """Check a URL with a real browser user agent."""
    try:
        async with session.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            ssl=False,
            headers={"User-Agent": USER_AGENT},
        ) as resp:
            content = await resp.text(errors="replace")
            final_url = str(resp.url)

            # Get page title
            title = ""
            if "<title>" in content.lower():
                start = content.lower().find("<title>") + 7
                end = content.lower().find("</title>", start)
                if end > start:
                    title = content[start:end].strip()

            soft_404 = detect_soft_404(
                content=content,
                original_url=url,
                final_url=final_url,
                title=title,
            )

            return {
                "url": url,
                "final_url": final_url,
                "http_status": resp.status,
                "content_length": len(content),
                "title": title[:100],
                "is_soft_404": soft_404["is_soft_404"],
                "reason": soft_404.get("reason"),
                "status": "soft_404" if soft_404["is_soft_404"] else "active",
            }
    except TimeoutError:
        return {"url": url, "status": "timeout", "content_length": 0}
    except aiohttp.ClientError as e:
        return {"url": url, "status": "error", "error": str(e)[:100], "content_length": 0}
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)[:100], "content_length": 0}


async def check_all(urls: list[str], concurrency: int = 20) -> list[dict]:
    """Check all URLs concurrently."""
    sem = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:

        async def bounded_check(url):
            async with sem:
                return await check_url(session, url)

        tasks = [bounded_check(url) for url in urls]
        return await asyncio.gather(*tasks)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=str, help="Save results JSON")
    args = parser.parse_args()

    dry_run = not args.apply or args.dry_run

    eng = get_prod_engine()
    resources = get_resources(eng)
    print(f"Found {len(resources)} short-content resources to re-check")

    if not resources:
        return

    urls = [r["website"] for r in resources if r["website"]]
    print(f"Checking {len(urls)} URLs...")

    results = asyncio.run(check_all(urls))

    # Map results
    url_map = {r["url"]: r for r in results}

    active_ids = []
    dead_ids = []
    error_ids = []

    for resource in resources:
        result = url_map.get(resource["website"])
        if not result:
            continue

        icon = {"active": "✓", "soft_404": "⚠", "timeout": "⏱", "error": "✗"}.get(result["status"], "?")
        clen = result.get("content_length", 0)
        print(f"  {icon} {resource['title'][:55]:55s} | {clen:>6} chars | {result['status']}")

        if result["status"] == "active":
            active_ids.append(resource["id"])
        elif result["status"] == "soft_404":
            dead_ids.append(resource["id"])
        else:
            error_ids.append(resource["id"])

    print("\nSummary:")
    print(f"  Active (recovered): {len(active_ids)}")
    print(f"  Confirmed dead:     {len(dead_ids)}")
    print(f"  Errors/timeouts:    {len(error_ids)}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to {args.output}")

    if dry_run:
        print("\n⚠ DRY RUN. Use --apply to commit changes.")
        return

    now = datetime.now(UTC)

    with eng.begin() as conn:
        if active_ids:
            conn.execute(
                text("""
                UPDATE resources
                SET status = 'active', link_flagged_reason = NULL,
                    link_health_score = 0.9, link_checked_at = :now, updated_at = :now
                WHERE id::text = ANY(:ids)
            """),
                {"ids": active_ids, "now": now},
            )
            print(f"  ✓ Cleared flags on {len(active_ids)} recovered resources")

        if dead_ids:
            conn.execute(
                text("""
                UPDATE resources
                SET status = 'inactive', link_health_score = 0.0,
                    link_checked_at = :now, updated_at = :now
                WHERE id::text = ANY(:ids)
            """),
                {"ids": dead_ids, "now": now},
            )
            print(f"  ✗ Marked {len(dead_ids)} resources inactive")

        if error_ids:
            print(f"  ? Left {len(error_ids)} error/timeout resources as NEEDS_REVIEW")


if __name__ == "__main__":
    main()
