#!/usr/bin/env python3
"""Import enriched SSVF (Supportive Services for Veteran Families) providers.

This script imports 234 SSVF providers from the FY26 awards list, enriched with
website, phone, address, intake process, and service area information.

Usage:
    # Dry run (default) - shows what would be imported
    python scripts/import_ssvf_providers.py

    # Actually import
    python scripts/import_ssvf_providers.py --execute

    # Import with verbose output
    python scripts/import_ssvf_providers.py --execute --verbose
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine, select

from app.models import Location, Organization, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus
from app.models.source import HealthStatus, SourceType

# Default data file location
DATA_FILE = Path(__file__).parent.parent / "data" / "ssvf" / "ssvf-enriched-all.json"

# Trust score mapping based on tier
TIER_SCORES = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4}

# SSVF is tier 1-2 (VA-funded program)
SSVF_TIER = 2
SSVF_RELIABILITY = TIER_SCORES[SSVF_TIER]

# Standard SSVF eligibility
SSVF_ELIGIBILITY = (
    "Veterans and veteran families at risk of homelessness or currently homeless. "
    "Must have served in the U.S. military and received an honorable or other than "
    "dishonorable discharge. Income must be at or below 50% of Area Median Income (AMI)."
)


def parse_states(state_str: str) -> list[str]:
    """Parse state field which may contain multiple states separated by semicolons.

    Examples:
        "AK" -> ["AK"]
        "AL;FL" -> ["AL", "FL"]
        "AZ;CA;NV" -> ["AZ", "CA", "NV"]
    """
    if not state_str:
        return []
    return [s.strip().upper() for s in state_str.split(";") if s.strip()]


def determine_scope(states: list[str], service_area: str) -> ResourceScope:
    """Determine resource scope based on states and service area.

    - Multiple states = STATE or REGIONAL
    - Single state with statewide service = STATE
    - Single state with local service = LOCAL
    """
    if len(states) > 1:
        return ResourceScope.STATE  # Multi-state providers
    if len(states) == 1:
        # Check if service area mentions statewide or multiple counties
        service_lower = (service_area or "").lower()
        if "statewide" in service_lower or "all counties" in service_lower:
            return ResourceScope.STATE
    return ResourceScope.LOCAL


def get_or_create_source(session: Session, dry_run: bool = True) -> Source:
    """Get or create the SSVF data source."""
    statement = select(Source).where(Source.name == "VA SSVF Program Directory")
    existing = session.exec(statement).first()

    if existing:
        return existing

    source = Source(
        name="VA SSVF Program Directory",
        url="https://www.va.gov/homeless/ssvf/",
        source_type=SourceType.MANUAL,  # AI-enriched data
        tier=SSVF_TIER,
        health_status=HealthStatus.HEALTHY,
        last_success=datetime.now(timezone.utc),
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
    """Find existing SSVF resource by title pattern and org."""
    statement = select(Resource).where(
        Resource.title == title, Resource.organization_id == org_id
    )
    return session.exec(statement).first()


def import_ssvf_providers(
    database_url: str,
    data_file: Path = DATA_FILE,
    dry_run: bool = True,
    verbose: bool = False,
) -> dict:
    """Import SSVF providers from enriched JSON file.

    Args:
        database_url: PostgreSQL connection string
        data_file: Path to ssvf-enriched-all.json
        dry_run: If True, don't commit changes (default)
        verbose: If True, print detailed progress

    Returns:
        dict with import statistics
    """
    # Load data
    with open(data_file) as f:
        providers = json.load(f)

    engine = create_engine(database_url, echo=False)

    stats = {
        "total": len(providers),
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "low_confidence": 0,
        "multi_state": 0,
        "errors": [],
    }

    with Session(engine) as session:
        source = get_or_create_source(session, dry_run=dry_run)

        for provider in providers:
            grant_id = provider.get("grant_id", "unknown")
            try:
                org_name = provider["org_name"]
                title = f"{org_name} - SSVF Program"

                # Parse states (handle multi-state like "AL;FL")
                states = parse_states(provider.get("state", ""))
                if len(states) > 1:
                    stats["multi_state"] += 1

                # Track low confidence records
                confidence = provider.get("confidence", 0.5)
                if confidence < 0.5:
                    stats["low_confidence"] += 1
                    if verbose:
                        print(f"  ⚠️  Low confidence ({confidence}): {org_name}")

                # Get or create organization
                org = get_or_create_organization(
                    session, org_name, provider.get("website"), dry_run=dry_run
                )

                # Check for existing resource
                existing = find_existing_resource(session, title, org.id)
                if existing:
                    stats["skipped"] += 1
                    if verbose:
                        print(f"  Skipping existing: {title}")
                    continue

                # Determine scope
                service_area = provider.get("service_area", "")
                scope = determine_scope(states, service_area)

                # Calculate reliability score (tier-based, adjusted by confidence)
                reliability = SSVF_RELIABILITY * min(confidence + 0.2, 1.0)

                # Build location (first state for physical location)
                primary_state = states[0] if states else ""
                city = provider.get("city", "")
                # Handle multi-city like "Birmingham, AL; Pensacola, FL"
                if ";" in city:
                    city = city.split(";")[0].strip()
                    # Remove state suffix if present
                    if "," in city:
                        city = city.split(",")[0].strip()

                zip_code = provider.get("zip", "")
                # Handle multi-zip like "35222 (AL); 32502 (FL)" or "32922/32905"
                if ";" in zip_code:
                    zip_code = zip_code.split(";")[0].strip()
                if "/" in zip_code:
                    zip_code = zip_code.split("/")[0].strip()
                if "(" in zip_code:
                    zip_code = zip_code.split("(")[0].strip()
                # Extract just the zip portion (first 5 or 10 chars for ZIP+4)
                parts = zip_code.split()
                zip_code = parts[0] if parts else zip_code
                # Ensure it fits in varchar(10)
                zip_code = zip_code[:10]

                location = Location(
                    id=uuid4(),
                    organization_id=org.id,
                    address=provider.get("address", ""),
                    city=city,
                    state=primary_state,
                    zip_code=zip_code,
                    service_area=[service_area] if service_area else [],
                    # Eligibility
                    income_limit_type="ami_percent",
                    income_limit_ami_percent=50,
                    housing_status_required=["homeless", "at_risk"],
                    veteran_status_required=True,
                    docs_required=["DD-214", "Income verification", "Photo ID"],
                    # Intake
                    intake_phone=provider.get("phone"),
                    intake_notes=provider.get("intake_process"),
                    # Verification
                    last_verified_at=datetime.now(timezone.utc),
                    verified_by="ai_enrichment",
                )

                # Create resource
                resource = Resource(
                    id=uuid4(),
                    organization_id=org.id,
                    location_id=location.id,
                    source_id=source.id,
                    title=title,
                    description=(
                        f"Supportive Services for Veteran Families (SSVF) program operated by "
                        f"{org_name}. SSVF provides housing assistance, case management, and "
                        f"supportive services to very low-income veteran families who are "
                        f"experiencing homelessness or at risk of housing instability."
                    ),
                    summary=f"SSVF rapid re-housing and homelessness prevention services for veteran families",
                    eligibility=SSVF_ELIGIBILITY,
                    how_to_apply=provider.get("intake_process"),
                    categories=["housing"],
                    subcategories=["ssvf", "rapid_rehousing", "homelessness_prevention"],
                    scope=scope,
                    states=states,
                    website=provider.get("website"),
                    phone=provider.get("phone"),
                    source_url=provider.get("source_url"),
                    status=ResourceStatus.NEEDS_REVIEW if confidence < 0.5 else ResourceStatus.ACTIVE,
                    freshness_score=1.0,
                    reliability_score=reliability,
                    last_verified=datetime.now(timezone.utc),
                )

                if not dry_run:
                    session.add(location)
                    session.add(resource)

                stats["created"] += 1
                if verbose:
                    state_str = ";".join(states)
                    print(f"  ✓ Created: {title} ({state_str})")

            except Exception as e:
                stats["errors"].append({"grant_id": grant_id, "error": str(e)})
                print(f"  ✗ Error importing {provider.get('org_name', 'unknown')}: {e}")

        if not dry_run:
            session.commit()
            print("\n✓ Changes committed to database")
        else:
            print("\n⚠️  DRY RUN - no changes made. Use --execute to import.")

    return stats


def print_summary(stats: dict):
    """Print import summary."""
    print("\n" + "=" * 60)
    print("SSVF Import Summary")
    print("=" * 60)
    print(f"  Total providers:    {stats['total']}")
    print(f"  Created:            {stats['created']}")
    print(f"  Updated:            {stats['updated']}")
    print(f"  Skipped (existing): {stats['skipped']}")
    print(f"  Multi-state:        {stats['multi_state']}")
    print(f"  Low confidence:     {stats['low_confidence']}")
    if stats["errors"]:
        print(f"  Errors:             {len(stats['errors'])}")
        for err in stats["errors"][:5]:
            print(f"    - {err['grant_id']}: {err['error']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Import enriched SSVF providers into the database"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually import (default is dry run)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=DATA_FILE,
        help=f"Path to enriched JSON (default: {DATA_FILE})",
    )
    args = parser.parse_args()

    database_url = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets"
    )

    dry_run = not args.execute
    if dry_run:
        print("🔍 DRY RUN MODE - no changes will be made")
    else:
        print("🚀 EXECUTE MODE - importing to database")

    stats = import_ssvf_providers(
        database_url=database_url,
        data_file=args.data_file,
        dry_run=dry_run,
        verbose=args.verbose,
    )

    print_summary(stats)


if __name__ == "__main__":
    main()
