"""Partner API endpoints for resource submissions.

Allows trusted partners (VSOs, nonprofits) to submit and manage resources
through API key authentication. Submissions go through human review.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlmodel import Session, col, select

from app.database import get_session
from app.models import Location, Organization, Resource
from app.models.partner import Partner, PartnerAPILog, PartnerSubmission
from app.models.resource import ResourceStatus
from app.models.review import ReviewState, ReviewStatus
from app.schemas.partner import (
    PartnerResourceCreate,
    PartnerResourceList,
    PartnerResourceRead,
    PartnerResourceUpdate,
)

router = APIRouter()

# Rate limit: requests per hour
RATE_LIMIT_WINDOW = timedelta(hours=1)


class PartnerAuth:
    """Dependency for partner API key authentication with rate limiting."""

    def __init__(self, log_request: bool = True) -> None:
        self.log_request = log_request

    def __call__(
        self,
        request: Request,
        x_api_key: Annotated[str | None, Header()] = None,
        session: Session = Depends(get_session),
    ) -> tuple[Partner, Session]:
        """Validate API key and check rate limits."""
        if not x_api_key:
            raise HTTPException(
                status_code=401,
                detail="Missing API key. Include X-API-Key header.",
            )

        # Look up partner by API key hash
        api_key_hash = Partner.hash_api_key(x_api_key)
        stmt = select(Partner).where(Partner.api_key_hash == api_key_hash)
        partner = session.exec(stmt).first()

        if not partner:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key.",
            )

        if not partner.is_active:
            raise HTTPException(
                status_code=403,
                detail="Partner account is inactive. Contact support.",
            )

        # Check rate limiting
        now = datetime.now(UTC)
        if partner.rate_limit_reset_at is None or now >= partner.rate_limit_reset_at:
            # Reset the rate limit window
            partner.rate_limit_count = 0
            partner.rate_limit_reset_at = now + RATE_LIMIT_WINDOW

        if partner.rate_limit_count >= partner.rate_limit:
            reset_in = (partner.rate_limit_reset_at - now).seconds
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Resets in {reset_in} seconds.",
                headers={"Retry-After": str(reset_in)},
            )

        # Increment rate limit counter
        partner.rate_limit_count += 1
        session.add(partner)
        session.commit()

        # Store request info for audit logging after response
        if self.log_request:
            request.state.partner_id = partner.id
            request.state.endpoint = request.url.path
            request.state.method = request.method

        return partner, session


# Reusable dependency
PartnerAuthDep = Annotated[tuple[Partner, Session], Depends(PartnerAuth())]


def log_api_call(
    session: Session,
    partner_id: UUID,
    endpoint: str,
    method: str,
    status_code: int,
    request_summary: str | None = None,
) -> None:
    """Log a partner API call for audit purposes."""
    log = PartnerAPILog(
        partner_id=partner_id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        request_summary=request_summary,
    )
    session.add(log)
    session.commit()


@router.post(
    "/resources",
    response_model=PartnerResourceRead,
    status_code=201,
    summary="Submit a new resource",
    responses={
        201: {"description": "Resource submitted for review"},
        401: {"description": "Invalid or missing API key"},
        403: {"description": "Partner account inactive"},
        429: {"description": "Rate limit exceeded"},
    },
)
def submit_resource(
    data: PartnerResourceCreate,
    auth: PartnerAuthDep,
) -> PartnerResourceRead:
    """Submit a new resource for review.

    Resources submitted via the partner API go through human review before
    becoming active. The partner's trust tier determines the resource's
    initial reliability score.

    **Required fields:**
    - `title` - Resource name
    - `description` - Full description
    - `organization_name` - Name of the providing organization

    **Response:**
    Returns the created resource with `status: needs_review`.
    """
    partner, session = auth

    # Find or create organization
    org_query = select(Organization).where(Organization.name == data.organization_name)
    organization = session.exec(org_query).first()

    if not organization:
        organization = Organization(
            name=data.organization_name,
            website=str(data.website) if data.website else None,
        )
        session.add(organization)
        session.flush()

    # Create location if address provided
    location = None
    if data.address and data.city and data.state and data.zip_code:
        location = Location(
            organization_id=organization.id,
            address=data.address,
            city=data.city,
            state=data.state,
            zip_code=data.zip_code,
        )
        session.add(location)
        session.flush()

    # Create resource with NEEDS_REVIEW status
    # Reliability score based on partner tier (tier 2=0.8, 3=0.6, 4=0.4)
    reliability_map = {2: 0.8, 3: 0.6, 4: 0.4}
    reliability_score = reliability_map.get(partner.tier.value, 0.4)

    resource = Resource(
        organization_id=organization.id,
        location_id=location.id if location else None,
        title=data.title,
        description=data.description,
        summary=data.summary,
        eligibility=data.eligibility,
        how_to_apply=data.how_to_apply,
        categories=data.categories,
        subcategories=data.subcategories,
        tags=data.tags,
        scope=data.scope,
        states=data.states,
        website=str(data.website) if data.website else None,
        phone=data.phone,
        hours=data.hours,
        languages=data.languages,
        cost=data.cost,
        status=ResourceStatus.NEEDS_REVIEW,
        freshness_score=1.0,
        reliability_score=reliability_score,
    )
    session.add(resource)
    session.flush()

    # Create review state
    review = ReviewState(
        resource_id=resource.id,
        status=ReviewStatus.PENDING,
        reason=f"Partner submission from {partner.name}",
    )
    session.add(review)

    # Track partner submission
    submission = PartnerSubmission(
        partner_id=partner.id,
        resource_id=resource.id,
    )
    session.add(submission)

    session.commit()
    session.refresh(resource)

    # Log the API call
    log_api_call(
        session,
        partner.id,
        "/api/v1/partner/resources",
        "POST",
        201,
        f"Created resource: {resource.title}",
    )

    return PartnerResourceRead(
        id=resource.id,
        title=resource.title,
        description=resource.description,
        summary=resource.summary,
        eligibility=resource.eligibility,
        how_to_apply=resource.how_to_apply,
        categories=resource.categories,
        subcategories=resource.subcategories,
        tags=resource.tags,
        scope=resource.scope,
        states=resource.states,
        website=resource.website,
        phone=resource.phone,
        hours=resource.hours,
        languages=resource.languages,
        cost=resource.cost,
        status=resource.status.value,
        submitted_at=submission.submitted_at,
        updated_at=None,
    )


@router.put(
    "/resources/{resource_id}",
    response_model=PartnerResourceRead,
    summary="Update a submitted resource",
    responses={
        200: {"description": "Resource updated and re-submitted for review"},
        401: {"description": "Invalid or missing API key"},
        403: {"description": "Not authorized to update this resource"},
        404: {"description": "Resource not found"},
        429: {"description": "Rate limit exceeded"},
    },
)
def update_resource(
    resource_id: UUID,
    data: PartnerResourceUpdate,
    auth: PartnerAuthDep,
) -> PartnerResourceRead:
    """Update a resource that was previously submitted by this partner.

    Partners can only update resources they originally submitted.
    Updates trigger re-review before becoming active.

    Only include fields you want to change.
    """
    partner, session = auth

    # Check partner owns this submission
    stmt = select(PartnerSubmission).where(
        PartnerSubmission.partner_id == partner.id,
        PartnerSubmission.resource_id == resource_id,
    )
    submission = session.exec(stmt).first()

    if not submission:
        log_api_call(
            session,
            partner.id,
            f"/api/v1/partner/resources/{resource_id}",
            "PUT",
            403,
            "Attempted to update resource not owned by partner",
        )
        raise HTTPException(
            status_code=403,
            detail="You can only update resources you submitted.",
        )

    resource = session.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Update fields that are provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "website" and value is not None:
            value = str(value)
        setattr(resource, field, value)

    # Reset to needs_review status
    resource.status = ResourceStatus.NEEDS_REVIEW
    resource.updated_at = datetime.now(UTC)
    session.add(resource)

    # Create or update review state
    review_stmt = (
        select(ReviewState)
        .where(ReviewState.resource_id == resource_id)
        .where(ReviewState.status == ReviewStatus.PENDING)
    )
    existing_review = session.exec(review_stmt).first()

    if existing_review:
        existing_review.reason = f"{existing_review.reason}; Updated by partner {partner.name}"
        session.add(existing_review)
    else:
        review = ReviewState(
            resource_id=resource.id,
            status=ReviewStatus.PENDING,
            reason=f"Partner update from {partner.name}",
        )
        session.add(review)

    # Update submission tracking
    submission.updated_at = datetime.now(UTC)
    session.add(submission)

    session.commit()
    session.refresh(resource)
    session.refresh(submission)

    # Log the API call
    log_api_call(
        session,
        partner.id,
        f"/api/v1/partner/resources/{resource_id}",
        "PUT",
        200,
        f"Updated resource: {resource.title}",
    )

    return PartnerResourceRead(
        id=resource.id,
        title=resource.title,
        description=resource.description,
        summary=resource.summary,
        eligibility=resource.eligibility,
        how_to_apply=resource.how_to_apply,
        categories=resource.categories,
        subcategories=resource.subcategories,
        tags=resource.tags,
        scope=resource.scope,
        states=resource.states,
        website=resource.website,
        phone=resource.phone,
        hours=resource.hours,
        languages=resource.languages,
        cost=resource.cost,
        status=resource.status.value,
        submitted_at=submission.submitted_at,
        updated_at=submission.updated_at,
    )


@router.get(
    "/resources",
    response_model=PartnerResourceList,
    summary="List your submitted resources",
    responses={
        200: {"description": "List of resources submitted by this partner"},
        401: {"description": "Invalid or missing API key"},
        429: {"description": "Rate limit exceeded"},
    },
)
def list_resources(
    auth: PartnerAuthDep,
    status: str | None = Query(
        default=None,
        description="Filter by status: needs_review, active, inactive",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PartnerResourceList:
    """List resources submitted by this partner.

    Returns all resources this partner has submitted, including their
    current review status.

    **Query Parameters:**
    - `status` - Filter by status (needs_review, active, inactive)
    - `limit` - Maximum results (default 20, max 100)
    - `offset` - Pagination offset
    """
    partner, session = auth

    # Get submissions for this partner
    stmt = (
        select(PartnerSubmission)
        .where(PartnerSubmission.partner_id == partner.id)
        .order_by(col(PartnerSubmission.submitted_at).desc())
    )

    submissions = session.exec(stmt).all()

    # Build response with resource details
    resources = []
    for submission in submissions:
        resource = session.get(Resource, submission.resource_id)
        if not resource:
            continue

        # Apply status filter
        if status and resource.status.value != status:
            continue

        resources.append(
            PartnerResourceRead(
                id=resource.id,
                title=resource.title,
                description=resource.description,
                summary=resource.summary,
                eligibility=resource.eligibility,
                how_to_apply=resource.how_to_apply,
                categories=resource.categories,
                subcategories=resource.subcategories,
                tags=resource.tags,
                scope=resource.scope,
                states=resource.states,
                website=resource.website,
                phone=resource.phone,
                hours=resource.hours,
                languages=resource.languages,
                cost=resource.cost,
                status=resource.status.value,
                submitted_at=submission.submitted_at,
                updated_at=submission.updated_at,
            )
        )

    # Apply pagination
    total = len(resources)
    paginated = resources[offset : offset + limit]

    # Log the API call
    log_api_call(
        session,
        partner.id,
        "/api/v1/partner/resources",
        "GET",
        200,
        f"Listed {len(paginated)} resources",
    )

    return PartnerResourceList(
        resources=paginated,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/resources/{resource_id}",
    response_model=PartnerResourceRead,
    summary="Get a submitted resource",
    responses={
        200: {"description": "Resource details"},
        401: {"description": "Invalid or missing API key"},
        403: {"description": "Not authorized to view this resource"},
        404: {"description": "Resource not found"},
        429: {"description": "Rate limit exceeded"},
    },
)
def get_resource(
    resource_id: UUID,
    auth: PartnerAuthDep,
) -> PartnerResourceRead:
    """Get details of a specific resource submitted by this partner."""
    partner, session = auth

    # Check partner owns this submission
    stmt = select(PartnerSubmission).where(
        PartnerSubmission.partner_id == partner.id,
        PartnerSubmission.resource_id == resource_id,
    )
    submission = session.exec(stmt).first()

    if not submission:
        raise HTTPException(
            status_code=403,
            detail="You can only view resources you submitted.",
        )

    resource = session.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    return PartnerResourceRead(
        id=resource.id,
        title=resource.title,
        description=resource.description,
        summary=resource.summary,
        eligibility=resource.eligibility,
        how_to_apply=resource.how_to_apply,
        categories=resource.categories,
        subcategories=resource.subcategories,
        tags=resource.tags,
        scope=resource.scope,
        states=resource.states,
        website=resource.website,
        phone=resource.phone,
        hours=resource.hours,
        languages=resource.languages,
        cost=resource.cost,
        status=resource.status.value,
        submitted_at=submission.submitted_at,
        updated_at=submission.updated_at,
    )
