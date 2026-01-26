"""Vet Centers connector using VA Lighthouse Facilities API.

Vet Centers are community-based counseling centers providing readjustment
counseling, mental health services, and support for combat veterans, MST
survivors, drone crews, and their families.

Documentation: https://developer.va.gov/explore/api/va-facilities/docs
Vet Center Info: https://www.vetcenter.va.gov/
"""

import os
from datetime import UTC, datetime
from typing import Any

import httpx

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Vet Center eligibility categories
VET_CENTER_ELIGIBILITY = """Eligible if you:
- Served in any combat zone or area of hostility
- Experienced military sexual trauma (MST) - regardless of service era
- Provided mortuary services or emergency medical care for casualties of war
- Served as an unmanned aerial vehicle (drone) crew supporting combat operations
- Served in response to a national emergency or major disaster
- Served in Coast Guard drug interdiction operations
- Are a family member of an eligible veteran or service member
- Are bereaved by the death of a service member while on active duty

No discharge status requirements for MST-related services. Services are free and confidential."""

# Map of services commonly offered at Vet Centers
VET_CENTER_SERVICES = {
    "readjustment_counseling": "Readjustment Counseling",
    "ptsd": "PTSD Treatment",
    "mst": "Military Sexual Trauma (MST) Counseling",
    "depression": "Depression Counseling",
    "anxiety": "Anxiety Treatment",
    "grief": "Bereavement Counseling",
    "family": "Family Counseling",
    "substance_abuse": "Substance Abuse Assessment",
    "employment": "Employment Referrals",
    "benefits": "VA Benefits Referrals",
    "outreach": "Community Outreach",
}


