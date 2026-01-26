"""County Veteran Service Officer (CVSO) connector.

Imports CVSO data from curated reference data. CVSOs are local government
employees who help veterans with benefits claims, often located at county
courthouses or government buildings.

Sources:
- NACVSO (National Association of County Veteran Service Officers)
- State-specific CVSO directories
- VA accredited representative database

Note: CVSOs must be VA-accredited to represent veterans in claims matters.
NACVSO represents approximately 2,400 county and state employees from 29 states.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class CVSOConnector(BaseConnector):
    """Connector for County Veteran Service Officer (CVSO) data.

    Parses the cvso_directory.json file containing CVSO contact information
    organized by state and county. CVSOs are local government employees who
    provide free assistance to veterans with:

    - VA disability compensation claims
    - Pension and survivor benefits
    - Healthcare enrollment
    - Appeals and higher-level reviews
    - Referrals to local resources

    Data fields:
        - state: Two-letter state code
        - county: County or parish name
        - office_name: Official office name
        - officer_name: CVSO name (may be vacant)
        - address: Office street address
        - city: City name
        - zip_code: ZIP code
        - phone: Office phone number
        - email: Office email (if available)
        - hours: Office hours (if available)
        - website: Office or county website (if available)
        - services: List of services offered
    """

    DEFAULT_DATA_PATH = "data/reference/cvso_directory.json"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to JSON file. Falls back to DEFAULT_DATA_PATH.
        """
        if data_path is None:
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
            name="County Veteran Service Officers (CVSO)",
            url="https://www.nacvso.org/",
            tier=3,  # County/state-level government employees
            frequency="quarterly",  # CVSOs change infrequently
            terms_url="https://www.nacvso.org/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse CVSO data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"CVSO data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for cvso in data.get("cvsos", []):
            candidate = self._parse_cvso(
                state=cvso.get("state"),
                county=cvso.get("county"),
                office_name=cvso.get("office_name"),
                officer_name=cvso.get("officer_name"),
                address=cvso.get("address"),
                city=cvso.get("city"),
                zip_code=cvso.get("zip_code"),
                phone=cvso.get("phone"),
                email=cvso.get("email"),
                hours=cvso.get("hours"),
                website=cvso.get("website"),
                services=cvso.get("services", []),
                fetched_at=now,
            )
            resources.append(candidate)

        return resources

    def _parse_cvso(
        self,
        state: str | None,
        county: str | None,
        office_name: str | None,
        officer_name: str | None,
        address: str | None,
        city: str | None,
        zip_code: str | None,
        phone: str | None,
        email: str | None,
        hours: str | None,
        website: str | None,
        services: list[str],
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a CVSO entry into a ResourceCandidate.

        Args:
            state: Two-letter state code
            county: County or parish name
            office_name: Official office name
            officer_name: Current CVSO name
            address: Office street address
            city: City name
            zip_code: ZIP code
            phone: Office phone number
            email: Office email address
            hours: Office hours
            website: Office or county website
            services: List of services offered
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this CVSO office.
        """
        state_name = self._get_state_name(state)
        title = self._build_title(county, state, office_name)
        description = self._build_description(county, state_name, office_name, officer_name, services)

        # Build full address string
        full_address = None
        if address:
            full_address = address
            if city and state and zip_code:
                full_address = f"{address}, {city}, {state} {zip_code}"
            elif city and state:
                full_address = f"{address}, {city}, {state}"

        # Build source URL - prefer office website, fall back to NACVSO
        source_url = website or "https://www.nacvso.org/county-veterans-service-officers"

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name=office_name or f"{county} County Veterans Service Office",
            org_website=website,
            address=full_address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["benefits"],
            tags=self._build_tags(state, county, services),
            phone=self._normalize_phone(phone),
            email=email,
            hours=hours,
            eligibility=self._build_eligibility(state_name, county),
            how_to_apply=self._build_how_to_apply(county, office_name, phone, email, website),
            scope="local",
            states=[state] if state else None,
            raw_data={
                "state": state,
                "county": county,
                "office_name": office_name,
                "officer_name": officer_name,
                "address": address,
                "city": city,
                "zip_code": zip_code,
                "phone": phone,
                "email": email,
                "hours": hours,
                "website": website,
                "services": services,
            },
            fetched_at=fetched_at,
        )

    def _get_state_name(self, state: str | None) -> str | None:
        """Get full state name from code."""
        if not state:
            return None

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
        return state_names.get(state.upper())

    def _build_title(
        self,
        county: str | None,
        state: str | None,
        office_name: str | None,
    ) -> str:
        """Build resource title.

        Args:
            county: County name
            state: State code
            office_name: Official office name

        Returns:
            Formatted title string.
        """
        if office_name and county and state:
            return f"{county} County CVSO ({state})"
        elif county and state:
            return f"{county} County Veterans Service Office ({state})"
        elif office_name:
            return office_name
        return "County Veterans Service Office"

    def _build_description(
        self,
        county: str | None,
        state_name: str | None,
        office_name: str | None,
        officer_name: str | None,
        services: list[str],
    ) -> str:
        """Build resource description.

        Args:
            county: County name
            state_name: Full state name
            office_name: Official office name
            officer_name: Current CVSO name
            services: List of services offered

        Returns:
            Formatted description string.
        """
        parts = []

        # Opening description
        if county and state_name:
            parts.append(
                f"The {county} County Veterans Service Office in {state_name} "
                "provides free assistance to veterans, their dependents, and survivors "
                "with VA benefits claims and local resources."
            )
        else:
            parts.append(
                "County Veterans Service Office providing free assistance to veterans, "
                "their dependents, and survivors with VA benefits claims and local resources."
            )

        # Officer name if available and not vacant
        if officer_name and officer_name.lower() not in ["vacant", "position not filled", "tbd"]:
            parts.append(f"Current County Veteran Service Officer: {officer_name}.")

        # Core services description
        parts.append(
            "CVSOs are accredited by the VA to help veterans file disability "
            "compensation claims, pension applications, healthcare enrollment, "
            "and appeals. All services are provided at no cost."
        )

        # Specific services if provided
        if services:
            services_text = ", ".join(services[:8])  # Limit to 8 services
            if len(services) > 8:
                services_text += f", and {len(services) - 8} more"
            parts.append(f"Services include: {services_text}.")

        return " ".join(parts)

    def _build_eligibility(
        self,
        state_name: str | None,
        county: str | None,
    ) -> str:
        """Build eligibility description.

        Args:
            state_name: Full state name
            county: County name

        Returns:
            Eligibility description string.
        """
        location = f"{county} County, {state_name}" if county and state_name else "your county"

        return (
            f"Veterans, service members, and their dependents and survivors residing in {location}. "
            "CVSOs can assist regardless of discharge characterization, service era, "
            "or current VA enrollment status. While CVSOs primarily serve their county's "
            "residents, they will often assist any veteran who visits their office."
        )

    def _build_how_to_apply(
        self,
        county: str | None,
        office_name: str | None,
        phone: str | None,
        email: str | None,
        website: str | None,
    ) -> str:
        """Build how to apply instructions.

        Args:
            county: County name
            office_name: Official office name
            phone: Office phone number
            email: Office email address
            website: Office or county website

        Returns:
            How to apply instructions string.
        """
        parts = []
        office_display = office_name or f"{county} County Veterans Service Office"

        # Primary contact method
        if phone:
            parts.append(f"Call {office_display} at {phone} to schedule an appointment.")
        elif email:
            parts.append(f"Email {office_display} at {email} to schedule an appointment.")
        else:
            parts.append(f"Contact {office_display} to schedule an appointment.")

        # Additional contact methods
        if email and phone:
            parts.append(f"Email: {email}")
        if website:
            parts.append(f"Website: {website}")

        # What to bring
        parts.append(
            "Bring your DD-214 (discharge papers), any VA correspondence, and medical records related to your claim."
        )

        return " ".join(parts)

    def _build_tags(
        self,
        state: str | None,
        county: str | None,
        services: list[str],
    ) -> list[str]:
        """Build tags list.

        Args:
            state: Two-letter state code
            county: County name
            services: List of services offered

        Returns:
            List of tag strings.
        """
        tags = [
            "cvso",
            "county-veteran-service-officer",
            "benefits-assistance",
            "va-claims",
            "free-services",
            "accredited-representative",
        ]

        if state:
            tags.append(f"state-{state.lower()}")

        if county:
            county_slug = county.lower().replace(" ", "-").replace("'", "")
            tags.append(f"county-{county_slug}")

        # Add service-based tags
        service_tag_map = {
            "disability": "disability-claims",
            "pension": "pension-claims",
            "healthcare": "healthcare-enrollment",
            "education": "education-benefits",
            "survivor": "survivor-benefits",
            "appeal": "va-appeals",
            "housing": "housing-assistance",
            "employment": "employment-services",
        }

        services_lower = " ".join(services).lower()
        for keyword, tag in service_tag_map.items():
            if keyword in services_lower:
                tags.append(tag)

        return list(set(tags))  # Deduplicate
