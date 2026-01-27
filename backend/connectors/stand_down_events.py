"""Stand Down Events connector for veteran outreach events.

Stand Down events are multi-day outreach initiatives providing health screenings,
job training, housing assistance, and other services to homeless and at-risk
veterans in one location.

Source: VA Stand Down Events (https://www.va.gov/homeless/events.asp)
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Map of state abbreviations to full names
STATE_NAMES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

# Map service tags to human-readable labels and categories
SERVICE_LABELS = {
    "health-screening": "Health Screening",
    "dental": "Dental Care",
    "housing": "Housing Assistance",
    "employment": "Employment Services",
    "legal": "Legal Aid",
    "benefits": "VA Benefits Counseling",
    "clothing": "Clothing",
    "food": "Food Services",
    "mental-health": "Mental Health Services",
    "substance-use": "Substance Use Treatment",
}

# Map services to resource categories
SERVICE_TO_CATEGORY = {
    "housing": "housing",
    "employment": "employment",
    "legal": "legal",
}


class StandDownEventsConnector(BaseConnector):
    """Connector for VA Stand Down outreach events.

    Stand Downs are typically one to three day events providing:
    - Food, clothing, and health screenings
    - Referrals for healthcare, housing, and employment
    - Mental health and substance use counseling
    - Benefits assistance and legal aid

    Events are tracked from VA.gov and community partners.
    """

    DATA_PATH = "data/reference/stand_down_events.json"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to the events JSON file. Defaults to DATA_PATH.
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
            name="VA Stand Down Events",
            url="https://www.va.gov/homeless/events.asp",
            tier=1,  # Official VA program events
            frequency="monthly",  # Events updated regularly
            terms_url="https://www.va.gov/homeless/events.asp",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse Stand Down events data.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        now = datetime.now(UTC)

        data = self._load_data()
        if not data:
            return []

        resources: list[ResourceCandidate] = []
        for event in data.get("events", []):
            candidate = self._parse_event(event, fetched_at=now)
            if candidate:
                resources.append(candidate)

        return resources

    def _load_data(self) -> dict:
        """Load events data from JSON file."""
        if not self.data_path.exists():
            return {}

        with open(self.data_path) as f:
            return json.load(f)

    def _parse_event(
        self,
        event: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate | None:
        """Parse an event entry into a ResourceCandidate.

        Args:
            event: Event data dictionary.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this event, or None if invalid.
        """
        name = event.get("name")
        start_date = event.get("start_date")
        if not name or not start_date:
            return None

        end_date = event.get("end_date", start_date)
        city = event.get("city")
        state = event.get("state")
        services = event.get("services", [])

        title = self._build_title(name, start_date, end_date, city, state)
        description = self._build_description(event)
        categories = self._get_categories(services)
        tags = self._build_tags(services, state)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=event.get("source_url", "https://www.va.gov/homeless/events.asp"),
            org_name=event.get("organizer_name", "VA Stand Down Program"),
            org_website="https://www.va.gov/homeless/events.asp",
            address=event.get("address"),
            city=city,
            state=state,
            zip_code=event.get("zip_code"),
            categories=categories,
            tags=tags,
            phone=self._normalize_phone(event.get("organizer_phone")),
            email=event.get("organizer_email"),
            eligibility=self._build_eligibility(),
            how_to_apply=self._build_how_to_apply(event),
            scope="local",
            states=[state] if state else None,
            raw_data=event,
            fetched_at=fetched_at,
        )

    def _build_title(
        self,
        name: str,
        start_date: str,
        end_date: str,
        city: str | None,
        state: str | None,
    ) -> str:
        """Build resource title with event name and dates.

        Args:
            name: Event name.
            start_date: Start date (YYYY-MM-DD).
            end_date: End date (YYYY-MM-DD).
            city: City name.
            state: State code.

        Returns:
            Formatted title string.
        """
        date_str = self._format_date_range(start_date, end_date)
        location_parts = []
        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        location = ", ".join(location_parts)

        if location:
            return f"{name} - {date_str} ({location})"
        return f"{name} - {date_str}"

    def _format_date_range(self, start_date: str, end_date: str) -> str:
        """Format a date range for display.

        Args:
            start_date: Start date (YYYY-MM-DD).
            end_date: End date (YYYY-MM-DD).

        Returns:
            Formatted date range string.
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            if start_date == end_date:
                return start.strftime("%B %d, %Y")

            if start.year == end.year and start.month == end.month:
                return f"{start.strftime('%B %d')}-{end.strftime('%d, %Y')}"
            elif start.year == end.year:
                return f"{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}"
            else:
                return f"{start.strftime('%B %d, %Y')} - {end.strftime('%B %d, %Y')}"
        except ValueError:
            return f"{start_date} - {end_date}"

    def _build_description(self, event: dict) -> str:
        """Build resource description.

        Args:
            event: Event data dictionary.

        Returns:
            Formatted description string.
        """
        parts = []

        # Event dates prominently
        start_date = event.get("start_date", "")
        end_date = event.get("end_date", start_date)
        date_str = self._format_date_range(start_date, end_date)
        city = event.get("city", "")
        state = event.get("state", "")
        state_name = STATE_NAMES.get(state, state)

        if city and state_name:
            parts.append(f"Stand Down event on {date_str} in {city}, {state_name}.")
        elif date_str:
            parts.append(f"Stand Down event on {date_str}.")

        # Custom description if provided
        if event.get("description"):
            parts.append(event["description"])

        # Services offered
        services = event.get("services", [])
        if services:
            service_labels = [SERVICE_LABELS.get(s, s.replace("-", " ").title()) for s in services]
            parts.append(f"Services provided: {', '.join(service_labels)}.")

        # Address
        address = event.get("address")
        if address:
            location_parts = [address]
            if city:
                location_parts.append(city)
            if state:
                location_parts.append(state)
            zip_code = event.get("zip_code")
            if zip_code:
                location_parts.append(zip_code)
            parts.append(f"Location: {', '.join(location_parts)}.")

        # General Stand Down info
        parts.append(
            "Stand Downs are one to three day events providing food, clothing, health screenings, "
            "and referrals for healthcare, housing, employment, and other essential services to "
            "homeless and at-risk veterans."
        )

        return " ".join(parts)

    def _get_categories(self, services: list[str]) -> list[str]:
        """Get resource categories based on services offered.

        Args:
            services: List of service tags.

        Returns:
            List of category strings.
        """
        categories = set()

        for service in services:
            if service in SERVICE_TO_CATEGORY:
                categories.add(SERVICE_TO_CATEGORY[service])

        # Always include housing since Stand Downs primarily serve homeless veterans
        categories.add("housing")

        return sorted(categories)

    def _build_tags(self, services: list[str], state: str | None) -> list[str]:
        """Build tags list.

        Args:
            services: List of service tags.
            state: State code.

        Returns:
            List of tags.
        """
        tags = [
            "stand-down",
            "outreach-event",
            "homeless-services",
            "veteran-event",
        ]

        # Add service tags
        for service in services:
            if service not in tags:
                tags.append(service)

        # Add state tag
        if state:
            tags.append(f"state-{state.lower()}")

        return tags

    def _build_eligibility(self) -> str:
        """Build eligibility text.

        Returns:
            Eligibility description string.
        """
        return (
            "All veterans are welcome at Stand Down events regardless of discharge status. "
            "These events are designed to serve homeless veterans and veterans at risk of "
            "homelessness, but any veteran can attend and access services. Family members "
            "of veterans may also be eligible for some services."
        )

    def _build_how_to_apply(self, event: dict) -> str:
        """Build how to apply instructions.

        Args:
            event: Event data dictionary.

        Returns:
            Instructions string.
        """
        parts = []

        # Event-specific date and location
        start_date = event.get("start_date", "")
        end_date = event.get("end_date", start_date)
        date_str = self._format_date_range(start_date, end_date)
        address = event.get("address")
        city = event.get("city")
        state = event.get("state")

        parts.append(f"Attend the event on {date_str}.")
        if address:
            location_parts = [address]
            if city:
                location_parts.append(city)
            if state:
                location_parts.append(state)
            parts.append(f"Location: {', '.join(location_parts)}.")

        # Contact info
        phone = event.get("organizer_phone")
        organizer = event.get("organizer_name")
        if phone:
            if organizer:
                parts.append(f"For more information, contact {organizer} at {phone}.")
            else:
                parts.append(f"For more information, call {phone}.")
        elif organizer:
            parts.append(f"Contact {organizer} for more information.")

        parts.append("No appointment or registration required for most Stand Down events - just show up!")
        parts.append("Bring your DD-214 if available, but it is not required to receive services.")

        return " ".join(parts)
