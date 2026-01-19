#!/usr/bin/env python3
"""Seed script for DC/MD/VA food distribution resources with eligibility data.

This script seeds food distribution resources for the DMV (DC/MD/VA) area with
structured eligibility fields for the eligibility wizard feature.
"""

import os
import sys
from datetime import datetime
from uuid import uuid4

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine, select

from app.models import Location, Organization, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus
from app.models.source import HealthStatus, SourceType

# Trust score mapping based on tier
TIER_SCORES = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4}

# DMV Food Distribution Resources data
DMV_FOOD_RESOURCES = [
    # Capital Area Food Bank - Main Distribution
    {
        "org_name": "Capital Area Food Bank",
        "title": "CAFB Veterans Food Distribution - DC Main Site",
        "description": (
            "Monthly food distribution specifically for veterans and their families in Washington DC. "
            "Provides a variety of shelf-stable foods, fresh produce when available, and frozen proteins. "
            "Veterans receive priority service and additional portions."
        ),
        "summary": "Monthly veteran-focused food distribution with fresh produce and proteins",
        "categories": ["food"],
        "subcategories": ["food-pantry", "mobile-distribution"],
        "scope": "local",
        "states": ["DC"],
        "tier": 2,
        "website": "https://www.capitalareafoodbank.org/find-food",
        "location": {
            "address": "4900 Puerto Rico Ave NE",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20017",
            "service_area": ["Washington DC"],
            "eligibility": {
                "veteran_status_required": False,
                "docs_required": [],
                "waitlist_status": "open",
            },
            "food": {
                "distribution_schedule": "First Saturday of each month, 9:00 AM - 12:00 PM",
                "serves_dietary": ["vegetarian", "gluten_free"],
                "quantity_limit": "One box per household per month",
                "id_required": False,
            },
            "intake": {
                "phone": "202-644-9800",
                "url": "https://www.capitalareafoodbank.org/find-food",
                "hours": "Distribution day only",
                "notes": "No appointment needed. Veterans line available for faster service.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 15),
                "verified_by": "provider_contact",
            },
        },
    },
    {
        "org_name": "Capital Area Food Bank",
        "title": "CAFB Mobile Market - Alexandria VA",
        "description": (
            "Weekly mobile food market serving the Alexandria community with fresh produce, "
            "dairy products, and pantry staples. Open to all residents including veterans "
            "and military families."
        ),
        "summary": "Weekly mobile market with fresh produce in Alexandria",
        "categories": ["food"],
        "subcategories": ["mobile-distribution"],
        "scope": "local",
        "states": ["VA"],
        "tier": 2,
        "website": "https://www.capitalareafoodbank.org/mobile-market",
        "location": {
            "address": "2355 Mill Rd",
            "city": "Alexandria",
            "state": "VA",
            "zip_code": "22314",
            "service_area": ["Alexandria City", "Arlington County"],
            "eligibility": {
                "veteran_status_required": False,
                "docs_required": [],
                "waitlist_status": "open",
            },
            "food": {
                "distribution_schedule": "Every Wednesday, 10:00 AM - 1:00 PM",
                "serves_dietary": ["vegetarian", "halal", "kosher"],
                "quantity_limit": "30 lbs per household per visit",
                "id_required": False,
            },
            "intake": {
                "phone": "202-644-9800",
                "hours": "Distribution hours only",
                "notes": "First come, first served. Bring bags to carry food.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 12),
                "verified_by": "official_directory",
            },
        },
    },
    # Maryland Food Bank
    {
        "org_name": "Maryland Food Bank",
        "title": "Veterans and Military Families Food Program - Baltimore",
        "description": (
            "Dedicated food assistance program for veterans, active duty military, "
            "and their families in the Baltimore metro area. Provides monthly food packages "
            "with culturally appropriate options and dietary accommodations."
        ),
        "summary": "Monthly food packages for veterans and military families in Baltimore",
        "categories": ["food"],
        "subcategories": ["food-pantry"],
        "scope": "state",
        "states": ["MD"],
        "tier": 2,
        "website": "https://mdfoodbank.org/veterans",
        "location": {
            "address": "2200 Halethorpe Farms Rd",
            "city": "Baltimore",
            "state": "MD",
            "zip_code": "21227",
            "service_area": ["Baltimore City", "Baltimore County", "Howard County"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["DD-214 or military ID", "Proof of residency"],
                "waitlist_status": "open",
            },
            "food": {
                "distribution_schedule": "Second and fourth Tuesday, 9:00 AM - 2:00 PM",
                "serves_dietary": ["halal", "kosher", "vegetarian", "vegan"],
                "quantity_limit": "One package per veteran household per distribution",
                "id_required": True,
            },
            "intake": {
                "phone": "410-737-8282",
                "url": "https://mdfoodbank.org/veterans-intake",
                "hours": "Mon-Fri 9:00 AM - 5:00 PM",
                "notes": "Pre-registration required for first visit. Bring military documentation.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 10),
                "verified_by": "provider_contact",
            },
        },
    },
    # VFW Post Food Pantry
    {
        "org_name": "VFW Post 1503",
        "title": "VFW Veterans Food Pantry - Silver Spring",
        "description": (
            "Weekly food pantry operated by VFW Post 1503 for veterans in Montgomery County. "
            "Provides emergency food assistance with no income verification required. "
            "Includes baby supplies and pet food when available."
        ),
        "summary": "Weekly veteran food pantry with no income requirements",
        "categories": ["food"],
        "subcategories": ["food-pantry"],
        "scope": "local",
        "states": ["MD"],
        "tier": 2,
        "website": "https://www.vfwpost1503.org/food-pantry",
        "location": {
            "address": "10 E Columbia Ave",
            "city": "Silver Spring",
            "state": "MD",
            "zip_code": "20901",
            "service_area": ["Montgomery County"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["Veteran ID or DD-214"],
                "waitlist_status": "open",
            },
            "food": {
                "distribution_schedule": "Every Thursday, 10:00 AM - 2:00 PM",
                "serves_dietary": ["vegetarian"],
                "quantity_limit": "One bag per week per household",
                "id_required": True,
            },
            "intake": {
                "phone": "301-589-1503",
                "hours": "Distribution hours only",
                "notes": "Walk-ins welcome during distribution hours.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 8),
                "verified_by": "provider_contact",
            },
        },
    },
    # American Legion Food Program
    {
        "org_name": "American Legion Post 139",
        "title": "Legion Emergency Food Assistance - Fairfax",
        "description": (
            "Emergency food assistance for veterans and their families in Fairfax County. "
            "Provides immediate food supplies during crisis situations with no advance "
            "appointment required."
        ),
        "summary": "Emergency veteran food assistance in Fairfax County",
        "categories": ["food"],
        "subcategories": ["food-pantry"],
        "scope": "local",
        "states": ["VA"],
        "tier": 2,
        "website": "https://www.legion139.org/services",
        "location": {
            "address": "3939 Oak St",
            "city": "Fairfax",
            "state": "VA",
            "zip_code": "22030",
            "service_area": ["Fairfax County", "Fairfax City"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["Any veteran documentation"],
                "waitlist_status": "open",
            },
            "food": {
                "distribution_schedule": "Mon, Wed, Fri 1:00 PM - 4:00 PM",
                "serves_dietary": [],
                "quantity_limit": "Emergency supplies as needed",
                "id_required": False,
            },
            "intake": {
                "phone": "703-591-0139",
                "hours": "Distribution hours",
                "notes": "No appointment needed for emergency assistance.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 6),
                "verified_by": "provider_contact",
            },
        },
    },
    # Church-based Pantry
    {
        "org_name": "Metropolitan Community Church of Washington DC",
        "title": "MCC DC Community Food Pantry",
        "description": (
            "LGBTQ+ affirming food pantry serving all community members including veterans. "
            "Weekly distribution with special accommodations for dietary restrictions. "
            "Safe and welcoming environment for all."
        ),
        "summary": "LGBTQ+ affirming community food pantry in DC",
        "categories": ["food"],
        "subcategories": ["food-pantry"],
        "scope": "local",
        "states": ["DC"],
        "tier": 3,
        "website": "https://www.mccdc.com/food-pantry",
        "location": {
            "address": "474 Ridge St NW",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20001",
            "service_area": ["Washington DC"],
            "eligibility": {
                "veteran_status_required": False,
                "docs_required": [],
                "waitlist_status": "open",
            },
            "food": {
                "distribution_schedule": "Every Saturday, 11:00 AM - 1:00 PM",
                "serves_dietary": ["vegetarian", "vegan", "gluten_free"],
                "quantity_limit": "One bag per person per week",
                "id_required": False,
            },
            "intake": {
                "phone": "202-638-7373",
                "hours": "Distribution hours",
                "notes": "All are welcome. Special dietary needs can be accommodated with notice.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 14),
                "verified_by": "provider_contact",
            },
        },
    },
    # Senior Meal Program
    {
        "org_name": "Arlington County Department of Human Services",
        "title": "Senior and Veterans Meal Program - Arlington",
        "description": (
            "Hot meal program for seniors aged 60+ and veterans of any age in Arlington County. "
            "Provides nutritious congregate meals at community centers with social activities."
        ),
        "summary": "Hot meals for seniors 60+ and all veterans in Arlington",
        "categories": ["food"],
        "subcategories": ["meal-program", "senior-food"],
        "scope": "local",
        "states": ["VA"],
        "tier": 3,
        "website": "https://www.arlingtonva.us/senior-services",
        "location": {
            "address": "2100 Washington Blvd",
            "city": "Arlington",
            "state": "VA",
            "zip_code": "22204",
            "service_area": ["Arlington County"],
            "eligibility": {
                "age_min": 60,
                "veteran_status_required": False,
                "docs_required": [],
                "waitlist_status": "open",
            },
            "food": {
                "distribution_schedule": "Monday through Friday, 11:30 AM - 12:30 PM",
                "serves_dietary": ["vegetarian", "halal", "gluten_free"],
                "quantity_limit": "One hot meal per day",
                "id_required": True,
            },
            "intake": {
                "phone": "703-228-1700",
                "url": "https://www.arlingtonva.us/meals",
                "hours": "Mon-Fri 8:00 AM - 5:00 PM",
                "notes": "Registration required. Veterans of any age qualify.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 11),
                "verified_by": "official_directory",
            },
        },
    },
    # Feeding America Partner
    {
        "org_name": "So Others Might Eat (SOME)",
        "title": "SOME Veterans Food Services - Washington DC",
        "description": (
            "Comprehensive food services for veterans experiencing homelessness or housing "
            "instability in Washington DC. Provides daily hot meals, food pantry access, "
            "and take-home groceries. Part of broader veteran support services."
        ),
        "summary": "Daily meals and pantry for veterans facing housing instability in DC",
        "categories": ["food"],
        "subcategories": ["meal-program", "food-pantry"],
        "scope": "local",
        "states": ["DC"],
        "tier": 2,
        "website": "https://www.some.org/services/food",
        "location": {
            "address": "71 O St NW",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20001",
            "service_area": ["Washington DC"],
            "eligibility": {
                "housing_status_required": ["homeless", "at_risk"],
                "veteran_status_required": False,
                "docs_required": [],
                "waitlist_status": "open",
            },
            "food": {
                "distribution_schedule": "Daily breakfast 7-8 AM, lunch 12-1 PM",
                "serves_dietary": ["vegetarian", "halal"],
                "quantity_limit": "No limit on daily meals",
                "id_required": False,
            },
            "intake": {
                "phone": "202-797-8806",
                "url": "https://www.some.org/get-help",
                "hours": "Daily 7:00 AM - 4:00 PM",
                "notes": "No documentation required. Walk-ins welcome for meals.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 13),
                "verified_by": "provider_contact",
            },
        },
    },
    # Prince George's County
    {
        "org_name": "Prince George's County Food Equity Council",
        "title": "Veterans Fresh Food Market - Largo",
        "description": (
            "Bi-weekly fresh food market specifically for veterans and their families "
            "in Prince George's County. Features locally sourced produce, dairy, and "
            "proteins with culturally diverse options."
        ),
        "summary": "Bi-weekly fresh food market for PG County veterans",
        "categories": ["food"],
        "subcategories": ["mobile-distribution"],
        "scope": "local",
        "states": ["MD"],
        "tier": 3,
        "website": "https://www.pgcfoodequity.org/veterans",
        "location": {
            "address": "9500 Arena Dr",
            "city": "Largo",
            "state": "MD",
            "zip_code": "20774",
            "service_area": ["Prince George's County"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["Military ID or VA card"],
                "waitlist_status": "open",
            },
            "food": {
                "distribution_schedule": "First and third Saturday, 9:00 AM - 12:00 PM",
                "serves_dietary": ["halal", "kosher", "vegetarian", "vegan", "gluten_free"],
                "quantity_limit": "Market basket for family size",
                "id_required": True,
            },
            "intake": {
                "phone": "301-883-6040",
                "hours": "Market hours only",
                "notes": "Pre-registration recommended but not required.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 9),
                "verified_by": "provider_contact",
            },
        },
    },
    # DAV Food Support
    {
        "org_name": "Disabled American Veterans Chapter 5",
        "title": "DAV Food Support Program - Woodbridge VA",
        "description": (
            "Food assistance program for disabled veterans and their dependents in the "
            "Woodbridge/Prince William County area. Monthly food packages with focus on "
            "nutrition for veterans with dietary restrictions due to health conditions."
        ),
        "summary": "Monthly food support for disabled veterans in Woodbridge",
        "categories": ["food"],
        "subcategories": ["food-pantry"],
        "scope": "local",
        "states": ["VA"],
        "tier": 2,
        "website": "https://www.dav.org/veterans/local-chapters",
        "location": {
            "address": "15150 Potomac Town Pl",
            "city": "Woodbridge",
            "state": "VA",
            "zip_code": "22191",
            "service_area": ["Prince William County", "Stafford County"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["VA disability rating letter or DD-214"],
                "waitlist_status": "open",
            },
            "food": {
                "distribution_schedule": "Third Saturday of each month, 10:00 AM - 2:00 PM",
                "serves_dietary": ["vegetarian", "gluten_free"],
                "quantity_limit": "One package per veteran household",
                "id_required": True,
            },
            "intake": {
                "phone": "703-878-5105",
                "hours": "Distribution day, or call Mon-Fri 9-5",
                "notes": "Priority given to service-connected disabled veterans.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 7),
                "verified_by": "provider_contact",
            },
        },
    },
]


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
    statement = select(Resource).where(Resource.title == title, Resource.organization_id == org_id)
    return session.exec(statement).first() is not None


