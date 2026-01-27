"""Veteran Food Assistance Programs connector.

Imports curated data about food assistance programs for veterans and military
families - pantries, distributions, meal programs. Consolidates data from
national organizations and local programs.

Programs included:
- Soldiers' Angels Military and Veteran Food Distribution
- Disabled Veterans National Foundation (DVNF) Veterans Food Assistance
- Armed Services YMCA food programs
- VFW food pantries
- Regional food banks with veteran programs
- VA Food Security Office resources

Source: Curated from official program websites and VA resources
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class VeteranFoodAssistanceConnector(BaseConnector):
    """Connector for veteran food assistance programs.

    Loads curated data about food pantries, distributions, and meal programs
    that serve veterans and military families.

    These are tier 2 (established nonprofits) and tier 4 (community) programs
    that help combat food insecurity among veterans.
    """

    # Data file path relative to project root
    DATA_PATH = "data/reference/veteran_food_assistance.json"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to data JSON. Falls back to DATA_PATH.
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
            name="Veteran Food Assistance Programs",
            url="https://www.nutrition.va.gov/food_insecurity.asp",
            tier=2,  # Mix of established nonprofits and community programs
            frequency="monthly",  # Programs change infrequently
            terms_url=None,
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse and return food assistance programs.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        now = datetime.now(UTC)

        data = self._load_data()
        if not data:
            return []

        resources: list[ResourceCandidate] = []

        for program in data.get("programs", []):
            candidate = self._parse_program(program, fetched_at=now)
            resources.append(candidate)

        return resources

    def _load_data(self) -> dict:
        """Load program data from JSON file."""
        if not self.data_path.exists():
            return {}

        with open(self.data_path) as f:
            return json.load(f)

    def _parse_program(
        self,
        program: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a program entry into a ResourceCandidate.

        Args:
            program: Dictionary containing program data.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this food assistance program.
        """
        org_name = program.get("org_name", "Unknown Organization")
        program_name = program.get("program_name", "Food Assistance")
        website = program.get("website")
        phone = program.get("phone")
        email = program.get("email")
        hours = program.get("hours")

        # Location info
        address = program.get("address")
        city = program.get("city")
        state = program.get("state")
        zip_code = program.get("zip_code")

        title = self._build_title(org_name, program_name)
        description = self._build_description(program)
        eligibility = self._build_eligibility(program)
        how_to_apply = self._build_how_to_apply(program)
        tags = self._build_tags(program)

        # Determine scope
        scope = program.get("scope", "local")
        states = program.get("states")

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website or "https://www.nutrition.va.gov/food_insecurity.asp",
            org_name=org_name,
            org_website=website,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["housing"],  # Food insecurity often tied to housing needs
            tags=tags,
            phone=self._normalize_phone(phone),
            email=email,
            hours=self._format_hours(hours),
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope=scope,
            states=states,
            raw_data=program,
            fetched_at=fetched_at,
        )

    def _build_title(self, org_name: str, program_name: str) -> str:
        """Build resource title."""
        # Use common abbreviations for well-known organizations
        abbrevs = {
            "Soldiers' Angels": "Soldiers' Angels",
            "Disabled Veterans National Foundation (DVNF)": "DVNF",
            "Armed Services YMCA Hawaii": "ASYMCA Hawaii",
            "ASYMCA Fort Bragg": "ASYMCA Fort Liberty",
            "VFW Post 10054": "VFW",
            "VFW Department of Missouri": "VFW Missouri",
            "VA Food Security Office": "VA",
        }
        org_short = abbrevs.get(org_name, org_name)
        return f"{org_short} - {program_name}"

    def _build_description(self, program: dict) -> str:
        """Build resource description with key program details."""
        parts = []

        org_name = program.get("org_name", "This organization")
        program_name = program.get("program_name", "")

        # Opening description
        parts.append(f"{org_name}'s {program_name} provides food assistance to veterans and military families.")

        # Services offered
        services = program.get("services", [])
        if services:
            readable_services = self._format_services(services)
            parts.append(f"Services include: {readable_services}.")

        # Distribution cities for national programs
        distribution_cities = program.get("distribution_cities", [])
        if distribution_cities:
            city_names = [f"{c['city']}, {c['state']}" for c in distribution_cities[:5]]
            if len(distribution_cities) > 5:
                city_names.append(f"and {len(distribution_cities) - 5} more cities")
            parts.append(f"Locations: {'; '.join(city_names)}.")

        # Hours
        hours = program.get("hours")
        if hours:
            parts.append(f"Hours: {hours}.")

        # Additional context from eligibility notes
        eligibility = program.get("eligibility", {})
        notes = eligibility.get("notes")
        if notes and "pounds" in notes.lower():
            # Include quantity info if present
            parts.append(notes)

        return " ".join(parts)

    def _format_services(self, services: list[str]) -> str:
        """Format services into readable list."""
        service_labels = {
            "monthly_food_distribution": "monthly food distributions",
            "fresh_produce": "fresh produce",
            "meat": "meat",
            "non_perishables": "non-perishable items",
            "holiday_meals": "holiday meals",
            "grocery_delivery": "grocery delivery",
            "household_supplies": "household supplies",
            "one_time_grant": "one-time food grants",
            "dried_goods": "dried goods",
            "client_choice_pantry": "client-choice pantry",
            "milk": "milk",
            "eggs": "eggs",
            "cheese": "cheese",
            "pantry_staples": "pantry staples",
            "twelve_month_groceries": "12-month grocery program",
            "monthly_food_boxes": "monthly food boxes",
            "case_management": "case management",
            "dry_goods": "dry goods",
            "mobile_pantry": "mobile pantry",
            "food_pantry": "food pantry",
            "canned_goods": "canned goods",
            "military_family_support": "military family support",
            "mobile_food_market": "mobile food market",
            "produce_prescriptions": "produce prescriptions",
            "snap_referrals": "SNAP enrollment assistance",
            "food_bank_referrals": "food bank referrals",
            "nutrition_counseling": "nutrition counseling",
        }

        readable = []
        for s in services[:6]:  # Limit to avoid overly long lists
            readable.append(service_labels.get(s, s.replace("_", " ")))

        if len(services) > 6:
            readable.append("and more")

        return ", ".join(readable)

    def _format_hours(self, hours: str | None) -> str | None:
        """Format hours string, ensuring consistency."""
        if not hours:
            return None
        # Return as-is since our data is already well-formatted
        return hours

    def _build_eligibility(self, program: dict) -> str:
        """Build eligibility description."""
        eligibility = program.get("eligibility", {})
        parts = []

        # Main eligibility summary
        summary = eligibility.get("summary")
        if summary:
            parts.append(summary)

        # Veteran status requirement
        if eligibility.get("veteran_status_required") is True:
            # Already covered in summary typically
            pass
        elif eligibility.get("veteran_status_required") is False:
            parts.append("Open to active duty service members and their families.")

        # Income limit
        income_limit = eligibility.get("income_limit")
        if income_limit and income_limit != "Based on need":
            parts.append(f"Income requirement: {income_limit}.")

        # Documentation required
        docs = eligibility.get("documentation_required", [])
        if docs:
            doc_labels = {
                "military_id": "military ID",
                "dd214": "DD-214",
                "va_card": "VA card",
                "veteran_id": "veteran ID",
                "state_id": "state ID",
                "recommendation_letter": "recommendation letter",
                "va_enrollment": "VA healthcare enrollment",
            }
            doc_names = [doc_labels.get(d, d) for d in docs]
            if doc_names:
                parts.append(f"Required documentation: {', '.join(doc_names)}.")

        # Additional notes
        notes = eligibility.get("notes")
        if notes and "pounds" not in notes.lower():  # Avoid duplicating quantity info
            parts.append(notes)

        return " ".join(parts) if parts else "Contact the organization for eligibility requirements."

    def _build_how_to_apply(self, program: dict) -> str:
        """Build application instructions."""
        parts = []

        # Location info
        address = program.get("address")
        city = program.get("city")
        state = program.get("state")
        zip_code = program.get("zip_code")

        if address and city:
            addr_parts = [address, city]
            if state:
                addr_parts.append(state)
            if zip_code:
                addr_parts.append(zip_code)
            parts.append(f"Location: {', '.join(addr_parts)}.")

        # Hours
        hours = program.get("hours")
        if hours:
            parts.append(f"Hours: {hours}.")

        # Phone
        phone = program.get("phone")
        if phone:
            parts.append(f"Phone: {phone}.")

        # Email
        email = program.get("email")
        if email:
            parts.append(f"Email: {email}.")

        # Website
        website = program.get("website")
        if website:
            parts.append(f"Website: {website}")

        # If no specific info, provide generic guidance
        if not parts:
            parts.append(
                "Contact the organization through their website to learn about "
                "food distribution schedules and registration requirements."
            )

        return " ".join(parts)

    def _build_tags(self, program: dict) -> list[str]:
        """Build tags list."""
        tags = [
            "food-assistance",
            "food-insecurity",
            "veteran-services",
        ]

        services = program.get("services", [])

        # Add tags based on services
        if "food_pantry" in services or "client_choice_pantry" in services:
            tags.append("food-pantry")
        if "monthly_food_distribution" in services or "mobile_pantry" in services:
            tags.append("food-distribution")
        if "fresh_produce" in services:
            tags.append("fresh-produce")
        if "grocery_delivery" in services:
            tags.append("grocery-delivery")
        if "mobile_pantry" in services or "mobile_food_market" in services:
            tags.append("mobile-pantry")
        if "snap_referrals" in services:
            tags.append("snap")
        if "produce_prescriptions" in services:
            tags.append("produce-rx")
        if "twelve_month_groceries" in services:
            tags.append("long-term-support")
        if "holiday_meals" in services:
            tags.append("holiday-meals")

        # Add org-specific tags
        org_name = program.get("org_name", "").lower()
        if "soldiers' angels" in org_name:
            tags.append("soldiers-angels")
        elif "dvnf" in org_name or "disabled veterans national" in org_name:
            tags.append("dvnf")
        elif "asymca" in org_name or "armed services ymca" in org_name:
            tags.append("asymca")
        elif "vfw" in org_name:
            tags.append("vfw")
        elif "va food security" in org_name:
            tags.append("va")

        # Add scope tags
        scope = program.get("scope", "local")
        if scope == "national":
            tags.append("nationwide")
        elif scope == "state":
            states = program.get("states", [])
            if states and len(states) == 1:
                tags.append(states[0].lower())

        return tags
