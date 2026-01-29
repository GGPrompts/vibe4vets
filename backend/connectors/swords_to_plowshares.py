"""Swords to Plowshares veteran services connector.

Swords to Plowshares is a comprehensive veteran service organization serving the
San Francisco Bay Area, founded in 1974 by Vietnam veterans. They provide:
- Permanent supportive housing (500+ units)
- Legal services (discharge upgrades, VA benefits appeals)
- Employment services
- Mental health and wellness programs

Source: https://www.swords-to-plowshares.org/
"""

from datetime import UTC, datetime

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Swords to Plowshares program data
# Last updated: 2026-01-29
# Source: https://www.swords-to-plowshares.org/
SWORDS_TO_PLOWSHARES_PROGRAMS = [
    {
        "id": "stp-housing",
        "name": "Swords to Plowshares Housing Programs",
        "category": "housing",
        "description": (
            "Swords to Plowshares operates 500+ units of permanent supportive housing "
            "across San Francisco, including the nation's first veteran-specific permanent "
            "supportive housing opened in 2000. Housing programs provide on-site support staff, "
            "case management, peer counseling, daily meals, and wraparound services. "
            "They have permanently housed over 1,000 veterans and their families through "
            "diverse housing programs including rental assistance for veterans to secure "
            "their own apartments."
        ),
        "services": [
            "permanent supportive housing",
            "transitional housing",
            "rental assistance",
            "case management",
            "on-site support staff",
            "peer counseling",
            "daily meals",
            "in-home habitability support",
            "transportation to medical appointments",
        ],
        "eligibility": (
            "Veterans experiencing homelessness or at risk of homelessness in the "
            "San Francisco Bay Area. Priority given to veterans with disabilities. "
            "Programs serve formerly homeless veterans and their families."
        ),
        "how_to_apply": (
            "Contact the San Francisco Veterans Center at (415) 252-4788 or visit "
            "1060 Howard St, San Francisco, CA 94103 during business hours. "
            "Intake assessments available Monday-Saturday. You can also contact "
            "the Oakland Veterans Center at (510) 844-7500."
        ),
        "tags": [
            "permanent-supportive-housing",
            "transitional-housing",
            "homeless-services",
            "rental-assistance",
            "case-management",
            "wraparound-services",
        ],
    },
    {
        "id": "stp-legal",
        "name": "Swords to Plowshares Legal Services",
        "category": "legal",
        "description": (
            "Free legal services for veterans including VA benefits representation, "
            "discharge upgrade assistance, and appeals support. Swords to Plowshares "
            "was the first VA-certified veteran service organization (1978) and has "
            "decades of experience navigating the VA system. They offer pro bono legal "
            "programs, self-help guides on Agent Orange and Gulf War exposures, and "
            "have won over $15 million in lifetime income for veterans with disabilities "
            "through benefits claims."
        ),
        "services": [
            "VA benefits claims assistance",
            "discharge upgrade representation",
            "VA benefits appeals",
            "pro bono legal program",
            "Agent Orange exposure claims",
            "Gulf War exposure claims",
            "legal self-help guides",
        ],
        "eligibility": (
            "Veterans in the San Francisco Bay Area seeking assistance with VA benefits, "
            "discharge upgrades, or military-related legal issues. No discharge status "
            "restrictions for initial consultation."
        ),
        "how_to_apply": (
            "Contact the San Francisco Veterans Center at (415) 252-4788 to schedule "
            "a legal consultation. Walk-in legal clinics available at 1060 Howard St, "
            "San Francisco. Legal self-help guides available online at "
            "swords-to-plowshares.org."
        ),
        "tags": [
            "legal-aid",
            "va-benefits",
            "discharge-upgrade",
            "appeals",
            "pro-bono",
            "agent-orange",
            "gulf-war",
            "free-legal-services",
        ],
    },
    {
        "id": "stp-employment",
        "name": "Swords to Plowshares Employment Services",
        "category": "employment",
        "description": (
            "Employment services to support veterans' economic independence and financial "
            "stability. Programs include access to the Veterans Job Board connecting "
            "veterans with employment opportunities, job training, career counseling, "
            "and income assistance for veterans with disabilities. Focus on helping "
            "veterans transition to civilian careers and achieve long-term financial security."
        ),
        "services": [
            "veterans job board",
            "job training",
            "career counseling",
            "resume assistance",
            "interview preparation",
            "income assistance",
            "financial stability support",
        ],
        "eligibility": (
            "Veterans in the San Francisco Bay Area seeking employment assistance. "
            "Services available regardless of discharge status."
        ),
        "how_to_apply": (
            "Contact the San Francisco Veterans Center at (415) 252-4788 or visit "
            "1060 Howard St, San Francisco, CA 94103 to meet with an employment specialist. "
            "The Veterans Job Board is accessible online. Oakland location also available "
            "at (510) 844-7500."
        ),
        "tags": [
            "employment",
            "job-training",
            "career-services",
            "job-board",
            "financial-stability",
            "veteran-employers",
        ],
    },
    {
        "id": "stp-mental-health",
        "name": "Swords to Plowshares Mental Health & Wellness",
        "category": "mentalHealth",
        "description": (
            "Comprehensive mental health and wellness services for veterans including "
            "peer counseling, support groups, crisis intervention, and the Combat to "
            "Community professional training program. The Veterans Community Center "
            "provides a supportive environment for connection and healing. Services "
            "include healthcare navigation, counseling, and community meals that have "
            "served over 90,000 veterans to increase food security and social connection."
        ),
        "services": [
            "peer counseling",
            "support groups",
            "crisis intervention",
            "healthcare navigation",
            "community meals",
            "Combat to Community training",
            "Veterans Community Center",
            "wellness programs",
        ],
        "eligibility": (
            "Veterans in the San Francisco Bay Area. Mental health services available "
            "regardless of VA enrollment or discharge status. Family members may also "
            "be eligible for certain programs."
        ),
        "how_to_apply": (
            "Contact the San Francisco Veterans Center at (415) 252-4788 to schedule "
            "an intake appointment. Drop-in support available at 1060 Howard St, "
            "San Francisco during business hours. For crisis support, call the Veterans "
            "Crisis Line at 988 (press 1)."
        ),
        "tags": [
            "mental-health",
            "peer-counseling",
            "support-groups",
            "crisis-intervention",
            "community-center",
            "wellness",
            "food-security",
            "healthcare-navigation",
        ],
    },
]

