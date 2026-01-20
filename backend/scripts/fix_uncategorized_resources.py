#!/usr/bin/env python3
"""Fix 10 VA resources missing categories (V4V-v8i).

These resources have no categories assigned and are invisible to category filters.
This script updates them with the correct categories identified in the issue.
"""

import os
import sys
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, col, create_engine, select  # type: ignore[import-untyped]

from app.models import Resource

# Resources to fix with their correct categories
# Format: (title pattern to match, additional title patterns, categories to assign)
RESOURCES_TO_FIX = [
    # Pattern matches partial title, categories to assign
    ("VA Richmond", ["HUD-VASH", "Health Care for Homeless"], ["housing"]),
    ("Fort Gregg-Adams", ["Employment Readiness"], ["employment"]),
    ("American Legion Virginia", ["Veteran Services"], ["employment", "legal"]),
    ("DAV Virginia", ["Employment Program"], ["employment"]),
    ("SupportWorks Housing", ["SSVF"], ["housing"]),
    ("Liberation Veteran Services", [], ["housing", "employment"]),
    ("HomeAgain Richmond", ["Veteran Transitional Housing"], ["housing"]),
    ("Virginia Department of Veterans Services", ["Employment"], ["employment", "training"]),
    ("Virginia Career Works", ["Henrico"], ["employment", "training"]),
    ("CARITAS", ["Mens Emergency Shelter", "Men's Emergency Shelter"], ["housing"]),
]


def fix_uncategorized_resources(database_url: str) -> dict:
    """Update uncategorized resources with correct categories.

    Returns dict with counts of updated/not_found resources.
    """
    engine = create_engine(database_url, echo=False)
    results: dict[str, list[str]] = {"updated": [], "not_found": [], "already_categorized": []}

    with Session(engine) as session:
        for org_pattern, title_patterns, categories in RESOURCES_TO_FIX:
            # Build query to find resource by title pattern using ilike
            statement = select(Resource).where(col(Resource.title).ilike(f"%{org_pattern}%"))

            # If title patterns provided, narrow down
            resources = session.exec(statement).all()

            matched = None
            for resource in resources:
                # Check if any title pattern matches
                if not title_patterns:
                    matched = resource
                    break
                for pattern in title_patterns:
                    if pattern.lower() in resource.title.lower():
                        matched = resource
                        break
                if matched:
                    break

            if not matched:
                results["not_found"].append(
                    f"{org_pattern} ({', '.join(title_patterns) if title_patterns else 'any'})"
                )
                continue

            # Check if already has categories
            if matched.categories and len(matched.categories) > 0:
                results["already_categorized"].append(
                    f"{matched.title} (has: {matched.categories})"
                )
                continue

            # Update categories
            matched.categories = categories
            matched.updated_at = datetime.now(timezone.utc)
            session.add(matched)
            results["updated"].append(f"{matched.title} -> {categories}")

        session.commit()

    return results


def verify_filter_counts(database_url: str) -> dict:
    """Verify resource counts by category filter."""
    engine = create_engine(database_url, echo=False)

    with Session(engine) as session:
        # Total VA resources (state = VA) - using col() for type checker
        # Resource.states.contains is a SQLAlchemy array operation
        total_va = session.exec(
            select(Resource).where(Resource.states.contains(["VA"]))  # type: ignore[union-attr]
        ).all()

        # Resources with any category
        categorized = [r for r in total_va if r.categories and len(r.categories) > 0]

        # Resources without categories
        uncategorized = [r for r in total_va if not r.categories or len(r.categories) == 0]

        # Count by category
        category_counts: dict[str, int] = {}
        for r in total_va:
            for cat in r.categories or []:
                category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_va": len(total_va),
            "categorized": len(categorized),
            "uncategorized": len(uncategorized),
            "uncategorized_titles": [r.title for r in uncategorized],
            "by_category": category_counts,
        }


def main():
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets")

    print("=" * 60)
    print("Fixing uncategorized VA resources (V4V-v8i)")
    print("=" * 60)

    # Show before state
    print("\nBEFORE:")
    before = verify_filter_counts(database_url)
    print(f"  Total VA resources: {before['total_va']}")
    print(f"  Categorized: {before['categorized']}")
    print(f"  Uncategorized: {before['uncategorized']}")
    if before["uncategorized_titles"]:
        print("  Uncategorized resources:")
        for title in before["uncategorized_titles"]:
            print(f"    - {title}")

    # Fix resources
    print("\nFIXING...")
    results = fix_uncategorized_resources(database_url)

    if results["updated"]:
        print("\n  Updated:")
        for item in results["updated"]:
            print(f"    + {item}")

    if results["already_categorized"]:
        print("\n  Already categorized (skipped):")
        for item in results["already_categorized"]:
            print(f"    ~ {item}")

    if results["not_found"]:
        print("\n  Not found:")
        for item in results["not_found"]:
            print(f"    ! {item}")

    # Show after state
    print("\nAFTER:")
    after = verify_filter_counts(database_url)
    print(f"  Total VA resources: {after['total_va']}")
    print(f"  Categorized: {after['categorized']}")
    print(f"  Uncategorized: {after['uncategorized']}")
    if after["uncategorized_titles"]:
        print("  Remaining uncategorized:")
        for title in after["uncategorized_titles"]:
            print(f"    - {title}")
    print(f"  By category: {after['by_category']}")

    print("\n" + "=" * 60)
    print(f"Summary: {len(results['updated'])} updated, {len(results['not_found'])} not found")
    print("=" * 60)


if __name__ == "__main__":
    main()
