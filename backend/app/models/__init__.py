"""Database models using SQLModel."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return current UTC time (timezone-aware).

    Use this as default_factory for datetime fields instead of
    datetime.utcnow() which is deprecated in Python 3.12+.
    """
    return datetime.now(UTC)


from app.models.analytics import (
    AnalyticsDailyAggregate,
    AnalyticsEvent,
    AnalyticsEventType,
)
from app.models.feedback import Feedback, FeedbackIssueType, FeedbackStatus
from app.models.location import Location
from app.models.organization import Organization
from app.models.partner import (
    Partner,
    PartnerAPILog,
    PartnerSubmission,
    PartnerTier,
)
from app.models.program import Program, ProgramStatus, ProgramType
from app.models.resource import Resource, ResourceScope, ResourceStatus
from app.models.review import ChangeLog, ChangeType, ReviewState, ReviewStatus
from app.models.source import (
    HealthStatus,
    Source,
    SourceError,
    SourceErrorType,
    SourceRecord,
    SourceType,
)

__all__ = [
    "utc_now",
    "AnalyticsDailyAggregate",
    "AnalyticsEvent",
    "AnalyticsEventType",
    "Feedback",
    "FeedbackIssueType",
    "FeedbackStatus",
    "Organization",
    "Location",
    "Partner",
    "PartnerAPILog",
    "PartnerSubmission",
    "PartnerTier",
    "Program",
    "ProgramStatus",
    "ProgramType",
    "Resource",
    "ResourceStatus",
    "ResourceScope",
    "Source",
    "SourceError",
    "SourceErrorType",
    "SourceRecord",
    "SourceType",
    "HealthStatus",
    "ReviewState",
    "ChangeLog",
    "ReviewStatus",
    "ChangeType",
]
