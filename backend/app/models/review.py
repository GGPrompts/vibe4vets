"""Review and ChangeLog models using SQLModel."""

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel


def _utc_now() -> datetime:
    return datetime.now(UTC)


if TYPE_CHECKING:
    from app.models.resource import Resource


class ReviewStatus(StrEnum):
    """Review workflow status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ChangeType(StrEnum):
    """Type of change."""

    UPDATE = "update"
    RISKY_CHANGE = "risky_change"
    MANUAL_EDIT = "manual_edit"


class ReviewState(SQLModel, table=True):
    """Human review workflow."""

    __tablename__ = "review_states"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    resource_id: uuid.UUID = Field(foreign_key="resources.id")

    status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    reason: str | None = None  # Why flagged for review
    reviewer: str | None = Field(default=None, max_length=100)
    reviewed_at: datetime | None = None
    notes: str | None = None

    created_at: datetime = Field(default_factory=_utc_now)

    # Relationships
    resource: "Resource" = Relationship(back_populates="reviews")


class ChangeLog(SQLModel, table=True):
    """Field-level change history."""

    __tablename__ = "change_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    resource_id: uuid.UUID = Field(foreign_key="resources.id")

    field: str = Field(max_length=100)
    old_value: str | None = None
    new_value: str | None = None
    change_type: ChangeType = Field(default=ChangeType.UPDATE)

    timestamp: datetime = Field(default_factory=_utc_now)

    # Relationships
    resource: "Resource" = Relationship(back_populates="changes")
