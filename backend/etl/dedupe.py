"""Deduplication for ETL pipeline.

Detects and merges duplicate resources across different sources,
preferring higher-tier sources when conflicts occur.
"""

from difflib import SequenceMatcher

from etl.models import NormalizedResource


class Deduplicator:
    """Detects and merges duplicate resources."""

    # Threshold for fuzzy title matching (0-1)
    TITLE_SIMILARITY_THRESHOLD = 0.85

    def __init__(
        self,
        title_threshold: float = TITLE_SIMILARITY_THRESHOLD,
    ):
        """Initialize deduplicator.

        Args:
            title_threshold: Minimum similarity ratio for title matching (0-1).
        """
        self.title_threshold = title_threshold

    def deduplicate(self, resources: list[NormalizedResource]) -> tuple[list[NormalizedResource], int]:
        """Remove duplicates from a list of normalized resources.

        Uses the following matching criteria:
        1. Same organization (case-insensitive)
        2. Same address (if present) OR both have no address
        3. Similar title (fuzzy match above threshold)

        When duplicates are found, prefers:
        1. Higher-tier source (lower tier number)
        2. More complete data (more fields filled)
        3. First encountered (stable ordering)

        Args:
            resources: List of normalized resources to deduplicate.

        Returns:
            Tuple of (deduplicated list, number removed as duplicates).
        """
        if not resources:
            return [], 0

        # Group by organization + location key
        groups: dict[str, list[NormalizedResource]] = {}

        for resource in resources:
            # Create grouping key from org and location
            group_key = self._create_group_key(resource)

            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(resource)

        # Process each group for title-based duplicates
        deduplicated: list[NormalizedResource] = []
        duplicates_removed = 0

        for group in groups.values():
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                # Find duplicates within group based on title similarity
                unique, removed = self._dedupe_group(group)
                deduplicated.extend(unique)
                duplicates_removed += removed

        return deduplicated, duplicates_removed

    def _create_group_key(self, resource: NormalizedResource) -> str:
        """Create a grouping key for initial clustering.

        Groups resources by organization and location to narrow
        down candidates for title comparison.
        """
        org_key = resource.org_name.lower().strip()

        # Normalize org name by removing common suffixes
        for suffix in [" inc", " inc.", " llc", " corp", " corporation"]:
            if org_key.endswith(suffix):
                org_key = org_key[: -len(suffix)]

        location_key = resource.location_key() or "no-location"

        return f"{org_key}|{location_key}"

    def _dedupe_group(self, group: list[NormalizedResource]) -> tuple[list[NormalizedResource], int]:
        """Deduplicate resources within a group using title similarity.

        Args:
            group: Resources with same org and location.

        Returns:
            Tuple of (unique resources, count of duplicates removed).
        """
        if len(group) <= 1:
            return group, 0

        # Sort by tier (lower is better) then by completeness
        sorted_group = sorted(
            group,
            key=lambda r: (r.source_tier, -self._completeness_score(r)),
        )

        # Track which resources to keep
        keep: list[NormalizedResource] = []
        duplicates_removed = 0

        for resource in sorted_group:
            is_duplicate = False

            for kept in keep:
                if self._are_duplicates(resource, kept):
                    # Merge any additional data from lower-priority resource
                    self._merge_data(kept, resource)
                    is_duplicate = True
                    duplicates_removed += 1
                    break

            if not is_duplicate:
                keep.append(resource)

        return keep, duplicates_removed

    def _are_duplicates(self, resource1: NormalizedResource, resource2: NormalizedResource) -> bool:
        """Check if two resources are duplicates.

        Two resources are considered duplicates if they have:
        1. Same organization (already guaranteed by grouping)
        2. Same location (already guaranteed by grouping)
        3. Similar titles (fuzzy match)
        """
        title_similarity = self._title_similarity(resource1.title, resource2.title)
        return title_similarity >= self.title_threshold

    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles.

        Uses SequenceMatcher for fuzzy string matching.
        """
        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()

        # Exact match
        if t1 == t2:
            return 1.0

        # Fuzzy match
        return SequenceMatcher(None, t1, t2).ratio()

    def _completeness_score(self, resource: NormalizedResource) -> int:
        """Calculate how complete a resource's data is.

        Higher score = more fields filled.
        """
        score = 0

        # Required fields always present
        score += 4

        # Optional fields
        if resource.org_website:
            score += 1
        if resource.address:
            score += 2
        if resource.city:
            score += 1
        if resource.state:
            score += 1
        if resource.zip_code:
            score += 1
        if resource.phone:
            score += 2
        if resource.email:
            score += 1
        if resource.hours:
            score += 1
        if resource.eligibility:
            score += 2
        if resource.how_to_apply:
            score += 2
        if resource.categories:
            score += len(resource.categories)
        if resource.tags:
            score += min(len(resource.tags), 5)

        return score

    def _merge_data(self, primary: NormalizedResource, secondary: NormalizedResource) -> None:
        """Merge data from secondary into primary resource.

        Only fills in missing fields from primary, preserving
        the higher-tier source's data.
        """
        # Merge optional fields if primary is missing them
        if not primary.org_website and secondary.org_website:
            primary.org_website = secondary.org_website

        if not primary.phone and secondary.phone:
            primary.phone = secondary.phone

        if not primary.email and secondary.email:
            primary.email = secondary.email

        if not primary.hours and secondary.hours:
            primary.hours = secondary.hours

        if not primary.eligibility and secondary.eligibility:
            primary.eligibility = secondary.eligibility

        if not primary.how_to_apply and secondary.how_to_apply:
            primary.how_to_apply = secondary.how_to_apply

        # Merge lists (deduplicate)
        primary.categories = list(set(primary.categories) | set(secondary.categories))
        primary.tags = list(set(primary.tags) | set(secondary.tags))
        primary.states = list(set(primary.states) | set(secondary.states))


def find_potential_duplicates(
    new_resource: NormalizedResource,
    existing_resources: list[NormalizedResource],
    title_threshold: float = 0.85,
) -> list[NormalizedResource]:
    """Find potential duplicates for a new resource.

    Useful for checking against existing database records.

    Args:
        new_resource: The resource to check.
        existing_resources: List of existing resources.
        title_threshold: Minimum title similarity.

    Returns:
        List of potential duplicate resources.
    """
    deduplicator = Deduplicator(title_threshold=title_threshold)
    duplicates = []

    new_group_key = deduplicator._create_group_key(new_resource)

    for existing in existing_resources:
        existing_group_key = deduplicator._create_group_key(existing)

        # Same group (org + location) and similar title?
        if new_group_key == existing_group_key and deduplicator._are_duplicates(new_resource, existing):
            duplicates.append(existing)

    return duplicates
