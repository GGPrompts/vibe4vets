"""Enrichment for ETL pipeline.

Adds geocoding, trust scores, tags, and scope information
to normalized resources.
"""

from typing import Protocol

from app.core.taxonomy import CATEGORIES, get_reliability_score
from etl.models import NormalizedResource


class GeocoderProtocol(Protocol):
    """Protocol for geocoding services."""

    def geocode(self, address: str, city: str, state: str, zip_code: str) -> tuple[float | None, float | None]:
        """Geocode an address.

        Args:
            address: Street address
            city: City name
            state: 2-letter state code
            zip_code: ZIP code

        Returns:
            Tuple of (latitude, longitude) or (None, None) if not found.
        """
        ...


class StubGeocoder:
    """Stub geocoder that returns None for all addresses.

    Replace with real implementation (Google Maps, Nominatim, etc.)
    in production.
    """

    def geocode(self, address: str, city: str, state: str, zip_code: str) -> tuple[float | None, float | None]:
        """Return None for stub geocoding."""
        return None, None


class Enricher:
    """Enriches normalized resources with additional data."""

    # Keywords that suggest specific categories
    CATEGORY_KEYWORDS = {
        "employment": [
            "job",
            "jobs",
            "career",
            "careers",
            "employment",
            "hiring",
            "workforce",
            "work",
            "employer",
            "placement",
            "resume",
        ],
        "training": [
            "training",
            "education",
            "certification",
            "apprentice",
            "vocational",
            "gi bill",
            "school",
            "college",
            "degree",
            "skills",
            "learning",
        ],
        "housing": [
            "housing",
            "shelter",
            "unhoused",
            "hud",
            "vash",
            "ssvf",
            "transitional",
            "rent",
            "apartment",
            "home",
        ],
        "legal": [
            "legal",
            "law",
            "attorney",
            "lawyer",
            "court",
            "appeal",
            "discharge",
            "claims",
            "benefits",
        ],
    }

    # Keywords for tag extraction
    TAG_KEYWORDS = [
        "veteran",
        "veterans",
        "disabled",
        "disability",
        "ptsd",
        "mental health",
        "substance abuse",
        "addiction",
        "family",
        "spouse",
        "transition",
        "reintegration",
        "housing",
        "emergency",
        "crisis",
        "financial",
        "assistance",
        "free",
        "women",
        "female",
        "lgbtq",
    ]

    def __init__(self, geocoder: GeocoderProtocol | None = None):
        """Initialize enricher.

        Args:
            geocoder: Geocoding service. Uses StubGeocoder if not provided.
        """
        self.geocoder = geocoder or StubGeocoder()

    def enrich(self, resource: NormalizedResource) -> NormalizedResource:
        """Enrich a single resource.

        Adds:
        - Geocoding (lat/lng) for address
        - Reliability score from source tier
        - Inferred categories from content
        - Generated tags from keywords
        - Scope determination

        Args:
            resource: Normalized resource to enrich.

        Returns:
            Enriched resource (modifies in place and returns).
        """
        # Geocode if address present
        self._geocode(resource)

        # Set reliability score from tier
        self._set_reliability(resource)

        # Infer categories from content
        self._infer_categories(resource)

        # Extract tags from content
        self._extract_tags(resource)

        # Determine scope from address
        self._determine_scope(resource)

        return resource

    def enrich_batch(self, resources: list[NormalizedResource]) -> list[NormalizedResource]:
        """Enrich a batch of resources.

        Args:
            resources: List of normalized resources.

        Returns:
            List of enriched resources.
        """
        return [self.enrich(r) for r in resources]

    def _geocode(self, resource: NormalizedResource) -> None:
        """Add geocoding to resource if address is present."""
        if not resource.has_location():
            return

        lat, lng = self.geocoder.geocode(
            resource.address or "",
            resource.city or "",
            resource.state or "",
            resource.zip_code or "",
        )

        resource.latitude = lat
        resource.longitude = lng

    def _set_reliability(self, resource: NormalizedResource) -> None:
        """Set reliability score from source tier."""
        resource.reliability_score = get_reliability_score(resource.source_tier)

    def _infer_categories(self, resource: NormalizedResource) -> None:
        """Infer categories from title and description.

        Only adds categories if none are present.
        """
        if resource.categories:
            return  # Already has categories

        # Combine text for analysis
        text = f"{resource.title} {resource.description}".lower()

        inferred: set[str] = set()

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    inferred.add(category)
                    break

        # Only use valid categories
        valid_categories = set(CATEGORIES.keys())
        resource.categories = list(inferred & valid_categories)

    def _extract_tags(self, resource: NormalizedResource) -> None:
        """Extract tags from content based on keywords."""
        text = f"{resource.title} {resource.description}".lower()

        new_tags: set[str] = set(resource.tags)

        for keyword in self.TAG_KEYWORDS:
            if keyword in text:
                # Convert keyword to tag format
                tag = keyword.replace(" ", "-")
                new_tags.add(tag)

        # Add category-based tags
        for category in resource.categories:
            new_tags.add(category)

        # Add scope-based tags
        if resource.scope == "national":
            new_tags.add("nationwide")
        elif resource.scope == "state" and resource.states:
            for state in resource.states:
                new_tags.add(f"state-{state.lower()}")

        resource.tags = list(new_tags)

    def _determine_scope(self, resource: NormalizedResource) -> None:
        """Determine scope from address and states list."""
        # If already has a valid scope, respect it
        if resource.scope in ("national", "state", "local"):
            # But update states list if we have address info
            if resource.scope in ("local", "state") and resource.state and resource.state not in resource.states:
                resource.states = list(set(resource.states) | {resource.state})
            return

        # Infer scope from available data
        if resource.has_location():
            # Has full address = local
            resource.scope = "local"
            if resource.state and resource.state not in resource.states:
                resource.states = list(set(resource.states) | {resource.state})
        elif resource.state or resource.states:
            # Has state but no full address = state-level
            resource.scope = "state"
            if resource.state and resource.state not in resource.states:
                resource.states = list(set(resource.states) | {resource.state})
        else:
            # No location info = assume national
            resource.scope = "national"
            resource.states = []


class GoogleMapsGeocoder:
    """Google Maps geocoder implementation.

    Placeholder - implement when Google Maps API key is available.
    """

    def __init__(self, api_key: str):
        """Initialize with API key.

        Args:
            api_key: Google Maps API key.
        """
        self.api_key = api_key

    def geocode(self, address: str, city: str, state: str, zip_code: str) -> tuple[float | None, float | None]:
        """Geocode using Google Maps API.

        TODO: Implement when API key is available.
        """
        # Placeholder - would use httpx to call Google Maps Geocoding API
        return None, None


class NominatimGeocoder:
    """OpenStreetMap Nominatim geocoder implementation.

    Free alternative to Google Maps. Rate limited.
    """

    def __init__(self, user_agent: str = "vibe4vets-etl"):
        """Initialize with user agent.

        Args:
            user_agent: User agent for Nominatim requests.
        """
        self.user_agent = user_agent

    def geocode(self, address: str, city: str, state: str, zip_code: str) -> tuple[float | None, float | None]:
        """Geocode using Nominatim API.

        TODO: Implement with proper rate limiting.
        """
        # Placeholder - would use httpx to call Nominatim API
        # Note: Requires rate limiting (1 request/second)
        return None, None
