"""Pydantic schemas for API request/response validation."""

from app.schemas.feedback import (
    FeedbackAdminResponse,
    FeedbackCreate,
    FeedbackListResponse,
    FeedbackResponse,
    FeedbackReviewAction,
)
from app.schemas.health import (
    DashboardStats,
    ErrorListResponse,
    ErrorRecord,
    JobRunSummary,
    SourceHealthDetail,
    SourceHealthListResponse,
)
from app.schemas.organization import OrganizationCreate, OrganizationRead
from app.schemas.partner import (
    PartnerCreate,
    PartnerRead,
    PartnerResourceCreate,
    PartnerResourceList,
    PartnerResourceRead,
    PartnerResourceUpdate,
    PartnerSubmissionRead,
    PartnerWithKey,
)
from app.schemas.resource import (
    ResourceCreate,
    ResourceList,
    ResourceRead,
    ResourceSearchResult,
    ResourceUpdate,
)
from app.schemas.review import ReviewAction, ReviewQueueItem

__all__ = [
    # Feedback schemas
    "FeedbackAdminResponse",
    "FeedbackCreate",
    "FeedbackListResponse",
    "FeedbackResponse",
    "FeedbackReviewAction",
    # Health schemas
    "DashboardStats",
    "ErrorListResponse",
    "ErrorRecord",
    "JobRunSummary",
    "SourceHealthDetail",
    "SourceHealthListResponse",
    # Partner schemas
    "PartnerCreate",
    "PartnerRead",
    "PartnerResourceCreate",
    "PartnerResourceList",
    "PartnerResourceRead",
    "PartnerResourceUpdate",
    "PartnerSubmissionRead",
    "PartnerWithKey",
    # Resource schemas
    "ResourceCreate",
    "ResourceRead",
    "ResourceUpdate",
    "ResourceList",
    "ResourceSearchResult",
    # Organization schemas
    "OrganizationCreate",
    "OrganizationRead",
    # Review schemas
    "ReviewAction",
    "ReviewQueueItem",
]
