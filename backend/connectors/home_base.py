"""Home Base veteran mental health program connector.

Imports locations from Home Base, a program of Massachusetts General Hospital
and the Red Sox Foundation providing intensive mental health treatment for
post-9/11 veterans, service members, and their families.

Source: https://homebase.org/
"""

from datetime import UTC, datetime

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Home Base location data
# Last updated: 2026-01-29
# Source: https://homebase.org/contact/
HOME_BASE_LOCATIONS = [
    {
        "name": "Home Base National Center of Excellence",
        "address": "One Constitution Wharf, Suite 140",
        "city": "Charlestown",
        "state": "MA",
        "zip_code": "02129",
        "phone": "617-724-5202",
        "email": "homebaseprogram@partners.org",
        "serves_states": ["MA", "ME", "NH", "VT", "RI", "CT"],
        "is_headquarters": True,
    },
    {
        "name": "Home Base Florida",
        "address": "Kleist Center - Home Base Veterans Program, 10501 FGCU Boulevard South",
        "city": "Fort Myers",
        "state": "FL",
        "zip_code": "33965",
        "phone": "239-338-8389",
        "email": "homebasefl@partners.org",
        "serves_states": ["FL"],
        "is_headquarters": False,
    },
    {
        "name": "Home Base Arizona",
        "address": "550 North 3rd Street, Mail Code 9020",
        "city": "Phoenix",
        "state": "AZ",
        "zip_code": "85004",
        "phone": "833-865-0500",
        "email": "hbarizona@massgeneralbrigham.org",
        "serves_states": ["AZ"],
        "is_headquarters": False,
    },
]


