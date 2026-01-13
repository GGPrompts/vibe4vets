"""Resource CRUD endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.database import SessionDep
from app.models.resource import ResourceStatus
from app.schemas.resource import ResourceCreate, ResourceList, ResourceRead, ResourceUpdate
from app.services.resource import ResourceService

router = APIRouter()


@router.get("", response_model=ResourceList)
def list_resources(
    session: SessionDep,
    category: str | None = Query(default=None, description="Filter by category"),
    state: str | None = Query(default=None, description="Filter by state (2-letter code)"),
    status: ResourceStatus | None = Query(default=None, description="Filter by status"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
) -> ResourceList:
    """List resources with optional filtering and pagination."""
    service = ResourceService(session)
    resources, total = service.list_resources(
        category=category,
        state=state,
        status=status,
        limit=limit,
        offset=offset,
    )
    return ResourceList(resources=resources, total=total, limit=limit, offset=offset)


@router.get("/{resource_id}", response_model=ResourceRead)
def get_resource(resource_id: UUID, session: SessionDep) -> ResourceRead:
    """Get a single resource by ID."""
    service = ResourceService(session)
    resource = service.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.post("", response_model=ResourceRead, status_code=201)
def create_resource(data: ResourceCreate, session: SessionDep) -> ResourceRead:
    """Create a new resource.

    This endpoint is for manual resource entry. It will:
    - Create or find the associated organization
    - Create a location if address details are provided
    - Set initial trust scores for manual entry
    """
    service = ResourceService(session)
    return service.create_resource(data)


@router.patch("/{resource_id}", response_model=ResourceRead)
def update_resource(
    resource_id: UUID,
    data: ResourceUpdate,
    session: SessionDep,
) -> ResourceRead:
    """Update a resource.

    Partial updates are supported - only include fields you want to change.
    Changes to sensitive fields (phone, website, eligibility) may trigger review.
    """
    service = ResourceService(session)
    resource = service.update_resource(resource_id, data)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.delete("/{resource_id}", status_code=204)
def delete_resource(resource_id: UUID, session: SessionDep) -> None:
    """Soft delete a resource by setting status to inactive."""
    service = ResourceService(session)
    if not service.delete_resource(resource_id):
        raise HTTPException(status_code=404, detail="Resource not found")
