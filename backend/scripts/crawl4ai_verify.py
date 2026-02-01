#!/usr/bin/env python3
"""Verify and update resources using Crawl4AI.

Uses Crawl4AI to:
1. Visit resource URLs that failed simple HTTP checks (403s, etc.)
2. Verify the page is still active
3. Extract updated information (phone, address, eligibility)
4. Flag resources that need human review

This is useful for:
- Rechecking 403s that might just be blocking bots (Crawl4AI has stealth mode)
- Extracting updated contact info from pages
- Verifying resources that use heavy JavaScript

Usage:
    # Check resources flagged as broken
    python scripts/crawl4ai_verify.py --flagged

    # Check specific resources by ID
    python scripts/crawl4ai_verify.py --ids abc123 def456

    # Check random sample of resources
    python scripts/crawl4ai_verify.py --sample 50

    # Dry run (don't update database)
    python scripts/crawl4ai_verify.py --flagged --dry-run
"""

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select

from app.database import engine
from app.models.resource import Resource, ResourceStatus

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("crawl4ai not installed. Run: uv pip install crawl4ai")
    sys.exit(1)


async def verify_url(crawler: "AsyncWebCrawler", url: str) -> dict:
    """Verify a single URL using Crawl4AI.

    Args:
        crawler: AsyncWebCrawler instance.
        url: URL to verify.

    Returns:
        dict with status, title, content_length, and extracted_info.
    """
    config = CrawlerRunConfig(
        wait_until="networkidle",
        word_count_threshold=50,
    )

    try:
        result = await crawler.arun(url=url, config=config)

        if result.success:
            # Extract some basic info for comparison
            return {
                "url": url,
                "status": "active",
                "title": result.metadata.get("title", ""),
                "content_length": len(result.markdown),
                "markdown_preview": result.markdown[:1000] if result.markdown else "",
                "links_count": len(result.links.get("internal", []))
                + len(result.links.get("external", [])),
            }
        else:
            return {
                "url": url,
                "status": "failed",
                "error": result.error_message,
            }
    except Exception as e:
        return {
            "url": url,
            "status": "error",
            "error": str(e),
        }


