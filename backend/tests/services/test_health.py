"""Tests for HealthService."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import Session

# Import all models to ensure SQLModel resolves relationships
# This must happen before any model instantiation
import app.models  # noqa: F401
from app.models import (
    HealthStatus,
    Organization,
    Resource,
    ResourceStatus,
    Source,
    SourceErrorType,
    SourceType,
)
from app.services.health import (
    STALE_THRESHOLD_DAYS,
    HealthService,
)

# Skip tests that require PostgreSQL ARRAY types
requires_postgres = pytest.mark.skip(reason="Test requires PostgreSQL for ARRAY column types")


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def health_service(session: Session) -> HealthService:
    """Create a HealthService with the test session."""
    return HealthService(session)


@pytest.fixture
def organization(session: Session) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Test Organization",
        website="https://test.org",
    )
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


@pytest.fixture
def source(session: Session) -> Source:
    """Create a test source."""
    src = Source(
        name="test_source",
        url="https://test.source.org",
        source_type=SourceType.API,
        tier=1,
        health_status=HealthStatus.HEALTHY,
    )
    session.add(src)
    session.commit()
    session.refresh(src)
    return src


@pytest.fixture
def degraded_source(session: Session) -> Source:
    """Create a degraded source."""
    src = Source(
        name="degraded_source",
        url="https://degraded.source.org",
        source_type=SourceType.SCRAPE,
        tier=2,
        health_status=HealthStatus.DEGRADED,
        error_count=2,
    )
    session.add(src)
    session.commit()
    session.refresh(src)
    return src


@pytest.fixture
def failing_source(session: Session) -> Source:
    """Create a failing source."""
    src = Source(
        name="failing_source",
        url="https://failing.source.org",
        source_type=SourceType.SCRAPE,
        tier=3,
        health_status=HealthStatus.FAILING,
        error_count=5,
    )
    session.add(src)
    session.commit()
    session.refresh(src)
    return src


@pytest.fixture
def resource(session: Session, organization: Organization, source: Source) -> Resource:
    """Create a test resource."""
    res = Resource(
        organization_id=organization.id,
        source_id=source.id,
        title="Test Resource",
        description="A test resource for veterans",
        categories=["employment"],
        status=ResourceStatus.ACTIVE,
        freshness_score=0.8,
        last_verified=datetime.now(UTC),
    )
    session.add(res)
    session.commit()
    session.refresh(res)
    return res


def create_resource(
    session: Session,
    organization: Organization,
    source: Source | None = None,
    categories: list[str] | None = None,
    status: ResourceStatus = ResourceStatus.ACTIVE,
    freshness_score: float = 1.0,
    last_verified: datetime | None = None,
) -> Resource:
    """Helper to create resources with custom attributes."""
    res = Resource(
        organization_id=organization.id,
        source_id=source.id if source else None,
        title=f"Resource {uuid.uuid4().hex[:8]}",
        description="Test description",
        categories=categories or ["employment"],
        status=status,
        freshness_score=freshness_score,
        last_verified=last_verified or datetime.now(UTC),
    )
    session.add(res)
    session.commit()
    session.refresh(res)
    return res


# ============================================================================
# Dashboard Stats Tests
# ============================================================================


class TestGetDashboardStats:
    """Tests for HealthService.get_dashboard_stats()."""

    def test_empty_database(self, health_service: HealthService) -> None:
        """Test dashboard stats with no data."""
        stats = health_service.get_dashboard_stats()

        assert stats.total_sources == 0
        assert stats.total_resources == 0
        assert stats.stale_resources == 0
        assert stats.sources_by_status == {
            "healthy": 0,
            "degraded": 0,
            "failing": 0,
        }

    def test_sources_by_status(
        self,
        health_service: HealthService,
        source: Source,
        degraded_source: Source,
        failing_source: Source,
    ) -> None:
        """Test counting sources by health status."""
        stats = health_service.get_dashboard_stats()

        assert stats.total_sources == 3
        assert stats.sources_by_status["healthy"] == 1
        assert stats.sources_by_status["degraded"] == 1
        assert stats.sources_by_status["failing"] == 1

    @requires_postgres
    def test_resources_by_category(
        self,
        session: Session,
        health_service: HealthService,
        organization: Organization,
        source: Source,
    ) -> None:
        """Test counting resources by category."""
        # Create resources with different categories
        create_resource(session, organization, source, categories=["employment"])
        create_resource(session, organization, source, categories=["training"])
        create_resource(session, organization, source, categories=["employment", "training"])
        create_resource(session, organization, source, categories=["housing"])

        stats = health_service.get_dashboard_stats()

        # employment: 2 (one solo, one combined)
        # training: 2 (one solo, one combined)
        # housing: 1
        assert stats.resources_by_category["employment"] == 2
        assert stats.resources_by_category["training"] == 2
        assert stats.resources_by_category["housing"] == 1

    @requires_postgres
    def test_resources_by_status(
        self,
        session: Session,
        health_service: HealthService,
        organization: Organization,
        source: Source,
    ) -> None:
        """Test counting resources by status."""
        create_resource(session, organization, source, status=ResourceStatus.ACTIVE)
        create_resource(session, organization, source, status=ResourceStatus.ACTIVE)
        create_resource(session, organization, source, status=ResourceStatus.NEEDS_REVIEW)
        create_resource(session, organization, source, status=ResourceStatus.INACTIVE)

        stats = health_service.get_dashboard_stats()

        assert stats.total_resources == 4
        assert stats.resources_by_status["active"] == 2
        assert stats.resources_by_status["needs_review"] == 1
        assert stats.resources_by_status["inactive"] == 1

    @requires_postgres
    def test_stale_resources(
        self,
        session: Session,
        health_service: HealthService,
        organization: Organization,
        source: Source,
    ) -> None:
        """Test counting stale resources."""
        now = datetime.now(UTC)
        old_date = now - timedelta(days=STALE_THRESHOLD_DAYS + 1)

        # Fresh resource
        create_resource(session, organization, source, last_verified=now)
        # Stale resource
        create_resource(session, organization, source, last_verified=old_date)
        # No verification date (counts as stale)
        create_resource(session, organization, source, last_verified=None)

        stats = health_service.get_dashboard_stats()

        # 2 stale: one old, one never verified
        assert stats.stale_resources == 2


# ============================================================================
# Source Health Tests
# ============================================================================


class TestGetSourceHealth:
    """Tests for HealthService.get_source_health()."""

    def test_source_not_found(self, health_service: HealthService) -> None:
        """Test getting health for non-existent source."""
        result = health_service.get_source_health(uuid.uuid4())
        assert result is None

    def test_basic_health_info(
        self,
        health_service: HealthService,
        source: Source,
    ) -> None:
        """Test basic source health information."""
        health = health_service.get_source_health(source.id)

        assert health is not None
        assert health.source_id == str(source.id)
        assert health.name == source.name
        assert health.url == source.url
        assert health.tier == source.tier
        assert health.status == HealthStatus.HEALTHY.value

    @requires_postgres
    def test_health_with_resources(
        self,
        session: Session,
        health_service: HealthService,
        organization: Organization,
        source: Source,
    ) -> None:
        """Test source health includes resource counts."""
        create_resource(session, organization, source, status=ResourceStatus.ACTIVE)
        create_resource(session, organization, source, status=ResourceStatus.ACTIVE)
        create_resource(session, organization, source, status=ResourceStatus.NEEDS_REVIEW)

        health = health_service.get_source_health(source.id)

        assert health is not None
        assert health.resource_count == 3
        assert health.resources_by_status["active"] == 2
        assert health.resources_by_status["needs_review"] == 1

    @requires_postgres
    def test_average_freshness(
        self,
        session: Session,
        health_service: HealthService,
        organization: Organization,
        source: Source,
    ) -> None:
        """Test average freshness calculation."""
        create_resource(session, organization, source, freshness_score=1.0)
        create_resource(session, organization, source, freshness_score=0.5)
        create_resource(session, organization, source, freshness_score=0.5)

        health = health_service.get_source_health(source.id)

        # Average of 1.0, 0.5, 0.5 = ~0.67
        assert health is not None
        assert 0.65 <= health.average_freshness <= 0.70


class TestGetAllSourcesHealth:
    """Tests for HealthService.get_all_sources_health()."""

    def test_empty_database(self, health_service: HealthService) -> None:
        """Test with no sources."""
        result = health_service.get_all_sources_health()
        assert result == []

    def test_multiple_sources(
        self,
        health_service: HealthService,
        source: Source,
        degraded_source: Source,
        failing_source: Source,
    ) -> None:
        """Test getting health for all sources."""
        result = health_service.get_all_sources_health()

        assert len(result) == 3
        # Should be ordered by tier, then name
        names = [s.name for s in result]
        assert "test_source" in names
        assert "degraded_source" in names
        assert "failing_source" in names


# ============================================================================
# Connector Run Recording Tests
# ============================================================================


class TestRecordConnectorRun:
    """Tests for HealthService.record_connector_run()."""

    def test_record_success(
        self,
        health_service: HealthService,
        session: Session,
        source: Source,
    ) -> None:
        """Test recording a successful run."""
        # Add some errors first
        source.error_count = 2
        source.health_status = HealthStatus.DEGRADED
        session.add(source)
        session.commit()

        result = health_service.record_connector_run(
            source_name="test_source",
            success=True,
            stats={"created": 10, "updated": 5},
        )

        assert result is not None
        assert result.error_count == 0
        assert result.health_status == HealthStatus.HEALTHY
        assert result.last_run is not None
        assert result.last_success is not None

    def test_record_failure(
        self,
        health_service: HealthService,
        source: Source,
    ) -> None:
        """Test recording a failed run."""
        result = health_service.record_connector_run(
            source_name="test_source",
            success=False,
            stats={},
            error="Connection timeout",
        )

        assert result is not None
        assert result.error_count == 1
        assert result.health_status == HealthStatus.DEGRADED

    def test_record_multiple_failures(
        self,
        health_service: HealthService,
        source: Source,
    ) -> None:
        """Test recording multiple failures transitions to FAILING."""
        # Record 3 failures
        for _ in range(3):
            result = health_service.record_connector_run(
                source_name="test_source",
                success=False,
                stats={},
                error="Connection error",
            )

        assert result is not None
        assert result.error_count == 3
        assert result.health_status == HealthStatus.FAILING

    def test_record_unknown_source(self, health_service: HealthService) -> None:
        """Test recording for non-existent source."""
        result = health_service.record_connector_run(
            source_name="nonexistent",
            success=True,
            stats={},
        )
        assert result is None


# ============================================================================
# Error History Tests
# ============================================================================


class TestErrorHistory:
    """Tests for error recording and retrieval."""

    def test_record_error(
        self,
        session: Session,
        health_service: HealthService,
        source: Source,
    ) -> None:
        """Test recording an error."""
        error = health_service.record_error(
            source_id=source.id,
            error_type=SourceErrorType.CONNECTION,
            message="Connection refused",
            details={"host": "api.example.com", "port": 443},
            job_run_id="run-123",
        )

        assert error.id is not None
        assert error.source_id == source.id
        assert error.error_type == SourceErrorType.CONNECTION
        assert error.message == "Connection refused"
        assert error.details == {"host": "api.example.com", "port": 443}
        assert error.job_run_id == "run-123"

    def test_get_error_history(
        self,
        session: Session,
        health_service: HealthService,
        source: Source,
    ) -> None:
        """Test retrieving error history."""
        # Record multiple errors
        for i in range(5):
            health_service.record_error(
                source_id=source.id,
                error_type=SourceErrorType.UNKNOWN,
                message=f"Error {i}",
            )

        history = health_service.get_error_history(source.id, limit=3)

        assert len(history) == 3
        # Should be newest first
        assert history[0].message == "Error 4"
        assert history[0].source_name == source.name

    def test_get_all_errors(
        self,
        session: Session,
        health_service: HealthService,
        source: Source,
        degraded_source: Source,
    ) -> None:
        """Test retrieving errors across all sources."""
        health_service.record_error(
            source_id=source.id,
            error_type=SourceErrorType.TIMEOUT,
            message="Source 1 error",
        )
        health_service.record_error(
            source_id=degraded_source.id,
            error_type=SourceErrorType.PARSE,
            message="Source 2 error",
        )

        errors = health_service.get_all_errors(limit=10)

        assert len(errors) == 2
        source_names = {e.source_name for e in errors}
        assert source.name in source_names
        assert degraded_source.name in source_names


# ============================================================================
# Health Status Calculation Tests
# ============================================================================


class TestCalculateHealthStatus:
    """Tests for HealthService.calculate_health_status()."""

    def test_healthy_no_errors(self, health_service: HealthService) -> None:
        """Test healthy status with no errors."""
        source = Source(
            name="test",
            url="https://test.org",
            error_count=0,
            last_success=datetime.now(UTC),
        )
        status = health_service.calculate_health_status(source)
        assert status == HealthStatus.HEALTHY

    def test_degraded_one_error(self, health_service: HealthService) -> None:
        """Test degraded status with 1 error."""
        source = Source(
            name="test",
            url="https://test.org",
            error_count=1,
        )
        status = health_service.calculate_health_status(source)
        assert status == HealthStatus.DEGRADED

    def test_degraded_two_errors(self, health_service: HealthService) -> None:
        """Test degraded status with 2 errors."""
        source = Source(
            name="test",
            url="https://test.org",
            error_count=2,
        )
        status = health_service.calculate_health_status(source)
        assert status == HealthStatus.DEGRADED

    def test_failing_three_errors(self, health_service: HealthService) -> None:
        """Test failing status with 3+ errors."""
        source = Source(
            name="test",
            url="https://test.org",
            error_count=3,
        )
        status = health_service.calculate_health_status(source)
        assert status == HealthStatus.FAILING

    def test_failing_stale_success(self, health_service: HealthService) -> None:
        """Test failing status when last success is old."""
        source = Source(
            name="test",
            url="https://test.org",
            error_count=0,
            last_success=datetime.now(UTC) - timedelta(days=8),
        )
        status = health_service.calculate_health_status(source)
        assert status == HealthStatus.FAILING

    def test_degraded_moderately_stale(self, health_service: HealthService) -> None:
        """Test degraded status when last success is moderately old."""
        source = Source(
            name="test",
            url="https://test.org",
            error_count=0,
            last_success=datetime.now(UTC) - timedelta(days=5),
        )
        status = health_service.calculate_health_status(source)
        assert status == HealthStatus.DEGRADED
