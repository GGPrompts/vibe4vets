"""Feedback endpoints for anonymous user-reported resource corrections.

Allows users to report outdated or incorrect resource information without
requiring an account. Feedback is reviewed by admins and applied to improve
data quality.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from app.api.deps import AdminAuthDep
from app.database import SessionDep
from app.models import Feedback, FeedbackStatus, Resource
from app.schemas.feedback import (
    FeedbackAdminResponse,
    FeedbackCreate,
    FeedbackListResponse,
    FeedbackResponse,
    FeedbackReviewAction,
)

router = APIRouter()


# ============================================================================
# Public Endpoints (no auth required)
# ============================================================================


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=201,
    summary="Submit feedback",
    response_description="The submitted feedback with tracking ID",
    responses={
        201: {
            "description": "Feedback submitted successfully",
        },
        404: {
            "description": "Resource not found",
            "content": {"application/json": {"example": {"detail": "Resource not found"}}},
        },
        422: {
            "description": "Invalid feedback data",
        },
    },
)
def submit_feedback(
    feedback_data: FeedbackCreate,
    session: SessionDep,
) -> Feedback:
    """Submit anonymous feedback about a resource.

    Report outdated phone numbers, closed programs, or incorrect information.
    **No account or personal information required.**

    **Issue types:**
    - `phone_wrong` - Phone number is incorrect or disconnected
    - `website_wrong` - Website URL is broken or incorrect
    - `address_wrong` - Address has changed
    - `program_closed` - Program is no longer available
    - `eligibility_changed` - Eligibility requirements have changed
    - `other` - Other corrections or updates

    **Tips for helpful feedback:**
    - Include the source of your correction if available
    - Be specific about what's wrong and what the correct info is
    """
    # Verify resource exists
    resource = session.get(Resource, feedback_data.resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Create feedback
    feedback = Feedback(
        resource_id=feedback_data.resource_id,
        issue_type=feedback_data.issue_type,
        description=feedback_data.description,
        suggested_correction=feedback_data.suggested_correction,
        source_of_correction=feedback_data.source_of_correction,
    )

    session.add(feedback)
    session.commit()
    session.refresh(feedback)

    return feedback


# ============================================================================
# Admin Endpoints
# ============================================================================


@router.get("/admin", response_model=FeedbackListResponse)
def list_feedback(
    _auth: AdminAuthDep,
    session: SessionDep,
    status: FeedbackStatus | None = Query(default=None, description="Filter by status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> FeedbackListResponse:
    """List feedback items for admin review.

    Returns feedback with resource context for the admin dashboard.
    Optionally filter by status (pending, reviewed, applied, dismissed).
    """
    # Build query with joins
    query = (
        select(Feedback, Resource)
        .join(Resource, Feedback.resource_id == Resource.id)
        .order_by(Feedback.created_at.desc())
    )

    if status:
        query = query.where(Feedback.status == status)

    # Get total count
    from sqlmodel import func

    count_query = select(func.count(Feedback.id))
    if status:
        count_query = count_query.where(Feedback.status == status)
    total = session.exec(count_query).one()

    # Apply pagination
    query = query.offset(offset).limit(limit)
    results = session.exec(query).all()

    # Build response items
    items = []
    for feedback, resource in results:
        org_name = resource.organization.name if resource.organization else "Unknown"
        items.append(
            FeedbackAdminResponse(
                id=feedback.id,
                resource_id=feedback.resource_id,
                resource_title=resource.title,
                organization_name=org_name,
                issue_type=feedback.issue_type,
                description=feedback.description,
                suggested_correction=feedback.suggested_correction,
                source_of_correction=feedback.source_of_correction,
                status=feedback.status,
                reviewer=feedback.reviewer,
                reviewed_at=feedback.reviewed_at,
                reviewer_notes=feedback.reviewer_notes,
                created_at=feedback.created_at,
            )
        )

    return FeedbackListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/admin/{feedback_id}", response_model=FeedbackAdminResponse)
def get_feedback(
    feedback_id: UUID,
    _auth: AdminAuthDep,
    session: SessionDep,
) -> FeedbackAdminResponse:
    """Get a single feedback item with resource context."""
    result = session.exec(
        select(Feedback, Resource).join(Resource, Feedback.resource_id == Resource.id).where(Feedback.id == feedback_id)
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Feedback not found")

    feedback, resource = result

    org_name = resource.organization.name if resource.organization else "Unknown"
    return FeedbackAdminResponse(
        id=feedback.id,
        resource_id=feedback.resource_id,
        resource_title=resource.title,
        organization_name=org_name,
        issue_type=feedback.issue_type,
        description=feedback.description,
        suggested_correction=feedback.suggested_correction,
        source_of_correction=feedback.source_of_correction,
        status=feedback.status,
        reviewer=feedback.reviewer,
        reviewed_at=feedback.reviewed_at,
        reviewer_notes=feedback.reviewer_notes,
        created_at=feedback.created_at,
    )


@router.patch("/admin/{feedback_id}", response_model=FeedbackAdminResponse)
def review_feedback(
    feedback_id: UUID,
    action: FeedbackReviewAction,
    _auth: AdminAuthDep,
    session: SessionDep,
) -> FeedbackAdminResponse:
    """Review and update feedback status.

    Allows admins to mark feedback as:
    - reviewed: Acknowledged but no action taken
    - applied: Correction was applied to the resource
    - dismissed: Feedback was incorrect or spam
    """
    result = session.exec(
        select(Feedback, Resource).join(Resource, Feedback.resource_id == Resource.id).where(Feedback.id == feedback_id)
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Feedback not found")

    feedback, resource = result

    # Update feedback
    feedback.status = action.status
    feedback.reviewer = action.reviewer
    feedback.reviewed_at = datetime.utcnow()
    feedback.reviewer_notes = action.reviewer_notes

    session.add(feedback)
    session.commit()
    session.refresh(feedback)

    org_name = resource.organization.name if resource.organization else "Unknown"
    return FeedbackAdminResponse(
        id=feedback.id,
        resource_id=feedback.resource_id,
        resource_title=resource.title,
        organization_name=org_name,
        issue_type=feedback.issue_type,
        description=feedback.description,
        suggested_correction=feedback.suggested_correction,
        source_of_correction=feedback.source_of_correction,
        status=feedback.status,
        reviewer=feedback.reviewer,
        reviewed_at=feedback.reviewed_at,
        reviewer_notes=feedback.reviewer_notes,
        created_at=feedback.created_at,
    )


@router.get("/admin/stats/summary")
def get_feedback_stats(_auth: AdminAuthDep, session: SessionDep) -> dict:
    """Get summary statistics for feedback.

    Returns counts by status for the admin dashboard.
    """
    from sqlmodel import func

    # Count by status
    stats_query = select(Feedback.status, func.count(Feedback.id)).group_by(Feedback.status)
    results = session.exec(stats_query).all()

    status_counts = {status.value: count for status, count in results}

    return {
        "pending": status_counts.get("pending", 0),
        "reviewed": status_counts.get("reviewed", 0),
        "applied": status_counts.get("applied", 0),
        "dismissed": status_counts.get("dismissed", 0),
        "total": sum(status_counts.values()),
    }
