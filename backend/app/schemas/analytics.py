"""Analytics schemas for API validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.analytics import AnalyticsEventType


class AnalyticsEventCreate(BaseModel):
    """Schema for creating an analytics event from the frontend."""

    event_type: AnalyticsEventType
    event_name: str = Field(..., max_length=100)
    category: str | None = Field(default=None, max_length=50)
    state: str | None = Field(default=None, max_length=2)
    resource_id: UUID | None = None
    search_query: str | None = Field(default=None, max_length=255)
    wizard_step: int | None = None
    page_path: str | None = Field(default=None, max_length=255)


class AnalyticsEventResponse(BaseModel):
    """Response for a recorded analytics event."""

    id: UUID
    event_type: AnalyticsEventType
    event_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyticsSummaryStats(BaseModel):
    """Summary statistics for the dashboard."""

    period_days: int
    total_searches: int
    total_resource_views: int
    wizard_starts: int
    wizard_completions: int
    chat_sessions: int
    chat_messages: int
    filter_usage: int


class PopularSearchItem(BaseModel):
    """A popular search query."""

    query: str
    count: int


class PopularCategoryItem(BaseModel):
    """A popular category."""

    category: str
    count: int


class PopularStateItem(BaseModel):
    """A popular state."""

    state: str
    count: int


class PopularResourceItem(BaseModel):
    """A popular resource."""

    resource_id: str
    resource_title: str | None = None
    count: int


class WizardFunnelStats(BaseModel):
    """Wizard completion funnel statistics."""

    starts: int
    completions: int
    completion_rate: float


class DailyTrendItem(BaseModel):
    """Daily trend data point."""

    date: str
    search: int | None = None
    resource_view: int | None = None
    wizard_start: int | None = None
    wizard_complete: int | None = None
    chat_start: int | None = None
    chat_message: int | None = None


class AnalyticsDashboardResponse(BaseModel):
    """Full analytics dashboard data."""

    summary: AnalyticsSummaryStats
    popular_searches: list[PopularSearchItem]
    popular_categories: list[PopularCategoryItem]
    popular_states: list[PopularStateItem]
    popular_resources: list[PopularResourceItem]
    wizard_funnel: WizardFunnelStats
    daily_trends: list[DailyTrendItem]
