"""Review and ChangeLog models."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReviewStatus(str, Enum):
    """Review workflow status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ChangeType(str, Enum):
    """Type of change."""

    UPDATE = "update"
    RISKY_CHANGE = "risky_change"
    MANUAL_EDIT = "manual_edit"


class ReviewState(Base):
    """Human review workflow."""

    __tablename__ = "review_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False
    )

    status: Mapped[str] = mapped_column(String(20), default=ReviewStatus.PENDING.value)
    reason: Mapped[str | None] = mapped_column(Text)  # Why flagged for review
    reviewer: Mapped[str | None] = mapped_column(String(100))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    resource = relationship("Resource", back_populates="reviews")


class ChangeLog(Base):
    """Field-level change history."""

    __tablename__ = "change_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False
    )

    field: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    change_type: Mapped[str] = mapped_column(String(20), default=ChangeType.UPDATE.value)

    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    resource = relationship("Resource", back_populates="changes")
