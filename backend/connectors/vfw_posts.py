"""VFW (Veterans of Foreign Wars) Post Locator connector.

Imports VFW post locations from curated reference data. VFW posts provide
peer support, benefits assistance, and community connections for veterans.

VFW is the largest and oldest war veterans service organization, with 5,500+
posts nationwide. Posts typically offer:
- Peer support and camaraderie
- VA claims assistance (accredited representatives)
- Community events and activities
- Service referrals
- Youth programs (Voice of Democracy, Patriots Pen)
- Funeral honors and memorial services

Source: https://www.vfw.org/find-a-post
Note: No public API available - data sourced via web scraping or partnership.
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

# VFW amenity codes to readable names
VFW_AMENITIES = {
    "BarCanteen": "Club Room",
    "VOD": "Voice of Democracy",
    "HallRental": "Hall Rental",
    "BoyScouts": "Boy Scouts",
    "FuneralHonors": "Funeral Honors",
    "PatriotsPen": "Patriots Pen",
    "RidersGroup": "VFW Riders Group",
}


class VFWPostsConnector(BaseConnector):
    """Connector for VFW (Veterans of Foreign Wars) post locations.

    Parses the vfw_posts.json file containing VFW post information from
    across the United States. VFW posts provide peer support, claims
    assistance, and community services for veterans.

    Data is sourced from:
    - VFW Find a Post: https://www.vfw.org/find-a-post
    - State department directories
    - VFW national headquarters (via partnership request)

    Since VFW doesn't provide a public API, data is collected through:
    1. Web scraping (state-by-state due to large dataset)
    2. Partnership agreements with VFW headquarters
    3. Manual updates from state departments

    Data fields per post:
        - post_number: VFW post number (e.g., "1234")
        - post_name: Post name if available (e.g., "John Doe Memorial Post")
        - address: Street address
        - city: City name
        - state: Two-letter state code
        - zip_code: ZIP code
        - phone: Contact phone number
        - website: Post website (if available)
        - email: Contact email (if available)
        - amenities: List of amenity codes (BarCanteen, VOD, etc.)
        - lat: Latitude (if geocoded)
        - lng: Longitude (if geocoded)
    """

    # Path to data file relative to project root
    DATA_PATH = "data/reference/vfw_posts.json"

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
            name="VFW Post Locator",
            url="https://www.vfw.org/find-a-post",
            tier=2,  # Established nonprofit VSO
            frequency="quarterly",  # Posts change infrequently
            terms_url="https://www.vfw.org/terms-of-use",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse VFW post data from JSON file.

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
        """Load VFW post data from JSON file."""
        if not self.data_path.exists():
            return {}

        with open(self.data_path) as f:
            return json.load(f)

    def _parse_post(
        self,
        post: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate | None:
        """Parse a VFW post entry into a ResourceCandidate.

        Args:
            post: Dictionary containing post data.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this VFW post, or None if invalid.
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
        amenities = post.get("amenities", [])

        # Skip posts without minimum required data
        if not post_number or not state:
            return None

        state_name = STATE_NAMES.get(state)

        title = self._build_title(post_number, post_name, city, state)
        description = self._build_description(
            post_number, post_name, city, state_name, amenities
        )
        eligibility = self._build_eligibility()
        how_to_apply = self._build_how_to_apply(
            post_number, post_name, phone, email, website
        )
        tags = self._build_tags(state, amenities)

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
        org_name = f"VFW {post_name}" if post_name else f"VFW Post {post_number}"

        # Source URL - link to VFW locator
        source_url = website or "https://www.vfw.org/find-a-post"

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name=org_name,
            org_website=website or "https://www.vfw.org",
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
                "amenities": amenities,
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
            post_number: VFW post number.
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
                return f"VFW {post_name} {location}".strip()
            return f"VFW Post {post_number} - {post_name} {location}".strip()
        return f"VFW Post {post_number} {location}".strip()

    def _build_description(
        self,
        post_number: str,
        post_name: str | None,
        city: str | None,
        state_name: str | None,
        amenities: list[str],
    ) -> str:
        """Build resource description.

        Args:
            post_number: VFW post number.
            post_name: Optional post name.
            city: City name.
            state_name: Full state name.
            amenities: List of amenity codes.

        Returns:
            Formatted description string.
        """
        parts = []

        # Opening with location context
        location = f"in {city}, {state_name}" if city and state_name else ""
        if post_name:
            parts.append(
                f"VFW Post {post_number} ({post_name}) {location} provides peer support, "
                "service assistance, and community for veterans.".strip()
            )
        else:
            parts.append(
                f"VFW Post {post_number} {location} provides peer support, "
                "service assistance, and community for veterans.".strip()
            )

        # VFW background
        parts.append(
            "The Veterans of Foreign Wars (VFW) is the largest and oldest war veterans "
            "service organization, founded in 1899 and dedicated to fostering camaraderie "
            "among U.S. veterans of overseas conflicts."
        )

        # Amenities if available
        if amenities:
            amenity_names = [
                VFW_AMENITIES.get(a, a) for a in amenities if a in VFW_AMENITIES
            ]
            if amenity_names:
                parts.append(f"This post offers: {', '.join(amenity_names)}.")

        # Standard VFW offerings
        parts.append(
            "VFW posts offer a place for veterans to connect with others who share "
            "similar military experiences, access benefits assistance from trained "
            "service officers, and participate in community service activities."
        )

        return " ".join(parts)

    def _build_eligibility(self) -> str:
        """Build eligibility description.

        Returns:
            Eligibility description string.
        """
        return (
            "VFW membership is open to U.S. citizens who have served honorably in the "
            "Armed Forces of the United States in a foreign war, insurrection, or "
            "expedition and earned a campaign medal or ribbon. Eligible conflicts include "
            "World War II, Korea, Vietnam, Gulf War, Iraq, Afghanistan, and other "
            "overseas operations. Note: VFW service officers provide free claims assistance "
            "to ALL veterans regardless of VFW membership status."
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
            post_number: VFW post number.
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
            parts.append(f"Call VFW {post_display} at {phone} to inquire about membership or services.")
        elif email:
            parts.append(f"Email VFW {post_display} at {email} to inquire about membership or services.")
        elif website:
            parts.append(f"Visit the website for VFW {post_display} to learn about membership and services.")
        else:
            parts.append(f"Contact VFW {post_display} to inquire about membership and available services.")

        # Additional contact methods
        if email and phone:
            parts.append(f"Email: {email}")
        if website:
            parts.append(f"Website: {website}")

        # National resources
        parts.append(
            "For national membership information, visit https://www.vfw.org/join. "
            "To find a VFW Service Officer for free benefits assistance, visit "
            "https://www.vfw.org/assistance/va-claims-702-service."
        )

        return " ".join(parts)

    def _build_tags(
        self,
        state: str | None,
        amenities: list[str],
    ) -> list[str]:
        """Build tags list.

        Args:
            state: Two-letter state code.
            amenities: List of amenity codes.

        Returns:
            List of tag strings.
        """
        tags = [
            "vfw",
            "vso",
            "veterans-of-foreign-wars",
            "veterans-service-organization",
            "community",
            "peer-support",
        ]

        # State tag
        if state:
            tags.append(f"state-{state.lower()}")

        # Amenity-based tags
        for amenity in amenities:
            if amenity == "BarCanteen":
                tags.append("club-room")
            elif amenity == "VOD":
                tags.append("voice-of-democracy")
                tags.append("youth-programs")
            elif amenity == "HallRental":
                tags.append("hall-rental")
                tags.append("event-space")
            elif amenity == "BoyScouts":
                tags.append("boy-scouts")
                tags.append("youth-programs")
            elif amenity == "FuneralHonors":
                tags.append("funeral-honors")
                tags.append("military-honors")
            elif amenity == "PatriotsPen":
                tags.append("patriots-pen")
                tags.append("youth-programs")
            elif amenity == "RidersGroup":
                tags.append("vfw-riders")
                tags.append("motorcycle-group")

        return list(set(tags))  # Deduplicate
