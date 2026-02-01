#!/usr/bin/env python3
"""Fix resources that have mismatched scope/states data.

This script fixes resources where:
1. scope=NATIONAL but states has specific state codes -> change to scope=STATE
2. scope=STATE but states is empty -> investigate (log only, no auto-fix)

Resources should only have scope=NATIONAL if they are truly nationwide
(hotlines, online services, states=['*'] or empty states array).
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Load .env file
from dotenv import load_dotenv  # noqa: E402

load_dotenv(backend_dir / ".env")

from sqlmodel import Session, create_engine, select  # noqa: E402

from app.models.resource import Resource, ResourceScope  # noqa: E402


def fix_scope_data(dry_run: bool = True) -> dict:
    """Fix resources with mismatched scope/states data.

    Args:
        dry_run: If True, only report what would be changed without making changes.

    Returns:
        Dictionary with fix statistics.
    """
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets")
    engine = create_engine(database_url, echo=False)

    stats = {
        "national_with_states_fixed": 0,
        "state_with_empty_states": 0,
        "already_correct": 0,
        "errors": [],
    }

    with Session(engine) as session:
        # =================================================================
        # Fix 1: Resources marked NATIONAL but have specific state codes
        # These should be scope=STATE
        # =================================================================
        print("=" * 60)
        print("Checking: NATIONAL scope with specific states")
        print("=" * 60)

        stmt = select(Resource).where(
            Resource.scope == ResourceScope.NATIONAL,
        )
        national_resources = session.exec(stmt).all()

        for resource in national_resources:
            states = resource.states or []
            # Skip if truly national (empty or wildcard)
            if len(states) == 0 or states == ["*"]:
                stats["already_correct"] += 1
                continue

            # This resource has specific states but is marked national
            print(f"\n  ID: {resource.id}")
            print(f"  Title: {resource.title[:60]}...")
            print(f"  Current: scope={resource.scope.value}, states={states}")
            print("  Fix: scope=STATE")

            if not dry_run:
                resource.scope = ResourceScope.STATE
                session.add(resource)

            stats["national_with_states_fixed"] += 1

        # =================================================================
        # Check 2: Resources marked STATE but have empty states array
        # Log these for investigation but don't auto-fix
        # =================================================================
        print("\n" + "=" * 60)
        print("Checking: STATE scope with empty states (log only)")
        print("=" * 60)

        stmt = select(Resource).where(
            Resource.scope == ResourceScope.STATE,
        )
        state_resources = session.exec(stmt).all()

        for resource in state_resources:
            states = resource.states or []
            if len(states) == 0:
                print(f"\n  ID: {resource.id}")
                print(f"  Title: {resource.title[:60]}...")
                print("  Issue: scope=STATE but states is empty")
                print("  Action: Needs manual investigation")
                stats["state_with_empty_states"] += 1

        # =================================================================
        # Commit changes
        # =================================================================
        if not dry_run and stats["national_with_states_fixed"] > 0:
            session.commit()
            print(f"\nCommitted {stats['national_with_states_fixed']} fixes to database.")

    return stats


def print_summary(stats: dict, dry_run: bool) -> None:
    """Print a summary of the fixes."""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Resources with NATIONAL scope fixed to STATE: {stats['national_with_states_fixed']}")
    print(f"  Resources with STATE scope but empty states:  {stats['state_with_empty_states']}")
    print(f"  Resources already correct:                    {stats['already_correct']}")

    if stats["errors"]:
        print(f"  Errors: {len(stats['errors'])}")
        for err in stats["errors"]:
            print(f"    - {err}")

    if dry_run:
        print("\n[DRY RUN] No changes were made. Run with --apply to fix.")
    else:
        print(f"\n[APPLIED] Fixed {stats['national_with_states_fixed']} resources.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix resources with mismatched scope/states data")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually apply changes (default is dry-run)",
    )
    args = parser.parse_args()

    print("Fix Scope Data Script")
    print("=====================")
    print(f"Mode: {'APPLY' if args.apply else 'DRY RUN'}")
    print()

    stats = fix_scope_data(dry_run=not args.apply)
    print_summary(stats, dry_run=not args.apply)
