"""Wounded Warrior Project (WWP) program locations connector.

Imports program locations and resources from the Wounded Warrior Project,
one of the largest veteran service organizations. WWP offers multiple
programs including the Warrior Care Network (intensive outpatient treatment
at 4 academic medical centers), Project Odyssey (12-week mental health program),
and WWP Talk (peer support).

Source: https://www.woundedwarriorproject.org/
Research: backend/data/reference/research/veteran-mental-health.json
"""

from datetime import UTC, datetime

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Warrior Care Network academic medical center locations
# Source: https://www.woundedwarriorproject.org/programs/warrior-care-network
# Last updated: 2026-01-29
WARRIOR_CARE_NETWORK_CENTERS = [
    {
        "name": "Emory Healthcare Veterans Program",
        "partner": "Emory Healthcare",
        "address": "12 Executive Park Drive NE",
        "city": "Atlanta",
        "state": "GA",
        "zip_code": "30329",
        "phone": "888-514-5345",
        "website": "https://www.emoryhealthcare.org/centers-programs/veterans-program/",
    },
    {
        "name": "Home Base at Massachusetts General Hospital",
        "partner": "Mass General Brigham",
        "address": "125 Nashua Street, Suite 324",
        "city": "Boston",
        "state": "MA",
        "zip_code": "02114",
        "phone": "617-724-5202",
        "website": "https://homebase.org/",
    },
    {
        "name": "Road Home Program at Rush University Medical Center",
        "partner": "Rush University Medical Center",
        "address": "325 S. Paulina Street",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60612",
        "phone": "312-942-8387",
        "website": "https://roadhomeprogram.org/",
    },
    {
        "name": "Operation Mend at UCLA Health",
        "partner": "UCLA Health",
        "address": "300 UCLA Medical Plaza, Suite B200",
        "city": "Los Angeles",
        "state": "CA",
        "zip_code": "90095",
        "phone": "310-267-5733",
        "website": "https://www.uclahealth.org/operation-mend/",
    },
]


