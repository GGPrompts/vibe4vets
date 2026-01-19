"""HUD-VASH (HUD-VA Supportive Housing) multi-year awards data connector.

Imports HUD-VASH voucher awards by Public Housing Authority (PHA) linked to
VA Medical Centers (VAMCs). This data helps veterans find local housing
voucher resources.

Supports both:
- Single-year detailed data (2024) with VAMC and budget info
- Multi-year data (2020-2024) for comprehensive PHA coverage

Source: HUD PIH Notices (2020-2024)
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Map of state abbreviations to full names
STATE_CODES = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "GQ": "Guam",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MT": "Montana",
    "NC": "North Carolina",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
}


class HUDVASHConnector(BaseConnector):
    """Connector for HUD-VASH voucher awards data (2020-2024).

    Merges two data sources:
    1. Multi-year data (HUD_VASH_All_Years.json) - 421 PHAs across 46 states
    2. Single-year detailed data (HUD_VASH_2024_Awards.json) - with VAMC/budget info

    This provides comprehensive coverage:
    - More PHAs than single-year data alone
    - Historical award tracking
    - VAMC partnership details where available
    """

    # Data file paths relative to project root
    MULTIYEAR_DATA_PATH = "data/reference/HUD_VASH_All_Years.json"
    SINGLE_YEAR_DATA_PATH = "data/reference/HUD_VASH_2024_Awards.json"

    def __init__(
        self,
        multiyear_path: str | Path | None = None,
        single_year_path: str | Path | None = None,
    ):
        """Initialize the connector.

        Args:
            multiyear_path: Path to multi-year JSON. Falls back to MULTIYEAR_DATA_PATH.
            single_year_path: Path to single-year JSON. Falls back to SINGLE_YEAR_DATA_PATH.
        """
        root = self._find_project_root()
        self.multiyear_path = Path(multiyear_path) if multiyear_path else root / self.MULTIYEAR_DATA_PATH
        self.single_year_path = Path(single_year_path) if single_year_path else root / self.SINGLE_YEAR_DATA_PATH

    def _find_project_root(self) -> Path:
        """Find project root (directory containing 'data' folder)."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / "data").is_dir():
                return current
            current = current.parent
        return Path(__file__).resolve().parent.parent

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="HUD-VASH Voucher Awards (2020-2024)",
            url="https://www.hud.gov/program_offices/public_indian_housing/programs/hcv/vash",
            tier=1,  # Official HUD/VA program data
            frequency="yearly",  # Updated with annual awards
            terms_url="https://www.hud.gov/program_offices/public_indian_housing/programs/hcv/vash",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse and merge HUD-VASH awards data.

        Merges multi-year data with detailed single-year data to provide:
        - Comprehensive PHA coverage (421 PHAs vs 153 in 2024 alone)
        - VAMC partnership details where available
        - Historical award context

        Returns:
            List of normalized ResourceCandidate objects.
        """
        now = datetime.now(UTC)

        # Load multi-year data (primary source for comprehensive coverage)
        multiyear_data = self._load_multiyear_data()

        # Load single-year data for VAMC details
        single_year_lookup = self._load_single_year_lookup()

        resources: list[ResourceCandidate] = []

        for award in multiyear_data.get("awards", []):
            pha_code = award.get("pha_code")

            # Get detailed info from single-year data if available
            detailed = single_year_lookup.get(pha_code, {})

            candidate = self._parse_award(
                pha_code=pha_code,
                pha_name=award.get("pha_name"),
                awards_by_year=award.get("awards_by_year", {}),
                total_vouchers=award.get("total_vouchers", 0),
                vamc=detailed.get("vamc"),
                budget=detailed.get("budget"),
                fetched_at=now,
            )
            resources.append(candidate)

        return resources

    def _load_multiyear_data(self) -> dict:
        """Load multi-year awards data."""
        if not self.multiyear_path.exists():
            # Fall back to single-year if multi-year not available
            return {"awards": []}

        with open(self.multiyear_path) as f:
            return json.load(f)

    def _load_single_year_lookup(self) -> dict[str, dict]:
        """Load single-year data as PHA code lookup for detailed info."""
        if not self.single_year_path.exists():
            return {}

        with open(self.single_year_path) as f:
            data = json.load(f)

        # Create lookup by PHA code
        return {
            award["pha_code"]: award
            for award in data.get("awards", [])
            if "pha_code" in award
        }

    def _parse_award(
        self,
        pha_code: str | None,
        pha_name: str | None,
        awards_by_year: dict[str, int],
        total_vouchers: int,
        vamc: str | None,
        budget: int | float | None,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse an award entry into a ResourceCandidate.

        Args:
            pha_code: Public Housing Authority code
            pha_name: PHA organization name
            awards_by_year: Dict of year -> voucher count
            total_vouchers: Total vouchers across all years
            vamc: VA Medical Center with VISN prefix (from 2024 data)
            budget: Budget authority awarded (from 2024 data)
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this HUD-VASH partnership.
        """
        state = self._extract_state(pha_code)
        visn, vamc_name = self._parse_vamc(vamc)

        title = self._build_title(pha_name, vamc_name, state)
        description = self._build_description(
            pha_name, vamc_name, state, awards_by_year, total_vouchers, budget
        )

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://www.hud.gov/program_offices/public_indian_housing/programs/hcv/vash",
            org_name=pha_name or "Unknown PHA",
            org_website=None,
            categories=["housing"],
            tags=self._build_tags(pha_code, visn, vamc_name, awards_by_year),
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
                "awards_by_year": awards_by_year,
                "total_vouchers": total_vouchers,
                "vamc": vamc,
                "budget": budget,
            },
            fetched_at=fetched_at,
        )

    def _extract_state(self, pha_code: str | None) -> str | None:
        """Extract state code from PHA code."""
        if not pha_code or len(pha_code) < 2:
            return None
        state = pha_code[:2].upper()
        return state if state in STATE_CODES else None

    def _parse_vamc(self, vamc: str | None) -> tuple[str | None, str | None]:
        """Parse VAMC string into VISN and name."""
        if not vamc:
            return None, None

        parts = vamc.split("/", 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return None, vamc

    def _build_title(
        self,
        pha_name: str | None,
        vamc_name: str | None,
        state: str | None,
    ) -> str:
        """Build resource title."""
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
        awards_by_year: dict[str, int],
        total_vouchers: int,
        budget: int | float | None,
    ) -> str:
        """Build resource description with multi-year context."""
        parts = []

        # Main description
        state_name = STATE_CODES.get(state, state) if state else "your area"
        parts.append(
            f"HUD-VASH (HUD-VA Supportive Housing) provides housing vouchers to "
            f"homeless veterans in {state_name}."
        )

        # PHA info
        if pha_name:
            parts.append(f"This program is administered by {pha_name} in partnership with the VA.")

        # VAMC info
        if vamc_name:
            parts.append(f"Veterans receive case management services through {vamc_name}.")

        # Multi-year award summary
        if awards_by_year:
            years = sorted(awards_by_year.keys(), reverse=True)
            recent_years = years[:3]  # Show up to 3 most recent years

            if len(recent_years) == 1:
                year = recent_years[0]
                vouchers = awards_by_year[year]
                if budget:
                    parts.append(f"FY{year} award: {vouchers:,} vouchers (${budget:,.0f} budget authority).")
                else:
                    parts.append(f"FY{year} award: {vouchers:,} vouchers.")
            else:
                year_strs = [f"FY{y}: {awards_by_year[y]:,}" for y in recent_years]
                parts.append(f"Recent awards: {', '.join(year_strs)} vouchers.")

            if total_vouchers > sum(awards_by_year.get(y, 0) for y in recent_years):
                parts.append(f"Total vouchers awarded (2020-2024): {total_vouchers:,}.")

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
        awards_by_year: dict[str, int],
    ) -> list[str]:
        """Build tags list."""
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
            visn_normalized = visn.lower().replace("v", "visn-")
            tags.append(visn_normalized)

        if vamc_name:
            vamc_slug = vamc_name.lower().replace(" ", "-").replace("/", "-")
            vamc_slug = "".join(c for c in vamc_slug if c.isalnum() or c == "-")
            tags.append(f"vamc-{vamc_slug}")

        # Add year tags for recent awards
        for year in sorted(awards_by_year.keys(), reverse=True)[:3]:
            tags.append(f"fy{year}")

        return tags