# Location data for Swords to Plowshares centers
SWORDS_TO_PLOWSHARES_LOCATIONS = {
    "sf": {
        "name": "San Francisco Veterans Center",
        "address": "1060 Howard St",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94103",
        "phone": "(415) 252-4788",
        "hours": "Mon 9AM-7PM, Tue-Thu 8AM-7PM, Fri 8AM-6PM, Sat 11AM-7PM",
    },
    "oakland": {
        "name": "Oakland Veterans Center",
        "address": "330 Franklin St, Suite 100",
        "city": "Oakland",
        "state": "CA",
        "zip_code": "94607",
        "phone": "(510) 844-7500",
        "hours": "Mon-Fri 8:30AM-4:30PM",
    },
}


class SwordsToPlowsharesConnector(BaseConnector):
    """Connector for Swords to Plowshares veteran services.

    Swords to Plowshares is a comprehensive veteran service organization in the
    San Francisco Bay Area, founded in 1974 by Vietnam veterans. They provide:
    - Permanent supportive housing (500+ units)
    - Legal services (discharge upgrades, VA benefits)
    - Employment services
    - Mental health and wellness programs

    This connector creates separate ResourceCandidate objects for each program
    type to allow veterans to find specific services.
    """

    # Organization info
    ORG_NAME = "Swords to Plowshares"
    ORG_WEBSITE = "https://www.swords-to-plowshares.org/"
    FOUNDED = "1974"

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Swords to Plowshares",
            url="https://www.swords-to-plowshares.org/",
            tier=2,  # Established nonprofit
            frequency="monthly",
            terms_url="https://www.swords-to-plowshares.org/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Return Swords to Plowshares program resources.

        Returns:
            List of ResourceCandidate objects for each program type.
        """
        now = datetime.now(UTC)
        resources: list[ResourceCandidate] = []

        for program in SWORDS_TO_PLOWSHARES_PROGRAMS:
            candidate = self._parse_program(program, fetched_at=now)
            resources.append(candidate)

        return resources

    def _parse_program(
        self,
        program: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse program data into a ResourceCandidate.

        Args:
            program: Program data dictionary.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this program.
        """
        program_id = program["id"]
        program_name = program["name"]
        category = program["category"]
        description = program["description"]
        services = program.get("services", [])
        eligibility = program.get("eligibility", "")
        how_to_apply = program.get("how_to_apply", "")
        tags = program.get("tags", [])

        # Use SF location as primary
        sf_location = SWORDS_TO_PLOWSHARES_LOCATIONS["sf"]

        # Build title based on category
        title = self._build_title(program_name, category)

        # Build extended description
        full_description = self._build_description(description, services)

        # Build tags including base tags
        full_tags = self._build_tags(tags, category, program_id)

        return ResourceCandidate(
            title=title,
            description=full_description,
            source_url=self.ORG_WEBSITE,
            org_name=self.ORG_NAME,
            org_website=self.ORG_WEBSITE,
            address=sf_location["address"],
            city=sf_location["city"],
            state=sf_location["state"],
            zip_code=sf_location["zip_code"],
            categories=[category],
            tags=full_tags,
            phone=sf_location["phone"],
            hours=sf_location["hours"],
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="local",
            states=["CA"],
            raw_data={
                "program_id": program_id,
                "program_name": program_name,
                "category": category,
                "services": services,
                "locations": SWORDS_TO_PLOWSHARES_LOCATIONS,
                "founded": self.FOUNDED,
            },
            fetched_at=fetched_at,
        )

    def _build_title(self, program_name: str, category: str) -> str:
        """Build resource title.

        Args:
            program_name: Full program name.
            category: Service category.

        Returns:
            Formatted title string.
        """
        category_suffix = {
            "housing": "Permanent Supportive Housing",
            "legal": "Free Legal Aid",
            "employment": "Career Services",
            "mentalHealth": "Mental Health Support",
        }
        suffix = category_suffix.get(category, "Veteran Services")
        return f"{program_name} - {suffix}"

    def _build_description(self, description: str, services: list[str]) -> str:
        """Build extended description.

        Args:
            description: Base program description.
            services: List of services offered.

        Returns:
            Formatted description string.
        """
        parts = [description]

        # Add services list
        if services:
            services_str = ", ".join(services[:6])
            if len(services) > 6:
                services_str += f", and {len(services) - 6} more"
            parts.append(f"Services include: {services_str}.")

        # Add organization context
        parts.append(
            "Founded in 1974 by Vietnam veterans, Swords to Plowshares serves "
            "over 3,000 Bay Area veterans annually with wraparound care and advocacy."
        )

        return " ".join(parts)

    def _build_tags(self, program_tags: list[str], category: str, program_id: str) -> list[str]:
        """Build tags list.

        Args:
            program_tags: Program-specific tags.
            category: Service category.
            program_id: Program identifier.

        Returns:
            List of tag strings.
        """
        tags = [
            "swords-to-plowshares",
            "bay-area",
            "san-francisco",
            "veteran-services",
        ]

        # Add category tag
        category_tags = {
            "housing": "housing-services",
            "legal": "legal-services",
            "employment": "employment-services",
            "mentalHealth": "mental-health-services",
        }
        if category in category_tags:
            tags.append(category_tags[category])

        # Add program-specific tags
        tags.extend(program_tags)

        # Add program ID tag
        tags.append(program_id)

        # Add state tag
        tags.append("state-ca")

        return tags
