"""Resource CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("")
async def list_resources(
    category: str | None = None,
    state: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> dict:
    """List resources with optional filtering."""
    # TODO: Implement after models are created
    return {"resources": [], "total": 0, "limit": limit, "offset": offset}


@router.get("/{resource_id}")
async def get_resource(resource_id: str, db: Session = Depends(get_db)) -> dict:
    """Get a single resource by ID."""
    # TODO: Implement after models are created
    raise HTTPException(status_code=404, detail="Resource not found")


@router.post("")
async def create_resource(db: Session = Depends(get_db)) -> dict:
    """Create a new resource (admin only)."""
    # TODO: Implement with auth
    return {"id": "placeholder"}
