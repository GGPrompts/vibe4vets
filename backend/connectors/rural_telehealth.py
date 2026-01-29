"""Rural Veteran Telehealth Programs connector.

Imports curated data about telehealth programs serving Veterans in rural and
underserved areas, including:
- VA ATLAS (Accessing Telehealth through Local Area Stations)
- VA Connected Devices Program
- HRSA FLEX grant programs (Alaska, Montana, Maine)
- Cohen Veterans Network telehealth
- VA Video Connect and rural health initiatives

Source: Curated from VA Office of Rural Health, HRSA, and nonprofit sources
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class RuralTelehealthConnector(BaseConnector):
    """Connector for rural Veteran telehealth programs.

    Loads curated data about telehealth programs specifically designed to
    reach Veterans in rural, frontier, and underserved areas. These programs
    address the geographic barriers that prevent many Veterans from accessing
    VA health care in person.

    Programs include:
    - VA ATLAS community telehealth sites
    - VA Connected Devices (free tablets/internet)
    - State FLEX grant programs (AK, MT, ME)
    - National telehealth initiatives for rural Veterans
    - Nonprofit telehealth mental health services
    """

    # Data file path relative to project root
    DATA_PATH = "data/reference/rural_telehealth_programs.json"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to data JSON. Falls back to DATA_PATH.
        """
        root = self._find_project_root()
        self.data_path = Path(data_path) if data_path else root / self.DATA_PATH

    def _find_project_root(self) -> Path:
        """Find project root (directory containing 'data' folder)."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / "data").is_dir():
                return current
            current = current.parent
        return Path(__file__).resolve().parent.parent

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Rural Veteran Telehealth Programs",
            url="https://www.ruralhealth.va.gov/",
            tier=1,  # Primarily VA programs with some tier 2 nonprofits
            frequency="monthly",  # Programs change infrequently
            terms_url=None,
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse and return rural telehealth resources.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        now = datetime.now(UTC)

        data = self._load_data()
        if not data:
            return []

        resources: list[ResourceCandidate] = []

        for program in data.get("programs", []):
            # Create main program resource
            candidate = self._parse_program(program, fetched_at=now)
            resources.append(candidate)

            # Create resources for specific locations if available
            locations = program.get("locations", [])
            if locations:
                for location in locations:
                    location_candidate = self._parse_location(program, location, fetched_at=now)
                    resources.append(location_candidate)

        return resources

    def _load_data(self) -> dict[str, Any]:
        """Load resource data from JSON file."""
        if not self.data_path.exists():
            return {}

        with open(self.data_path) as f:
            return json.load(f)

    def _parse_program(
        self,
        program: dict[str, Any],
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a program entry into a ResourceCandidate.

        Args:
            program: Dictionary containing program data.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this telehealth program.
        """
        org_name = program.get("org_name", "Unknown Organization")
        program_name = program.get("name", "Telehealth Services")
        website = program.get("website")
        phone = program.get("phone")
        email = program.get("email")
        # tier is available in program data but not currently used
        _ = program.get("tier", 2)

        title = self._build_title(program_name)
        description = self._build_description(program)
        eligibility = self._build_eligibility(program)
        how_to_apply = self._build_how_to_apply(program)
        tags = self._build_tags(program)
        categories = program.get("categories", ["healthcare"])

        # Determine scope
        scope = program.get("scope", "national")
        states = program.get("states")

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website or "https://www.ruralhealth.va.gov/",
            org_name=org_name,
            org_website=website,
            categories=categories,
            tags=tags,
            phone=self._normalize_phone(phone) if phone else None,
            email=email,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope=scope,
            states=states,
            raw_data=program,
            fetched_at=fetched_at,
        )

    def _parse_location(
        self,
        program: dict[str, Any],
        location: dict[str, Any],
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a specific location into a ResourceCandidate.

        Args:
            program: Parent program data.
            location: Location-specific data.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this telehealth location.
        """
        org_name = program.get("org_name", "Unknown Organization")
        program_name = program.get("name", "Telehealth Services")
        location_name = location.get("name", "Telehealth Site")
        city = location.get("city", "")
        state = location.get("state", "")

        # Build location-specific title
        title = f"{location_name} - {program_name.split('-')[0].strip()} Telehealth"
        if len(title) > 100:
            title = f"{location_name} - Rural Telehealth"

        description = self._build_location_description(program, location)
        eligibility = self._build_eligibility(program)
        how_to_apply = self._build_how_to_apply(program)
        tags = self._build_tags(program)
        tags.append("telehealth-site")
        categories = program.get("categories", ["healthcare"])

        # Build full address
        address = location.get("address", "")
        zip_code = location.get("zip", "")

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=program.get("website") or "https://www.ruralhealth.va.gov/",
            org_name=org_name,
            org_website=program.get("website"),
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=categories,
            tags=tags,
            phone=self._normalize_phone(program.get("phone")) if program.get("phone") else None,
            email=program.get("email"),
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="local",
            states=[state] if state else None,
            raw_data={"program": program, "location": location},
            fetched_at=fetched_at,
        )

    def _build_title(self, program_name: str) -> str:
        """Build resource title."""
        # Keep title concise but descriptive
        if "Telehealth" not in program_name and "ATLAS" not in program_name:
            return f"{program_name} - Rural Telehealth"
        return program_name

    def _build_description(self, program: dict[str, Any]) -> str:
        """Build resource description with key details."""
        parts = []

        # Main description from data
        description = program.get("description")
        if description:
            parts.append(description)

        # Add services offered
        services = program.get("services", [])
        if services:
            services_str = ", ".join(services[:5])
            if len(services) > 5:
                services_str += f", and {len(services) - 5} more services"
            parts.append(f"Services include: {services_str}.")

        # Add coverage area if regional/state
        coverage_area = program.get("coverage_area")
        if coverage_area:
            parts.append(f"Coverage area: {coverage_area}.")

        return " ".join(parts)

    def _build_location_description(
        self,
        program: dict[str, Any],
        location: dict[str, Any],
    ) -> str:
        """Build description for a specific location."""
        parts = []

        location_name = location.get("name", "")
        city = location.get("city", "")
        state = location.get("state", "")
        program_name = program.get("name", "")

        # Location-specific intro
        if "ATLAS" in program_name:
            parts.append(
                f"{location_name} in {city}, {state} is a VA ATLAS telehealth site "
                "where Veterans can connect with VA providers via secure video in a "
                "private, comfortable setting."
            )
        else:
            parts.append(
                f"{location_name} in {city}, {state} offers VA telehealth services "
                "for Veterans who live far from VA medical facilities."
            )

        # Add services from parent program
        services = program.get("services", [])
        if services:
            services_str = ", ".join(services[:4])
            parts.append(f"Available services: {services_str}.")

        # Add general program info
        description = program.get("description", "")
        if description and len(description) < 200:
            parts.append(description)

        return " ".join(parts)

    def _build_eligibility(self, program: dict[str, Any]) -> str:
        """Build eligibility description."""
        eligibility = program.get("eligibility", {})
        parts = []

        # Main eligibility summary
        summary = eligibility.get("summary")
        if summary:
            parts.append(summary)

        # VA enrollment requirement
        va_required = eligibility.get("va_enrollment_required")
        if va_required is True:
            parts.append("VA health care enrollment required.")
        elif va_required is False:
            parts.append("No VA enrollment required.")

        # Additional notes
        notes = eligibility.get("notes")
        if notes:
            parts.append(notes)

        return " ".join(parts) if parts else "Contact the program for eligibility requirements."

    def _build_how_to_apply(self, program: dict[str, Any]) -> str:
        """Build application/access instructions."""
        parts = []

        # Access method if available
        access_method = program.get("access_method")
        if access_method:
            parts.append(access_method)

        # Phone with instructions
        phone = program.get("phone")
        if phone and not access_method:
            parts.append(f"Call {phone} to schedule a telehealth appointment.")

        # Email
        email = program.get("email")
        if email:
            parts.append(f"Email: {email}")

        # Website
        website = program.get("website")
        if website and not access_method:
            parts.append(f"Visit {website} for more information.")

        if not parts:
            parts.append("Contact your local VA facility to learn about telehealth options available in your area.")

        return " ".join(parts)

    def _build_tags(self, program: dict[str, Any]) -> list[str]:
        """Build tags list."""
        # Start with program-specified tags
        tags = list(program.get("tags", []))

        # Ensure core tags are present
        core_tags = ["telehealth", "rural"]
        for tag in core_tags:
            if tag not in tags:
                tags.insert(0, tag)

        # Add organization-based tags
        org_name = program.get("org_name", "").lower()
        if "veterans affairs" in org_name or "va " in org_name:
            if "va" not in tags:
                tags.append("va")
        elif "cohen" in org_name and "cohen-veterans-network" not in tags:
            tags.append("cohen-veterans-network")

        # Add scope-based tags
        scope = program.get("scope", "national")
        if scope == "state":
            states = program.get("states", [])
            for state in states:
                state_tag = f"state-{state.lower()}"
                if state_tag not in tags:
                    tags.append(state_tag)

        # Add mental health tag if applicable
        categories = program.get("categories", [])
        if "mentalHealth" in categories and "mental-health" not in tags:
            tags.append("mental-health")

        # Check eligibility for VA enrollment tag
        eligibility = program.get("eligibility", {})
        if eligibility.get("va_enrollment_required") is False and "no-va-enrollment" not in tags:
            tags.append("no-va-enrollment")

        return list(dict.fromkeys(tags))  # Remove duplicates while preserving order

    def close(self) -> None:
        """Close any resources (no-op for file-based connector)."""
        pass

    def __enter__(self) -> "RuralTelehealthConnector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
