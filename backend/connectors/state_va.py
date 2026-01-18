"""State VA agency connector.

Imports state veteran affairs agency data from the NASDVA member directory.
Covers all 50 states plus DC and US territories.

Source: NASDVA - National Association of State Directors of Veterans Affairs
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class StateVAConnector(BaseConnector):
    """Connector for state veteran affairs agency data.

    Parses the state_va_agencies.json file containing contact information
    for all state and territory veteran affairs agencies in the US.

    Data fields:
        - state: Two-letter state/territory code
        - state_name: Full state name
        - agency_name: Official agency name
        - director: Current agency director
        - website: Agency website URL
    """

    DEFAULT_DATA_PATH = "data/reference/state_va_agencies.json"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to JSON file. Falls back to DEFAULT_DATA_PATH.
        """
        if data_path is None:
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
            name="State VA Agencies (NASDVA)",
            url="https://nasdva.us/resources/",
            tier=3,  # State-level agencies
            frequency="yearly",
            terms_url="https://nasdva.us/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse state VA agency data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"State VA data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for agency in data.get("agencies", []):
            candidate = self._parse_agency(
                state=agency.get("state"),
                state_name=agency.get("state_name"),
                agency_name=agency.get("agency_name"),
                director=agency.get("director"),
                website=agency.get("website"),
                fetched_at=now,
            )
            resources.append(candidate)

        return resources

    def _parse_agency(
        self,
        state: str | None,
        state_name: str | None,
        agency_name: str | None,
        director: str | None,
        website: str | None,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse an agency entry into a ResourceCandidate.

        Args:
            state: Two-letter state code
            state_name: Full state name
            agency_name: Official agency name
            director: Current director name
            website: Agency website URL
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this state VA agency.
        """
        title = f"{agency_name}" if agency_name else f"{state_name} Veterans Affairs"
        description = self._build_description(state_name, agency_name, director)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website or "https://nasdva.us/resources/",
            org_name=agency_name or f"{state_name} Veterans Affairs",
            org_website=website,
            categories=["employment", "training", "housing", "legal"],
            tags=self._build_tags(state),
            eligibility=(
                f"Veterans residing in {state_name}. State veteran affairs offices "
                "serve all veterans regardless of service era, discharge status, or "
                "VA enrollment. Many state benefits are available to veterans who may "
                "not qualify for federal VA benefits."
            ),
            how_to_apply=(
                f"Visit the {agency_name or (state_name + ' VA') if state_name else 'state VA'} "
                f"website at {website} or contact your local state veterans service office. "
                "State offices can assist with federal VA claims, state-specific benefits, "
                "and connecting you to local resources."
            ),
            scope="state",
            state=state,
            states=[state] if state else None,
            raw_data={
                "state": state,
                "state_name": state_name,
                "agency_name": agency_name,
                "director": director,
                "website": website,
            },
            fetched_at=fetched_at,
        )

    def _build_description(
        self,
        state_name: str | None,
        agency_name: str | None,
        director: str | None,
    ) -> str:
        """Build resource description.

        Args:
            state_name: Full state name
            agency_name: Official agency name
            director: Current director name

        Returns:
            Formatted description string.
        """
        parts = []

        if agency_name and state_name:
            parts.append(
                f"The {agency_name} is the official state agency serving veterans in {state_name}."
            )
        elif state_name:
            parts.append(f"Official state veteran affairs agency serving veterans in {state_name}.")

        parts.append(
            "State veteran affairs offices provide services including: assistance "
            "with federal VA claims, state-specific veteran benefits, employment "
            "assistance, education benefits, housing programs, and referrals to "
            "local veteran service organizations."
        )

        if director:
            parts.append(f"Current Director: {director}.")

        parts.append(
            "State agencies often have field offices throughout the state and can "
            "help veterans navigate both state and federal benefits."
        )

        return " ".join(parts)

    def _build_tags(self, state: str | None) -> list[str]:
        """Build tags list.

        Args:
            state: Two-letter state code

        Returns:
            List of tag strings.
        """
        tags = [
            "state-va",
            "state-benefits",
            "veteran-services",
            "claims-assistance",
            "nasdva",
        ]

        if state:
            tags.append(f"state-{state.lower()}")

        return tags
