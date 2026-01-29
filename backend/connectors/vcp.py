"""Veterans Community Project (VCP) tiny home village connector.

VCP builds tiny home villages for homeless veterans, providing fully furnished
homes (240-320 sq ft) with wraparound support services. Founded by combat veterans,
VCP follows a unique model where veterans keep all furniture when transitioning
to permanent housing. Success rate: 85% transition to permanent housing.

Source: https://vcp.org/
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class VCPConnector(BaseConnector):
    """Connector for Veterans Community Project tiny home villages.

    Loads village data from a curated JSON file containing VCP village locations
    across the United States. Each village provides:
    - Fully furnished tiny homes (240-320 sq ft)
    - All utilities included
    - Case management and wraparound services
    - Veterans keep furniture when transitioning to permanent housing
    """

    DEFAULT_DATA_PATH = "data/reference/vcp_villages.json"

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
            name="Veterans Community Project Villages",
            url="https://vcp.org/",
            tier=2,  # Established nonprofit
            frequency="monthly",
            terms_url="https://vcp.org/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse VCP village data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects, one per village.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"VCP data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)
        success_rate = data.get("success_rate", "85% transition to permanent housing")

        for village in data.get("villages", []):
            candidate = self._parse_village(village, success_rate, now)
            resources.append(candidate)

        return resources

    def _parse_village(
        self,
        village: dict,
        success_rate: str,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a village record into a ResourceCandidate.

        Args:
            village: Village data dictionary.
            success_rate: VCP success rate for transitions.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this village.
        """
        name = village.get("name", "VCP Village")
        city = village.get("city", "")
        state = village.get("state", "")
        status = village.get("status", "operational")

        # Build title based on status
        if status == "under-construction":
            title = f"{name} - Tiny Home Village (Under Construction)"
        else:
            title = f"{name} - Tiny Home Village for Veterans"

        # Build description
        description = self._build_description(village, success_rate)

        # Build eligibility
        eligibility = self._build_eligibility(village)

        # Build how to apply
        how_to_apply = self._build_how_to_apply(village)

        # Build tags
        tags = self._build_tags(village)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=f"https://vcp.org/about-vcp/our-locations/{city.lower().replace(' ', '-')}/",
            org_name="Veterans Community Project",
            org_website="https://vcp.org/",
            address=village.get("address"),
            city=city,
            state=state,
            zip_code=village.get("zip_code"),
            categories=["housing"],
            tags=tags,
            phone=self._normalize_phone(village.get("phone")),
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="local",
            states=[state] if state else None,
            raw_data=village,
            fetched_at=fetched_at,
        )

    def _build_description(self, village: dict, success_rate: str) -> str:
        """Build resource description.

        Args:
            village: Village data dictionary.
            success_rate: VCP success rate for transitions.

        Returns:
            Formatted description string.
        """
        parts = []

        # Add village-specific description
        if village.get("description"):
            parts.append(village["description"])

        # Add home count
        status = village.get("status", "operational")
        if status == "operational":
            homes = village.get("homes", 0)
            if homes:
                home_sizes = village.get("home_sizes", "240-320 sq ft")
                parts.append(
                    f"Features {homes} fully furnished tiny homes ({home_sizes}), "
                    "each with all utilities included."
                )
        else:
            planned_homes = village.get("planned_homes", 0)
            if planned_homes:
                parts.append(f"Will feature {planned_homes} tiny homes when complete.")

        # Add family housing info
        family_homes = village.get("family_homes", 0)
        if family_homes:
            parts.append(f"Includes {family_homes} family-sized homes.")

        # Add services summary
        services = village.get("services", [])
        if services:
            service_list = ", ".join(services[:4])
            if len(services) > 4:
                service_list += f", and {len(services) - 4} more services"
            parts.append(f"Services include: {service_list}.")

        # Add success rate
        parts.append(
            f"VCP has an {success_rate}. Veterans keep all furniture when "
            "moving to permanent housing."
        )

        return " ".join(parts)

    def _build_eligibility(self, village: dict) -> str:
        """Build eligibility description.

        Args:
            village: Village data dictionary.

        Returns:
            Eligibility requirements string.
        """
        parts = [
            "Veterans experiencing homelessness or at imminent risk of homelessness.",
            "Must be a U.S. military veteran.",
        ]

        # Check for family housing
        family_homes = village.get("family_homes", 0)
        if family_homes:
            parts.append("Family housing available for veterans with dependents.")

        # Pet-friendly
        features = village.get("features", [])
        if any("pet" in f.lower() for f in features):
            parts.append("Pet-friendly community.")

        return " ".join(parts)

    def _build_how_to_apply(self, village: dict) -> str:
        """Build application instructions.

        Args:
            village: Village data dictionary.

        Returns:
            How to apply string.
        """
        phone = village.get("phone", "(816) 912-8406")
        city = village.get("city", "")
        status = village.get("status", "operational")

        parts = []

        if status == "operational":
            parts.append(
                f"Contact VCP at {phone} to inquire about housing at the {city} village."
            )
            parts.append(
                "Visit vcp.org to learn more about the application process. "
                "Walk-ins are welcome at the Outreach Center."
            )
        else:
            parts.append(
                f"The {city} village is currently under construction. "
                f"Contact VCP at {phone} for updates on availability."
            )
            parts.append("Visit vcp.org for the latest information.")

        return " ".join(parts)

    def _build_tags(self, village: dict) -> list[str]:
        """Build tags list.

        Args:
            village: Village data dictionary.

        Returns:
            List of tag strings.
        """
        tags = [
            "vcp",
            "veterans-community-project",
            "tiny-homes",
            "homeless-services",
            "transitional-housing",
            "housing-first",
        ]

        # Add status tag
        status = village.get("status", "operational")
        if status == "under-construction":
            tags.append("under-construction")
        else:
            tags.append("operational")

        # Add family housing tag if applicable
        family_homes = village.get("family_homes", 0)
        if family_homes:
            tags.append("family-housing")
            tags.append("veterans-with-children")

        # Add pet-friendly tag if applicable
        features = village.get("features", [])
        if any("pet" in f.lower() for f in features):
            tags.append("pet-friendly")

        # Check for specific services
        services = village.get("services", [])
        service_lower = [s.lower() for s in services]

        if any("mental health" in s for s in service_lower):
            tags.append("mental-health")
        if any("employment" in s for s in service_lower):
            tags.append("employment-services")
        if any("dental" in s for s in service_lower):
            tags.append("dental-services")
        if any("medical" in s or "health" in s for s in service_lower):
            tags.append("medical-services")
        if any("veterinary" in s for s in service_lower):
            tags.append("veterinary-services")

        # Add village ID tag
        village_id = village.get("id", "")
        if village_id:
            tags.append(village_id)

        # Add state tag
        state = village.get("state", "")
        if state:
            tags.append(f"state-{state.lower()}")

        return tags
