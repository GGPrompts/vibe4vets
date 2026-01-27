"""Mental Health Resources connector for veterans.

Imports curated data about mental health resources for veterans including
crisis lines, therapy providers, peer support groups, and community programs.

Resources included:
- Veterans Crisis Line (VA)
- VA Vet Centers (Readjustment Counseling)
- Cohen Veterans Network
- Give an Hour
- The Headstrong Project
- Wounded Warrior Project programs
- Team Red, White & Blue
- Travis Manion Foundation / The Mission Continues
- And other mental health support organizations

Source: Curated from official program websites and VA resources
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Service type to category mapping
SERVICE_TYPE_CATEGORIES = {
    "crisis": ["housing"],  # Crisis services are essential safety net
    "therapy": ["housing"],  # Mental health is tied to housing stability
    "peer-support": ["housing"],
    "recreation": ["housing"],
}


class MentalHealthConnector(BaseConnector):
    """Connector for veteran mental health resources.

    Loads curated data about national programs that provide mental health
    support to veterans including crisis intervention, therapy, peer support,
    and community wellness programs.

    These resources span tier 1 (VA programs) through tier 2 (established
    nonprofits) providers.
    """

    # Data file path relative to project root
    DATA_PATH = "data/reference/mental_health_resources.json"

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
            name="Veteran Mental Health Resources",
            url="https://www.mentalhealth.va.gov/",
            tier=2,  # Mix of VA (tier 1) and established nonprofits (tier 2)
            frequency="monthly",  # Programs change infrequently
            terms_url=None,
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse and return mental health resources.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        now = datetime.now(UTC)

        data = self._load_data()
        if not data:
            return []

        resources: list[ResourceCandidate] = []

        for resource in data.get("resources", []):
            candidate = self._parse_resource(resource, fetched_at=now)
            resources.append(candidate)

        return resources

    def _load_data(self) -> dict:
        """Load resource data from JSON file."""
        if not self.data_path.exists():
            return {}

        with open(self.data_path) as f:
            return json.load(f)

    def _parse_resource(
        self,
        resource: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a resource entry into a ResourceCandidate.

        Args:
            resource: Dictionary containing resource data.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this mental health resource.
        """
        org_name = resource.get("org_name", "Unknown Organization")
        program_name = resource.get("program_name", "Mental Health Services")
        service_type = resource.get("service_type", "therapy")
        website = resource.get("website")
        phone = resource.get("phone")
        email = resource.get("email")

        title = self._build_title(org_name, program_name)
        description = self._build_description(resource)
        eligibility = self._build_eligibility(resource)
        how_to_apply = self._build_how_to_apply(resource)
        tags = self._build_tags(resource)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website or "https://www.mentalhealth.va.gov/",
            org_name=org_name,
            org_website=website,
            categories=self._get_categories(service_type),
            tags=tags,
            phone=self._normalize_phone(phone) if phone and phone != "988" else phone,
            email=email,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope=self._determine_scope(resource),
            states=resource.get("states_in_person"),
            raw_data=resource,
            fetched_at=fetched_at,
        )

    def _build_title(self, org_name: str, program_name: str) -> str:
        """Build resource title."""
        # For well-known orgs, use abbreviation in title
        abbrevs = {
            "Veterans Crisis Line": "Veterans Crisis Line",
            "VA Vet Centers": "VA Vet Centers",
            "VA Mental Health Services": "VA",
            "Cohen Veterans Network": "Cohen Veterans Network",
            "Wounded Warrior Project": "WWP",
            "Team Red, White & Blue": "Team RWB",
            "Travis Manion Foundation (formerly The Mission Continues)": "TMF/Mission Continues",
            "Semper Fi & America's Fund": "Semper Fi Fund",
        }
        org_short = abbrevs.get(org_name, org_name)

        # Handle special case where org name IS the program
        if org_name == "Veterans Crisis Line":
            return f"{org_name} - {program_name}"

        return f"{org_short} - {program_name}"

    def _build_description(self, resource: dict) -> str:
        """Build resource description with key details."""
        parts = []

        # Main description from data
        description = resource.get("description")
        if description:
            parts.append(description)

        # Add cost information
        cost = resource.get("cost")
        cost_notes = resource.get("cost_notes")
        if cost == "free":
            if cost_notes:
                parts.append(f"This service is free. {cost_notes}")
            else:
                parts.append("This service is provided at no cost.")
        elif cost == "sliding-scale":
            if cost_notes:
                parts.append(cost_notes)
            else:
                parts.append("Services provided on a sliding scale based on ability to pay.")
        elif cost == "copay" and cost_notes:
            parts.append(cost_notes)

        # Add delivery methods
        delivery = resource.get("delivery", [])
        if delivery:
            delivery_str = self._format_delivery_methods(delivery)
            parts.append(f"Available via: {delivery_str}.")

        # Add impact/stats if available
        impact = resource.get("impact")
        if impact:
            parts.append(impact)

        return " ".join(parts)

    def _format_delivery_methods(self, delivery: list[str]) -> str:
        """Format delivery methods into readable string."""
        method_labels = {
            "phone": "phone",
            "text": "text message",
            "chat": "online chat",
            "in-person": "in-person",
            "telehealth": "telehealth/video",
            "virtual": "virtual/online",
            "residential": "residential program",
            "case-management": "case management",
        }
        readable = [method_labels.get(m, m) for m in delivery]
        return ", ".join(readable)

    def _build_eligibility(self, resource: dict) -> str:
        """Build eligibility description."""
        eligibility = resource.get("eligibility", {})
        parts = []

        # Main eligibility summary
        summary = eligibility.get("summary")
        if summary:
            parts.append(summary)

        # Service era requirement
        service_era = eligibility.get("service_era")
        if service_era and service_era != "any":
            parts.append(f"Service era: {service_era}.")

        # VA enrollment requirement
        if eligibility.get("enrollment_required"):
            parts.append("VA health care enrollment required.")
        elif eligibility.get("enrollment_required") is False:
            parts.append("No VA enrollment required.")

        # Disability requirement
        if eligibility.get("disability_required"):
            disability_notes = eligibility.get("disability_notes")
            if disability_notes:
                parts.append(disability_notes)

        # Membership requirement
        if eligibility.get("membership_notes"):
            parts.append(eligibility["membership_notes"])

        # Separation limit
        separation_limit = eligibility.get("separation_limit")
        if separation_limit:
            parts.append(separation_limit)

        # Additional notes
        notes = eligibility.get("notes")
        if notes:
            parts.append(notes)

        return " ".join(parts) if parts else "Contact the organization for eligibility requirements."

    def _build_how_to_apply(self, resource: dict) -> str:
        """Build application/access instructions."""
        parts = []

        # How to access
        how_to_access = resource.get("how_to_access")
        if how_to_access:
            parts.append(how_to_access)

        # Response time if notable
        response_time = resource.get("response_time")
        if response_time:
            parts.append(f"Response time: {response_time}.")

        # Phone with instructions
        phone = resource.get("phone")
        phone_instructions = resource.get("phone_instructions")
        if phone and not how_to_access:
            if phone_instructions:
                parts.append(f"Call {phone} ({phone_instructions}).")
            else:
                parts.append(f"Call {phone}.")

        # Text option
        text = resource.get("text")
        if text:
            parts.append(f"Text: {text}.")

        # Chat URL
        chat_url = resource.get("chat_url")
        if chat_url:
            parts.append(f"Chat online: {chat_url}")

        # Website
        website = resource.get("website")
        if website and not how_to_access:
            parts.append(f"Website: {website}")

        # Hours
        hours = resource.get("hours")
        if hours:
            parts.append(f"Hours: {hours}.")

        # If no specific instructions, provide generic guidance
        if not parts:
            parts.append("Contact the organization through their website to learn more about accessing services.")

        return " ".join(parts)

    def _get_categories(self, service_type: str) -> list[str]:
        """Determine categories based on service type.

        Note: Mental health resources are categorized under 'housing' in the
        current taxonomy as mental health stability is crucial for housing
        stability. This may change if a 'health' category is added.
        """
        # For now, categorize under housing since mental health is tied to
        # housing stability and homelessness prevention
        return ["housing"]

    def _determine_scope(self, resource: dict) -> str:
        """Determine geographic scope of the resource."""
        # If there are specific states listed, it's state-level
        if resource.get("states_in_person"):
            return "state"

        # Check location notes for local indicators
        location_notes = resource.get("location_notes", "")
        if "nationwide" in location_notes.lower() or not location_notes:
            return "national"

        # Check location count - large numbers suggest national
        location_count = resource.get("location_count", 0)
        if location_count >= 10:
            return "national"

        return "national"  # Default to national for mental health resources

    def _build_tags(self, resource: dict) -> list[str]:
        """Build tags list."""
        tags = ["mental-health", "veteran-mental-health"]

        # Service type tag
        service_type = resource.get("service_type")
        if service_type:
            tags.append(service_type)

        # Specialties
        specialties = resource.get("specialties", [])
        for specialty in specialties:
            if specialty not in tags:
                tags.append(specialty)

        # Cost tag
        cost = resource.get("cost")
        if cost == "free":
            tags.append("free")
        elif cost == "sliding-scale":
            tags.append("sliding-scale")

        # Delivery method tags
        delivery = resource.get("delivery", [])
        if "telehealth" in delivery or "virtual" in delivery:
            tags.append("telehealth")
        if "24/7/365" in resource.get("hours", "") or "24/7" in resource.get("hours", ""):
            tags.append("24-7")

        # Program format tags
        program_format = resource.get("program_format", "")
        if "intensive" in program_format.lower():
            tags.append("intensive-program")
        if "residential" in program_format.lower() or "residential" in delivery:
            tags.append("residential")
        if "retreat" in program_format.lower():
            tags.append("retreat")

        # Eligibility-based tags
        eligibility = resource.get("eligibility", {})
        service_era = eligibility.get("service_era", "")
        if "post-9/11" in service_era.lower():
            tags.append("post-9/11")

        if eligibility.get("disability_required"):
            tags.append("disabled-veterans")

        # Family support tag
        summary = eligibility.get("summary", "").lower()
        if "family" in summary or "spouse" in summary or "caregiver" in summary:
            tags.append("family-support")

        # Therapies offered
        therapies = resource.get("therapies_offered", [])
        for therapy in therapies:
            therapy_tag = therapy.lower().replace(" ", "-")
            if therapy_tag not in tags:
                tags.append(therapy_tag)

        # Organization-specific tags
        org_name = resource.get("org_name", "").lower()
        if "va" in org_name or "veterans crisis" in org_name:
            tags.append("va")
        elif "wounded warrior" in org_name:
            tags.append("wwp")
        elif "team r" in org_name:
            tags.append("team-rwb")
        elif "cohen" in org_name:
            tags.append("cohen-veterans-network")
        elif "headstrong" in org_name:
            tags.append("headstrong")

        return list(dict.fromkeys(tags))  # Remove duplicates while preserving order
