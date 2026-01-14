"""Health service for source monitoring and dashboard statistics."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlmodel import Session, func, select

from app.models import (
    HealthStatus,
    Resource,
    ResourceStatus,
    Source,
    SourceError,
    SourceErrorType,
)
from app.schemas.health import (
    DashboardStats,
    ErrorRecord,
    JobRunSummary,
    SourceHealthDetail,
)

# How many days without verification before a resource is considered stale
STALE_THRESHOLD_DAYS = 30

# How many recent runs to consider for success rate
SUCCESS_RATE_WINDOW = 10


class HealthService:
    """Service for source health monitoring and dashboard statistics."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_dashboard_stats(self) -> DashboardStats:
        """Get aggregated statistics for the admin dashboard.

        Returns dashboard-level metrics including:
        - Source counts by health status
        - Resource counts by category and status
        - Stale resource count
        - Recent job runs (from scheduler)
        """
        # Count sources by health status
        sources_by_status = self._count_sources_by_status()

        # Count resources by category
        resources_by_category = self._count_resources_by_category()

        # Count resources by status
        resources_by_status = self._count_resources_by_status()

        # Count stale resources (not verified in STALE_THRESHOLD_DAYS)
        stale_resources = self._count_stale_resources()

        # Get total counts
        total_sources = sum(sources_by_status.values())
        total_resources = sum(resources_by_status.values())

        # Get recent job runs from scheduler
        recent_job_runs = self._get_recent_job_runs()

        return DashboardStats(
            total_sources=total_sources,
            sources_by_status=sources_by_status,
            total_resources=total_resources,
            resources_by_category=resources_by_category,
            resources_by_status=resources_by_status,
            stale_resources=stale_resources,
            recent_job_runs=recent_job_runs,
        )

    def get_source_health(self, source_id: UUID) -> SourceHealthDetail | None:
        """Get detailed health information for a single source.

        Args:
            source_id: The source UUID.

        Returns:
            Detailed health info or None if source not found.
        """
        source = self.session.get(Source, source_id)
        if not source:
            return None

        # Count resources for this source
        resource_count = self._count_source_resources(source_id)

        # Get resources by status for this source
        resources_by_status = self._count_source_resources_by_status(source_id)

        # Calculate average freshness
        average_freshness = self._calculate_average_freshness(source_id)

        # Calculate success rate from error history
        success_rate = self._calculate_success_rate(source_id)

        # Get recent errors
        errors = self.get_error_history(source_id, limit=10)

        return SourceHealthDetail(
            source_id=str(source.id),
            name=source.name,
            url=source.url,
            tier=source.tier,
            source_type=source.source_type.value,
            frequency=source.frequency,
            status=source.health_status.value,
            resource_count=resource_count,
            resources_by_status=resources_by_status,
            average_freshness=average_freshness,
            last_run=source.last_run,
            last_success=source.last_success,
            error_count=source.error_count,
            success_rate=success_rate,
            errors=errors,
        )

    def get_all_sources_health(self) -> list[SourceHealthDetail]:
        """Get health details for all sources.

        Returns:
            List of SourceHealthDetail for each registered source.
        """
        stmt = select(Source).order_by(Source.tier, Source.name)
        sources = self.session.exec(stmt).all()

        result = []
        for source in sources:
            health = self.get_source_health(source.id)
            if health:
                result.append(health)

        return result

    def record_connector_run(
        self,
        source_name: str,
        success: bool,
        stats: dict,
        error: str | None = None,
        run_id: str | None = None,
    ) -> Source | None:
        """Record the result of a connector run.

        Updates the source's health tracking fields based on run outcome.

        Args:
            source_name: Name of the source (used to look up Source record).
            success: Whether the run succeeded.
            stats: Statistics from the run (resources_created, etc.).
            error: Error message if the run failed.
            run_id: Optional job run ID for linking to scheduler history.

        Returns:
            Updated Source or None if source not found.
        """
        # Find source by name
        stmt = select(Source).where(Source.name == source_name)
        source = self.session.exec(stmt).first()
        if not source:
            return None

        now = datetime.now(UTC)
        source.last_run = now

        if success:
            source.last_success = now
            # Reset error count on success
            source.error_count = 0
            source.health_status = HealthStatus.HEALTHY
        else:
            source.error_count += 1
            source.health_status = self.calculate_health_status(source)

            # Record the error
            if error:
                self.record_error(
                    source_id=source.id,
                    error_type=SourceErrorType.UNKNOWN,
                    message=error,
                    details={"stats": stats},
                    job_run_id=run_id,
                )

        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    def record_error(
        self,
        source_id: UUID,
        error_type: SourceErrorType,
        message: str,
        details: dict | None = None,
        job_run_id: str | None = None,
    ) -> SourceError:
        """Record an error for a source.

        Args:
            source_id: The source that had the error.
            error_type: Classification of the error.
            message: Human-readable error message.
            details: Additional context (stack trace, etc.).
            job_run_id: Optional link to job scheduler history.

        Returns:
            The created SourceError record.
        """
        error = SourceError(
            source_id=source_id,
            error_type=error_type,
            message=message,
            details=details,
            job_run_id=job_run_id,
        )
        self.session.add(error)
        self.session.commit()
        self.session.refresh(error)
        return error

    def get_error_history(
        self,
        source_id: UUID,
        limit: int = 10,
    ) -> list[ErrorRecord]:
        """Get recent errors for a source.

        Args:
            source_id: The source to get errors for.
            limit: Maximum number of errors to return.

        Returns:
            List of ErrorRecord, newest first.
        """
        stmt = (
            select(SourceError)
            .where(SourceError.source_id == source_id)
            .order_by(SourceError.occurred_at.desc())
            .limit(limit)
        )
        errors = self.session.exec(stmt).all()

        # Get source name for the records
        source = self.session.get(Source, source_id)
        source_name = source.name if source else "Unknown"

        return [
            ErrorRecord(
                id=e.id,
                source_id=e.source_id,
                source_name=source_name,
                error_type=e.error_type.value,
                message=e.message,
                occurred_at=e.occurred_at,
                job_run_id=e.job_run_id,
            )
            for e in errors
        ]

    def get_all_errors(self, limit: int = 20) -> list[ErrorRecord]:
        """Get recent errors across all sources.

        Args:
            limit: Maximum number of errors to return.

        Returns:
            List of ErrorRecord from all sources, newest first.
        """
        stmt = select(SourceError).order_by(SourceError.occurred_at.desc()).limit(limit)
        errors = self.session.exec(stmt).all()

        result = []
        for e in errors:
            source = self.session.get(Source, e.source_id)
            source_name = source.name if source else "Unknown"
            result.append(
                ErrorRecord(
                    id=e.id,
                    source_id=e.source_id,
                    source_name=source_name,
                    error_type=e.error_type.value,
                    message=e.message,
                    occurred_at=e.occurred_at,
                    job_run_id=e.job_run_id,
                )
            )
        return result

    def calculate_health_status(self, source: Source) -> HealthStatus:
        """Calculate health status based on error rate and freshness.

        Rules:
        - HEALTHY: No errors or last run was successful
        - DEGRADED: 1-2 consecutive errors
        - FAILING: 3+ consecutive errors or no successful run in 7 days

        Args:
            source: The source to evaluate.

        Returns:
            Calculated HealthStatus.
        """
        # Check error count threshold
        if source.error_count >= 3:
            return HealthStatus.FAILING

        if source.error_count >= 1:
            return HealthStatus.DEGRADED

        # Check freshness - if no success in 7 days, mark as failing
        if source.last_success:
            days_since_success = (datetime.now(UTC) - source.last_success).days
            if days_since_success > 7:
                return HealthStatus.FAILING
            if days_since_success > 3:
                return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    # =========================================================================
    # Private helper methods
    # =========================================================================

    def _count_sources_by_status(self) -> dict[str, int]:
        """Count sources grouped by health status."""
        result = {status.value: 0 for status in HealthStatus}

        stmt = select(Source.health_status, func.count(Source.id)).group_by(Source.health_status)
        counts = self.session.exec(stmt).all()

        for status, count in counts:
            result[status.value] = count

        return result

    def _count_resources_by_category(self) -> dict[str, int]:
        """Count resources by their categories.

        Note: Resources can have multiple categories, so totals may exceed
        the actual resource count.
        """
        # Get all resources with their categories
        stmt = select(Resource.categories)
        resources = self.session.exec(stmt).all()

        result: dict[str, int] = {}
        for categories in resources:
            if categories:
                for cat in categories:
                    result[cat] = result.get(cat, 0) + 1

        return result

    def _count_resources_by_status(self) -> dict[str, int]:
        """Count resources grouped by status."""
        result = {status.value: 0 for status in ResourceStatus}

        stmt = select(Resource.status, func.count(Resource.id)).group_by(Resource.status)
        counts = self.session.exec(stmt).all()

        for status, count in counts:
            result[status.value] = count

        return result

    def _count_stale_resources(self) -> int:
        """Count resources not verified within the stale threshold."""
        threshold = datetime.now(UTC) - timedelta(days=STALE_THRESHOLD_DAYS)

        stmt = select(func.count(Resource.id)).where(
            (Resource.last_verified == None)  # noqa: E711
            | (Resource.last_verified < threshold)
        )
        count = self.session.exec(stmt).one()
        return count or 0

    def _count_source_resources(self, source_id: UUID) -> int:
        """Count resources belonging to a source."""
        stmt = select(func.count(Resource.id)).where(Resource.source_id == source_id)
        count = self.session.exec(stmt).one()
        return count or 0

    def _count_source_resources_by_status(self, source_id: UUID) -> dict[str, int]:
        """Count resources for a source grouped by status."""
        result = {status.value: 0 for status in ResourceStatus}

        stmt = (
            select(Resource.status, func.count(Resource.id))
            .where(Resource.source_id == source_id)
            .group_by(Resource.status)
        )
        counts = self.session.exec(stmt).all()

        for status, count in counts:
            result[status.value] = count

        return result

    def _calculate_average_freshness(self, source_id: UUID) -> float:
        """Calculate average freshness score for a source's resources."""
        stmt = select(func.avg(Resource.freshness_score)).where(Resource.source_id == source_id)
        avg = self.session.exec(stmt).one()
        return float(avg) if avg is not None else 1.0

    def _calculate_success_rate(self, source_id: UUID) -> float:
        """Calculate success rate from recent error history.

        Uses a simple heuristic: looks at error count and last success
        to estimate success rate over the success rate window.
        """
        source = self.session.get(Source, source_id)
        if not source:
            return 1.0

        # If no errors, 100% success
        if source.error_count == 0:
            return 1.0

        # Count recent errors (last 7 days)
        week_ago = datetime.now(UTC) - timedelta(days=7)
        stmt = select(func.count(SourceError.id)).where(
            SourceError.source_id == source_id,
            SourceError.occurred_at >= week_ago,
        )
        recent_error_count = self.session.exec(stmt).one() or 0

        # Estimate: assume one run per day on average
        estimated_runs = min(7, SUCCESS_RATE_WINDOW)
        if estimated_runs == 0:
            return 1.0

        success_rate = max(0.0, (estimated_runs - recent_error_count) / estimated_runs)
        return round(success_rate, 2)

    def _get_recent_job_runs(self, limit: int = 5) -> list[JobRunSummary]:
        """Get recent job runs from the scheduler.

        This retrieves from the in-memory scheduler history.
        """
        from jobs import get_scheduler

        try:
            scheduler = get_scheduler()
            history = scheduler.get_history(limit=limit)

            return [
                JobRunSummary(
                    run_id=h["run_id"],
                    job_name=h["job_name"],
                    status=h["status"],
                    started_at=datetime.fromisoformat(h["started_at"]),
                    completed_at=(
                        datetime.fromisoformat(h["completed_at"]) if h.get("completed_at") else None
                    ),
                    message=h.get("message", ""),
                    resources_processed=h.get("stats", {}).get("processed", 0),
                    errors=1 if h.get("error") else 0,
                )
                for h in history
            ]
        except Exception:
            # Scheduler may not be initialized in tests
            return []
