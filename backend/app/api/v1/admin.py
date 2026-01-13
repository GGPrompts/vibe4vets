"""Admin endpoints for review queue and source management."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import select

from app.database import SessionDep
from app.models import Source
from app.schemas.review import ReviewAction, ReviewQueueResponse
from app.services.review import ReviewService

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
