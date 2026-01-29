"""State VA Office connector with detailed location data.

Imports detailed state veteran affairs office data including main offices
and regional field offices with full contact information.

Covers all 50 states plus DC and US territories.

Source: Compiled from state VA agency websites and NASDVA directory.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class StateVAOfficesConnector(BaseConnector):
    """Connector for detailed state veteran affairs office data.

    Parses the state_va_offices.json file containing detailed contact
    information for all state and territory veteran affairs agencies,
    including their main offices and regional field offices.

    Data fields per office:
        - state: Two-letter state/territory code
        - state_name: Full state name
        - agency_name: Official agency name
        - main_office: Main office details (address, phone, email, etc.)
        - services: List of services offered
        - regional_offices: List of regional/field offices

    Each office entry includes:
        - name: Office name
        - address: Street address
        - city: City name
        - zip_code: ZIP code
        - phone: Phone number
        - fax: Fax number (optional)
        - email: Email address (optional)
        - website: Website URL (optional)
        - hours: Operating hours (optional)
    """

    DEFAULT_DATA_PATH = "data/reference/state_va_offices.json"

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
            name="State VA Offices (Detailed)",
            url="https://nasdva.us/resources/",
            tier=3,  # State-level agencies
            frequency="quarterly",  # Offices change infrequently
            terms_url="https://nasdva.us/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse state VA office data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
            Includes both main offices and regional offices as separate resources.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"State VA offices data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for entry in data.get("offices", []):
            state = entry.get("state")
            state_name = entry.get("state_name")
            agency_name = entry.get("agency_name")
            services = entry.get("services", [])
            main_office = entry.get("main_office", {})
            regional_offices = entry.get("regional_offices", [])

            # Add main office as a resource
            if main_office:
                candidate = self._parse_office(
                    state=state,
                    state_name=state_name,
                    agency_name=agency_name,
                    office=main_office,
                    services=services,
                    is_main_office=True,
                    fetched_at=now,
                )
                resources.append(candidate)

            # Add regional offices as separate resources
            for regional_office in regional_offices:
                candidate = self._parse_office(
                    state=state,
                    state_name=state_name,
                    agency_name=agency_name,
                    office=regional_office,
                    services=services,
                    is_main_office=False,
                    fetched_at=now,
                )
                resources.append(candidate)

        return resources

    def _parse_office(
        self,
        state: str | None,
        state_name: str | None,
        agency_name: str | None,
        office: dict,
        services: list[str],
        is_main_office: bool,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse an office entry into a ResourceCandidate.

        Args:
            state: Two-letter state code
            state_name: Full state name
            agency_name: Official agency name
            office: Office data dictionary
            services: List of services offered
            is_main_office: True if this is the main/headquarters office
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this office.
        """
        office_name = office.get("name", "")
        address = office.get("address")
        city = office.get("city")
        zip_code = office.get("zip_code")
        phone = office.get("phone")
        fax = office.get("fax")
        email = office.get("email")
        website = office.get("website")
        hours = office.get("hours")

        title = self._build_title(agency_name, office_name, state, is_main_office)
        description = self._build_description(
            state_name, agency_name, office_name, services, is_main_office
        )

        # Build full address string
        full_address = self._build_full_address(address, city, state, zip_code)

        # Build source URL - prefer office website, fall back to NASDVA
        source_url = website or "https://nasdva.us/resources/"

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name=agency_name or f"{state_name} Veterans Affairs",
            org_website=website,
            address=full_address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["benefits", "supportServices"],
            tags=self._build_tags(state, services, is_main_office),
            phone=self._normalize_phone(phone),
            email=email,
            hours=hours,
            eligibility=self._build_eligibility(state_name),
            how_to_apply=self._build_how_to_apply(
                agency_name, office_name, phone, email, website
            ),
            scope="state",
            states=[state] if state else None,
            raw_data={
                "state": state,
                "state_name": state_name,
                "agency_name": agency_name,
                "office_name": office_name,
                "address": address,
                "city": city,
                "zip_code": zip_code,
                "phone": phone,
                "fax": fax,
                "email": email,
                "website": website,
                "hours": hours,
                "services": services,
                "is_main_office": is_main_office,
            },
            fetched_at=fetched_at,
        )

    def _build_title(
        self,
        agency_name: str | None,
        office_name: str | None,
        state: str | None,
        is_main_office: bool,
    ) -> str:
        """Build resource title.

        Args:
            agency_name: Official agency name
            office_name: Specific office name
            state: State code
            is_main_office: True if main/headquarters office

        Returns:
            Formatted title string.
        """
        if office_name:
            return office_name
        if agency_name:
            if is_main_office:
                return f"{agency_name} - Main Office"
            return agency_name
        if state:
            return f"{state} Department of Veterans Affairs"
        return "State Veterans Affairs Office"

    def _build_description(
        self,
        state_name: str | None,
        agency_name: str | None,
        office_name: str | None,
        services: list[str],
        is_main_office: bool,
    ) -> str:
        """Build resource description.

        Args:
            state_name: Full state name
            agency_name: Official agency name
            office_name: Specific office name
            services: List of services offered
            is_main_office: True if main/headquarters office

        Returns:
            Formatted description string.
        """
        parts = []

        # Opening description
        if is_main_office:
            if agency_name and state_name:
                parts.append(
                    f"The {agency_name} is the official state agency serving Veterans "
                    f"in {state_name}. This is the main headquarters office."
                )
            elif state_name:
                parts.append(
                    f"Official state Veteran affairs headquarters serving Veterans in {state_name}."
                )
        else:
            if office_name and state_name:
                parts.append(
                    f"{office_name} is a regional field office providing Veteran services "
                    f"for {state_name} residents."
                )
            elif state_name:
                parts.append(
                    f"Regional field office providing Veteran services for {state_name} residents."
                )

        # Core services description
        parts.append(
            "State Veteran affairs offices provide assistance with federal VA claims, "
            "state-specific Veteran benefits, employment services, education benefits, "
            "and referrals to local Veteran service organizations."
        )

        # Specific services if provided
        if services:
            services_text = ", ".join(services[:6])  # Limit display
            if len(services) > 6:
                services_text += f", and {len(services) - 6} more services"
            parts.append(f"Services include: {services_text}.")

        return " ".join(parts)

    def _build_eligibility(self, state_name: str | None) -> str:
        """Build eligibility description.

        Args:
            state_name: Full state name

        Returns:
            Eligibility description string.
        """
        location = state_name if state_name else "this state"

        return (
            f"Veterans residing in {location}. State Veteran affairs offices serve all "
            "Veterans regardless of service era, discharge status, or VA enrollment. "
            "Many state benefits are available to Veterans who may not qualify for "
            "federal VA benefits. Family members and survivors of Veterans may also "
            "be eligible for certain state benefits."
        )

    def _build_how_to_apply(
        self,
        agency_name: str | None,
        office_name: str | None,
        phone: str | None,
        email: str | None,
        website: str | None,
    ) -> str:
        """Build how to apply instructions.

        Args:
            agency_name: Official agency name
            office_name: Specific office name
            phone: Office phone number
            email: Office email address
            website: Office website

        Returns:
            How to apply instructions string.
        """
        parts = []
        office_display = office_name or agency_name or "the state VA office"

        # Primary contact method
        if phone:
            parts.append(f"Call {office_display} at {phone} to schedule an appointment.")
        elif email:
            parts.append(f"Email {office_display} at {email} to schedule an appointment.")
        else:
            parts.append(f"Contact {office_display} to schedule an appointment.")

        # Website
        if website:
            parts.append(f"Visit {website} for more information and online services.")

        # What to bring
        parts.append(
            "Bring your DD-214 (discharge papers), any VA correspondence, and "
            "documentation related to your inquiry. State offices can assist "
            "with federal VA claims, state-specific benefits, and connecting "
            "you to local resources."
        )

        return " ".join(parts)

    def _build_full_address(
        self,
        address: str | None,
        city: str | None,
        state: str | None,
        zip_code: str | None,
    ) -> str | None:
        """Build full address string.

        Args:
            address: Street address
            city: City name
            state: State code
            zip_code: ZIP code

        Returns:
            Full address string or None if no address.
        """
        if not address:
            return None

        if city and state and zip_code:
            return f"{address}, {city}, {state} {zip_code}"
        elif city and state:
            return f"{address}, {city}, {state}"
        elif city:
            return f"{address}, {city}"
        return address

    def _build_tags(
        self,
        state: str | None,
        services: list[str],
        is_main_office: bool,
    ) -> list[str]:
        """Build tags list.

        Args:
            state: Two-letter state code
            services: List of services offered
            is_main_office: True if main/headquarters office

        Returns:
            List of tag strings.
        """
        tags = [
            "state-va",
            "state-benefits",
            "veteran-services",
            "claims-assistance",
            "free-services",
        ]

        if is_main_office:
            tags.append("headquarters")
        else:
            tags.append("regional-office")

        if state:
            tags.append(f"state-{state.lower()}")

        # Add service-based tags
        service_tag_map = {
            "claims": "va-claims",
            "education": "education-benefits",
            "employment": "employment-services",
            "housing": "housing-assistance",
            "healthcare": "healthcare",
            "burial": "burial-benefits",
            "cemetery": "cemetery",
            "veterans home": "veterans-home",
            "nursing": "nursing-home",
            "women": "women-veterans",
            "trust fund": "financial-assistance",
            "emergency": "emergency-assistance",
            "property tax": "property-tax-exemption",
        }

        services_lower = " ".join(services).lower()
        for keyword, tag in service_tag_map.items():
            if keyword in services_lower:
                tags.append(tag)

        return list(set(tags))  # Deduplicate