def seed_dmv_food(database_url: str) -> None:
    """Seed DMV food distribution resources into the database."""
    engine = create_engine(database_url, echo=False)

    created = 0
    skipped = 0

    with Session(engine) as session:
        # Create source for DMV food data
        source = get_or_create_source(
            session,
            name="DMV Food Distribution Provider Data",
            url="https://vibe4vets.org/dmv-food",
        )

        for res_data in DMV_FOOD_RESOURCES:
            # Get or create organization
            org = get_or_create_organization(session, res_data["org_name"], res_data.get("website"))

            # Check if resource already exists
            if resource_exists(session, res_data["title"], org.id):
                print(f"  Skipping existing: {res_data['title']}")
                skipped += 1
                continue

            # Create location with eligibility and food data
            loc_data = res_data.get("location", {})
            eligibility_data = loc_data.get("eligibility", {})
            food_data = loc_data.get("food", {})
            intake_data = loc_data.get("intake", {})
            verification_data = loc_data.get("verification", {})

            location = Location(
                id=uuid4(),
                organization_id=org.id,
                address=loc_data.get("address", ""),
                city=loc_data.get("city", ""),
                state=loc_data.get("state", ""),
                zip_code=loc_data.get("zip_code", ""),
                service_area=loc_data.get("service_area", []),
                # Eligibility fields
                age_min=eligibility_data.get("age_min"),
                age_max=eligibility_data.get("age_max"),
                household_size_min=eligibility_data.get("household_size_min"),
                household_size_max=eligibility_data.get("household_size_max"),
                income_limit_type=eligibility_data.get("income_limit_type"),
                income_limit_ami_percent=eligibility_data.get("income_limit_ami_percent"),
                housing_status_required=eligibility_data.get("housing_status_required", []),
                veteran_status_required=eligibility_data.get("veteran_status_required", False),
                docs_required=eligibility_data.get("docs_required", []),
                waitlist_status=eligibility_data.get("waitlist_status"),
                # Food-specific fields
                distribution_schedule=food_data.get("distribution_schedule"),
                serves_dietary=food_data.get("serves_dietary", []),
                quantity_limit=food_data.get("quantity_limit"),
                id_required=food_data.get("id_required"),
                # Intake fields
                intake_phone=intake_data.get("phone"),
                intake_url=intake_data.get("url"),
                intake_hours=intake_data.get("hours"),
                intake_notes=intake_data.get("notes"),
                # Verification fields
                last_verified_at=verification_data.get("last_verified_at"),
                verified_by=verification_data.get("verified_by"),
            )
            session.add(location)
            session.flush()

            # Calculate reliability score
            tier = res_data.get("tier", 2)
            reliability = TIER_SCORES.get(tier, 0.5)

            # Map scope
            scope_str = res_data.get("scope", "local")
            scope_map = {
                "national": ResourceScope.NATIONAL,
                "state": ResourceScope.STATE,
                "local": ResourceScope.LOCAL,
            }
            scope = scope_map.get(scope_str, ResourceScope.LOCAL)

            # Create resource
            resource = Resource(
                organization_id=org.id,
                location_id=location.id,
                source_id=source.id,
                title=res_data["title"],
                description=res_data["description"],
                summary=res_data.get("summary"),
                categories=res_data.get("categories", ["food"]),
                subcategories=res_data.get("subcategories", []),
                scope=scope,
                states=res_data.get("states", []),
                website=res_data.get("website"),
                source_url=res_data.get("website"),
                status=ResourceStatus.ACTIVE,
                freshness_score=1.0,
                reliability_score=reliability,
                last_verified=verification_data.get("last_verified_at"),
            )
            session.add(resource)
            created += 1
            print(f"  Created: {res_data['title']}")

        session.commit()

    print("\n" + "=" * 50)
    print("DMV Food Distribution seeding complete!")
    print(f"  Created: {created} resources")
    print(f"  Skipped: {skipped} existing resources")
    print("=" * 50)


if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets")
    seed_dmv_food(database_url)
