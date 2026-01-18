"""HUD-VASH (HUD-VA Supportive Housing) 2024 awards data connector.

Imports HUD-VASH voucher awards by Public Housing Authority (PHA) linked to
VA Medical Centers (VAMCs). This data helps veterans find local housing
voucher resources.

Source: HUD PIH Notice 2024-18
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Map of state abbreviations in PHA codes
STATE_CODES = {
    "AL": "Alabama",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "FL": "Florida",
    "GA": "Georgia",
    "GQ": "Guam",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "NC": "North Carolina",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "SC": "South Carolina",
    "TN": "Tennessee",
    "TX": "Texas",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
}


class HUDVASHConnector(BaseConnector):
    """Connector for HUD-VASH 2024 voucher awards data.

    Parses the HUD-VASH awards JSON file containing PHA-to-VAMC partnerships
    for housing vouchers awarded to homeless veterans.

    Data fields:
        - pha_code: Public Housing Authority code (e.g., CA004)
        - pha_name: PHA organization name
        - vamc: VA Medical Center name with VISN prefix
        - vouchers: Number of HUD-VASH vouchers awarded
        - budget: Budget authority awarded in dollars
    """

    # Path to the HUD-VASH data file relative to project root
    DEFAULT_DATA_PATH = "data/reference/HUD_VASH_2024_Awards.json"

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
            name="HUD-VASH 2024 Voucher Awards",
            url="https://www.hud.gov/program_offices/public_indian_housing/programs/hcv/vash",
            tier=1,  # Official HUD/VA program data
            frequency="yearly",  # Updated with annual awards
            terms_url="https://www.hud.gov/program_offices/public_indian_housing/programs/hcv/vash",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse HUD-VASH awards data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"HUD-VASH data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for award in data.get("awards", []):
            candidate = self._parse_award(
                pha_code=award.get("pha_code"),
                pha_name=award.get("pha_name"),
                vamc=award.get("vamc"),
                vouchers=award.get("vouchers"),
                budget=award.get("budget"),
                fetched_at=now,
            )
            resources.append(candidate)

        return resources

    def _parse_award(
        self,
        pha_code: str | None,
        pha_name: str | None,
        vamc: str | None,
        vouchers: int | None,
        budget: int | float | None,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse an award entry into a ResourceCandidate.

        Args:
            pha_code: Public Housing Authority code
            pha_name: PHA organization name
            vamc: VA Medical Center with VISN prefix
            vouchers: Number of vouchers awarded
            budget: Budget authority awarded
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this HUD-VASH partnership.
        """
        # Extract state from PHA code (first 2 characters)
        state = self._extract_state(pha_code)

        # Parse VAMC info
        visn, vamc_name = self._parse_vamc(vamc)

        # Build title
        title = self._build_title(pha_name, vamc_name, state)

        # Build description
        description = self._build_description(
            pha_name, vamc_name, state, vouchers, budget
        )

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://www.hud.gov/program_offices/public_indian_housing/programs/hcv/vash",
            org_name=pha_name or "Unknown PHA",
            org_website=None,
            categories=["housing"],
            tags=self._build_tags(pha_code, visn, vamc_name),
            eligibility=(
                "Homeless veterans or veterans at risk of homelessness. Must be "
                "eligible for VA health care. Income must be at or below 80% of Area "
                "Median Income (AMI). Veterans must have served on active duty and "
                "received an other than dishonorable discharge."
            ),
            how_to_apply=(
                "Contact your local VA Medical Center and ask for the HUD-VASH "
                "coordinator, or call the National Call Center for Homeless Veterans "
                "at 1-877-4AID-VET (1-877-424-3838). You can also contact the local "
                "Public Housing Authority directly to inquire about HUD-VASH vouchers."
            ),
            scope="local",
            state=state,
            states=[state] if state else None,
            raw_data={
                "pha_code": pha_code,
                "pha_name": pha_name,
                "vamc": vamc,
                "vouchers": vouchers,
                "budget": budget,
            },
            fetched_at=fetched_at,
        )

    def _extract_state(self, pha_code: str | None) -> str | None:
        """Extract state code from PHA code.

        Args:
            pha_code: PHA code like "CA004" or "TX901"

        Returns:
            Two-letter state code or None.
        """
        if not pha_code or len(pha_code) < 2:
            return None
        state = pha_code[:2].upper()
        return state if state in STATE_CODES else None

    def _parse_vamc(self, vamc: str | None) -> tuple[str | None, str | None]:
        """Parse VAMC string into VISN and name.

        Args:
            vamc: VAMC string like "V22/Phoenix" or "V21/Northern California HCS"

        Returns:
            Tuple of (visn, vamc_name).
        """
        if not vamc:
            return None, None

        parts = vamc.split("/", 1)
        if len(parts) == 2:
            visn = parts[0].strip()
            vamc_name = parts[1].strip()
            return visn, vamc_name
        return None, vamc

    def _build_title(
        self,
        pha_name: str | None,
        vamc_name: str | None,
        state: str | None,
    ) -> str:
        """Build resource title.

        Args:
            pha_name: PHA organization name
            vamc_name: VAMC name
            state: State code

        Returns:
            Formatted title string.
        """
        if vamc_name and state:
            return f"HUD-VASH - {vamc_name} ({state})"
        elif pha_name and state:
            return f"HUD-VASH - {pha_name} ({state})"
        elif vamc_name:
            return f"HUD-VASH - {vamc_name}"
        elif pha_name:
            return f"HUD-VASH - {pha_name}"
        return "HUD-VASH Housing Voucher Program"

    def _build_description(
        self,
        pha_name: str | None,
        vamc_name: str | None,
        state: str | None,
        vouchers: int | None,
        budget: int | float | None,
    ) -> str:
        """Build resource description.

        Args:
            pha_name: PHA organization name
            vamc_name: VAMC name
            state: State code
            vouchers: Number of vouchers
            budget: Budget amount

        Returns:
            Formatted description string.
        """
        parts = []

        # Main description
        state_name = STATE_CODES.get(state, state) if state else "your area"
        parts.append(
            f"HUD-VASH (HUD-VA Supportive Housing) provides housing vouchers to "
            f"homeless veterans in {state_name}."
        )

        # PHA info
        if pha_name:
            parts.append(
                f"This program is administered by {pha_name} in partnership with the VA."
            )

        # VAMC info
        if vamc_name:
            parts.append(
                f"Veterans receive case management services through {vamc_name}."
            )

        # Award info
        if vouchers:
            voucher_str = f"{vouchers:,}"
            if budget:
                budget_str = f"${budget:,.0f}"
                parts.append(
                    f"2024 award: {voucher_str} vouchers ({budget_str} budget authority)."
                )
            else:
                parts.append(f"2024 award: {voucher_str} vouchers.")

        # Services
        parts.append(
            "HUD-VASH combines Housing Choice Voucher rental assistance with VA "
            "supportive services including case management, mental health treatment, "
            "and substance use counseling."
        )

        return " ".join(parts)

    def _build_tags(
        self,
        pha_code: str | None,
        visn: str | None,
        vamc_name: str | None,
    ) -> list[str]:
        """Build tags list.

        Args:
            pha_code: PHA code
            visn: VISN identifier
            vamc_name: VAMC name

        Returns:
            List of tag strings.
        """
        tags = [
            "hud-vash",
            "housing-voucher",
            "housing",
            "homeless-services",
            "rental-assistance",
        ]

        if pha_code:
            tags.append(f"pha-{pha_code.lower()}")

        if visn:
            # Normalize VISN to lowercase, e.g., "V22" -> "visn-22"
            visn_normalized = visn.lower().replace("v", "visn-")
            tags.append(visn_normalized)

        if vamc_name:
            # Create slug from VAMC name
            vamc_slug = vamc_name.lower().replace(" ", "-").replace("/", "-")
            vamc_slug = "".join(c for c in vamc_slug if c.isalnum() or c == "-")
            tags.append(f"vamc-{vamc_slug}")

        return tags
