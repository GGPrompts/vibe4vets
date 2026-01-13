"""Admin endpoints for review queue, source management, and job scheduling."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import select

from app.database import SessionDep
from app.models import Source
from app.schemas.health import (
    DashboardStats,
    ErrorListResponse,
    SourceHealthDetail,
    SourceHealthListResponse,
)
from app.schemas.review import ReviewAction, ReviewQueueResponse
from app.services.health import HealthService
from app.services.review import ReviewService
from jobs import get_available_connectors, get_scheduler

router = APIRouter()


@router.get("/review-queue", response_model=ReviewQueueResponse)
def get_review_queue(
    session: SessionDep,
    status: str = Query(default="pending", description="Filter by status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ReviewQueueResponse:
    """Get resources pending review.

    Returns items that need human review due to:
    - Risky field changes (phone, address, eligibility)
    - New resources from lower-tier sources
    - Flagged during automated checks
    """
    service = ReviewService(session)
    items, total = service.get_queue(status=status, limit=limit, offset=offset)
    return ReviewQueueResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("/review/{review_id}")
def review_resource(
    review_id: UUID,
    action: ReviewAction,
    session: SessionDep,
) -> dict:
    """Approve or reject a pending review.

    - approve: Marks resource as verified and active
    - reject: Marks resource as inactive
    """
    service = ReviewService(session)
    review = service.process_review(review_id, action)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return {
        "review_id": str(review.id),
        "resource_id": str(review.resource_id),
        "action": action.action.value,
        "success": True,
    }


class SourceHealth(BaseModel):
    """Source health information."""

    source_id: str
    name: str
    url: str
    tier: int
    status: str
    last_run: str | None
    last_success: str | None
    error_count: int


class SourcesResponse(BaseModel):
    """Response for sources endpoint."""

    sources: list[SourceHealth]


@router.get("/sources", response_model=SourcesResponse)
def get_sources(session: SessionDep) -> SourcesResponse:
    """Get all data sources with health status."""
    stmt = select(Source).order_by(Source.tier, Source.name)
    sources = session.exec(stmt).all()

    return SourcesResponse(
        sources=[
            SourceHealth(
                source_id=str(s.id),
                name=s.name,
                url=s.url,
                tier=s.tier,
                status=s.health_status.value,
                last_run=s.last_run.isoformat() if s.last_run else None,
                last_success=s.last_success.isoformat() if s.last_success else None,
                error_count=s.error_count,
            )
            for s in sources
        ]
    )


@router.get("/sources/{source_id}/health")
def get_source_health(source_id: UUID, session: SessionDep) -> dict:
    """Get detailed health info for a source."""
    source = session.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Count resources from this source
    from sqlmodel import func

    from app.models import Resource

    resource_count = session.exec(
        select(func.count(Resource.id)).where(Resource.source_id == source_id)
    ).one()

    return {
        "source_id": str(source.id),
        "name": source.name,
        "url": source.url,
        "tier": source.tier,
        "source_type": source.source_type.value,
        "frequency": source.frequency,
        "status": source.health_status.value,
        "last_run": source.last_run.isoformat() if source.last_run else None,
        "last_success": source.last_success.isoformat() if source.last_success else None,
        "error_count": source.error_count,
        "resource_count": resource_count,
    }


# ============================================================================
# Dashboard Endpoints
# ============================================================================


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(session: SessionDep) -> DashboardStats:
    """Get aggregated statistics for the admin dashboard.

    Returns:
    - Total source and resource counts
    - Sources grouped by health status (healthy, degraded, failing)
    - Resources grouped by category and status
    - Stale resource count (not verified in 30 days)
    - Recent job execution summaries
    """
    service = HealthService(session)
    return service.get_dashboard_stats()


@router.get("/dashboard/sources", response_model=SourceHealthListResponse)
def get_sources_health_detailed(session: SessionDep) -> SourceHealthListResponse:
    """Get all sources with detailed health information.

    Returns comprehensive health metrics for each source including:
    - Resource counts and status distribution
    - Average freshness score
    - Success rate over recent runs
    - Recent error history
    """
    service = HealthService(session)
    sources = service.get_all_sources_health()
    return SourceHealthListResponse(sources=sources, total=len(sources))


@router.get("/dashboard/sources/{source_id}", response_model=SourceHealthDetail)
def get_source_health_detailed(
    source_id: UUID, session: SessionDep
) -> SourceHealthDetail:
    """Get detailed health information for a single source.

    Returns comprehensive health metrics including:
    - Resource counts and status distribution
    - Average freshness score
    - Success rate calculation
    - Recent error history
    """
    service = HealthService(session)
    health = service.get_source_health(source_id)
    if not health:
        raise HTTPException(status_code=404, detail="Source not found")
    return health


@router.get("/dashboard/errors", response_model=ErrorListResponse)
def get_recent_errors(
    session: SessionDep,
    limit: int = Query(default=20, ge=1, le=100, description="Maximum errors to return"),
) -> ErrorListResponse:
    """Get recent errors across all sources.

    Returns the most recent errors from all data sources,
    useful for monitoring overall system health.
    """
    service = HealthService(session)
    errors = service.get_all_errors(limit=limit)
    return ErrorListResponse(errors=errors, total=len(errors))


# ============================================================================
# Job Management Endpoints
# ============================================================================


class JobInfo(BaseModel):
    """Information about a scheduled job."""

    name: str
    description: str
    scheduled: bool
    next_run: str | None


class JobsResponse(BaseModel):
    """Response for jobs list endpoint."""

    jobs: list[JobInfo]
    scheduler_running: bool


class JobRunRequest(BaseModel):
    """Request to run a job manually."""

    connector_name: str | None = None
    dry_run: bool = False


class JobHistoryEntry(BaseModel):
    """Entry in job history."""

    run_id: str
    job_name: str
    status: str
    started_at: str
    completed_at: str | None
    message: str
    stats: dict[str, Any]
    error: str | None


class JobHistoryResponse(BaseModel):
    """Response for job history endpoint."""

    history: list[JobHistoryEntry]
    total: int


@router.get("/jobs", response_model=JobsResponse)
def list_jobs() -> JobsResponse:
    """List all scheduled jobs with their next run times.

    Returns information about each registered job including:
    - Whether it's scheduled
    - When it will run next
    - Job description
    """
    scheduler = get_scheduler()
    jobs = scheduler.get_scheduled_jobs()

    return JobsResponse(
        jobs=[
            JobInfo(
                name=j["name"],
                description=j["description"],
                scheduled=j["scheduled"],
                next_run=j["next_run"],
            )
            for j in jobs
        ],
        scheduler_running=scheduler.is_running,
    )


@router.post("/jobs/{job_name}/run")
async def run_job(
    job_name: str,
    request: JobRunRequest | None = None,
) -> dict[str, Any]:
    """Trigger a job to run immediately.

    Args:
        job_name: Name of the job to run (e.g., "refresh" or "freshness").
        request: Optional request body with job parameters.

    Returns:
        Job result with statistics and any errors.
    """
    scheduler = get_scheduler()

    if job_name not in scheduler.jobs:
        available = list(scheduler.jobs.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_name}' not found. Available: {available}",
        )

    # Build kwargs from request
    kwargs: dict[str, Any] = {}
    if request:
        if request.connector_name:
            kwargs["connector_name"] = request.connector_name
        if request.dry_run:
            kwargs["dry_run"] = request.dry_run

    try:
        result = await scheduler.run_job(job_name, **kwargs)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Job execution failed: {str(e)}",
        )


@router.get("/jobs/history", response_model=JobHistoryResponse)
def get_job_history(
    limit: int = Query(default=20, ge=1, le=100),
) -> JobHistoryResponse:
    """Get recent job execution history.

    Args:
        limit: Maximum number of entries to return (default 20).

    Returns:
        List of recent job runs with results.
    """
    scheduler = get_scheduler()
    history = scheduler.get_history(limit=limit)

    return JobHistoryResponse(
        history=[
            JobHistoryEntry(
                run_id=h["run_id"],
                job_name=h["job_name"],
                status=h["status"],
                started_at=h["started_at"],
                completed_at=h["completed_at"],
                message=h["message"],
                stats=h["stats"],
                error=h["error"],
            )
            for h in history
        ],
        total=len(history),
    )


@router.get("/jobs/connectors")
def list_connectors() -> dict[str, Any]:
    """List available data source connectors.

    Returns metadata about each connector that can be used
    with the refresh job.
    """
    connectors = get_available_connectors()
    return {
        "connectors": connectors,
        "total": len(connectors),
    }
