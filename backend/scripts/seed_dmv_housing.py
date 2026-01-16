#!/usr/bin/env python3
"""Seed script for DC/MD/VA housing resources with eligibility data.

This script seeds housing resources for the DMV (DC/MD/VA) area with
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

# DMV Housing Resources data
DMV_HOUSING_RESOURCES = [
    # SSVF Providers
    {
        "org_name": "Volunteers of America Chesapeake",
        "title": "SSVF - Northern Virginia",
        "description": "Supportive Services for Veteran Families (SSVF) program providing housing "
        "assistance, case management, and supportive services to very low-income veteran families "
        "who are homeless or at risk of homelessness in Northern Virginia.",
        "summary": "SSVF rapid re-housing and homelessness prevention for veteran families",
        "categories": ["housing"],
        "subcategories": ["ssvf", "rapid_rehousing"],
        "scope": "state",
        "states": ["VA"],
        "tier": 2,
        "website": "https://www.voaches.org/ssvf",
        "location": {
            "address": "8614 Westwood Center Dr, Suite 100",
            "city": "Vienna",
            "state": "VA",
            "zip_code": "22182",
            "service_area": [
                "Fairfax County",
                "Arlington County",
                "Alexandria City",
                "Loudoun County",
            ],
            "eligibility": {
                "income_limit_type": "ami_percent",
                "income_limit_ami_percent": 50,
                "housing_status_required": ["homeless", "at_risk"],
                "veteran_status_required": True,
                "docs_required": [
                    "DD-214",
                    "Income verification",
                    "Photo ID",
                    "Proof of homelessness or at-risk status",
                ],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "703-288-2218",
                "url": "https://www.voaches.org/ssvf-intake",
                "hours": "Mon-Fri 9:00 AM - 5:00 PM",
                "notes": "Call for initial screening. Walk-ins accepted Tuesdays 10AM-2PM.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 10),
                "verified_by": "provider_contact",
            },
        },
    },
    {
        "org_name": "Pathways to Housing DC",
        "title": "SSVF - Washington DC",
        "description": (
            "Housing First program providing immediate access to permanent housing for "
            "chronically homeless veterans in Washington DC, combined with intensive "
            "supportive services to maintain housing stability."
        ),
        "summary": "Housing First SSVF program for chronically homeless veterans in DC",
        "categories": ["housing"],
        "subcategories": ["ssvf", "housing_first"],
        "scope": "local",
        "states": ["DC"],
        "tier": 2,
        "website": "https://www.pathwaystohousingdc.org",
        "location": {
            "address": "2136 Pennsylvania Ave NW",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20037",
            "service_area": ["Washington DC"],
            "eligibility": {
                "income_limit_type": "ami_percent",
                "income_limit_ami_percent": 30,
                "housing_status_required": ["homeless"],
                "veteran_status_required": True,
                "docs_required": ["DD-214 or VA letter", "Photo ID", "Social Security card"],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "202-529-2972",
                "url": "https://www.pathwaystohousingdc.org/veterans",
                "hours": "Mon-Fri 8:30 AM - 5:00 PM",
                "notes": "Referrals accepted from VA, Community Partnership, and self-referrals.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 8),
                "verified_by": "official_directory",
            },
        },
    },
    {
        "org_name": "Maryland Center for Veterans Education and Training",
        "title": "SSVF - Baltimore Metro",
        "description": "Comprehensive veteran housing program providing transitional housing, "
        "rapid re-housing assistance, and employment services for homeless veterans in the "
        "Baltimore metropolitan area.",
        "summary": "SSVF and transitional housing for Baltimore area veterans",
        "categories": ["housing"],
        "subcategories": ["ssvf", "transitional_housing"],
        "scope": "state",
        "states": ["MD"],
        "tier": 2,
        "website": "https://www.mcvet.org",
        "location": {
            "address": "301 N High St",
            "city": "Baltimore",
            "state": "MD",
            "zip_code": "21202",
            "service_area": ["Baltimore City", "Baltimore County", "Anne Arundel County"],
            "eligibility": {
                "income_limit_type": "ami_percent",
                "income_limit_ami_percent": 50,
                "housing_status_required": ["homeless", "at_risk"],
                "veteran_status_required": True,
                "docs_required": ["DD-214", "Photo ID", "Birth certificate or passport"],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "410-576-9626",
                "url": "https://www.mcvet.org/apply",
                "hours": "Mon-Fri 8:00 AM - 4:30 PM",
                "notes": "24-hour intake available for emergency situations.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 12),
                "verified_by": "provider_contact",
            },
        },
    },
    # HUD-VASH
    {
        "org_name": "DC Housing Authority",
        "title": "HUD-VASH - Washington DC",
        "description": "HUD-Veterans Affairs Supportive Housing program combining Housing Choice "
        "Vouchers with VA case management and supportive services for homeless veterans in DC.",
        "summary": "HUD-VASH permanent supportive housing vouchers for homeless veterans",
        "categories": ["housing"],
        "subcategories": ["hud_vash", "voucher"],
        "scope": "local",
        "states": ["DC"],
        "tier": 1,
        "website": "https://www.dchousing.org/hudvash",
        "location": {
            "address": "1133 North Capitol St NE",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20002",
            "service_area": ["Washington DC"],
            "eligibility": {
                "income_limit_type": "ami_percent",
                "income_limit_ami_percent": 50,
                "housing_status_required": ["homeless"],
                "veteran_status_required": True,
                "docs_required": [
                    "DD-214",
                    "VA eligibility letter",
                    "Photo ID",
                    "Social Security card",
                ],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "202-535-1000",
                "url": "https://www.dchousing.org/apply",
                "hours": "Mon-Fri 8:30 AM - 4:30 PM",
                "notes": (
                    "Must be referred by DC VA Medical Center. Contact VA social worker first."
                ),
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 14),
                "verified_by": "official_directory",
            },
        },
    },
    {
        "org_name": "Fairfax County Housing Authority",
        "title": "HUD-VASH - Fairfax County",
        "description": "HUD-VASH housing voucher program for homeless veterans in Fairfax County, "
        "providing rental assistance and connection to VA healthcare and supportive services.",
        "summary": "HUD-VASH vouchers for Fairfax County homeless veterans",
        "categories": ["housing"],
        "subcategories": ["hud_vash", "voucher"],
        "scope": "local",
        "states": ["VA"],
        "tier": 1,
        "website": "https://www.fairfaxcounty.gov/housing",
        "location": {
            "address": "3700 Pender Dr, Suite 300",
            "city": "Fairfax",
            "state": "VA",
            "zip_code": "22030",
            "service_area": ["Fairfax County"],
            "eligibility": {
                "income_limit_type": "ami_percent",
                "income_limit_ami_percent": 50,
                "housing_status_required": ["homeless"],
                "veteran_status_required": True,
                "docs_required": ["DD-214", "VA eligibility verification", "Photo ID"],
                "waitlist_status": "closed",
            },
            "intake": {
                "phone": "703-246-5100",
                "hours": "Mon-Fri 8:00 AM - 4:30 PM",
                "notes": "Referral required from DC VA Medical Center HUD-VASH team.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 5),
                "verified_by": "official_directory",
            },
        },
    },
    # Senior Housing
    {
        "org_name": "Armed Forces Retirement Home",
        "title": "Armed Forces Retirement Home - Washington DC",
        "description": (
            "Residential retirement community for eligible military veterans, providing "
            "independent living, assisted living, and long-term care on a historic campus "
            "in Washington DC."
        ),
        "summary": "Retirement living for veterans 60+ with military service",
        "categories": ["housing"],
        "subcategories": ["senior_housing", "retirement"],
        "scope": "national",
        "states": [],
        "tier": 1,
        "website": "https://www.afrh.gov",
        "location": {
            "address": "3700 North Capitol St NW",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20011",
            "service_area": [],
            "eligibility": {
                "age_min": 60,
                "veteran_status_required": True,
                "docs_required": ["DD-214", "Medical records", "Financial statement"],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "800-422-9988",
                "url": "https://www.afrh.gov/apply",
                "hours": "Mon-Fri 8:00 AM - 4:30 PM",
                "notes": "Tours available by appointment. Application process takes 4-6 weeks.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 13),
                "verified_by": "official_directory",
            },
        },
    },
    {
        "org_name": "Knollwood Military Retirement Community",
        "title": "Knollwood Military Community - Virginia",
        "description": "Independent and assisted living community for military officers and their "
        "spouses in Northern Virginia, offering a range of housing options and amenities.",
        "summary": "Retirement community for military officers 62+ in Northern VA",
        "categories": ["housing"],
        "subcategories": ["senior_housing", "retirement"],
        "scope": "state",
        "states": ["VA"],
        "tier": 3,
        "website": "https://www.armydistaff.org",
        "location": {
            "address": "6200 Oregon Ave NW",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20015",
            "service_area": ["Northern Virginia", "Washington DC", "Maryland"],
            "eligibility": {
                "age_min": 62,
                "veteran_status_required": True,
                "docs_required": [
                    "DD-214",
                    "Officer service verification",
                    "Financial documentation",
                ],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "202-541-0400",
                "url": "https://www.armydistaff.org/admissions",
                "hours": "Mon-Fri 9:00 AM - 5:00 PM",
                "notes": "Schedule a visit to tour the community and meet with admissions.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 7),
                "verified_by": "provider_contact",
            },
        },
    },
    # Emergency Shelter
    {
        "org_name": "US VETS",
        "title": "US VETS - Washington DC",
        "description": "Comprehensive homeless services including emergency shelter, transitional "
        "housing, and permanent supportive housing for veterans in the DC metro area.",
        "summary": "Emergency shelter and housing continuum for DC area veterans",
        "categories": ["housing"],
        "subcategories": ["emergency_shelter", "transitional_housing"],
        "scope": "local",
        "states": ["DC"],
        "tier": 2,
        "website": "https://www.usvetsinc.org/dc",
        "location": {
            "address": "1016 11th St NW",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20001",
            "service_area": ["Washington DC", "Northern Virginia", "Southern Maryland"],
            "eligibility": {
                "housing_status_required": ["homeless"],
                "veteran_status_required": True,
                "docs_required": ["Photo ID", "DD-214 or VA letter"],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "202-842-9433",
                "hours": "24/7 for emergency intake",
                "notes": "Walk-ins accepted. Emergency beds available nightly.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 11),
                "verified_by": "provider_contact",
            },
        },
    },
    # Rental Assistance
    {
        "org_name": "Virginia Housing",
        "title": "Virginia Rent Relief Program - Veterans Priority",
        "description": "Emergency rental assistance program with priority processing for veteran "
        "households facing housing instability due to financial hardship.",
        "summary": "Emergency rent assistance with veteran priority in Virginia",
        "categories": ["housing"],
        "subcategories": ["rental_assistance", "emergency_assistance"],
        "scope": "state",
        "states": ["VA"],
        "tier": 1,
        "website": "https://www.virginiahousing.com/renters/rent-relief",
        "location": {
            "address": "601 S Belvidere St",
            "city": "Richmond",
            "state": "VA",
            "zip_code": "23220",
            "service_area": ["Virginia (Statewide)"],
            "eligibility": {
                "income_limit_type": "ami_percent",
                "income_limit_ami_percent": 80,
                "housing_status_required": ["at_risk", "stably_housed"],
                "veteran_status_required": False,
                "docs_required": [
                    "Lease agreement",
                    "Landlord information",
                    "Income verification",
                    "ID",
                ],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "833-687-0977",
                "url": "https://www.virginiahousing.com/renters/rent-relief/apply",
                "hours": "Mon-Fri 8:00 AM - 6:00 PM",
                "notes": "Veterans receive priority processing. Apply online for fastest service.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 9),
                "verified_by": "official_directory",
            },
        },
    },
    {
        "org_name": "Montgomery County DHHS",
        "title": "Emergency Assistance Program - Montgomery County",
        "description": (
            "Emergency financial assistance for rent and utilities for Montgomery County "
            "residents facing eviction or utility shutoff, with dedicated veteran liaison."
        ),
        "summary": "Emergency rent/utility assistance in Montgomery County MD",
        "categories": ["housing"],
        "subcategories": ["rental_assistance", "utility_assistance"],
        "scope": "local",
        "states": ["MD"],
        "tier": 3,
        "website": "https://www.montgomerycountymd.gov/HHS/",
        "location": {
            "address": "1301 Piccard Dr",
            "city": "Rockville",
            "state": "MD",
            "zip_code": "20850",
            "service_area": ["Montgomery County"],
            "eligibility": {
                "income_limit_type": "ami_percent",
                "income_limit_ami_percent": 60,
                "housing_status_required": ["at_risk"],
                "veteran_status_required": False,
                "docs_required": [
                    "Eviction notice or utility shutoff notice",
                    "Lease",
                    "Income documentation",
                ],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "240-773-3556",
                "hours": "Mon-Fri 8:30 AM - 5:00 PM",
                "notes": "Ask for Veteran Services liaison for expedited processing.",
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 6),
                "verified_by": "provider_contact",
            },
        },
    },
    # GPD - Grant and Per Diem
    {
        "org_name": "Operation Renewed Hope Foundation",
        "title": "GPD Transitional Housing - Prince George's County",
        "description": "VA Grant and Per Diem funded transitional housing for homeless veterans "
        "in Prince George's County, providing up to 24 months of supportive housing.",
        "summary": "VA GPD transitional housing in Prince George's County MD",
        "categories": ["housing"],
        "subcategories": ["gpd", "transitional_housing"],
        "scope": "local",
        "states": ["MD"],
        "tier": 2,
        "website": "https://www.operationrenewedhope.org",
        "location": {
            "address": "4700 Auth Pl",
            "city": "Marlow Heights",
            "state": "MD",
            "zip_code": "20746",
            "service_area": ["Prince George's County", "Washington DC"],
            "eligibility": {
                "housing_status_required": ["homeless"],
                "veteran_status_required": True,
                "docs_required": ["DD-214", "VA healthcare eligibility", "Photo ID"],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "301-423-4700",
                "hours": "Mon-Fri 9:00 AM - 5:00 PM",
                "notes": (
                    "VA referral preferred but not required. Substance abuse recovery supported."
                ),
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 4),
                "verified_by": "provider_contact",
            },
        },
    },
    # Women Veterans
    {
        "org_name": "Final Salute Inc.",
        "title": "Women Veterans Housing - National Capital Region",
        "description": "Transitional housing program specifically for homeless women veterans and "
        "their children in the DC metro area, providing safe housing and wraparound services.",
        "summary": "Housing for homeless women veterans and children in DMV",
        "categories": ["housing"],
        "subcategories": ["women_veterans", "transitional_housing"],
        "scope": "local",
        "states": ["DC", "MD", "VA"],
        "tier": 2,
        "website": "https://www.finalsaluteinc.org",
        "location": {
            "address": "P.O. Box 10447",
            "city": "Alexandria",
            "state": "VA",
            "zip_code": "22310",
            "service_area": ["Washington DC", "Northern Virginia", "Southern Maryland"],
            "eligibility": {
                "housing_status_required": ["homeless", "at_risk"],
                "veteran_status_required": True,
                "docs_required": [
                    "DD-214",
                    "Photo ID",
                    "Children's birth certificates if applicable",
                ],
                "waitlist_status": "open",
            },
            "intake": {
                "phone": "866-472-5883",
                "url": "https://www.finalsaluteinc.org/apply",
                "hours": "Mon-Fri 9:00 AM - 5:00 PM",
                "notes": (
                    "For women veterans and their children only. Pet-friendly options available."
                ),
            },
            "verification": {
                "last_verified_at": datetime(2026, 1, 3),
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


def seed_dmv_housing(database_url: str) -> None:
    """Seed DMV housing resources into the database."""
    engine = create_engine(database_url, echo=False)

    created = 0
    skipped = 0

    with Session(engine) as session:
        # Create source for DMV housing data
        source = get_or_create_source(
            session,
            name="DMV Housing Provider Data",
            url="https://vibe4vets.org/dmv-housing",
        )

        for res_data in DMV_HOUSING_RESOURCES:
            # Get or create organization
            org = get_or_create_organization(session, res_data["org_name"], res_data.get("website"))

            # Check if resource already exists
            if resource_exists(session, res_data["title"], org.id):
                print(f"  Skipping existing: {res_data['title']}")
                skipped += 1
                continue

            # Create location with eligibility data
            loc_data = res_data.get("location", {})
            eligibility_data = loc_data.get("eligibility", {})
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
                veteran_status_required=eligibility_data.get("veteran_status_required", True),
                docs_required=eligibility_data.get("docs_required", []),
                waitlist_status=eligibility_data.get("waitlist_status"),
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
                categories=res_data.get("categories", ["housing"]),
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
    print("DMV Housing seeding complete!")
    print(f"  Created: {created} resources")
    print(f"  Skipped: {skipped} existing resources")
    print("=" * 50)


if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets")
    seed_dmv_housing(database_url)
