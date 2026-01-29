"""Veteran Emergency Financial Assistance Programs connector.

Imports curated data about emergency financial assistance programs for veterans
in crisis (eviction, utility shutoff, medical emergencies). Consolidates data
from major VSO and nonprofit programs providing rapid assistance.

Programs included:
- VFW Unmet Needs Program
- American Legion Temporary Financial Assistance (TFA)
- DAV Disaster Relief Program
- Operation Homefront Critical Financial Assistance
- Semper Fi & America's Fund
- PenFed Foundation Military Heroes Fund
- USA Cares Military Assistance Response Program
- DVNF GPS (Grants for Patriots and Supporters) Program

Source: Curated from official program websites and VA resources
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class VeteranEmergencyAssistanceConnector(BaseConnector):
    """Connector for veteran emergency financial assistance programs.

    Loads curated data about national programs that provide rapid financial
    assistance to veterans facing immediate hardship such as eviction,
    utility shutoff, or medical emergencies.

    These are tier 2 (established nonprofits) programs that complement
    official VA resources.
    """

    # Data file path relative to project root
    DATA_PATH = "data/reference/veteran_emergency_assistance.json"

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
            name="Veteran Emergency Financial Assistance Programs",
            url="https://www.va.gov/resources/how-to-get-help-from-a-veteran-service-organization/",
            tier=2,  # Established nonprofits (VFW, Legion, DAV, etc.)
            frequency="monthly",  # Programs change infrequently
            terms_url=None,
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse and return emergency assistance programs.

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
            ResourceCandidate for this emergency assistance program.
        """
        org_name = program.get("org_name", "Unknown Organization")
        program_name = program.get("program_name", "Emergency Assistance")
        website = program.get("website")
        phone = program.get("phone")
        email = program.get("email")

        title = self._build_title(org_name, program_name)
        description = self._build_description(program)
        eligibility = self._build_eligibility(program)
        how_to_apply = self._build_how_to_apply(program)
        tags = self._build_tags(program)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website or "https://www.va.gov/resources/",
            org_name=org_name,
            org_website=website,
            categories=self._get_categories(program),
            tags=tags,
            phone=self._normalize_phone(phone),
            email=email,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="national",
            states=None,  # National programs
            raw_data=program,
            fetched_at=fetched_at,
        )

    def _build_title(self, org_name: str, program_name: str) -> str:
        """Build resource title."""
        # For well-known orgs, use abbreviation
        abbrevs = {
            "Veterans of Foreign Wars (VFW)": "VFW",
            "The American Legion": "American Legion",
            "Disabled American Veterans (DAV)": "DAV",
            "Semper Fi & America's Fund": "Semper Fi Fund",
        }
        org_short = abbrevs.get(org_name, org_name)
        return f"{org_short} - {program_name}"

    def _build_description(self, program: dict) -> str:
        """Build resource description with key program details."""
        parts = []

        org_name = program.get("org_name", "This organization")
        program_name = program.get("program_name", "")

        # Opening description
        parts.append(
            f"{org_name}'s {program_name} provides emergency financial assistance "
            "to veterans and military families facing immediate hardship."
        )

        # Assistance types
        assistance_types = program.get("assistance_types", [])
        if assistance_types:
            readable_types = self._format_assistance_types(assistance_types)
            parts.append(f"The program can help with: {readable_types}.")

        # Max amount
        max_amount = program.get("max_amount")
        max_notes = program.get("max_amount_notes")
        if max_amount:
            parts.append(f"Grants up to ${max_amount:,} are available.")
        elif max_notes:
            parts.append(max_notes)

        # Turnaround time
        turnaround = program.get("turnaround_time")
        if turnaround:
            parts.append(f"Typical response time: {turnaround}.")

        # Key differentiator based on org
        org_name_lower = org_name.lower()
        if "vfw" in org_name_lower:
            parts.append(
                "Grants are paid directly to creditors with no repayment required. "
                "VFW membership is not required to apply."
            )
        elif "legion" in org_name_lower:
            parts.append(
                "This program focuses on supporting the minor children of veterans "
                "and service members during financial hardship."
            )
        elif "dav" in org_name_lower:
            parts.append(
                "DAV provides disaster relief to veterans affected by hurricanes, "
                "tornadoes, floods, fires, and other natural disasters."
            )
        elif "operation homefront" in org_name_lower:
            parts.append(
                "Professional caseworkers validate needs before providing support. "
                "Assistance is provided as grants, not loans."
            )
        elif "semper fi" in org_name_lower:
            parts.append(
                "The Fund provides one-on-one case management and lifetime support "
                "to combat wounded, critically ill, and catastrophically injured service members."
            )
        elif "penfed" in org_name_lower:
            parts.append(
                "The program can cover up to 3 months of delinquent payments. "
                "Payments are made directly to creditors after approval."
            )
        elif "usa cares" in org_name_lower:
            parts.append(
                "Each family is assigned an advocate who ensures timely assistance. No fees or repayment required."
            )
        elif "dvnf" in org_name_lower or "disabled veterans national" in org_name_lower:
            parts.append(
                "DVNF provides emergency grants to help veterans and their families "
                "facing immediate financial crisis. No membership required."
            )

        return " ".join(parts)

    def _format_assistance_types(self, types: list[str]) -> str:
        """Format assistance types into readable list."""
        type_labels = {
            "mortgage": "mortgage payments",
            "rent": "rent",
            "utilities": "utilities",
            "auto_payment": "auto payments",
            "auto_repair": "auto repairs",
            "vehicle_payment": "vehicle payments",
            "food": "food assistance",
            "clothing": "clothing",
            "medical_bills": "medical bills",
            "medical": "medical expenses",
            "medical_child": "children's medical care",
            "dental": "dental care",
            "dental_child": "children's dental care",
            "prescriptions": "prescriptions",
            "medications_child": "children's medications",
            "childcare": "childcare",
            "baby_items": "baby items",
            "educational": "educational expenses",
            "home_repairs": "home repairs",
            "home_modifications": "home modifications",
            "transportation": "transportation",
            "travel": "travel expenses",
            "lodging": "lodging",
            "moving": "moving/relocation",
            "vision": "vision care",
            "security_deposits": "security deposits",
            "rental_deposits": "rental deposits",
            "disaster_relief": "disaster relief",
            "shelter": "temporary shelter",
            "basic_necessities": "basic necessities",
        }

        readable = []
        for t in types[:8]:  # Limit to avoid overly long lists
            readable.append(type_labels.get(t, t.replace("_", " ")))

        if len(types) > 8:
            readable.append("and more")

        return ", ".join(readable)

    def _build_eligibility(self, program: dict) -> str:
        """Build eligibility description."""
        eligibility = program.get("eligibility", {})
        parts = []

        # Main eligibility summary
        summary = eligibility.get("summary")
        if summary:
            parts.append(summary)

        # Membership requirement
        if eligibility.get("membership_required"):
            membership_notes = eligibility.get("membership_notes")
            if membership_notes:
                parts.append(membership_notes)
            else:
                parts.append(f"Membership in {program.get('org_name', 'the organization')} is required.")
        elif eligibility.get("membership_required") is False:
            parts.append("No membership required to apply.")

        # Service era
        service_era = eligibility.get("service_era")
        if service_era and service_era != "any":
            parts.append(f"Service era: {service_era}.")

        # Disability requirement
        if eligibility.get("disability_required"):
            disability_notes = eligibility.get("disability_notes")
            if disability_notes:
                parts.append(disability_notes)
            else:
                parts.append("Must have a service-connected disability or injury.")

        # Additional notes
        notes = eligibility.get("notes")
        if notes:
            parts.append(notes)

        return " ".join(parts) if parts else "Contact the organization for eligibility requirements."

    def _build_how_to_apply(self, program: dict) -> str:
        """Build application instructions."""
        parts = []

        # Application process
        process = program.get("application_process")
        if process:
            parts.append(process)

        # Phone
        phone = program.get("phone")
        if phone:
            parts.append(f"Phone: {phone}")

        # Email
        email = program.get("email")
        if email:
            parts.append(f"Email: {email}")

        # Website
        website = program.get("website")
        if website:
            parts.append(f"Website: {website}")

        # If no specific process, provide generic guidance
        if not parts:
            parts.append("Contact the organization through their website to begin the application process.")

        return " ".join(parts)

    def _get_categories(self, program: dict) -> list[str]:
        """Determine categories based on assistance types."""
        assistance_types = program.get("assistance_types", [])

        # All emergency assistance programs are financial by nature
        categories = {"financial"}

        # Housing-related assistance
        housing_keywords = {
            "mortgage",
            "rent",
            "shelter",
            "home_repairs",
            "home_modifications",
            "security_deposits",
            "rental_deposits",
        }
        if housing_keywords & set(assistance_types):
            categories.add("housing")

        # Legal assistance (none of these programs, but for completeness)
        legal_keywords = {"legal", "legal_aid"}
        if legal_keywords & set(assistance_types):
            categories.add("legal")

        return sorted(categories)

    def _build_tags(self, program: dict) -> list[str]:
        """Build tags list."""
        tags = [
            "emergency-assistance",
            "financial-assistance",
            "crisis-support",
        ]

        assistance_types = program.get("assistance_types", [])

        # Add tags based on assistance types
        if "mortgage" in assistance_types or "rent" in assistance_types:
            tags.append("housing-assistance")
        if "utilities" in assistance_types:
            tags.append("utility-assistance")
        if "food" in assistance_types:
            tags.append("food-assistance")
        if any(t in assistance_types for t in ["medical", "medical_bills", "prescriptions"]):
            tags.append("medical-assistance")
        if "disaster_relief" in assistance_types:
            tags.append("disaster-relief")
        if any(t in assistance_types for t in ["auto_payment", "auto_repair", "vehicle_payment"]):
            tags.append("transportation-assistance")

        # Add tags based on eligibility
        eligibility = program.get("eligibility", {})
        service_era = eligibility.get("service_era", "")
        if "post-9/11" in service_era.lower():
            tags.append("post-9/11")
        if eligibility.get("disability_required"):
            tags.append("disabled-veterans")

        # Add org-specific tags
        org_name = program.get("org_name", "").lower()
        if "vfw" in org_name:
            tags.append("vfw")
        elif "legion" in org_name:
            tags.append("american-legion")
        elif "dav" in org_name:
            tags.append("dav")
        elif "operation homefront" in org_name:
            tags.append("operation-homefront")
        elif "semper fi" in org_name:
            tags.append("semper-fi-fund")
        elif "penfed" in org_name:
            tags.append("penfed-foundation")
        elif "usa cares" in org_name:
            tags.append("usa-cares")
        elif "dvnf" in org_name or "disabled veterans national" in org_name:
            tags.append("dvnf")

        return tags
