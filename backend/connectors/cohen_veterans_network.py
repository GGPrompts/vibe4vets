"""Cohen Veterans Network mental health clinic connector.

Imports clinic locations from the Cohen Veterans Network (CVN), which operates
22 clinics across 21 states providing free mental health services to post-9/11
veterans and their families.

Source: https://www.cohenveteransnetwork.org/clinics/
"""

from datetime import UTC, datetime

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Cohen Veterans Network clinic data
# Last updated: 2025-01-28
# Source: https://www.cohenveteransnetwork.org/clinics/
COHEN_CLINICS = [
    {
        "partner_org": "Alaska Behavioral Health",
        "clinic_name": "Cohen Clinic at Alaska Behavioral Health - Fairbanks",
        "address": "926 Aspen Street",
        "city": "Fairbanks",
        "state": "AK",
        "zip_code": "99709",
        "phone": "907-762-8668",
        "serves_states": ["AK"],
    },
    {
        "partner_org": "Alaska Behavioral Health",
        "clinic_name": "Cohen Clinic at Alaska Behavioral Health - Anchorage",
        "address": "1450 Muldoon Road, #111",
        "city": "Anchorage",
        "state": "AK",
        "zip_code": "99504",
        "phone": "907-762-8668",
        "serves_states": ["AK"],
    },
    {
        "partner_org": "VVSD",
        "clinic_name": "Cohen Clinic at VVSD - San Diego",
        "address": "8885 Rio San Diego Drive, Suite 301",
        "city": "San Diego",
        "state": "CA",
        "zip_code": "92108",
        "phone": "619-345-4611",
        "serves_states": ["CA"],
    },
    {
        "partner_org": "VVSD",
        "clinic_name": "Cohen Clinic at VVSD - Oceanside",
        "address": "3609 Ocean Ranch Blvd, Suite 120",
        "city": "Oceanside",
        "state": "CA",
        "zip_code": "92056",
        "phone": "760-418-4611",
        "serves_states": ["CA"],
    },
    {
        "partner_org": "VVSD",
        "clinic_name": "Cohen Clinic at VVSD - Los Angeles",
        "address": "20800 Madrona Avenue, Suite C-100",
        "city": "Torrance",
        "state": "CA",
        "zip_code": "90503",
        "phone": "213-642-4611",
        "serves_states": ["CA"],
    },
    {
        "partner_org": "Red Rock",
        "clinic_name": "Cohen Clinic at Red Rock - Colorado Springs",
        "address": "1915 Aerotech Drive, Suite 114",
        "city": "Colorado Springs",
        "state": "CO",
        "zip_code": "80916",
        "phone": "719-370-5141",
        "serves_states": ["CO"],
    },
    {
        "partner_org": "Easterseals",
        "clinic_name": "Cohen Clinic at Easterseals - Silver Spring",
        "address": "1420 Spring Street, Suite 300",
        "city": "Silver Spring",
        "state": "MD",
        "zip_code": "20910",
        "phone": "240-847-7500",
        "serves_states": ["DE", "DC", "MD", "NJ", "PA", "VA", "WV"],
    },
    {
        "partner_org": "Centerstone",
        "clinic_name": "Cohen Clinic at Centerstone - Jacksonville",
        "address": "7011 A.C. Skinner Parkway",
        "city": "Jacksonville",
        "state": "FL",
        "zip_code": "32256",
        "phone": "877-463-6505",
        "serves_states": ["FL"],
    },
    {
        "partner_org": "Aspire Health Partners",
        "clinic_name": "Cohen Clinic at Aspire Health Partners - Tampa",
        "address": "4520 Oak Fair Blvd, Suite 100",
        "city": "Tampa",
        "state": "FL",
        "zip_code": "33610",
        "phone": "813-542-5500",
        "serves_states": ["FL"],
    },
    {
        "partner_org": "Centerstone",
        "clinic_name": "Cohen Clinic at Centerstone - Hinesville",
        "address": "345 W. Memorial Drive",
        "city": "Hinesville",
        "state": "GA",
        "zip_code": "31313",
        "phone": "912-456-2010",
        "serves_states": ["GA"],
    },
    {
        "partner_org": "Endeavors",
        "clinic_name": "Cohen Clinic at Endeavors - Mililani",
        "address": "95-1091 Ainamakua Drive",
        "city": "Mililani",
        "state": "HI",
        "zip_code": "96789",
        "phone": "808-204-4020",
        "serves_states": ["HI"],
    },
    {
        "partner_org": "Centerstone",
        "clinic_name": "Cohen Clinic at Centerstone - Clarksville",
        "address": "775 Weatherly Drive",
        "city": "Clarksville",
        "state": "TN",
        "zip_code": "37043",
        "phone": "877-463-6505",
        "serves_states": ["KY", "TN"],
    },
    {
        "partner_org": "Hope for the Warriors",
        "clinic_name": "Cohen Clinic at Hope for the Warriors - Jacksonville",
        "address": "3245 Henderson Drive",
        "city": "Jacksonville",
        "state": "NC",
        "zip_code": "28546",
        "phone": "910-388-5232",
        "serves_states": ["NC"],
    },
    {
        "partner_org": "Centerstone",
        "clinic_name": "Cohen Clinic at Centerstone - Fayetteville",
        "address": "3505 Village Drive",
        "city": "Fayetteville",
        "state": "NC",
        "zip_code": "28304",
        "phone": "877-463-6505",
        "serves_states": ["NC", "SC"],
    },
    {
        "partner_org": "Red Rock",
        "clinic_name": "Cohen Clinic at Red Rock - Oklahoma City",
        "address": "1500 SW 104th Street",
        "city": "Oklahoma City",
        "state": "OK",
        "zip_code": "73159",
        "phone": "405-635-3888",
        "serves_states": ["OK"],
    },
    {
        "partner_org": "Red Rock",
        "clinic_name": "Cohen Clinic at Red Rock - Lawton",
        "address": "4202 S.W. Lee Blvd",
        "city": "Lawton",
        "state": "OK",
        "zip_code": "73505",
        "phone": "580-771-2662",
        "serves_states": ["OK"],
    },
    {
        "partner_org": "Metrocare",
        "clinic_name": "Cohen Clinic at Metrocare - Dallas",
        "address": "9696 Skillman Street, Suite 170",
        "city": "Dallas",
        "state": "TX",
        "zip_code": "75243",
        "phone": "469-680-3500",
        "serves_states": ["TX"],
    },
    {
        "partner_org": "Endeavors",
        "clinic_name": "Cohen Clinic at Endeavors - San Antonio",
        "address": "6333 De Zavala Road, Suite B101",
        "city": "San Antonio",
        "state": "TX",
        "zip_code": "78249",
        "phone": "210-399-4838",
        "serves_states": ["TX"],
    },
    {
        "partner_org": "Endeavors",
        "clinic_name": "Cohen Clinic at Endeavors - Killeen",
        "address": "1103 West Stan Schlueter Loop, Building A, Suite 100",
        "city": "Killeen",
        "state": "TX",
        "zip_code": "76549",
        "phone": "254-213-7847",
        "serves_states": ["TX"],
    },
    {
        "partner_org": "Endeavors",
        "clinic_name": "Cohen Clinic at Endeavors - El Paso",
        "address": "12135 Pebble Hills Blvd, Suite 110",
        "city": "El Paso",
        "state": "TX",
        "zip_code": "79936",
        "phone": "915-320-1390",
        "serves_states": ["NM", "TX"],
    },
    {
        "partner_org": "The Up Center",
        "clinic_name": "Cohen Clinic at The Up Center - Virginia Beach",
        "address": "828 Healthy Way, Suite 105",
        "city": "Virginia Beach",
        "state": "VA",
        "zip_code": "23462",
        "phone": "757-965-8686",
        "serves_states": ["VA"],
    },
    {
        "partner_org": "Valley Cities",
        "clinic_name": "Cohen Clinic at Valley Cities - Lakewood",
        "address": "6103 Mt. Tacoma Drive",
        "city": "Lakewood",
        "state": "WA",
        "zip_code": "98499",
        "phone": "253-215-7070",
        "serves_states": ["WA"],
    },
]


