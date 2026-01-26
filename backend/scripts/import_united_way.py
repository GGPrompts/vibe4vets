#!/usr/bin/env python3
"""Import United Way regional veteran resources and Missions United programs.

This script imports veteran resources from regional United Way chapters,
with a focus on Missions United employment programs and other veteran services.

Usage:
    # Dry run (default) - shows what would be imported
    python scripts/import_united_way.py

    # Actually import
    python scripts/import_united_way.py --execute

    # Import with verbose output
    python scripts/import_united_way.py --execute --verbose
"""

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine, select

from app.models import Location, Organization, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus
from app.models.source import HealthStatus, SourceType

# Default data directory
DATA_DIR = Path(__file__).parent.parent / "data" / "united_way"

# Trust score mapping based on tier
TIER_SCORES = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4}

# United Way is tier 2 (established nonprofit network)
UNITED_WAY_TIER = 2
UNITED_WAY_RELIABILITY = TIER_SCORES[UNITED_WAY_TIER]

# Missions United eligibility (more specific)
MISSIONS_UNITED_ELIGIBILITY = (
    "Veterans, active-duty service members, National Guard, Reservists, "
    "and their families. Some programs may have additional income or "
    "service requirements."
)

# General United Way eligibility (broader)
GENERAL_ELIGIBILITY = (
    "Eligibility varies by program. Many United Way veteran programs "
    "serve all veterans and their families. Contact the program directly "
    "for specific eligibility requirements."
)

# Category mapping from United Way services
SERVICE_CATEGORY_MAP = {
    # Missions United core services -> employment
    "missions united": "employment",
    "veteran employment": "employment",
    "career coaching": "employment",
    "job readiness": "employment",
    "resume assistance": "employment",
    "interview preparation": "employment",
    "job placement": "employment",
    "career transition": "employment",
    "workforce development": "employment",
    "job training": "employment",
    "vocational training": "employment",
    "career training": "employment",
    # Housing
    "housing assistance": "housing",
    "housing stability": "housing",
    "rental assistance": "housing",
    "emergency housing": "housing",
    "homelessness prevention": "housing",
    "transitional housing": "housing",
    # Legal
    "legal assistance": "legal",
    "legal aid": "legal",
    "legal services": "legal",
    # Training (vocational)
    "education assistance": "training",
    "GI Bill assistance": "training",
    "education benefits": "training",
}


def map_categories(services: list[str]) -> list[str]:
    """Map United Way service tags to vibe4vets categories."""
    categories = set()

    for service in services:
        service_lower = service.lower().strip()
        if service_lower in SERVICE_CATEGORY_MAP:
            categories.add(SERVICE_CATEGORY_MAP[service_lower])
        else:
            # Try partial matching
            for key, category in SERVICE_CATEGORY_MAP.items():
                if key in service_lower or service_lower in key:
                    categories.add(category)
                    break

    # Filter to only include primary categories from taxonomy
    primary_categories = {"employment", "training", "housing", "legal"}
    return sorted([c for c in categories if c in primary_categories])


def determine_scope(state: str | None, service_area: str | None) -> ResourceScope:
    """Determine resource scope based on state and service area."""
    if service_area:
        service_lower = service_area.lower()
        if "statewide" in service_lower:
            return ResourceScope.STATE
        if "county" in service_lower or "metro" in service_lower:
            return ResourceScope.LOCAL
    return ResourceScope.LOCAL


def is_missions_united(resource: dict) -> bool:
    """Check if resource is a Missions United program."""
    name = resource.get("name", "").lower()
    services = [s.lower() for s in resource.get("services", [])]

    missions_terms = ["missions united", "mission united"]

    for term in missions_terms:
        if term in name:
            return True
        for service in services:
            if term in service:
                return True

    return resource.get("is_missions_united", False)


