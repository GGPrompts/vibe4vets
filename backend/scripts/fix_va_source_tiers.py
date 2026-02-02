#!/usr/bin/env python3
"""Fix source tiers for VA.gov and other government sources.

This script ensures that sources from VA.gov, DOL, HUD, and other federal
government APIs are correctly marked as tier 1 (Official Government).

VA.gov sources should display as "Government" in the frontend, not "Nonprofit".

Run with:
    cd backend && python scripts/fix_va_source_tiers.py

Or via Railway:
    railway run python scripts/fix_va_source_tiers.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select

from app.database import engine
from app.models import Source

# Sources that should be tier 1 (Official Government)
# These patterns are used to match source names
TIER_1_PATTERNS = [
    # VA sources
    "va.gov",
    "va ",
    "veteran",
    "vet center",
    "lighthouse",
    # DOL sources
    "dol",
    "department of labor",
    "careeronestop",
    "usajobs",
    "apprenticeship",
    # HUD sources
    "hud",
    "housing and urban development",
    "hud-vash",
    # SBA sources
    "sba",
    "small business administration",
    "vboc",
    # DOD sources
    "dod",
    "department of defense",
    "skillbridge",
    # Other federal
    "federal",
    "usa.gov",
    "gi bill",
    "gpd",  # Grant and Per Diem
    "ssvf",  # Supportive Services for Veteran Families
]


def fix_va_source_tiers(dry_run: bool = False) -> dict:
    """Fix source tiers for VA.gov and government sources.

    Args:
        dry_run: If True, don't commit changes.

    Returns:
        Statistics dictionary.
    """
    stats = {
        "total_sources": 0,
        "already_tier_1": 0,
        "fixed_to_tier_1": 0,
        "unchanged": 0,
        "changes": [],
    }

    with Session(engine) as session:
        sources = session.exec(select(Source)).all()
        stats["total_sources"] = len(sources)

        print(f"Checking {len(sources)} sources...")

        for source in sources:
            name_lower = source.name.lower()
            url_lower = (source.url or "").lower()

            # Check if source should be tier 1
            should_be_tier_1 = False
            matched_pattern = None

            for pattern in TIER_1_PATTERNS:
                if pattern in name_lower or pattern in url_lower:
                    should_be_tier_1 = True
                    matched_pattern = pattern
                    break

            if should_be_tier_1:
                if source.tier == 1:
                    stats["already_tier_1"] += 1
                else:
                    old_tier = source.tier
                    source.tier = 1
                    stats["fixed_to_tier_1"] += 1
                    stats["changes"].append(
                        {
                            "name": source.name,
                            "old_tier": old_tier,
                            "new_tier": 1,
                            "matched_pattern": matched_pattern,
                        }
                    )
            else:
                stats["unchanged"] += 1

        if dry_run:
            print("\n[DRY RUN] Would make the following changes:")
        else:
            session.commit()
            print("\nCommitted the following changes:")

        print(f"\nTotal sources: {stats['total_sources']}")
        print(f"Already tier 1: {stats['already_tier_1']}")
        print(f"Fixed to tier 1: {stats['fixed_to_tier_1']}")
        print(f"Unchanged (non-government): {stats['unchanged']}")

        if stats["changes"]:
            print("\nSources changed:")
            for change in stats["changes"]:
                print(f"  - {change['name']}: tier {change['old_tier']} -> {change['new_tier']}")
                print(f"    (matched pattern: '{change['matched_pattern']}')")
        else:
            print("\nNo sources needed fixing.")

    return stats


def list_sources() -> None:
    """List all sources with their current tiers."""
    with Session(engine) as session:
        sources = session.exec(select(Source).order_by(Source.tier, Source.name)).all()

        print(f"\n{'Source Name':<50} {'Tier':<5} {'URL'}")
        print("-" * 100)

        for source in sources:
            name = source.name[:48] + ".." if len(source.name) > 50 else source.name
            url = (source.url or "")[:40]
            print(f"{name:<50} {source.tier:<5} {url}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix source tiers for VA.gov sources")
    parser.add_argument("--dry-run", action="store_true", help="Don't commit changes")
    parser.add_argument("--list", action="store_true", help="List all sources and their tiers")
    args = parser.parse_args()

    if args.list:
        list_sources()
    else:
        fix_va_source_tiers(dry_run=args.dry_run)
