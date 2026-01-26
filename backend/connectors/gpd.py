"""GPD (Grant and Per Diem) transitional housing grantee data connector.

Imports GPD grantee data from the FY24 Awards JSON file extracted from VA.gov.
Source: VA Homeless Programs - GPD Program Office

The Grant and Per Diem (GPD) Program is VA's largest transitional housing program
for veterans experiencing homelessness. It funds community organizations to provide:
- Transitional housing (up to 24 months)
- Service centers (non-residential support)
- Bridge housing (short-term while awaiting permanent housing)
- Low-demand beds (harm reduction model)
- Clinical treatment beds
- Beds for veterans with minor dependents
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class GPDConnector(BaseConnector):
    """Connector for GPD (Grant and Per Diem) transitional housing data.

    Parses the GPD_FY24_Awards.json file containing 295 grantee organizations
    providing transitional housing to homeless veterans across the US.

    Data structure per award:
        - visn: VA Integrated Service Network number
        - station: VA Medical Center station code
        - organization: Grantee organization name
        - grant_id: Unique grant identifier
        - total_beds: Total transitional housing beds
        - is_service_center: Whether this is a service center (non-residential)
        - state: State code (derived from station mapping)
        - bed_types: Breakdown by bed type (bridge, low_demand, clinical, etc.)
    """

    # Path to the GPD data file relative to project root
    DEFAULT_DATA_PATH = "data/reference/GPD_FY24_Awards.json"

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
            name="VA GPD FY24 Grantee Data",
            url="https://www.va.gov/homeless/gpd.asp",
            tier=1,  # Official VA program data
            frequency="yearly",  # Updated annually with fiscal year
            terms_url="https://www.va.gov/homeless/gpd.asp",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse GPD grantee data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"GPD data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for award in data.get("awards", []):
            candidate = self._parse_grantee(
                visn=award.get("visn"),
                station=award.get("station"),
                org_name=award.get("organization"),
                grant_id=award.get("grant_id"),
                total_beds=award.get("total_beds", 0),
                is_service_center=award.get("is_service_center", False),
                state=award.get("state"),
                bed_types=award.get("bed_types", {}),
                fetched_at=now,
            )
            resources.append(candidate)

        return resources

    def _parse_grantee(
        self,
        visn: str | None,
        station: str | None,
        org_name: str | None,
        grant_id: str | None,
        total_beds: int,
        is_service_center: bool,
        state: str | None,
        bed_types: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a grantee record into a ResourceCandidate.

        Args:
            visn: VA Integrated Service Network number
            station: VA Medical Center station code
            org_name: Organization name
            grant_id: GPD grant identifier
            total_beds: Total transitional housing beds
            is_service_center: Whether this is a service center
            state: State code
            bed_types: Breakdown by bed type
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this grantee.
        """
        if not org_name:
            org_name = "Unknown Organization"

        # Build title
        title = self._build_title(org_name, state, is_service_center)

        # Build description
        description = self._build_description(org_name, state, total_beds, is_service_center, bed_types)

        # Determine scope
        scope = "state" if state else "local"

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://www.va.gov/homeless/gpd.asp",
            org_name=org_name,
            org_website=None,  # Not provided in data
            categories=["housing"],
            tags=self._build_tags(grant_id, visn, is_service_center, bed_types),
            eligibility=self._build_eligibility(is_service_center),
            how_to_apply=self._build_how_to_apply(org_name),
            scope=scope,
            states=[state] if state else None,
            raw_data={
                "grant_id": grant_id,
                "visn": visn,
                "station": station,
                "total_beds": total_beds,
                "is_service_center": is_service_center,
                "bed_types": bed_types,
            },
            fetched_at=fetched_at,
        )

    def _build_title(
        self,
        org_name: str,
        state: str | None,
        is_service_center: bool,
    ) -> str:
        """Build resource title.

        Args:
            org_name: Organization name
            state: State code
            is_service_center: Whether this is a service center

        Returns:
            Formatted title string.
        """
        if is_service_center:
            if state:
                return f"GPD Service Center - {org_name} ({state})"
            return f"GPD Service Center - {org_name}"
        else:
            if state:
                return f"GPD Transitional Housing - {org_name} ({state})"
            return f"GPD Transitional Housing - {org_name}"

    def _build_description(
        self,
        org_name: str,
        state: str | None,
        total_beds: int,
        is_service_center: bool,
        bed_types: dict,
    ) -> str:
        """Build resource description.

        Args:
            org_name: Organization name
            state: State code
            total_beds: Total beds
            is_service_center: Whether this is a service center
            bed_types: Breakdown by bed type

        Returns:
            Formatted description string.
        """
        parts = []

        if is_service_center:
            parts.append(
                f"{org_name} operates a VA GPD (Grant and Per Diem) Service Center "
                f"providing daytime support services to veterans experiencing homelessness."
            )
            if state:
                parts.append(f"Located in {state}.")
            parts.append(
                "Service centers offer case management, employment assistance, "
                "housing search support, and connections to VA and community resources "
                "without requiring overnight stays."
            )
        else:
            parts.append(
                f"{org_name} is a VA GPD (Grant and Per Diem) grantee providing "
                f"transitional housing to veterans experiencing homelessness."
            )
            if state:
                parts.append(f"Serves veterans in {state}.")
            if total_beds > 0:
                parts.append(f"Capacity: {total_beds} transitional housing beds.")

            # Describe bed types if available
            bed_descriptions = self._describe_bed_types(bed_types)
            if bed_descriptions:
                parts.append(f"Programs include: {bed_descriptions}.")

            parts.append(
                "GPD transitional housing provides up to 24 months of supportive housing "
                "with case management, mental health services, substance use treatment, "
                "and assistance finding permanent housing."
            )

        return " ".join(parts)

    def _describe_bed_types(self, bed_types: dict) -> str:
        """Describe bed types in human-readable format.

        Args:
            bed_types: Dictionary of bed type counts

        Returns:
            Comma-separated description of bed types with counts.
        """
        descriptions = []

        type_names = {
            "bridge_housing": "bridge housing",
            "low_demand": "low-demand/harm reduction",
            "hospital_to_housing": "hospital-to-housing",
            "clinical_treatment": "clinical treatment",
            "intensive": "intensive services",
            "minor_dependents": "beds for veterans with children",
        }

        for key, label in type_names.items():
            count = bed_types.get(key, 0)
            if count > 0:
                descriptions.append(f"{count} {label} beds")

        return ", ".join(descriptions)

    def _build_eligibility(self, is_service_center: bool) -> str:
        """Build eligibility description.

        Args:
            is_service_center: Whether this is a service center

        Returns:
            Eligibility requirements string.
        """
        if is_service_center:
            return (
                "Veterans experiencing homelessness or at risk of homelessness. "
                "Must be eligible for VA health care. Service centers do not require "
                "overnight stays - veterans can access daytime services while seeking "
                "other housing arrangements."
            )
        else:
            return (
                "Veterans experiencing homelessness. Must be eligible for VA health care. "
                "Veterans must have served on active duty and received an other than "
                "dishonorable discharge. GPD is designed for veterans ready to engage "
                "in services and work toward permanent housing within 24 months."
            )

    def _build_how_to_apply(self, org_name: str) -> str:
        """Build application instructions.

        Args:
            org_name: Organization name

        Returns:
            How to apply string.
        """
        return (
            f"Contact {org_name} directly or visit your local VA Medical Center and "
            f"ask for the Homeless Veteran Coordinator. You can also call the National "
            f"Call Center for Homeless Veterans at 1-877-4AID-VET (1-877-424-3838) "
            f"24 hours a day, 7 days a week for assistance."
        )

    def _build_tags(
        self,
        grant_id: str | None,
        visn: str | None,
        is_service_center: bool,
        bed_types: dict,
    ) -> list[str]:
        """Build tags list.

        Args:
            grant_id: GPD grant identifier
            visn: VA Integrated Service Network number
            is_service_center: Whether this is a service center
            bed_types: Breakdown by bed type

        Returns:
            List of tag strings.
        """
        tags = [
            "gpd",
            "housing",
            "homeless-services",
            "transitional-housing",
        ]

        if is_service_center:
            tags.append("service-center")
        else:
            tags.append("residential")

        # Add bed type tags
        if bed_types.get("bridge_housing", 0) > 0:
            tags.append("bridge-housing")
        if bed_types.get("low_demand", 0) > 0:
            tags.append("low-demand")
            tags.append("harm-reduction")
        if bed_types.get("hospital_to_housing", 0) > 0:
            tags.append("hospital-to-housing")
        if bed_types.get("clinical_treatment", 0) > 0:
            tags.append("clinical-treatment")
        if bed_types.get("minor_dependents", 0) > 0:
            tags.append("families-with-children")

        if grant_id:
            tags.append(f"grant-{grant_id}")

        if visn:
            tags.append(f"visn-{visn}")

        return tags
