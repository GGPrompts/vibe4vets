#!/usr/bin/env python3
"""Seed script for DC/MD/VA benefits consultation resources.

This script seeds benefits consultation resources for the DMV (DC/MD/VA) area
with structured eligibility and benefits-specific fields for the eligibility wizard.
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

# DMV Benefits Consultation Resources data
DMV_BENEFITS_RESOURCES = [
    # VSO Services
    {
        "org_name": "Disabled American Veterans (DAV)",
        "title": "DAV National Service Office - Washington DC",
        "description": "Free claims assistance from accredited DAV National Service Officers. "
        "Provides help with disability compensation, pension, survivor benefits, and appeals. "
        "Located at the VA Regional Office.",
        "summary": "Free VA claims assistance from accredited DAV service officers",
        "categories": ["benefits"],
        "subcategories": ["vso-services", "disability-claims"],
        "scope": "local",
        "states": ["DC", "MD", "VA"],
        "tier": 2,
        "website": "https://www.dav.org/veterans/find-your-local-office/",
        "location": {
            "address": "1722 I St NW, Room 150",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20421",
            "service_area": ["Washington DC", "Northern Virginia", "Southern Maryland"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["DD-214 or service records", "Medical records", "Photo ID"],
            },
            "benefits": {
                "benefits_types_supported": ["disability", "pension", "survivor", "healthcare"],
                "representative_type": "vso",
                "accredited": True,
                "walk_in_available": True,
                "appointment_required": False,
                "virtual_available": True,
                "free_service": True,
                "languages_supported": ["English", "Spanish"],
            },
            "intake": {
                "phone": "202-530-9260",
                "url": "https://www.dav.org/veterans/find-your-local-office/",
                "hours": "Mon-Fri 8:00 AM - 4:30 PM",
                "notes": "Walk-ins welcome. Appointments recommended for complex claims.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 15),
                "verified_by": "official_directory",
            },
        },
    },
    {
        "org_name": "Veterans of Foreign Wars (VFW)",
        "title": "VFW Department Service Office - Maryland",
        "description": "VFW accredited service officers provide free assistance with VA claims, "
        "appeals, and benefits counseling. Specializes in combat veteran issues and "
        "disability compensation claims.",
        "summary": "Free VFW claims assistance for Maryland veterans",
        "categories": ["benefits"],
        "subcategories": ["vso-services", "disability-claims"],
        "scope": "state",
        "states": ["MD"],
        "tier": 2,
        "website": "https://www.vfw.org/assistance/va-claims-assistance",
        "location": {
            "address": "31 Hopkins Plaza, Room 941",
            "city": "Baltimore",
            "state": "MD",
            "zip_code": "21201",
            "service_area": ["Maryland (Statewide)"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["DD-214", "VA file number if known"],
            },
            "benefits": {
                "benefits_types_supported": ["disability", "pension", "education", "survivor"],
                "representative_type": "vso",
                "accredited": True,
                "walk_in_available": True,
                "appointment_required": False,
                "virtual_available": True,
                "free_service": True,
                "languages_supported": ["English"],
            },
            "intake": {
                "phone": "410-230-4440",
                "hours": "Mon-Fri 8:00 AM - 4:00 PM",
                "notes": "Call ahead for complex claims. Walk-ins accepted for simple questions.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 12),
                "verified_by": "provider_contact",
            },
        },
    },
    {
        "org_name": "American Legion",
        "title": "American Legion Department Service Office - Virginia",
        "description": "American Legion accredited representatives provide free VA claims filing, "
        "appeals assistance, and benefits counseling. No Legion membership required for service.",
        "summary": "Free American Legion claims assistance for Virginia veterans",
        "categories": ["benefits"],
        "subcategories": ["vso-services", "disability-claims"],
        "scope": "state",
        "states": ["VA"],
        "tier": 2,
        "website": "https://www.legion.org/veteransbenefits",
        "location": {
            "address": "210 Franklin Rd SW, Room 543",
            "city": "Roanoke",
            "state": "VA",
            "zip_code": "24011",
            "service_area": ["Virginia (Statewide)"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["DD-214", "Medical evidence"],
            },
            "benefits": {
                "benefits_types_supported": [
                    "disability",
                    "pension",
                    "education",
                    "healthcare",
                    "survivor",
                ],
                "representative_type": "vso",
                "accredited": True,
                "walk_in_available": False,
                "appointment_required": True,
                "virtual_available": True,
                "free_service": True,
                "languages_supported": ["English"],
            },
            "intake": {
                "phone": "540-857-2391",
                "hours": "Mon-Fri 8:00 AM - 4:30 PM",
                "notes": "Appointment required. Virtual appointments available statewide.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 10),
                "verified_by": "provider_contact",
            },
        },
    },
    # County Veteran Service Officers
    {
        "org_name": "Fairfax County Government",
        "title": "Fairfax County Veteran Services",
        "description": "County Veteran Service Officers provide free benefits counseling, "
        "claims assistance, and referrals to local resources. Serve all veterans in "
        "Fairfax County regardless of discharge status.",
        "summary": "Free county veteran services for Fairfax County veterans",
        "categories": ["benefits"],
        "subcategories": ["cvso", "disability-claims", "healthcare-enrollment"],
        "scope": "local",
        "states": ["VA"],
        "tier": 3,
        "website": "https://www.fairfaxcounty.gov/familyservices/older-adults/veteran-services",
        "location": {
            "address": "12011 Government Center Pkwy, Suite 1030",
            "city": "Fairfax",
            "state": "VA",
            "zip_code": "22035",
            "service_area": ["Fairfax County"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["DD-214 or equivalent"],
            },
            "benefits": {
                "benefits_types_supported": [
                    "disability",
                    "pension",
                    "education",
                    "healthcare",
                    "burial",
                    "survivor",
                ],
                "representative_type": "cvso",
                "accredited": True,
                "walk_in_available": False,
                "appointment_required": True,
                "virtual_available": True,
                "free_service": True,
                "languages_supported": ["English", "Spanish", "Korean", "Vietnamese"],
            },
            "intake": {
                "phone": "703-324-5489",
                "url": "https://www.fairfaxcounty.gov/familyservices/older-adults/veteran-services",
                "hours": "Mon-Fri 8:00 AM - 4:30 PM",
                "notes": "Appointments required. Virtual consultations available.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 14),
                "verified_by": "official_directory",
            },
        },
    },
    {
        "org_name": "Montgomery County Government",
        "title": "Montgomery County Veterans Services",
        "description": "Montgomery County provides free veteran service officers for benefits "
        "counseling, claims filing, and connection to county and state resources. "
        "Multilingual services available.",
        "summary": "Free county veteran services for Montgomery County MD veterans",
        "categories": ["benefits"],
        "subcategories": ["cvso", "disability-claims"],
        "scope": "local",
        "states": ["MD"],
        "tier": 3,
        "website": "https://www.montgomerycountymd.gov/HHS-Program/ADS/VeteransAffairs/",
        "location": {
            "address": "1301 Piccard Dr, Suite 1300",
            "city": "Rockville",
            "state": "MD",
            "zip_code": "20850",
            "service_area": ["Montgomery County"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["DD-214"],
            },
            "benefits": {
                "benefits_types_supported": ["disability", "pension", "healthcare", "education"],
                "representative_type": "cvso",
                "accredited": True,
                "walk_in_available": True,
                "appointment_required": False,
                "virtual_available": True,
                "free_service": True,
                "languages_supported": ["English", "Spanish", "French", "Amharic"],
            },
            "intake": {
                "phone": "240-773-8352",
                "url": "https://www.montgomerycountymd.gov/HHS-Program/ADS/VeteransAffairs/",
                "hours": "Mon-Fri 8:30 AM - 5:00 PM",
                "notes": "Walk-ins welcome. Call for complex claims appointments.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 11),
                "verified_by": "provider_contact",
            },
        },
    },
    {
        "org_name": "Prince George's County Government",
        "title": "Prince George's County Veterans Affairs",
        "description": "County veteran service officers help with VA claims, healthcare enrollment, "
        "and connecting veterans to local programs. Offers outreach at community locations.",
        "summary": "Free veteran services for Prince George's County MD veterans",
        "categories": ["benefits"],
        "subcategories": ["cvso", "healthcare-enrollment"],
        "scope": "local",
        "states": ["MD"],
        "tier": 3,
        "website": "https://www.princegeorgescountymd.gov/departments-offices/family-services/veterans-affairs",
        "location": {
            "address": "9200 Basil Court, Suite 504",
            "city": "Largo",
            "state": "MD",
            "zip_code": "20774",
            "service_area": ["Prince George's County"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["DD-214", "Photo ID"],
            },
            "benefits": {
                "benefits_types_supported": ["disability", "healthcare", "education", "burial"],
                "representative_type": "cvso",
                "accredited": True,
                "walk_in_available": True,
                "appointment_required": False,
                "virtual_available": False,
                "free_service": True,
                "languages_supported": ["English", "Spanish"],
            },
            "intake": {
                "phone": "301-883-6565",
                "hours": "Mon-Fri 8:30 AM - 4:30 PM",
                "notes": "Walk-ins accepted. Community outreach at Largo Library on Thursdays.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 8),
                "verified_by": "provider_contact",
            },
        },
    },
    # VA Benefits Hotline / National Resources
    {
        "org_name": "U.S. Department of Veterans Affairs",
        "title": "VA Benefits Hotline",
        "description": "National VA benefits hotline for general information, claim status, "
        "and appointment scheduling. Available for all veterans nationwide.",
        "summary": "National VA benefits information hotline",
        "categories": ["benefits"],
        "subcategories": ["disability-claims", "healthcare-enrollment", "education-benefits"],
        "scope": "national",
        "states": [],
        "tier": 1,
        "website": "https://www.va.gov/contact-us/",
        "location": {
            "address": "810 Vermont Ave NW",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20420",
            "service_area": [],
            "eligibility": {
                "veteran_status_required": True,
            },
            "benefits": {
                "benefits_types_supported": [
                    "disability",
                    "pension",
                    "education",
                    "healthcare",
                    "burial",
                    "survivor",
                    "vre",
                ],
                "accredited": True,
                "walk_in_available": False,
                "appointment_required": False,
                "virtual_available": True,
                "free_service": True,
                "languages_supported": ["English", "Spanish"],
            },
            "intake": {
                "phone": "800-827-1000",
                "url": "https://www.va.gov/contact-us/",
                "hours": "Mon-Fri 8:00 AM - 9:00 PM ET",
                "notes": "Automated system available 24/7. Live agents during business hours.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 16),
                "verified_by": "official_directory",
            },
        },
    },
    # DC Office of Veterans Affairs
    {
        "org_name": "DC Office of Veterans Affairs",
        "title": "DC Office of Veterans Affairs",
        "description": "DC government office providing benefits counseling, claims assistance, "
        "and connection to District-specific veteran programs. Located near the VA Medical Center.",
        "summary": "DC government veteran services and benefits assistance",
        "categories": ["benefits"],
        "subcategories": ["cvso", "disability-claims", "healthcare-enrollment"],
        "scope": "local",
        "states": ["DC"],
        "tier": 3,
        "website": "https://ova.dc.gov/",
        "location": {
            "address": "441 4th St NW, Suite 870N",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20001",
            "service_area": ["Washington DC"],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["DD-214", "DC residency proof"],
            },
            "benefits": {
                "benefits_types_supported": ["disability", "healthcare", "education", "pension"],
                "representative_type": "cvso",
                "accredited": True,
                "walk_in_available": True,
                "appointment_required": False,
                "virtual_available": True,
                "free_service": True,
                "languages_supported": ["English", "Spanish", "Amharic"],
            },
            "intake": {
                "phone": "202-724-5454",
                "url": "https://ova.dc.gov/service/benefits-assistance",
                "hours": "Mon-Fri 8:30 AM - 5:00 PM",
                "notes": "Walk-ins welcome. Virtual appointments available upon request.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 13),
                "verified_by": "official_directory",
            },
        },
    },
    # Virginia Department of Veterans Services
    {
        "org_name": "Virginia Department of Veterans Services",
        "title": "Virginia Benefits Services - Northern Region",
        "description": "State-employed veteran service representatives provide free assistance with "
        "VA disability claims, appeals, and state veteran benefits. Serves Northern Virginia.",
        "summary": "Virginia state veteran benefits services for Northern VA",
        "categories": ["benefits"],
        "subcategories": ["disability-claims", "education-benefits"],
        "scope": "state",
        "states": ["VA"],
        "tier": 3,
        "website": "https://www.dvs.virginia.gov/benefits",
        "location": {
            "address": "5001 Eisenhower Ave, Suite 120",
            "city": "Alexandria",
            "state": "VA",
            "zip_code": "22304",
            "service_area": [
                "Fairfax County",
                "Arlington County",
                "Loudoun County",
                "Prince William County",
                "Alexandria City",
            ],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["DD-214", "VA file number if known"],
            },
            "benefits": {
                "benefits_types_supported": ["disability", "education", "healthcare", "vre"],
                "representative_type": "cvso",
                "accredited": True,
                "walk_in_available": False,
                "appointment_required": True,
                "virtual_available": True,
                "free_service": True,
                "languages_supported": ["English", "Spanish"],
            },
            "intake": {
                "phone": "703-305-3042",
                "url": "https://www.dvs.virginia.gov/benefits/claims-services",
                "hours": "Mon-Fri 8:00 AM - 5:00 PM",
                "notes": "Appointments required. Book online or by phone.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 9),
                "verified_by": "official_directory",
            },
        },
    },
    # Legal aid for VA appeals
    {
        "org_name": "National Veterans Legal Services Program",
        "title": "NVLSP - VA Appeals Assistance",
        "description": "Free legal representation for veterans appealing VA benefit denials. "
        "Specializes in complex disability claims, character of discharge upgrades, "
        "and Board of Veterans Appeals cases.",
        "summary": "Free legal help for VA benefits appeals",
        "categories": ["benefits", "legal"],
        "subcategories": ["disability-claims", "va-appeals"],
        "scope": "national",
        "states": [],
        "tier": 2,
        "website": "https://www.nvlsp.org/",
        "location": {
            "address": "1600 K St NW, Suite 500",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20006",
            "service_area": [],
            "eligibility": {
                "veteran_status_required": True,
                "docs_required": ["VA denial letter", "DD-214", "Medical records"],
            },
            "benefits": {
                "benefits_types_supported": ["disability", "pension"],
                "representative_type": "attorney",
                "accredited": True,
                "walk_in_available": False,
                "appointment_required": True,
                "virtual_available": True,
                "free_service": True,
                "languages_supported": ["English"],
            },
            "intake": {
                "phone": "202-265-8305",
                "url": "https://www.nvlsp.org/what-we-do/individual-veterans",
                "hours": "Mon-Fri 9:00 AM - 5:00 PM",
                "notes": "Must have existing VA denial. Apply online for case review.",
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


def seed_dmv_benefits(database_url: str) -> None:
    """Seed DMV benefits consultation resources into the database."""
    engine = create_engine(database_url, echo=False)

    created = 0
    skipped = 0

    with Session(engine) as session:
        # Create source for DMV benefits data
        source = get_or_create_source(
            session,
            name="DMV Benefits Consultation Data",
            url="https://vibe4vets.org/dmv-benefits",
        )

        for res_data in DMV_BENEFITS_RESOURCES:
            # Get or create organization
            org = get_or_create_organization(session, res_data["org_name"], res_data.get("website"))

            # Check if resource already exists
            if resource_exists(session, res_data["title"], org.id):
                print(f"  Skipping existing: {res_data['title']}")
                skipped += 1
                continue

            # Create location with eligibility and benefits data
            loc_data = res_data.get("location", {})
            eligibility_data = loc_data.get("eligibility", {})
            benefits_data = loc_data.get("benefits", {})
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
                veteran_status_required=eligibility_data.get("veteran_status_required", True),
                docs_required=eligibility_data.get("docs_required", []),
                # Benefits-specific fields
                benefits_types_supported=benefits_data.get("benefits_types_supported", []),
                representative_type=benefits_data.get("representative_type"),
                accredited=benefits_data.get("accredited"),
                walk_in_available=benefits_data.get("walk_in_available"),
                appointment_required=benefits_data.get("appointment_required"),
                virtual_available=benefits_data.get("virtual_available"),
                free_service=benefits_data.get("free_service"),
                languages_supported=benefits_data.get("languages_supported", []),
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
                categories=res_data.get("categories", ["benefits"]),
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
    print("DMV Benefits seeding complete!")
    print(f"  Created: {created} resources")
    print(f"  Skipped: {skipped} existing resources")
    print("=" * 50)


if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets")
    seed_dmv_benefits(database_url)