def get_or_create_source(session: Session, dry_run: bool = True) -> Source:
    """Get or create the United Way data source."""
    statement = select(Source).where(Source.name == "United Way Regional Directories")
    existing = session.exec(statement).first()

    if existing:
        return existing

    source = Source(
        name="United Way Regional Directories",
        url="https://www.unitedway.org/local/united-states",
        source_type=SourceType.MANUAL,  # Pre-fetched data
        tier=UNITED_WAY_TIER,
        health_status=HealthStatus.HEALTHY,
        last_success=datetime.now(UTC),
    )

    if not dry_run:
        session.add(source)
        session.flush()

    return source


def get_or_create_organization(
    session: Session, name: str, website: str | None = None, dry_run: bool = True
) -> Organization:
    """Get existing organization by name or create new one."""
    statement = select(Organization).where(Organization.name == name)
    existing = session.exec(statement).first()

    if existing:
        # Update website if we have one and org doesn't
        if website and not existing.website and not dry_run:
            existing.website = website
        return existing

    org = Organization(
        id=uuid4(),
        name=name,
        website=website,
    )

    if not dry_run:
        session.add(org)
        session.flush()

    return org


def find_existing_resource(session: Session, title: str, org_id) -> Resource | None:
    """Find existing resource by title and org."""
    statement = select(Resource).where(Resource.title == title, Resource.organization_id == org_id)
    return session.exec(statement).first()


def import_united_way(
    database_url: str,
    data_dir: Path = DATA_DIR,
    dry_run: bool = True,
    verbose: bool = False,
) -> dict:
    """Import United Way resources from regional JSON files.

    Args:
        database_url: PostgreSQL connection string
        data_dir: Path to directory containing regional JSON files
        dry_run: If True, don't commit changes (default)
        verbose: If True, print detailed progress

    Returns:
        dict with import statistics
    """
    engine = create_engine(database_url, echo=False)

    stats = {
        "total": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "missions_united": 0,
        "by_region": {},
        "by_category": {},
        "errors": [],
    }

    # Find all JSON files in data directory
    json_files = sorted(data_dir.glob("*.json"))

    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return stats

    with Session(engine) as session:
        source = get_or_create_source(session, dry_run=dry_run)

        for json_file in json_files:
            region = json_file.stem
            if verbose:
                print(f"\n📁 Processing {region}...")

            try:
                with open(json_file) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                stats["errors"].append({"region": region, "error": str(e)})
                print(f"  ✗ Error loading {json_file}: {e}")
                continue

            resources = data.get("resources", [])
            region_name = data.get("region_name", region)
            region_count = 0

            for resource in resources:
                stats["total"] += 1
                name = resource.get("name", "").strip()
                if not name:
                    continue

                try:
                    org_name = resource.get("org_name", "United Way")
                    title = name  # Use resource name directly as title

                    # Get or create organization
                    org = get_or_create_organization(
                        session, org_name, resource.get("website"), dry_run=dry_run
                    )

                    # Check for existing resource
                    existing = find_existing_resource(session, title, org.id)
                    if existing:
                        stats["skipped"] += 1
                        if verbose:
                            print(f"  Skipping existing: {title}")
                        continue

                    # Determine if Missions United program
                    is_mu = is_missions_united(resource)
                    if is_mu:
                        stats["missions_united"] += 1

                    # Map categories
                    services = resource.get("services", [])
                    categories = map_categories(services)
                    if not categories:
                        # Default category based on program type
                        categories = ["employment"] if is_mu else ["support"]

                    # Track categories
                    for cat in categories:
                        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

                    # Build subcategories from services
                    subcategories = ["united-way"]
                    if is_mu:
                        subcategories.append("missions-united")
                    subcategories.append(f"uw-{region}")

                    # Determine scope
                    state = resource.get("state", "")
                    service_area = resource.get("service_area")
                    scope = determine_scope(state, service_area)

                    # Build eligibility
                    eligibility = resource.get("eligibility")
                    if not eligibility:
                        eligibility = MISSIONS_UNITED_ELIGIBILITY if is_mu else GENERAL_ELIGIBILITY

                    # Create location
                    location = Location(
                        id=uuid4(),
                        organization_id=org.id,
                        address=resource.get("address", ""),
                        city=resource.get("city", ""),
                        state=state,
                        zip_code=resource.get("zip_code", ""),
                        # Intake
                        intake_phone=resource.get("phone"),
                        intake_notes=resource.get("hours"),
                        # Verification
                        last_verified_at=datetime.now(UTC),
                        verified_by="united_way_import",
                    )

                    # Build description
                    description = resource.get("description", "")
                    if not description:
                        if services:
                            description = f"United Way {region_name} program. Services: {', '.join(services)}"
                        else:
                            description = f"United Way {region_name} veteran resource."

                    # Create resource
                    resource_obj = Resource(
                        id=uuid4(),
                        organization_id=org.id,
                        location_id=location.id,
                        source_id=source.id,
                        title=title,
                        description=description,
                        summary=f"{'Missions United' if is_mu else 'United Way'} veteran program in {region_name}",
                        eligibility=eligibility,
                        how_to_apply=resource.get("how_to_apply"),
                        categories=categories,
                        subcategories=subcategories,
                        scope=scope,
                        states=[state] if state else [],
                        website=resource.get("website"),
                        phone=resource.get("phone"),
                        email=resource.get("email"),
                        source_url=resource.get("source_url", resource.get("website")),
                        status=ResourceStatus.ACTIVE,
                        freshness_score=1.0,
                        reliability_score=UNITED_WAY_RELIABILITY,
                        last_verified=datetime.now(UTC),
                    )

                    if not dry_run:
                        session.add(location)
                        session.add(resource_obj)

                    stats["created"] += 1
                    region_count += 1
                    if verbose:
                        mu_marker = " [Missions United]" if is_mu else ""
                        print(f"  ✓ Created: {title}{mu_marker}")

                except Exception as e:
                    stats["errors"].append({"resource": name, "error": str(e)})
                    print(f"  ✗ Error importing {name}: {e}")

            stats["by_region"][region] = region_count

        if not dry_run:
            session.commit()
            print("\n✓ Changes committed to database")
        else:
            print("\n⚠️  DRY RUN - no changes made. Use --execute to import.")

    return stats


