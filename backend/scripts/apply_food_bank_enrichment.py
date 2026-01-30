#!/usr/bin/env python3
"""Apply Feeding America food bank website enrichment to the database.

This script reads the food_bank_website_enrichment.json file and updates
resources in the database with the found URLs.

Usage:
    python scripts/apply_food_bank_enrichment.py          # Dry run - show what would be updated
    python scripts/apply_food_bank_enrichment.py --apply  # Apply updates to database
"""

import json
import sys
import uuid
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select

from app.database import engine
from app.models.resource import Resource


def load_enrichment_data() -> list[dict]:
    """Load the enrichment data from JSON file."""
    data_path = Path(__file__).parent.parent / "data" / "food_bank_website_enrichment.json"
    with open(data_path) as f:
        return json.load(f)


def main():
    apply = "--apply" in sys.argv
    high_only = "--high-only" in sys.argv

    enrichment_data = load_enrichment_data()

    # Filter by confidence if requested
    if high_only:
        entries_to_apply = [e for e in enrichment_data if e["confidence"] == "HIGH" and e["url"]]
    else:
        # Apply both HIGH and MEDIUM confidence (reviewed and approved)
        entries_to_apply = [
            e for e in enrichment_data if e["confidence"] in ("HIGH", "MEDIUM") and e["url"]
        ]

    print(f"{'=' * 60}")
    print("Food Bank Website Enrichment")
    print(f"{'=' * 60}\n")

    print(f"Total entries in enrichment file: {len(enrichment_data)}")
    print(f"Entries to apply (HIGH + MEDIUM with URLs): {len(entries_to_apply)}")
    print()

    # Stats
    stats = {"updated": 0, "skipped_has_url": 0, "not_found": 0, "errors": 0}

    with Session(engine) as session:
        for entry in entries_to_apply:
            resource_id = entry["id"]
            new_url = entry["url"]
            title = entry["title"]
            confidence = entry["confidence"]

            try:
                resource_uuid = uuid.UUID(resource_id)
            except ValueError:
                print(f"  ERROR: Invalid UUID: {resource_id}")
                stats["errors"] += 1
                continue

            # Find the resource
            resource = session.get(Resource, resource_uuid)
            if not resource:
                print(f"  NOT FOUND: {title} ({resource_id})")
                stats["not_found"] += 1
                continue

            # Check if already has a URL
            if resource.website:
                if not apply:
                    print(f"  SKIP (has URL): {title}")
                    print(f"    Current: {resource.website}")
                    print(f"    New: {new_url}")
                stats["skipped_has_url"] += 1
                continue

            # Update the resource
            if apply:
                resource.website = new_url
                session.add(resource)
                print(f"  UPDATED [{confidence}]: {title}")
            else:
                print(f"  WOULD UPDATE [{confidence}]: {title}")
                print(f"    URL: {new_url}")

            stats["updated"] += 1

        if apply:
            session.commit()
            print(f"\n{'=' * 60}")
            print("Changes committed to database!")
            print(f"{'=' * 60}")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Updated: {stats['updated']}")
    print(f"  Skipped (already has URL): {stats['skipped_has_url']}")
    print(f"  Not found in database: {stats['not_found']}")
    print(f"  Errors: {stats['errors']}")

    if not apply:
        print(f"\nRun with --apply to apply these changes to the database.")
        print(f"Run with --high-only to only apply HIGH confidence URLs.")


if __name__ == "__main__":
    main()
