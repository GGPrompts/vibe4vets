"""Team Red White & Blue (Team RWB) community chapters connector.

Imports Team RWB chapter data from curated reference data.
Team RWB enriches Veterans' lives by connecting them to their community
through physical and social activity.

Team RWB locations include:
- 150+ local chapters providing fitness activities and social events
- 48 state-level coordination groups
- Weekly activities: running, hiking, yoga, functional fitness, cycling
- Monthly social events building community and combating isolation
- Eagle Leadership Development program for advanced engagement

Sources:
- Team RWB Chapter Finder: https://teamrwb.org/find-your-chapter/
- StorePoint API: https://api.storepoint.co/v1/166d0aac9a052d/locations
- Team RWB Member Portal: https://members.teamrwb.org/
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

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
    "PR": "Puerto Rico",
    "GU": "Guam",
    "VI": "Virgin Islands",
    "AS": "American Samoa",
}


class TeamRWBConnector(BaseConnector):
    """Connector for Team Red White & Blue chapter data.

    Parses the team_rwb_chapters.json file containing:
    - Local chapters providing fitness activities and social events
    - State-level coordination groups

    Team RWB is unique for:
    - Free membership for Veterans, service members, and supporters
    - Focus on physical activity to combat isolation
    - Weekly fitness events (running, hiking, yoga, etc.)
    - Monthly social events for community building
    - Eagle Leadership Development for advanced engagement

    Data fields:
        - storepoint_id: Unique identifier from StorePoint API
        - name: Chapter or state group name
        - chapter_type: "chapter" or "state"
        - city, state, zip_code: Location information
        - latitude, longitude: Geographic coordinates
        - email: Chapter captain contact email
        - phone: Contact phone (if available)
        - website: Members portal URL
        - description: Chapter description
    """

    DEFAULT_DATA_PATH = "data/reference/team_rwb_chapters.json"

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
            name="Team Red White & Blue Chapters",
            url="https://teamrwb.org/find-your-chapter/",
            tier=2,  # Established nonprofit
            frequency="quarterly",  # Chapters change infrequently
            terms_url="https://teamrwb.org/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse Team RWB chapter data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Team RWB chapters data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for chapter in data.get("chapters", []):
            candidate = self._parse_chapter(
                storepoint_id=chapter.get("storepoint_id"),
                name=chapter.get("name"),
                chapter_type=chapter.get("chapter_type", "chapter"),
                city=chapter.get("city"),
                state=chapter.get("state"),
                zip_code=chapter.get("zip_code"),
                latitude=chapter.get("latitude"),
                longitude=chapter.get("longitude"),
                email=chapter.get("email"),
                phone=chapter.get("phone"),
                website=chapter.get("website"),
                description=chapter.get("description"),
                fetched_at=now,
            )
            resources.append(candidate)

        return resources

    def _parse_chapter(
        self,
        storepoint_id: int | None,
        name: str | None,
        chapter_type: str,
        city: str | None,
        state: str | None,
        zip_code: str | None,
        latitude: float | None,
        longitude: float | None,
        email: str | None,
        phone: str | None,
        website: str | None,
        description: str | None,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a Team RWB chapter entry into a ResourceCandidate.

        Args:
            storepoint_id: Unique ID from StorePoint API
            name: Chapter or state group name
            chapter_type: "chapter" or "state"
            city: City name
            state: Two-letter state code
            zip_code: ZIP code
            latitude: Geographic latitude
            longitude: Geographic longitude
            email: Chapter captain contact email
            phone: Contact phone number
            website: Members portal URL
            description: Chapter description from API
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this Team RWB chapter.
        """
        state_name = STATE_NAMES.get(state) if state else None

        title = self._build_title(name, chapter_type, city, state)
        resource_description = self._build_description(name, chapter_type, city, state_name, description)

        # Build source URL - prefer website, fall back to chapter finder
        source_url = website or "https://teamrwb.org/find-your-chapter/"

        # Organization name
        org_name = self._build_org_name(name, chapter_type, city, state)

        return ResourceCandidate(
            title=title,
            description=resource_description,
            source_url=source_url,
            org_name=org_name,
            org_website="https://teamrwb.org",
            address=None,  # Team RWB chapters are activity-based, not facility-based
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["supportServices", "mentalHealth"],
            tags=self._build_tags(chapter_type, state),
            phone=self._normalize_phone(phone),
            email=email,
            hours=None,  # Events scheduled through app
            eligibility=self._build_eligibility(),
            how_to_apply=self._build_how_to_apply(name, email, website),
            scope="local",
            states=[state] if state else None,
            raw_data={
                "storepoint_id": storepoint_id,
                "name": name,
                "chapter_type": chapter_type,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "latitude": latitude,
                "longitude": longitude,
                "email": email,
                "phone": phone,
                "website": website,
                "description": description,
            },
            fetched_at=fetched_at,
        )

    def _build_org_name(
        self,
        name: str | None,
        chapter_type: str,
        city: str | None,
        state: str | None,
    ) -> str:
        """Build organization name for display.

        Args:
            name: Chapter name
            chapter_type: "chapter" or "state"
            city: City name
            state: State code

        Returns:
            Formatted organization name.
        """
        if chapter_type == "state":
            state_name = STATE_NAMES.get(state) if state else name
            return f"Team RWB {state_name or 'State Group'}"

        if name:
            return f"Team RWB {name}"

        if city:
            return f"Team RWB {city}"

        return "Team Red White & Blue"

    def _build_title(
        self,
        name: str | None,
        chapter_type: str,
        city: str | None,
        state: str | None,
    ) -> str:
        """Build resource title.

        Args:
            name: Chapter name
            chapter_type: "chapter" or "state"
            city: City name
            state: State code

        Returns:
            Formatted title string.
        """
        if chapter_type == "state":
            state_name = STATE_NAMES.get(state) if state else name
            return f"Team RWB {state_name or 'State Group'}"

        location = f"({city}, {state})" if city and state else f"({state})" if state else ""

        if name:
            # Avoid redundant city name in title
            if name.lower() == (city or "").lower():
                return f"Team RWB {name} Chapter {location}".strip()
            return f"Team RWB {name} Chapter {location}".strip()

        if city:
            return f"Team RWB {city} Chapter".strip()

        return f"Team RWB Chapter {location}".strip()

    def _build_description(
        self,
        name: str | None,
        chapter_type: str,
        city: str | None,
        state_name: str | None,
        api_description: str | None,
    ) -> str:
        """Build resource description.

        Args:
            name: Chapter name
            chapter_type: "chapter" or "state"
            city: City name
            state_name: Full state name
            api_description: Description from API

        Returns:
            Formatted description string.
        """
        parts = []
        location_str = f"in {city}, {state_name}" if city and state_name else f"in {state_name}" if state_name else ""

        if chapter_type == "state":
            parts.append(
                f"Team RWB {state_name or 'State'} coordinates Veteran fitness and "
                "social activities across the state.".strip()
            )
        else:
            parts.append(
                f"Team RWB chapter {location_str} hosts weekly fitness activities and "
                "monthly social events for Veterans, service members, and supporters.".strip()
            )

        # Core mission
        parts.append(
            "Team Red White & Blue enriches Veterans' lives by connecting them to their "
            "community through physical and social activity. Activities combat isolation "
            "and build camaraderie through shared experiences."
        )

        # Activities offered
        parts.append(
            "Weekly activities include running groups, hiking, yoga, functional fitness, "
            "cycling, and other group workouts. Monthly social events provide opportunities "
            "to connect in a relaxed environment."
        )

        # Membership and cost
        parts.append(
            "Membership is completely free. Open to all Veterans, active duty service "
            "members, National Guard, Reserve, military families, and community supporters "
            "who want to honor and support those who serve."
        )

        return " ".join(parts)

    def _build_eligibility(self) -> str:
        """Build eligibility description.

        Returns:
            Eligibility description string.
        """
        return (
            "Team RWB is open to everyone who supports Veterans and wants to be part of "
            "America's leading health and wellness community for Veterans. This includes: "
            "Veterans of any era or discharge status, active duty service members, "
            "National Guard and Reserve members, military spouses and family members, "
            "and community supporters who want to honor those who serve. There are no "
            "fitness requirements - all levels welcome. Membership is 100% free."
        )

    def _build_how_to_apply(
        self,
        name: str | None,
        email: str | None,
        website: str | None,
    ) -> str:
        """Build how to apply/join instructions.

        Args:
            name: Chapter name
            email: Chapter contact email
            website: Members portal URL

        Returns:
            How to join instructions string.
        """
        parts = []

        parts.append(
            "Join Team RWB for free at teamrwb.org or download the Team RWB Member App "
            "(available on iOS and Android) to find local events and connect with your chapter."
        )

        if website:
            parts.append(f"Visit the chapter page at {website} to see upcoming events.")

        if email:
            chapter_display = name or "your local chapter"
            parts.append(
                f"Contact {chapter_display} chapter captain at {email} with questions "
                "or to get involved with chapter leadership."
            )

        parts.append(
            "No registration or RSVP required for most events - just show up! Check the "
            "app or members portal for event details, meeting locations, and times."
        )

        return " ".join(parts)

    def _build_tags(self, chapter_type: str, state: str | None) -> list[str]:
        """Build tags list.

        Args:
            chapter_type: "chapter" or "state"
            state: Two-letter state code

        Returns:
            List of tag strings.
        """
        tags = [
            "team-rwb",
            "peer-support",
            "fitness",
            "community",
            "social-connection",
            "mental-wellness",
            "veteran-community",
            "free-membership",
        ]

        # Chapter type tags
        if chapter_type == "state":
            tags.append("state-coordination")
        else:
            tags.append("local-chapter")

        # Activity tags
        tags.extend(
            [
                "running",
                "hiking",
                "yoga",
                "group-fitness",
            ]
        )

        if state:
            tags.append(f"state-{state.lower()}")

        return list(set(tags))  # Deduplicate
