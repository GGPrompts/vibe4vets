"""Veterans Service Organization (VSO) Post Locator connector.

Imports VSO post data from curated reference data. VSO posts provide peer support,
service help, and community connections for veterans.

Supported organizations:
- VFW (Veterans of Foreign Wars)
- American Legion
- DAV (Disabled American Veterans)

VSO posts typically offer:
- Peer support and community
- Claims assistance (often VA-accredited representatives)
- Service referrals
- Community events and activities
- Networking opportunities

Sources:
- VFW Post Locator: https://www.vfw.org/find-a-post
- American Legion Post Directory: https://mylegion.org/PersonifyEbusiness/Find-a-Post
- DAV Chapter Locator: https://locators.dav.org/ChapterUnitLocator
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


# VSO organization metadata
VSO_ORGANIZATIONS = {
    "VFW": {
        "full_name": "Veterans of Foreign Wars",
        "description": "VFW is the largest and oldest war veterans service organization, "
        "dedicated to fostering camaraderie among United States veterans of overseas conflicts.",
        "website": "https://www.vfw.org",
        "locator_url": "https://www.vfw.org/find-a-post",
        "founded": 1899,
        "eligibility": "U.S. citizens who have served honorably in the Armed Forces of the "
        "United States in a foreign war, insurrection, or expedition and earned a campaign "
        "medal or ribbon.",
    },
    "American Legion": {
        "full_name": "The American Legion",
        "description": "The American Legion is the nation's largest veterans service organization, "
        "chartered by Congress in 1919 as a patriotic veterans organization devoted to "
        "mutual helpfulness.",
        "website": "https://www.legion.org",
        "locator_url": "https://mylegion.org/PersonifyEbusiness/Find-a-Post",
        "founded": 1919,
        "eligibility": "All wartime veterans and those currently serving in the U.S. military. "
        "Eligibility dates extend back to December 7, 1941 through present.",
    },
    "DAV": {
        "full_name": "Disabled American Veterans",
        "description": "DAV is dedicated to a single purpose: empowering veterans to lead "
        "high-quality lives with respect and dignity through free benefits assistance, "
        "advocacy, and education.",
        "website": "https://www.dav.org",
        "locator_url": "https://locators.dav.org/ChapterUnitLocator",
        "founded": 1920,
        "eligibility": "Men and women who were wounded, injured, or became ill while serving "
        "in the U.S. Armed Forces during wartime or peacetime and who have an honorable "
        "discharge. Service-connected disability is required.",
    },
}

# State code to name mapping
STATE_NAMES = {
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


class VSOPostLocatorConnector(BaseConnector):
    """Connector for Veterans Service Organization (VSO) post data.

    Parses the vso_posts.json file containing post information for:
    - VFW (Veterans of Foreign Wars) posts
    - American Legion posts
    - DAV (Disabled American Veterans) chapters

    VSO posts provide:
    - Peer support and community
    - Claims assistance (VA-accredited representatives)
    - Service referrals
    - Community events and activities
    - Meeting space and networking

    Data fields:
        - organization: VSO name (VFW, American Legion, DAV)
        - post_name: Full post/chapter name
        - post_number: Post/chapter number
        - address: Street address
        - city: City name
        - state: Two-letter state code
        - zip_code: ZIP code
        - phone: Contact phone number
        - email: Contact email (if available)
        - website: Post website (if available)
        - services: List of services offered
        - meeting_schedule: Meeting schedule info
        - hours: Operating hours (if available)
    """

    DEFAULT_DATA_PATH = "data/reference/vso_posts.json"

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
            name="VSO Post Locator (VFW, American Legion, DAV)",
            url="https://www.vfw.org/find-a-post",
            tier=2,  # Established nonprofit VSOs
            frequency="quarterly",  # Posts change infrequently
            terms_url="https://www.vfw.org/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse VSO post data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"VSO posts data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for post in data.get("posts", []):
            candidate = self._parse_post(
                organization=post.get("organization"),
                post_name=post.get("post_name"),
                post_number=post.get("post_number"),
                address=post.get("address"),
                city=post.get("city"),
                state=post.get("state"),
                zip_code=post.get("zip_code"),
                phone=post.get("phone"),
                email=post.get("email"),
                website=post.get("website"),
                services=post.get("services", []),
                meeting_schedule=post.get("meeting_schedule"),
                hours=post.get("hours"),
                fetched_at=now,
            )
            resources.append(candidate)

        return resources

    def _parse_post(
        self,
        organization: str | None,
        post_name: str | None,
        post_number: str | None,
        address: str | None,
        city: str | None,
        state: str | None,
        zip_code: str | None,
        phone: str | None,
        email: str | None,
        website: str | None,
        services: list[str],
        meeting_schedule: str | None,
        hours: str | None,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a VSO post entry into a ResourceCandidate.

        Args:
            organization: VSO name (VFW, American Legion, DAV)
            post_name: Full post/chapter name
            post_number: Post/chapter number
            address: Street address
            city: City name
            state: Two-letter state code
            zip_code: ZIP code
            phone: Contact phone number
            email: Contact email address
            website: Post website
            services: List of services offered
            meeting_schedule: Meeting schedule information
            hours: Operating hours
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this VSO post.
        """
        org_info = VSO_ORGANIZATIONS.get(organization, {})
        state_name = STATE_NAMES.get(state) if state else None

        title = self._build_title(organization, post_name, post_number, city, state)
        description = self._build_description(
            organization, org_info, post_name, post_number, city, state_name, services, meeting_schedule
        )

        # Build full address string
        full_address = None
        if address:
            full_address = address
            if city and state and zip_code:
                full_address = f"{address}, {city}, {state} {zip_code}"
            elif city and state:
                full_address = f"{address}, {city}, {state}"

        # Build source URL - prefer post website, fall back to org locator
        source_url = website or org_info.get("locator_url", "https://www.vfw.org/find-a-post")

        # Organization website
        org_website = website or org_info.get("website")

        # Build org name for display
        org_name = post_name or f"{organization} Post"
        if post_number and organization and organization not in (post_name or ""):
            org_name = f"{organization} {post_name or 'Post ' + str(post_number)}"

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name=org_name,
            org_website=org_website,
            address=full_address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["community"],
            tags=self._build_tags(organization, state, services),
            phone=self._normalize_phone(phone),
            email=email,
            hours=hours,
            eligibility=self._build_eligibility(organization, org_info, state_name),
            how_to_apply=self._build_how_to_apply(organization, post_name, phone, email, website, meeting_schedule),
            scope="local",
            states=[state] if state else None,
            raw_data={
                "organization": organization,
                "post_name": post_name,
                "post_number": post_number,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "phone": phone,
                "email": email,
                "website": website,
                "services": services,
                "meeting_schedule": meeting_schedule,
                "hours": hours,
            },
            fetched_at=fetched_at,
        )

    def _build_title(
        self,
        organization: str | None,
        post_name: str | None,
        post_number: str | None,
        city: str | None,
        state: str | None,
    ) -> str:
        """Build resource title.

        Args:
            organization: VSO name (VFW, American Legion, DAV)
            post_name: Full post/chapter name
            post_number: Post/chapter number
            city: City name
            state: State code

        Returns:
            Formatted title string.
        """
        location = f"({city}, {state})" if city and state else f"({state})" if state else ""

        if post_name and organization:
            # If post_name already includes organization, don't duplicate
            if organization.lower() in post_name.lower():
                return f"{post_name} {location}".strip()
            return f"{organization} {post_name} {location}".strip()
        elif post_number and organization:
            unit_type = "Chapter" if organization == "DAV" else "Post"
            return f"{organization} {unit_type} {post_number} {location}".strip()
        elif organization and city:
            return f"{organization} - {city} {location}".strip()
        elif organization:
            return f"{organization} Post {location}".strip()
        return "Veterans Service Organization Post"

    def _build_description(
        self,
        organization: str | None,
        org_info: dict,
        post_name: str | None,
        post_number: str | None,
        city: str | None,
        state_name: str | None,
        services: list[str],
        meeting_schedule: str | None,
    ) -> str:
        """Build resource description.

        Args:
            organization: VSO name
            org_info: Organization metadata dict
            post_name: Full post/chapter name
            post_number: Post/chapter number
            city: City name
            state_name: Full state name
            services: List of services offered
            meeting_schedule: Meeting schedule information

        Returns:
            Formatted description string.
        """
        parts = []

        # Opening description with location context
        location = f"in {city}, {state_name}" if city and state_name else ""

        if post_name and organization:
            parts.append(f"{organization} {post_name} {location} provides peer support, "
                         "service assistance, and community for veterans.".strip())
        elif organization:
            unit_type = "Chapter" if organization == "DAV" else "Post"
            parts.append(f"This {organization} {unit_type} {location} provides peer support, "
                         "service assistance, and community for veterans.".strip())
        else:
            parts.append("Veterans Service Organization post providing peer support and services.")

        # Organization background
        org_desc = org_info.get("description")
        if org_desc:
            parts.append(org_desc)

        # Services offered
        if services:
            services_text = ", ".join(services[:6])  # Limit to 6 services
            if len(services) > 6:
                services_text += f", and {len(services) - 6} more"
            parts.append(f"Services include: {services_text}.")

        # Meeting schedule
        if meeting_schedule:
            parts.append(f"Meeting schedule: {meeting_schedule}")

        # Standard VSO offerings
        parts.append(
            "VSO posts offer a place for veterans to connect with others who share "
            "similar military experiences, access benefits assistance from trained "
            "representatives, and participate in community service activities."
        )

        return " ".join(parts)

    def _build_eligibility(
        self,
        organization: str | None,
        org_info: dict,
        state_name: str | None,
    ) -> str:
        """Build eligibility description.

        Args:
            organization: VSO name
            org_info: Organization metadata dict
            state_name: Full state name

        Returns:
            Eligibility description string.
        """
        # Organization-specific eligibility
        org_eligibility = org_info.get("eligibility")
        if org_eligibility:
            eligibility = f"Membership eligibility for {organization}: {org_eligibility}"
        else:
            eligibility = (
                "Eligibility varies by organization. Most VSOs require military service "
                "during specific periods or campaigns. Contact the post for specific "
                "membership requirements."
            )

        # Note about services being available to all veterans
        eligibility += (
            " Note: Many VSO posts provide claims assistance and referrals to all "
            "veterans regardless of membership status."
        )

        return eligibility

    def _build_how_to_apply(
        self,
        organization: str | None,
        post_name: str | None,
        phone: str | None,
        email: str | None,
        website: str | None,
        meeting_schedule: str | None,
    ) -> str:
        """Build how to apply/contact instructions.

        Args:
            organization: VSO name
            post_name: Full post/chapter name
            phone: Contact phone number
            email: Contact email address
            website: Post website
            meeting_schedule: Meeting schedule information

        Returns:
            How to apply instructions string.
        """
        parts = []
        post_display = post_name or f"this {organization} post" if organization else "this VSO post"

        # Primary contact method
        if phone:
            parts.append(f"Call {post_display} at {phone} to inquire about membership or services.")
        elif email:
            parts.append(f"Email {post_display} at {email} to inquire about membership or services.")
        elif website:
            parts.append(f"Visit the website for {post_display} to learn about membership and services.")
        else:
            parts.append(f"Contact {post_display} to inquire about membership and available services.")

        # Additional contact methods
        if email and phone:
            parts.append(f"Email: {email}")
        if website:
            parts.append(f"Website: {website}")

        # Meeting schedule as opportunity to visit
        if meeting_schedule:
            parts.append(f"Veterans are often welcome to attend meetings: {meeting_schedule}")

        # Membership guidance
        if organization:
            org_info = VSO_ORGANIZATIONS.get(organization, {})
            org_website = org_info.get("website")
            if org_website:
                parts.append(
                    f"For national membership information, visit {org_website}"
                )

        return " ".join(parts)

    def _build_tags(
        self,
        organization: str | None,
        state: str | None,
        services: list[str],
    ) -> list[str]:
        """Build tags list.

        Args:
            organization: VSO name
            state: Two-letter state code
            services: List of services offered

        Returns:
            List of tag strings.
        """
        tags = [
            "vso",
            "veterans-service-organization",
            "peer-support",
            "community",
            "veteran-community",
        ]

        # Organization-specific tags
        if organization:
            org_slug = organization.lower().replace(" ", "-")
            tags.append(org_slug)
            if organization == "VFW":
                tags.append("veterans-of-foreign-wars")
            elif organization == "American Legion":
                tags.append("american-legion")
            elif organization == "DAV":
                tags.append("disabled-american-veterans")

        if state:
            tags.append(f"state-{state.lower()}")

        # Service-based tags
        services_lower = " ".join(services).lower()
        service_tag_map = {
            "claims": "va-claims-assistance",
            "benefits": "benefits-assistance",
            "service officer": "va-claims-assistance",
            "employment": "employment-services",
            "housing": "housing-assistance",
            "food": "food-assistance",
            "emergency": "emergency-assistance",
            "scholarship": "education-benefits",
            "transportation": "transportation-assistance",
            "funeral": "burial-benefits",
            "honor guard": "military-honors",
        }

        for keyword, tag in service_tag_map.items():
            if keyword in services_lower:
                tags.append(tag)

        return list(set(tags))  # Deduplicate
