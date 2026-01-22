#!/usr/bin/env python3
"""Seed script for discovered benefits resources from JSON files.

Loads benefits resources from backend/data/discovery/benefits-*.json files
and seeds them into the database. Handles deduplication by checking for
existing resources with the same title and organization.

Usage:
    python scripts/seed_discovered_benefits.py
    python scripts/seed_discovered_benefits.py --dry-run
"""

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

# Trust score mapping based on source type
CONFIDENCE_TIERS = {
    (0.9, 1.0): 1,  # Very high confidence = Tier 1
    (0.7, 0.9): 2,  # High confidence = Tier 2
    (0.5, 0.7): 3,  # Medium confidence = Tier 3
    (0.0, 0.5): 4,  # Low confidence = Tier 4
}

TIER_SCORES = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4}

# State abbreviation mapping
STATE_ABBREV = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
}


def get_tier_from_confidence(confidence: float) -> int:
    """Map confidence score to tier."""
    for (low, high), tier in CONFIDENCE_TIERS.items():
        if low <= confidence < high:
            return tier
    return 3  # Default to tier 3


def normalize_state(state: str) -> str:
    """Normalize state to 2-letter abbreviation."""
    if len(state) == 2:
        return state.upper()
    return STATE_ABBREV.get(state, state)


def parse_address(address: str, city: str, state: str) -> dict:
    """Parse address components, extracting zip if present."""
    zip_code = ""

    # Try to extract zip from address
    import re

    zip_match = re.search(r"\b(\d{5}(?:-\d{4})?)\b", address)
    if zip_match:
        zip_code = zip_match.group(1)

    return {
        "address": address,
        "city": city,
        "state": normalize_state(state),
        "zip_code": zip_code,
    }


def map_subcategory(subcategory: str) -> str:
    """Map discovered subcategories to our taxonomy."""
    mapping = {
        "vso-services": "vso-services",
        "disability-claims": "disability-claims",
        "pension": "pension",
        "survivor-benefits": "survivor-benefits",
        "appeals": "va-appeals",
        "state-benefits": "state-benefits",
        "healthcare-enrollment": "healthcare-enrollment",
        "education-benefits": "education-benefits",
        "cvso": "cvso",
    }
    return mapping.get(subcategory, subcategory)


def determine_scope(coverage_area: str, state: str) -> tuple[ResourceScope, list[str]]:
    """Determine resource scope from coverage area."""
    coverage_lower = coverage_area.lower() if coverage_area else ""

    if "national" in coverage_lower or "nationwide" in coverage_lower:
        return ResourceScope.NATIONAL, []
    elif "statewide" in coverage_lower or "state" in coverage_lower:
        return ResourceScope.STATE, [normalize_state(state)]
    else:
        # Local/county scope
        return ResourceScope.LOCAL, [normalize_state(state)]


