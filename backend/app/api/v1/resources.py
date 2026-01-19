"""Resource CRUD endpoints.

Provides REST API for managing veteran resources including listing, creating,
updating, and deleting resources with filtering and pagination support.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.database import SessionDep
from app.models.resource import ResourceStatus
from app.schemas.resource import ResourceCreate, ResourceList, ResourceRead, ResourceUpdate
from app.services.resource import ResourceService

router = APIRouter()


@router.get(
    "",
    response_model=ResourceList,
    summary="List resources",
    response_description="Paginated list of resources with total count",
    responses={
        200: {
            "description": "Successful response with list of resources",
            "content": {
                "application/json": {
                    "example": {
                        "resources": [
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "title": "VA Employment Services",
                                "description": "Career counseling and job placement assistance for veterans.",
                                "categories": ["employment"],
                                "scope": "national",
                                "states": [],
                                "status": "active",
                                "organization": {
                                    "id": "550e8400-e29b-41d4-a716-446655440001",
                                    "name": "Department of Veterans Affairs",
                                },
                                "trust": {
                                    "freshness_score": 0.95,
                                    "reliability_score": 1.0,
                                    "source_tier": 1,
                                    "source_name": "VA.gov",
                                },
                            }
                        ],
                        "total": 1,
                        "limit": 20,
                        "offset": 0,
                    }
                }
            },
        }
    },
)
def list_resources(
    session: SessionDep,
    category: str | None = Query(
        default=None,
        description="Filter by category (employment, training, housing, legal)",
        examples=["housing", "employment"],
    ),
    state: str | None = Query(
        default=None,
        description="Filter by state using 2-letter code",
        examples=["VA", "TX", "CA"],
        min_length=2,
        max_length=2,
    ),
    status: ResourceStatus | None = Query(
        default=None,
        description="Filter by resource status",
    ),
    limit: int = Query(default=20, ge=1, le=500, description="Maximum results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip for pagination"),
) -> ResourceList:
    """List veteran resources with optional filtering and pagination.

    Returns resources sorted by relevance with trust scoring information.
    Use filters to narrow down results by category, state, or status.

    **Categories:**
    - `employment` - Job placement, career counseling
    - `training` - Vocational programs, certifications
    - `housing` - HUD-VASH, SSVF, shelters
    - `legal` - VA appeals, legal aid
    """
    service = ResourceService(session)
    resources, total = service.list_resources(
        category=category,
        state=state,
        status=status,
        limit=limit,
        offset=offset,
    )
    return ResourceList(resources=resources, total=total, limit=limit, offset=offset)


@router.get(
    "/{resource_id}",
    response_model=ResourceRead,
    summary="Get resource details",
    response_description="Full resource details including organization, location, and trust signals",
    responses={
        200: {
            "description": "Resource found",
        },
        404: {
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Resource not found"}
                }
            },
        },
    },
)
def get_resource(
    resource_id: UUID,
    session: SessionDep,
) -> ResourceRead:
    """Get detailed information about a specific resource.

    Returns comprehensive resource data including:
    - Basic info (title, description, eligibility, how to apply)
    - Contact details (website, phone, hours)
    - Organization information
    - Location with service area
    - Trust signals (freshness, reliability, source)
    """
    service = ResourceService(session)
    resource = service.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.post(
    "",
    response_model=ResourceRead,
    status_code=201,
    summary="Create a new resource",
    response_description="The newly created resource",
    responses={
        201: {
            "description": "Resource created successfully",
        },
        422: {
            "description": "Validation error in request body",
        },
    },
)
def create_resource(data: ResourceCreate, session: SessionDep) -> ResourceRead:
    """Create a new veteran resource.

    This endpoint is for manual resource entry. It will:
    - Create or find the associated organization by name
    - Create a location if address details are provided
    - Set initial trust scores based on manual entry tier

    **Required fields:**
    - `title` - Resource name
    - `description` - Full description of the resource
    - `organization_name` - Name of the providing organization

    **Optional but recommended:**
    - `categories` - List of categories (employment, training, housing, legal)
    - `website` - Official URL
    - `phone` - Contact phone number
    - `eligibility` - Who qualifies for this resource
    """
    service = ResourceService(session)
    return service.create_resource(data)


@router.patch(
    "/{resource_id}",
    response_model=ResourceRead,
    summary="Update a resource",
    response_description="The updated resource",
    responses={
        200: {
            "description": "Resource updated successfully",
        },
        404: {
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Resource not found"}
                }
            },
        },
        422: {
            "description": "Validation error in request body",
        },
    },
)
def update_resource(
    resource_id: UUID,
    data: ResourceUpdate,
    session: SessionDep,
) -> ResourceRead:
    """Update an existing resource with partial data.

    Only include fields you want to change. Unspecified fields remain unchanged.

    **Note:** Changes to sensitive fields may trigger review:
    - `phone` - Contact number changes
    - `website` - URL changes
    - `eligibility` - Eligibility criteria changes

    Reviewed changes won't be visible until approved by an admin.
    """
    service = ResourceService(session)
    resource = service.update_resource(resource_id, data)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.delete(
    "/{resource_id}",
    status_code=204,
    summary="Delete a resource",
    response_description="No content on successful deletion",
    responses={
        204: {
            "description": "Resource deleted (soft delete)",
        },
        404: {
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Resource not found"}
                }
            },
        },
    },
)
def delete_resource(resource_id: UUID, session: SessionDep) -> None:
    """Soft delete a resource.

    Sets the resource status to `inactive` rather than permanently deleting.
    Inactive resources are excluded from search results but can be restored.
    """
    service = ResourceService(session)
    if not service.delete_resource(resource_id):
        raise HTTPException(status_code=404, detail="Resource not found")
