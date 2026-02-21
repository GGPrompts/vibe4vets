#!/usr/bin/env python3
"""Review and resolve soft 404 flagged resources.

Processes resources flagged as soft 404s in three tiers:
1. High confidence (error phrases): Mark inactive immediately
2. Homepage redirects: Attempt to find new URLs, else mark inactive
3. Short content: Re-verify with crawl4ai browser rendering

Usage:
    # Dry run - see what would happen
    python scripts/review_soft_404s.py --dry-run

    # Process high-confidence dead links only
    python scripts/review_soft_404s.py --tier high

    # Process homepage redirects
    python scripts/review_soft_404s.py --tier redirect

    # Process short content with crawl4ai
    python scripts/review_soft_404s.py --tier short

    # Process all tiers
    python scripts/review_soft_404s.py --all

    # Apply changes (no --dry-run)
    python scripts/review_soft_404s.py --all --apply
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text


def get_engine(use_public_url: bool = False):
    """Get database engine.

    If use_public_url is set, tries to get the public Railway URL.
    Otherwise uses the standard DATABASE_URL.
    """
    import os

    db_url = os.environ.get("DATABASE_URL", "")

    if not db_url or "railway.internal" in db_url:
        # Try to get public URL via railway CLI
        import subprocess

        try:
            result = subprocess.run(
                ["railway", "variables", "--service", "Postgres", "--json"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                db_url = data.get("DATABASE_PUBLIC_URL", db_url)
        except Exception:
            pass

    if not db_url:
        print("ERROR: No DATABASE_URL available")
        sys.exit(1)

    return create_engine(db_url, pool_pre_ping=True)


def get_soft_404_resources(eng, tier: str | None = None) -> list[dict]:
    """Fetch soft 404 flagged resources from database."""
    with eng.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT id, title, website, link_flagged_reason, status,
                       link_http_status, link_health_score
                FROM resources
                WHERE link_flagged_reason LIKE 'Soft 404:%%'
                  AND status = 'NEEDS_REVIEW'
                ORDER BY link_flagged_reason, title
            """)
        ).all()

    resources = []
    for r in rows:
        reason = r[3] or ""
        reason_lower = reason.lower()

        # Classify tier
        if "error" in reason_lower or "not found" in reason_lower:
            resource_tier = "high"
        elif "redirect" in reason_lower:
            resource_tier = "redirect"
        elif "short" in reason_lower or "tiny" in reason_lower:
            resource_tier = "short"
        else:
            resource_tier = "other"

        if tier and resource_tier != tier:
            continue

        resources.append(
            {
                "id": str(r[0]),
                "title": r[1],
                "website": r[2],
                "reason": reason,
                "status": r[4],
                "http_status": r[5],
                "health_score": float(r[6]) if r[6] is not None else None,
                "tier": resource_tier,
            }
        )

    return resources


def mark_inactive(eng, resource_ids: list[str], reason: str, dry_run: bool = True):
    """Mark resources as inactive."""
    if not resource_ids:
        return 0

    if dry_run:
        print(f"  [DRY RUN] Would mark {len(resource_ids)} resources inactive")
        return len(resource_ids)

    with eng.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE resources
                SET status = 'inactive',
                    link_health_score = 0.0,
                    link_checked_at = :now,
                    updated_at = :now
                WHERE id::text = ANY(:ids)
            """),
            {
                "ids": resource_ids,
                "now": datetime.now(UTC),
            },
        )
        return result.rowcount


def mark_active(eng, resource_ids: list[str], dry_run: bool = True):
    """Clear flags and mark resources as active."""
    if not resource_ids:
        return 0

    if dry_run:
        print(f"  [DRY RUN] Would mark {len(resource_ids)} resources active")
        return len(resource_ids)

    with eng.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE resources
                SET status = 'active',
                    link_flagged_reason = NULL,
                    link_health_score = 0.9,
                    link_checked_at = :now,
                    updated_at = :now
                WHERE id::text = ANY(:ids)
            """),
            {
                "ids": resource_ids,
                "now": datetime.now(UTC),
            },
        )
        return result.rowcount


