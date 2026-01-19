"""Feedback schemas for API validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.feedback import FeedbackIssueType, FeedbackStatus


class FeedbackCreate(BaseModel):
    """Schema for submitting anonymous feedback about a resource."""

    resource_id: UUID
    issue_type: FeedbackIssueType = Field(default=FeedbackIssueType.OTHER)
    description: str = Field(..., min_length=10, max_length=1000)
    suggested_correction: str | None = Field(default=None, max_length=1000)
    source_of_correction: str | None = Field(default=None, max_length=255)


class FeedbackResponse(BaseModel):
    """Response for a single feedback item."""

    id: UUID
    resource_id: UUID
    issue_type: FeedbackIssueType
    description: str
    suggested_correction: str | None
    source_of_correction: str | None
    status: FeedbackStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackAdminResponse(BaseModel):
    """Response for admin view of feedback with additional context."""

    id: UUID
    resource_id: UUID
    resource_title: str
    organization_name: str
    issue_type: FeedbackIssueType
    description: str
    suggested_correction: str | None
    source_of_correction: str | None
    status: FeedbackStatus
    reviewer: str | None
    reviewed_at: datetime | None
    reviewer_notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackReviewAction(BaseModel):
    """Schema for admin reviewing feedback."""

    status: FeedbackStatus
    reviewer: str = Field(..., min_length=1, max_length=100)
    reviewer_notes: str | None = Field(default=None, max_length=1000)


class FeedbackListResponse(BaseModel):
    """Response for list of feedback items."""

    items: list[FeedbackAdminResponse]
    total: int
    limit: int
    offset: int
