"""Stats endpoints for AI transparency and system metrics."""

from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlmodel import func, select

from app.database import SessionDep
from app.models import Resource, ResourceStatus, Source
from jobs import get_available_connectors, get_scheduler

router = APIRouter()


class ConnectorInfo(BaseModel):
    """Information about a data connector."""

    name: str
    source_name: str
    tier: int
    description: str


class AIStats(BaseModel):
    """AI transparency statistics for the About page."""

    # Resource counts
    total_resources: int = Field(description="Total resources in database")
    resources_verified: int = Field(description="Resources that have been human-verified")
    resources_by_category: dict[str, int] = Field(
        description="Resource count by category"
    )

    # Source/connector info
    total_sources: int = Field(description="Number of data sources")
    connectors_active: list[ConnectorInfo] = Field(
        description="Active data connectors"
    )

    # Freshness info
    last_refresh: datetime | None = Field(
        default=None,
        description="When the last connector refresh ran"
    )
    average_trust_score: float = Field(
        ge=0.0, le=1.0, description="Average trust score across all resources"
    )

    # System info
    scheduler_status: str = Field(description="Whether the job scheduler is running")
    jobs_completed_today: int = Field(
        description="Number of jobs completed in last 24 hours"
    )


@router.get("/ai", response_model=AIStats)
def get_ai_stats(session: SessionDep) -> AIStats:
    """Get AI transparency statistics for the About page.

    This endpoint provides metrics about:
    - How many resources we've aggregated
    - What data sources and connectors we use
    - When data was last refreshed
    - Overall trust/quality metrics

    These stats are displayed on the About page to show transparency
    about how the AI-powered resource aggregation works.
    """
    # Count total resources
    total_resources = session.exec(
        select(func.count(Resource.id))
    ).one() or 0

    # Count verified resources (those that have been reviewed)
    resources_verified = session.exec(
        select(func.count(Resource.id)).where(
            Resource.last_verified != None  # noqa: E711
        )
    ).one() or 0

    # Count resources by category
    all_resources = session.exec(select(Resource.categories)).all()
    resources_by_category: dict[str, int] = {}
    for categories in all_resources:
        if categories:
            for cat in categories:
                resources_by_category[cat] = resources_by_category.get(cat, 0) + 1

    # Count sources
    total_sources = session.exec(
        select(func.count(Source.id))
    ).one() or 0

    # Get active connectors
    connectors_raw = get_available_connectors()
    connectors = [
        ConnectorInfo(
            name=c["name"],
            source_name=c["source_name"],
            tier=c["tier"],
            description=c["description"],
        )
        for c in connectors_raw
    ]

    # Get last refresh time from job history
    scheduler = get_scheduler()
    history = scheduler.get_history(limit=50)

    last_refresh: datetime | None = None
    jobs_completed_today = 0

    # Find last successful refresh and count today's jobs
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    for h in history:
        if h["job_name"] == "refresh" and h.get("completed_at"):
            completed = datetime.fromisoformat(h["completed_at"])
            if last_refresh is None:
                last_refresh = completed
        if h.get("completed_at"):
            completed = datetime.fromisoformat(h["completed_at"])
            if completed >= today_start:
                jobs_completed_today += 1

    # Calculate average trust score
    avg_trust = session.exec(
        select(func.avg(Resource.reliability_score * Resource.freshness_score)).where(
            Resource.status == ResourceStatus.ACTIVE
        )
    ).one()
    average_trust_score = float(avg_trust) if avg_trust else 0.0

    # Scheduler status
    scheduler_status = "Running" if scheduler.is_running else "Stopped"

    return AIStats(
        total_resources=total_resources,
        resources_verified=resources_verified,
        resources_by_category=resources_by_category,
        total_sources=total_sources,
        connectors_active=connectors,
        last_refresh=last_refresh,
        average_trust_score=round(average_trust_score, 2),
        scheduler_status=scheduler_status,
        jobs_completed_today=jobs_completed_today,
    )
