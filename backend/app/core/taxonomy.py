"""Core taxonomy definitions for veteran resources.

Categories and subcategories for classifying resources.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    """Resource category definition."""

    id: str
    name: str
    description: str


@dataclass(frozen=True)
class Subcategory:
    """Resource subcategory definition."""

    id: str
    name: str
    category_id: str
    description: str


# Main resource categories
CATEGORIES: dict[str, Category] = {
    "employment": Category(
        id="employment",
        name="Employment",
        description="Job placement, career services, and hiring programs for Veterans",
    ),
    "training": Category(
        id="training",
        name="Training & Education",
        description="Vocational rehabilitation, certifications, and educational benefits",
    ),
    "housing": Category(
        id="housing",
        name="Housing",
        description="HUD-VASH, SSVF, emergency shelters, and housing assistance",
    ),
    "legal": Category(
        id="legal",
        name="Legal",
        description="Legal aid, VA appeals, discharge upgrades, and benefits claims",
    ),
    "food": Category(
        id="food",
        name="Food Assistance",
        description="Food pantries, meal programs, and emergency food distributions",
    ),
    "benefits": Category(
        id="benefits",
        name="Benefits Consultation",
        description="VA claims assistance, benefits counseling, and accredited representatives",
    ),
    "mentalHealth": Category(
        id="mentalHealth",
        name="Mental Health",
        description="Counseling, PTSD support, crisis services, and mental wellness programs",
    ),
    "supportServices": Category(
        id="supportServices",
        name="Support Services",
        description="General Veteran support, peer mentoring, and case management",
    ),
    "healthcare": Category(
        id="healthcare",
        name="Healthcare",
        description="Medical care, VA health services, and wellness programs",
    ),
    "education": Category(
        id="education",
        name="Education",
        description="College programs, scholarships, and academic support",
    ),
    "financial": Category(
        id="financial",
        name="Financial",
        description="Financial counseling, emergency assistance, and debt relief",
    ),
    "family": Category(
        id="family",
        name="Family",
        description="Resources for Veteran families, spouses, dependents, survivors, and childcare support",
    ),
}

# Subcategories organized by parent category
SUBCATEGORIES: dict[str, Subcategory] = {
    # Employment subcategories
    "job-placement": Subcategory(
        id="job-placement",
        name="Job Placement",
        category_id="employment",
        description="Direct job placement services and hiring programs",
    ),
    "career-counseling": Subcategory(
        id="career-counseling",
        name="Career Counseling",
        category_id="employment",
        description="Career guidance, resume help, and interview prep",
    ),
    "veteran-preference": Subcategory(
        id="veteran-preference",
        name="Veteran Hiring Preference",
        category_id="employment",
        description="Employers with Veteran hiring programs",
    ),
    "self-employment": Subcategory(
        id="self-employment",
        name="Self-Employment & Entrepreneurship",
        category_id="employment",
        description="Small business support and Veteran-owned business resources",
    ),
    # Training subcategories
    "voc-rehab": Subcategory(
        id="voc-rehab",
        name="Vocational Rehabilitation",
        category_id="training",
        description="VA VR&E and state vocational programs",
    ),
    "certifications": Subcategory(
        id="certifications",
        name="Certifications & Licenses",
        category_id="training",
        description="Professional certifications and license programs",
    ),
    "apprenticeships": Subcategory(
        id="apprenticeships",
        name="Apprenticeships",
        category_id="training",
        description="On-the-job training and apprenticeship programs",
    ),
    "gi-bill": Subcategory(
        id="gi-bill",
        name="GI Bill Programs",
        category_id="training",
        description="GI Bill benefits and approved institutions",
    ),
    # Housing subcategories
    "hud-vash": Subcategory(
        id="hud-vash",
        name="HUD-VASH",
        category_id="housing",
        description="HUD-VASH voucher program",
    ),
    "ssvf": Subcategory(
        id="ssvf",
        name="SSVF",
        category_id="housing",
        description="Supportive Services for Veteran Families",
    ),
    "emergency-shelter": Subcategory(
        id="emergency-shelter",
        name="Emergency Shelter",
        category_id="housing",
        description="Emergency and transitional housing",
    ),
    "home-repair": Subcategory(
        id="home-repair",
        name="Home Repair & Modification",
        category_id="housing",
        description="Adaptive housing and home repair assistance",
    ),
    # Legal subcategories
    "va-appeals": Subcategory(
        id="va-appeals",
        name="VA Appeals",
        category_id="legal",
        description="VA claims and appeals assistance",
    ),
    "discharge-upgrade": Subcategory(
        id="discharge-upgrade",
        name="Discharge Upgrade",
        category_id="legal",
        description="Military discharge characterization upgrades",
    ),
    "legal-aid": Subcategory(
        id="legal-aid",
        name="General Legal Aid",
        category_id="legal",
        description="Free or low-cost legal services",
    ),
    "veterans-court": Subcategory(
        id="veterans-court",
        name="Veterans Treatment Court",
        category_id="legal",
        description="Veterans treatment courts and diversion programs",
    ),
    # Food subcategories
    "food-pantry": Subcategory(
        id="food-pantry",
        name="Food Pantry",
        category_id="food",
        description="Food banks and pantries for grocery pickup",
    ),
    "meal-program": Subcategory(
        id="meal-program",
        name="Meal Program",
        category_id="food",
        description="Hot meals and community dining programs",
    ),
    "mobile-distribution": Subcategory(
        id="mobile-distribution",
        name="Mobile Distribution",
        category_id="food",
        description="Mobile food pantries and pop-up distributions",
    ),
    "senior-food": Subcategory(
        id="senior-food",
        name="Senior Food Programs",
        category_id="food",
        description="SNAP assistance and senior-focused food programs",
    ),
    # Benefits subcategories
    "disability-claims": Subcategory(
        id="disability-claims",
        name="Disability Claims",
        category_id="benefits",
        description="VA disability compensation claims assistance",
    ),
    "pension-claims": Subcategory(
        id="pension-claims",
        name="Pension Claims",
        category_id="benefits",
        description="VA pension and aid & attendance claims",
    ),
    "education-benefits": Subcategory(
        id="education-benefits",
        name="Education Benefits",
        category_id="benefits",
        description="GI Bill and education benefits counseling",
    ),
    "healthcare-enrollment": Subcategory(
        id="healthcare-enrollment",
        name="Healthcare Enrollment",
        category_id="benefits",
        description="VA healthcare enrollment assistance",
    ),
    "survivor-benefits": Subcategory(
        id="survivor-benefits",
        name="Survivor Benefits",
        category_id="benefits",
        description="DIC and survivor benefit claims",
    ),
    "vso-services": Subcategory(
        id="vso-services",
        name="VSO Services",
        category_id="benefits",
        description="Veterans Service Organization representation",
    ),
    "cvso": Subcategory(
        id="cvso",
        name="County Veteran Service Officers",
        category_id="benefits",
        description="Local county-level Veteran service officers",
    ),
}

# Source tier definitions
SOURCE_TIERS: dict[int, dict[str, str | float]] = {
    1: {
        "name": "Official",
        "description": "Federal agencies (VA, DOL, HUD)",
        "reliability": 1.0,
    },
    2: {
        "name": "Established",
        "description": "Major VSOs (DAV, VFW, American Legion)",
        "reliability": 0.8,
    },
    3: {
        "name": "State",
        "description": "State Veteran agencies and departments",
        "reliability": 0.6,
    },
    4: {
        "name": "Community",
        "description": "Community directories and local organizations",
        "reliability": 0.4,
    },
}


def get_category(category_id: str) -> Category | None:
    """Get category by ID."""
    return CATEGORIES.get(category_id)


def get_subcategories(category_id: str) -> list[Subcategory]:
    """Get all subcategories for a category."""
    return [s for s in SUBCATEGORIES.values() if s.category_id == category_id]


def is_valid_category(category_id: str) -> bool:
    """Check if category ID is valid."""
    return category_id in CATEGORIES


def is_valid_subcategory(subcategory_id: str, category_id: str | None = None) -> bool:
    """Check if subcategory ID is valid, optionally checking parent category."""
    if subcategory_id not in SUBCATEGORIES:
        return False
    if category_id is not None:
        return SUBCATEGORIES[subcategory_id].category_id == category_id
    return True


def get_reliability_score(tier: int) -> float:
    """Get reliability score for a source tier."""
    tier_info = SOURCE_TIERS.get(tier)
    if tier_info is None:
        return 0.0
    reliability = tier_info.get("reliability", 0.0)
    return float(reliability)


# Eligibility tags organized by category
# These tags allow case managers to filter resources by specific criteria
ELIGIBILITY_TAGS: dict[str, dict[str, list[str]]] = {
    "housing": {
        "voucher": ["hud-vash", "ssvf", "section-8", "vash-voucher"],
        "type": ["emergency-shelter", "transitional", "permanent", "rapid-rehousing", "supportive_housing", "rental_assistance"],
        "eligibility": ["no-service-connection", "families", "singles-only", "veterans-only", "low-income"],
        "availability": ["waitlist-open", "accepting-now", "waitlist-closed"],
        "support": ["case-management", "case_management", "substance-abuse", "mental-health-support"],
    },
    "employment": {
        "type": ["entry-level", "skilled-trades", "remote", "part-time", "full-time", "federal-jobs"],
        "support": ["job-placement", "resume-help", "interview-prep", "career-counseling"],
        "employer": ["veteran-friendly", "federal-contractor", "military-spouse-friendly"],
        "industry": ["tech", "healthcare", "manufacturing", "logistics", "construction"],
    },
    "legal": {
        "type": ["free-legal-aid", "va-appeals", "discharge-upgrade", "pro-bono"],
        "scope": ["claims-help", "family-law", "housing-rights", "criminal-defense", "civil-rights"],
        "representation": ["attorney", "claims-agent", "vso-representative"],
    },
    "training": {
        "type": ["voc-rehab", "certifications", "apprenticeship", "on-the-job", "degree-program"],
        "format": ["in-person", "online", "hybrid", "self-paced"],
        "funding": ["gi-bill-approved", "vre-approved", "free", "scholarship-available"],
        "duration": ["short-term", "long-term", "bootcamp"],
    },
    "benefits": {
        "type": ["disability-claims", "pension", "education-benefits", "healthcare-enrollment"],
        "support": ["claims-assistance", "appeals-help", "benefits-counseling"],
        "representative": ["vso", "cvso", "accredited-attorney", "claims-agent"],
    },
    "food": {
        "type": ["food-pantry", "meal-program", "mobile-distribution", "groceries", "food-bank", "emergency-assistance"],
        "eligibility": ["no-id-required", "walk-in", "appointment-required"],
        "dietary": ["vegetarian", "halal", "kosher", "gluten-free"],
    },
    "mentalHealth": {
        "type": ["counseling", "ptsd-treatment", "crisis-services", "peer-support"],
        "format": ["in-person", "telehealth", "group-therapy", "individual"],
        "specialization": ["combat-trauma", "mst", "substance-abuse", "family-counseling"],
    },
    "healthcare": {
        "type": ["primary-care", "specialty-care", "dental", "vision", "urgent-care"],
        "eligibility": ["va-enrolled", "community-care", "no-va-required"],
        "access": ["walk-in", "appointment-only", "telehealth-available"],
    },
    "financial": {
        "type": ["emergency-assistance", "debt-counseling", "tax-prep", "savings-programs"],
        "eligibility": ["low-income", "no-income-requirement", "veteran-household"],
    },
    "education": {
        "type": ["college", "vocational", "tutoring", "scholarship"],
        "funding": ["gi-bill", "scholarship", "grants", "loans"],
        "level": ["undergraduate", "graduate", "certificate", "high-school-equivalency"],
    },
    "supportServices": {
        "type": ["case-management", "peer-mentoring", "transportation", "clothing"],
        "population": ["homeless-veterans", "female-veterans", "elderly-veterans", "disabled-veterans"],
    },
    "family": {
        "type": ["childcare", "spouse-support", "dependent-care", "survivor-benefits"],
        "eligibility": ["military-spouse", "dependent", "caregiver", "survivor"],
    },
}


@dataclass(frozen=True)
class EligibilityTag:
    """Eligibility tag definition."""

    id: str
    name: str
    category_id: str
    group: str


def get_eligibility_tags(category_id: str) -> dict[str, list[str]]:
    """Get all eligibility tags for a category."""
    return ELIGIBILITY_TAGS.get(category_id, {})


def get_all_eligibility_tags() -> dict[str, dict[str, list[str]]]:
    """Get the complete eligibility tags taxonomy."""
    return ELIGIBILITY_TAGS


def get_flat_tags_for_category(category_id: str) -> list[str]:
    """Get a flat list of all tags for a category."""
    tags = []
    category_tags = ELIGIBILITY_TAGS.get(category_id, {})
    for group_tags in category_tags.values():
        tags.extend(group_tags)
    return tags


def is_valid_eligibility_tag(tag: str, category_id: str | None = None) -> bool:
    """Check if a tag is valid, optionally for a specific category."""
    if category_id:
        return tag in get_flat_tags_for_category(category_id)

    # Check across all categories
    for cat_tags in ELIGIBILITY_TAGS.values():
        for group_tags in cat_tags.values():
            if tag in group_tags:
                return True
    return False


def get_tag_display_name(tag: str) -> str:
    """Convert tag ID to display name (e.g., 'hud-vash' -> 'HUD-VASH')."""
    # Special cases
    special_cases = {
        "hud-vash": "HUD-VASH",
        "ssvf": "SSVF",
        "section-8": "Section 8",
        "va-appeals": "VA Appeals",
        "gi-bill": "GI Bill",
        "gi-bill-approved": "GI Bill Approved",
        "vre-approved": "VR&E Approved",
        "vso": "VSO",
        "cvso": "CVSO",
        "ptsd-treatment": "PTSD Treatment",
        "mst": "MST",
    }
    if tag in special_cases:
        return special_cases[tag]

    # Default: capitalize words and replace hyphens with spaces
    return tag.replace("-", " ").title()
