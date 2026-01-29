"""Boulder Crest Foundation PATHH program connector.

Imports locations from Boulder Crest Foundation, which operates residential
PTSD treatment programs using a Posttraumatic Growth (PTG) model. Free for
combat veterans and first responders.

Source: https://bouldercrest.org/
"""

from datetime import UTC, datetime

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Boulder Crest Foundation location data
# Last updated: 2025-01-29
# Source: https://bouldercrest.org/contact/
BOULDER_CREST_LOCATIONS = [
    {
        "name": "Boulder Crest Virginia",
        "address": "18370 Bluemont Village Ln",
        "city": "Bluemont",
        "state": "VA",
        "zip_code": "20135",
        "phone": "540-554-2727",
        "serves_states": ["VA", "MD", "DC", "WV", "PA", "NC"],
    },
    {
        "name": "Boulder Crest Arizona",
        "address": "415 Gardner Canyon Rd",
        "city": "Sonoita",
        "state": "AZ",
        "zip_code": "85637",
        "phone": "520-455-4668",
        "serves_states": ["AZ", "NM", "NV", "CA", "CO", "UT", "TX"],
    },
]


class BoulderCrestConnector(BaseConnector):
    """Connector for Boulder Crest Foundation PATHH program.

    Boulder Crest Foundation operates rural retreat locations offering the
    Warrior PATHH (Progressive and Alternative Training for Helping Heroes)
    program - a 90-day trauma recovery program grounded in Posttraumatic
    Growth (PTG) science.

    Programs include:
    - Warrior PATHH: 90-day program (5-day in-person initiation + 90-day journey)
    - Family Rest & Reconnection: 2-7 night retreats for combat veterans/families
    - Struggle Well: Agency-focused programs (1, 2, and 5-day formats)

    All programs for combat veterans and first responders are completely free.
    The program has demonstrated a 58% reduction in PTSD symptoms for graduates.
    """

    # National contact number (Virginia headquarters)
    NATIONAL_PHONE = "540-554-2727"

    # Programs offered
    PROGRAMS = [
        "Warrior PATHH (90-day trauma recovery)",
        "Family Rest & Reconnection retreats",
        "Struggle Well programs",
        "Posttraumatic Growth training",
    ]

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Boulder Crest Foundation",
            url="https://bouldercrest.org/",
            tier=2,  # Established nonprofit
            frequency="monthly",  # Location info changes infrequently
            terms_url="https://bouldercrest.org/privacy-policy/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Return Boulder Crest location resources.

        Returns:
            List of ResourceCandidate objects for each location.
        """
        now = datetime.now(UTC)
        resources: list[ResourceCandidate] = []

        for location in BOULDER_CREST_LOCATIONS:
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
        serves_states = location["serves_states"]

        # Build full address
        full_address = f"{address}, {city}, {state} {zip_code}"

        title = f"{name} - Warrior PATHH Program (Free PTSD Treatment)"
        description = self._build_description(name, city, state, serves_states)
        eligibility = self._build_eligibility()
        how_to_apply = self._build_how_to_apply(name, phone)
        tags = self._build_tags(state, serves_states)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://bouldercrest.org/",
            org_name="Boulder Crest Foundation",
            org_website="https://bouldercrest.org/",
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
                "location_name": name,
                "serves_states": serves_states,
                "national_phone": self.NATIONAL_PHONE,
                "program": "Warrior PATHH",
            },
            fetched_at=fetched_at,
        )

    def _build_description(
        self,
        name: str,
        city: str,
        state: str,
        serves_states: list[str],
    ) -> str:
        """Build location description.

        Args:
            name: Location name.
            city: City where location is located.
            state: State code.
            serves_states: List of state codes served by this location.

        Returns:
            Formatted description string.
        """
        parts = []

        # Main description
        parts.append(
            f"{name} in {city}, {state} offers the Warrior PATHH (Progressive and "
            "Alternative Training for Helping Heroes) program - a 90-day trauma "
            "recovery journey grounded in Posttraumatic Growth (PTG) science."
        )

        # Program structure
        parts.append(
            "The program begins with a 5-day in-person initiation at the rural "
            "retreat, followed by continued support over 90 days. Graduates have "
            "experienced a 58% reduction in PTSD symptoms."
        )

        # Coverage area for multi-state locations
        if len(serves_states) > 1:
            state_names = [self._state_code_to_name(s) for s in serves_states[:4]]
            if len(serves_states) > 4:
                parts.append(
                    f"This location serves participants from {', '.join(state_names)}, "
                    "and surrounding states."
                )
            else:
                parts.append(
                    f"This location serves participants from "
                    f"{', '.join(state_names)}."
                )

        # Additional programs
        parts.append(
            "Boulder Crest also offers Family Rest & Reconnection retreats "
            "(2-7 nights for combat veterans and their families) and Struggle Well "
            "agency programs."
        )

        # Cost emphasis
        parts.append(
            "All programs for combat veterans and first responders are completely "
            "free, including lodging, meals, and programming."
        )

        return " ".join(parts)

    def _build_eligibility(self) -> str:
        """Build eligibility text.

        Returns:
            Eligibility description string.
        """
        return (
            "Combat veterans (any era), active-duty military, and first responders "
            "(firefighters, police, EMS, dispatchers) struggling with trauma, PTSD, "
            "or the invisible wounds of service. Family members may participate in "
            "Family Rest & Reconnection programs. All programs for eligible "
            "participants are completely free, including travel assistance, lodging, "
            "meals, and programming. No VA enrollment required."
        )

    def _build_how_to_apply(self, name: str, phone: str) -> str:
        """Build how-to-apply text.

        Args:
            name: Location name.
            phone: Location phone number.

        Returns:
            How to apply description string.
        """
        return (
            f"Call {phone} to learn more about the Warrior PATHH program at {name}. "
            "You can also visit bouldercrest.org to submit an inquiry form. "
            "Program staff will guide you through the application process and help "
            "determine the best program fit. Travel assistance may be available for "
            "those who qualify."
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
            "ptsd",
            "ptsd-treatment",
            "posttraumatic-growth",
            "trauma-recovery",
            "residential-program",
            "retreat",
            "combat-veterans",
            "first-responders",
            "family-support",
            "warrior-pathh",
            "boulder-crest",
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
