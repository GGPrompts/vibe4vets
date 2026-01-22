"""Tests for ETL pipeline idempotency.

Tests verify that:
1. ETL jobs can be safely re-run without creating duplicates
2. Progress is checkpointed and can be resumed
3. Already-processed URLs are skipped on retry
"""

import uuid
from datetime import UTC, datetime

import pytest
from sqlmodel import select

from app.models import ETLJobRun, ETLJobStatus, Resource
from connectors.base import ResourceCandidate
from etl.loader import Loader
from etl.models import NormalizedResource
from etl.pipeline import (
    ETLPipeline,
    create_pipeline,
    get_latest_job,
    resume_job,
    start_job,
)
from tests.etl.conftest import MockConnector

# Skip tests that require PostgreSQL
pytestmark = pytest.mark.skip(reason="Idempotency tests require PostgreSQL (JSONB column type)")


class TestETLJobRun:
    """Tests for ETLJobRun model."""

    def test_mark_url_processed(self, etl_session):
        """Test marking URLs as processed."""
        job_run = ETLJobRun(
            id=uuid.uuid4(),
            job_name="test_job",
        )
        etl_session.add(job_run)
        etl_session.commit()

        # Initially empty
        assert not job_run.is_url_processed("https://example.com/1")

        # Mark as processed
        job_run.mark_url_processed("https://example.com/1")
        assert job_run.is_url_processed("https://example.com/1")

        # Duplicate marking doesn't add twice
        job_run.mark_url_processed("https://example.com/1")
        assert job_run.processed_urls.count("https://example.com/1") == 1

    def test_update_checkpoint(self, etl_session):
        """Test checkpoint updates."""
        job_run = ETLJobRun(
            id=uuid.uuid4(),
            job_name="test_job",
        )
        etl_session.add(job_run)
        etl_session.commit()

        job_run.update_checkpoint(connector_idx=2, resource_idx=50)
        assert job_run.checkpoint_connector_idx == 2
        assert job_run.checkpoint_resource_idx == 50


class TestStartJob:
    """Tests for start_job function."""

    def test_creates_job_run(self, etl_session):
        """Test that start_job creates a new job run."""
        job_run = start_job(etl_session, "test_refresh")

        assert job_run.id is not None
        assert job_run.job_name == "test_refresh"
        assert job_run.status == ETLJobStatus.PENDING
        assert job_run.started_at is not None

        # Verify persisted to database
        loaded = etl_session.get(ETLJobRun, job_run.id)
        assert loaded is not None
        assert loaded.job_name == "test_refresh"


class TestResumeJob:
    """Tests for resume_job function."""

    def test_resumes_failed_job(self, etl_session):
        """Test resuming a failed job."""
        job_run = ETLJobRun(
            id=uuid.uuid4(),
            job_name="test_job",
            status=ETLJobStatus.FAILED,
        )
        etl_session.add(job_run)
        etl_session.commit()

        resumed = resume_job(etl_session, job_run.id)
        assert resumed is not None
        assert resumed.id == job_run.id

    def test_resumes_partially_completed_job(self, etl_session):
        """Test resuming a partially completed job."""
        job_run = ETLJobRun(
            id=uuid.uuid4(),
            job_name="test_job",
            status=ETLJobStatus.PARTIALLY_COMPLETED,
        )
        etl_session.add(job_run)
        etl_session.commit()

        resumed = resume_job(etl_session, job_run.id)
        assert resumed is not None

    def test_does_not_resume_completed_job(self, etl_session):
        """Test that completed jobs cannot be resumed."""
        job_run = ETLJobRun(
            id=uuid.uuid4(),
            job_name="test_job",
            status=ETLJobStatus.COMPLETED,
        )
        etl_session.add(job_run)
        etl_session.commit()

        resumed = resume_job(etl_session, job_run.id)
        assert resumed is None

    def test_does_not_resume_running_job(self, etl_session):
        """Test that running jobs cannot be resumed."""
        job_run = ETLJobRun(
            id=uuid.uuid4(),
            job_name="test_job",
            status=ETLJobStatus.RUNNING,
        )
        etl_session.add(job_run)
        etl_session.commit()

        resumed = resume_job(etl_session, job_run.id)
        assert resumed is None

    def test_returns_none_for_unknown_id(self, etl_session):
        """Test that unknown job ID returns None."""
        resumed = resume_job(etl_session, uuid.uuid4())
        assert resumed is None


class TestGetLatestJob:
    """Tests for get_latest_job function."""

    def test_returns_most_recent(self, etl_session):
        """Test that get_latest_job returns the most recent job."""
        # Create older job
        old_job = ETLJobRun(
            id=uuid.uuid4(),
            job_name="test_job",
            started_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
        )
        etl_session.add(old_job)

        # Create newer job
        new_job = ETLJobRun(
            id=uuid.uuid4(),
            job_name="test_job",
            started_at=datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC),
        )
        etl_session.add(new_job)
        etl_session.commit()

        latest = get_latest_job(etl_session, "test_job")
        assert latest is not None
        assert latest.id == new_job.id

    def test_returns_none_for_unknown_job(self, etl_session):
        """Test that unknown job name returns None."""
        latest = get_latest_job(etl_session, "nonexistent_job")
        assert latest is None


