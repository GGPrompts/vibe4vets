"""SSVF (Supportive Services for Veteran Families) FY26 grantee data connector.

Imports SSVF grantee data from the FY26 Awards spreadsheet.
Source: VA SSVF Program Office
"""

from datetime import UTC, datetime
from pathlib import Path

import openpyxl

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class SSVFConnector(BaseConnector):
    """Connector for SSVF FY26 grantee data.

    Parses the SSVF_FY26_Awards.xlsx spreadsheet containing 235 organizations
    providing Supportive Services for Veteran Families across the US.

    Columns:
        - Geographical Area Served: State(s) served (semicolon-separated for multi-state)
        - Grant ID: Unique grant identifier
        - Organization Name: Grantee organization
        - Adjusted Awarded Amount: FY26 award in dollars
        - VISN: VA Integrated Service Network(s)
    """

    # Path to the SSVF data file relative to project root
    DEFAULT_DATA_PATH = "data/reference/SSVF_FY26_Awards.xlsx"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to Excel file. Falls back to DEFAULT_DATA_PATH.
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
            name="SSVF FY26 Grantee Data",
            url="https://www.va.gov/homeless/ssvf/",
            tier=1,  # Official VA program data
            frequency="yearly",  # Updated annually with fiscal year
            terms_url="https://www.va.gov/homeless/ssvf/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse SSVF grantee data from Excel file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"SSVF data file not found: {self.data_path}")

        workbook = openpyxl.load_workbook(self.data_path, read_only=True)
        sheet = workbook.active
        if sheet is None:
            raise ValueError("Excel file has no active sheet")

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        # Skip header row (row 1)
        for row in sheet.iter_rows(min_row=2, values_only=True):
            states_raw, grant_id, org_name, award_amount, visn = row

            # Skip empty rows
            if not org_name:
                continue

            candidate = self._parse_grantee(
                states_raw=str(states_raw) if states_raw else None,
                grant_id=str(grant_id) if grant_id else None,
                org_name=str(org_name),
                award_amount=float(award_amount) if award_amount else None,
                visn=str(visn) if visn else None,
                fetched_at=now,
            )
            resources.append(candidate)

        workbook.close()
        return resources

    def _parse_grantee(
        self,
        states_raw: str | None,
        grant_id: str | None,
        org_name: str,
        award_amount: int | float | None,
        visn: str | None,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a grantee row into a ResourceCandidate.

        Args:
            states_raw: State(s) served, semicolon-separated for multi-state
            grant_id: SSVF grant identifier
            org_name: Organization name
            award_amount: FY26 award amount in dollars
            visn: VA Integrated Service Network
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this grantee.
        """
        # Parse states (semicolon-separated for multi-state grantees)
        states = self._parse_states(states_raw)

        # Determine scope based on coverage
        if len(states) > 1:
            scope = "regional"
        elif len(states) == 1:
            scope = "state"
        else:
            scope = "national"

        # Format award amount for description
        award_str = f"${award_amount:,.0f}" if award_amount else "Undisclosed"

        # Build description
        description = self._build_description(org_name, states, award_str)

        # Build title
        if len(states) == 1:
            title = f"SSVF - {org_name} ({states[0]})"
        elif len(states) > 1:
            title = f"SSVF - {org_name} (Multi-State)"
        else:
            title = f"SSVF - {org_name}"

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://www.va.gov/homeless/ssvf/",
            org_name=org_name,
            org_website=None,  # Not provided in spreadsheet
            categories=["housing"],
            tags=self._build_tags(grant_id, visn),
            eligibility=(
                "Very low-income veteran families who are homeless or at imminent risk "
                "of homelessness. Income must be at or below 50% of Area Median Income. "
                "Veterans must have served on active duty and received an other than "
                "dishonorable discharge."
            ),
            how_to_apply=(
                "Contact the SSVF provider directly or call the National Call Center "
                "for Homeless Veterans at 1-877-4AID-VET (1-877-424-3838)."
            ),
            scope=scope,
            states=states if states else None,
            raw_data={
                "grant_id": grant_id,
                "states_raw": states_raw,
                "award_amount": award_amount,
                "visn": visn,
            },
            fetched_at=fetched_at,
        )

    def _parse_states(self, states_raw: str | None) -> list[str]:
        """Parse state string into list of state codes.

        Args:
            states_raw: Raw state string, possibly semicolon-separated

        Returns:
            List of normalized state codes.
        """
        if not states_raw:
            return []

        # Split by semicolon for multi-state grantees
        raw_states = states_raw.split(";")

        states = []
        for state in raw_states:
            normalized = self._normalize_state(state)
            if normalized:
                states.append(normalized)

        return states

    def _build_description(
        self,
        org_name: str,
        states: list[str],
        award_str: str,
    ) -> str:
        """Build resource description.

        Args:
            org_name: Organization name
            states: List of state codes served
            award_str: Formatted award amount

        Returns:
            Formatted description string.
        """
        parts = [
            f"{org_name} is an SSVF (Supportive Services for Veteran Families) grantee "
            f"providing housing assistance to veteran families."
        ]

        if len(states) == 1:
            parts.append(f"Serves veterans in {states[0]}.")
        elif len(states) > 1:
            parts.append(f"Serves veterans across {', '.join(states)}.")

        parts.append(
            "Services include rapid re-housing assistance, homelessness prevention, "
            "temporary financial assistance, and case management."
        )

        parts.append(f"FY2026 award: {award_str}.")

        return " ".join(parts)

    def _build_tags(self, grant_id: str | None, visn: str | None) -> list[str]:
        """Build tags list.

        Args:
            grant_id: SSVF grant identifier
            visn: VA Integrated Service Network

        Returns:
            List of tag strings.
        """
        tags = [
            "ssvf",
            "housing",
            "homeless-services",
            "rapid-rehousing",
            "veteran-families",
        ]

        if grant_id:
            tags.append(f"grant-{grant_id}")

        # Extract VISN number if present
        if visn:
            # VISN format: "VISN 20: Northwest Network"
            visn_parts = visn.split(":")
            if visn_parts:
                visn_id = visn_parts[0].strip().lower().replace(" ", "-")
                tags.append(visn_id)

        return tags
