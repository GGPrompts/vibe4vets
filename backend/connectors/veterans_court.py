"""Veterans Treatment Court (VTC) connector.

Imports Veterans Treatment Court programs from curated state directories.
VTCs provide alternative sentencing for veteran defendants with substance use
and mental health disorders.

Sources:
- Bureau of Justice Assistance: https://bja.ojp.gov/program/veterans-treatment-court-program/overview
- State judicial branch websites
- Justice for Vets (All Rise): https://allrise.org/about/division/justice-for-vets/
"""

from datetime import UTC, datetime
from pathlib import Path

import yaml

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class VeteransCourtConnector(BaseConnector):
    """Connector for Veterans Treatment Court programs.

    Parses the veterans_treatment_courts.yaml file containing state-level
    VTC program information. There are 600+ VTCs nationwide, but data is
    maintained at the state level without a centralized national database.

    Veterans Treatment Courts help justice-involved veterans with:
    - Substance use disorder treatment
    - Mental health treatment (PTSD, TBI, MST)
    - VA benefits enrollment
    - Housing and employment support
    - Veteran peer mentorship
    """

    # Path to the VTC data file relative to project root
    DEFAULT_DATA_PATH = "data/reference/veterans_treatment_courts.yaml"

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
            name="Veterans Treatment Courts Directory",
            url="https://bja.ojp.gov/program/veterans-treatment-court-program/overview",
            tier=2,  # Established nonprofit/government directory
            frequency="quarterly",  # State programs update periodically
            terms_url="https://www.justice.gov/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse Veterans Treatment Court data from YAML file.

        Creates resources for:
        1. National-level resources (VJO, Justice for Vets)
        2. State-level program pages (one per state with VTC info)
        3. Individual courts with specific contact info (where available)

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"VTC data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = yaml.safe_load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        # Add national resources
        for nat_resource in data.get("national_resources", []):
            candidate = self._parse_national_resource(nat_resource, fetched_at=now)
            resources.append(candidate)

        # Add state program pages
        for state_program in data.get("state_programs", []):
            # Add state-level program resource
            candidate = self._parse_state_program(state_program, data, fetched_at=now)
            resources.append(candidate)

            # Add individual courts if detailed info available
            for court in state_program.get("courts", []):
                if court.get("contact_email") or court.get("contact_phone"):
                    candidate = self._parse_individual_court(court, state_program, data, fetched_at=now)
                    resources.append(candidate)

        return resources

    def _parse_national_resource(
        self,
        resource: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a national resource into a ResourceCandidate.

        Args:
            resource: National resource data from YAML
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this national resource.
        """
        name = resource["name"]
        url = resource.get("url", "")
        description = resource.get("description", "").strip()
        how_to_access = resource.get("how_to_access", "")

        return ResourceCandidate(
            title=f"Veterans Treatment Court Resource - {name}",
            description=description,
            source_url=url,
            org_name=name,
            org_website=url,
            categories=["legal"],
            tags=[
                "veterans-court",
                "veterans-treatment-court",
                "vtc",
                "justice-involved",
                "national",
            ],
            eligibility=self._build_eligibility_text(),
            how_to_apply=how_to_access,
            scope="national",
            states=None,
            raw_data={
                "vtc_resource_type": "national",
                "resource_name": name,
            },
            fetched_at=fetched_at,
        )

    def _parse_state_program(
        self,
        program: dict,
        data: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a state program into a ResourceCandidate.

        Args:
            program: State program data from YAML
            data: Full YAML data for accessing general eligibility info
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this state program.
        """
        state = program["state"]
        name = program.get("name", f"{state} Veterans Treatment Courts")
        program_url = program.get("program_url", "")
        notes = program.get("notes", "").strip()
        court_count = program.get("court_count_estimate", 0)

        # Build description
        description = self._build_state_description(name, state, notes, court_count)

        # Build tags
        tags = self._build_tags(state, is_state_program=True)

        # State-specific eligibility if available
        state_eligibility = program.get("eligibility", "")
        eligibility = state_eligibility if state_eligibility else self._build_eligibility_text()

        # How to apply
        how_to_apply = self._build_how_to_apply(
            name,
            program_url,
            program.get("contact_phone"),
            program.get("contact_name"),
        )

        return ResourceCandidate(
            title=name,
            description=description,
            source_url=program_url,
            org_name=name,
            org_website=program_url,
            categories=["legal"],
            tags=tags,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="state",
            states=[state],
            state=state,
            phone=self._normalize_phone(program.get("contact_phone")),
            raw_data={
                "vtc_resource_type": "state_program",
                "state_code": state,
                "court_count_estimate": court_count,
            },
            fetched_at=fetched_at,
        )

    def _parse_individual_court(
        self,
        court: dict,
        state_program: dict,
        data: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse an individual court into a ResourceCandidate.

        Args:
            court: Individual court data from YAML
            state_program: Parent state program data
            data: Full YAML data
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this individual court.
        """
        state = state_program["state"]
        court_name = court["name"]
        jurisdiction = court.get("jurisdiction", "")

        # Build title
        state_name = self._state_code_to_name(state)
        title = f"{court_name}"

        # Build description
        description = self._build_court_description(court_name, jurisdiction, state_name, court.get("notes", ""))

        # Build tags
        tags = self._build_tags(state, is_state_program=False)

        # Use court-specific URL if available, otherwise state program URL
        court_url = court.get("program_url", state_program.get("program_url", ""))

        # Get eligibility from state program or general
        eligibility = state_program.get("eligibility", self._build_eligibility_text())

        # How to apply with court-specific contact
        how_to_apply = self._build_court_how_to_apply(
            court_name,
            court_url,
            court.get("contact_email"),
            court.get("contact_phone"),
        )

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=court_url,
            org_name=court_name,
            org_website=court_url,
            categories=["legal"],
            tags=tags,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="local",
            states=[state],
            state=state,
            email=court.get("contact_email"),
            phone=self._normalize_phone(court.get("contact_phone")),
            raw_data={
                "vtc_resource_type": "individual_court",
                "state_code": state,
                "jurisdiction": jurisdiction,
                "established": court.get("established"),
            },
            fetched_at=fetched_at,
        )

    def _build_state_description(
        self,
        name: str,
        state: str,
        notes: str,
        court_count: int,
    ) -> str:
        """Build state program description.

        Args:
            name: Program name
            state: State code
            notes: Additional notes
            court_count: Estimated number of courts

        Returns:
            Formatted description string.
        """
        state_name = self._state_code_to_name(state)
        parts = []

        if court_count > 0:
            parts.append(
                f"{state_name} has approximately {court_count} Veterans Treatment Courts "
                f"that provide alternative sentencing for justice-involved veterans."
            )
        else:
            parts.append(
                f"{state_name} Veterans Treatment Courts provide alternative sentencing for justice-involved veterans."
            )

        parts.append(
            "VTCs help veterans with substance use disorders, PTSD, TBI, and other "
            "service-connected conditions through supervised treatment programs "
            "instead of traditional incarceration."
        )

        if notes:
            parts.append(notes)

        return " ".join(parts)

    def _build_court_description(
        self,
        court_name: str,
        jurisdiction: str,
        state_name: str,
        notes: str,
    ) -> str:
        """Build individual court description.

        Args:
            court_name: Court name
            jurisdiction: Jurisdiction (county, etc.)
            state_name: Full state name
            notes: Additional notes

        Returns:
            Formatted description string.
        """
        parts = [
            f"The {court_name} serves {jurisdiction} in {state_name}, "
            f"providing alternative sentencing for justice-involved veterans."
        ]

        parts.append(
            "This Veterans Treatment Court offers supervised treatment programs "
            "for veterans with substance use disorders, PTSD, TBI, and other "
            "service-connected conditions."
        )

        if notes:
            parts.append(notes)

        return " ".join(parts)

    def _build_eligibility_text(self) -> str:
        """Build general VTC eligibility text.

        Returns:
            Eligibility description string.
        """
        return (
            "Eligibility varies by jurisdiction but typically requires: "
            "(1) Veteran or current service member status in the U.S. Armed Forces; "
            "(2) A diagnosed condition such as PTSD, TBI, MST, or substance use disorder; "
            "(3) A criminal charge in the court's jurisdiction; "
            "(4) Willingness to participate in the treatment program. "
            "Some courts require a 'nexus' connecting military service to the criminal behavior. "
            "Offense types accepted (misdemeanor vs. felony) vary by court. "
            "Contact the court directly to confirm specific eligibility requirements."
        )

    def _build_how_to_apply(
        self,
        name: str,
        url: str | None,
        phone: str | None,
        contact_name: str | None,
    ) -> str:
        """Build how-to-apply text for state programs.

        Args:
            name: Program name
            url: Program website
            phone: Contact phone
            contact_name: Contact person name

        Returns:
            How to apply description string.
        """
        parts = []

        if url:
            parts.append(f"Visit {url} for local court locations and contact information.")

        if contact_name and phone:
            parts.append(f"Contact {contact_name} at {phone} for referrals.")
        elif phone:
            parts.append(f"Call {phone} for program information.")

        parts.append(
            "You can also contact your local VA Medical Center and ask for the "
            "Veterans Justice Outreach (VJO) Specialist, who can connect you to "
            "local Veterans Treatment Courts."
        )

        parts.append(
            "Defense attorneys, prosecutors, and probation officers can also refer eligible veterans to the program."
        )

        return " ".join(parts)

    def _build_court_how_to_apply(
        self,
        court_name: str,
        url: str | None,
        email: str | None,
        phone: str | None,
    ) -> str:
        """Build how-to-apply text for individual courts.

        Args:
            court_name: Court name
            url: Court/program website
            email: Contact email
            phone: Contact phone

        Returns:
            How to apply description string.
        """
        parts = [f"Contact the {court_name} directly for intake and eligibility determination."]

        if email:
            parts.append(f"Email: {email}")

        if phone:
            parts.append(f"Phone: {phone}")

        if url:
            parts.append(f"Visit {url} for more information.")

        parts.append(
            "Referrals typically come from defense attorneys, prosecutors, "
            "probation officers, or the VA Veterans Justice Outreach program."
        )

        return " ".join(parts)

    def _build_tags(self, state: str, is_state_program: bool = False) -> list[str]:
        """Build tags list.

        Args:
            state: State code
            is_state_program: Whether this is a state-level program

        Returns:
            List of tag strings.
        """
        tags = [
            "veterans-court",
            "veterans-treatment-court",
            "vtc",
            "justice-involved",
            "alternative-sentencing",
            "substance-abuse-treatment",
            "mental-health-treatment",
            "ptsd",
            "legal",
        ]

        if is_state_program:
            tags.append("state-program")

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
            "AZ": "Arizona",
            "AR": "Arkansas",
            "CA": "California",
            "CO": "Colorado",
            "CT": "Connecticut",
            "DE": "Delaware",
            "DC": "District of Columbia",
            "FL": "Florida",
            "GA": "Georgia",
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
            "OH": "Ohio",
            "OK": "Oklahoma",
            "OR": "Oregon",
            "PA": "Pennsylvania",
            "RI": "Rhode Island",
            "SC": "South Carolina",
            "SD": "South Dakota",
            "TN": "Tennessee",
            "TX": "Texas",
            "UT": "Utah",
            "VT": "Vermont",
            "VA": "Virginia",
            "WA": "Washington",
            "WV": "West Virginia",
            "WI": "Wisconsin",
            "WY": "Wyoming",
        }
        return state_names.get(code, code)
