"""Tests for ETL deduplicator."""

import pytest

from etl.dedupe import Deduplicator, find_potential_duplicates
from etl.models import NormalizedResource


class TestDeduplicator:
    """Tests for the Deduplicator class."""

    def test_dedupe_empty_list(self):
        """Test deduplication of empty list."""
        deduplicator = Deduplicator()
        result, removed = deduplicator.deduplicate([])

        assert result == []
        assert removed == 0

    def test_dedupe_single_resource(self):
        """Test deduplication of single resource."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Org",
        )

        deduplicator = Deduplicator()
        result, removed = deduplicator.deduplicate([resource])

        assert len(result) == 1
        assert removed == 0

    def test_dedupe_no_duplicates(self):
        """Test deduplication when no duplicates exist."""
        resources = [
            NormalizedResource(
                title="Resource A",
                description="Description A",
                source_url="https://example.com/a",
                org_name="Org A",
            ),
            NormalizedResource(
                title="Resource B",
                description="Description B",
                source_url="https://example.com/b",
                org_name="Org B",
            ),
        ]

        deduplicator = Deduplicator()
        result, removed = deduplicator.deduplicate(resources)

        assert len(result) == 2
        assert removed == 0

    def test_dedupe_exact_duplicates(self):
        """Test deduplication of exact duplicates."""
        resources = [
            NormalizedResource(
                title="Employment Services",
                description="Employment help",
                source_url="https://example.com/1",
                org_name="VA",
                address="123 Main St",
                city="Washington",
                state="DC",
                zip_code="20001",
                source_tier=1,
            ),
            NormalizedResource(
                title="Employment Services",
                description="Employment help",
                source_url="https://example.com/2",
                org_name="VA",
                address="123 Main St",
                city="Washington",
                state="DC",
                zip_code="20001",
                source_tier=2,
            ),
        ]

        deduplicator = Deduplicator()
        result, removed = deduplicator.deduplicate(resources)

        assert len(result) == 1
        assert removed == 1
        # Should keep tier 1 (better)
        assert result[0].source_tier == 1

    def test_dedupe_similar_titles(self):
        """Test deduplication of similar (but not exact) titles."""
        resources = [
            NormalizedResource(
                title="VA Employment Services Program",
                description="Employment help",
                source_url="https://example.com/1",
                org_name="Department of Veterans Affairs",
                source_tier=2,
            ),
            NormalizedResource(
                title="VA Employment Services",  # Similar title
                description="Employment help",
                source_url="https://example.com/2",
                org_name="Department of Veterans Affairs",
                source_tier=1,
            ),
        ]

        deduplicator = Deduplicator(title_threshold=0.80)
        result, removed = deduplicator.deduplicate(resources)

        assert len(result) == 1
        assert removed == 1
        # Should keep tier 1 (better)
        assert result[0].source_tier == 1

    def test_dedupe_different_orgs_not_duplicates(self):
        """Test that same title at different orgs are not duplicates."""
        resources = [
            NormalizedResource(
                title="Employment Services",
                description="Employment help",
                source_url="https://example.com/1",
                org_name="VA",
            ),
            NormalizedResource(
                title="Employment Services",
                description="Employment help",
                source_url="https://example.com/2",
                org_name="DOL",  # Different org
            ),
        ]

        deduplicator = Deduplicator()
        result, removed = deduplicator.deduplicate(resources)

        assert len(result) == 2
        assert removed == 0

    def test_dedupe_different_locations_not_duplicates(self):
        """Test that same title at different locations are not duplicates."""
        resources = [
            NormalizedResource(
                title="VA Medical Center",
                description="Healthcare services",
                source_url="https://example.com/1",
                org_name="VA",
                address="123 Main St",
                city="New York",
                state="NY",
                zip_code="10001",
            ),
            NormalizedResource(
                title="VA Medical Center",
                description="Healthcare services",
                source_url="https://example.com/2",
                org_name="VA",
                address="456 Oak Ave",
                city="Los Angeles",
                state="CA",
                zip_code="90001",
            ),
        ]

        deduplicator = Deduplicator()
        result, removed = deduplicator.deduplicate(resources)

        assert len(result) == 2
        assert removed == 0

    def test_dedupe_prefers_higher_tier(self):
        """Test that higher tier (lower number) is preferred."""
        resources = [
            NormalizedResource(
                title="Test Resource",
                description="Description",
                source_url="https://example.com/1",
                org_name="Test Org",
                source_tier=4,  # Community
            ),
            NormalizedResource(
                title="Test Resource",
                description="Description",
                source_url="https://example.com/2",
                org_name="Test Org",
                source_tier=1,  # Official
            ),
            NormalizedResource(
                title="Test Resource",
                description="Description",
                source_url="https://example.com/3",
                org_name="Test Org",
                source_tier=2,  # Established
            ),
        ]

        deduplicator = Deduplicator()
        result, removed = deduplicator.deduplicate(resources)

        assert len(result) == 1
        assert removed == 2
        assert result[0].source_tier == 1

    def test_dedupe_merges_data(self):
        """Test that data is merged from duplicates."""
        resources = [
            NormalizedResource(
                title="Test Resource",
                description="Description",
                source_url="https://example.com/1",
                org_name="Test Org",
                source_tier=1,
                phone="(555) 123-4567",
                # No email
                categories=["employment"],
                tags=["tag1"],
            ),
            NormalizedResource(
                title="Test Resource",
                description="Description",
                source_url="https://example.com/2",
                org_name="Test Org",
                source_tier=2,
                # No phone
                email="test@example.com",
                categories=["training"],
                tags=["tag2"],
            ),
        ]

        deduplicator = Deduplicator()
        result, removed = deduplicator.deduplicate(resources)

        assert len(result) == 1
        # Should have phone from tier 1
        assert result[0].phone == "(555) 123-4567"
        # Should have email merged from tier 2
        assert result[0].email == "test@example.com"
        # Categories and tags should be merged
        assert "employment" in result[0].categories
        assert "training" in result[0].categories
        assert "tag1" in result[0].tags
        assert "tag2" in result[0].tags

    def test_dedupe_prefers_more_complete(self):
        """Test that more complete resource is preferred when same tier."""
        resources = [
            NormalizedResource(
                title="Test Resource",
                description="Description",
                source_url="https://example.com/1",
                org_name="Test Org",
                source_tier=2,
                # Minimal data
            ),
            NormalizedResource(
                title="Test Resource",
                description="Full description with more details",
                source_url="https://example.com/2",
                org_name="Test Org",
                source_tier=2,
                phone="(555) 123-4567",
                email="test@example.com",
                eligibility="All veterans",
                categories=["employment", "training"],
            ),
        ]

        deduplicator = Deduplicator()
        result, removed = deduplicator.deduplicate(resources)

        assert len(result) == 1
        # Should keep the more complete one
        assert result[0].phone == "(555) 123-4567"

    def test_dedupe_org_name_normalization(self):
        """Test that org names are normalized for matching."""
        resources = [
            NormalizedResource(
                title="Test Resource",
                description="Description",
                source_url="https://example.com/1",
                org_name="Test Organization Inc.",
                source_tier=1,
            ),
            NormalizedResource(
                title="Test Resource",
                description="Description",
                source_url="https://example.com/2",
                org_name="Test Organization",  # Without Inc.
                source_tier=2,
            ),
        ]

        deduplicator = Deduplicator()
        result, removed = deduplicator.deduplicate(resources)

        assert len(result) == 1
        assert removed == 1

    def test_dedupe_threshold_adjustable(self):
        """Test that title similarity threshold is adjustable."""
        resources = [
            NormalizedResource(
                title="VA Employment Services",
                description="Description",
                source_url="https://example.com/1",
                org_name="VA",
            ),
            NormalizedResource(
                title="VA Employment Program",  # Somewhat similar
                description="Description",
                source_url="https://example.com/2",
                org_name="VA",
            ),
        ]

        # High threshold - not duplicates
        dedup_high = Deduplicator(title_threshold=0.95)
        result_high, removed_high = dedup_high.deduplicate(resources)
        assert len(result_high) == 2

        # Low threshold - duplicates
        dedup_low = Deduplicator(title_threshold=0.5)
        result_low, removed_low = dedup_low.deduplicate(resources)
        assert len(result_low) == 1


class TestFindPotentialDuplicates:
    """Tests for the find_potential_duplicates function."""

    def test_find_duplicates_exact_match(self):
        """Test finding exact duplicate matches."""
        new_resource = NormalizedResource(
            title="Test Resource",
            description="Description",
            source_url="https://example.com/new",
            org_name="Test Org",
            address="123 Main St",
            city="City",
            state="CA",
            zip_code="12345",
        )

        existing = [
            NormalizedResource(
                title="Test Resource",
                description="Description",
                source_url="https://example.com/existing",
                org_name="Test Org",
                address="123 Main St",
                city="City",
                state="CA",
                zip_code="12345",
            ),
        ]

        duplicates = find_potential_duplicates(new_resource, existing)
        assert len(duplicates) == 1

    def test_find_duplicates_no_match(self):
        """Test when no duplicates exist."""
        new_resource = NormalizedResource(
            title="New Resource",
            description="Description",
            source_url="https://example.com/new",
            org_name="New Org",
        )

        existing = [
            NormalizedResource(
                title="Existing Resource",
                description="Description",
                source_url="https://example.com/existing",
                org_name="Existing Org",
            ),
        ]

        duplicates = find_potential_duplicates(new_resource, existing)
        assert len(duplicates) == 0

    def test_find_duplicates_empty_existing(self):
        """Test with empty existing list."""
        new_resource = NormalizedResource(
            title="Test Resource",
            description="Description",
            source_url="https://example.com",
            org_name="Test Org",
        )

        duplicates = find_potential_duplicates(new_resource, [])
        assert len(duplicates) == 0
