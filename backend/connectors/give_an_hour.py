"""Give an Hour volunteer mental health provider network connector.

Imports organization data from Give an Hour, which connects veterans with
volunteer licensed mental health professionals offering free counseling.

Source: https://giveanhour.org/military/
Research: backend/data/reference/research/veteran-mental-health.json

Note: Give an Hour uses a Salesforce-based provider portal with staff-mediated
referrals. Individual provider data is not publicly accessible via API, so this
connector returns a single national resource pointing to their services.
"""

from datetime import UTC, datetime

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# All US state codes for nationwide coverage
ALL_US_STATES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]


class GiveAnHourConnector(BaseConnector):
    """Connector for Give an Hour volunteer mental health services.

    Give an Hour connects veterans with volunteer licensed mental health
    professionals who donate their time to provide free counseling services.
    The network includes thousands of providers across the United States.

    Key features:
    - Free, confidential counseling from licensed professionals
    - Covers anxiety, depression, PTSD, substance abuse, grief
    - In-person and telehealth options
    - No referral required - schedule directly with providers
    - Services for active-duty, Guard, Reserve, veterans, and some families

    Data source: Organization information from website.
    No public API available - providers matched through staff-mediated referrals.
    """

    # Contact information
    WEBSITE = "https://giveanhour.org/"
    MILITARY_URL = "https://giveanhour.org/military/"
    PROVIDER_RELATIONS_EMAIL = "providerrelations@giveanhour.org"

    # Services provided
    SERVICES = [
        "anxiety treatment",
        "depression treatment",
        "PTSD treatment",
        "substance abuse counseling",
        "grief counseling",
        "stress management",
        "relationship issues",
        "trauma therapy",
    ]

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Give an Hour",
            url=self.WEBSITE,
            tier=2,  # Established nonprofit
            frequency="monthly",  # Organization info changes infrequently
            terms_url="https://giveanhour.org/privacy-policy/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Return Give an Hour resource.

        Creates a single national resource for the Give an Hour network.
        Individual provider data is not publicly accessible.

        Returns:
            List containing one ResourceCandidate for the organization.
        """
        now = datetime.now(UTC)
        return [self._create_national_resource(fetched_at=now)]

    def _create_national_resource(self, fetched_at: datetime) -> ResourceCandidate:
        """Create the national resource for Give an Hour.

        Args:
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for Give an Hour services nationwide.
        """
        title = "Give an Hour - Free Mental Health Counseling from Volunteer Professionals"

        description = (
            "Give an Hour connects veterans with volunteer licensed mental health "
            "professionals who donate their time to provide free, confidential "
            "counseling. The network includes thousands of providers across the "
            "United States offering both in-person and telehealth appointments. "
            "Services address a wide range of mental health concerns including "
            "anxiety, depression, PTSD, substance abuse, grief, stress, and "
            "relationship issues. Providers are licensed clinicians (psychologists, "
            "psychiatrists, social workers, counselors) who volunteer their expertise "
            "to support those who serve. Give an Hour was founded in 2005 and has "
            "provided over 350,000 hours of free mental health care."
        )

        eligibility = (
            "Active-duty military, National Guard, Reserves, and veterans of all eras. "
            "Some providers also see military spouses, caregivers, and family members. "
            "No discharge status restrictions. No VA enrollment or referral required. "
            "Services are completely free - providers volunteer their time."
        )

        how_to_apply = (
            "Visit giveanhour.org/military/ to learn about services and connect with "
            "a provider. You can also contact Give an Hour directly for assistance "
            "finding a provider in your area. Appointments are scheduled directly with "
            "individual providers. Both in-person and telehealth options are available "
            "depending on provider availability in your location."
        )

        tags = [
            "give-an-hour",
            "mental-health",
            "free-therapy",
            "volunteer-providers",
            "ptsd",
            "depression",
            "anxiety",
            "substance-abuse",
            "grief-counseling",
            "telehealth",
            "in-person",
            "free-services",
            "all-eras",
            "any-discharge",
            "no-referral",
            "nationwide",
            "licensed-professionals",
        ]

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=self.MILITARY_URL,
            org_name="Give an Hour",
            org_website=self.WEBSITE,
            categories=["mentalHealth"],
            tags=tags,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="national",
            states=ALL_US_STATES,
            raw_data={
                "service_type": "volunteer_network",
                "cost": "free",
                "services": self.SERVICES,
                "delivery_methods": ["in-person", "telehealth"],
                "provider_types": [
                    "psychologists",
                    "psychiatrists",
                    "social workers",
                    "licensed counselors",
                ],
                "hours_donated": "350,000+",
                "founded": 2005,
                "contact_email": self.PROVIDER_RELATIONS_EMAIL,
            },
            fetched_at=fetched_at,
        )
