"""Admin endpoints for review queue and source management."""

from fastapi import APIRouter

from app.database import SessionDep

router = APIRouter()


@router.get("/review-queue")
def get_review_queue(
    session: SessionDep,
    status: str = "pending",
    limit: int = 20,
) -> dict:
    """Get resources pending review."""
    # TODO: Implement after models
    return {"items": [], "total": 0}


@router.post("/review/{resource_id}")
def review_resource(
    session: SessionDep,
    resource_id: str,
    action: str,  # approve, reject
    notes: str | None = None,
) -> dict:
    """Approve or reject a resource."""
    # TODO: Implement with auth
    return {"resource_id": resource_id, "action": action, "success": True}


@router.get("/sources")
def get_sources(session: SessionDep) -> dict:
    """Get all data sources with health status."""
    # TODO: Implement after models
    return {"sources": []}


@router.get("/sources/{source_id}/health")
def get_source_health(source_id: str, session: SessionDep) -> dict:
    """Get detailed health info for a source."""
    return {
        "source_id": source_id,
        "status": "unknown",
        "last_run": None,
        "last_success": None,
        "error_count": 0,
    }
