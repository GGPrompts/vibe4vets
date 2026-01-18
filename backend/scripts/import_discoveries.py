#!/usr/bin/env python3
"""Import AI-discovered resources into the review queue.

Usage:
    python -m backend.scripts.import_discoveries <json_file>
    python -m backend.scripts.import_discoveries backend/data/discoveries/scan-housing-virginia-2026-01-18.json

The JSON file should match the discovery output format with a "discovered" array.
"""

import json
import os
import sys
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine, select

from app.models import Organization, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus
from app.models.review import ReviewState, ReviewStatus
from app.models.source import HealthStatus, SourceType


def normalize_name(name: str) -> str:
    """Normalize organization name for comparison."""
    return (
        name.lower()
        .strip()
        .replace("the ", "")
        .replace(" inc", "")
        .replace(" llc", "")
        .replace(" corp", "")
        .replace(".", "")
    )


def find_existing_org(session: Session, org_name: str, org_website: str | None) -> Organization | None:
    """Find existing organization by name similarity or website match."""
    normalized_name = normalize_name(org_name)

    # First try website match (most reliable)
    if org_website:
        stmt = select(Organization).where(Organization.website == org_website)
        org = session.exec(stmt).first()
        if org:
            return org

    # Then try name similarity
    stmt = select(Organization)
    existing_orgs = session.exec(stmt).all()

    for org in existing_orgs:
        existing_normalized = normalize_name(org.name)
        similarity = SequenceMatcher(None, normalized_name, existing_normalized).ratio()
        if similarity >= 0.85:
            return org

    return None


def find_duplicate_resource(
    session: Session,
    org_id,
    title: str,
    source_url: str | None
) -> Resource | None:
    """Check if a similar resource already exists."""
    # Check by source URL first
    if source_url:
        stmt = select(Resource).where(Resource.source_url == source_url)
        existing = session.exec(stmt).first()
        if existing:
            return existing

    # Check by org + title similarity
    stmt = select(Resource).where(Resource.organization_id == org_id)
    org_resources = session.exec(stmt).all()

    normalized_title = title.lower().strip()
    for resource in org_resources:
        existing_title = resource.title.lower().strip()
        similarity = SequenceMatcher(None, normalized_title, existing_title).ratio()
        if similarity >= 0.85:
            return resource

    return None


def get_or_create_discovery_source(session: Session) -> Source:
    """Get or create the AI Discovery source."""
    stmt = select(Source).where(Source.name == "AI Discovery")
    source = session.exec(stmt).first()

    if not source:
        source = Source(
            name="AI Discovery",
            url="https://vibe4vets.org/discovery",
            source_type=SourceType.MANUAL,
            tier=4,  # Community tier - needs review
            health_status=HealthStatus.HEALTHY,
            last_success=datetime.now(timezone.utc),
        )
        session.add(source)
        session.flush()

    return source


def map_scope(scope_str: str | None) -> ResourceScope:
    """Map scope string to ResourceScope enum."""
    if not scope_str:
        return ResourceScope.NATIONAL
    scope_lower = scope_str.lower()
    if scope_lower == "state":
        return ResourceScope.STATE
    elif scope_lower == "local":
        return ResourceScope.LOCAL
    return ResourceScope.NATIONAL