def load_discovery_files(data_dir: Path) -> list[dict]:
    """Load all benefits discovery JSON files."""
    resources = []

    for json_file in data_dir.glob("benefits-*.json"):
        print(f"Loading {json_file.name}...")
        try:
            with open(json_file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    resources.extend(data)
                    print(f"  Loaded {len(data)} resources")
                else:
                    print(f"  Warning: {json_file.name} is not a list")
        except json.JSONDecodeError as e:
            print(f"  Error parsing {json_file.name}: {e}")

    return resources


def get_or_create_source(session: Session, region: str) -> Source:
    """Get existing source or create new one for discovered data."""
    name = f"AI Discovery - Benefits ({region})"
    statement = select(Source).where(Source.name == name)
    existing = session.exec(statement).first()

    if existing:
        return existing

    source = Source(
        name=name,
        url="https://vibe4vets.org/discovery",
        source_type=SourceType.SCRAPE,  # AI-discovered via web scraping
        tier=3,  # AI-discovered data starts at tier 3
        health_status=HealthStatus.HEALTHY,
        last_success=datetime.now(UTC),
    )
    session.add(source)
    session.flush()
    return source


def get_or_create_organization(session: Session, name: str, website: str | None = None) -> Organization:
    """Get existing organization or create new one."""
    statement = select(Organization).where(Organization.name == name)
    existing = session.exec(statement).first()

    if existing:
        return existing

    org = Organization(name=name, website=website)
    session.add(org)
    session.flush()
    return org


def resource_exists(session: Session, title: str, org_id, city: str, state: str) -> bool:
    """Check if a resource with this title, org, and location already exists."""
    # Join with location to check city/state
    statement = (
        select(Resource)
        .join(Location)
        .where(
            Resource.title == title,
            Resource.organization_id == org_id,
            Location.city == city,
            Location.state == state,
        )
    )
    return session.exec(statement).first() is not None


def seed_discovered_benefits(database_url: str, dry_run: bool = False) -> None:
    """Seed discovered benefits resources into the database."""
    data_dir = Path(__file__).parent.parent / "data" / "discovery"

    if not data_dir.exists():
        print(f"Error: Discovery data directory not found: {data_dir}")
        return

    # Load all discovery files
    resources = load_discovery_files(data_dir)
    print(f"\nTotal resources loaded: {len(resources)}")

    if not resources:
        print("No resources to seed.")
        return

    if dry_run:
        print("\n[DRY RUN] Would seed the following resources:")
        for res in resources[:10]:
            print(f"  - {res.get('name')} ({res.get('city')}, {res.get('state')})")
        if len(resources) > 10:
            print(f"  ... and {len(resources) - 10} more")
        return

    engine = create_engine(database_url, echo=False)

    created = 0
    skipped = 0
    errors = 0

    with Session(engine) as session:
        # Create source for discovered data
        source = get_or_create_source(session, "Multi-Region")
        print(f"\nUsing source: {source.name}")

        for res_data in resources:
            try:
                # Extract basic info
                name = res_data.get("name", "Unknown Resource")
                org_name = res_data.get("organization", name.split(" - ")[0] if " - " in name else name)
                city = res_data.get("city", "")
                state = normalize_state(res_data.get("state", ""))

                if not city or not state:
                    print(f"  Skipping (missing location): {name}")
                    skipped += 1
                    continue

                # Get or create organization
                org = get_or_create_organization(session, org_name, res_data.get("website"))

                # Check if resource already exists
                if resource_exists(session, name, org.id, city, state):
                    print(f"  Skipping existing: {name}")
                    skipped += 1
                    continue

                # Parse address
                addr_info = parse_address(res_data.get("address", ""), city, state)

                # Determine scope
                scope, states = determine_scope(res_data.get("coverage_area", ""), state)

                # Map eligibility
                eligibility = res_data.get("eligibility", {})

                # Map services to benefits types
                services = res_data.get("services", [])
                benefits_types = []
                service_mapping = {
                    "disability": ["disability", "compensation"],
                    "pension": ["pension"],
                    "healthcare": ["healthcare", "medical"],
                    "education": ["education", "gi bill"],
                    "survivor": ["survivor", "dic", "dependent"],
                    "burial": ["burial", "memorial"],
                }
                for benefit_type, keywords in service_mapping.items():
                    for service in services:
                        if any(kw in service.lower() for kw in keywords):
                            if benefit_type not in benefits_types:
                                benefits_types.append(benefit_type)
                            break

                # Create location
                location = Location(
                    id=uuid4(),
                    organization_id=org.id,
                    address=addr_info["address"],
                    city=addr_info["city"],
                    state=addr_info["state"],
                    zip_code=addr_info["zip_code"],
                    service_area=[res_data.get("coverage_area", "")] if res_data.get("coverage_area") else [],
                    # Eligibility fields
                    veteran_status_required=eligibility.get("veteran_status_required", True),
                    docs_required=eligibility.get("docs_required", []),
                    # Benefits-specific fields
                    benefits_types_supported=benefits_types,
                    accredited=True,  # Assume VSOs are accredited
                    walk_in_available=not res_data.get("appointment_required", False),
                    appointment_required=res_data.get("appointment_required", False),
                    free_service=res_data.get("cost", "").lower() == "free",
                    # Intake fields
                    intake_phone=res_data.get("phone"),
                    intake_url=res_data.get("website"),
                    intake_hours=res_data.get("hours"),
                    intake_notes=res_data.get("notes"),
                    # Verification
                    last_verified_at=datetime.now(UTC),
                    verified_by="ai_discovery",
                )
                session.add(location)
                session.flush()

                # Calculate reliability from confidence
                confidence = res_data.get("confidence", 0.7)
                tier = get_tier_from_confidence(confidence)
                reliability = TIER_SCORES.get(tier, 0.6)

                # Map subcategories
                subcategories = [map_subcategory(s) for s in res_data.get("subcategory", "").split("|") if s]
                if not subcategories:
                    subcategories = ["vso-services"]

                # Create resource
                resource = Resource(
                    organization_id=org.id,
                    location_id=location.id,
                    source_id=source.id,
                    title=name,
                    description=res_data.get("description", ""),
                    summary=res_data.get("description", "")[:200] if res_data.get("description") else None,
                    categories=["benefits"],
                    subcategories=subcategories,
                    scope=scope,
                    states=states if states else [state],
                    website=res_data.get("website"),
                    source_url=res_data.get("source_url"),
                    status=ResourceStatus.ACTIVE,
                    freshness_score=1.0,
                    reliability_score=reliability,
                    last_verified=datetime.now(UTC),
                )
                session.add(resource)
                created += 1
                print(f"  Created: {name} ({city}, {state})")

            except Exception as e:
                print(f"  Error processing {res_data.get('name', 'unknown')}: {e}")
                errors += 1
                continue

        session.commit()

    print("\n" + "=" * 60)
    print("Discovered Benefits seeding complete!")
    print(f"  Created: {created} resources")
    print(f"  Skipped: {skipped} existing/invalid resources")
    print(f"  Errors:  {errors}")
    print("=" * 60)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets")
    seed_discovered_benefits(database_url, dry_run=dry_run)
