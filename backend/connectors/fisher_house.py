"""Fisher House Foundation connector.

Imports Fisher House locations that provide free temporary housing for military
and Veteran families during a medical crisis.

Source: https://www.fisherhouse.org/

Fisher House Foundation builds comfort homes where military and Veteran families
can stay free of charge while a loved one is receiving medical treatment at a
nearby VA medical center or military hospital. There are over 100 Fisher Houses
located across the United States, Germany, and the United Kingdom.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class FisherHouseConnector(BaseConnector):
    """Connector for Fisher House Foundation locations.

    Fisher Houses provide:
    - Free temporary lodging for families of Veterans receiving treatment
    - Home-like environment with private bedrooms, shared kitchen/dining
    - Located near VA medical centers and military hospitals
    - No length-of-stay limits based on treatment needs
    - Support services and connections to other resources

    Each Fisher House typically accommodates 8-21 families at once.
    """

    # Path to reference data file
    DATA_FILE = Path(__file__).parent.parent / "data" / "reference" / "fisher_house_locations.json"

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Fisher House Foundation",
            url="https://www.fisherhouse.org/",
            tier=2,  # Established nonprofit organization
            frequency="monthly",
            terms_url="https://www.fisherhouse.org/terms-of-use/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Load Fisher House locations from reference file.

        Returns:
            List of ResourceCandidate objects for each Fisher House location.
        """
        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        # Load reference data
        data = self._load_data()
        if not data:
            return resources

        locations = data.get("locations", [])

        for location in locations:
            candidate = self._parse_location(location, now)
            if candidate:
                resources.append(candidate)

        return resources

    def _load_data(self) -> dict[str, Any]:
        """Load Fisher House data from JSON file.

        Returns:
            Parsed JSON data or empty dict on error.
        """
        try:
            with open(self.DATA_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Log error but don't crash - return empty list
            print(f"Error loading Fisher House data: {e}")  # noqa: T201
            return {}

    def _parse_location(
        self,
        location: dict[str, Any],
        fetched_at: datetime,
    ) -> ResourceCandidate | None:
        """Parse a location entry into a ResourceCandidate.

        Args:
            location: Dictionary with location data
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate or None if data is invalid.
        """
        location_id = location.get("id", "")
        name = location.get("name", "")

        if not name:
            return None

        # Extract location data
        address = location.get("address", "")
        city = location.get("city", "")
        state = location.get("state")  # May be None for international locations
        zip_code = location.get("zip", "")
        country = location.get("country", "US")

        # Contact info
        phone = self._normalize_phone(location.get("phone"))
        email = location.get("email")
        manager = location.get("manager")

        # Facility info
        facility_name = location.get("facility_name", name)
        facility_type = location.get("facility_type", "va")
        houses_count = location.get("houses_count", 1)
        slug = location.get("slug", "")

        # Build title
        title = self._build_title(name, city, state)

        # Build description
        description = self._build_description(
            name=name,
            facility_name=facility_name,
            facility_type=facility_type,
            houses_count=houses_count,
            city=city,
            state=state,
        )

        # Build source URL - unique per location
        if slug:
            source_url = f"https://www.fisherhouse.org/programs/houses/current-houses/{slug}/"
        else:
            source_url = f"https://www.fisherhouse.org/programs/houses/?id={location_id}"

        # Determine scope based on location
        if country and country != "US":
            scope = "international"
            states = None
        elif state:
            scope = "local"
            states = [state]
        else:
            scope = "local"
            states = None

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name="Fisher House Foundation",
            org_website="https://www.fisherhouse.org/",
            address=address if address else None,
            city=city if city else None,
            state=self._normalize_state(state) if state else None,
            zip_code=zip_code if zip_code else None,
            categories=["family", "housing"],
            tags=self._build_tags(facility_type, houses_count),
            phone=phone,
            email=email,
            hours="Available 24/7 during family member's medical treatment",
            eligibility=self._build_eligibility(facility_type),
            how_to_apply=self._build_how_to_apply(name, phone, email, manager, facility_type),
            scope=scope,
            states=states,
            raw_data={
                "id": location_id,
                "facility_name": facility_name,
                "facility_type": facility_type,
                "houses_count": houses_count,
                "manager": manager,
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "country": country,
            },
            fetched_at=fetched_at,
        )

    def _build_title(self, name: str, city: str | None, state: str | None) -> str:
        """Build resource title.

        Args:
            name: Fisher House location name
            city: City name
            state: State abbreviation

        Returns:
            Formatted title string.
        """
        # Most Fisher House names already include location context
        if city and state and city not in name and state not in name:
            return f"Fisher House at {name} - {city}, {state}"
        elif state and state not in name:
            return f"Fisher House at {name} ({state})"
        return f"Fisher House at {name}"

    def _build_description(
        self,
        name: str,
        facility_name: str,
        facility_type: str,
        houses_count: int,
        city: str | None,
        state: str | None,
    ) -> str:
        """Build resource description.

        Args:
            name: Fisher House location name
            facility_name: Medical facility name
            facility_type: Type of facility (va, military, international)
            houses_count: Number of houses at this location
            city: City name
            state: State code

        Returns:
            Formatted description string.
        """
        parts = []

        house_word = "house" if houses_count == 1 else "houses"
        parts.append(
            f"Fisher House at {facility_name} provides free temporary lodging for "
            f"military and Veteran families while a loved one receives medical treatment. "
            f"This location has {houses_count} {house_word} available."
        )

        # Location info
        if city and state:
            parts.append(f"Located in {city}, {state}.")

        # Standard Fisher House info
        parts.append(
            "Fisher Houses are comfortable home-like environments with private bedrooms, "
            "shared kitchens and living spaces, and laundry facilities. "
            "Families can stay as long as their Veteran is receiving treatment."
        )

        parts.append(
            "There is no charge to stay at a Fisher House. "
            "The program has saved families over $500 million in lodging costs since 1990."
        )

        return " ".join(parts)

    def _build_eligibility(self, facility_type: str) -> str:
        """Build eligibility description.

        Args:
            facility_type: Type of facility (va, military, international)

        Returns:
            Eligibility requirements string.
        """
        if facility_type == "military":
            return (
                "Family members (spouse, parent, child, sibling, or other close relative) "
                "of active-duty service members, reservists, or National Guard members "
                "who are receiving treatment at the associated military medical center. "
                "Families of Veterans receiving treatment may also be eligible depending on space."
            )
        elif facility_type == "international":
            return (
                "Family members of military personnel or Veterans receiving treatment "
                "at the associated medical facility. Contact the Fisher House manager "
                "for specific eligibility requirements at this international location."
            )
        else:  # VA
            return (
                "Family members (spouse, parent, child, sibling, or other close relative) "
                "of Veterans receiving treatment at the associated VA medical center. "
                "The Veteran must be an inpatient or receiving ongoing outpatient treatment. "
                "Priority is given to families traveling long distances or facing extended treatments. "
                "No income requirements."
            )

    def _build_how_to_apply(
        self,
        name: str,
        phone: str | None,
        email: str | None,
        manager: str | None,
        facility_type: str,
    ) -> str:
        """Build application instructions.

        Args:
            name: Fisher House name
            phone: Phone number if available
            email: Email address if available
            manager: Manager name if available
            facility_type: Type of facility

        Returns:
            How to apply string.
        """
        parts = []

        # Contact method
        contact_info = []
        if phone:
            contact_info.append(f"call {phone}")
        if email:
            contact_info.append(f"email {email}")

        if contact_info:
            contact_str = " or ".join(contact_info)
            if manager:
                parts.append(f"Contact Fisher House Manager {manager}: {contact_str}.")
            else:
                parts.append(f"Contact the Fisher House directly: {contact_str}.")
        else:
            parts.append("Contact the Fisher House at the medical facility.")

        # Referral process
        if facility_type == "va":
            parts.append(
                "You can also ask your Veteran's VA social worker or case manager "
                "for a referral to the Fisher House program."
            )
        else:
            parts.append(
                "You can also ask your service member's medical team or "
                "Patient Administration office for a Fisher House referral."
            )

        parts.append(
            "Reservations are based on availability. "
            "Call ahead when possible, especially for planned treatments. "
            "There is no application or income verification required."
        )

        return " ".join(parts)

    def _build_tags(self, facility_type: str, houses_count: int) -> list[str]:
        """Build tags list.

        Args:
            facility_type: Type of facility
            houses_count: Number of houses at location

        Returns:
            List of tag strings.
        """
        tags = [
            "fisher-house",
            "family-housing",
            "free-lodging",
            "medical-travel",
            "caregiver-support",
        ]

        # Facility type tags
        if facility_type == "military":
            tags.extend(["military-medical-center", "active-duty-families"])
        elif facility_type == "va":
            tags.extend(["va-medical-center", "veteran-families"])
        elif facility_type == "international":
            tags.append("international")

        # Size indicator
        if houses_count >= 4:
            tags.append("large-facility")
        elif houses_count >= 2:
            tags.append("multiple-houses")

        return tags