def import_discoveries(json_path: str, database_url: str, dry_run: bool = False):
    """Import discovered resources from JSON file into review queue."""
    # Load JSON file
    path = Path(json_path)
    if not path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    with open(path) as f:
        data = json.load(f)

    # Handle both formats: direct array or {discovered: [...]}
    if isinstance(data, list):
        discoveries = data
    elif "discovered" in data:
        discoveries = data["discovered"]
    else:
        print("Error: JSON must be an array or have a 'discovered' key")
        sys.exit(1)

    if not discoveries:
        print("No discoveries to import")
        return

    print(f"Found {len(discoveries)} discoveries to import")

    if dry_run:
        print("\n[DRY RUN - No changes will be made, no DB connection needed]\n")
        # In dry run, just show what would be imported without DB
        for i, disc in enumerate(discoveries, 1):
            title = disc.get("title") or disc.get("name") or "Unknown"
            org_name = disc.get("org_name") or disc.get("organization") or "Unknown"
            category = disc.get("category", "unknown")
            confidence = disc.get("confidence", 0.5)
            print(f"  [{i}] {title}")
            print(f"      Org: {org_name} | Category: {category} | Confidence: {confidence:.2f}")

        print("\n" + "=" * 50)
        print("Dry Run Summary")
        print("=" * 50)
        print(f"  Would import: {len(discoveries)} resources")
        print(f"\nTo import for real, run without --dry-run flag")
        print(f"(Requires DATABASE_URL or running PostgreSQL)")
        return

    engine = create_engine(database_url, echo=False)

    stats = {
        "imported": 0,
        "duplicates_skipped": 0,
        "orgs_created": 0,
        "orgs_reused": 0,
        "errors": 0,
    }

    with Session(engine) as session:
        # Get or create discovery source
        source = get_or_create_discovery_source(session)

        for i, disc in enumerate(discoveries, 1):
            try:
                # Extract fields with fallbacks
                title = disc.get("title") or disc.get("name")
                if not title:
                    print(f"  [{i}] Skipping: no title")
                    stats["errors"] += 1
                    continue

                org_name = disc.get("org_name") or disc.get("organization") or "Unknown Organization"
                org_website = disc.get("org_website") or disc.get("website")
                description = disc.get("description") or ""
                source_url = disc.get("source_url") or disc.get("website")

                # Find or create organization
                existing_org = find_existing_org(session, org_name, org_website)

                if existing_org:
                    org = existing_org
                    stats["orgs_reused"] += 1
                    print(f"  [{i}] Using existing org: {org.name}")
                else:
                    if dry_run:
                        print(f"  [{i}] Would create org: {org_name}")
                        org = None
                    else:
                        org = Organization(
                            name=org_name,
                            website=org_website,
                            phones=[disc.get("phone")] if disc.get("phone") else [],
                            emails=[disc.get("email")] if disc.get("email") else [],
                        )
                        session.add(org)
                        session.flush()
                        stats["orgs_created"] += 1
                        print(f"  [{i}] Created org: {org_name}")

                # Skip if we couldn't get/create an org (dry run case)
                if org is None:
                    stats["imported"] += 1
                    continue

                # Check for duplicate resource
                duplicate = find_duplicate_resource(session, org.id, title, source_url)
                if duplicate:
                    print(f"  [{i}] Skipping duplicate: {title}")
                    stats["duplicates_skipped"] += 1
                    continue

                # Map fields
                categories = disc.get("categories", [])
                if isinstance(categories, str):
                    categories = [categories]

                subcategories = disc.get("subcategories", [])
                if isinstance(subcategories, str):
                    subcategories = [subcategories]

                # Tags can come from tags field or eligibility array
                tags = disc.get("tags", [])
                if isinstance(tags, str):
                    tags = [tags]

                states = disc.get("states", [])
                if isinstance(states, str):
                    states = [states]

                # Convert eligibility array to readable string
                eligibility_raw = disc.get("eligibility")
                if isinstance(eligibility_raw, list):
                    # Convert array like ["veteran", "housing"] to readable string
                    eligibility_map = {
                        "veteran": "Must be a veteran",
                        "housing": "For veterans experiencing homelessness or housing instability",
                        "homeless": "For veterans experiencing homelessness",  # Legacy support
                        "at_risk_homeless": "For veterans at risk of housing instability",
                        "low_income": "Income restrictions apply",
                        "disabled_veteran": "For disabled veterans",
                        "transitioning_military": "For transitioning service members",
                        "military_spouse": "Open to military spouses",
                        "military_family": "Open to military families",
                        "active_duty": "For active duty service members",
                    }
                    eligibility_parts = []
                    for e in eligibility_raw:
                        if e in eligibility_map:
                            eligibility_parts.append(eligibility_map[e])
                        else:
                            eligibility_parts.append(e.replace("_", " ").title())
                    eligibility_str = ". ".join(eligibility_parts) + "." if eligibility_parts else None
                    # Add eligibility items to tags for card display
                    tags = list(set(tags + eligibility_raw))
                elif isinstance(eligibility_raw, str):
                    eligibility_str = eligibility_raw
                else:
                    eligibility_str = None

                # Generate summary from description or notes (first sentence or 100 chars)
                summary = disc.get("summary")
                if not summary:
                    desc_text = description or ""
                    if ". " in desc_text:
                        summary = desc_text.split(". ")[0] + "."
                    elif len(desc_text) > 100:
                        summary = desc_text[:100].rsplit(" ", 1)[0] + "..."
                    else:
                        summary = desc_text if desc_text else None

                # Get suggested tier (affects reliability score)
                suggested_tier = disc.get("suggested_tier", 4)
                tier_scores = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4}
                reliability = tier_scores.get(suggested_tier, 0.4)

                # Get confidence score
                confidence = disc.get("confidence", 0.5)

                if dry_run:
                    print(f"  [{i}] Would import: {title} (confidence: {confidence:.2f})")
                    stats["imported"] += 1
                    continue

                # Create resource
                resource = Resource(
                    organization_id=org.id,
                    source_id=source.id,
                    title=title,
                    description=description,
                    summary=summary,
                    eligibility=eligibility_str,
                    how_to_apply=disc.get("how_to_apply"),
                    categories=categories,
                    subcategories=subcategories,
                    tags=tags,
                    scope=map_scope(disc.get("scope")),
                    states=states,
                    website=disc.get("website"),
                    phone=disc.get("phone"),
                    hours=disc.get("hours"),
                    cost=disc.get("cost", "Free") if disc.get("cost") else None,
                    source_url=source_url,
                    status=ResourceStatus.NEEDS_REVIEW,
                    freshness_score=confidence,
                    reliability_score=reliability,
                )
                session.add(resource)
                session.flush()

                # Create review queue entry
                discovery_notes = disc.get("discovery_notes") or disc.get("notes") or ""
                review_reason = f"AI-discovered resource (confidence: {confidence:.2f})"
                if discovery_notes:
                    review_reason += f" - {discovery_notes}"

                review = ReviewState(
                    resource_id=resource.id,
                    status=ReviewStatus.PENDING,
                    reason=review_reason,
                )
                session.add(review)

                print(f"  [{i}] Imported: {title}")
                stats["imported"] += 1

            except Exception as e:
                print(f"  [{i}] Error: {e}")
                stats["errors"] += 1
                continue

        if not dry_run:
            session.commit()

    # Print summary
    print("\n" + "=" * 50)
    print("Import Summary")
    print("=" * 50)
    print(f"  Resources imported:    {stats['imported']}")
    print(f"  Duplicates skipped:    {stats['duplicates_skipped']}")
    print(f"  Organizations created: {stats['orgs_created']}")
    print(f"  Organizations reused:  {stats['orgs_reused']}")
    print(f"  Errors:                {stats['errors']}")

    if not dry_run and stats["imported"] > 0:
        print(f"\n✓ {stats['imported']} resources added to review queue")
        print("  Review at: /admin (or via API: GET /api/v1/admin/review-queue)")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Import AI-discovered resources into the review queue"
    )
    parser.add_argument(
        "json_file",
        help="Path to discovery JSON file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without making changes"
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets"),
        help="Database URL (default: from DATABASE_URL env var)"
    )

    args = parser.parse_args()

    import_discoveries(args.json_file, args.database_url, args.dry_run)


if __name__ == "__main__":
    main()
