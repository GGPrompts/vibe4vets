"""Feeding America Food Bank Network connector.

Imports data about 200+ member food banks in the Feeding America network.
Food banks provide food assistance to veterans and their families.

Source: https://www.feedingamerica.org/find-your-local-foodbank
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class FeedingAmericaConnector(BaseConnector):
    """Connector for Feeding America member food banks.

    Feeding America is the nation's largest domestic hunger-relief organization,
    with a network of 200 food banks serving every state, the District of Columbia,
    and Puerto Rico. These food banks partner with 60,000+ food pantries and meal
    programs to provide food to people in need.

    Food banks serve as regional distribution centers, sourcing food from farmers,
    manufacturers, and retailers to distribute to local food pantries and meal
    programs in their service areas.

    This connector focuses on the 200 member food banks (not the 60,000 pantries).
    Veterans and military families can access food assistance through these food
    banks or their partner agencies.
    """

    # Path to the data file relative to project root
    DATA_PATH = "data/reference/feeding_america_foodbanks.json"

    # State code mapping for extracting state from food bank names
    STATE_PATTERNS = {
        "alabama": "AL",
        "alaska": "AK",
        "arizona": "AZ",
        "arkansas": "AR",
        "california": "CA",
        "colorado": "CO",
        "connecticut": "CT",
        "delaware": "DE",
        "florida": "FL",
        "georgia": "GA",
        "hawaii": "HI",
        "idaho": "ID",
        "illinois": "IL",
        "indiana": "IN",
        "iowa": "IA",
        "kansas": "KS",
        "kentucky": "KY",
        "louisiana": "LA",
        "maine": "ME",
        "maryland": "MD",
        "massachusetts": "MA",
        "michigan": "MI",
        "minnesota": "MN",
        "mississippi": "MS",
        "missouri": "MO",
        "montana": "MT",
        "nebraska": "NE",
        "nevada": "NV",
        "new hampshire": "NH",
        "new jersey": "NJ",
        "new mexico": "NM",
        "new york": "NY",
        "north carolina": "NC",
        "north dakota": "ND",
        "ohio": "OH",
        "oklahoma": "OK",
        "oregon": "OR",
        "pennsylvania": "PA",
        "puerto rico": "PR",
        "rhode island": "RI",
        "south carolina": "SC",
        "south dakota": "SD",
        "tennessee": "TN",
        "texas": "TX",
        "utah": "UT",
        "vermont": "VT",
        "virginia": "VA",
        "washington": "WA",
        "west virginia": "WV",
        "wisconsin": "WI",
        "wyoming": "WY",
    }

    # Region patterns for extracting state from regional names
    REGION_STATE_MAP = {
        "atlanta": "GA",
        "boston": "MA",
        "chicago": "IL",
        "cleveland": "OH",
        "houston": "TX",
        "los angeles": "CA",
        "san antonio": "TX",
        "san diego": "CA",
        "san francisco": "CA",
        "tampa": "FL",
        "baton rouge": "LA",
        "pittsburgh": "PA",
        "akron": "OH",
        "toledo": "OH",
        "wichita": "KS",
        "fresno": "CA",
        "sacramento": "CA",
        "chattanooga": "TN",
        "memphis": "TN",
        "el paso": "TX",
        "austin": "TX",
        "dallas": "TX",
        "fort worth": "TX",
        "lansing": "MI",
        "ann arbor": "MI",
        "detroit": "MI",
        "dayton": "OH",
        "cincinnati": "OH",
        "columbus": "OH",
        "indianapolis": "IN",
        "louisville": "KY",
        "lexington": "KY",
        "nashville": "TN",
        "knoxville": "TN",
        "charlotte": "NC",
        "raleigh": "NC",
        "greensboro": "NC",
        "richmond": "VA",
        "norfolk": "VA",
        "baltimore": "MD",
        "philadelphia": "PA",
        "allentown": "PA",
        "erie": "PA",
        "rochester": "NY",
        "buffalo": "NY",
        "albany": "NY",
        "syracuse": "NY",
        "portland": "OR",  # Could be ME too, but OR is more common
        "seattle": "WA",
        "spokane": "WA",
        "phoenix": "AZ",
        "tucson": "AZ",
        "albuquerque": "NM",
        "denver": "CO",
        "salt lake": "UT",
        "las vegas": "NV",
        "reno": "NV",
        "minneapolis": "MN",
        "st. paul": "MN",
        "st paul": "MN",
        "st louis": "MO",
        "st. louis": "MO",
        "kansas city": "MO",
        "omaha": "NE",
        "lincoln": "NE",
        "des moines": "IA",
        "milwaukee": "WI",
        "madison": "WI",
        "peoria": "IL",
        "springfield": "IL",
        "orange county": "CA",
        "silicon valley": "CA",
        "monmouth": "NJ",
        "ocean": "NJ",
        "long island": "NY",
        "westchester": "NY",
        "terre haute": "IN",
        "fredericksburg": "VA",
        "mahoning valley": "OH",
        "lehigh valley": "PA",
        "metrolina": "NC",
        "gulf coast": "AL",  # Could be MS or AL
        "rio grande": "TX",
        "big bend": "FL",
        "heartland": "NE",
    }

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to JSON data file. Falls back to DATA_PATH.
        """
        root = self._find_project_root()
        self.data_path = Path(data_path) if data_path else root / self.DATA_PATH

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
            name="Feeding America Food Bank Network",
            url="https://www.feedingamerica.org/find-your-local-foodbank",
            tier=2,  # Major national nonprofit network
            frequency="monthly",  # Network changes infrequently
            terms_url="https://www.feedingamerica.org/about-us/terms",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse and return food bank resources.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        now = datetime.now(UTC)

        data = self._load_data()
        if not data:
            return []

        resources: list[ResourceCandidate] = []

        for food_bank in data.get("food_banks", []):
            candidate = self._parse_food_bank(food_bank, fetched_at=now)
            resources.append(candidate)

        return resources

    def _load_data(self) -> dict:
        """Load food bank data from JSON file."""
        if not self.data_path.exists():
            return {}

        with open(self.data_path) as f:
            return json.load(f)

    def _parse_food_bank(
        self,
        food_bank: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a food bank entry into a ResourceCandidate.

        Args:
            food_bank: Dictionary containing food bank data.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this food bank.
        """
        name = food_bank.get("name", "Unknown Food Bank")
        slug = food_bank.get("slug", "")
        website = food_bank.get("website")
        phone = food_bank.get("phone")
        email = food_bank.get("email")

        # Location info
        address = food_bank.get("address")
        city = food_bank.get("city")
        state = food_bank.get("state") or self._extract_state(name, slug)
        zip_code = food_bank.get("zip_code")

        # Service area
        counties = food_bank.get("counties", [])
        service_area = food_bank.get("service_area")

        title = f"Feeding America - {name}"
        description = self._build_description(
            name, state, counties, service_area
        )
        eligibility = self._build_eligibility()
        how_to_apply = self._build_how_to_apply(name, website, phone, slug)
        tags = self._build_tags(name, state, counties)

        # Build source URL from slug if available
        source_url = (
            f"https://www.feedingamerica.org/find-your-local-foodbank/{slug}"
            if slug
            else "https://www.feedingamerica.org/find-your-local-foodbank"
        )

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name=name,
            org_website=website,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["food"],
            tags=tags,
            phone=self._normalize_phone(phone),
            email=email,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="regional",  # Food banks serve multi-county regions
            states=[state] if state else None,
            raw_data={
                "slug": slug,
                "counties": counties,
                "service_area": service_area,
                "network": "Feeding America",
            },
            fetched_at=fetched_at,
        )

    def _extract_state(self, name: str, slug: str) -> str | None:
        """Extract state code from food bank name or slug.

        Args:
            name: Food bank name.
            slug: URL slug.

        Returns:
            Two-letter state code or None.
        """
        name_lower = name.lower()
        slug_lower = slug.lower()

        # Check for state name patterns
        for state_name, code in self.STATE_PATTERNS.items():
            if state_name in name_lower or state_name in slug_lower:
                return code

        # Check for city/region patterns
        for region, code in self.REGION_STATE_MAP.items():
            if region in name_lower or region in slug_lower:
                return code

        return None

    def _build_description(
        self,
        name: str,
        state: str | None,
        counties: list[str],
        service_area: str | None,
    ) -> str:
        """Build resource description.

        Args:
            name: Food bank name.
            state: State code.
            counties: List of counties served.
            service_area: General service area description.

        Returns:
            Formatted description string.
        """
        parts = []

        parts.append(
            f"{name} is a member of Feeding America, the nation's largest "
            "domestic hunger-relief organization."
        )

        # Service area
        if counties:
            county_text = ", ".join(counties[:5])
            if len(counties) > 5:
                county_text += f" and {len(counties) - 5} more"
            parts.append(f"Serves {county_text} counties.")
        elif service_area:
            parts.append(f"Service area: {service_area}.")
        elif state:
            parts.append(f"Serves communities in {state}.")

        parts.append(
            "Food banks collect and distribute food to local food pantries, "
            "soup kitchens, and meal programs. Veterans and military families "
            "can receive food assistance by visiting a local partner agency "
            "or attending a mobile food distribution."
        )

        return " ".join(parts)

    def _build_eligibility(self) -> str:
        """Build eligibility description.

        Returns:
            Eligibility requirements string.
        """
        return (
            "Food assistance is available to anyone in need. Most food pantries "
            "do not require documentation, though some may ask for proof of "
            "residence within their service area. Veterans and military families "
            "are welcome at all Feeding America member food banks. Contact the "
            "food bank or visit their website to find a local food pantry or "
            "distribution event near you."
        )

    def _build_how_to_apply(
        self,
        name: str,
        website: str | None,
        phone: str | None,
        slug: str | None,
    ) -> str:
        """Build application/access instructions.

        Args:
            name: Food bank name.
            website: Food bank website.
            phone: Food bank phone.
            slug: URL slug for Feeding America page.

        Returns:
            How to apply string.
        """
        parts = []

        if website:
            parts.append(
                f"Visit {name}'s website at {website} to find a food pantry "
                "or distribution event near you."
            )
        elif slug:
            parts.append(
                f"Visit https://www.feedingamerica.org/find-your-local-foodbank/{slug} "
                "for information about food assistance."
            )

        if phone:
            parts.append(f"Call {phone} for assistance or to locate services.")

        parts.append(
            "You can also text 'FOOD' to 211 or call 211 to find food assistance "
            "in your area."
        )

        return " ".join(parts)

    def _build_tags(
        self,
        name: str,
        state: str | None,
        counties: list[str],
    ) -> list[str]:
        """Build tags list.

        Args:
            name: Food bank name.
            state: State code.
            counties: List of counties served.

        Returns:
            List of tag strings.
        """
        tags = [
            "food-bank",
            "food-assistance",
            "feeding-america",
            "hunger-relief",
            "food-pantry",
        ]

        # Add state tag
        if state:
            tags.append(f"state-{state.lower()}")

        # Check for special program types in the name
        name_lower = name.lower()
        if "second harvest" in name_lower:
            tags.append("second-harvest")
        if "community" in name_lower:
            tags.append("community-food-bank")
        if "regional" in name_lower:
            tags.append("regional-food-bank")

        return tags
