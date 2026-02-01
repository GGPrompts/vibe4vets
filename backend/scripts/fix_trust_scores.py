#!/usr/bin/env python3
"""Fix trust scores after data import.

This script recalculates reliability_score based on source tier and
updates freshness_score and last_verified for all resources.

For tier-1 sources (official government APIs), we consider the data
"verified" since it comes directly from authoritative sources.

Run with:
    cd backend && python scripts/fix_trust_scores.py

Or via Railway:
    railway run python scripts/fix_trust_scores.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import UTC, datetime

from sqlmodel import Session, select

from app.database import engine
from app.models import Resource, Source
from app.models.resource import ResourceStatus
from app.services.trust import TIER_SCORES, TrustService


def fix_trust_scores(dry_run: bool = False) -> dict:
    """Recalculate trust scores for all resources based on source tier.

    Args:
        dry_run: If True, don't commit changes.

    Returns:
        Statistics dictionary.
    """

    stats = {
        "total": 0,
        "updated_reliability": 0,
        "marked_verified": 0,
        "no_source": 0,
        "by_tier": {1: 0, 2: 0, 3: 0, 4: 0},
    }

    with Session(engine) as session:
        trust_service = TrustService(session)

        # Get all active resources
        resources = session.exec(
            select(Resource).where(Resource.status == ResourceStatus.ACTIVE)
        ).all()

        stats["total"] = len(resources)
        print(f"Processing {len(resources)} active resources...")

        # Build source cache
        sources = session.exec(select(Source)).all()
        source_map = {s.id: s for s in sources}
        print(f"Loaded {len(sources)} sources")

        for i, resource in enumerate(resources):
            if resource.source_id and resource.source_id in source_map:
                source = source_map[resource.source_id]
                tier = source.tier

                # Update reliability based on tier
                old_reliability = resource.reliability_score
                new_reliability = TIER_SCORES.get(tier, 0.4)

                if abs(old_reliability - new_reliability) > 0.01:
                    resource.reliability_score = new_reliability
                    stats["updated_reliability"] += 1

                stats["by_tier"][tier] = stats["by_tier"].get(tier, 0) + 1

                # For tier-1 sources, mark as verified (they're from official APIs)
                if tier == 1 and resource.last_verified is None:
                    resource.last_verified = resource.created_at or datetime.now(UTC)
                    stats["marked_verified"] += 1

            else:
                stats["no_source"] += 1
                # Resources without source get default tier-4 reliability
                if resource.reliability_score == 0.5:
                    resource.reliability_score = 0.4
                    stats["updated_reliability"] += 1

            # Update freshness based on last_verified or created_at
            # Handle timezone-naive datetimes by calculating freshness directly
            if resource.last_verified is not None:
                reference_date = resource.last_verified
            else:
                reference_date = resource.created_at

            if reference_date:
                # Make timezone-aware if needed
                if reference_date.tzinfo is None:
                    reference_date = reference_date.replace(tzinfo=UTC)
                days_old = (datetime.now(UTC) - reference_date).days
                freshness = max(0.1, min(1.0, 0.5 ** (days_old / 30)))
                resource.freshness_score = freshness

            if (i + 1) % 1000 == 0:
                print(f"  Processed {i + 1}/{len(resources)}...")

        if dry_run:
            print("\n[DRY RUN] Would have updated:")
        else:
            session.commit()
            print("\nCommitted changes:")

        print(f"  Total resources: {stats['total']}")
        print(f"  Reliability updated: {stats['updated_reliability']}")
        print(f"  Marked verified (tier-1): {stats['marked_verified']}")
        print(f"  No source linked: {stats['no_source']}")
        print(f"  By tier: {stats['by_tier']}")

        # Calculate new average trust score
        if not dry_run:
            from sqlmodel import func

            avg_trust = session.exec(
                select(func.avg(Resource.reliability_score * Resource.freshness_score)).where(
                    Resource.status == ResourceStatus.ACTIVE
                )
            ).one()
            verified_count = session.exec(
                select(func.count()).select_from(Resource).where(
                    Resource.last_verified != None  # noqa: E711
                )
            ).one()
            print(f"\nNew average trust score: {float(avg_trust):.1%}")
            print(f"Verified resources: {verified_count}")

    return stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix trust scores after data import")
    parser.add_argument("--dry-run", action="store_true", help="Don't commit changes")
    args = parser.parse_args()

    fix_trust_scores(dry_run=args.dry_run)
