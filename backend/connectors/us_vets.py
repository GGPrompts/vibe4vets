"""U.S.VETS (United States Veterans Initiative) homeless veteran housing connector.

U.S.VETS is the nation's largest nonprofit provider of comprehensive services
to homeless and at-risk veterans, following a Housing First model with:
- Emergency shelter (low-barrier, 24/7 access)
- Transitional housing (stepping stone to permanent housing)
- Permanent supportive housing (long-term stability)

Source: https://usvets.org/
National Hotline: (877) 548-7838 (1-877-5-4USVETS)
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class USVetsConnector(BaseConnector):
    """Connector for U.S.VETS homeless veteran housing locations.

    Loads location data from a curated JSON file containing 10 U.S.VETS sites
    across California, Arizona, Nevada, Texas, DC, and Hawaii.

    Each site provides comprehensive services including:
    - Emergency, transitional, and permanent housing
    - Mental health and substance use treatment
    - Career development and job placement
    - Case management and wraparound services
    """

    DEFAULT_DATA_PATH = "data/reference/us_vets_locations.json"

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
            name="U.S.VETS Housing Locations",
            url="https://usvets.org/",
            tier=2,  # Established nonprofit
            frequency="monthly",
            terms_url="https://usvets.org/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse U.S.VETS location data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects, one per location.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"U.S.VETS data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)
        national_phone = data.get("national_phone", "(877) 548-7838")

        for location in data.get("locations", []):
            candidate = self._parse_location(location, national_phone, now)
            resources.append(candidate)

        return resources

    def _parse_location(
        self,
        location: dict,
        national_phone: str,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a location record into a ResourceCandidate.

        Args:
            location: Location data dictionary.
            national_phone: National hotline number.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this location.
        """
        name = location.get("name", "U.S.VETS")
        city = location.get("city", "")
        state = location.get("state", "")

        # Build title
        title = f"{name} - Veteran Housing"

        # Build description
        description = self._build_description(location, national_phone)

        # Build eligibility
        eligibility = self._build_eligibility(location)

        # Build how to apply
        how_to_apply = self._build_how_to_apply(location, national_phone)

        # Determine scope
        scope = "local"

        # Build tags
        tags = self._build_tags(location)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=f"https://usvets.org/locations/{city.lower().replace(' ', '-').replace("'", '')}/",
            org_name="U.S.VETS (United States Veterans Initiative)",
            org_website="https://usvets.org/",
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
            states=[state] if state else None,
            raw_data=location,
            fetched_at=fetched_at,
        )

    def _build_description(self, location: dict, national_phone: str) -> str:
        """Build resource description.

        Args:
            location: Location data dictionary.
            national_phone: National hotline number.

        Returns:
            Formatted description string.
        """
        parts = []

        # Add location-specific description
        if location.get("description"):
            parts.append(location["description"])

        # Add services summary
        services = location.get("services", [])
        if services:
            service_list = ", ".join(services[:5])
            if len(services) > 5:
                service_list += f", and {len(services) - 5} more services"
            parts.append(f"Services include: {service_list}.")

        # Add housing types
        housing_types = location.get("housing_types", [])
        if housing_types:
            type_labels = {
                "emergency-shelter": "emergency shelter",
                "bridge-housing": "bridge housing",
                "transitional-housing": "transitional housing",
                "permanent-supportive-housing": "permanent supportive housing",
            }
            types_str = ", ".join(type_labels.get(t, t) for t in housing_types)
            parts.append(f"Housing options: {types_str}.")

        # Add capacity info if available
        capacity = location.get("capacity", {})
        if capacity:
            if isinstance(capacity, dict):
                if "total_beds" in capacity:
                    parts.append(f"Capacity: {capacity['total_beds']} beds.")
                elif "veterans_village" in capacity:
                    parts.append(f"Capacity: {capacity['veterans_village']} veterans at Veterans Village.")

        # Add national hotline
        parts.append(f"National hotline: {national_phone} (24/7).")

        return " ".join(parts)

    def _build_eligibility(self, location: dict) -> str:
        """Build eligibility description.

        Args:
            location: Location data dictionary.

        Returns:
            Eligibility requirements string.
        """
        eligibility_info = location.get("eligibility", {})

        parts = [
            "Veterans experiencing homelessness or at risk of homelessness.",
            "U.S.VETS follows a Housing First model with low-barrier access.",
        ]

        # Check for special eligibility notes
        if isinstance(eligibility_info, dict):
            if eligibility_info.get("serves_families"):
                parts.append("Services available for veterans and their families.")
            if eligibility_info.get("minimum_discharge") == "None":
                parts.append("No minimum discharge requirement.")
            if not eligibility_info.get("disability_required", True):
                parts.append("No disability requirement.")

        # Check for special programs
        special_programs = location.get("special_programs", [])
        if "women-veterans" in special_programs:
            parts.append("Special programs available for women veterans.")
        if "veterans-with-children" in special_programs:
            parts.append("Housing available for veterans with children.")

        return " ".join(parts)

    def _build_how_to_apply(self, location: dict, national_phone: str) -> str:
        """Build application instructions.

        Args:
            location: Location data dictionary.
            national_phone: National hotline number.

        Returns:
            How to apply string.
        """
        phone = location.get("phone", "")
        intake_phone = location.get("intake_phone", "")
        city = location.get("city", "")

        parts = []

        if intake_phone:
            parts.append(f"For intake, call {intake_phone}.")
        elif phone:
            parts.append(f"Contact the {city} site at {phone}.")

        parts.append(
            f"You can also call the national hotline at {national_phone} "
            "(1-877-5-4USVETS) 24 hours a day, 7 days a week for immediate assistance."
        )

        # Check for 24-hour access
        hours = location.get("hours", "")
        if "24 hours" in hours.lower():
            parts.append("This location offers 24/7 walk-in access.")

        return " ".join(parts)

    def _build_tags(self, location: dict) -> list[str]:
        """Build tags list.

        Args:
            location: Location data dictionary.

        Returns:
            List of tag strings.
        """
        tags = [
            "us-vets",
            "homeless-services",
            "housing-first",
        ]

        # Add housing type tags
        housing_types = location.get("housing_types", [])
        tags.extend(housing_types)

        # Add special program tags
        special_programs = location.get("special_programs", [])
        for program in special_programs:
            if program == "women-veterans":
                tags.append("women-veterans")
            elif program == "veterans-with-children":
                tags.append("families-with-children")
            elif program == "veterans-in-progress":
                tags.append("work-reentry")

        # Check for specific services
        services = location.get("services", [])
        service_lower = [s.lower() for s in services]

        if any("ssvf" in s or "supportive services for veteran families" in s for s in service_lower):
            tags.append("ssvf")
        if any("mental health" in s for s in service_lower):
            tags.append("mental-health")
        if any("substance" in s or "treatment" in s for s in service_lower):
            tags.append("substance-use-treatment")
        if any("career" in s or "employment" in s or "workforce" in s for s in service_lower):
            tags.append("employment-services")

        # Location-specific tags
        location_id = location.get("id", "")
        if location_id:
            tags.append(location_id)

        return tags
