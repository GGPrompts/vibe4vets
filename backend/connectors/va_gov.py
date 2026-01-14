"""VA.gov Lighthouse Facilities API connector.

Fetches veteran facilities from the official VA Developer API.
Documentation: https://developer.va.gov/explore/api/va-facilities/docs
"""

import os
from datetime import UTC, datetime
from typing import Any

import httpx

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class VAGovConnector(BaseConnector):
    """Connector for VA.gov Lighthouse Facilities API.

    This connector fetches facility data from the official VA Developer API,
    which provides information about VA health facilities, benefits offices,
    cemeteries, and vet centers nationwide.

    Requires VA_API_KEY environment variable for production use.
    """

    BASE_URL = "https://api.va.gov/services/va_facilities/v1/facilities"
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGES = 50  # Safety limit to prevent runaway pagination

    # Map VA facility types to our categories
    FACILITY_TYPE_MAP = {
        "health": ["employment", "training"],  # VA health facilities often have vocational rehab
        "benefits": ["employment", "training", "housing", "legal"],  # VBA handles all benefits
        "vet_center": ["employment", "training"],  # Readjustment counseling
        "cemetery": [],  # Not relevant to our resource categories
    }

    def __init__(self, api_key: str | None = None):
        """Initialize the connector.

        Args:
            api_key: VA API key. Falls back to VA_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("VA_API_KEY")
        self._client: httpx.Client | None = None

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="VA.gov Lighthouse API",
            url="https://developer.va.gov/explore/api/va-facilities",
            tier=1,  # Official government source
            frequency="daily",
            terms_url="https://developer.va.gov/terms-of-service",
            requires_auth=True,
        )

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["apikey"] = self.api_key
            self._client = httpx.Client(
                headers=headers,
                timeout=30.0,
            )
        return self._client

    def run(self) -> list[ResourceCandidate]:
        """Fetch all facilities from VA.gov API.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        resources: list[ResourceCandidate] = []
        client = self._get_client()

        # Fetch facilities by type to ensure we get employment-relevant ones
        for facility_type in ["health", "benefits", "vet_center"]:
            page_resources = self._fetch_facilities_by_type(client, facility_type)
            resources.extend(page_resources)

        return resources

    def _fetch_facilities_by_type(
        self, client: httpx.Client, facility_type: str
    ) -> list[ResourceCandidate]:
        """Fetch all facilities of a specific type.

        Args:
            client: HTTP client
            facility_type: One of health, benefits, vet_center, cemetery

        Returns:
            List of ResourceCandidate objects for this facility type.
        """
        resources: list[ResourceCandidate] = []
        page = 1

        while page <= self.MAX_PAGES:
            try:
                response = client.get(
                    self.BASE_URL,
                    params={
                        "type": facility_type,
                        "page": page,
                        "per_page": self.DEFAULT_PAGE_SIZE,
                    },
                )
                response.raise_for_status()
                data = response.json()

                facilities = data.get("data", [])
                if not facilities:
                    break

                for facility in facilities:
                    candidate = self._parse_facility(facility, facility_type)
                    if candidate:
                        resources.append(candidate)

                # Check for more pages
                meta = data.get("meta", {})
                pagination = meta.get("pagination", {})
                total_pages = pagination.get("totalPages", 1)

                if page >= total_pages:
                    break

                page += 1

            except httpx.HTTPError as e:
                # Log error but continue with other types
                print(f"Error fetching {facility_type} facilities page {page}: {e}")
                break

        return resources

    def _parse_facility(
        self, facility: dict[str, Any], facility_type: str
    ) -> ResourceCandidate | None:
        """Parse a facility object into a ResourceCandidate.

        Args:
            facility: Raw facility data from API
            facility_type: The facility type for categorization

        Returns:
            ResourceCandidate or None if not relevant to our categories.
        """
        categories = self.FACILITY_TYPE_MAP.get(facility_type, [])
        if not categories:
            return None  # Skip irrelevant facility types like cemeteries

        attrs = facility.get("attributes", {})
        address_obj = attrs.get("address", {}).get("physical", {})

        # Build description from available services
        services = []
        health_services = attrs.get("services", {}).get("health", [])
        benefits_services = attrs.get("services", {}).get("benefits", {}).get("standard", [])
        other_services = attrs.get("services", {}).get("other", [])

        for svc in health_services:
            if isinstance(svc, dict):
                services.append(svc.get("name", ""))
            else:
                services.append(str(svc))

        for svc in benefits_services:
            if isinstance(svc, dict):
                services.append(svc.get("name", ""))
            else:
                services.append(str(svc))

        for svc in other_services:
            if isinstance(svc, dict):
                services.append(svc.get("name", ""))
            else:
                services.append(str(svc))

        services = [s for s in services if s]  # Filter empty strings

        description = self._build_description(attrs, services, facility_type)

        # Extract hours
        hours_obj = attrs.get("hours", {})
        hours = self._format_hours(hours_obj)

        # Determine scope based on facility type
        state = address_obj.get("state")
        scope = "local" if state else "national"
        states = [state] if state else None

        return ResourceCandidate(
            title=attrs.get("name", "Unknown VA Facility"),
            description=description,
            source_url=attrs.get("website") or "https://www.va.gov/find-locations",
            org_name="U.S. Department of Veterans Affairs",
            org_website="https://www.va.gov",
            address=self._format_address(address_obj),
            city=address_obj.get("city"),
            state=self._normalize_state(state),
            zip_code=address_obj.get("zip"),
            categories=categories,
            tags=self._extract_tags(services, facility_type),
            phone=self._normalize_phone(attrs.get("phone", {}).get("main")),
            hours=hours,
            eligibility=(
                "Veterans, service members, and their families. Eligibility varies by program."
            ),
            how_to_apply="Visit the facility, call, or apply online at va.gov",
            scope=scope,
            states=states,
            raw_data=facility,
            fetched_at=datetime.now(UTC),
        )

    def _build_description(
        self, attrs: dict[str, Any], services: list[str], facility_type: str
    ) -> str:
        """Build a description from facility attributes.

        Args:
            attrs: Facility attributes
            services: List of service names
            facility_type: Type of facility

        Returns:
            Formatted description string.
        """
        parts = []

        # Add facility type context
        type_descriptions = {
            "health": "VA Health Care facility providing medical services to veterans.",
            "benefits": "Veterans Benefits Administration office providing benefits assistance.",
            "vet_center": "Vet Center providing readjustment counseling and community outreach.",
        }
        parts.append(type_descriptions.get(facility_type, "VA facility."))

        # Add services if available
        if services:
            services_text = ", ".join(services[:10])  # Limit to first 10
            if len(services) > 10:
                services_text += f", and {len(services) - 10} more services"
            parts.append(f"Services include: {services_text}.")

        # Add classification if available
        classification = attrs.get("classification")
        if classification:
            parts.append(f"Classification: {classification}.")

        return " ".join(parts)

    def _format_address(self, address_obj: dict[str, Any]) -> str | None:
        """Format address object into a single string.

        Args:
            address_obj: Address object with address1, address2, city, state, zip

        Returns:
            Formatted address string or None.
        """
        parts = []
        if address_obj.get("address1"):
            parts.append(address_obj["address1"])
        if address_obj.get("address2"):
            parts.append(address_obj["address2"])
        if address_obj.get("address3"):
            parts.append(address_obj["address3"])

        street = ", ".join(parts) if parts else None

        city = address_obj.get("city")
        state = address_obj.get("state")
        zip_code = address_obj.get("zip")

        if street and city and state:
            return f"{street}, {city}, {state} {zip_code or ''}".strip()
        elif street:
            return street
        return None

    def _format_hours(self, hours_obj: dict[str, Any]) -> str | None:
        """Format hours object into readable string.

        Args:
            hours_obj: Object with day names as keys and hour strings as values

        Returns:
            Formatted hours string or None.
        """
        if not hours_obj:
            return None

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        parts = []

        for day in days:
            value = hours_obj.get(day)
            if value and value.lower() not in ["closed", "-"]:
                parts.append(f"{day.capitalize()}: {value}")

        return "; ".join(parts) if parts else None

    def _extract_tags(self, services: list[str], facility_type: str) -> list[str]:
        """Extract relevant tags from services and facility type.

        Args:
            services: List of service names
            facility_type: Type of facility

        Returns:
            List of tag strings.
        """
        tags = [f"va-{facility_type}"]

        # Add relevant service-based tags
        service_tag_map = {
            "vocational": "vocational-rehab",
            "employment": "employment",
            "career": "career-services",
            "housing": "housing",
            "homeless": "homeless-services",
            "legal": "legal-aid",
            "benefits": "benefits",
            "education": "education",
            "training": "training",
        }

        services_lower = " ".join(services).lower()
        for keyword, tag in service_tag_map.items():
            if keyword in services_lower:
                tags.append(tag)

        return list(set(tags))  # Deduplicate

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "VAGovConnector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
