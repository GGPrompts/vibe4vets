"""Student Veterans of America (SVA) Chapters connector.

Fetches SVA chapter directory data from their website's map API.
SVA has 1,600+ chapters at colleges nationwide providing peer support
and resources for student veterans.

Data source: https://studentveterans.org/chapters/find-a-chapter/
"""

from datetime import UTC, datetime
from typing import Any

import httpx

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# US State coordinate bounding boxes for state detection from lat/lng
# Format: (min_lat, max_lat, min_lng, max_lng)
STATE_BOUNDS: dict[str, tuple[float, float, float, float]] = {
    "AL": (30.14, 35.01, -88.47, -84.89),
    "AK": (51.21, 71.39, -179.15, -129.98),
    "AZ": (31.33, 37.00, -114.81, -109.04),
    "AR": (33.00, 36.50, -94.62, -89.64),
    "CA": (32.53, 42.01, -124.41, -114.13),
    "CO": (36.99, 41.00, -109.05, -102.04),
    "CT": (40.95, 42.05, -73.73, -71.79),
    "DE": (38.45, 39.84, -75.79, -75.05),
    "DC": (38.79, 38.99, -77.12, -76.91),
    "FL": (24.40, 31.00, -87.63, -80.03),
    "GA": (30.36, 35.00, -85.61, -80.84),
    "HI": (18.91, 22.24, -160.25, -154.81),
    "ID": (41.99, 49.00, -117.24, -111.04),
    "IL": (36.97, 42.51, -91.51, -87.02),
    "IN": (37.77, 41.76, -88.10, -84.78),
    "IA": (40.38, 43.50, -96.64, -90.14),
    "KS": (36.99, 40.00, -102.05, -94.59),
    "KY": (36.50, 39.15, -89.57, -81.96),
    "LA": (28.93, 33.02, -94.04, -88.82),
    "ME": (43.06, 47.46, -71.08, -66.95),
    "MD": (37.97, 39.72, -79.49, -75.05),
    "MA": (41.24, 42.89, -73.50, -69.93),
    "MI": (41.70, 48.31, -90.42, -82.12),
    "MN": (43.50, 49.38, -97.24, -89.49),
    "MS": (30.17, 35.00, -91.66, -88.10),
    "MO": (35.99, 40.61, -95.77, -89.10),
    "MT": (44.36, 49.00, -116.05, -104.04),
    "NE": (39.99, 43.00, -104.05, -95.31),
    "NV": (35.00, 42.00, -120.01, -114.04),
    "NH": (42.70, 45.31, -72.56, -70.70),
    "NJ": (38.93, 41.36, -75.56, -73.89),
    "NM": (31.33, 37.00, -109.05, -103.00),
    "NY": (40.50, 45.02, -79.76, -71.86),
    "NC": (33.84, 36.59, -84.32, -75.46),
    "ND": (45.94, 49.00, -104.05, -96.55),
    "OH": (38.40, 42.32, -84.82, -80.52),
    "OK": (33.62, 37.00, -103.00, -94.43),
    "OR": (41.99, 46.29, -124.57, -116.46),
    "PA": (39.72, 42.27, -80.52, -74.69),
    "RI": (41.15, 42.02, -71.86, -71.12),
    "SC": (32.04, 35.22, -83.35, -78.54),
    "SD": (42.48, 45.95, -104.06, -96.44),
    "TN": (34.98, 36.68, -90.31, -81.65),
    "TX": (25.84, 36.50, -106.65, -93.51),
    "UT": (37.00, 42.00, -114.05, -109.04),
    "VT": (42.73, 45.02, -73.44, -71.46),
    "VA": (36.54, 39.47, -83.68, -75.24),
    "WA": (45.54, 49.00, -124.85, -116.92),
    "WV": (37.20, 40.64, -82.64, -77.72),
    "WI": (42.49, 47.08, -92.89, -86.25),
    "WY": (40.99, 45.01, -111.05, -104.05),
    # Territories
    "PR": (17.88, 18.52, -67.27, -65.59),
    "VI": (17.62, 18.42, -65.15, -64.56),
    "GU": (13.23, 13.65, 144.62, 144.96),
    "AS": (-14.38, -14.16, -170.83, -169.41),
    "MP": (14.11, 20.56, 144.89, 145.87),
}


