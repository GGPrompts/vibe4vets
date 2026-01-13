#!/usr/bin/env python3
"""Idempotent seed script for hub pages with curated veteran resources."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine, select

from app.models import Organization, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus
from app.models.source import HealthStatus, SourceType

# Directory containing hub JSON files
HUBS_DIR = Path(__file__).parent.parent / "data" / "hubs"

# Trust score mapping based on tier
TIER_SCORES = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4}

# Scope string to enum mapping
SCOPE_MAP = {
    "national": ResourceScope.NATIONAL,
    "state": ResourceScope.STATE,
    "local": ResourceScope.LOCAL,
}


def load_hub_data(category: str) -> dict | None:
    """Load hub data from JSON file."""
    hub_file = HUBS_DIR / f"{category}.json"
    if not hub_file.exists():
        print(f"  Warning: Hub file not found: {hub_file}")
        return None

    with open(hub_file) as f:
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
        tier=1,  # Hub data is curated, treat as reliable
        health_status=HealthStatus.HEALTHY,
        last_success=datetime.utcnow(),
    )
    session.add(source)
    session.flush()
    print(f"  Created source: {name}")
    return source


def get_or_create_organization(
    session: Session, name: str, website: str | None = None
) -> Organization:
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
    statement = select(Resource).where(
        Resource.title == title, Resource.organization_id == org_id
    )
    return session.exec(statement).first() is not None


def seed_hub(session: Session, category: str, source: Source) -> tuple[int, int]:
    """
    Seed resources from a hub JSON file.

    Returns:
        Tuple of (created_count, skipped_count)
    """
    hub_data = load_hub_data(category)
    if not hub_data:
        return 0, 0

    created = 0
    skipped = 0

    for res_data in hub_data.get("resources", []):
        # Get or create organization
        org_name = res_data.get("org_name", "Unknown Organization")
        org_website = res_data.get("website")
        org = get_or_create_organization(session, org_name, org_website)

        # Check if resource already exists (idempotent)
        if resource_exists(session, res_data["title"], org.id):
            print(f"    Skipping existing: {res_data['title']}")
            skipped += 1
            continue

        # Calculate reliability score based on tier
        tier = res_data.get("tier", 2)
        reliability = TIER_SCORES.get(tier, 0.5)

        # Map scope string to enum
        scope_str = res_data.get("scope", "national")
        scope = SCOPE_MAP.get(scope_str, ResourceScope.NATIONAL)

        # Create resource
        resource = Resource(
            organization_id=org.id,
            source_id=source.id,
            title=res_data["title"],
            description=res_data["description"],
            summary=res_data.get("summary"),
            eligibility=res_data.get("eligibility"),
            how_to_apply=res_data.get("how_to_apply"),
            categories=[category],
            subcategories=res_data.get("subcategories", []),
            scope=scope,
            states=res_data.get("states", []),
            website=res_data.get("website"),
            phone=res_data.get("phone"),
            cost=res_data.get("cost"),
            source_url=res_data.get("website"),
            status=ResourceStatus.ACTIVE,
            freshness_score=1.0,
            reliability_score=reliability,
            last_verified=datetime.utcnow(),
        )
        session.add(resource)
        created += 1
        print(f"    Created: {res_data['title']}")

    return created, skipped


def seed_all_hubs(database_url: str) -> None:
    """Seed all hub categories into the database."""
    engine = create_engine(database_url, echo=False)

    categories = ["employment", "housing", "legal", "training"]

    total_created = 0
    total_skipped = 0

    with Session(engine) as session:
        # Create a single source for all hub data
        source = get_or_create_source(
            session,
            name="Vibe4Vets Hub Data",
            url="https://vibe4vets.org/hubs",
        )

        for category in categories:
            print(f"\nProcessing {category} hub...")
            created, skipped = seed_hub(session, category, source)
            total_created += created
            total_skipped += skipped

        session.commit()

    print("\n" + "=" * 50)
    print("Hub seeding complete!")
    print(f"  Created: {total_created} resources")
    print(f"  Skipped: {total_skipped} existing resources")
    print("=" * 50)


if __name__ == "__main__":
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets"
    )
    seed_all_hubs(database_url)
