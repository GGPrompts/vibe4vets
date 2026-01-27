"""VA Community Care Network (CCN) provider directory connector.

Imports curated data about VA Community Care Network providers who offer
healthcare services to eligible veterans outside VA facilities.

The Community Care Network is managed by two Third Party Administrators:
- Optum: Regions 1, 2, 3 (Eastern/Central US)
- TriWest: Regions 4, 5 (Western US)

Resources include:
- Primary Care providers
- Specialty Care (cardiology, orthopedics, dermatology, etc.)
- Mental Health providers
- Urgent Care facilities
- Dental providers
- Eye/Vision Care providers

Source: Curated from VA Community Care provider directories and registrations
"""

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# CCN region mapping
CCN_REGIONS = {
    # Region 1 - Optum (Northeast)
    "CT": 1, "DE": 1, "DC": 1, "ME": 1, "MD": 1, "MA": 1, "NH": 1, "NJ": 1,
    "NY": 1, "PA": 1, "RI": 1, "VT": 1, "VA": 1, "WV": 1,
    # Region 2 - Optum (Southeast)
    "AL": 2, "FL": 2, "GA": 2, "KY": 2, "MS": 2, "NC": 2, "SC": 2, "TN": 2, "PR": 2, "VI": 2,
    # Region 3 - Optum (Central)
    "AR": 3, "LA": 3, "OK": 3, "TX": 3, "IL": 3, "IN": 3, "MI": 3, "MN": 3,
    "OH": 3, "WI": 3, "IA": 3, "KS": 3, "MO": 3, "NE": 3, "ND": 3, "SD": 3,
    # Region 4 - TriWest (Mountain)
    "AZ": 4, "CO": 4, "ID": 4, "MT": 4, "NV": 4, "NM": 4, "UT": 4, "WY": 4,
    # Region 5 - TriWest (Pacific)
    "AK": 5, "CA": 5, "HI": 5, "OR": 5, "WA": 5, "GU": 5, "AS": 5,
}

# TPA contact information
TPA_CONTACTS = {
    "optum": {
        "name": "Optum Public Sector Solutions",
        "regions": [1, 2, 3],
        "phone": {
            1: "(888) 901-7407",
            2: "(844) 839-6108",
            3: "(888) 901-6613",
        },
        "website": "https://vacommunitycare.com/",
        "provider_portal": "https://vacommunitycare.com/provider",
    },
    "triwest": {
        "name": "TriWest Health Care Alliance",
        "regions": [4, 5],
        "phone": "(877) 226-8749",
        "email": "providerservices@triwest.com",
        "website": "https://vaccn.triwest.com/",
        "provider_portal": "https://vaccn.triwest.com/en/provider/",
    },
}

# Specialty to category mapping
SPECIALTY_CATEGORIES = {
    "primary_care": ["housing"],  # Healthcare access is tied to housing stability
    "mental_health": ["housing"],
    "cardiology": ["housing"],
    "orthopedics": ["housing"],
    "dermatology": ["housing"],
    "neurology": ["housing"],
    "urgent_care": ["housing"],
    "dental": ["housing"],
    "vision": ["housing"],
    "audiology": ["housing"],
    "physical_therapy": ["housing"],
    "chiropractic": ["housing"],
    "podiatry": ["housing"],
    "radiology": ["housing"],
    "lab_services": ["housing"],
}


