#!/usr/bin/env python3
"""Local link checker for Claude Code sessions.

This script extracts resources needing link checks and outputs them
in a format suitable for parallel subagent processing.

Usage:
    # Export resources needing checks (oldest first)
    python scripts/link_check_local.py export --limit 1000 > urls.json

    # Import results and update database
    python scripts/link_check_local.py import < results.json

    # Show stats
    python scripts/link_check_local.py stats
"""

import argparse
import json
import sys
from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select, func, text

# Add parent to path for imports
sys.path.insert(0, ".")

from app.database import engine
from app.models.resource import Resource, ResourceStatus


def export_for_check(limit: int = 1000, days_old: int = 7) -> None:
    """Export resources needing link checks.

    Prioritizes:
    1. Never checked (link_checked_at IS NULL)
    2. Oldest checked first
    3. Only active resources with websites
    """
    cutoff = datetime.now(UTC) - timedelta(days=days_old)

    with Session(engine) as session:
        stmt = (
            select(
                Resource.id,
                Resource.title,
                Resource.website,
                Resource.link_checked_at,
                Resource.link_health_score,
            )
            .where(Resource.website.isnot(None))
            .where(Resource.status == ResourceStatus.ACTIVE)
            .where(
                (Resource.link_checked_at.is_(None))
                | (Resource.link_checked_at < cutoff)
            )
            .order_by(Resource.link_checked_at.asc().nullsfirst())
            .limit(limit)
        )

        results = session.exec(stmt).all()

        resources = []
        for r in results:
            url = r.website
            if url and not url.startswith(("http://", "https://")):
                url = f"https://{url}"

            resources.append(
                {
                    "id": str(r.id),
                    "title": r.title,
                    "url": url,
                    "last_checked": r.link_checked_at.isoformat() if r.link_checked_at else None,
                    "current_score": r.link_health_score,
                }
            )

        print(json.dumps(resources, indent=2))
        print(f"\n# Exported {len(resources)} resources", file=sys.stderr)


def import_results() -> None:
    """Import link check results from stdin and update database."""
    try:
        results = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(results, list):
        print("Expected JSON array of results", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(UTC)
    updated = 0
    flagged = 0
    broken = 0

    with Session(engine) as session:
        for r in results:
            resource_id = r.get("id")
            score = r.get("score", 1.0)
            status = r.get("status", "healthy")
            reason = r.get("reason")

            if not resource_id:
                continue

            # Find resource
            stmt = select(Resource).where(Resource.id == resource_id)
            resource = session.exec(stmt).first()

            if not resource:
                print(f"Resource not found: {resource_id}", file=sys.stderr)
                continue

            # Update fields
            resource.link_checked_at = now
            resource.link_health_score = score
            resource.link_http_status = r.get("http_status")

            if status == "broken":
                resource.link_flagged_reason = reason or "Broken link"
                resource.status = ResourceStatus.NEEDS_REVIEW
                broken += 1
            elif status == "flagged" or score < 0.5:
                resource.link_flagged_reason = reason or "Low health score"
                resource.status = ResourceStatus.NEEDS_REVIEW
                flagged += 1
            else:
                # Clear any previous flags if now healthy
                resource.link_flagged_reason = None

            session.add(resource)
            updated += 1

        session.commit()

    print(f"Updated: {updated}, Broken: {broken}, Flagged: {flagged}")


def show_stats() -> None:
    """Show link check statistics."""
    with Session(engine) as session:
        # Total with URLs
        total = session.exec(
            select(func.count(Resource.id)).where(Resource.website.isnot(None))
        ).one()

        # Never checked
        never_checked = session.exec(
            select(func.count(Resource.id))
            .where(Resource.website.isnot(None))
            .where(Resource.link_checked_at.is_(None))
        ).one()

        # Checked in last 7 days
        week_ago = datetime.now(UTC) - timedelta(days=7)
        recent = session.exec(
            select(func.count(Resource.id))
            .where(Resource.website.isnot(None))
            .where(Resource.link_checked_at >= week_ago)
        ).one()

        # Broken (score < 0.3)
        broken = session.exec(
            select(func.count(Resource.id))
            .where(Resource.website.isnot(None))
            .where(Resource.link_health_score < 0.3)
        ).one()

        # Flagged for review
        flagged = session.exec(
            select(func.count(Resource.id))
            .where(Resource.website.isnot(None))
            .where(Resource.link_flagged_reason.isnot(None))
        ).one()

        # Average score (where checked)
        avg_score = session.exec(
            select(func.avg(Resource.link_health_score))
            .where(Resource.link_health_score.isnot(None))
        ).one()

        print("Link Check Statistics")
        print("=" * 40)
        print(f"Total resources with URLs: {total:,}")
        print(f"Never checked:             {never_checked:,}")
        print(f"Checked (last 7 days):     {recent:,}")
        print(f"Stale (>7 days old):       {total - never_checked - recent:,}")
        print(f"Broken (score < 0.3):      {broken:,}")
        print(f"Flagged for review:        {flagged:,}")
        print(f"Average health score:      {avg_score:.2f}" if avg_score else "N/A")


def main():
    parser = argparse.ArgumentParser(description="Local link checker for Claude Code")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export resources for checking")
    export_parser.add_argument(
        "--limit", type=int, default=1000, help="Max resources to export"
    )
    export_parser.add_argument(
        "--days-old", type=int, default=7, help="Check resources older than N days"
    )

    # Import command
    subparsers.add_parser("import", help="Import results from stdin")

    # Stats command
    subparsers.add_parser("stats", help="Show link check statistics")

    args = parser.parse_args()

    if args.command == "export":
        export_for_check(limit=args.limit, days_old=args.days_old)
    elif args.command == "import":
        import_results()
    elif args.command == "stats":
        show_stats()


if __name__ == "__main__":
    main()