async def verify_batch(urls: list[str], concurrency: int = 3) -> list[dict]:
    """Verify a batch of URLs.

    Args:
        urls: List of URLs to verify.
        concurrency: How many to process at once (be nice to servers).

    Returns:
        List of verification results.
    """
    browser_config = BrowserConfig(
        headless=True,
        browser_type="firefox",
    )

    results = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Process in batches to avoid overwhelming servers
        for i in range(0, len(urls), concurrency):
            batch = urls[i : i + concurrency]
            print(f"\nVerifying batch {i//concurrency + 1} ({len(batch)} URLs)...")

            tasks = [verify_url(crawler, url) for url in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            # Brief pause between batches
            if i + concurrency < len(urls):
                await asyncio.sleep(1)

    return results


def get_flagged_resources(session: Session, limit: int = 100) -> list[Resource]:
    """Get resources that were flagged by the link checker.

    Args:
        session: Database session.
        limit: Max resources to return.

    Returns:
        List of Resource objects.
    """
    stmt = (
        select(Resource)
        .where(Resource.link_flagged_reason.isnot(None))
        .where(Resource.website.isnot(None))
        .where(Resource.status == ResourceStatus.NEEDS_REVIEW)
        .order_by(Resource.updated_at.desc())
        .limit(limit)
    )
    return list(session.exec(stmt).all())


def get_resources_by_ids(session: Session, ids: list[str]) -> list[Resource]:
    """Get resources by their IDs.

    Args:
        session: Database session.
        ids: List of resource IDs.

    Returns:
        List of Resource objects.
    """
    stmt = select(Resource).where(Resource.id.in_(ids))
    return list(session.exec(stmt).all())


def get_random_sample(session: Session, count: int) -> list[Resource]:
    """Get a random sample of resources to verify.

    Args:
        session: Database session.
        count: Number of resources to sample.

    Returns:
        List of Resource objects.
    """
    from sqlalchemy import func

    stmt = (
        select(Resource)
        .where(Resource.website.isnot(None))
        .where(Resource.status == ResourceStatus.ACTIVE)
        .order_by(func.random())
        .limit(count)
    )
    return list(session.exec(stmt).all())


def update_resource_from_verification(
    session: Session,
    resource: Resource,
    verification: dict,
    dry_run: bool = False,
) -> bool:
    """Update a resource based on verification results.

    Args:
        session: Database session.
        resource: Resource to update.
        verification: Verification result dict.
        dry_run: If True, don't actually update.

    Returns:
        True if resource was updated (or would be in dry run).
    """
    updated = False

    if verification["status"] == "active":
        # Page is working - clear the flag
        if resource.link_flagged_reason:
            print(f"  ✓ Clearing flag for {resource.title[:50]}")
            if not dry_run:
                resource.link_flagged_reason = None
                resource.link_health_score = 0.9  # High score - verified working
                resource.status = ResourceStatus.ACTIVE
                resource.link_checked_at = datetime.now(UTC)
            updated = True

    elif verification["status"] in ("failed", "error"):
        # Confirm the resource is broken
        error = verification.get("error", "Verification failed")
        print(f"  ✗ Confirmed broken: {resource.title[:50]} - {error[:50]}")
        if not dry_run:
            resource.link_flagged_reason = f"Crawl4AI: {error[:200]}"
            resource.link_health_score = 0.0
            resource.link_checked_at = datetime.now(UTC)
        updated = True

    if updated and not dry_run:
        session.add(resource)

    return updated


def main():
    parser = argparse.ArgumentParser(description="Verify resources using Crawl4AI")
    parser.add_argument(
        "--flagged",
        action="store_true",
        help="Check resources flagged as broken",
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        help="Check specific resource IDs",
    )
    parser.add_argument(
        "--sample",
        type=int,
        help="Check random sample of N resources",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max resources to check (default: 50)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't update database",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save results to JSON file",
    )
    args = parser.parse_args()

    if not any([args.flagged, args.ids, args.sample]):
        parser.print_help()
        print("\nError: Specify --flagged, --ids, or --sample")
        sys.exit(1)

    with Session(engine) as session:
        # Get resources to check
        if args.ids:
            resources = get_resources_by_ids(session, args.ids)
            print(f"Found {len(resources)} resources by ID")
        elif args.flagged:
            resources = get_flagged_resources(session, args.limit)
            print(f"Found {len(resources)} flagged resources")
        elif args.sample:
            resources = get_random_sample(session, args.sample)
            print(f"Got {len(resources)} random resources")
        else:
            resources = []

        if not resources:
            print("No resources to verify")
            sys.exit(0)

        # Get URLs (use website field)
        urls = [r.website for r in resources if r.website]
        print(f"Verifying {len(urls)} URLs...")

        # Run verification
        results = asyncio.run(verify_batch(urls))

        # Create URL to result mapping
        result_map = {r["url"]: r for r in results}

        # Update resources
        updated_count = 0
        recovered_count = 0
        confirmed_broken = 0

        for resource in resources:
            if not resource.website:
                continue

            verification = result_map.get(resource.website)
            if not verification:
                continue

            was_flagged = resource.link_flagged_reason is not None

            if update_resource_from_verification(
                session, resource, verification, args.dry_run
            ):
                updated_count += 1
                if verification["status"] == "active" and was_flagged:
                    recovered_count += 1
                elif verification["status"] != "active":
                    confirmed_broken += 1

        # Commit changes
        if not args.dry_run:
            session.commit()
            print(f"\nCommitted {updated_count} updates")
        else:
            print(f"\n[DRY RUN] Would update {updated_count} resources")

        # Summary
        print(f"\nSummary:")
        print(f"  Total checked: {len(results)}")
        print(f"  Active: {sum(1 for r in results if r['status'] == 'active')}")
        print(f"  Failed: {sum(1 for r in results if r['status'] != 'active')}")
        print(f"  Recovered (was flagged, now works): {recovered_count}")
        print(f"  Confirmed broken: {confirmed_broken}")

        # Save results if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