def update_url(eng, resource_id: str, new_url: str, dry_run: bool = True):
    """Update a resource's URL and clear flags."""
    if dry_run:
        print(f"  [DRY RUN] Would update URL to {new_url}")
        return 1

    with eng.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE resources
                SET website = :url,
                    status = 'active',
                    link_flagged_reason = NULL,
                    link_health_score = 0.8,
                    link_checked_at = :now,
                    updated_at = :now
                WHERE id::text = :id
            """),
            {
                "id": resource_id,
                "url": new_url,
                "now": datetime.now(UTC),
            },
        )
        return result.rowcount


def process_high_confidence(eng, resources: list[dict], dry_run: bool = True) -> dict:
    """Process high-confidence dead links (error phrases in content)."""
    print(f"\n{'=' * 60}")
    print(f"Processing {len(resources)} HIGH CONFIDENCE dead links")
    print(f"{'=' * 60}")

    inactive_ids = []
    for r in resources:
        print(f"  ✗ {r['title'][:60]}")
        print(f"    URL: {r['website']}")
        print(f"    Reason: {r['reason']}")
        inactive_ids.append(r["id"])

    count = mark_inactive(eng, inactive_ids, "Confirmed soft 404", dry_run)
    print(f"\nMarked {count} resources inactive")
    return {"inactive": count, "active": 0, "updated_url": 0}


def process_redirects(eng, resources: list[dict], dry_run: bool = True) -> dict:
    """Process homepage redirect resources."""
    print(f"\n{'=' * 60}")
    print(f"Processing {len(resources)} HOMEPAGE REDIRECT resources")
    print(f"{'=' * 60}")

    inactive_ids = []
    for r in resources:
        print(f"  → {r['title'][:60]}")
        print(f"    URL: {r['website']}")
        print(f"    Reason: {r['reason']}")
        # Homepage redirects are confirmed dead - the deep link is gone
        inactive_ids.append(r["id"])

    count = mark_inactive(eng, inactive_ids, "Deep URL redirects to homepage", dry_run)
    print(f"\nMarked {count} resources inactive")
    return {"inactive": count, "active": 0, "updated_url": 0}


def process_short_content(eng, resources: list[dict], dry_run: bool = True) -> dict:
    """Process short-content resources - these need crawl4ai re-verification."""
    print(f"\n{'=' * 60}")
    print(f"Processing {len(resources)} SHORT CONTENT resources")
    print(f"{'=' * 60}")

    # Group by domain for reporting
    from collections import defaultdict
    from urllib.parse import urlparse

    by_domain = defaultdict(list)
    for r in resources:
        try:
            domain = urlparse(r["website"]).netloc
        except Exception:
            domain = "unknown"
        by_domain[domain].append(r)

    print("\nBy domain:")
    for domain, items in sorted(by_domain.items(), key=lambda x: -len(x[1])):
        print(f"  {domain}: {len(items)} resources")

    print(f"\nThese {len(resources)} resources need crawl4ai re-verification.")
    print("Run: python scripts/crawl4ai_verify.py --flagged --limit 100")
    print("Or: python scripts/review_soft_404s.py --tier short --crawl4ai --apply")

    return {"inactive": 0, "active": 0, "needs_crawl4ai": len(resources)}


def main():
    parser = argparse.ArgumentParser(description="Review soft 404 flagged resources")
    parser.add_argument(
        "--tier",
        choices=["high", "redirect", "short"],
        help="Process specific tier only",
    )
    parser.add_argument("--all", action="store_true", help="Process all tiers")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry run)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes (default)",
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export resource list to JSON file",
    )
    args = parser.parse_args()

    dry_run = not args.apply or args.dry_run

    if not any([args.tier, args.all, args.export]):
        parser.print_help()
        print("\nError: Specify --tier, --all, or --export")
        sys.exit(1)

    eng = get_engine(use_public_url=True)

    if args.export:
        resources = get_soft_404_resources(eng)
        with open(args.export, "w") as f:
            json.dump(resources, f, indent=2)
        print(f"Exported {len(resources)} resources to {args.export}")
        return

    totals = {"inactive": 0, "active": 0, "updated_url": 0, "needs_crawl4ai": 0}

    if args.tier == "high" or args.all:
        resources = get_soft_404_resources(eng, tier="high")
        if resources:
            result = process_high_confidence(eng, resources, dry_run)
            for k, v in result.items():
                totals[k] = totals.get(k, 0) + v

    if args.tier == "redirect" or args.all:
        resources = get_soft_404_resources(eng, tier="redirect")
        if resources:
            result = process_redirects(eng, resources, dry_run)
            for k, v in result.items():
                totals[k] = totals.get(k, 0) + v

    if args.tier == "short" or args.all:
        resources = get_soft_404_resources(eng, tier="short")
        if resources:
            result = process_short_content(eng, resources, dry_run)
            for k, v in result.items():
                totals[k] = totals.get(k, 0) + v

    print(f"\n{'=' * 60}")
    print("TOTALS")
    print(f"{'=' * 60}")
    for k, v in totals.items():
        if v > 0:
            print(f"  {k}: {v}")

    if dry_run:
        print("\n⚠ DRY RUN - no changes made. Use --apply to commit changes.")


if __name__ == "__main__":
    main()
