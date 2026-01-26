"""DOL Apprenticeship Finder API connector.

Fetches state and regional apprenticeship offices from the CareerOneStop API.
These offices connect veterans with registered apprenticeship programs,
many of which are GI Bill-approved for education benefits.

Documentation: https://www.careeronestop.org/Developers/WebAPI/Apprenticeships/list-apprenticeship-offices.aspx
"""

import os
from datetime import UTC, datetime
from typing import Any

import httpx

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class ApprenticeshipConnector(BaseConnector):
    """Connector for CareerOneStop Apprenticeship Finder API.

    This connector fetches state and regional apprenticeship office data from
    the DOL CareerOneStop API. These offices administer registered apprenticeship
    programs and can help veterans find GI Bill-approved apprenticeships.

    Apprenticeship offices are valuable resources because they:
    - Connect job seekers with registered apprenticeship programs
    - Help employers start new apprenticeship programs
    - Provide information on GI Bill eligibility for apprenticeships
    - Offer guidance on the apprenticeship registration process

    Requires CAREERONESTOP_API_KEY environment variable for API access.
    """

    BASE_URL = "https://api.careeronestop.org/v1/apprenticeshipfinder"
    DEFAULT_RADIUS = 500  # Miles - large radius to get all offices in state
    MAX_RESULTS = 100  # Maximum results per request

    # All US states and territories for comprehensive fetching
    US_STATES = [
        "AL",
        "AK",
        "AS",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "DC",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "MP",
        "PR",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "GU",
        "VT",
        "VA",
        "VI",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    def __init__(self, api_key: str | None = None, user_id: str | None = None):
        """Initialize the connector.

        Args:
            api_key: CareerOneStop API key. Falls back to CAREERONESTOP_API_KEY env var.
            user_id: CareerOneStop User ID. Falls back to CAREERONESTOP_USER_ID env var
                     or uses default.
        """
        self.api_key = api_key or os.environ.get("CAREERONESTOP_API_KEY")
        self.user_id = user_id or os.environ.get("CAREERONESTOP_USER_ID", "vibe4vets")
        self._client: httpx.Client | None = None

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="CareerOneStop Apprenticeship Offices",
            url="https://www.careeronestop.org/LocalHelp/EmploymentAndTraining/find-apprenticeship-offices.aspx",
            tier=1,  # Official DOL government source
            frequency="monthly",
            terms_url="https://www.careeronestop.org/Developers/WebAPI/Terms-of-service.aspx",
            requires_auth=True,
        )

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.Client(
                headers=headers,
                timeout=30.0,
            )
        return self._client

    def run(self) -> list[ResourceCandidate]:
        """Fetch all apprenticeship offices from CareerOneStop API.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        resources: list[ResourceCandidate] = []
        seen_ids: set[str] = set()  # Track unique offices to avoid duplicates

        try:
            client = self._get_client()

            # Fetch offices by state to ensure comprehensive coverage
            for state in self.US_STATES:
                state_resources = self._fetch_offices_by_state(client, state, seen_ids)
                resources.extend(state_resources)

            return resources
        finally:
            self.close()

    def _fetch_offices_by_state(self, client: httpx.Client, state: str, seen_ids: set[str]) -> list[ResourceCandidate]:
        """Fetch apprenticeship offices for a specific state.

        Args:
            client: HTTP client
            state: Two-letter state code
            seen_ids: Set of already-seen office IDs to avoid duplicates

        Returns:
            List of ResourceCandidate objects for this state.
        """
        resources: list[ResourceCandidate] = []

        try:
            # CareerOneStop API uses location-based search
            url = f"{self.BASE_URL}/{self.user_id}/{state}/{self.DEFAULT_RADIUS}"

            response = client.get(
                url,
                params={
                    "sortColumns": "Location",
                    "sortOrder": "ASC",
                    "startRecord": 0,
                    "limitRecord": self.MAX_RESULTS,
                    "format": "json",
                },
            )
            response.raise_for_status()
            data = response.json()

            # Extract offices from response
            # API returns ApprenticeshipOfficeList for apprenticeship finder
            offices = data.get("ApprenticeshipOfficeList", [])

            for office in offices:
                # Create unique ID from name and location
                office_id = self._create_office_id(office)
                if office_id in seen_ids:
                    continue
                seen_ids.add(office_id)

                candidate = self._parse_office(office)
                if candidate:
                    resources.append(candidate)

        except httpx.HTTPError as e:
            # Log error but continue with other states
            print(f"Error fetching apprenticeship offices for {state}: {e}")

        return resources

    def _create_office_id(self, office: dict[str, Any]) -> str:
        """Create a unique identifier for an office.

        Args:
            office: Raw office data from API

        Returns:
            Unique string identifier.
        """
        name = office.get("Name", office.get("OfficeName", ""))
        address = office.get("Address", office.get("Address1", ""))
        city = office.get("City", "")
        state = office.get("State", office.get("StateName", ""))
        return f"{name}|{address}|{city}|{state}".lower()

    def _parse_office(self, office: dict[str, Any]) -> ResourceCandidate | None:
        """Parse an office object into a ResourceCandidate.

        Args:
            office: Raw office data from API

        Returns:
            ResourceCandidate or None if parsing fails.
        """
        name = office.get("Name") or office.get("OfficeName")
        if not name:
            return None

        # Build description
        description = self._build_description(office)

        # Extract contact info
        phone = office.get("Phone") or office.get("Telephone")
        email = office.get("Email") or office.get("EmailAddress")

        # Format address
        address = office.get("Address") or office.get("Address1")
        city = office.get("City")
        state = office.get("State") or office.get("StateName")
        zip_code = office.get("Zip") or office.get("ZipCode")

        # Build source URL - prefer office's own URL, fallback to finder
        source_url = office.get("URL") or office.get("Url") or office.get("Website")
        if not source_url:
            source_url = (
                "https://www.careeronestop.org/LocalHelp/EmploymentAndTraining/find-apprenticeship-offices.aspx"
            )

        # Determine office type for tags
        office_type = office.get("OfficeType", office.get("Type", ""))

        return ResourceCandidate(
            title=f"Apprenticeship Office - {name}",
            description=description,
            source_url=source_url,
            org_name=name,
            org_website=source_url if source_url.startswith("http") else None,
            address=address,
            city=city,
            state=self._normalize_state(state),
            zip_code=zip_code,
            categories=["training"],
            tags=self._extract_tags(office, office_type),
            phone=self._normalize_phone(phone),
            email=email,
            hours=self._format_hours(office),
            eligibility=self._build_eligibility(),
            how_to_apply=self._build_how_to_apply(name, phone, email),
            scope="state",  # Offices typically serve their state/region
            states=[self._normalize_state(state)] if state else None,
            raw_data=office,
            fetched_at=datetime.now(UTC),
        )

    def _build_description(self, office: dict[str, Any]) -> str:
        """Build a description from office attributes.

        Args:
            office: Office data

        Returns:
            Formatted description string.
        """
        parts = [
            "State or regional apprenticeship office that connects job seekers with "
            "registered apprenticeship programs. Apprenticeships combine on-the-job "
            "training with classroom instruction, allowing you to earn while you learn."
        ]

        # Add office type context
        office_type = office.get("OfficeType", office.get("Type", ""))
        if office_type:
            if "state" in office_type.lower():
                parts.append(
                    "This state office oversees apprenticeship programs and can help you find local opportunities."
                )
            elif "federal" in office_type.lower():
                parts.append("This federal office works with employers to develop new apprenticeship programs.")

        # Add veteran-specific information
        parts.append(
            "Veterans: Many registered apprenticeship programs are approved for "
            "GI Bill benefits, allowing you to receive a monthly housing allowance "
            "while earning apprentice wages."
        )

        return " ".join(parts)

    def _build_eligibility(self) -> str:
        """Build eligibility text for apprenticeship resources.

        Returns:
            Eligibility description string.
        """
        return (
            "Open to all job seekers 16 years or older. Some programs have specific "
            "requirements (education, physical ability, aptitude tests). Veterans "
            "receive priority consideration at many programs. GI Bill benefits may "
            "be used at VA-approved apprenticeship programs."
        )

    def _build_how_to_apply(self, office_name: str, phone: str | None, email: str | None) -> str:
        """Build application instructions.

        Args:
            office_name: Name of the apprenticeship office
            phone: Office phone number
            email: Office email address

        Returns:
            How to apply description string.
        """
        parts = [f"Contact {office_name} for information about apprenticeship programs in your area."]

        contact_methods = []
        if phone:
            contact_methods.append(f"call {phone}")
        if email:
            contact_methods.append(f"email {email}")

        if contact_methods:
            parts.append(f"You can {' or '.join(contact_methods)}.")

        parts.append("Visit apprenticeship.gov to search for specific programs and verify GI Bill eligibility.")

        return " ".join(parts)

    def _format_hours(self, office: dict[str, Any]) -> str | None:
        """Format hours from office data.

        Args:
            office: Office data

        Returns:
            Formatted hours string or None.
        """
        hours = office.get("Hours") or office.get("BusinessHours")
        if hours:
            return hours

        # Try individual day fields if available
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hour_parts = []

        for day in days:
            day_hours = office.get(f"{day}Hours") or office.get(day)
            if day_hours and day_hours.lower() not in ["closed", "-", ""]:
                hour_parts.append(f"{day}: {day_hours}")

        return "; ".join(hour_parts) if hour_parts else None

    def _extract_tags(self, office: dict[str, Any], office_type: str) -> list[str]:
        """Extract relevant tags from office data.

        Args:
            office: Office data
            office_type: Type of apprenticeship office

        Returns:
            List of tag strings.
        """
        tags = [
            "apprenticeship",
            "apprenticeships",
            "training",
            "on-the-job-training",
            "earn-while-you-learn",
            "gi-bill-eligible",
            "registered-apprenticeship",
        ]

        # Add office type tag
        if office_type:
            type_lower = office_type.lower()
            if "state" in type_lower:
                tags.append("state-apprenticeship-agency")
            elif "federal" in type_lower:
                tags.append("federal-apprenticeship-office")
            else:
                tags.append(f"office-{type_lower.replace(' ', '-')}")

        # Add any specific programs or industries mentioned
        programs = office.get("Programs") or office.get("Industries")
        if programs:
            # Parse common industries/trades
            programs_lower = programs.lower()
            trade_keywords = {
                "construction": "construction-trades",
                "electrical": "electrical-trades",
                "plumbing": "plumbing-trades",
                "hvac": "hvac-trades",
                "manufacturing": "manufacturing",
                "healthcare": "healthcare",
                "it": "information-technology",
                "technology": "information-technology",
            }
            for keyword, tag in trade_keywords.items():
                if keyword in programs_lower:
                    tags.append(tag)

        return list(set(tags))  # Deduplicate

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "ApprenticeshipConnector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
