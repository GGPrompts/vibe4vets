"""Final Salute Inc. women veterans housing connector.

Final Salute Inc. provides homeless women veterans and their children with safe
and suitable housing. Founded in 2010, FSI has served over 5,000 women veterans
through:
- H.O.M.E. Program: Transitional housing with mentorship
- S.A.F.E. Program: Emergency financial assistance
- Next Uniform: Employment transition support

Source: https://www.finalsaluteinc.org/
National Hotline: (866) 472-5883
Main Office: (703) 224-8843
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class FinalSaluteConnector(BaseConnector):
    """Connector for Final Salute Inc. women veterans housing.

    Loads location and program data from a curated JSON file.
    Final Salute serves women veterans nationwide with a primary focus
    on the DC/Northern Virginia/Southern Maryland region.

    Programs include:
    - H.O.M.E. (Housing, Outreach, Mentorship, Encouragement): Transitional housing
    - S.A.F.E.: Emergency financial assistance
    - Next Uniform: Employment transition support
    """

    DEFAULT_DATA_PATH = "data/reference/final_salute_locations.json"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to JSON file. Falls back to DEFAULT_DATA_PATH.
        """
        if data_path is None:
            # Find project root (directory containing 'data' folder)
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
            name="Final Salute Inc. Women Veterans Housing",
            url="https://www.finalsaluteinc.org/",
            tier=2,  # Established nonprofit
            frequency="monthly",
            terms_url="https://www.finalsaluteinc.org/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse Final Salute data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Final Salute data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)
        national_phone = data.get("national_phone", "(866) 472-5883")
        programs = data.get("programs", [])
        eligibility_data = data.get("eligibility", {})

        for location in data.get("locations", []):
            candidate = self._parse_location(location, national_phone, programs, eligibility_data, now)
            resources.append(candidate)

        return resources

    def _parse_location(
        self,
        location: dict,
        national_phone: str,
        programs: list[dict],
        eligibility_data: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a location record into a ResourceCandidate.

        Args:
            location: Location data dictionary.
            national_phone: National hotline number.
            programs: List of program data.
            eligibility_data: Eligibility requirements.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this location.
        """
        name = location.get("name", "Final Salute Inc.")
        city = location.get("city", "")
        state = location.get("state", "")

        # Build title
        title = f"{name} - Women Veterans Housing"

        # Build description
        description = self._build_description(location, programs, national_phone)

        # Build eligibility
        eligibility = self._build_eligibility(eligibility_data)

        # Build how to apply
        how_to_apply = self._build_how_to_apply(location, national_phone)

        # Determine scope - national reach with local headquarters
        scope = "national"

        # Build tags
        tags = self._build_tags(location)

        # Coverage states
        coverage = location.get("coverage", {})
        states_list = None
        if coverage.get("national_reach"):
            # Organization serves nationally
            states_list = None
        elif state:
            states_list = [state]

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://www.finalsaluteinc.org/",
            org_name="Final Salute Inc.",
            org_website="https://www.finalsaluteinc.org/",
            address=location.get("address"),
            city=city,
            state=state,
            zip_code=location.get("zip_code"),
            categories=["housing"],
            tags=tags,
            phone=self._normalize_phone(location.get("phone")),
            email=location.get("email"),
            hours=location.get("hours"),
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope=scope,
            states=states_list,
            raw_data=location,
            fetched_at=fetched_at,
        )

    def _build_description(self, location: dict, programs: list[dict], national_phone: str) -> str:
        """Build resource description.

        Args:
            location: Location data dictionary.
            programs: List of program data.
            national_phone: National hotline number.

        Returns:
            Formatted description string.
        """
        parts = [
            "Final Salute Inc. provides homeless women veterans and their children "
            "with safe and suitable housing. Founded in 2010, this nonprofit serves "
            "women veterans nationwide."
        ]

        # Add program highlights
        program_names = [p.get("name", "") for p in programs if p.get("name")]
        if program_names:
            parts.append(f"Programs include: {', '.join(program_names)}.")

        # Add services from location
        services = location.get("services", [])
        if services:
            service_list = ", ".join(services[:4])
            if len(services) > 4:
                service_list += f", and {len(services) - 4} more services"
            parts.append(f"Services: {service_list}.")

        # Add coverage info
        coverage = location.get("coverage", {})
        if coverage.get("primary_region"):
            parts.append(f"Primary service area: {coverage['primary_region']}.")
        if coverage.get("national_reach"):
            parts.append("Programs available nationwide to women veterans regardless of location.")

        # Add national hotline
        parts.append(f"National hotline: {national_phone}.")

        return " ".join(parts)

    def _build_eligibility(self, eligibility_data: dict) -> str:
        """Build eligibility description.

        Args:
            eligibility_data: Eligibility requirements dictionary.

        Returns:
            Eligibility requirements string.
        """
        parts = []

        # Gender requirement
        gender = eligibility_data.get("gender", "Women veterans only")
        parts.append(gender + ".")

        # Housing status
        housing_status = eligibility_data.get("housing_status", [])
        if housing_status:
            status_str = ", ".join(housing_status).lower()
            parts.append(f"Must be {status_str}.")

        # Children
        if eligibility_data.get("children_accepted"):
            parts.append("Children are welcome and can be housed with their veteran parent.")

        # Additional notes
        notes = eligibility_data.get("notes")
        if notes:
            parts.append(notes)

        return " ".join(parts)

    def _build_how_to_apply(self, location: dict, national_phone: str) -> str:
        """Build application instructions.

        Args:
            location: Location data dictionary.
            national_phone: National hotline number.

        Returns:
            How to apply string.
        """
        parts = []

        phone = location.get("phone", "")
        if phone:
            parts.append(f"Call the main office at {phone}.")

        parts.append(f"You can also call the national hotline at {national_phone}.")

        hours = location.get("hours", "")
        if hours:
            parts.append(f"Office hours: {hours}.")

        parts.append(
            "Visit finalsaluteinc.org for online application and additional resources. "
            "Women veterans in crisis can reach out regardless of their location."
        )

        return " ".join(parts)

    def _build_tags(self, location: dict) -> list[str]:
        """Build tags list.

        Args:
            location: Location data dictionary.

        Returns:
            List of tag strings.
        """
        tags = [
            "final-salute",
            "women-veterans",
            "transitional",
            "families-with-children",
            "homeless-services",
            "mst-support",
            "single-mothers",
        ]

        # Add location type tag
        location_type = location.get("type", "")
        if location_type:
            tags.append(location_type)

        # Check coverage
        coverage = location.get("coverage", {})
        if coverage.get("national_reach"):
            tags.append("national-program")

        # Add location-specific tags
        location_id = location.get("id", "")
        if location_id:
            tags.append(location_id)

        # Add service-based tags
        services = location.get("services", [])
        service_lower = [s.lower() for s in services]

        if any("employment" in s or "career" in s for s in service_lower):
            tags.append("employment-services")
        if any("financial" in s for s in service_lower):
            tags.append("financial-assistance")

        return tags