class HomeBaseConnector(BaseConnector):
    """Connector for Home Base veteran mental health program.

    Home Base is a partnership between Massachusetts General Hospital and the
    Red Sox Foundation, providing world-class clinical care, wellness, and
    support for post-9/11 veterans, service members, and their families.

    Key programs include:
    - Intensive Clinical Program (ICP): 2-week comprehensive treatment
    - Comprehensive Brain Health and Trauma Program (ComBHaT)
    - Intensive Clinical Program for Families of the Fallen
    - Outpatient clinical services
    - Warrior Health and Fitness programs
    - Family support and resiliency programs

    Since 2009, Home Base has served over 50,000 veterans and families across
    all 50 states, with a 95% graduation rate for national clinical programs.

    All care is provided at no out-of-pocket cost to veterans and families.
    """

    # National contact (Massachusetts headquarters)
    NATIONAL_PHONE = "617-724-5202"

    # Programs offered
    PROGRAMS = [
        "Intensive Clinical Program (ICP) - 2-week comprehensive treatment",
        "Comprehensive Brain Health and Trauma Program (ComBHaT)",
        "Intensive Clinical Program for Families of the Fallen",
        "Outpatient clinical services",
        "Warrior Health and Fitness programs",
        "Family and youth resiliency programs",
    ]

    # Services provided
    SERVICES = [
        "PTSD treatment",
        "traumatic brain injury (TBI) care",
        "depression treatment",
        "anxiety treatment",
        "military sexual trauma (MST) support",
        "substance use support",
        "family counseling",
        "wellness programs",
    ]

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Home Base",
            url="https://homebase.org/",
            tier=2,  # Established nonprofit/hospital partnership
            frequency="monthly",  # Location info changes infrequently
            terms_url="https://homebase.org/privacy-policy/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Return Home Base location resources.

        Returns:
            List of ResourceCandidate objects for each location.
        """
        now = datetime.now(UTC)
        resources: list[ResourceCandidate] = []

        for location in HOME_BASE_LOCATIONS:
            candidate = self._parse_location(location, fetched_at=now)
            resources.append(candidate)

        return resources

    def _parse_location(
        self,
        location: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse location data into a ResourceCandidate.

        Args:
            location: Location data dictionary.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this location.
        """
        name = location["name"]
        city = location["city"]
        state = location["state"]
        address = location["address"]
        zip_code = location["zip_code"]
        phone = location["phone"]
        email = location["email"]
        serves_states = location["serves_states"]
        is_headquarters = location["is_headquarters"]

        # Build full address
        full_address = f"{address}, {city}, {state} {zip_code}"

        title = f"{name} - Free Veteran Mental Health Care"
        description = self._build_description(name, city, state, serves_states, is_headquarters)
        eligibility = self._build_eligibility()
        how_to_apply = self._build_how_to_apply(name, phone, email)
        tags = self._build_tags(state, serves_states, is_headquarters)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://homebase.org/",
            org_name="Home Base (MGH/Red Sox Foundation)",
            org_website="https://homebase.org/",
            address=full_address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["mentalHealth"],
            tags=tags,
            phone=self._normalize_phone(phone),
            email=email,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="local",
            states=serves_states,
            raw_data={
                "location_name": name,
                "serves_states": serves_states,
                "national_phone": self.NATIONAL_PHONE,
                "email": email,
                "is_headquarters": is_headquarters,
                "programs": self.PROGRAMS,
            },
            fetched_at=fetched_at,
        )

    def _build_description(
        self,
        name: str,
        city: str,
        state: str,
        serves_states: list[str],
        is_headquarters: bool,
    ) -> str:
        """Build location description.

        Args:
            name: Location name.
            city: City where location is located.
            state: State code.
            serves_states: List of state codes served by this location.
            is_headquarters: Whether this is the main headquarters.

        Returns:
            Formatted description string.
        """
        parts = []

        # Main description
        if is_headquarters:
            parts.append(
                f"{name} in {city}, {state} is the flagship location of Home Base, "
                "a partnership between Massachusetts General Hospital and the Red Sox "
                "Foundation providing world-class mental health care for post-9/11 "
                "veterans, service members, and their families."
            )
        else:
            parts.append(
                f"{name} in {city}, {state} provides mental health care and support "
                "for post-9/11 veterans, service members, and their families as part "
                "of the Home Base program, a partnership between Massachusetts General "
                "Hospital and the Red Sox Foundation."
            )

        # Program highlights
        parts.append(
            "The Intensive Clinical Program (ICP) is a 2-week comprehensive treatment "
            "program addressing PTSD, traumatic brain injury (TBI), and related conditions. "
            "Home Base has served over 50,000 veterans and families with a 95% graduation "
            "rate and 93% recommendation rate."
        )

        # Coverage area for multi-state locations
        if len(serves_states) > 1:
            state_names = [self._state_code_to_name(s) for s in serves_states]
            parts.append(f"This location serves veterans throughout New England: {', '.join(state_names)}.")

        # Additional services
        parts.append(
            "Additional programs include outpatient clinical services, Comprehensive "
            "Brain Health and Trauma Program (ComBHaT), family resiliency programs, "
            "and Warrior Health and Fitness wellness initiatives."
        )

        # Cost emphasis
        parts.append(
            "All care is provided at no out-of-pocket cost, regardless of insurance "
            "or VA enrollment status. Home Base also serves families of the fallen "
            "through specialized intensive programs."
        )

        return " ".join(parts)

    def _build_eligibility(self) -> str:
        """Build eligibility text.

        Returns:
            Eligibility description string.
        """
        return (
            "Post-9/11 veterans (served after September 10, 2001), active duty "
            "service members, National Guard, Reserves, and their family members. "
            "Also serves families of the fallen. No VA enrollment required. "
            "All care is provided at no out-of-pocket cost regardless of insurance "
            "status or discharge type. Home Base is also a Warrior Care Network "
            "partner through Wounded Warrior Project."
        )

    def _build_how_to_apply(self, name: str, phone: str, email: str) -> str:
        """Build how-to-apply text.

        Args:
            name: Location name.
            phone: Location phone number.
            email: Location email address.

        Returns:
            How to apply description string.
        """
        return (
            f"Call {phone} to learn more about programs at {name}, or email "
            f"{email}. You can also visit homebase.org and complete the 'Get Care' "
            "form to request services. A Veteran Outreach Coordinator will contact "
            "you to discuss your needs. For emergencies, go to the nearest ER or "
            "call the Veterans Crisis Line at 988, then press 1."
        )

    def _build_tags(
        self,
        state: str,
        serves_states: list[str],
        is_headquarters: bool,
    ) -> list[str]:
        """Build tags list.

        Args:
            state: Primary state code.
            serves_states: All served state codes.
            is_headquarters: Whether this is the main headquarters.

        Returns:
            List of tag strings.
        """
        tags = [
            "mental-health",
            "free-services",
            "post-9/11",
            "ptsd",
            "tbi",
            "traumatic-brain-injury",
            "depression",
            "anxiety",
            "mst",
            "family-support",
            "no-va-enrollment",
            "home-base",
            "mass-general",
            "red-sox-foundation",
            "intensive-program",
            "warrior-care-network",
        ]

        if is_headquarters:
            tags.append("headquarters")

        # Add state tags
        for s in serves_states:
            tags.append(f"state-{s.lower()}")

        return tags

    def _state_code_to_name(self, code: str) -> str:
        """Convert state code to full name.

        Args:
            code: Two-letter state code.

        Returns:
            Full state name or the code if unknown.
        """
        state_names = {
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
        return state_names.get(code, code)
