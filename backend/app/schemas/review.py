"""Review schemas for admin API validation."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewActionType(StrEnum):
    """Review action types."""

    APPROVE = "approve"
    REJECT = "reject"


class ReviewAction(BaseModel):
    """Schema for submitting a review action."""

    action: ReviewActionType
    notes: str | None = Field(default=None, max_length=1000)
    reviewer: str = Field(..., min_length=1, max_length=100)


class ReviewQueueItem(BaseModel):
    """Item in the review queue."""

    id: UUID
    resource_id: UUID
    resource_title: str
    organization_name: str
    reason: str | None = None
    status: str
    created_at: datetime
    changes_summary: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ReviewQueueResponse(BaseModel):
    """Response for review queue endpoint."""

    items: list[ReviewQueueItem]
    total: int
    limit: int
    offset: int
