"""Headstrong Project PTSD treatment connector.

Imports service areas from The Headstrong Project, which provides free,
confidential, barrier-free mental health treatment for Veterans and their families.

Source: https://theheadstrongproject.org/
Research: backend/data/reference/research/veteran-mental-health.json
"""

from datetime import UTC, datetime

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# States with in-person treatment availability
# Source: Headstrong website and veteran-mental-health.json research
# Last updated: 2026-01-29
HEADSTRONG_IN_PERSON_STATES = [
    "AZ",  # Arizona
    "CA",  # California
    "CO",  # Colorado
    "DC",  # District of Columbia
    "FL",  # Florida
    "GA",  # Georgia
    "ID",  # Idaho
    "IL",  # Illinois
    "MD",  # Maryland
    "NJ",  # New Jersey
    "NY",  # New York
    "NC",  # North Carolina
    "OR",  # Oregon
    "PA",  # Pennsylvania
    "TX",  # Texas
]

# All US state codes for telehealth coverage
ALL_US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
    "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]


class HeadstrongConnector(BaseConnector):
    """Connector for The Headstrong Project PTSD treatment services.

    The Headstrong Project provides free, confidential, barrier-free mental
    health treatment for Veterans of all eras (any discharge status), service
    members, and their family members.

    Key features:
    - 30 free sessions per trauma type
    - Evidence-based therapies: CPT, EMDR, Prolonged Exposure
    - In-person treatment in 15 states + DC
    - Nationwide telehealth coverage
    - Contact within 2 business days
    - First session within 2 weeks

    Data source: Reference data compiled from website and research.
    No public API available.
    """

    # Contact information
    WEBSITE = "https://theheadstrongproject.org/"
    GET_HELP_URL = "https://theheadstrongproject.org/get-help/"

    # Treatment modalities offered
    TREATMENT_MODALITIES = [
        "Cognitive Processing Therapy (CPT)",
        "Eye Movement Desensitization and Reprocessing (EMDR)",
        "Prolonged Exposure Therapy",
    ]

    # Services provided
    SERVICES = [
        "PTSD treatment",
        "trauma therapy",
        "anxiety treatment",
        "depression treatment",
        "military sexual trauma (MST) support",
        "moral injury support",
    ]

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="The Headstrong Project",
            url=self.WEBSITE,
            tier=2,  # Established nonprofit
            frequency="monthly",  # Service areas change infrequently
            terms_url="https://theheadstrongproject.org/privacy-policy/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Return Headstrong Project resources.

        Creates:
        1. One national telehealth resource
        2. Individual resources for each state with in-person services

        Returns:
            List of ResourceCandidate objects.
        """
        now = datetime.now(UTC)
        resources: list[ResourceCandidate] = []

        # Add national telehealth resource
        resources.append(self._create_telehealth_resource(fetched_at=now))

        # Add state-specific in-person resources
        for state in HEADSTRONG_IN_PERSON_STATES:
            resources.append(self._create_in_person_resource(state, fetched_at=now))

        return resources

    def _create_telehealth_resource(self, fetched_at: datetime) -> ResourceCandidate:
        """Create the national telehealth resource.

        Args:
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for nationwide telehealth services.
        """
        title = "The Headstrong Project - Free PTSD Treatment (Nationwide Telehealth)"

        description = (
            "The Headstrong Project provides free, confidential, barrier-free "
            "mental health treatment for Veterans, service members, and their families "
            "via telehealth anywhere in the United States. Veterans receive 30 free "
            "sessions per trauma type with expert clinicians trained in evidence-based "
            "therapies including Cognitive Processing Therapy (CPT), EMDR, and Prolonged "
            "Exposure. Headstrong matches Veterans with a clinician within 2 business days "
            "and the first session typically occurs within 2 weeks. In 2024, Headstrong "
            "provided over 44,000 free sessions with a 97% client return rate and 89% "
            "reporting treatment as effective."
        )

        eligibility = (
            "Veterans of all eras (any service period), any discharge status (including "
            "other-than-honorable), active duty service members, National Guard, Reserves, "
            "and family members (spouses, partners, children, parents, siblings, caregivers). "
            "No VA enrollment required. No cost to Veterans or families."
        )

        how_to_apply = (
            "Visit theheadstrongproject.org/get-help/ to fill out the intake form. "
            "A Headstrong team member will contact you within 2 business days to match "
            "you with a clinician. Your first session is typically scheduled within 2 weeks. "
            "All services are free and confidential."
        )

        tags = [
            "headstrong",
            "ptsd",
            "free-therapy",
            "cpt",
            "emdr",
            "telehealth",
            "prolonged-exposure",
            "trauma",
            "mental-health",
            "free-services",
            "all-eras",
            "any-discharge",
            "family-support",
            "nationwide",
        ]

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=self.GET_HELP_URL,
            org_name="The Headstrong Project",
            org_website=self.WEBSITE,
            categories=["mentalHealth"],
            tags=tags,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="national",
            states=ALL_US_STATES,
            raw_data={
                "service_type": "telehealth",
                "sessions_offered": 30,
                "cost": "free",
                "treatment_modalities": self.TREATMENT_MODALITIES,
                "response_time": "2 business days",
                "first_session": "within 2 weeks",
            },
            fetched_at=fetched_at,
        )

    def _create_in_person_resource(
        self,
        state: str,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Create an in-person resource for a specific state.

        Args:
            state: Two-letter state code.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for in-person services in the state.
        """
        state_name = self._state_code_to_name(state)

        title = f"The Headstrong Project - Free PTSD Treatment ({state_name})"

        description = (
            f"The Headstrong Project provides free, confidential, barrier-free "
            f"mental health treatment for Veterans, service members, and their families "
            f"in {state_name}. Both in-person and telehealth appointments are available. "
            f"Veterans receive 30 free sessions per trauma type with expert clinicians "
            f"trained in evidence-based therapies including Cognitive Processing Therapy (CPT), "
            f"EMDR, and Prolonged Exposure. Headstrong matches Veterans with a clinician "
            f"within 2 business days and the first session typically occurs within 2 weeks."
        )

        eligibility = (
            "Veterans of all eras (any service period), any discharge status (including "
            "other-than-honorable), active duty service members, National Guard, Reserves, "
            "and family members (spouses, partners, children, parents, siblings, caregivers). "
            "No VA enrollment required. No cost to Veterans or families."
        )

        how_to_apply = (
            "Visit theheadstrongproject.org/get-help/ to fill out the intake form. "
            "A Headstrong team member will contact you within 2 business days to match "
            "you with a clinician. Specify your preference for in-person or telehealth. "
            "Your first session is typically scheduled within 2 weeks. All services are "
            "free and confidential."
        )

        tags = [
            "headstrong",
            "ptsd",
            "free-therapy",
            "cpt",
            "emdr",
            "telehealth",
            "in-person",
            "prolonged-exposure",
            "trauma",
            "mental-health",
            "free-services",
            "all-eras",
            "any-discharge",
            "family-support",
            f"state-{state.lower()}",
        ]

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=self.GET_HELP_URL,
            org_name="The Headstrong Project",
            org_website=self.WEBSITE,
            state=state,
            categories=["mentalHealth"],
            tags=tags,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="state",
            states=[state],
            raw_data={
                "service_type": "in-person",
                "telehealth_available": True,
                "sessions_offered": 30,
                "cost": "free",
                "treatment_modalities": self.TREATMENT_MODALITIES,
                "response_time": "2 business days",
                "first_session": "within 2 weeks",
            },
            fetched_at=fetched_at,
        )

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
