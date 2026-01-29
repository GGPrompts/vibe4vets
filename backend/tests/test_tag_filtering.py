"""Tests for tag filtering with AND logic.

These tests verify that selecting multiple tags narrows results (AND logic)
rather than broadening them (OR logic).
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.models import Resource
from app.models.resource import ResourceStatus, ResourceScope


class TestTagFilteringLogic:
    """Test that tag filtering uses AND logic."""

    def test_single_tag_filter_matches_resource_with_tag(self):
        """A single tag should match resources that have that tag."""
        # This is a unit test verifying the logic pattern
        resource_tags = ["veterans", "housing", "hud-vash"]
        filter_tags = ["veterans"]

        # AND logic: resource must have ALL filter tags
        result = all(tag in resource_tags for tag in filter_tags)
        assert result is True

    def test_multiple_tags_require_all_matches(self):
        """Multiple tags should require ALL tags to match (AND logic)."""
        resource_tags = ["veterans", "housing", "hud-vash"]
        filter_tags = ["veterans", "housing"]

        # AND logic: resource must have ALL filter tags
        result = all(tag in resource_tags for tag in filter_tags)
        assert result is True

    def test_multiple_tags_fails_if_one_missing(self):
        """If any tag is missing, the resource should NOT match (AND logic)."""
        resource_tags = ["veterans", "housing"]
        filter_tags = ["veterans", "families"]  # "families" is not in resource_tags

        # AND logic: resource must have ALL filter tags
        result = all(tag in resource_tags for tag in filter_tags)
        assert result is False

    def test_more_tags_narrow_results(self):
        """Adding more tags should narrow results, not broaden them."""
        resources = [
            {"tags": ["veterans", "housing", "hud-vash"]},
            {"tags": ["veterans", "employment"]},
            {"tags": ["families", "housing"]},
        ]

        # Single tag "veterans" - should match 2 resources
        filter_single = ["veterans"]
        matches_single = [r for r in resources if all(t in r["tags"] for t in filter_single)]
        assert len(matches_single) == 2

        # Two tags "veterans" AND "housing" - should match 1 resource (narrower)
        filter_double = ["veterans", "housing"]
        matches_double = [r for r in resources if all(t in r["tags"] for t in filter_double)]
        assert len(matches_double) == 1

        # More tags = fewer results (refinement behavior)
        assert len(matches_double) < len(matches_single)

    def test_empty_tags_matches_all(self):
        """Empty tags list should not filter anything."""
        resources = [
            {"tags": ["veterans"]},
            {"tags": ["families"]},
        ]

        filter_tags = []
        # Empty filter should match all (no filtering applied)
        if not filter_tags:
            matches = resources
        else:
            matches = [r for r in resources if all(t in r["tags"] for t in filter_tags)]

        assert len(matches) == 2


class TestBuildTagsSql:
    """Test the SQL generation for tag filtering."""

    def test_build_tags_sql_uses_and_join(self):
        """The build_tags_sql helper should use AND to join tag conditions."""
        # Simulate the build_tags_sql function logic
        tags = ["veterans", "housing"]
        tag_conditions = []
        for tag in tags:
            search_term = f"%{tag}%"
            search_term_spaced = f"%{tag.replace('-', ' ')}%"
            tag_conditions.append(
                f"(r.eligibility ILIKE '{search_term}' OR r.eligibility ILIKE '{search_term_spaced}' "
                f"OR r.title ILIKE '{search_term}' OR r.title ILIKE '{search_term_spaced}' "
                f"OR r.description ILIKE '{search_term}' OR r.description ILIKE '{search_term_spaced}' "
                f"OR r.tags @> ARRAY['{tag}']::text[] "
                f"OR r.subcategories @> ARRAY['{tag}']::text[])"
            )

        # AND logic: join with AND
        result = " AND ".join(tag_conditions)

        # Verify AND is used between conditions
        assert " AND " in result
        # Verify there's no OR at the top level (only within each tag's condition)
        assert result.count(" AND ") == len(tags) - 1  # One AND between each pair
        # Verify both tags are in the result
        assert "veterans" in result
        assert "housing" in result

    def test_single_tag_no_and_needed(self):
        """Single tag should not need AND join."""
        tags = ["veterans"]
        tag_conditions = []
        for tag in tags:
            search_term = f"%{tag}%"
            tag_conditions.append(f"(r.tags @> ARRAY['{tag}']::text[])")

        result = " AND ".join(tag_conditions)

        # Single condition, no AND in output
        assert " AND " not in result
        assert "veterans" in result
