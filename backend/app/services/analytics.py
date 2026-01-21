"""Analytics service for privacy-respecting usage tracking.

All data is anonymous - no PII, no user identifiers, no IP addresses.
This service provides methods to record events and query aggregated statistics.
"""

import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlmodel import Session, func, select

from app.models.analytics import (
    AnalyticsDailyAggregate,
    AnalyticsEvent,
    AnalyticsEventType,
)


class AnalyticsService:
    """Service for recording and querying anonymous analytics."""

    def __init__(self, session: Session):
        self.session = session

    # =========================================================================
    # Event Recording
    # =========================================================================

    def track_search(
        self,
        query: str,
        category: str | None = None,
        state: str | None = None,
        page_path: str | None = None,
    ) -> AnalyticsEvent:
        """Track a search event (anonymized query)."""
        event = AnalyticsEvent(
            event_type=AnalyticsEventType.SEARCH,
            event_name="search",
            search_query=query[:255] if query else None,
            category=category,
            state=state[:2] if state else None,
            page_path=page_path,
        )
        self.session.add(event)
        self.session.commit()
        return event

    def track_filter_usage(
        self,
        category: str | None = None,
        state: str | None = None,
        page_path: str | None = None,
    ) -> AnalyticsEvent:
        """Track filter usage (category/state selection)."""
        event = AnalyticsEvent(
            event_type=AnalyticsEventType.SEARCH_FILTER,
            event_name="filter",
            category=category,
            state=state[:2] if state else None,
            page_path=page_path,
        )
        self.session.add(event)
        self.session.commit()
        return event

    def track_resource_view(
        self,
        resource_id: uuid.UUID,
        category: str | None = None,
        state: str | None = None,
    ) -> AnalyticsEvent:
        """Track a resource view."""
        event = AnalyticsEvent(
            event_type=AnalyticsEventType.RESOURCE_VIEW,
            event_name="resource_view",
            resource_id=resource_id,
            category=category,
            state=state[:2] if state else None,
            page_path=f"/resources/{resource_id}",
        )
        self.session.add(event)
        self.session.commit()
        return event

    def track_wizard_event(
        self,
        event_name: str,
        step: int | None = None,
    ) -> AnalyticsEvent:
        """Track wizard progress (start, step, complete)."""
        if event_name == "start":
            event_type = AnalyticsEventType.WIZARD_START
        elif event_name == "complete":
            event_type = AnalyticsEventType.WIZARD_COMPLETE
        else:
            event_type = AnalyticsEventType.WIZARD_STEP

        event = AnalyticsEvent(
            event_type=event_type,
            event_name=f"wizard_{event_name}",
            wizard_step=step,
            page_path="/search",
        )
        self.session.add(event)
        self.session.commit()
        return event

    def track_chat_event(
        self,
        event_name: str,
    ) -> AnalyticsEvent:
        """Track chat usage (session start or message sent)."""
        if event_name == "start":
            event_type = AnalyticsEventType.CHAT_START
        else:
            event_type = AnalyticsEventType.CHAT_MESSAGE

        event = AnalyticsEvent(
            event_type=event_type,
            event_name=f"chat_{event_name}",
            page_path="/chat",
        )
        self.session.add(event)
        self.session.commit()
        return event

    def track_page_view(
        self,
        page_path: str,
        category: str | None = None,
        state: str | None = None,
    ) -> AnalyticsEvent:
        """Track a page view."""
        event = AnalyticsEvent(
            event_type=AnalyticsEventType.PAGE_VIEW,
            event_name="page_view",
            page_path=page_path,
            category=category,
            state=state[:2] if state else None,
        )
        self.session.add(event)
        self.session.commit()
        return event

    # =========================================================================
    # Statistics Queries
    # =========================================================================

    def get_summary_stats(self, days: int = 30) -> dict[str, Any]:
        """Get summary statistics for the dashboard."""
        since = datetime.now(UTC) - timedelta(days=days)

        # Count by event type
        counts = self.session.exec(
            select(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id))
            .where(AnalyticsEvent.created_at >= since)
            .group_by(AnalyticsEvent.event_type)
        ).all()

        count_dict = {str(event_type): count for event_type, count in counts}

        return {
            "period_days": days,
            "total_searches": count_dict.get("search", 0),
            "total_resource_views": count_dict.get("resource_view", 0),
            "wizard_starts": count_dict.get("wizard_start", 0),
            "wizard_completions": count_dict.get("wizard_complete", 0),
            "chat_sessions": count_dict.get("chat_start", 0),
            "chat_messages": count_dict.get("chat_message", 0),
            "filter_usage": count_dict.get("search_filter", 0),
        }

    def get_popular_searches(self, days: int = 30, limit: int = 10) -> list[dict]:
        """Get most popular search queries."""
        since = datetime.now(UTC) - timedelta(days=days)

        results = self.session.exec(
            select(AnalyticsEvent.search_query, func.count(AnalyticsEvent.id).label("count"))
            .where(
                AnalyticsEvent.event_type == AnalyticsEventType.SEARCH,
                AnalyticsEvent.created_at >= since,
                AnalyticsEvent.search_query.isnot(None),
            )
            .group_by(AnalyticsEvent.search_query)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(limit)
        ).all()

        return [{"query": query, "count": count} for query, count in results]

    def get_popular_categories(self, days: int = 30, limit: int = 10) -> list[dict]:
        """Get most used categories."""
        since = datetime.now(UTC) - timedelta(days=days)

        results = self.session.exec(
            select(AnalyticsEvent.category, func.count(AnalyticsEvent.id).label("count"))
            .where(
                AnalyticsEvent.created_at >= since,
                AnalyticsEvent.category.isnot(None),
            )
            .group_by(AnalyticsEvent.category)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(limit)
        ).all()

        return [{"category": category, "count": count} for category, count in results]

    def get_popular_states(self, days: int = 30, limit: int = 10) -> list[dict]:
        """Get most searched states."""
        since = datetime.now(UTC) - timedelta(days=days)

        results = self.session.exec(
            select(AnalyticsEvent.state, func.count(AnalyticsEvent.id).label("count"))
            .where(
                AnalyticsEvent.created_at >= since,
                AnalyticsEvent.state.isnot(None),
            )
            .group_by(AnalyticsEvent.state)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(limit)
        ).all()

        return [{"state": state, "count": count} for state, count in results]

    def get_most_viewed_resources(self, days: int = 30, limit: int = 10) -> list[dict]:
        """Get most viewed resources."""
        since = datetime.now(UTC) - timedelta(days=days)

        results = self.session.exec(
            select(AnalyticsEvent.resource_id, func.count(AnalyticsEvent.id).label("count"))
            .where(
                AnalyticsEvent.event_type == AnalyticsEventType.RESOURCE_VIEW,
                AnalyticsEvent.created_at >= since,
                AnalyticsEvent.resource_id.isnot(None),
            )
            .group_by(AnalyticsEvent.resource_id)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(limit)
        ).all()

        return [{"resource_id": str(resource_id), "count": count} for resource_id, count in results]

    def get_wizard_funnel(self, days: int = 30) -> dict[str, int]:
        """Get wizard completion funnel."""
        since = datetime.now(UTC) - timedelta(days=days)

        # Count starts and completions
        starts = self.session.exec(
            select(func.count(AnalyticsEvent.id)).where(
                AnalyticsEvent.event_type == AnalyticsEventType.WIZARD_START,
                AnalyticsEvent.created_at >= since,
            )
        ).one()

        completions = self.session.exec(
            select(func.count(AnalyticsEvent.id)).where(
                AnalyticsEvent.event_type == AnalyticsEventType.WIZARD_COMPLETE,
                AnalyticsEvent.created_at >= since,
            )
        ).one()

        # Get step distribution
        step_counts = self.session.exec(
            select(AnalyticsEvent.wizard_step, func.count(AnalyticsEvent.id))
            .where(
                AnalyticsEvent.event_type == AnalyticsEventType.WIZARD_STEP,
                AnalyticsEvent.created_at >= since,
                AnalyticsEvent.wizard_step.isnot(None),
            )
            .group_by(AnalyticsEvent.wizard_step)
            .order_by(AnalyticsEvent.wizard_step)
        ).all()

        steps = {f"step_{step}": count for step, count in step_counts}

        return {
            "starts": starts,
            "completions": completions,
            "completion_rate": round(completions / starts * 100, 1) if starts > 0 else 0,
            **steps,
        }

    def get_daily_trends(self, days: int = 30) -> list[dict]:
        """Get daily event counts for trend chart."""
        since = datetime.now(UTC) - timedelta(days=days)

        # Use a column reference for date_trunc to avoid GROUP BY issues
        date_col = func.date_trunc("day", AnalyticsEvent.created_at)

        results = self.session.exec(
            select(
                date_col.label("date"),
                AnalyticsEvent.event_type,
                func.count(AnalyticsEvent.id).label("count"),
            )
            .where(AnalyticsEvent.created_at >= since)
            .group_by(
                date_col,
                AnalyticsEvent.event_type,
            )
            .order_by(date_col)
        ).all()

        # Group by date
        trends: dict[str, dict] = {}
        for date, event_type, count in results:
            date_str = date.strftime("%Y-%m-%d")
            if date_str not in trends:
                trends[date_str] = {"date": date_str}
            trends[date_str][str(event_type)] = count

        return list(trends.values())

    # =========================================================================
    # Aggregation (for background job)
    # =========================================================================

    def compute_daily_aggregate(self, date: datetime) -> AnalyticsDailyAggregate:
        """Compute and store daily aggregate for a specific date."""
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        # Count by event type for this day
        counts = self.session.exec(
            select(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id))
            .where(
                AnalyticsEvent.created_at >= start,
                AnalyticsEvent.created_at < end,
            )
            .group_by(AnalyticsEvent.event_type)
        ).all()

        count_dict = {str(event_type): count for event_type, count in counts}

        # Top categories
        top_cats = self.session.exec(
            select(AnalyticsEvent.category, func.count(AnalyticsEvent.id))
            .where(
                AnalyticsEvent.created_at >= start,
                AnalyticsEvent.created_at < end,
                AnalyticsEvent.category.isnot(None),
            )
            .group_by(AnalyticsEvent.category)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(10)
        ).all()

        # Top states
        top_states = self.session.exec(
            select(AnalyticsEvent.state, func.count(AnalyticsEvent.id))
            .where(
                AnalyticsEvent.created_at >= start,
                AnalyticsEvent.created_at < end,
                AnalyticsEvent.state.isnot(None),
            )
            .group_by(AnalyticsEvent.state)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(10)
        ).all()

        # Top searches
        top_searches = self.session.exec(
            select(AnalyticsEvent.search_query, func.count(AnalyticsEvent.id))
            .where(
                AnalyticsEvent.event_type == AnalyticsEventType.SEARCH,
                AnalyticsEvent.created_at >= start,
                AnalyticsEvent.created_at < end,
                AnalyticsEvent.search_query.isnot(None),
            )
            .group_by(AnalyticsEvent.search_query)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(10)
        ).all()

        # Top resources
        top_resources = self.session.exec(
            select(AnalyticsEvent.resource_id, func.count(AnalyticsEvent.id))
            .where(
                AnalyticsEvent.event_type == AnalyticsEventType.RESOURCE_VIEW,
                AnalyticsEvent.created_at >= start,
                AnalyticsEvent.created_at < end,
                AnalyticsEvent.resource_id.isnot(None),
            )
            .group_by(AnalyticsEvent.resource_id)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(10)
        ).all()

        # Check if aggregate exists
        existing = self.session.exec(
            select(AnalyticsDailyAggregate).where(AnalyticsDailyAggregate.date == start)
        ).first()

        if existing:
            aggregate = existing
        else:
            aggregate = AnalyticsDailyAggregate(date=start)

        aggregate.total_searches = count_dict.get("search", 0)
        aggregate.total_resource_views = count_dict.get("resource_view", 0)
        aggregate.total_chat_sessions = count_dict.get("chat_start", 0)
        aggregate.total_chat_messages = count_dict.get("chat_message", 0)
        aggregate.wizard_starts = count_dict.get("wizard_start", 0)
        aggregate.wizard_completions = count_dict.get("wizard_complete", 0)
        aggregate.top_categories = json.dumps({cat: cnt for cat, cnt in top_cats})
        aggregate.top_states = json.dumps({st: cnt for st, cnt in top_states})
        aggregate.top_searches = json.dumps({q: cnt for q, cnt in top_searches})
        aggregate.top_resources = json.dumps({str(rid): cnt for rid, cnt in top_resources})
        aggregate.updated_at = datetime.now(UTC)

        self.session.add(aggregate)
        self.session.commit()
        self.session.refresh(aggregate)

        return aggregate