class WoundedWarriorProjectConnector(BaseConnector):
    """Connector for Wounded Warrior Project programs.

    The Wounded Warrior Project (WWP) is one of the largest veteran service
    organizations in the United States. This connector provides resources for:

    1. Warrior Care Network: 2-week intensive outpatient program at 4 academic
       medical centers (Emory, MGH, Rush, UCLA) for PTSD, TBI, and MST treatment.
       WWP covers 100% of treatment, travel, meals, and expenses.

    2. Project Odyssey: 12-week mental health program using adventure-based
       learning, starting with a 5-day retreat. Available for individuals,
       couples, and families.

    3. WWP Talk: Non-clinical peer support program with weekly phone calls
       from trained Talk Partners for goal-setting and emotional support.

    All programs are free for post-9/11 veterans who have experienced physical
    or mental injuries during military service, as well as their family members.
    """

    # WWP contact information
    RESOURCE_CENTER_PHONE = "888-997-2586"
    RESOURCE_CENTER_PHONE_ALT = "904-405-1213"
    MAIN_PHONE = "877-832-6997"  # 877-TEAM-WWP
    EMAIL = "resourcecenter@woundedwarriorproject.org"
    WEBSITE = "https://www.woundedwarriorproject.org/"

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Wounded Warrior Project",
            url=self.WEBSITE,
            tier=1,  # Major national nonprofit
            frequency="monthly",  # Program info changes infrequently
            terms_url="https://www.woundedwarriorproject.org/privacy-policy",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Return Wounded Warrior Project resources.

        Creates:
        1. Resources for each Warrior Care Network center (4 locations)
        2. National Project Odyssey resource
        3. National WWP Talk resource

        Returns:
            List of ResourceCandidate objects.
        """
        now = datetime.now(UTC)
        resources: list[ResourceCandidate] = []

        # Add Warrior Care Network centers
        for center in WARRIOR_CARE_NETWORK_CENTERS:
            resources.append(self._create_wcn_resource(center, fetched_at=now))

        # Add Project Odyssey national resource
        resources.append(self._create_project_odyssey_resource(fetched_at=now))

        # Add WWP Talk national resource
        resources.append(self._create_wwp_talk_resource(fetched_at=now))

        return resources

    def _create_wcn_resource(
        self,
        center: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Create a Warrior Care Network center resource.

        Args:
            center: Center data dictionary.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for the center.
        """
        name = center["name"]
        partner = center["partner"]
        city = center["city"]
        state = center["state"]
        address = center["address"]
        zip_code = center["zip_code"]
        phone = center["phone"]
        website = center["website"]

        title = f"Warrior Care Network - {name}"

        description = self._build_wcn_description(name, partner, city, state)
        eligibility = self._build_wcn_eligibility()
        how_to_apply = self._build_wcn_how_to_apply(name, phone)
        tags = self._build_wcn_tags(state)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://www.woundedwarriorproject.org/programs/warrior-care-network",
            org_name="Wounded Warrior Project",
            org_website=self.WEBSITE,
            address=f"{address}, {city}, {state} {zip_code}",
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["mentalHealth"],
            tags=tags,
            phone=self._normalize_phone(phone),
            email=self.EMAIL,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="national",  # Accepts veterans nationwide
            states=None,  # All states eligible
            raw_data={
                "program": "Warrior Care Network",
                "center_name": name,
                "partner": partner,
                "center_website": website,
                "treatment_hours": "50+",
                "duration": "2 weeks",
                "cost": "free (all-inclusive)",
                "conditions_treated": ["PTSD", "TBI", "MST"],
            },
            fetched_at=fetched_at,
        )

    def _build_wcn_description(
        self,
        name: str,
        partner: str,
        city: str,
        state: str,
    ) -> str:
        """Build Warrior Care Network center description.

        Args:
            name: Center name.
            partner: Partner organization name.
            city: City where center is located.
            state: State code.

        Returns:
            Formatted description string.
        """
        return (
            f"The {name} in {city}, {state} is part of the Wounded Warrior Project's "
            f"Warrior Care Network, a partnership with {partner}. This 2-week intensive "
            "outpatient program provides over 50 hours of evidence-based treatment for "
            "PTSD, traumatic brain injury (TBI), military sexual trauma (MST), and related "
            "mental health conditions. Treatment includes individual and group therapy, "
            "wellness workshops, art therapy, mindfulness training, and peer support "
            "activities. WWP covers 100% of all costs including treatment, travel, meals, "
            "and lodging. The program uses a cohort model where veterans heal alongside "
            "peers with similar experiences."
        )

    def _build_wcn_eligibility(self) -> str:
        """Build Warrior Care Network eligibility text.

        Returns:
            Eligibility description string.
        """
        return (
            "Post-9/11 veterans and service members (served on or after September 11, 2001) "
            "who experience symptoms of PTSD, traumatic brain injury (TBI), military sexual "
            "trauma (MST), or related conditions. A formal diagnosis is not required. Must be "
            "able to travel and commit to two weeks of treatment. Not currently in crisis. "
            "Must be able to safely reduce or abstain from alcohol and drug use during the "
            "program. All services are free of cost."
        )

    def _build_wcn_how_to_apply(self, center_name: str, phone: str) -> str:
        """Build Warrior Care Network how-to-apply text.

        Args:
            center_name: Name of the center.
            phone: Center phone number.

        Returns:
            How to apply description string.
        """
        return (
            f"Contact the WWP Resource Center at {self.RESOURCE_CENTER_PHONE} or email "
            f"{self.EMAIL} to begin the referral process. You can also call "
            f"{center_name} directly at {phone}. Registration with WWP is required. "
            f"Visit woundedwarriorproject.org/programs/wwp-registration to register."
        )

    def _build_wcn_tags(self, state: str) -> list[str]:
        """Build Warrior Care Network tags.

        Args:
            state: State code where center is located.

        Returns:
            List of tag strings.
        """
        return [
            "mental-health",
            "ptsd",
            "tbi",
            "mst",
            "military-sexual-trauma",
            "free-services",
            "post-9/11",
            "wounded-warrior-project",
            "warrior-care-network",
            "intensive-outpatient",
            "evidence-based",
            "residential-style",
            "all-inclusive",
            f"state-{state.lower()}",
        ]

    def _create_project_odyssey_resource(
        self,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Create the Project Odyssey national resource.

        Args:
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for Project Odyssey.
        """
        title = "WWP Project Odyssey - 12-Week Mental Health Program"

        description = (
            "Project Odyssey is a 12-week mental health program from the Wounded Warrior "
            "Project that uses adventure-based learning to build resilience and coping skills. "
            "The program begins with a 5-day in-person retreat featuring activities like hiking, "
            "mountain biking, rock climbing, skiing, rafting, and snowboarding. Participants "
            "then continue 12 weeks of skill development with support from peer mentors, WWP "
            "staff, and licensed clinicians. The program is available in all-male, all-female, "
            "couples, and family formats, with virtual options also available. All costs "
            "including travel, food, and lodging are covered by WWP."
        )

        eligibility = (
            "Post-9/11 veterans and service members who experienced mental or physical injury "
            "during military service (served on or after September 11, 2001). Also open to "
            "family members and caregivers of wounded warriors. Must have experienced significant "
            "stress during military service and be ready to address emotional challenges. Must "
            "not be currently in crisis. All services are free of cost."
        )

        how_to_apply = (
            f"Contact the WWP Resource Center at {self.RESOURCE_CENTER_PHONE} or email "
            f"{self.EMAIL}. You can also use the live chat on the WWP website. Registration "
            "with WWP is required at woundedwarriorproject.org/programs/wwp-registration. "
            "Program dates and locations vary throughout the year."
        )

        tags = [
            "mental-health",
            "adventure-therapy",
            "ptsd",
            "resilience",
            "coping-skills",
            "free-services",
            "post-9/11",
            "wounded-warrior-project",
            "project-odyssey",
            "retreat",
            "peer-support",
            "family-support",
            "outdoor-activities",
            "nationwide",
        ]

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://www.woundedwarriorproject.org/programs/project-odyssey",
            org_name="Wounded Warrior Project",
            org_website=self.WEBSITE,
            categories=["mentalHealth"],
            tags=tags,
            phone=self._normalize_phone(self.RESOURCE_CENTER_PHONE),
            email=self.EMAIL,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="national",
            states=None,
            raw_data={
                "program": "Project Odyssey",
                "duration": "12 weeks",
                "retreat_length": "5 days",
                "cost": "free (all-inclusive)",
                "formats": ["individual", "couples", "family", "virtual"],
                "activities": [
                    "hiking",
                    "mountain biking",
                    "rock climbing",
                    "skiing",
                    "rafting",
                    "snowboarding",
                ],
            },
            fetched_at=fetched_at,
        )

    def _create_wwp_talk_resource(
        self,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Create the WWP Talk national resource.

        Args:
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for WWP Talk.
        """
        title = "WWP Talk - Non-Clinical Peer Support Program"

        description = (
            "WWP Talk is a non-clinical emotional support program from the Wounded Warrior "
            "Project that provides weekly phone calls from trained Talk Partners. The program "
            "helps veterans set S.M.A.R.T. goals (Specific, Measurable, Attainable, Realistic, "
            "Time-Bound) and develop coping skills and resilience. Calls are approximately "
            "20 minutes weekly at a scheduled time, typically lasting about 6 months on average. "
            "Talk Partners provide a safe, non-judgmental space for discussing personal concerns "
            "and can provide referrals to additional resources for PTSD, anger management, and "
            "other services. Conversations are confidential and not reported to the VA or "
            "affecting VA disability ratings."
        )

        eligibility = (
            "Post-9/11 veterans and service members who experienced injuries from military "
            "service (served on or after September 11, 2001). Also open to family members "
            "and caregivers of wounded warriors. Must be registered with WWP. Must not be "
            "currently experiencing a crisis. This is not a crisis line - for emergencies, "
            "contact the Veterans Crisis Line at 988 (press 1). All services are free."
        )

        how_to_apply = (
            f"Call the WWP main line at {self.MAIN_PHONE} (877-TEAM-WWP) to get started. "
            "You can also contact the Resource Center at {self.RESOURCE_CENTER_PHONE} or email "
            f"{self.EMAIL}. Registration with WWP is required at "
            "woundedwarriorproject.org/programs/wwp-registration. After an initial call, "
            "you will be paired with a Talk Partner and receive weekly calls at a "
            "pre-established day and time."
        )

        tags = [
            "mental-health",
            "peer-support",
            "emotional-support",
            "goal-setting",
            "coping-skills",
            "free-services",
            "post-9/11",
            "wounded-warrior-project",
            "wwp-talk",
            "phone-support",
            "weekly-calls",
            "family-support",
            "confidential",
            "nationwide",
        ]

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://www.woundedwarriorproject.org/programs/wwp-talk",
            org_name="Wounded Warrior Project",
            org_website=self.WEBSITE,
            categories=["mentalHealth"],
            tags=tags,
            phone=self._normalize_phone(self.MAIN_PHONE),
            email=self.EMAIL,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="national",
            states=None,
            raw_data={
                "program": "WWP Talk",
                "duration": "approximately 6 months",
                "call_frequency": "weekly",
                "call_length": "20 minutes",
                "cost": "free",
                "is_clinical": False,
                "is_crisis_line": False,
            },
            fetched_at=fetched_at,
        )
