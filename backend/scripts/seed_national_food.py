#!/usr/bin/env python3
"""Seed script for national food assistance resources.

This script seeds food distribution resources from the food-national.json file
which contains enriched resources from the nationwide food assistance collection.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine, select

from app.models import Location, Organization, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus
from app.models.source import HealthStatus, SourceType

# Trust score mapping based on confidence
CONFIDENCE_TO_TIER = {
    0.9: 1,  # Official VA/government
    0.8: 2,  # Well-known nonprofit
    0.7: 3,  # Community organization
    0.6: 4,  # Limited info
}

TIER_SCORES = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4}

# State name to abbreviation mapping
STATE_ABBREVS = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR', 'california': 'CA',
    'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE', 'florida': 'FL', 'georgia': 'GA',
    'hawaii': 'HI', 'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA',
    'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS', 'missouri': 'MO',
    'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV', 'new hampshire': 'NH', 'new jersey': 'NJ',
    'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH',
    'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
    'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT', 'vermont': 'VT',
    'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY',
    'district of columbia': 'DC', 'washington dc': 'DC', 'dc': 'DC',
}


def normalize_state(state: str) -> str:
    """Normalize state to 2-letter abbreviation."""
    if not state:
        return ''
    state = state.strip()
    if len(state) == 2:
        return state.upper()
    return STATE_ABBREVS.get(state.lower(), state.upper()[:2])


def load_food_data() -> list[dict]:
    """Load food resources from JSON file."""
    data_path = Path(__file__).parent.parent / "data" / "food" / "food-national.json"
    if not data_path.exists():
        print(f"Error: {data_path} not found")
        return []

    with open(data_path) as f:
        return json.load(f)


def get_or_create_source(session: Session, name: str, url: str) -> Source:
    """Get existing source or create new one (idempotent)."""
    statement = select(Source).where(Source.name == name)
    existing = session.exec(statement).first()

    if existing:
        print(f"  Found existing source: {name}")
        return existing

    source = Source(
        name=name,
        url=url,
        source_type=SourceType.MANUAL,
        tier=2,
        health_status=HealthStatus.HEALTHY,
        last_success=datetime.utcnow(),
    )
    session.add(source)
    session.flush()
    print(f"  Created source: {name}")
    return source


def get_or_create_organization(session: Session, name: str, website: str | None = None) -> Organization:
    """Get existing organization or create new one (idempotent)."""
    statement = select(Organization).where(Organization.name == name)
    existing = session.exec(statement).first()

    if existing:
        return existing

    org = Organization(name=name, website=website)
    session.add(org)
    session.flush()
    return org


def resource_exists(session: Session, title: str, org_id) -> bool:
    """Check if a resource with this title and org already exists."""
    statement = select(Resource).where(Resource.title == title, Resource.organization_id == org_id)
    return session.exec(statement).first() is not None


def seed_national_food(database_url: str) -> None:
    """Seed national food resources into the database."""
    engine = create_engine(database_url, echo=False)

    resources_data = load_food_data()
    if not resources_data:
        print("No resources to seed")
        return

    print(f"Found {len(resources_data)} resources to seed")

    created = 0
    skipped = 0

    with Session(engine) as session:
        # Create source for national food data
        source = get_or_create_source(
            session,
            name="National Food Assistance Collection",
            url="https://vibe4vets.org/food",
        )

        for res_data in resources_data:
            # Get or create organization
            org_name = res_data.get("organization") or res_data.get("name", "Unknown Organization")
            org = get_or_create_organization(session, org_name, res_data.get("website"))

            # Use resource name as title
            title = res_data.get("name", "Unknown Resource")

            # Check if resource already exists (idempotent)
            if resource_exists(session, title, org.id):
                skipped += 1
                continue

            # Extract state
            state = normalize_state(res_data.get("state", ""))
            states = [state] if state else []

            # Calculate reliability score based on confidence
            confidence = res_data.get("confidence", 0.7)
            tier = 3  # Default
            for conf_threshold, tier_val in sorted(CONFIDENCE_TO_TIER.items(), reverse=True):
                if confidence >= conf_threshold:
                    tier = tier_val
                    break
            reliability = TIER_SCORES.get(tier, 0.6)

            # Create location if we have address info
            location = None
            if res_data.get("address") or res_data.get("city"):
                eligibility = res_data.get("eligibility", {})
                food_details = res_data.get("food_details", {})
                intake = res_data.get("intake", {})

                location = Location(
                    organization_id=org.id,
                    address=res_data.get("address", ""),
                    city=res_data.get("city", ""),
                    state=state,
                    zip_code=res_data.get("zip", ""),
                    service_area=[res_data.get("city", "")] if res_data.get("city") else [],
                    # Eligibility fields
                    veteran_status_required=eligibility.get("veteran_status_required", False),
                    docs_required=eligibility.get("docs_required", []),
                    # Food-specific fields
                    distribution_schedule=food_details.get("distribution_schedule"),
                    quantity_limit=food_details.get("quantity_limit"),
                    id_required=food_details.get("id_required", False),
                    # Intake fields
                    intake_phone=intake.get("phone") or res_data.get("phone"),
                    intake_hours=intake.get("hours"),
                    intake_notes=intake.get("notes"),
                )
                session.add(location)
                session.flush()

            # Create resource
            resource = Resource(
                organization_id=org.id,
                location_id=location.id if location else None,
                source_id=source.id,
                title=title,
                description=res_data.get("description", ""),
                summary=res_data.get("description", "")[:200] if res_data.get("description") else None,
                categories=["food"],
                subcategories=[res_data.get("subcategory")] if res_data.get("subcategory") else [],
                scope=ResourceScope.LOCAL,
                states=states,
                website=res_data.get("website"),
                phone=res_data.get("phone"),
                source_url=res_data.get("source_url"),
                status=ResourceStatus.ACTIVE,
                freshness_score=1.0,
                reliability_score=reliability,
                last_verified=datetime.utcnow(),
            )
            session.add(resource)
            created += 1

            if created % 50 == 0:
                print(f"  Progress: {created} created, {skipped} skipped")

        session.commit()

    print("\n" + "=" * 50)
    print("National Food seeding complete!")
    print(f"  Created: {created} resources")
    print(f"  Skipped: {skipped} existing resources")
    print("=" * 50)


if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets")
    seed_national_food(database_url)
