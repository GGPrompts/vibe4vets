"""VA Patient Advocate connector for VAMC patient advocate contacts.

Patient Advocates help veterans and their families resolve concerns about
any aspect of their VA health care experience. They are available at every
VA Medical Center and can help with questions, problems, or special needs.

Source: https://www.va.gov/health/patientadvocate/
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Map of state abbreviations to full names
STATE_NAMES = {
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
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PI": "Philippines",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}


class VAPatientAdvocateConnector(BaseConnector):
    """Connector for VA Medical Center Patient Advocate contacts.

    Loads curated patient advocate contact information for VA Medical Centers
    nationwide. Patient Advocates help veterans navigate the VA system, file
    complaints, and resolve issues with their care.

    This connector provides:
    - Direct phone numbers to Patient Advocates at each VAMC
    - Email contacts where available
    - Office hours
    - Step-by-step complaint process instructions
    """

    DATA_PATH = "data/reference/va_patient_advocates.json"

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
            name="VA Patient Advocate Program",
            url="https://www.va.gov/health/patientadvocate/",
            tier=1,  # Official VA program
            frequency="quarterly",
            terms_url="https://www.va.gov/webpolicy/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Load and parse VA Patient Advocate data.

        Returns:
            List of normalized ResourceCandidate objects.

        Raises:
            FileNotFoundError: If data file not found.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"VA Patient Advocate data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        now = datetime.now(UTC)
        resources: list[ResourceCandidate] = []

        # Get complaint process steps
        complaint_process = data.get("complaint_process", {})
        complaint_steps = complaint_process.get("steps", [])
        escalation_contacts = complaint_process.get("escalation_contacts", {})

        for advocate in data.get("advocates", []):
            candidate = self._parse_advocate(
                advocate=advocate,
                complaint_steps=complaint_steps,
                escalation_contacts=escalation_contacts,
                fetched_at=now,
            )
            resources.append(candidate)

        return resources

    def _parse_advocate(
        self,
        advocate: dict,
        complaint_steps: list[str],
        escalation_contacts: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a patient advocate entry into a ResourceCandidate.

        Args:
            advocate: Raw advocate data from JSON
            complaint_steps: List of complaint process steps
            escalation_contacts: Dict of escalation contact info
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this Patient Advocate.
        """
        facility_name = advocate.get("facility_name", "VA Medical Center")
        state = advocate.get("state")
        city = advocate.get("city")
        phone = advocate.get("phone")
        toll_free = advocate.get("toll_free")
        email = advocate.get("email")
        hours = advocate.get("hours")

        title = self._build_title(facility_name, state)
        description = self._build_description(facility_name, city, state)
        eligibility = self._build_eligibility()
        how_to_apply = self._build_how_to_apply(
            facility_name=facility_name,
            phone=phone,
            toll_free=toll_free,
            email=email,
            complaint_steps=complaint_steps,
            escalation_contacts=escalation_contacts,
        )

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=f"https://www.va.gov/find-locations/facility/{advocate.get('facility_id', '')}",
            org_name=facility_name,
            org_website="https://www.va.gov/health/patientadvocate/",
            address=advocate.get("address"),
            city=city,
            state=self._normalize_state(state),
            zip_code=advocate.get("zip_code"),
            categories=["legal"],  # Patient advocates help with complaints/appeals
            tags=self._build_tags(advocate),
            phone=self._normalize_phone(phone),
            email=email,
            hours=hours,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="local",
            states=[state] if state else None,
            raw_data=advocate,
            fetched_at=fetched_at,
        )

    def _build_title(self, facility_name: str, state: str | None) -> str:
        """Build resource title.

        Args:
            facility_name: Name of the VA facility
            state: State code

        Returns:
            Formatted title string.
        """
        if state:
            return f"Patient Advocate - {facility_name}"
        return f"Patient Advocate - {facility_name}"

    def _build_description(
        self,
        facility_name: str,
        city: str | None,
        state: str | None,
    ) -> str:
        """Build resource description.

        Args:
            facility_name: Name of the VA facility
            city: City name
            state: State code

        Returns:
            Formatted description string.
        """
        state_name = STATE_NAMES.get(state, state) if state else "your area"
        location = f"{city}, {state_name}" if city else state_name

        return (
            f"Patient Advocate at {facility_name} in {location}. "
            "Patient Advocates are trained professionals who help veterans and their "
            "families resolve concerns about any aspect of VA health care. They can "
            "assist with questions, problems, or special needs, and refer concerns "
            "to appropriate Medical Center staff for resolution. Patient Advocates "
            "provide a direct line of communication between veterans and VA leadership "
            "to ensure concerns are heard and addressed in a timely manner."
        )

    def _build_eligibility(self) -> str:
        """Build eligibility text.

        Returns:
            Eligibility string.
        """
        return (
            "All veterans and their families who receive care at VA health care "
            "facilities are eligible to contact Patient Advocates. No enrollment "
            "or appointment required. You do not need to be enrolled in VA health "
            "care to file a complaint or provide feedback about your experience."
        )

    def _build_how_to_apply(
        self,
        facility_name: str,
        phone: str | None,
        toll_free: str | None,
        email: str | None,
        complaint_steps: list[str],
        escalation_contacts: dict,
    ) -> str:
        """Build instructions for accessing Patient Advocate services.

        Args:
            facility_name: Name of the VA facility
            phone: Direct phone number
            toll_free: Toll-free phone number
            email: Email address
            complaint_steps: List of complaint process steps
            escalation_contacts: Dict of escalation contacts

        Returns:
            Formatted instruction string.
        """
        parts = []

        # Contact information
        contact_parts = []
        if phone:
            contact_parts.append(f"call {phone}")
        if toll_free and toll_free != phone:
            contact_parts.append(f"toll-free {toll_free}")
        if email:
            contact_parts.append(f"email {email}")

        if contact_parts:
            parts.append(f"Contact the Patient Advocate at {facility_name}: {', or '.join(contact_parts)}.")
        else:
            parts.append(f"Contact the Patient Advocate at {facility_name} during business hours.")

        # Complaint process steps
        if complaint_steps:
            parts.append("\n\nComplaint Process:")
            for i, step in enumerate(complaint_steps, 1):
                parts.append(f"\n{i}. {step}")

        # Escalation contacts
        national_hotline = escalation_contacts.get("national_hotline")
        white_house_hotline = escalation_contacts.get("white_house_hotline")
        ask_va_portal = escalation_contacts.get("ask_va_portal")

        parts.append("\n\nAdditional Resources:")
        if national_hotline:
            parts.append(f"\n- VA National Hotline: {national_hotline}")
        if white_house_hotline:
            parts.append(f"\n- White House VA Hotline: {white_house_hotline}")
        if ask_va_portal:
            parts.append(f"\n- Ask VA Portal: {ask_va_portal}")

        return "".join(parts)

    def _build_tags(self, advocate: dict) -> list[str]:
        """Build tags for the resource.

        Args:
            advocate: Raw advocate data

        Returns:
            List of tag strings.
        """
        tags = [
            "patient-advocate",
            "complaints",
            "va-health-care",
            "veteran-rights",
            "grievance",
            "feedback",
        ]

        facility_id = advocate.get("facility_id")
        if facility_id:
            tags.append(f"facility-{facility_id}")

        visn = advocate.get("visn")
        if visn:
            tags.append(f"visn-{visn}")

        return tags
