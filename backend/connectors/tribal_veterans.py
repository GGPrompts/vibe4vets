"""Tribal Veteran Services connector for Urban Indian Health Organizations.

Imports data from the IHS/VA partnership including Urban Indian Health Organizations
and VA Tribal Health Programs serving American Indian/Alaska Native Veterans.

Sources:
- NCUIH Urban Indian Organization Directory (https://ncuih.org/uio-directory/)
- IHS Office of Urban Indian Health Programs (https://www.ihs.gov/urban/)
- VA-IHS MOU Native Veterans Map (https://www.ihs.gov/vaihsmou/findhealthcaremap/)
- VHA Office of Tribal Health (https://www.va.gov/health/vha-tribal-health.asp)

The IHS-VA MOU supports over 1,500 VA facilities and 41 Urban Indian Organizations
with 82+ locations providing health care to Native Veterans.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class TribalVeteransConnector(BaseConnector):
    """Connector for tribal veteran health services data.

    Parses the tribal_veteran_services.json file containing:
    - 41 Urban Indian Organizations (UIOs) across 20 states
    - VA Tribal Health Programs including Clinic-in-a-Clinic locations
    - Copayment exemption program for Native Veterans

    Urban Indian Organizations are IHS-funded nonprofits providing culturally
    competent health care to American Indian/Alaska Native people in urban areas.
    Many partner with VA through the IHS-VA MOU to serve Native Veterans.
    """

    DEFAULT_DATA_PATH = "data/reference/tribal_veteran_services.json"

    # Standard eligibility text for Urban Indian Organizations
    UIO_ELIGIBILITY = """American Indian and Alaska Native (AI/AN) individuals, with priority
