"""Resource CRUD endpoints.

Provides REST API for managing Veteran resources including listing, creating,
updating, and deleting resources with filtering and pagination support.
"""

import time
from collections import defaultdict
from threading import Lock
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request

from app.api.deps import AdminAuthDep
from app.database import SessionDep
from app.models.resource import ResourceStatus
from app.schemas.resource import (
    ResourceCount,
    ResourceCreate,
    ResourceList,
    ResourceNearbyList,
    ResourceRead,
    ResourceSuggest,
    ResourceUpdate,
    SuggestResponse,
)
from app.services.resource import ResourceService

router = APIRouter()

# Rate limiting for resource suggestions
# In production, use Redis for distributed rate limiting
_suggest_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_suggest_rate_limit_lock = Lock()
SUGGEST_RATE_LIMIT_REQUESTS = 5  # requests per window
SUGGEST_RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds


def _check_suggest_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded suggestion rate limit.

    Returns True if request is allowed, False if rate limited.
    """
    now = time.time()
    with _suggest_rate_limit_lock:
        # Clean old entries
        _suggest_rate_limit_store[client_ip] = [
            ts for ts in _suggest_rate_limit_store[client_ip] if now - ts < SUGGEST_RATE_LIMIT_WINDOW
        ]
        # Check limit
        if len(_suggest_rate_limit_store[client_ip]) >= SUGGEST_RATE_LIMIT_REQUESTS:
            return False
        # Add current request
        _suggest_rate_limit_store[client_ip].append(now)
        return True


def _get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    # Check for X-Forwarded-For header (common with proxies/load balancers)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Take the first IP in the chain (original client)
        return forwarded.split(",")[0].strip()
    # Fall back to direct client IP
    return request.client.host if request.client else "unknown"


@router.get(
    "/count",
    response_model=ResourceCount,
    summary="Get resource count",
    response_description="Count of resources matching filters",
    responses={
        200: {
            "description": "Successful response with resource count",
            "content": {"application/json": {"example": {"count": 523}}},
        }
    },
)
def get_resource_count(
    session: SessionDep,
    categories: str | None = Query(
        default=None,
        description="Filter by categories (comma-separated, e.g., 'housing,legal')",
        examples=["housing,legal", "employment,training"],
    ),
    states: str | None = Query(
        default=None,
        description="Filter by states (comma-separated 2-letter codes, e.g., 'VA,MD,DC')",
        examples=["VA,MD,DC", "TX,CA"],
    ),
    scope: str | None = Query(
        default=None,
        description="Filter by resource scope: 'national', 'state', 'local', or 'all'",
        examples=["national", "state", "local"],
    ),
) -> ResourceCount:
    """Get count of resources matching filters.

    This is a lightweight endpoint for getting resource counts without returning
    full resource data. Useful for live UI updates when filters change.

    **Query Parameters:**
    - `categories` - Comma-separated category names (housing, legal, employment, training)
    - `states` - Comma-separated 2-letter state codes (VA, MD, DC)
    - `scope` - Resource scope: national, state, local, or all

    Returns count of all active resources when no filters provided.
    """
    # Parse comma-separated filters into lists
    category_list: list[str] | None = None
    if categories:
        category_list = [c.strip() for c in categories.split(",") if c.strip()]

    state_list: list[str] | None = None
    if states:
        state_list = [s.strip().upper() for s in states.split(",") if s.strip()]

    service = ResourceService(session)
    count = service.get_count(
        categories=category_list,
        states=state_list,
        scope=scope,
    )
    return ResourceCount(count=count)


@router.post(
    "/suggest",
    response_model=SuggestResponse,
    status_code=201,
    summary="Suggest a resource",
    response_description="Confirmation that the suggestion was received",
    responses={
        201: {
            "description": "Suggestion submitted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Thank you! Your suggestion has been submitted for review.",
                        "suggestion_id": "550e8400-e29b-41d4-a716-446655440000",
                    }
                }
            },
        },
        429: {
            "description": "Rate limit exceeded (5 submissions per hour)",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded. Please wait before submitting another suggestion."}
                }
            },
        },
        422: {
            "description": "Validation error in request body",
        },
    },
)
def suggest_resource(
    data: ResourceSuggest,
    request: Request,
    session: SessionDep,
) -> SuggestResponse:
    """Suggest a resource not currently in the database.

    **No account or authentication required.**

    This endpoint allows case managers, Veterans, and community members to
    suggest resources they know about. Submissions are reviewed by our team
    before being added to the directory.

    **Required fields:**
    - `name` - Name of the resource or program
    - `description` - What the resource offers (min 20 characters)
    - `category` - Primary category (employment, housing, legal, etc.)

    **Recommended fields:**
    - `website` OR `phone` - At least one way to contact the resource
    - `city` and `state` - Location helps Veterans find local resources

    **Rate limiting:**
    Limited to 5 submissions per hour per IP address to prevent spam.

    **What happens next:**
    1. Your suggestion is added to our review queue
    2. Our team verifies the information
    3. If approved, it appears in search results

    Thank you for helping Veterans find resources!
    """
    # Check rate limit
    client_ip = _get_client_ip(request)
    if not _check_suggest_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before submitting another suggestion.",
        )

    # Create the resource suggestion
    service = ResourceService(session)
    resource_id = service.create_suggestion(data)

    return SuggestResponse(
        success=True,
        message="Thank you! Your suggestion has been submitted for review.",
        suggestion_id=str(resource_id) if resource_id else None,
    )


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
                                "description": "Career counseling and job placement assistance for Veterans.",
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
        description="Filter by single category (deprecated, use 'categories' instead)",
        examples=["housing", "employment"],
    ),
    categories: str | None = Query(
        default=None,
        description="Filter by categories (comma-separated, e.g., 'housing,legal')",
        examples=["housing,legal", "employment,training"],
    ),
    state: str | None = Query(
        default=None,
        description="Filter by single state (deprecated, use 'states' instead)",
        examples=["VA", "TX", "CA"],
        min_length=2,
        max_length=2,
    ),
    states: str | None = Query(
        default=None,
        description="Filter by states (comma-separated 2-letter codes, e.g., 'VA,MD,DC')",
        examples=["VA,MD,DC", "TX,CA"],
    ),
    scope: str | None = Query(
        default=None,
        description="Filter by resource scope: 'national', 'state', 'local', or 'all'",
        examples=["national", "state", "local"],
    ),
    status: ResourceStatus | None = Query(
        default=None,
        description="Filter by resource status",
    ),
    sort: str | None = Query(
        default=None,
        description="Sort order: 'newest', 'alpha', 'shuffle', or 'relevance' (default)",
        examples=["newest", "alpha", "shuffle"],
    ),
    tags: str | None = Query(
        default=None,
        description="Filter by eligibility tags (comma-separated tag IDs, e.g., 'combat_veteran,female_veteran')",
        examples=["combat_veteran,female_veteran", "homeless,at_risk"],
    ),
    limit: int = Query(default=20, ge=1, le=500, description="Maximum results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip for pagination"),
) -> ResourceList:
    """List Veteran resources with optional filtering and pagination.

    Returns resources sorted by relevance with trust scoring information.
    Use filters to narrow down results by category, state, or status.

    **Categories:**
    - `employment` - Job placement, career counseling
    - `training` - Vocational programs, certifications
    - `housing` - HUD-VASH, SSVF, shelters
    - `legal` - VA appeals, legal aid
    """
    # Parse comma-separated filters into lists
    category_list: list[str] | None = None
    if categories:
        category_list = [c.strip() for c in categories.split(",") if c.strip()]
    elif category:
        category_list = [category]

    state_list: list[str] | None = None
    if states:
        state_list = [s.strip().upper() for s in states.split(",") if s.strip()]
    elif state:
        state_list = [state.upper()]

    tag_list: list[str] | None = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    service = ResourceService(session)
    resources, total = service.list_resources(
        categories=category_list,
        states=state_list,
        scope=scope,
        status=status,
        sort=sort,
        tags=tag_list,
        limit=limit,
        offset=offset,
    )
    return ResourceList(resources=resources, total=total, limit=limit, offset=offset)


@router.get(
    "/zip/{zip_code}",
    summary="Get ZIP code info",
    response_description="State and location for a ZIP code",
    responses={
        200: {
            "description": "ZIP code found",
            "content": {"application/json": {"example": {"zip_code": "22201", "state": "VA"}}},
        },
        404: {
            "description": "ZIP code not found",
            "content": {"application/json": {"example": {"detail": "Zip code not found"}}},
        },
    },
)
def get_zip_info(
    session: SessionDep,
    zip_code: str,
) -> dict:
    """Get state and location info for a ZIP code.

    Used by the landing page to highlight the state on the map when a ZIP is entered.
    """
    from sqlalchemy import text

    result = session.execute(
        text("SELECT state FROM zip_codes WHERE zip_code = :zip"),
        {"zip": zip_code},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Zip code not found")

    return {"zip_code": zip_code, "state": result.state}


@router.get(
    "/nearby",
    response_model=ResourceNearbyList,
    summary="Find nearby resources",
    response_description="Resources near a zip code or coordinates sorted by distance",
    responses={
        200: {
            "description": "Successful response with nearby resources",
            "content": {
                "application/json": {
                    "example": {
                        "resources": [
                            {
                                "resource": {"id": "...", "title": "Local VA Clinic"},
                                "distance_miles": 2.3,
                            }
                        ],
                        "total": 15,
                        "zip_code": "22201",
                        "radius_miles": 25,
                        "center_lat": 38.88,
                        "center_lng": -77.09,
                    }
                }
            },
        },
        400: {
            "description": "Invalid parameters",
            "content": {"application/json": {"example": {"detail": "Either zip or lat/lng must be provided"}}},
        },
        404: {
            "description": "Zip code not found",
            "content": {"application/json": {"example": {"detail": "Zip code not found"}}},
        },
    },
)
def list_nearby_resources(
    session: SessionDep,
    zip: str | None = Query(
        default=None,
        description="5-digit zip code to search near (required if lat/lng not provided)",
        min_length=5,
        max_length=5,
        examples=["22201", "90210"],
    ),
    lat: float | None = Query(
        default=None,
        description="Latitude for geolocation search (use with lng instead of zip)",
        ge=-90,
        le=90,
        examples=[38.88],
    ),
    lng: float | None = Query(
        default=None,
        description="Longitude for geolocation search (use with lat instead of zip)",
        ge=-180,
        le=180,
        examples=[-77.09],
    ),
    radius: int = Query(
        default=25,
        ge=1,
        le=100,
        description="Search radius in miles (1-100)",
    ),
    categories: str | None = Query(
        default=None,
        description="Filter by categories (comma-separated, e.g., 'housing,legal')",
        examples=["housing,legal", "employment,training"],
    ),
    scope: str | None = Query(
        default=None,
        description="Filter by scope: 'national' (only nationwide), 'state' (only local/state), or omit for all",
        examples=["national", "state"],
    ),
    tags: str | None = Query(
        default=None,
        description="Filter by eligibility tags (comma-separated tag IDs, e.g., 'combat_veteran,female_veteran')",
        examples=["combat_veteran,female_veteran", "homeless,at_risk"],
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip for pagination"),
) -> ResourceNearbyList:
    """Find Veteran resources near a location.

    Returns resources sorted by distance from the search location.
    Uses PostGIS spatial queries for efficient nearest-neighbor lookup.

    **Location Options (provide one):**
    - `zip` - 5-digit zip code
    - `lat` + `lng` - GPS coordinates (for browser geolocation)

    **Use cases:**
    - Veterans with limited transportation needing closest resources
    - Case managers finding local services for clients
    - Mobile app location-based search with GPS

    **Query Parameters:**
    - `zip` - 5-digit zip code (required if lat/lng not provided)
    - `lat` + `lng` - GPS coordinates (alternative to zip, for geolocation)
    - `radius` - Search radius in miles (default 25, max 100)
    - `categories` - Optional category filter (housing, legal, employment, training)
    - `scope` - Optional scope filter: 'national' (only nationwide programs), 'state' (only local/state)
    - `tags` - Optional eligibility tags filter (comma-separated)

    **Note:** When scope is omitted (default), returns local/state resources sorted by distance
    PLUS all national resources (which apply everywhere). National resources appear after
    distance-sorted results with distance_miles=0.
    """
    # Validate that either zip or lat/lng is provided
    if not zip and (lat is None or lng is None):
        raise HTTPException(status_code=400, detail="Either zip or both lat and lng must be provided")

    category_list: list[str] | None = None
    if categories:
        category_list = [c.strip() for c in categories.split(",") if c.strip()]

    tag_list: list[str] | None = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    service = ResourceService(session)

    # Use lat/lng if provided, otherwise use zip
    if lat is not None and lng is not None:
        result = service.list_nearby_by_coords(
            lat=lat,
            lng=lng,
            radius_miles=radius,
            categories=category_list,
            scope=scope,
            tags=tag_list,
            limit=limit,
            offset=offset,
        )
    else:
        result = service.list_nearby(
            zip_code=zip,  # type: ignore  # We validated zip exists above
            radius_miles=radius,
            categories=category_list,
            scope=scope,
            tags=tag_list,
            limit=limit,
            offset=offset,
        )

    if result is None:
        raise HTTPException(status_code=404, detail="Zip code not found")

    return result


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
            "content": {"application/json": {"example": {"detail": "Resource not found"}}},
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
def create_resource(data: ResourceCreate, session: SessionDep, _auth: AdminAuthDep) -> ResourceRead:
    """Create a new Veteran resource.

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
            "content": {"application/json": {"example": {"detail": "Resource not found"}}},
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
    _auth: AdminAuthDep,
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
            "content": {"application/json": {"example": {"detail": "Resource not found"}}},
        },
    },
)
def delete_resource(resource_id: UUID, session: SessionDep, _auth: AdminAuthDep) -> None:
    """Soft delete a resource.

    Sets the resource status to `inactive` rather than permanently deleting.
    Inactive resources are excluded from search results but can be restored.
    """
    service = ResourceService(session)
    if not service.delete_resource(resource_id):
        raise HTTPException(status_code=404, detail="Resource not found")
