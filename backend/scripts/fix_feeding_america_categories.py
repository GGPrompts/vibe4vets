#!/usr/bin/env python3
"""Fix Feeding America resources to include the 'food' category.

This script finds all resources from Feeding America that don't have
the 'food' category and adds it to them.
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

from app.models.resource import Resource  # noqa: E402


def fix_feeding_america_categories(dry_run: bool = True) -> None:
    """Add 'food' category to Feeding America resources that are missing it.

    Args:
        dry_run: If True, only report what would be changed without making changes.
    """
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets"
    )
    engine = create_engine(database_url, echo=False)

    with Session(engine) as session:
        # Find resources with "Feeding America" in title that don't have food category
        stmt = select(Resource).where(
            Resource.title.ilike("%Feeding America%")
        )
        resources = session.exec(stmt).all()

        print(f"Found {len(resources)} Feeding America resources")

        updated_count = 0
        for resource in resources:
            current_categories = resource.categories or []

            if "food" not in current_categories:
                print(f"  - {resource.title}")
                print(f"    Current categories: {current_categories}")

                if not dry_run:
                    # Add food category
                    resource.categories = list(current_categories) + ["food"]
                    session.add(resource)

                updated_count += 1

        if updated_count == 0:
            print("\nAll Feeding America resources already have the 'food' category.")
        elif dry_run:
            print(f"\nWould update {updated_count} resources to add 'food' category.")
            print("Run with --apply to make changes.")
        else:
            session.commit()
            print(f"\nUpdated {updated_count} resources to include 'food' category.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix Feeding America resources to include 'food' category"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually apply changes (default is dry-run)",
    )
    args = parser.parse_args()

    fix_feeding_america_categories(dry_run=not args.apply)