class VACommunityConnector(BaseConnector):
    """Connector for VA Community Care Network provider data.

    Loads curated data about community healthcare providers participating
    in the VA CCN program. These providers offer care to veterans when
    VA facilities cannot provide timely or geographically accessible care.
    """

    # Data file path relative to project root
    DATA_PATH = "data/reference/va_community_care_providers.json"

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
            name="VA Community Care Network Providers",
            url="https://www.va.gov/COMMUNITYCARE/",
            tier=2,  # Curated from official VA CCN directories
            frequency="monthly",  # Provider networks change periodically
            terms_url="https://www.va.gov/COMMUNITYCARE/providers/index.asp",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse and return VA Community Care provider resources.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        now = datetime.now(UTC)

        data = self._load_data()
        if not data:
            return []

        resources: list[ResourceCandidate] = []

        for provider in data.get("providers", []):
            candidate = self._parse_provider(provider, fetched_at=now)
            resources.append(candidate)

        return resources

    def _load_data(self) -> dict:
        """Load provider data from JSON file."""
        if not self.data_path.exists():
            return {}

        with open(self.data_path) as f:
            return json.load(f)

    def _parse_provider(
        self,
        provider: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a provider entry into a ResourceCandidate.

        Args:
            provider: Dictionary containing provider data.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this community care provider.
        """
        provider_name = provider.get("provider_name", "Unknown Provider")
        org_name = provider.get("org_name", provider_name)
        specialty = provider.get("specialty", "primary_care")
        specialties = provider.get("specialties", [specialty])
        state = provider.get("state")
        city = provider.get("city")
        address = provider.get("address")
        zip_code = provider.get("zip_code")
        phone = provider.get("phone")
        email = provider.get("email")
        network_status = provider.get("network_status", "in_network")
        website = provider.get("website")

        title = self._build_title(provider_name, specialty, city, state)
        description = self._build_description(provider)
        eligibility = self._build_eligibility(provider)
        how_to_apply = self._build_how_to_apply(provider)
        tags = self._build_tags(provider)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website or "https://www.va.gov/COMMUNITYCARE/",
            org_name=org_name,
            org_website=website,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=self._get_categories(specialty),
            tags=tags,
            phone=self._normalize_phone(phone),
            email=email,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope=self._determine_scope(provider),
            states=[state] if state else None,
            raw_data=provider,
            fetched_at=fetched_at,
        )

    def _build_title(
        self,
        provider_name: str,
        specialty: str,
        city: str | None,
        state: str | None,
    ) -> str:
        """Build resource title."""
        specialty_display = self._format_specialty(specialty)

        if city and state:
            return f"VA CCN: {provider_name} - {specialty_display} ({city}, {state})"
        elif state:
            return f"VA CCN: {provider_name} - {specialty_display} ({state})"
        else:
            return f"VA CCN: {provider_name} - {specialty_display}"

    def _format_specialty(self, specialty: str) -> str:
        """Format specialty for display."""
        specialty_labels = {
            "primary_care": "Primary Care",
            "mental_health": "Mental Health",
            "cardiology": "Cardiology",
            "orthopedics": "Orthopedics",
            "dermatology": "Dermatology",
            "neurology": "Neurology",
            "urgent_care": "Urgent Care",
            "dental": "Dental Care",
            "vision": "Eye Care",
            "audiology": "Audiology/Hearing",
            "physical_therapy": "Physical Therapy",
            "chiropractic": "Chiropractic Care",
            "podiatry": "Podiatry",
            "radiology": "Radiology/Imaging",
            "lab_services": "Laboratory Services",
        }
        return specialty_labels.get(specialty, specialty.replace("_", " ").title())

    def _build_description(self, provider: dict) -> str:
        """Build provider description with key details."""
        parts = []

        provider_name = provider.get("provider_name", "This provider")
        specialty = provider.get("specialty", "primary_care")
        specialties = provider.get("specialties", [])
        city = provider.get("city")
        state = provider.get("state")
        network_status = provider.get("network_status", "in_network")
        description = provider.get("description")

        # Custom description if provided
        if description:
            parts.append(description)
        else:
            # Generate description
            specialty_display = self._format_specialty(specialty)
            location = f"{city}, {state}" if city and state else (state or "your area")
            parts.append(
                f"{provider_name} is a VA Community Care Network provider offering "
                f"{specialty_display} services to eligible veterans in {location}."
            )

        # Network status
        if network_status == "in_network":
            parts.append(
                "This provider is in-network with VA Community Care, which means "
                "no separate referral fees and streamlined billing."
            )
        elif network_status == "urgent_care":
            parts.append(
                "This is an approved urgent care location. Veterans do NOT need "
                "a VA referral or prior authorization for urgent care visits."
            )

        # Additional specialties
        if len(specialties) > 1:
            other_specs = [self._format_specialty(s) for s in specialties if s != specialty]
            if other_specs:
                parts.append(f"Additional services: {', '.join(other_specs)}.")

        # Service details
        services = provider.get("services")
        if services:
            parts.append(f"Services include: {services}.")

        # Accepting new patients
        accepting_patients = provider.get("accepting_new_patients")
        if accepting_patients is True:
            parts.append("Currently accepting new veteran patients.")
        elif accepting_patients is False:
            parts.append("Note: May not be accepting new patients at this time.")

        # Languages
        languages = provider.get("languages", [])
        if languages and len(languages) > 1:
            parts.append(f"Languages spoken: {', '.join(languages)}.")

        return " ".join(parts)

    def _build_eligibility(self, provider: dict) -> str:
        """Build eligibility description."""
        parts = []
        network_status = provider.get("network_status", "in_network")

        parts.append(
            "VA Community Care is available to veterans enrolled in VA health care "
            "who meet one of these criteria:"
        )

        parts.append(
            "1) VA cannot provide the care needed; "
            "2) VA cannot provide care within designated access standards (drive time/wait time); "
            "3) VA refers the veteran for care in the community; "
            "4) The veteran needs care from a specific provider for continuity of care; "
            "5) VA determines it is in the veteran's best medical interest."
        )

        if network_status == "urgent_care":
            parts.append(
                "For urgent care: No VA referral needed. Just present your Veteran Health "
                "Identification Card (VHIC) or VHIC-i to receive care."
            )
        else:
            parts.append(
                "IMPORTANT: You must have a VA referral before receiving community care. "
                "Without a referral, you may be responsible for the full cost of care."
            )

        return " ".join(parts)

    def _build_how_to_apply(self, provider: dict) -> str:
        """Build application/access instructions."""
        parts = []
        state = provider.get("state")
        phone = provider.get("phone")
        email = provider.get("email")
        network_status = provider.get("network_status", "in_network")
        hours = provider.get("hours")

        # Step 1: Get referral (unless urgent care)
        if network_status == "urgent_care":
            parts.append(
                "Step 1: Locate this urgent care facility and present your Veteran "
                "Health Identification Card (VHIC)."
            )
        else:
            parts.append(
                "Step 1: Talk to your VA primary care provider about getting a "
                "community care referral for this specialty."
            )

        # Step 2: Contact provider
        if phone:
            parts.append(f"Step 2: Contact the provider at {self._normalize_phone(phone)} to schedule an appointment.")
        else:
            parts.append("Step 2: Contact the provider to schedule an appointment.")

        # Additional contact info
        if email:
            parts.append(f"Email: {email}")

        if hours:
            parts.append(f"Hours: {hours}")

        # TPA contact for questions
        region = CCN_REGIONS.get(state) if state else None
        if region:
            if region <= 3:  # Optum regions
                tpa_phone = TPA_CONTACTS["optum"]["phone"].get(region, "(888) 901-7407")
                parts.append(
                    f"For questions about your referral, contact Optum at {tpa_phone} (Region {region})."
                )
            else:  # TriWest regions
                parts.append(
                    f"For questions about your referral, contact TriWest at (877) 226-8749 (Region {region})."
                )

        # National contact center
        parts.append(
            "VA Community Care Contact Center: 877-881-7618 (Option 1 for Veterans)."
        )

        return " ".join(parts)

    def _get_categories(self, specialty: str) -> list[str]:
        """Determine categories based on specialty.

        Note: Healthcare resources are categorized under 'housing' in the
        current taxonomy as healthcare access is crucial for housing stability.
        """
        return SPECIALTY_CATEGORIES.get(specialty, ["housing"])

    def _determine_scope(self, provider: dict) -> str:
        """Determine geographic scope of the provider."""
        # Individual providers are local
        return "local"

    def _build_tags(self, provider: dict) -> list[str]:
        """Build tags list."""
        tags = ["va-community-care", "ccn", "veteran-healthcare"]

        # Network status
        network_status = provider.get("network_status", "in_network")
        if network_status == "in_network":
            tags.append("in-network")
        elif network_status == "urgent_care":
            tags.append("urgent-care")
            tags.append("no-referral-needed")

        # Specialty tags
        specialty = provider.get("specialty", "primary_care")
        specialty_tag = specialty.replace("_", "-")
        tags.append(specialty_tag)

        # Additional specialties
        specialties = provider.get("specialties", [])
        for spec in specialties:
            spec_tag = spec.replace("_", "-")
            if spec_tag not in tags:
                tags.append(spec_tag)

        # State/region tags
        state = provider.get("state")
        if state:
            region = CCN_REGIONS.get(state)
            if region:
                tags.append(f"ccn-region-{region}")
                if region <= 3:
                    tags.append("optum")
                else:
                    tags.append("triwest")

        # Accepting patients
        if provider.get("accepting_new_patients"):
            tags.append("accepting-patients")

        # Languages
        languages = provider.get("languages", [])
        if "Spanish" in languages or "Espanol" in languages:
            tags.append("spanish-speaking")
        if len(languages) > 1:
            tags.append("multilingual")

        # Telehealth
        if provider.get("telehealth_available"):
            tags.append("telehealth")

        # Wheelchair accessible
        if provider.get("wheelchair_accessible"):
            tags.append("wheelchair-accessible")

        return list(dict.fromkeys(tags))  # Remove duplicates while preserving order
