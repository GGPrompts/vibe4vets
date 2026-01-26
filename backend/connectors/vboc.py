"""SBA Veterans Business Outreach Center (VBOC) connector.

Imports VBOC data from the reference JSON file.
Source: SBA Office of Veterans Business Development
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class VBOCConnector(BaseConnector):
    """Connector for SBA Veterans Business Outreach Centers.

    Parses the vboc_centers.json file containing 31 VBOCs nationwide
    providing entrepreneurship support to veterans, service members,
    and military spouses.

    Services offered:
        - Business counseling and mentorship
        - Entrepreneurship training workshops
        - Business plan development assistance
        - Access to SBA resource partner network
        - Boots to Business program support
    """

    # Path to the VBOC data file relative to project root
    DEFAULT_DATA_PATH = "data/reference/vboc_centers.json"

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
            name="SBA Veterans Business Outreach Centers",
            url="https://www.sba.gov/local-assistance/resource-partners/veterans-business-outreach-centers-vboc",
            tier=1,  # Official federal government (SBA)
            frequency="quarterly",  # VBOCs are relatively stable
            terms_url="https://www.sba.gov/about-sba/sba-performance/open-government/digital-sba/terms-service",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse VBOC data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"VBOC data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for center in data.get("centers", []):
            candidate = self._parse_center(center, fetched_at=now)
            if candidate:
                resources.append(candidate)

        return resources

    def _parse_center(
        self,
        center: dict[str, Any],
        fetched_at: datetime,
    ) -> ResourceCandidate | None:
        """Parse a VBOC center into a ResourceCandidate.

        Args:
            center: Center data from JSON
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this center, or None if invalid.
        """
        name = center.get("name")
        if not name:
            return None

        states_served = center.get("states_served", [])
        host_org = center.get("host_org", "")
        region_description = center.get("region_description")

        # Determine scope based on coverage
        if len(states_served) > 1:
            scope = "regional"
        elif len(states_served) == 1:
            scope = "state"
        else:
            scope = "national"

        # Build description
        description = self._build_description(
            name=name,
            host_org=host_org,
            states_served=states_served,
            region_description=region_description,
        )

        # Build title - include state(s) for clarity
        title = self._build_title(name, states_served)

        # Build source URL - prefer center's own website
        website = center.get("website") or self.metadata.url

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website,
            org_name=host_org or "SBA Veterans Business Outreach Center",
            org_website=center.get("website"),
            address=center.get("address"),
            city=center.get("city"),
            state=self._normalize_state(center.get("state")),
            zip_code=center.get("zip"),
            categories=["employment"],
            tags=self._build_tags(center),
            phone=self._normalize_phone(center.get("phone")),
            email=center.get("email"),
            eligibility=self._get_eligibility(),
            how_to_apply=self._get_how_to_apply(center),
            scope=scope,
            states=states_served if states_served else None,
            raw_data=center,
            fetched_at=fetched_at,
        )

    def _build_title(self, name: str, states_served: list[str]) -> str:
        """Build resource title.

        Args:
            name: Center name
            states_served: List of state codes served

        Returns:
            Formatted title string.
        """
        # If name already includes descriptive location, use as-is
        if len(states_served) == 1:
            return f"{name} ({states_served[0]})"
        elif len(states_served) > 1 and len(states_served) <= 3:
            return f"{name} ({', '.join(states_served)})"
        elif len(states_served) > 3:
            return f"{name} (Multi-State)"
        return name

    def _build_description(
        self,
        name: str,
        host_org: str,
        states_served: list[str],
        region_description: str | None,
    ) -> str:
        """Build resource description.

        Args:
            name: Center name
            host_org: Host organization name
            states_served: List of state codes served
            region_description: Optional regional description

        Returns:
            Formatted description string.
        """
        parts = []

        # Opening statement
        if host_org:
            parts.append(
                f"{name}, hosted by {host_org}, is an SBA Veterans Business "
                f"Outreach Center providing free entrepreneurship support."
            )
        else:
            parts.append(f"{name} is an SBA Veterans Business Outreach Center providing free entrepreneurship support.")

        # Coverage area
        if region_description:
            parts.append(f"Serves {region_description}.")
        elif len(states_served) == 1:
            parts.append(f"Serves veterans in {states_served[0]}.")
        elif len(states_served) > 1:
            parts.append(f"Serves veterans across {', '.join(states_served)}.")

        # Services offered
        parts.append(
            "Services include business counseling, entrepreneurship training, "
            "business plan development, and access to SBA resource partners. "
            "Supports Boots to Business program for transitioning service members."
        )

        return " ".join(parts)

    def _build_tags(self, center: dict[str, Any]) -> list[str]:
        """Build tags list for the center.

        Args:
            center: Center data

        Returns:
            List of tag strings.
        """
        tags = [
            "vboc",
            "sba",
            "small-business",
            "entrepreneurship",
            "self-employment",
            "business-counseling",
            "veteran-entrepreneur",
            "boots-to-business",
        ]

        # Add host organization tag if relevant
        host_org = center.get("host_org", "").lower()
        if "university" in host_org or "college" in host_org:
            tags.append("university-partnership")

        return tags

    def _get_eligibility(self) -> str:
        """Return standard VBOC eligibility text.

        Returns:
            Eligibility description string.
        """
        return (
            "Veterans, service members (including National Guard and Reserve), "
            "and military spouses interested in starting or growing a small business. "
            "Services are free and available regardless of discharge status."
        )

    def _get_how_to_apply(self, center: dict[str, Any]) -> str:
        """Build how-to-apply text for a center.

        Args:
            center: Center data

        Returns:
            How-to-apply description string.
        """
        parts = ["Contact the VBOC directly by phone or email to schedule a consultation."]

        website = center.get("website")
        if website:
            parts.append(f"Visit {website} for more information and to register for workshops.")

        parts.append("You can also find your local VBOC at sba.gov/vboc or call the SBA Answer Desk at 1-800-827-5722.")

        return " ".join(parts)
