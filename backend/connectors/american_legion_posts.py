"""American Legion Post Locator connector.

Imports American Legion post locations from curated reference data. American Legion
posts provide benefits assistance, youth programs, and community support for Veterans.

The American Legion is the largest wartime veterans service organization, founded
in 1919 with over 12,000 posts across the United States and abroad. Posts typically offer:
- Benefits assistance (VA claims support from accredited representatives)
- Youth programs (Boys/Girls State, Oratorical Contest, Legion Baseball)
- Community support and camaraderie
- Service referrals
- Family support programs (American Legion Auxiliary, Sons of The American Legion)
- Legion Riders motorcycle group

Source: https://mylegion.org/PersonifyEbusiness/Find-a-Post
Note: No public API available - data sourced via web scraping or partnership.
The post finder uses a server-side ASP.NET application with Telerik AJAX controls.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# State code to full name mapping
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
    "PR": "Puerto Rico",
    "GU": "Guam",
    "VI": "Virgin Islands",
    "AS": "American Samoa",
}

# American Legion program codes to readable names
LEGION_PROGRAMS = {
    "Baseball": "American Legion Baseball",
    "Boys State": "Boys State",
    "Girls State": "Girls State",
    "Oratorical": "Oratorical Contest",
    "Legion Riders": "American Legion Riders",
    "Sons of The American Legion": "Sons of The American Legion (SAL)",
    "American Legion Auxiliary": "American Legion Auxiliary",
    "Junior Shooting Sports": "Junior Shooting Sports Program",
    "Scouting": "Scouting Programs",
}

# American Legion attribute codes to readable names
LEGION_ATTRIBUTES = {
    "Canteen": "Club Room",
    "Hall Rental": "Hall Rental",
    "Smoking Allowed": "Smoking Permitted",
}


class AmericanLegionPostsConnector(BaseConnector):
    """Connector for American Legion post locations.

    Parses the american_legion_posts.json file containing American Legion post
    information from across the United States. American Legion posts provide
    benefits assistance, youth programs, and community services for Veterans.

    Data is sourced from:
    - American Legion Find a Post: https://mylegion.org/PersonifyEbusiness/Find-a-Post
    - State department directories
    - American Legion national headquarters (via partnership request)

    Since American Legion doesn't provide a public API, data is collected through:
    1. Web scraping (state-by-state due to large dataset of 12,000+ posts)
    2. Partnership agreements with American Legion headquarters
    3. Manual updates from state departments

    Data fields per post:
        - post_number: American Legion post number (e.g., "1", "134")
        - post_name: Post name if available (e.g., "Hollywood Post 43")
        - address: Street address
        - city: City name
        - state: Two-letter state code
        - zip_code: ZIP code
        - phone: Contact phone number
        - website: Post website (if available)
        - email: Contact email (if available)
        - department: State department name
        - attributes: List of attribute codes (Canteen, Hall Rental, etc.)
        - programs: List of program codes (Baseball, Boys State, etc.)
        - lat: Latitude (if geocoded)
        - lng: Longitude (if geocoded)
    """

    # Path to data file relative to project root
    DATA_PATH = "data/reference/american_legion_posts.json"

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
            name="American Legion Post Locator",
            url="https://mylegion.org/PersonifyEbusiness/Find-a-Post",
            tier=2,  # Established nonprofit VSO
            frequency="quarterly",  # Posts change infrequently
            terms_url="https://www.legion.org/privacy-policy",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse American Legion post data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        now = datetime.now(UTC)

        data = self._load_data()
        if not data:
            return []

        resources: list[ResourceCandidate] = []

        for post in data.get("posts", []):
            candidate = self._parse_post(post, fetched_at=now)
            if candidate:
                resources.append(candidate)

        return resources

    def _load_data(self) -> dict:
        """Load American Legion post data from JSON file."""
        if not self.data_path.exists():
            return {}

        with open(self.data_path) as f:
            return json.load(f)

    def _parse_post(
        self,
        post: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate | None:
        """Parse an American Legion post entry into a ResourceCandidate.

        Args:
            post: Dictionary containing post data.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this American Legion post, or None if invalid.
        """
        post_number = post.get("post_number")
        post_name = post.get("post_name")
        address = post.get("address")
        city = post.get("city")
        state = post.get("state")
        zip_code = post.get("zip_code")
        phone = post.get("phone")
        email = post.get("email")
        website = post.get("website")
        department = post.get("department")
        attributes = post.get("attributes", [])
        programs = post.get("programs", [])

        # Skip posts without minimum required data
        if not post_number or not state:
            return None

        state_name = STATE_NAMES.get(state)

        title = self._build_title(post_number, post_name, city, state)
        description = self._build_description(
            post_number, post_name, city, state_name, attributes, programs
        )
        eligibility = self._build_eligibility()
        how_to_apply = self._build_how_to_apply(
            post_number, post_name, phone, email, website
        )
        tags = self._build_tags(state, attributes, programs)

        # Build full address
        full_address = None
        if address:
            if city and state and zip_code:
                full_address = f"{address}, {city}, {state} {zip_code}"
            elif city and state:
                full_address = f"{address}, {city}, {state}"
            else:
                full_address = address

        # Build org name
        org_name = f"American Legion {post_name}" if post_name else f"American Legion Post {post_number}"

        # Source URL - link to Legion locator or post website
        source_url = website or "https://mylegion.org/PersonifyEbusiness/Find-a-Post"

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name=org_name,
            org_website=website or "https://www.legion.org",
            address=full_address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["benefits", "supportServices"],
            tags=tags,
            phone=self._normalize_phone(phone),
            email=email,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="local",
            states=[state] if state else None,
            raw_data={
                "post_number": post_number,
                "post_name": post_name,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "phone": phone,
                "email": email,
                "website": website,
                "department": department,
                "attributes": attributes,
                "programs": programs,
                "lat": post.get("lat"),
                "lng": post.get("lng"),
            },
            fetched_at=fetched_at,
        )

    def _build_title(
        self,
        post_number: str,
        post_name: str | None,
        city: str | None,
        state: str | None,
    ) -> str:
        """Build resource title.

        Args:
            post_number: American Legion post number.
            post_name: Optional post name.
            city: City name.
            state: State code.

        Returns:
            Formatted title string.
        """
        location = f"({city}, {state})" if city and state else f"({state})" if state else ""

        if post_name:
            # Check if post name already includes "Post" and number
            if "post" in post_name.lower():
                return f"American Legion {post_name} {location}".strip()
            return f"American Legion Post {post_number} - {post_name} {location}".strip()
        return f"American Legion Post {post_number} {location}".strip()

    def _build_description(
        self,
        post_number: str,
        post_name: str | None,
        city: str | None,
        state_name: str | None,
        attributes: list[str],
        programs: list[str],
    ) -> str:
        """Build resource description.

        Args:
            post_number: American Legion post number.
            post_name: Optional post name.
            city: City name.
            state_name: Full state name.
            attributes: List of attribute codes.
            programs: List of program codes.

        Returns:
            Formatted description string.
        """
        parts = []

        # Opening with location context
        location = f"in {city}, {state_name}" if city and state_name else ""
        if post_name:
            parts.append(
                f"American Legion Post {post_number} ({post_name}) {location} provides "
                "benefits assistance, youth programs, and community support for Veterans.".strip()
            )
        else:
            parts.append(
                f"American Legion Post {post_number} {location} provides "
                "benefits assistance, youth programs, and community support for Veterans.".strip()
            )

        # American Legion background
        parts.append(
            "The American Legion is the nation's largest wartime veterans service organization, "
            "founded in 1919 and committed to mentoring youth, sponsoring wholesome programs, "
            "providing assistance to veterans, and promoting patriotism and honor."
        )

        # Programs if available
        if programs:
            program_names = [
                LEGION_PROGRAMS.get(p, p) for p in programs if p in LEGION_PROGRAMS or p not in LEGION_ATTRIBUTES
            ]
            if program_names:
                parts.append(f"Programs at this post include: {', '.join(program_names)}.")

        # Attributes/amenities if available
        if attributes:
            attr_names = [
                LEGION_ATTRIBUTES.get(a, a) for a in attributes if a in LEGION_ATTRIBUTES
            ]
            if attr_names:
                parts.append(f"This post offers: {', '.join(attr_names)}.")

        # Standard Legion offerings
        parts.append(
            "American Legion posts provide a place for Veterans to connect with others who "
            "share similar military experiences, access free benefits assistance from trained "
            "service officers, and participate in community service and youth development programs."
        )

        return " ".join(parts)

    def _build_eligibility(self) -> str:
        """Build eligibility description.

        Returns:
            Eligibility description string.
        """
        return (
            "American Legion membership is open to any U.S. citizen who served at least one day "
            "of active military duty since December 7, 1941 and was honorably discharged or is "
            "still serving honorably. Active duty for training purposes does not qualify. "
            "Eligible service periods include World War II, Korea, Vietnam, Lebanon, Grenada, "
            "Panama, Gulf War, and the Global War on Terror (September 11, 2001 to present). "
            "Note: American Legion service officers provide free VA claims assistance to ALL "
            "Veterans regardless of Legion membership status."
        )

    def _build_how_to_apply(
        self,
        post_number: str,
        post_name: str | None,
        phone: str | None,
        email: str | None,
        website: str | None,
    ) -> str:
        """Build how to apply/contact instructions.

        Args:
            post_number: American Legion post number.
            post_name: Optional post name.
            phone: Contact phone number.
            email: Contact email.
            website: Post website.

        Returns:
            Application instructions string.
        """
        parts = []
        post_display = post_name or f"Post {post_number}"

        # Primary contact method
        if phone:
            parts.append(f"Call American Legion {post_display} at {phone} to inquire about membership or services.")
        elif email:
            parts.append(f"Email American Legion {post_display} at {email} to inquire about membership or services.")
        elif website:
            parts.append(
                f"Visit the website for American Legion {post_display} "
                "to learn about membership and services."
            )
        else:
            parts.append(f"Contact American Legion {post_display} to inquire about membership and available services.")

        # Additional contact methods
        if email and phone:
            parts.append(f"Email: {email}")
        if website:
            parts.append(f"Website: {website}")

        # National resources
        parts.append(
            "For national membership information, visit https://www.legion.org/join. "
            "To find an American Legion Service Officer for free benefits assistance, visit "
            "https://www.legion.org/serviceofficers or call the Legion's toll-free number at 1-800-433-3318."
        )

        return " ".join(parts)

    def _build_tags(
        self,
        state: str | None,
        attributes: list[str],
        programs: list[str],
    ) -> list[str]:
        """Build tags list.

        Args:
            state: Two-letter state code.
            attributes: List of attribute codes.
            programs: List of program codes.

        Returns:
            List of tag strings.
        """
        tags = [
            "american-legion",
            "vso",
            "veterans-service-organization",
            "community",
            "peer-support",
        ]

        # State tag
        if state:
            tags.append(f"state-{state.lower()}")

        # Attribute-based tags
        for attr in attributes:
            if attr == "Canteen":
                tags.append("club-room")
            elif attr == "Hall Rental":
                tags.append("hall-rental")
                tags.append("event-space")

        # Program-based tags
        for program in programs:
            if program == "Baseball":
                tags.append("legion-baseball")
                tags.append("youth-programs")
            elif program == "Boys State":
                tags.append("boys-state")
                tags.append("youth-programs")
            elif program == "Girls State":
                tags.append("girls-state")
                tags.append("youth-programs")
            elif program == "Oratorical":
                tags.append("oratorical-contest")
                tags.append("youth-programs")
            elif program == "Legion Riders":
                tags.append("legion-riders")
                tags.append("motorcycle-group")
            elif program == "Sons of The American Legion":
                tags.append("sons-of-the-american-legion")
                tags.append("family-programs")
            elif program == "American Legion Auxiliary":
                tags.append("american-legion-auxiliary")
                tags.append("family-programs")
            elif program == "Junior Shooting Sports":
                tags.append("junior-shooting-sports")
                tags.append("youth-programs")
            elif program == "Scouting":
                tags.append("scouting")
                tags.append("youth-programs")

        return list(set(tags))  # Deduplicate