class TestLoaderIdempotency:
    """Tests for Loader idempotency with job_run."""

    def test_skips_already_processed_urls(self, etl_session):
        """Test that already-processed URLs are skipped."""
        # Create job run with a processed URL
        job_run = ETLJobRun(
            id=uuid.uuid4(),
            job_name="test_job",
            processed_urls=["https://example.com/1"],
        )
        etl_session.add(job_run)
        etl_session.commit()

        loader = Loader(etl_session, job_run=job_run)

        resource = NormalizedResource(
            title="Test Resource",
            description="Test",
            source_url="https://example.com/1",  # Already processed
            org_name="Test Org",
        )

        result = loader.load(resource)
        assert result.action == "skipped"
        assert "Already processed" in (result.error or "")

    def test_marks_url_as_processed(self, etl_session):
        """Test that loaded URLs are marked as processed."""
        job_run = ETLJobRun(
            id=uuid.uuid4(),
            job_name="test_job",
        )
        etl_session.add(job_run)
        etl_session.commit()

        loader = Loader(etl_session, job_run=job_run)

        resource = NormalizedResource(
            title="Test Resource",
            description="Test",
            source_url="https://example.com/new",
            org_name="Test Org",
        )

        loader.load(resource)

        # URL should now be marked as processed
        assert job_run.is_url_processed("https://example.com/new")

    def test_batch_commits_atomically(self, etl_session):
        """Test that batch loading commits atomically."""
        job_run = start_job(etl_session, "test_job")
        loader = Loader(etl_session, job_run=job_run)

        resources = [
            NormalizedResource(
                title=f"Resource {i}",
                description=f"Description {i}",
                source_url=f"https://example.com/{i}",
                org_name=f"Org {i}",
            )
            for i in range(3)
        ]

        results, errors = loader.load_batch(resources, checkpoint_batch_size=10)

        assert len(results) == 3
        assert len(errors) == 0
        assert all(r.action == "created" for r in results)

        # All URLs should be marked as processed
        for i in range(3):
            assert job_run.is_url_processed(f"https://example.com/{i}")


class TestPipelineIdempotency:
    """Tests for pipeline idempotency."""

    def test_pipeline_updates_job_status(self, etl_session, sample_candidate):
        """Test that pipeline updates job run status."""
        job_run = start_job(etl_session, "test_pipeline")
        connector = MockConnector([sample_candidate])

        pipeline = create_pipeline(etl_session, job_run=job_run)
        result = pipeline.run([connector])

        # Refresh job_run from database
        etl_session.refresh(job_run)

        assert result.success is True
        assert job_run.status == ETLJobStatus.COMPLETED
        assert job_run.completed_at is not None
        assert job_run.total_created == 1

    def test_pipeline_skips_processed_on_retry(self, etl_session):
        """Test that re-running pipeline skips already-processed resources."""
        candidate = ResourceCandidate(
            title="Test Resource",
            description="Test description",
            source_url="https://example.com/resource",
            org_name="Test Org",
        )

        # First run
        job_run1 = start_job(etl_session, "test_run1")
        pipeline1 = create_pipeline(etl_session, job_run=job_run1)
        result1 = pipeline1.run([MockConnector([candidate])])

        assert result1.stats.created == 1

        # Simulate retry with same job run (e.g., after resume)
        # In practice, you'd resume the existing job_run
        job_run1.status = ETLJobStatus.PENDING  # Reset for retry
        etl_session.add(job_run1)
        etl_session.commit()

        pipeline2 = create_pipeline(etl_session, job_run=job_run1)
        result2 = pipeline2.run([MockConnector([candidate])])

        # Should skip the already-processed resource
        assert result2.stats.created == 0
        assert result2.stats.skipped == 1

    def test_pipeline_without_job_run_still_works(self, etl_session, sample_candidate):
        """Test that pipeline works without job_run (backward compatibility)."""
        connector = MockConnector([sample_candidate])

        pipeline = create_pipeline(etl_session)  # No job_run
        result = pipeline.run([connector])

        assert result.success is True
        assert result.stats.created == 1

    def test_pipeline_records_connector_names(self, etl_session, sample_candidate):
        """Test that pipeline records connector names in job run."""
        job_run = start_job(etl_session, "test_connectors")
        connector1 = MockConnector([sample_candidate], name="Connector A")
        connector2 = MockConnector([], name="Connector B")

        pipeline = create_pipeline(etl_session, job_run=job_run)
        pipeline.run([connector1, connector2])

        etl_session.refresh(job_run)
        assert "Connector A" in job_run.connector_names
        assert "Connector B" in job_run.connector_names

    def test_pipeline_handles_connector_failure(self, etl_session, sample_candidate, failing_connector):
        """Test that pipeline records errors but continues."""
        job_run = start_job(etl_session, "test_failure")

        connectors = [
            failing_connector,
            MockConnector([sample_candidate], name="Working"),
        ]

        pipeline = create_pipeline(etl_session, job_run=job_run)
        result = pipeline.run(connectors)

        etl_session.refresh(job_run)

        # Should have error from failing connector
        assert len(result.errors) > 0

        # But still processed the working connector
        assert result.stats.created == 1

        # Job should be partially completed (had errors but some success)
        assert job_run.status in (ETLJobStatus.COMPLETED, ETLJobStatus.PARTIALLY_COMPLETED)
