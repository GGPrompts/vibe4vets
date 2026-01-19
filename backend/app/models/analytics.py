"""Analytics models for privacy-respecting usage tracking.

All analytics data is anonymous - no PII, no user identifiers, no IP addresses.
Data is aggregated to understand usage patterns without tracking individuals.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class AnalyticsEventType(str, Enum):
    """Types of analytics events we track."""

    # Search events
    SEARCH = "search"
    SEARCH_FILTER = "search_filter"

    # Resource events
    RESOURCE_VIEW = "resource_view"

    # Wizard events
    WIZARD_START = "wizard_start"
    WIZARD_STEP = "wizard_step"
    WIZARD_COMPLETE = "wizard_complete"

    # Chat events
    CHAT_START = "chat_start"
    CHAT_MESSAGE = "chat_message"

    # Page views (aggregated only)
    PAGE_VIEW = "page_view"


class AnalyticsEvent(SQLModel, table=True):
    """Anonymous analytics event.

    Captures user interactions without any personally identifiable information.
    No IP addresses, cookies, or user identifiers are stored.
    """

    __tablename__ = "analytics_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Event classification
    event_type: AnalyticsEventType
    event_name: str = Field(max_length=100)  # e.g., "search", "view_resource"

    # Anonymous context (no PII)
    category: str | None = Field(default=None, max_length=50)  # e.g., "housing"
    state: str | None = Field(default=None, max_length=2)  # e.g., "TX"
    resource_id: uuid.UUID | None = Field(default=None, index=True)

    # For search events - store query terms (already anonymized by nature)
    search_query: str | None = Field(default=None, max_length=255)

    # For wizard events
    wizard_step: int | None = None

    # Metadata
    page_path: str | None = Field(default=None, max_length=255)

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class AnalyticsDailyAggregate(SQLModel, table=True):
    """Daily aggregated analytics for dashboard display.

    Pre-computed daily summaries for fast dashboard queries.
    Updated by a background job.
    """

    __tablename__ = "analytics_daily_aggregates"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date: datetime = Field(index=True)  # Date only, no time

    # Event counts
    total_searches: int = Field(default=0)
    total_resource_views: int = Field(default=0)
    total_chat_sessions: int = Field(default=0)
    total_chat_messages: int = Field(default=0)
    wizard_starts: int = Field(default=0)
    wizard_completions: int = Field(default=0)

    # Popular categories (JSON string of category counts)
    top_categories: str | None = Field(default=None)  # JSON: {"housing": 50, "employment": 30}

    # Popular states (JSON string of state counts)
    top_states: str | None = Field(default=None)  # JSON: {"TX": 100, "CA": 80}

    # Top search queries (JSON string, anonymized by nature)
    top_searches: str | None = Field(default=None)  # JSON: {"housing": 50, "jobs": 30}

    # Most viewed resources (JSON string of resource IDs and counts)
    top_resources: str | None = Field(default=None)  # JSON: {"uuid1": 100, "uuid2": 80}

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
