"""Tunnel to Towers Foundation Veterans Villages connector.

Tunnel to Towers Foundation provides permanent affordable housing communities for
homeless veterans through its Veterans Villages program. The foundation renovates
hotels and builds new facilities to provide stable housing with wraparound services.

Source: https://t2t.org/homeless-veteran-program/
National Contact: (718) 987-1931

The Veterans Villages program launched in 2023 and partners with organizations like
U.S.VETS to provide on-site supportive services including mental health care,
case management, and job readiness programs.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


# Operational Veterans Villages locations
T2T_VILLAGES = [
    {
        "id": "t2t-houston",
        "name": "Houston Veterans Village",
        "city": "Houston",
        "state": "TX",
        "address": "18818 Tomball Parkway",
        "zip_code": "77070",
        "phone": "(347) 868-6561",
        "hours": "24 hours, 7 days a week",
        "opened": "November 2023",
        "description": "Renovated 161-room former Holiday Inn providing permanent and transitional housing. Phase II added 14 Comfort Homes for senior veterans.",
        "capacity": {"total_units": 161, "comfort_homes": 14},
        "housing_types": ["permanent-supportive-housing", "transitional-housing"],
        "partner_org": "U.S.VETS",
    },
    {
        "id": "t2t-march-riverside",
        "name": "March Veterans Village",
        "city": "Riverside",
        "state": "CA",
        "address": "15305 6th Street",
        "zip_code": "92518",
        "phone": "(951) 867-9691",
        "hours": "8:00 AM - 5:00 PM",
        "opened": "2018",
        "description": "138-unit LEED Gold supportive housing on March Air Reserve Base. Phase II (2021) added 60 veteran homes. Supports over 400 veterans and families.",
        "capacity": {"phase_1_units": 138, "phase_2_units": 60},
        "housing_types": ["emergency-shelter", "transitional-housing", "permanent-supportive-housing"],
        "partner_org": "U.S.VETS",
        "facility_notes": "Located on March Air Reserve Base",
    },
    {
        "id": "t2t-west-la",
        "name": "West Los Angeles Veterans Village",
        "city": "Los Angeles",
        "state": "CA",
        "address": "11301 Wilshire Boulevard",
        "zip_code": "90073",
        "phone": "(310) 268-3240",
        "hours": "Monday - Friday: 8:00 AM - 5:00 PM",
        "opened": "February 2023",
        "description": "Building 207 on VA West LA Campus housing 67 veterans. Part of 388-acre campus planned to house 3,000+ veterans.",
        "capacity": {"building_207_veterans": 67, "campus_planned_units": 1700},
        "housing_types": ["permanent-supportive-housing"],
        "partner_org": "U.S.VETS",
        "facility_notes": "Located on VA West Los Angeles Healthcare Campus",
    },
    {
        "id": "t2t-phoenix",
        "name": "Phoenix Veterans Village",
        "city": "Phoenix",
        "state": "AZ",
        "address": "3507 North Central Avenue",
        "zip_code": "85012",
        "phone": "(602) 717-6682",
        "hours": "24 hours, 7 days a week",
        "description": "Renovated 150-room hotel providing permanent supportive housing. Serves over 300 veterans daily.",
        "capacity": {"total_units": 150},
        "housing_types": ["emergency-shelter", "transitional-housing", "permanent-supportive-housing"],
        "partner_org": "U.S.VETS",
    },
    {
        "id": "t2t-atlanta-mableton",
        "name": "Atlanta Veterans Village",
        "city": "Mableton",
        "state": "GA",
        "address": "65 S. Service Road",
        "zip_code": "30126",
        "phone": "(718) 987-1931",
        "hours": "24 hours, 7 days a week",
        "opened": "August 2025",
        "description": "First T2T project in Georgia. Converted Wingate hotel with 88 units. Features gym, business center, cafeteria.",
        "capacity": {"total_units": 88},
        "housing_types": ["permanent-supportive-housing"],
        "amenities": ["Gym", "Business center", "Great room", "Cafeteria"],
    },
]


class T2TVeteransVillagesConnector(BaseConnector):
    """Connector for Tunnel to Towers Foundation Veterans Villages.

    Loads location data for operational Veterans Villages providing permanent
    affordable housing for homeless veterans across the United States.

    Each village provides:
    - Permanent and/or transitional housing
    - On-site supportive services (often via U.S.VETS partnership)
    - Mental health care and case management
    - Job readiness and career programs
    - Community amenities
    """

    DEFAULT_DATA_PATH = "data/reference/t2t_veterans_villages.json"

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
            name="Tunnel to Towers Veterans Villages",
            url="https://t2t.org/homeless-veteran-program/",
            tier=2,  # Established nonprofit
            frequency="monthly",
            terms_url="https://t2t.org/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse Veterans Villages data from JSON file or fallback to embedded data.

        Returns:
            List of normalized ResourceCandidate objects, one per village.
        """
        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        # Try to load from file first, fall back to embedded data
        locations = self._load_locations()

        for location in locations:
            # Only include operational villages
            if location.get("status") == "planned":
                continue
            candidate = self._parse_location(location, now)
            resources.append(candidate)

        return resources

    def _load_locations(self) -> list[dict]:
        """Load locations from JSON file or fall back to embedded data.

        Returns:
            List of location dictionaries.
        """
        if self.data_path.exists():
            try:
                with open(self.data_path) as f:
                    data = json.load(f)
                return data.get("locations", [])
            except (json.JSONDecodeError, OSError):
                pass
        # Fall back to embedded data
        return T2T_VILLAGES

    def _parse_location(
        self,
        location: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a location record into a ResourceCandidate.

        Args:
            location: Location data dictionary.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this location.
        """
        name = location.get("name", "Veterans Village")
        city = location.get("city", "")
        state = location.get("state", "")

        # Build title
        title = f"Tunnel to Towers {name} - Veteran Housing"

        # Build description
        description = self._build_description(location)

        # Build eligibility
        eligibility = self._build_eligibility(location)

        # Build how to apply
        how_to_apply = self._build_how_to_apply(location)

        # Build tags
        tags = self._build_tags(location)

        # Build source URL
        source_url = f"https://t2t.org/homeless-veteran-program/"

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name="Tunnel to Towers Foundation",
            org_website="https://t2t.org/",
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
            scope="local",
            states=[state] if state else None,
            raw_data=location,
            fetched_at=fetched_at,
        )

    def _build_description(self, location: dict) -> str:
        """Build resource description.

        Args:
            location: Location data dictionary.

        Returns:
            Formatted description string.
        """
        parts = []

        # Add location-specific description
        if location.get("description"):
            parts.append(location["description"])

        # Add services summary if available
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
                "transitional-housing": "transitional housing",
                "permanent-supportive-housing": "permanent supportive housing",
            }
            types_str = ", ".join(type_labels.get(t, t) for t in housing_types)
            parts.append(f"Housing options: {types_str}.")

        # Add capacity info
        capacity = location.get("capacity", {})
        if capacity:
            if "total_units" in capacity:
                parts.append(f"Capacity: {capacity['total_units']} units.")
            elif "veterans_served" in capacity:
                parts.append(f"Serves {capacity['veterans_served']} veterans.")

        # Add partner organization
        partner = location.get("partner_org")
        if partner:
            parts.append(f"On-site supportive services provided by {partner}.")

        # Add facility notes
        facility_notes = location.get("facility_notes")
        if facility_notes:
            parts.append(facility_notes)

        # Standard T2T info
        parts.append(
            "Tunnel to Towers Foundation Veterans Villages provide permanent affordable "
            "housing for homeless veterans with comprehensive wraparound services."
        )

        return " ".join(parts)

    def _build_eligibility(self, location: dict) -> str:
        """Build eligibility description.

        Args:
            location: Location data dictionary.

        Returns:
            Eligibility requirements string.
        """
        parts = [
            "Veterans experiencing homelessness or at risk of homelessness.",
            "Tunnel to Towers Veterans Villages provide long-term housing solutions.",
        ]

        # Check for partner organization specifics
        partner = location.get("partner_org")
        if partner == "U.S.VETS":
            parts.append(
                "U.S.VETS follows a Housing First model with low-barrier access. "
                "No minimum discharge requirement."
            )

        # Housing type-specific eligibility
        housing_types = location.get("housing_types", [])
        if "permanent-supportive-housing" in housing_types:
            parts.append("Veterans can stay as long as they need stable housing.")

        return " ".join(parts)

    def _build_how_to_apply(self, location: dict) -> str:
        """Build application instructions.

        Args:
            location: Location data dictionary.

        Returns:
            How to apply string.
        """
        phone = location.get("phone", "")
        city = location.get("city", "")
        partner = location.get("partner_org")

        parts = []

        if phone:
            parts.append(f"Contact the {city} Veterans Village at {phone}.")

        if partner == "U.S.VETS":
            parts.append(
                "You can also call the U.S.VETS national hotline at (877) 548-7838 "
                "(1-877-5-4USVETS) 24 hours a day, 7 days a week."
            )
        else:
            parts.append(
                "Contact Tunnel to Towers Foundation at (718) 987-1931 or visit "
                "t2t.org/homeless-veteran-program/ for assistance."
            )

        # Check for 24-hour access
        hours = location.get("hours", "")
        if "24 hours" in hours.lower() or "24/7" in hours:
            parts.append("This location offers 24/7 access.")

        return " ".join(parts)

    def _build_tags(self, location: dict) -> list[str]:
        """Build tags list.

        Args:
            location: Location data dictionary.

        Returns:
            List of tag strings.
        """
        tags = [
            "tunnel-to-towers",
            "t2t",
            "veterans-village",
            "homeless-services",
            "affordable-housing",
        ]

        # Add housing type tags
        housing_types = location.get("housing_types", [])
        tags.extend(housing_types)

        # Add partner organization tag
        partner = location.get("partner_org")
        if partner == "U.S.VETS":
            tags.append("us-vets")
            tags.append("housing-first")

        # Add amenity tags
        amenities = location.get("amenities", [])
        if amenities:
            tags.append("full-amenities")

        # Add state tag
        state = location.get("state", "")
        if state:
            tags.append(f"state-{state.lower()}")

        # Add location ID
        location_id = location.get("id", "")
        if location_id:
            tags.append(location_id)

        return tags