def get_state_from_coords(lat: float, lng: float) -> str | None:
    """Determine US state from latitude/longitude coordinates.

    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate

    Returns:
        Two-letter state code or None if not found.
    """
    for state, (min_lat, max_lat, min_lng, max_lng) in STATE_BOUNDS.items():
        if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
            return state
    return None


class SVAChaptersConnector(BaseConnector):
    """Connector for Student Veterans of America (SVA) chapter directory.

    SVA is a national organization with 1,600+ chapters at colleges and universities
    across the United States. Each chapter provides peer support, resources, and
    community for student veterans and military-connected students.

    This connector fetches chapter data from SVA's website map API, which powers
    their Find A Chapter tool.
    """

    # WP Google Maps API endpoint used by the Find A Chapter page
    API_URL = "https://studentveterans.org/wp-json/wpgmza/v1/markers"

    # Fallback page URL for source reference
    DIRECTORY_URL = "https://studentveterans.org/chapters/find-a-chapter/"

    def __init__(self) -> None:
        """Initialize the connector."""
        self._client: httpx.Client | None = None

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Student Veterans of America Chapters",
            url="https://studentveterans.org/chapters/find-a-chapter/",
            tier=2,  # Established nonprofit
            frequency="monthly",  # Directory updated monthly per SVA website
            terms_url=None,
            requires_auth=False,
        )

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                headers={
                    "Accept": "application/json",
                    "User-Agent": "Vibe4Vets/1.0 (veteran-resource-aggregator)",
                },
                timeout=60.0,
                follow_redirects=True,
            )
        return self._client

    def run(self) -> list[ResourceCandidate]:
        """Fetch SVA chapters from the API.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        resources: list[ResourceCandidate] = []

        try:
            client = self._get_client()

            response = client.get(self.API_URL)
            response.raise_for_status()
            markers = response.json()

            # Markers can be a list or nested object
            if isinstance(markers, dict):
                # Sometimes the API returns markers in a nested structure
                markers = markers.get("markers", markers.get("data", []))

            if not isinstance(markers, list):
                print(f"Unexpected response format from SVA API: {type(markers)}")
                return resources

            for marker in markers:
                # Skip unapproved markers
                if str(marker.get("approved", "0")) != "1":
                    continue

                candidate = self._parse_chapter(marker)
                if candidate:
                    resources.append(candidate)

            return resources

        except httpx.HTTPError as e:
            print(f"Error fetching SVA chapters: {e}")
            return resources
        finally:
            self.close()

    def _parse_chapter(self, marker: dict[str, Any]) -> ResourceCandidate | None:
        """Parse a map marker into a ResourceCandidate.

        Args:
            marker: Raw marker data from API

        Returns:
            ResourceCandidate or None if required fields are missing.
        """
        # Title is the school name
        school_name = marker.get("title", "").strip()
        if not school_name:
            return None

        # Description typically contains the chapter/organization name
        chapter_name = marker.get("description", "").strip()
        if not chapter_name:
            chapter_name = "Student Veterans of America Chapter"

        # Extract coordinates for state detection
        try:
            lat = float(marker.get("lat", 0))
            lng = float(marker.get("lng", 0))
        except (ValueError, TypeError):
            lat, lng = 0.0, 0.0

        # Determine state from coordinates
        state = get_state_from_coords(lat, lng) if lat and lng else None

        # Build title
        title = f"SVA Chapter at {school_name}"

        # Build description
        description = self._build_description(school_name, chapter_name)

        # Get link if available, otherwise use directory URL
        link = marker.get("link", "").strip()
        source_url = link if link else self.DIRECTORY_URL

        # Build eligibility
        eligibility = self._build_eligibility()

        # Build how to apply
        how_to_apply = self._build_how_to_apply(school_name, link)

        # Build tags
        tags = self._build_tags(school_name, chapter_name)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name="Student Veterans of America",
            org_website="https://studentveterans.org/",
            address=None,  # Coordinates are available but not street address
            city=None,
            state=state,
            zip_code=None,
            categories=["education"],
            tags=tags,
            phone=None,
            email=None,
            hours=None,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="local",
            states=[state] if state else None,
            raw_data={
                "marker_id": marker.get("id"),
                "map_id": marker.get("map_id"),
                "school_name": school_name,
                "chapter_name": chapter_name,
                "lat": lat,
                "lng": lng,
                "link": link,
            },
            fetched_at=datetime.now(UTC),
        )

    def _build_description(self, school_name: str, chapter_name: str) -> str:
        """Build a description for the SVA chapter.

        Args:
            school_name: Name of the college/university
            chapter_name: Name of the SVA chapter or student organization

        Returns:
            Formatted description string.
        """
        parts = []

        # Primary description
        if chapter_name.lower() != "student veterans of america":
            parts.append(
                f"{chapter_name} is the Student Veterans of America chapter at {school_name}."
            )
        else:
            parts.append(f"Student Veterans of America chapter at {school_name}.")

        # What SVA chapters do
        parts.append(
            "SVA chapters provide peer support, networking, and resources for student "
            "veterans and military-connected students. They help veterans navigate "
            "campus life, connect with other student veterans, and access academic "
            "and career resources."
        )

        # Benefits of membership
        parts.append(
            "Chapter members can access scholarships, leadership development programs, "
            "career opportunities, and a nationwide network of over 1,600 SVA chapters."
        )

        return " ".join(parts)

    def _build_eligibility(self) -> str:
        """Build eligibility text for SVA chapters.

        Returns:
            Eligibility description string.
        """
        return (
            "Open to all student veterans, active duty service members, National Guard and "
            "Reserve members, military spouses, dependents, and supporters of student veterans. "
            "You do not need to be a veteran to join and support your campus SVA chapter."
        )

    def _build_how_to_apply(self, school_name: str, link: str) -> str:
        """Build how to apply/join instructions.

        Args:
            school_name: Name of the school
            link: Chapter URL if available

        Returns:
            Application instructions string.
        """
        parts = []

        parts.append(
            f"1. Contact the SVA chapter at {school_name} through your school's "
            "student organization office or veteran services center."
        )

        if link:
            parts.append(f"2. Visit the chapter website at {link} for meeting schedules and contact info.")
        else:
            parts.append("2. Search for the chapter on your school's student organization directory.")

        parts.append("3. Attend a chapter meeting - most SVA chapters welcome new members at any meeting.")
        parts.append("4. For national SVA membership, visit studentveterans.org to create an account.")

        return " ".join(parts)

    def _build_tags(self, school_name: str, chapter_name: str) -> list[str]:
        """Build tags for the SVA chapter.

        Args:
            school_name: Name of the school
            chapter_name: Name of the chapter

        Returns:
            List of tag strings.
        """
        tags = [
            "sva",
            "student-veterans",
            "education",
            "peer-support",
            "college",
            "higher-education",
            "networking",
            "student-organization",
        ]

        # Add tags based on school type indicators in name
        school_lower = school_name.lower()

        if "community college" in school_lower:
            tags.append("community-college")
        elif "university" in school_lower:
            tags.append("university")
        elif "college" in school_lower:
            tags.append("college")

        if "technical" in school_lower or "tech" in school_lower:
            tags.append("technical-school")

        if "state" in school_lower:
            tags.append("public-university")

        return list(set(tags))  # Deduplicate

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "SVAChaptersConnector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
