"""CareerOneStop API connector for American Job Centers.

Fetches American Job Center locations from the DOL CareerOneStop API.
Documentation: https://www.careeronestop.org/Developers/WebAPI/web-api.aspx
"""

import os
from datetime import UTC, datetime
from typing import Any

import httpx

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class CareerOneStopConnector(BaseConnector):
    """Connector for CareerOneStop American Job Center Finder API.

    This connector fetches American Job Center (AJC) data from the DOL
    CareerOneStop API. AJCs provide employment services to all job seekers
    including veterans, with many locations having dedicated veteran
    representatives.

    Requires CAREERONESTOP_API_KEY environment variable for API access.
    """

    BASE_URL = "https://api.careeronestop.org/v1/ajcfinder"
    DEFAULT_RADIUS = 500  # Miles - large radius to get all centers
    MAX_RESULTS = 500  # Maximum results per request

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
                     or uses default test user.
        """
        self.api_key = api_key or os.environ.get("CAREERONESTOP_API_KEY")
        self.user_id = user_id or os.environ.get("CAREERONESTOP_USER_ID", "vibe4vets")
        self._client: httpx.Client | None = None

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="CareerOneStop American Job Centers",
            url="https://www.careeronestop.org/LocalHelp/AmericanJobCenters/american-job-centers.aspx",
            tier=1,  # Official DOL government source
            frequency="weekly",
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
        """Fetch all American Job Centers from CareerOneStop API.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        resources: list[ResourceCandidate] = []
        client = self._get_client()
        seen_ids: set[str] = set()  # Track unique centers to avoid duplicates

        # Fetch AJCs by state to ensure comprehensive coverage
        for state in self.US_STATES:
            state_resources = self._fetch_ajcs_by_state(client, state, seen_ids)
            resources.extend(state_resources)

        return resources

    def _fetch_ajcs_by_state(self, client: httpx.Client, state: str, seen_ids: set[str]) -> list[ResourceCandidate]:
        """Fetch American Job Centers for a specific state.

        Args:
            client: HTTP client
            state: Two-letter state code
            seen_ids: Set of already-seen center IDs to avoid duplicates

        Returns:
            List of ResourceCandidate objects for this state.
        """
        resources: list[ResourceCandidate] = []

        try:
            # CareerOneStop API uses location-based search
            # Using state capital area with large radius to get all state results
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

            # Extract centers from response
            centers = data.get("OneStopCenterList", [])

            for center in centers:
                # Create unique ID from name and address
                center_id = self._create_center_id(center)
                if center_id in seen_ids:
                    continue
                seen_ids.add(center_id)

                candidate = self._parse_center(center)
                if candidate:
                    resources.append(candidate)

        except httpx.HTTPError as e:
            # Log error but continue with other states
            print(f"Error fetching AJCs for {state}: {e}")

        return resources

    def _create_center_id(self, center: dict[str, Any]) -> str:
        """Create a unique identifier for a center.

        Args:
            center: Raw center data from API

        Returns:
            Unique string identifier.
        """
        name = center.get("Name", "")
        address = center.get("Address", "")
        city = center.get("City", "")
        state = center.get("StateName", "")
        return f"{name}|{address}|{city}|{state}".lower()

    def _parse_center(self, center: dict[str, Any]) -> ResourceCandidate | None:
        """Parse a center object into a ResourceCandidate.

        Args:
            center: Raw center data from API

        Returns:
            ResourceCandidate or None if parsing fails.
        """
        name = center.get("Name")
        if not name:
            return None

        # Build description
        description = self._build_description(center)

        # Extract contact info
        phone = center.get("Phone")
        email = center.get("Email")

        # Format address
        address = center.get("Address")
        city = center.get("City")
        state = center.get("StateName")
        zip_code = center.get("Zip")

        # Build source URL - prefer center's own URL, fallback to finder
        source_url = center.get("URL") or center.get("Url")
        if not source_url:
            source_url = "https://www.careeronestop.org/LocalHelp/AmericanJobCenters/find-american-job-centers.aspx"

        return ResourceCandidate(
            title=name,
            description=description,
            source_url=source_url,
            org_name="American Job Center",
            org_website="https://www.careeronestop.org",
            address=address,
            city=city,
            state=self._normalize_state(state),
            zip_code=zip_code,
            categories=["employment", "training"],
            tags=self._extract_tags(center),
            phone=self._normalize_phone(phone),
            email=email,
            hours=self._format_hours(center),
            eligibility="Open to all job seekers. Veterans receive priority of service.",
            how_to_apply="Visit the center in person, call, or check website for services.",
            scope="local",
            states=[self._normalize_state(state)] if state else None,
            raw_data=center,
            fetched_at=datetime.now(UTC),
        )

    def _build_description(self, center: dict[str, Any]) -> str:
        """Build a description from center attributes.

        Args:
            center: Center data

        Returns:
            Formatted description string.
        """
        parts = [
            "American Job Center providing employment and training services. "
            "Offers career counseling, job search assistance, resume help, "
            "and training referrals."
        ]

        # Add veteran representative info if available
        vet_rep_name = center.get("VeteranRepName")
        vet_rep_email = center.get("VeteranRepEmail")
        vet_rep_phone = center.get("VeteranRepPhone")

        if vet_rep_name or vet_rep_email or vet_rep_phone:
            parts.append("Veterans: This location has a dedicated veterans representative.")
            vet_parts = []
            if vet_rep_name:
                vet_parts.append(f"Contact: {vet_rep_name}")
            if vet_rep_phone:
                vet_parts.append(f"Phone: {vet_rep_phone}")
            if vet_rep_email:
                vet_parts.append(f"Email: {vet_rep_email}")
            if vet_parts:
                parts.append(" ".join(vet_parts))

        # Add services if listed
        services = center.get("Services")
        if services:
            parts.append(f"Services: {services}")

        return " ".join(parts)

    def _format_hours(self, center: dict[str, Any]) -> str | None:
        """Format hours from center data.

        Args:
            center: Center data

        Returns:
            Formatted hours string or None.
        """
        hours = center.get("Hours")
        if hours:
            return hours

        # Try individual day fields if available
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hour_parts = []

        for day in days:
            day_hours = center.get(f"{day}Hours") or center.get(day)
            if day_hours and day_hours.lower() not in ["closed", "-", ""]:
                hour_parts.append(f"{day}: {day_hours}")

        return "; ".join(hour_parts) if hour_parts else None

    def _extract_tags(self, center: dict[str, Any]) -> list[str]:
        """Extract relevant tags from center data.

        Args:
            center: Center data

        Returns:
            List of tag strings.
        """
        tags = ["american-job-center", "employment", "training", "career-services"]

        # Add veteran tag if has veteran representative
        if center.get("VeteranRepName") or center.get("VeteranRepEmail"):
            tags.append("veteran-priority")
            tags.append("veteran-representative")

        # Add center type if specified
        center_type = center.get("CenterType") or center.get("Type")
        if center_type:
            tags.append(f"ajc-{center_type.lower().replace(' ', '-')}")

        return list(set(tags))  # Deduplicate

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "CareerOneStopConnector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
