#!/usr/bin/env python3
"""Seed script for initial veteran resources from official sources."""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine

from app.models import Location, Organization, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus
from app.models.source import HealthStatus, SourceType

# Seed data: Official VA and DOL resources
SEED_DATA = [
    # Tier 1: VA.gov sources
    {
        "source": {
            "name": "VA.gov",
            "url": "https://www.va.gov",
            "source_type": SourceType.API,
            "tier": 1,
        },
        "resources": [
            {
                "org_name": "U.S. Department of Veterans Affairs",
                "org_website": "https://www.va.gov",
                "title": "Veterans Employment Center",
                "description": "The Veterans Employment Center (VEC) is a VA-hosted resource connecting Veterans, transitioning Service members, and their families with meaningful career opportunities.",
                "summary": "Official VA job board connecting veterans with employers committed to hiring veterans.",
                "eligibility": "Veterans, transitioning Service members, and military spouses.",
                "how_to_apply": "Create an account at VA.gov and access the Veterans Employment Center.",
                "categories": ["employment"],
                "subcategories": ["job_search", "career_counseling"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.va.gov/careers-employment/",
                "cost": "Free",
            },
            {
                "org_name": "U.S. Department of Veterans Affairs",
                "title": "Vocational Rehabilitation and Employment (VR&E)",
                "description": "VR&E helps Veterans with service-connected disabilities prepare for, find, and maintain suitable employment. Services include career counseling, training, education, and job placement assistance.",
                "summary": "Job training and career support for veterans with service-connected disabilities.",
                "eligibility": "Veterans with a service-connected disability rating of at least 10% or a memorandum rating.",
                "how_to_apply": "Apply online through VA.gov or visit your local VA regional office.",
                "categories": ["employment", "training"],
                "subcategories": ["vocational_rehab", "education"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.va.gov/careers-employment/vocational-rehabilitation/",
                "cost": "Free for eligible veterans",
            },
            {
                "org_name": "U.S. Department of Veterans Affairs",
                "title": "VA Supportive Services for Veteran Families (SSVF)",
                "description": "SSVF provides case management and supportive services to prevent homelessness and promote housing stability among very low-income Veteran families.",
                "summary": "Housing assistance and case management to prevent veteran homelessness.",
                "eligibility": "Very low-income Veteran families who are homeless or at risk of homelessness.",
                "how_to_apply": "Contact your local VA Medical Center or call the National Call Center for Homeless Veterans at 1-877-4AID-VET.",
                "categories": ["housing"],
                "subcategories": ["homeless_prevention", "case_management"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.va.gov/homeless/ssvf/",
                "phone": "1-877-424-3838",
                "cost": "Free",
            },
            {
                "org_name": "U.S. Department of Veterans Affairs",
                "title": "HUD-VASH (Veterans Affairs Supportive Housing)",
                "description": "HUD-VASH combines Housing Choice Voucher (Section 8) rental assistance with VA supportive services to help homeless Veterans and their families find and sustain permanent housing.",
                "summary": "Section 8 housing vouchers combined with VA case management for homeless veterans.",
                "eligibility": "Homeless Veterans and their families. Veterans must be eligible for VA health care.",
                "how_to_apply": "Contact your local VA Medical Center's HUD-VASH program or call the National Call Center for Homeless Veterans.",
                "categories": ["housing"],
                "subcategories": ["rental_assistance", "supportive_housing"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.va.gov/homeless/hud-vash.asp",
                "phone": "1-877-424-3838",
                "cost": "Free (provides rental assistance)",
            },
        ],
    },
    # Tier 1: Department of Labor
    {
        "source": {
            "name": "Department of Labor - VETS",
            "url": "https://www.dol.gov/agencies/vets",
            "source_type": SourceType.API,
            "tier": 1,
        },
        "resources": [
            {
                "org_name": "U.S. Department of Labor",
                "org_website": "https://www.dol.gov",
                "title": "Jobs for Veterans State Grants (JVSG)",
                "description": "JVSG provides funding to states to employ Disabled Veterans' Outreach Program (DVOP) specialists and Local Veterans' Employment Representatives (LVERs) to provide employment services to veterans.",
                "summary": "State-funded employment specialists dedicated to helping veterans find jobs.",
                "eligibility": "Veterans, particularly those with significant barriers to employment.",
                "how_to_apply": "Visit your local American Job Center (One-Stop Career Center) and ask for a DVOP specialist.",
                "categories": ["employment"],
                "subcategories": ["job_placement", "career_counseling"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.dol.gov/agencies/vets/programs/grants/state/jvsg",
                "cost": "Free",
            },
            {
                "org_name": "U.S. Department of Labor",
                "title": "Transition Assistance Program (TAP)",
                "description": "TAP provides information, tools, and training to ensure service members are prepared for their transition to civilian life. Includes employment workshops, VA benefits briefings, and financial planning.",
                "summary": "Comprehensive transition support for service members entering civilian life.",
                "eligibility": "Active duty service members within 24 months of separation or retirement.",
                "how_to_apply": "TAP workshops are mandatory for separating service members. Contact your installation's Transition Office.",
                "categories": ["employment", "training"],
                "subcategories": ["transition_assistance", "career_planning"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.dol.gov/agencies/vets/programs/tap",
                "cost": "Free",
            },
            {
                "org_name": "CareerOneStop",
                "org_website": "https://www.careeronestop.org",
                "title": "CareerOneStop Veterans Services",
                "description": "CareerOneStop provides career exploration, training, and job search resources specifically tailored for veterans, including skills translators and veteran-friendly employer listings.",
                "summary": "DOL-sponsored career tools including military skills translator.",
                "eligibility": "All veterans and transitioning service members.",
                "how_to_apply": "Access online resources at CareerOneStop.org or visit a local American Job Center.",
                "categories": ["employment", "training"],
                "subcategories": ["skills_assessment", "job_search"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.careeronestop.org/Veterans/",
                "cost": "Free",
            },
        ],
    },
    # Tier 2: Major VSOs
    {
        "source": {
            "name": "DAV (Disabled American Veterans)",
            "url": "https://www.dav.org",
            "source_type": SourceType.SCRAPE,
            "tier": 2,
        },
        "resources": [
            {
                "org_name": "Disabled American Veterans (DAV)",
                "org_website": "https://www.dav.org",
                "title": "DAV Veterans Employment Services",
                "description": "DAV offers employment resources including job fairs, resume assistance, interview coaching, and connections with veteran-friendly employers through the DAV Employment Network.",
                "summary": "Employment support from one of the largest veteran service organizations.",
                "eligibility": "All veterans, with priority for disabled veterans.",
                "how_to_apply": "Register at jobs.dav.org or attend a DAV/RecruitMilitary job fair.",
                "categories": ["employment"],
                "subcategories": ["job_fairs", "networking"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://jobs.dav.org",
                "phone": "1-877-426-2838",
                "cost": "Free",
            },
            {
                "org_name": "Disabled American Veterans (DAV)",
                "title": "DAV Benefits Assistance",
                "description": "Free assistance with filing VA disability claims and appeals. DAV National Service Officers help veterans navigate the claims process and ensure they receive earned benefits.",
                "summary": "Free help filing VA disability claims from certified service officers.",
                "eligibility": "All veterans seeking VA benefits.",
                "how_to_apply": "Contact your local DAV chapter or call the national helpline.",
                "categories": ["legal"],
                "subcategories": ["claims_assistance", "appeals"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.dav.org/veterans/i-need-help/",
                "phone": "1-877-426-2838",
                "cost": "Free",
            },
        ],
    },
    # Tier 2: American Legion
    {
        "source": {
            "name": "The American Legion",
            "url": "https://www.legion.org",
            "source_type": SourceType.SCRAPE,
            "tier": 2,
        },
        "resources": [
            {
                "org_name": "The American Legion",
                "org_website": "https://www.legion.org",
                "title": "American Legion Veterans Employment & Training",
                "description": "The American Legion provides employment assistance through accredited service officers, job fairs, and partnerships with employers committed to hiring veterans.",
                "summary": "Employment resources and job placement from the largest veterans organization.",
                "eligibility": "All veterans and their families.",
                "how_to_apply": "Visit your local American Legion post or contact the national headquarters.",
                "categories": ["employment"],
                "subcategories": ["job_placement", "training"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.legion.org/careers",
                "phone": "1-800-433-3318",
                "cost": "Free",
            },
            {
                "org_name": "The American Legion",
                "title": "American Legion Temporary Financial Assistance",
                "description": "TFA provides direct financial grants to minor children of veterans to help families meet basic needs during times of financial crisis.",
                "summary": "Emergency financial grants for veteran families with children.",
                "eligibility": "Minor children of veterans experiencing financial hardship.",
                "how_to_apply": "Apply through your local American Legion post or department.",
                "categories": ["housing"],
                "subcategories": ["emergency_assistance", "financial_aid"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.legion.org/financialassistance",
                "cost": "Grant program (not a loan)",
            },
        ],
    },
    # Tier 3: State agency example
    {
        "source": {
            "name": "Texas Veterans Commission",
            "url": "https://www.tvc.texas.gov",
            "source_type": SourceType.SCRAPE,
            "tier": 3,
        },
        "resources": [
            {
                "org_name": "Texas Veterans Commission",
                "org_website": "https://www.tvc.texas.gov",
                "title": "Texas Veterans Employment Services",
                "description": "Texas Veterans Commission Employment Services connects Texas veterans with employers and provides job search assistance, resume help, and career counseling through local Workforce Solutions offices.",
                "summary": "State-funded employment services for Texas veterans.",
                "eligibility": "Veterans residing in Texas.",
                "how_to_apply": "Visit a local Workforce Solutions office or contact TVC.",
                "categories": ["employment"],
                "subcategories": ["job_search", "career_counseling"],
                "scope": ResourceScope.STATE,
                "states": ["TX"],
                "website": "https://www.tvc.texas.gov/employment/",
                "phone": "1-512-463-6564",
                "cost": "Free",
                "location": {
                    "address": "1700 North Congress Avenue",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": "78701",
                },
            },
            {
                "org_name": "Texas Veterans Commission",
                "title": "Hazlewood Act Education Benefits",
                "description": "The Hazlewood Act provides qualified Texas Veterans, spouses, and dependent children with up to 150 hours of tuition-free education at Texas public colleges and universities.",
                "summary": "Free college tuition for Texas veterans and their families.",
                "eligibility": "Texas veterans with at least 181 days of active duty and honorable discharge, plus spouses and children.",
                "how_to_apply": "Apply through your college's financial aid office with DD-214 documentation.",
                "categories": ["training"],
                "subcategories": ["education", "tuition_assistance"],
                "scope": ResourceScope.STATE,
                "states": ["TX"],
                "website": "https://www.tvc.texas.gov/education/hazlewood/",
                "cost": "Free tuition (up to 150 hours)",
            },
        ],
    },
    # Legal Aid
    {
        "source": {
            "name": "National Veterans Legal Services Program",
            "url": "https://www.nvlsp.org",
            "source_type": SourceType.SCRAPE,
            "tier": 2,
        },
        "resources": [
            {
                "org_name": "National Veterans Legal Services Program (NVLSP)",
                "org_website": "https://www.nvlsp.org",
                "title": "NVLSP Free Legal Assistance",
                "description": "NVLSP provides free legal representation to veterans and their families in claims for VA benefits, including disability compensation, pension, and education benefits.",
                "summary": "Free legal representation for veterans seeking VA benefits.",
                "eligibility": "Veterans and their families with VA benefits claims.",
                "how_to_apply": "Contact NVLSP or apply through their website for legal assistance.",
                "categories": ["legal"],
                "subcategories": ["legal_representation", "appeals"],
                "scope": ResourceScope.NATIONAL,
                "website": "https://www.nvlsp.org/what-we-do/direct-representation",
                "cost": "Free",
            },
        ],
    },
]


def seed_database(database_url: str):
    """Seed the database with initial resources."""
    engine = create_engine(database_url, echo=True)

    with Session(engine) as session:
        for source_data in SEED_DATA:
            # Create source
            source_info = source_data["source"]
            source = Source(
                name=source_info["name"],
                url=source_info["url"],
                source_type=source_info["source_type"],
                tier=source_info["tier"],
                health_status=HealthStatus.HEALTHY,
                last_success=datetime.utcnow(),
            )
            session.add(source)
            session.flush()

            # Create resources
            for res_data in source_data["resources"]:
                # Find or create organization
                org_name = res_data.get("org_name", source_info["name"])
                org_website = res_data.get("org_website", source_info["url"])

                org = Organization(
                    name=org_name,
                    website=org_website,
                )
                session.add(org)
                session.flush()

                # Create location if provided
                location = None
                if "location" in res_data:
                    loc_data = res_data["location"]
                    location = Location(
                        organization_id=org.id,
                        address=loc_data["address"],
                        city=loc_data["city"],
                        state=loc_data["state"],
                        zip_code=loc_data["zip_code"],
                    )
                    session.add(location)
                    session.flush()

                # Calculate reliability score based on tier
                tier_scores = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4}
                reliability = tier_scores.get(source_info["tier"], 0.5)

                # Create resource
                resource = Resource(
                    organization_id=org.id,
                    location_id=location.id if location else None,
                    source_id=source.id,
                    title=res_data["title"],
                    description=res_data["description"],
                    summary=res_data.get("summary"),
                    eligibility=res_data.get("eligibility"),
                    how_to_apply=res_data.get("how_to_apply"),
                    categories=res_data.get("categories", []),
                    subcategories=res_data.get("subcategories", []),
                    scope=res_data.get("scope", ResourceScope.NATIONAL),
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

        session.commit()
        print(f"Successfully seeded {len(SEED_DATA)} sources with resources!")


if __name__ == "__main__":
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets"
    )
    seed_database(database_url)
