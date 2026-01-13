"""Resource CRUD endpoints."""

from fastapi import APIRouter, HTTPException

from app.database import SessionDep

router = APIRouter()


@router.get("")
def list_resources(
    session: SessionDep,
    category: str | None = None,
    state: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """List resources with optional filtering."""
    # TODO: Implement after models are created
    return {"resources": [], "total": 0, "limit": limit, "offset": offset}


@router.get("/{resource_id}")
def get_resource(resource_id: str, session: SessionDep) -> dict:
    """Get a single resource by ID."""
    # TODO: Implement after models are created
    raise HTTPException(status_code=404, detail="Resource not found")


@router.post("")
def create_resource(session: SessionDep) -> dict:
    """Create a new resource (admin only)."""
    # TODO: Implement with auth
    return {"id": "placeholder"}
