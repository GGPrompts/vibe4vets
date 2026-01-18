"""Legal Services Corporation (LSC) funded legal aid program connector.

Imports LSC-funded legal aid organizations from the curated grantee directory.
Source: https://www.lsc.gov/grants/our-grantees
"""

from datetime import UTC, datetime
from pathlib import Path

import yaml

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class LegalAidConnector(BaseConnector):
    """Connector for LSC-funded legal aid programs.

    Parses the lsc_grantees.yaml file containing 129 LSC-funded legal aid
    organizations providing free civil legal services across all 50 states,
    DC, and US territories.

    These organizations often help veterans with:
    - VA benefits appeals and discharge upgrades
    - Housing issues (eviction defense, foreclosure prevention)
    - Family law (custody, divorce, child support)
    - Consumer protection (debt collection, bankruptcy)
    """

    # Path to the LSC grantee data file relative to project root
    DEFAULT_DATA_PATH = "data/reference/lsc_grantees.yaml"

    # Services that are particularly relevant to veterans
    VETERAN_RELEVANT_SERVICES = {"benefits", "housing", "family", "employment", "civil"}

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to YAML file. Falls back to DEFAULT_DATA_PATH.
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
            name="LSC Grantee Directory",
            url="https://www.lsc.gov/grants/our-grantees",
            tier=2,  # Established nonprofit directory
            frequency="yearly",  # LSC funding is annual
            terms_url="https://www.lsc.gov/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse LSC grantee data from YAML file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"LSC grantee data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = yaml.safe_load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        grantees = data.get("grantees", [])
        for grantee in grantees:
            # Only include grantees with veteran-relevant services
            services = set(grantee.get("services", []))
            if not services.intersection(self.VETERAN_RELEVANT_SERVICES):
                continue

            candidate = self._parse_grantee(grantee, fetched_at=now)
            resources.append(candidate)

        return resources

    def _parse_grantee(
        self,
        grantee: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a grantee entry into a ResourceCandidate.

        Args:
            grantee: Grantee data dictionary from YAML
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this grantee.
        """
        org_name = grantee["name"]
        state = grantee["state"]
        website = grantee.get("website")
        phone = grantee.get("phone")
        services = grantee.get("services", [])

        # Build title
        state_name = self._state_code_to_name(state)
        title = f"Legal Aid - {org_name}"

        # Build description
        description = self._build_description(org_name, state_name, services)

        # Build tags from services
        tags = self._build_tags(services, state)

        # Determine scope (all LSC grantees serve specific states)
        scope = "state"

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website or "https://www.lsc.gov/grants/our-grantees",
            org_name=org_name,
            org_website=website,
            categories=["legal"],
            tags=tags,
            eligibility=self._build_eligibility(),
            how_to_apply=self._build_how_to_apply(org_name, website, phone),
            scope=scope,
            states=[state] if state else None,
            state=state,
            phone=self._normalize_phone(phone),
            raw_data={
                "lsc_grantee": True,
                "services": services,
                "state_code": state,
            },
            fetched_at=fetched_at,
        )

    def _build_description(
        self,
        org_name: str,
        state_name: str,
        services: list[str],
    ) -> str:
        """Build resource description.

        Args:
            org_name: Organization name
            state_name: Full state name
            services: List of service types

        Returns:
            Formatted description string.
        """
        parts = [
            f"{org_name} provides free civil legal assistance to low-income residents "
            f"in {state_name}."
        ]

        # Describe veteran-relevant services
        veteran_services = []
        if "benefits" in services:
            veteran_services.append("VA benefits appeals and discharge upgrades")
        if "housing" in services:
            veteran_services.append("housing issues including eviction defense")
        if "family" in services:
            veteran_services.append("family law matters")
        if "consumer" in services:
            veteran_services.append("consumer protection and debt issues")

        if veteran_services:
            parts.append(f"Services include {', '.join(veteran_services)}.")

        parts.append(
            "As an LSC-funded program, they provide free legal help to those who qualify "
            "based on income guidelines (typically 125-200% of federal poverty level)."
        )

        return " ".join(parts)

    def _build_eligibility(self) -> str:
        """Build standard LSC eligibility text.

        Returns:
            Eligibility description string.
        """
        return (
            "Must meet income guidelines (typically 125-200% of federal poverty level). "
            "Services are free for those who qualify. Veterans are eligible regardless "
            "of discharge status for most civil legal matters. Priority may be given to "
            "certain case types. Contact the organization for specific eligibility requirements."
        )

    def _build_how_to_apply(
        self,
        org_name: str,
        website: str | None,
        phone: str | None,
    ) -> str:
        """Build how-to-apply text.

        Args:
            org_name: Organization name
            website: Organization website
            phone: Organization phone

        Returns:
            How to apply description string.
        """
        parts = [f"Contact {org_name} directly for intake."]

        if website:
            parts.append(f"Visit {website} for online intake or information.")

        if phone:
            parts.append(f"Call {phone} to speak with an intake specialist.")

        parts.append(
            "You can also find legal aid near you at LawHelp.org or call the LSC "
            "Legal Aid Locator."
        )

        return " ".join(parts)

    def _build_tags(self, services: list[str], state: str) -> list[str]:
        """Build tags list.

        Args:
            services: List of service types
            state: State code

        Returns:
            List of tag strings.
        """
        tags = [
            "legal-aid",
            "lsc-funded",
            "free-legal-services",
            "civil-legal",
        ]

        # Add service-specific tags
        service_tag_map = {
            "benefits": "benefits-appeals",
            "housing": "housing-legal",
            "family": "family-law",
            "consumer": "consumer-protection",
            "employment": "employment-law",
            "immigration": "immigration",
            "native-american": "native-american",
        }

        for service in services:
            if service in service_tag_map:
                tags.append(service_tag_map[service])

        # Add state tag
        if state:
            tags.append(f"state-{state.lower()}")

        return tags

    def _state_code_to_name(self, code: str) -> str:
        """Convert state code to full name.

        Args:
            code: Two-letter state code

        Returns:
            Full state name or the code if unknown.
        """
        state_names = {
            "AL": "Alabama",
            "AK": "Alaska",
            "AS": "American Samoa",
            "AZ": "Arizona",
            "AR": "Arkansas",
            "CA": "California",
            "CO": "Colorado",
            "CT": "Connecticut",
            "DE": "Delaware",
            "DC": "District of Columbia",
            "FL": "Florida",
            "FM": "Federated States of Micronesia",
            "GA": "Georgia",
            "GU": "Guam",
            "HI": "Hawaii",
            "ID": "Idaho",
            "IL": "Illinois",
            "IN": "Indiana",
            "IA": "Iowa",
            "KS": "Kansas",
            "KY": "Kentucky",
            "LA": "Louisiana",
            "ME": "Maine",
            "MD": "Maryland",
            "MA": "Massachusetts",
            "MI": "Michigan",
            "MN": "Minnesota",
            "MS": "Mississippi",
            "MO": "Missouri",
            "MT": "Montana",
            "NE": "Nebraska",
            "NV": "Nevada",
            "NH": "New Hampshire",
            "NJ": "New Jersey",
            "NM": "New Mexico",
            "NY": "New York",
            "NC": "North Carolina",
            "ND": "North Dakota",
            "MP": "Northern Mariana Islands",
            "OH": "Ohio",
            "OK": "Oklahoma",
            "OR": "Oregon",
            "PA": "Pennsylvania",
            "PR": "Puerto Rico",
            "RI": "Rhode Island",
            "SC": "South Carolina",
            "SD": "South Dakota",
            "TN": "Tennessee",
            "TX": "Texas",
            "UT": "Utah",
            "VT": "Vermont",
            "VI": "Virgin Islands",
            "VA": "Virginia",
            "WA": "Washington",
            "WV": "West Virginia",
            "WI": "Wisconsin",
            "WY": "Wyoming",
        }
        return state_names.get(code, code)
