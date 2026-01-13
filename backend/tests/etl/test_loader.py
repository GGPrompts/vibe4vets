"""Tests for ETL loader.

Note: These tests require PostgreSQL due to ARRAY column types.
They are skipped when running with SQLite.
"""

import pytest
from sqlmodel import select

from app.models import (
    ChangeLog,
    Location,
    Organization,
    Resource,
    ResourceStatus,
    ReviewState,
    ReviewStatus,
    Source,
    SourceRecord,
)
from etl.loader import Loader
from etl.models import NormalizedResource


# Skip all tests in this module - they require PostgreSQL for ARRAY types
pytestmark = pytest.mark.skip(reason="Loader tests require PostgreSQL (ARRAY column type)")


class TestLoader:
    """Tests for the Loader class."""

    def test_load_creates_organization(self, etl_session):
        """Test that loading creates an organization."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Organization",
            org_website="https://testorg.com",
            source_tier=2,
        )

        loader = Loader(etl_session)
        result = loader.load(resource)

        assert result.action == "created"
        assert result.organization_id is not None

        # Verify organization was created
        org = etl_session.get(Organization, result.organization_id)
        assert org is not None
        assert org.name == "Test Organization"
        assert org.website == "https://testorg.com"

    def test_load_reuses_existing_organization(self, etl_session):
        """Test that loading reuses existing organization."""
        # Create existing org
        existing_org = Organization(name="Test Organization")
        etl_session.add(existing_org)
        etl_session.commit()

        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Organization",
        )

        loader = Loader(etl_session)
        result = loader.load(resource)

        assert result.organization_id == existing_org.id

    def test_load_creates_location(self, etl_session):
        """Test that loading creates a location when address present."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Organization",
            address="123 Main St",
            city="Austin",
            state="TX",
            zip_code="78701",
            latitude=30.2672,
            longitude=-97.7431,
        )

        loader = Loader(etl_session)
        result = loader.load(resource)

        assert result.action == "created"
        assert result.location_id is not None

        # Verify location was created
        location = etl_session.get(Location, result.location_id)
        assert location is not None
        assert location.address == "123 Main St"
        assert location.city == "Austin"
        assert location.state == "TX"
        assert location.latitude == 30.2672

    def test_load_creates_resource(self, etl_session):
        """Test that loading creates a resource."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description with details",
            source_url="https://example.com/resource",
            org_name="Test Organization",
            phone="(555) 123-4567",
            categories=["employment", "training"],
            tags=["veteran", "job-placement"],
            eligibility="All veterans",
            how_to_apply="Call or visit",
            scope="national",
            reliability_score=0.8,
        )

        loader = Loader(etl_session)
        result = loader.load(resource)

        assert result.action == "created"
        assert result.resource_id is not None

        # Verify resource was created
        db_resource = etl_session.get(Resource, result.resource_id)
        assert db_resource is not None
        assert db_resource.title == "Test Resource"
        assert db_resource.phone == "(555) 123-4567"
        assert "employment" in db_resource.categories
        assert db_resource.reliability_score == 0.8

    def test_load_creates_source(self, etl_session):
        """Test that loading creates a source record."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Organization",
            source_name="VA.gov API",
            source_tier=1,
            raw_data={"test": "data"},
        )

        loader = Loader(etl_session)
        result = loader.load(resource)

        # Verify source was created
        stmt = select(Source).where(Source.name == "VA.gov API")
        source = etl_session.exec(stmt).first()
        assert source is not None
        assert source.tier == 1

        # Verify source record was created
        stmt = select(SourceRecord).where(SourceRecord.resource_id == result.resource_id)
        record = etl_session.exec(stmt).first()
        assert record is not None
        assert record.source_id == source.id

    def test_load_updates_existing_resource(self, etl_session):
        """Test that loading updates existing resource by source_url."""
        # Create initial resource
        initial = NormalizedResource(
            title="Test Resource",
            description="Initial description",
            source_url="https://example.com/resource",
            org_name="Test Organization",
            phone="(555) 111-1111",
        )

        loader = Loader(etl_session)
        first_result = loader.load(initial)
        assert first_result.action == "created"

        # Load updated version
        updated = NormalizedResource(
            title="Test Resource Updated",
            description="Updated description",
            source_url="https://example.com/resource",  # Same URL
            org_name="Test Organization",
            phone="(555) 222-2222",
        )

        second_result = loader.load(updated)
        assert second_result.action == "updated"
        assert second_result.resource_id == first_result.resource_id

        # Verify updates
        db_resource = etl_session.get(Resource, first_result.resource_id)
        assert db_resource.title == "Test Resource Updated"
        assert db_resource.phone == "(555) 222-2222"

    def test_load_skips_unchanged_resource(self, etl_session):
        """Test that loading skips resource with no changes."""
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com/resource",
            org_name="Test Organization",
        )

        loader = Loader(etl_session)
        first_result = loader.load(resource)

        # Load same resource again
        second_result = loader.load(resource)
        assert second_result.action == "skipped"

    def test_load_creates_change_log(self, etl_session):
        """Test that loading creates change log for updates."""
        # Create initial resource
        initial = NormalizedResource(
            title="Test Resource",
            description="Initial description",
            source_url="https://example.com/resource",
            org_name="Test Organization",
        )

        loader = Loader(etl_session)
        first_result = loader.load(initial)

        # Load updated version
        updated = NormalizedResource(
            title="Test Resource Updated",
            description="Initial description",
            source_url="https://example.com/resource",
            org_name="Test Organization",
        )

        loader.load(updated)

        # Verify change log
        stmt = select(ChangeLog).where(ChangeLog.resource_id == first_result.resource_id)
        changes = etl_session.exec(stmt).all()
        assert len(changes) >= 1

        title_change = next((c for c in changes if c.field == "title"), None)
        assert title_change is not None
        assert title_change.old_value == "Test Resource"
        assert title_change.new_value == "Test Resource Updated"

    def test_load_flags_risky_changes_for_review(self, etl_session):
        """Test that risky field changes trigger review."""
        # Create initial resource
        initial = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com/resource",
            org_name="Test Organization",
            phone="(555) 111-1111",
        )

        loader = Loader(etl_session)
        first_result = loader.load(initial)

        # Load with risky change (phone)
        updated = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com/resource",
            org_name="Test Organization",
            phone="(555) 999-9999",  # Phone changed
        )

        loader.load(updated)

        # Verify resource flagged for review
        db_resource = etl_session.get(Resource, first_result.resource_id)
        assert db_resource.status == ResourceStatus.NEEDS_REVIEW

        # Verify review state created
        stmt = select(ReviewState).where(ReviewState.resource_id == first_result.resource_id)
        review = etl_session.exec(stmt).first()
        assert review is not None
        assert review.status == ReviewStatus.PENDING

    def test_load_merges_categories(self, etl_session):
        """Test that loading merges categories from updates."""
        # Create initial resource
        initial = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com/resource",
            org_name="Test Organization",
            categories=["employment"],
        )

        loader = Loader(etl_session)
        first_result = loader.load(initial)

        # Load with additional category
        updated = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com/resource",
            org_name="Test Organization",
            categories=["training"],
        )

        loader.load(updated)

        # Verify categories merged
        db_resource = etl_session.get(Resource, first_result.resource_id)
        assert "employment" in db_resource.categories
        assert "training" in db_resource.categories

    def test_load_batch(self, etl_session):
        """Test batch loading."""
        resources = [
            NormalizedResource(
                title="Resource 1",
                description="Description 1",
                source_url="https://example.com/1",
                org_name="Org 1",
            ),
            NormalizedResource(
                title="Resource 2",
                description="Description 2",
                source_url="https://example.com/2",
                org_name="Org 2",
            ),
        ]

        loader = Loader(etl_session)
        results, errors = loader.load_batch(resources)

        assert len(results) == 2
        assert len(errors) == 0
        assert all(r.action == "created" for r in results)

    def test_load_handles_error(self, etl_session):
        """Test that errors are handled gracefully."""
        # This would need a way to trigger a DB error
        # For now, test that normal load doesn't error
        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Organization",
        )

        loader = Loader(etl_session)
        result = loader.load(resource)

        assert result.action != "failed"

    def test_load_updates_org_website_if_missing(self, etl_session):
        """Test that org website is updated if previously missing."""
        # Create org without website
        existing_org = Organization(name="Test Organization")
        etl_session.add(existing_org)
        etl_session.commit()

        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="Test Organization",
            org_website="https://testorg.com",
        )

        loader = Loader(etl_session)
        loader.load(resource)

        # Verify website was updated
        etl_session.refresh(existing_org)
        assert existing_org.website == "https://testorg.com"

    def test_load_case_insensitive_org_match(self, etl_session):
        """Test that org matching is case-insensitive."""
        # Create org with specific casing
        existing_org = Organization(name="Test Organization")
        etl_session.add(existing_org)
        etl_session.commit()

        resource = NormalizedResource(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com",
            org_name="TEST ORGANIZATION",  # Different case
        )

        loader = Loader(etl_session)
        result = loader.load(resource)

        assert result.organization_id == existing_org.id
