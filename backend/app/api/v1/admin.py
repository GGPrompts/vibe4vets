"""Admin endpoints for review queue and source management."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/review-queue")
async def get_review_queue(
    status: str = "pending",
    limit: int = 20,
    db: Session = Depends(get_db),
) -> dict:
    """Get resources pending review."""
    # TODO: Implement after models
    return {"items": [], "total": 0}


@router.post("/review/{resource_id}")
async def review_resource(
    resource_id: str,
    action: str,  # approve, reject
    notes: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Approve or reject a resource."""
    # TODO: Implement with auth
    return {"resource_id": resource_id, "action": action, "success": True}


@router.get("/sources")
async def get_sources(db: Session = Depends(get_db)) -> dict:
    """Get all data sources with health status."""
    # TODO: Implement after models
    return {"sources": []}


@router.get("/sources/{source_id}/health")
async def get_source_health(source_id: str, db: Session = Depends(get_db)) -> dict:
    """Get detailed health info for a source."""
    return {
        "source_id": source_id,
        "status": "unknown",
        "last_run": None,
        "last_success": None,
        "error_count": 0,
    }