def print_summary(stats: dict):
    """Print import summary."""
    print("\n" + "=" * 60)
    print("United Way Import Summary")
    print("=" * 60)
    print(f"  Total resources:     {stats['total']}")
    print(f"  Created:             {stats['created']}")
    print(f"  Skipped (existing):  {stats['skipped']}")
    print(f"  Missions United:     {stats['missions_united']}")

    if stats["by_region"]:
        print("\n  By Region:")
        for region, count in sorted(stats["by_region"].items()):
            print(f"    {region}: {count}")

    if stats["by_category"]:
        print("\n  By Category:")
        for cat, count in sorted(stats["by_category"].items(), key=lambda x: -x[1]):
            print(f"    {cat}: {count}")

    if stats["errors"]:
        print(f"\n  Errors: {len(stats['errors'])}")
        for err in stats["errors"][:5]:
            if "region" in err:
                print(f"    - {err['region']}: {err['error']}")
            else:
                print(f"    - {err['resource']}: {err['error']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Import United Way veteran resources into the database")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually import (default is dry run)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help=f"Path to data directory (default: {DATA_DIR})",
    )
    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets")

    dry_run = not args.execute
    if dry_run:
        print("🔍 DRY RUN MODE - no changes will be made")
    else:
        print("🚀 EXECUTE MODE - importing to database")

    stats = import_united_way(
        database_url=database_url,
        data_dir=args.data_dir,
        dry_run=dry_run,
        verbose=args.verbose,
    )

    print_summary(stats)


if __name__ == "__main__":
    main()
