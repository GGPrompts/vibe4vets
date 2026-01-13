"""Tests for ETL pipeline orchestrator.

Note: Integration tests that use the database require PostgreSQL.
Tests that don't need the loader can still run with SQLite.
"""

from datetime import datetime, timezone

import pytest

from connectors.base import ResourceCandidate, SourceMetadata
from etl.models import ETLResult
from etl.pipeline import ETLPipeline, create_pipeline
from tests.etl.conftest import FailingConnector, MockConnector


# Mark tests that require database as skipped
requires_postgres = pytest.mark.skip(reason="Requires PostgreSQL (ARRAY column type)")


class TestETLPipeline:
    """Tests for the ETLPipeline class."""

    @requires_postgres
    def test_run_single_connector(self, etl_session, sample_candidate):
        """Test running pipeline with single connector."""
        connector = MockConnector([sample_candidate], name="Test Source", tier=1)

        pipeline = ETLPipeline(etl_session)
        result = pipeline.run([connector])

        assert isinstance(result, ETLResult)
        assert result.success is True
        assert result.stats.extracted == 1
        assert result.stats.normalized == 1
        assert result.stats.created == 1
        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.duration_seconds is not None

    @requires_postgres
    def test_run_multiple_connectors(self, etl_session):
        """Test running pipeline with multiple connectors."""
        candidates1 = [
            ResourceCandidate(
                title="Resource A",
                description="Description A",
                source_url="https://example.com/a",
                org_name="Org A",
            ),
        ]
        candidates2 = [
            ResourceCandidate(
                title="Resource B",
                description="Description B",
                source_url="https://example.com/b",
                org_name="Org B",
            ),
        ]

        connectors = [
            MockConnector(candidates1, name="Source 1", tier=1),
            MockConnector(candidates2, name="Source 2", tier=2),
        ]

        pipeline = ETLPipeline(etl_session)
        result = pipeline.run(connectors)

        assert result.success is True
        assert result.stats.extracted == 2
        assert result.stats.created == 2

    @requires_postgres
    def test_run_with_duplicates(self, etl_session):
        """Test that pipeline deduplicates across sources."""
        # Same resource from two sources
        candidate = ResourceCandidate(
            title="Test Resource",
            description="Description",
            source_url="https://example.com/resource",
            org_name="Test Org",
        )

        connectors = [
            MockConnector([candidate], name="Source 1", tier=1),
            MockConnector([candidate], name="Source 2", tier=2),
        ]

        pipeline = ETLPipeline(etl_session)
        result = pipeline.run(connectors)

        # Should extract 2 but dedupe to 1
        assert result.stats.extracted == 2
        assert result.stats.deduplicated == 1
        assert result.stats.created == 1

    @requires_postgres
    def test_run_with_invalid_candidates(self, etl_session):
        """Test handling of invalid candidates."""
        candidates = [
            ResourceCandidate(
                title="Valid Resource",
                description="Valid description",
                source_url="https://example.com/valid",
                org_name="Valid Org",
            ),
            ResourceCandidate(
                title="",  # Invalid - missing title
                description="Description",
                source_url="https://example.com/invalid",
                org_name="",  # Invalid - missing org
            ),
        ]

        connector = MockConnector(candidates)

        pipeline = ETLPipeline(etl_session)
        result = pipeline.run([connector])

        assert result.stats.extracted == 2
        assert result.stats.normalized == 1
        assert result.stats.normalized_failed == 1
        assert len(result.errors) == 1
        assert result.errors[0].stage == "normalize"

    @requires_postgres
    def test_run_with_failing_connector(self, etl_session, failing_connector, sample_candidate):
        """Test handling of connector failures."""
        connectors = [
            failing_connector,
            MockConnector([sample_candidate], name="Working Source"),
        ]

        pipeline = ETLPipeline(etl_session)
        result = pipeline.run(connectors)

        # Should have error from failing connector
        extract_errors = [e for e in result.errors if e.stage == "extract"]
        assert len(extract_errors) == 1
        assert "Failing Source" in extract_errors[0].message

        # Should still process working connector
        assert result.stats.extracted == 1
        assert result.stats.created == 1

    @requires_postgres
    def test_run_single(self, etl_session, sample_candidate):
        """Test run_single convenience method."""
        connector = MockConnector([sample_candidate])

        pipeline = ETLPipeline(etl_session)
        result = pipeline.run_single(connector)

        assert result.success is True
        assert result.stats.created == 1

    def test_normalize_only(self, etl_session, sample_candidate):
        """Test normalize_only method for testing connectors."""
        connector = MockConnector([sample_candidate], name="Test Source", tier=1)

        pipeline = ETLPipeline(etl_session)
        normalized, errors = pipeline.normalize_only(connector)

        assert len(normalized) == 1
        assert len(errors) == 0
        assert normalized[0].title == sample_candidate.title
        assert normalized[0].source_name == "Test Source"

    @requires_postgres
    def test_dry_run(self, etl_session, sample_candidate):
        """Test dry run without database changes."""
        connector = MockConnector([sample_candidate])

        pipeline = ETLPipeline(etl_session)
        result = pipeline.dry_run([connector])

        assert result.success is True
        assert result.stats.extracted == 1
        assert result.stats.normalized == 1
        assert result.stats.enriched == 1
        # In dry run, all would-be-created
        assert result.stats.created == 1

        # But no actual database changes (resources table should be empty)
        from sqlmodel import select
        from app.models import Resource
        resources = etl_session.exec(select(Resource)).all()
        assert len(resources) == 0

    def test_empty_connectors(self, etl_session):
        """Test running with no connectors."""
        pipeline = ETLPipeline(etl_session)
        result = pipeline.run([])

        assert result.success is True
        assert result.stats.extracted == 0

    def test_connector_with_no_results(self, etl_session):
        """Test handling connector that returns no results."""
        connector = MockConnector([], name="Empty Source")

        pipeline = ETLPipeline(etl_session)
        result = pipeline.run([connector])

        assert result.success is True
        assert result.stats.extracted == 0
        assert result.stats.created == 0

    @requires_postgres
    def test_enrichment_in_pipeline(self, etl_session):
        """Test that enrichment is applied in pipeline."""
        candidate = ResourceCandidate(
            title="Employment Services",
            description="Job placement and career counseling for veterans",
            source_url="https://example.com",
            org_name="Test Org",
            categories=[],  # Empty - should be inferred
        )

        connector = MockConnector([candidate], tier=2)

        pipeline = ETLPipeline(etl_session)
        result = pipeline.run([connector])

        # Verify enrichment occurred
        from sqlmodel import select
        from app.models import Resource
        db_resource = etl_session.exec(select(Resource)).first()

        assert db_resource is not None
        # Categories should be inferred from content
        assert "employment" in db_resource.categories
        # Reliability should be set from tier
        assert db_resource.reliability_score == 0.8  # Tier 2

    def test_result_duration(self, etl_session, sample_candidate):
        """Test that result includes duration."""
        connector = MockConnector([sample_candidate])

        pipeline = ETLPipeline(etl_session)
        # Use dry_run which doesn't need DB
        result = pipeline.dry_run([connector])

        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.duration_seconds is not None
        assert result.duration_seconds >= 0

    @requires_postgres
    def test_source_tier_respected(self, etl_session):
        """Test that source tier is respected in deduplication."""
        # Same resource from tier 4 and tier 1 sources
        candidate = ResourceCandidate(
            title="Test Resource",
            description="Description",
            source_url="https://example.com/resource",
            org_name="Test Org",
        )

        connectors = [
            MockConnector([candidate], name="Community Source", tier=4),
            MockConnector([candidate], name="VA.gov", tier=1),
        ]

        pipeline = ETLPipeline(etl_session)
        result = pipeline.run(connectors)

        # Should keep tier 1
        from sqlmodel import select
        from app.models import Resource
        db_resource = etl_session.exec(select(Resource)).first()

        assert db_resource.reliability_score == 1.0  # Tier 1 score


class TestCreatePipeline:
    """Tests for the create_pipeline factory function."""

    def test_create_pipeline(self, etl_session):
        """Test factory function creates pipeline."""
        pipeline = create_pipeline(etl_session)

        assert isinstance(pipeline, ETLPipeline)
        assert pipeline.session is etl_session

    def test_create_pipeline_with_geocoder(self, etl_session):
        """Test factory function accepts geocoder."""
        class TestGeocoder:
            def geocode(self, *args):
                return None, None

        geocoder = TestGeocoder()
        pipeline = create_pipeline(etl_session, geocoder=geocoder)

        assert pipeline.enricher.geocoder is geocoder