class CohenVeteransNetworkConnector(BaseConnector):
    """Connector for Cohen Veterans Network mental health clinics.

    The Cohen Veterans Network operates 22 clinics across the United States,
    providing free, confidential mental health care to post-9/11 Veterans,
    active duty service members, and their families.

    Services include:
    - Individual therapy for PTSD, depression, anxiety
    - Family and couples counseling
    - Child and adolescent therapy
    - Relationship counseling
    - Anger management
    - Transition support

    All services are provided at no cost, regardless of discharge status,
    and do not require VA enrollment.
    """

    # National contact number
    NATIONAL_PHONE = "844-336-4226"

    # Standard services offered at all clinics
    SERVICES = [
        "PTSD treatment",
        "depression therapy",
        "anxiety treatment",
        "family counseling",
        "couples therapy",
        "child and adolescent therapy",
        "relationship counseling",
        "anger management",
        "military sexual trauma (MST) support",
        "transition adjustment",
    ]

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Cohen Veterans Network",
            url="https://www.cohenveteransnetwork.org/",
            tier=2,  # Established nonprofit
            frequency="monthly",  # Clinic info changes infrequently
            terms_url="https://www.cohenveteransnetwork.org/privacy-policy/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Return Cohen Veterans Network clinic resources.

        Returns:
            List of ResourceCandidate objects for each clinic location.
        """
        now = datetime.now(UTC)
        resources: list[ResourceCandidate] = []

        for clinic in COHEN_CLINICS:
            candidate = self._parse_clinic(clinic, fetched_at=now)
            resources.append(candidate)

        return resources

    def _parse_clinic(
        self,
        clinic: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse clinic data into a ResourceCandidate.

        Args:
            clinic: Clinic data dictionary.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this clinic.
        """
        clinic_name = clinic["clinic_name"]
        partner_org = clinic["partner_org"]
        city = clinic["city"]
        state = clinic["state"]
        address = clinic["address"]
        zip_code = clinic["zip_code"]
        phone = clinic["phone"]
        serves_states = clinic["serves_states"]

        # Build full address
        full_address = f"{address}, {city}, {state} {zip_code}"

        title = f"{clinic_name} - Free Mental Health Care"
        description = self._build_description(clinic_name, city, state, serves_states)
        eligibility = self._build_eligibility()
        how_to_apply = self._build_how_to_apply(clinic_name, phone)
        tags = self._build_tags(state, serves_states)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://www.cohenveteransnetwork.org/clinics/",
            org_name="Cohen Veterans Network",
            org_website="https://www.cohenveteransnetwork.org/",
            address=full_address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["mentalHealth"],
            tags=tags,
            phone=self._normalize_phone(phone),
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="local",
            states=serves_states,
            raw_data={
                "clinic_name": clinic_name,
                "partner_org": partner_org,
                "serves_states": serves_states,
                "national_phone": self.NATIONAL_PHONE,
            },
            fetched_at=fetched_at,
        )

    def _build_description(
        self,
        clinic_name: str,
        city: str,
        state: str,
        serves_states: list[str],
    ) -> str:
        """Build clinic description.

        Args:
            clinic_name: Full clinic name.
            city: City where clinic is located.
            state: State code.
            serves_states: List of state codes served by this clinic.

        Returns:
            Formatted description string.
        """
        parts = []

        # Main description
        parts.append(
            f"The {clinic_name} in {city}, {state} provides free, confidential "
            "mental health care to post-9/11 Veterans, active duty service members, "
            "National Guard, Reserves, and their families."
        )

        # Coverage area for multi-state clinics
        if len(serves_states) > 1:
            state_names = [self._state_code_to_name(s) for s in serves_states]
            parts.append(f"This clinic serves Veterans in {', '.join(state_names)}.")

        # Services
        services_str = ", ".join(self.SERVICES[:5])
        parts.append(
            f"Services include {services_str}, and more. Treatment is provided "
            "by licensed clinicians experienced in military culture."
        )

        # Cost emphasis
        parts.append(
            "All services are completely free, regardless of discharge status. "
            "No VA enrollment or referral required."
        )

        return " ".join(parts)

    def _build_eligibility(self) -> str:
        """Build eligibility text.

        Returns:
            Eligibility description string.
        """
        return (
            "Post-9/11 Veterans (served after September 10, 2001), active duty "
            "service members, National Guard, Reserves, and their family members "
            "(spouse, partner, children, parents, siblings, caregivers). "
            "No discharge status restrictions. No VA enrollment required. "
            "Services are free regardless of income or insurance status."
        )

    def _build_how_to_apply(self, clinic_name: str, phone: str) -> str:
        """Build how-to-apply text.

        Args:
            clinic_name: Clinic name.
            phone: Clinic phone number.

        Returns:
            How to apply description string.
        """
        return (
            f"Call {phone} to schedule an appointment at {clinic_name}. "
            f"You can also call the national line at {self.NATIONAL_PHONE} "
            "to find the nearest clinic. Walk-ins may be accommodated. "
            "Visit cohenveteransnetwork.org for online appointment requests."
        )

    def _build_tags(self, state: str, serves_states: list[str]) -> list[str]:
        """Build tags list.

        Args:
            state: Primary state code.
            serves_states: All served state codes.

        Returns:
            List of tag strings.
        """
        tags = [
            "mental-health",
            "free-services",
            "post-9/11",
            "ptsd",
            "depression",
            "anxiety",
            "family-support",
            "couples-therapy",
            "no-va-enrollment",
            "cohen-veterans-network",
        ]

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
