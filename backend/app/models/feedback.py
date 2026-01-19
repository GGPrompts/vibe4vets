"""User feedback model for reporting outdated or incorrect resource information."""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class FeedbackIssueType(str, Enum):
    """Type of issue being reported."""

    PHONE = "phone"
    ADDRESS = "address"
    HOURS = "hours"
    WEBSITE = "website"
    CLOSED = "closed"
    ELIGIBILITY = "eligibility"
    OTHER = "other"


class FeedbackStatus(str, Enum):
    """Status of feedback in review workflow."""

    PENDING = "pending"
    REVIEWED = "reviewed"
    APPLIED = "applied"
    DISMISSED = "dismissed"


class Feedback(SQLModel, table=True):
    """Anonymous user feedback for resource corrections.

    Allows veterans/users to report when resource information is
    outdated or incorrect without requiring an account or PII.
    """

    __tablename__ = "feedback"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    resource_id: uuid.UUID = Field(foreign_key="resources.id", index=True)

    # What's wrong
    issue_type: FeedbackIssueType = Field(default=FeedbackIssueType.OTHER)
    description: str = Field(max_length=1000)

    # Optional correction info
    suggested_correction: str | None = Field(default=None, max_length=1000)
    source_of_correction: str | None = Field(
        default=None, max_length=255
    )  # e.g., "Called them", "Website says..."

    # Review workflow
    status: FeedbackStatus = Field(default=FeedbackStatus.PENDING, index=True)
    reviewer: str | None = Field(default=None, max_length=100)
    reviewed_at: datetime | None = None
    reviewer_notes: str | None = Field(default=None, max_length=1000)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