class VetCentersConnector(BaseConnector):
    """Connector for VA Vet Centers via Lighthouse Facilities API.

    Vet Centers are community-based counseling centers separate from VA Medical
    Centers. They provide confidential counseling in a non-medical setting for:
    - Combat veterans
    - Military Sexual Trauma (MST) survivors
    - Drone crews
    - Mortuary services personnel
    - National emergency responders
    - Family members of eligible veterans

    There are 300+ Vet Centers nationwide, plus Mobile Vet Centers that provide
    services in underserved areas.
    """

    BASE_URL = "https://api.va.gov/services/va_facilities/v1/facilities"
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGES = 50  # Safety limit

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
            name="VA Vet Centers (Lighthouse API)",
            url="https://www.vetcenter.va.gov/",
            tier=1,  # Official government source
            frequency="weekly",
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
        """Fetch all Vet Centers from VA.gov API.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        resources: list[ResourceCandidate] = []
        try:
            client = self._get_client()
            page = 1

            while page <= self.MAX_PAGES:
                try:
                    response = client.get(
                        self.BASE_URL,
                        params={
                            "type": "vet_center",
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
                        candidate = self._parse_vet_center(facility)
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
                    print(f"Error fetching Vet Centers page {page}: {e}")
                    break

            return resources
        finally:
            self.close()

    def _parse_vet_center(self, facility: dict[str, Any]) -> ResourceCandidate | None:
        """Parse a Vet Center facility into a ResourceCandidate.

        Args:
            facility: Raw facility data from API

        Returns:
            ResourceCandidate for this Vet Center.
        """
        attrs = facility.get("attributes", {})
        address_obj = attrs.get("address", {}).get("physical", {})

        # Determine if this is a Mobile Vet Center
        name = attrs.get("name", "Vet Center")
        is_mobile = "mobile" in name.lower()

        # Extract services
        services = self._extract_services(attrs)

        # Build detailed description
        description = self._build_description(name, services, is_mobile)

        # Extract hours
        hours_obj = attrs.get("hours", {})
        hours = self._format_hours(hours_obj)

        # Get state for scope
        state = address_obj.get("state")

        # Build tags based on services and type
        tags = self._build_tags(services, is_mobile, name)

        # Vet Centers provide benefits consultation and employment referrals
        # But their primary focus is counseling/readjustment
        categories = ["benefits"]

        return ResourceCandidate(
            title=name,
            description=description,
            source_url=attrs.get("website") or f"https://www.va.gov/find-locations/facility/{facility.get('id', '')}",
            org_name="U.S. Department of Veterans Affairs - Vet Center Program",
            org_website="https://www.vetcenter.va.gov/",
            address=self._format_address(address_obj),
            city=address_obj.get("city"),
            state=self._normalize_state(state),
            zip_code=address_obj.get("zip"),
            categories=categories,
            tags=tags,
            phone=self._normalize_phone(attrs.get("phone", {}).get("main")),
            hours=hours,
            eligibility=VET_CENTER_ELIGIBILITY,
            how_to_apply=self._build_how_to_apply(name, is_mobile),
            scope="local",
            states=[state] if state else None,
            raw_data=facility,
            fetched_at=datetime.now(UTC),
        )

    def _extract_services(self, attrs: dict[str, Any]) -> list[str]:
        """Extract services from facility attributes.

        Args:
            attrs: Facility attributes

        Returns:
            List of service names.
        """
        services = []

        # Check for services in the API response
        health_services = attrs.get("services", {}).get("health", [])
        other_services = attrs.get("services", {}).get("other", [])

        for svc in health_services + other_services:
            if isinstance(svc, dict):
                services.append(svc.get("name", ""))
            else:
                services.append(str(svc))

        # Filter empty strings
        return [s for s in services if s]

    def _build_description(
        self,
        name: str,
        services: list[str],
        is_mobile: bool,
    ) -> str:
        """Build a detailed description for the Vet Center.

        Args:
            name: Facility name
            services: List of services offered
            is_mobile: Whether this is a Mobile Vet Center

        Returns:
            Formatted description string.
        """
        parts = []

        if is_mobile:
            parts.append(
                f"{name} is a Mobile Vet Center providing confidential counseling and "
                "outreach services in communities without a nearby Vet Center. Mobile "
                "Vet Centers bring readjustment counseling directly to veterans in "
                "underserved areas."
            )
        else:
            parts.append(
                f"{name} is a community-based counseling center providing confidential "
                "readjustment counseling and support services for veterans, service "
                "members, and their families. Vet Centers offer a non-medical, relaxed "
                "setting separate from VA Medical Centers."
            )

        # Core services offered at all Vet Centers
        core_services = [
            "individual and group counseling",
            "PTSD treatment",
            "military sexual trauma (MST) support",
            "bereavement counseling",
            "family counseling",
            "VA benefits referrals",
            "employment assistance referrals",
        ]

        parts.append(f"Services include: {', '.join(core_services)}.")

        # Add any specific services from the API
        if services:
            additional = [s for s in services if s.lower() not in " ".join(core_services).lower()]
            if additional:
                parts.append(f"Additional services: {', '.join(additional[:5])}.")

        parts.append(
            "All services are free and confidential. Records are not shared with "
            "other VA offices, the Defense Department, or military units."
        )

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

    def _build_tags(
        self,
        services: list[str],
        is_mobile: bool,
        name: str,
    ) -> list[str]:
        """Build tags for the Vet Center.

        Args:
            services: List of service names
            is_mobile: Whether this is a Mobile Vet Center
            name: Facility name

        Returns:
            List of tag strings.
        """
        tags = [
            "vet-center",
            "counseling",
            "readjustment-counseling",
            "ptsd",
            "mst",
            "mental-health",
            "free-services",
            "confidential",
        ]

        if is_mobile:
            tags.append("mobile-vet-center")
            tags.append("outreach")

        # Add service-based tags
        services_lower = " ".join(services).lower()
        service_tag_map = {
            "bereavement": "bereavement",
            "grief": "bereavement",
            "family": "family-counseling",
            "group": "group-counseling",
            "substance": "substance-abuse",
            "employment": "employment-referrals",
            "outreach": "outreach",
        }

        for keyword, tag in service_tag_map.items():
            if keyword in services_lower:
                tags.append(tag)

        # Check name for additional context
        name_lower = name.lower()
        if "outstation" in name_lower:
            tags.append("outstation")
        if "satellite" in name_lower:
            tags.append("satellite")

        return list(set(tags))  # Deduplicate

    def _build_how_to_apply(self, name: str, is_mobile: bool) -> str:
        """Build instructions for accessing Vet Center services.

        Args:
            name: Facility name
            is_mobile: Whether this is a Mobile Vet Center

        Returns:
            Instruction string.
        """
        if is_mobile:
            return (
                "Mobile Vet Centers travel to communities on a regular schedule. "
                "Contact the Vet Center Call Center at 1-877-927-8387 to find "
                "the Mobile Vet Center schedule in your area. No appointment needed "
                "for walk-in services. All services are free and confidential."
            )
        else:
            return (
                f"Visit {name} during operating hours or call to schedule an appointment. "
                "Walk-ins are welcome. You can also call the Vet Center Call Center at "
                "1-877-927-8387 (available 24/7) to get connected to your nearest "
                "Vet Center. No VA enrollment or service connection required. "
                "All services are free and confidential."
            )

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "VetCentersConnector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