for enrolled tribal members. Most UIOs serve all AI/AN people regardless of tribal
enrollment status. Native Veterans may be eligible for additional VA services through
IHS-VA partnerships. Some UIOs serve non-Native community members on a sliding fee
scale when capacity allows."""

    # Services commonly provided by UIOs
    UIO_CORE_SERVICES = [
        "primary medical care",
        "behavioral health services",
        "substance abuse treatment",
        "dental care",
        "pharmacy services",
        "traditional healing programs",
        "case management",
        "health education",
    ]

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to JSON file. Falls back to DEFAULT_DATA_PATH.
        """
        if data_path is None:
            current = Path(__file__).resolve().parent
            while current != current.parent:
                if (current / "data").is_dir():
                    break
                current = current.parent
            self.data_path = current / self.DEFAULT_DATA_PATH
        else:
            self.data_path = Path(data_path)

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="IHS/VA Tribal Veteran Services",
            url="https://www.ihs.gov/vaihsmou/findhealthcaremap/",
            tier=2,  # Established nonprofit/tribal organizations
            frequency="yearly",
            terms_url="https://www.ihs.gov/urban/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse tribal veteran services data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Tribal veteran services data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        # Parse Urban Indian Organizations
        for org in data.get("urban_indian_organizations", []):
            # Skip inactive organizations
            if not org.get("active", True):
                continue

            candidate = self._parse_urban_indian_org(org, fetched_at=now)
            resources.append(candidate)

        # Parse VA Tribal Programs
        for program in data.get("va_tribal_programs", []):
            candidate = self._parse_va_tribal_program(program, fetched_at=now)
            resources.append(candidate)

        return resources

    def _parse_urban_indian_org(
        self,
        org: dict[str, Any],
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse an Urban Indian Organization into a ResourceCandidate.

        Args:
            org: Organization data from JSON
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this organization.
        """
        name = org.get("name", "Urban Indian Health Organization")
        city = org.get("city")
        state = org.get("state")
        phone = org.get("phone")
        website = org.get("website")
        director = org.get("executive_director")
        ihs_region = org.get("ihs_region")

        # Build title
        title = f"{name}"
        if city and state:
            title = f"{name} - {city}, {state}"

        # Build description
        description = self._build_uio_description(name, city, state, director, ihs_region)

        # Build tags
        tags = self._build_uio_tags(state, ihs_region)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website or "https://ncuih.org/uio-directory/",
            org_name=name,
            org_website=website,
            city=city,
            state=self._normalize_state(state),
            categories=["healthcare", "supportServices", "mentalHealth"],
            tags=tags,
            phone=self._normalize_phone(phone),
            eligibility=self.UIO_ELIGIBILITY,
            how_to_apply=self._build_uio_how_to_apply(name, phone, website),
            scope="local",
            states=[state] if state else None,
            raw_data=org,
            fetched_at=fetched_at,
        )

    def _build_uio_description(
        self,
        name: str,
        city: str | None,
        state: str | None,
        director: str | None,
        ihs_region: str | None,
    ) -> str:
        """Build description for an Urban Indian Organization.

        Args:
            name: Organization name
            city: City location
            state: State code
            director: Executive director name
            ihs_region: IHS geographic region

        Returns:
            Formatted description string.
        """
        parts = []

        # Opening statement
        location = f"{city}, {state}" if city and state else (city or state or "the local area")
        parts.append(
            f"{name} is an Urban Indian Health Organization providing culturally competent "
            f"health care and support services to American Indian and Alaska Native people "
            f"in {location}."
        )

        # Native Veteran focus
        parts.append(
            "Through the IHS-VA Memorandum of Understanding, Urban Indian Organizations "
            "partner with the Department of Veterans Affairs to improve health care access "
            "for Native Veterans. Native Veterans can often access both IHS and VA services "
            "at these locations."
        )

        # Services
        services_text = ", ".join(self.UIO_CORE_SERVICES)
        parts.append(f"Services typically include: {services_text}.")

        # Cultural programs
        parts.append(
            "Many Urban Indian Organizations offer traditional healing practices, cultural "
            "programming, and community events alongside Western medical services."
        )

        # Leadership
        if director:
            parts.append(f"Executive Director: {director}.")

        # IHS region
        if ihs_region:
            parts.append(f"Part of IHS {ihs_region} Area.")

        return " ".join(parts)

    def _build_uio_how_to_apply(
        self,
        name: str,
        phone: str | None,
        website: str | None,
    ) -> str:
        """Build how-to-apply instructions for a UIO.

        Args:
            name: Organization name
            phone: Phone number
            website: Website URL

        Returns:
            How to apply string.
        """
        parts = [f"Contact {name} directly to schedule an appointment or learn about services."]

        if phone:
            parts.append(f"Call {self._normalize_phone(phone)} for more information.")

        if website:
            parts.append(f"Visit {website} to learn about available programs.")

        parts.append(
            "Most Urban Indian Organizations accept walk-ins for certain services. "
            "Bring tribal enrollment documentation if available, though services are "
            "generally available to all American Indian and Alaska Native individuals."
        )

        parts.append(
            "Native Veterans should ask about VA partnerships and whether they can access "
            "VA services at this location through the IHS-VA MOU."
        )

        return " ".join(parts)

    def _build_uio_tags(
        self,
        state: str | None,
        ihs_region: str | None,
    ) -> list[str]:
        """Build tags for an Urban Indian Organization.

        Args:
            state: State code
            ihs_region: IHS geographic region

        Returns:
            List of tag strings.
        """
        tags = [
            "tribal",
            "native-american",
            "alaska-native",
            "urban-indian-health",
            "ihs",
            "va-ihs-mou",
            "culturally-competent-care",
            "traditional-healing",
            "native-veteran",
        ]

        if state:
            tags.append(f"state-{state.lower()}")

        if ihs_region:
            tags.append(f"ihs-{ihs_region.lower().replace(' ', '-')}")

        return tags

    def _parse_va_tribal_program(
        self,
        program: dict[str, Any],
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a VA Tribal Program into a ResourceCandidate.

        Args:
            program: Program data from JSON
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this program.
        """
        name = program.get("name", "VA Tribal Health Program")
        program_type = program.get("type", "va_program")
        description = program.get("description", "")
        website = program.get("website")
        eligibility = program.get("eligibility")
        how_to_apply = program.get("how_to_apply")
        scope = program.get("scope", "national")
        contact_email = program.get("contact_email")

        # Handle Clinic-in-a-Clinic locations specially
        locations = program.get("locations", [])
        states_served = list({loc.get("state") for loc in locations if loc.get("state")})

        # Build enhanced description
        full_description = self._build_va_program_description(
            name, description, locations, contact_email
        )

        # Determine categories based on program type
        categories = ["benefits", "healthcare"]
        if "homelessness" in name.lower():
            categories.append("housing")

        # Build tags
        tags = self._build_va_program_tags(program_type, locations)

        # Determine scope based on locations
        if locations:
            scope = "local"
        elif scope == "national":
            states_served = None

        return ResourceCandidate(
            title=name,
            description=full_description,
            source_url=website or "https://www.va.gov/health/vha-tribal-health.asp",
            org_name="U.S. Department of Veterans Affairs - Office of Tribal Health",
            org_website="https://www.va.gov/health/vha-tribal-health.asp",
            email=contact_email,
            categories=categories,
            tags=tags,
            eligibility=eligibility or self._default_va_tribal_eligibility(),
            how_to_apply=how_to_apply or self._default_va_tribal_how_to_apply(contact_email),
            scope=scope,
            states=states_served if states_served else None,
            raw_data=program,
            fetched_at=fetched_at,
        )

    def _build_va_program_description(
        self,
        name: str,
        description: str,
        locations: list[dict],
        contact_email: str | None,
    ) -> str:
        """Build description for a VA Tribal Program.

        Args:
            name: Program name
            description: Base description
            locations: List of program locations
            contact_email: Contact email address

        Returns:
            Formatted description string.
        """
        parts = [description]

        if locations:
            location_names = [
                f"{loc.get('name')} ({loc.get('state')})"
                for loc in locations
                if loc.get("name")
            ]
            if location_names:
                parts.append(f"Current locations: {', '.join(location_names)}.")

        parts.append(
            "This program is part of VA's commitment to improving health care access "
            "for American Indian and Alaska Native Veterans through the IHS-VA MOU "
            "partnership established in 2003 and strengthened in subsequent agreements."
        )

        if contact_email:
            parts.append(f"For more information, contact: {contact_email}")

        return " ".join(parts)

    def _build_va_program_tags(
        self,
        program_type: str,
        locations: list[dict],
    ) -> list[str]:
        """Build tags for a VA Tribal Program.

        Args:
            program_type: Type of program
            locations: List of locations

        Returns:
            List of tag strings.
        """
        tags = [
            "va-tribal-health",
            "native-veteran",
            "va-ihs-mou",
            "tribal",
            "native-american",
            "alaska-native",
        ]

        if program_type == "va_program":
            tags.append("va-program")
        elif program_type == "federal_initiative":
            tags.append("federal-initiative")

        if locations:
            tags.append("clinic-in-a-clinic")
            for loc in locations:
                state = loc.get("state")
                if state:
                    tags.append(f"state-{state.lower()}")

        return list(set(tags))  # Deduplicate

    def _default_va_tribal_eligibility(self) -> str:
        """Return default eligibility for VA Tribal programs."""
        return (
            "American Indian and Alaska Native Veterans enrolled in VA health care. "
            "Tribal documentation may be required (tribal enrollment card, Certificate "
            "of Degree of Indian/Alaska Native Blood, or documentation on tribal letterhead). "
            "Contact the VHA Office of Tribal Health for specific program eligibility."
        )

    def _default_va_tribal_how_to_apply(self, contact_email: str | None) -> str:
        """Return default how-to-apply for VA Tribal programs."""
        parts = [
            "Contact the VHA Office of Tribal Health for more information about "
            "programs and eligibility."
        ]

        if contact_email:
            parts.append(f"Email: {contact_email}")

        parts.append(
            "You can also speak with your local VA Medical Center's tribal liaison "
            "or patient advocate about services available to Native Veterans."
        )

        return " ".join(parts)
