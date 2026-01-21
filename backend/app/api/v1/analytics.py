"""Analytics endpoints for privacy-respecting usage tracking.

Public endpoint for recording events (no auth, no PII).
Admin endpoints for viewing aggregated statistics.
"""

from fastapi import APIRouter, Query
from sqlmodel import select

from app.api.deps import AdminAuthDep
from app.database import SessionDep
from app.models import AnalyticsEvent, Resource
from app.schemas.analytics import (
    AnalyticsDashboardResponse,
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    AnalyticsSummaryStats,
    DailyTrendItem,
    PopularCategoryItem,
    PopularResourceItem,
    PopularSearchItem,
    PopularStateItem,
    WizardFunnelStats,
)
from app.services.analytics import AnalyticsService

router = APIRouter()


# ============================================================================
# Public Endpoints (no auth required)
# ============================================================================


@router.post("/events", response_model=AnalyticsEventResponse, status_code=201)
def record_event(
    event_data: AnalyticsEventCreate,
    session: SessionDep,
) -> AnalyticsEvent:
    """Record an anonymous analytics event.

    This endpoint accepts usage events from the frontend without requiring
    authentication. No PII is collected - no IP addresses, cookies, or
    user identifiers are stored.

    Events are used to understand aggregate usage patterns:
    - Which searches are most common
    - Which resources are most viewed
    - How users interact with the wizard
    """
    event = AnalyticsEvent(
        event_type=event_data.event_type,
        event_name=event_data.event_name,
        category=event_data.category,
        state=event_data.state[:2] if event_data.state else None,
        resource_id=event_data.resource_id,
        search_query=event_data.search_query[:255] if event_data.search_query else None,
        wizard_step=event_data.wizard_step,
        page_path=event_data.page_path,
    )

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


# ============================================================================
# Admin Endpoints
# ============================================================================


@router.get("/admin/summary", response_model=AnalyticsSummaryStats)
def get_summary_stats(
    _auth: AdminAuthDep,
    session: SessionDep,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
) -> AnalyticsSummaryStats:
    """Get summary statistics for the specified period."""
    analytics = AnalyticsService(session)
    stats = analytics.get_summary_stats(days=days)
    return AnalyticsSummaryStats(**stats)


@router.get("/admin/popular-searches", response_model=list[PopularSearchItem])
def get_popular_searches(
    _auth: AdminAuthDep,
    session: SessionDep,
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[PopularSearchItem]:
    """Get most popular search queries."""
    analytics = AnalyticsService(session)
    results = analytics.get_popular_searches(days=days, limit=limit)
    return [PopularSearchItem(**item) for item in results]


@router.get("/admin/popular-categories", response_model=list[PopularCategoryItem])
def get_popular_categories(
    _auth: AdminAuthDep,
    session: SessionDep,
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[PopularCategoryItem]:
    """Get most used categories."""
    analytics = AnalyticsService(session)
    results = analytics.get_popular_categories(days=days, limit=limit)
    return [PopularCategoryItem(**item) for item in results]


@router.get("/admin/popular-states", response_model=list[PopularStateItem])
def get_popular_states(
    _auth: AdminAuthDep,
    session: SessionDep,
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[PopularStateItem]:
    """Get most searched states."""
    analytics = AnalyticsService(session)
    results = analytics.get_popular_states(days=days, limit=limit)
    return [PopularStateItem(**item) for item in results]


@router.get("/admin/popular-resources", response_model=list[PopularResourceItem])
def get_popular_resources(
    _auth: AdminAuthDep,
    session: SessionDep,
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[PopularResourceItem]:
    """Get most viewed resources with titles."""
    analytics = AnalyticsService(session)
    results = analytics.get_most_viewed_resources(days=days, limit=limit)

    # Enrich with resource titles
    resource_ids = [item["resource_id"] for item in results]
    resources = session.exec(select(Resource).where(Resource.id.in_(resource_ids))).all()
    title_map = {str(r.id): r.title for r in resources}

    return [
        PopularResourceItem(
            resource_id=item["resource_id"],
            resource_title=title_map.get(item["resource_id"]),
            count=item["count"],
        )
        for item in results
    ]


@router.get("/admin/wizard-funnel", response_model=WizardFunnelStats)
def get_wizard_funnel(
    _auth: AdminAuthDep,
    session: SessionDep,
    days: int = Query(default=30, ge=1, le=365),
) -> WizardFunnelStats:
    """Get wizard completion funnel statistics."""
    analytics = AnalyticsService(session)
    stats = analytics.get_wizard_funnel(days=days)
    return WizardFunnelStats(
        starts=stats["starts"],
        completions=stats["completions"],
        completion_rate=stats["completion_rate"],
    )


@router.get("/admin/daily-trends", response_model=list[DailyTrendItem])
def get_daily_trends(
    _auth: AdminAuthDep,
    session: SessionDep,
    days: int = Query(default=30, ge=1, le=365),
) -> list[DailyTrendItem]:
    """Get daily event counts for trend chart."""
    analytics = AnalyticsService(session)
    trends = analytics.get_daily_trends(days=days)
    return [DailyTrendItem(**item) for item in trends]


@router.get("/admin/dashboard", response_model=AnalyticsDashboardResponse)
def get_dashboard(
    _auth: AdminAuthDep,
    session: SessionDep,
    days: int = Query(default=30, ge=1, le=365),
) -> AnalyticsDashboardResponse:
    """Get full analytics dashboard data in a single request."""
    analytics = AnalyticsService(session)

    # Get all stats
    summary = analytics.get_summary_stats(days=days)
    popular_searches = analytics.get_popular_searches(days=days, limit=10)
    popular_categories = analytics.get_popular_categories(days=days, limit=10)
    popular_states = analytics.get_popular_states(days=days, limit=10)
    popular_resources_raw = analytics.get_most_viewed_resources(days=days, limit=10)
    wizard_funnel = analytics.get_wizard_funnel(days=days)
    daily_trends = analytics.get_daily_trends(days=days)

    # Enrich resources with titles
    resource_ids = [item["resource_id"] for item in popular_resources_raw]
    resources = session.exec(select(Resource).where(Resource.id.in_(resource_ids))).all()
    title_map = {str(r.id): r.title for r in resources}

    popular_resources = [
        PopularResourceItem(
            resource_id=item["resource_id"],
            resource_title=title_map.get(item["resource_id"]),
            count=item["count"],
        )
        for item in popular_resources_raw
    ]

    return AnalyticsDashboardResponse(
        summary=AnalyticsSummaryStats(**summary),
        popular_searches=[PopularSearchItem(**item) for item in popular_searches],
        popular_categories=[PopularCategoryItem(**item) for item in popular_categories],
        popular_states=[PopularStateItem(**item) for item in popular_states],
        popular_resources=popular_resources,
        wizard_funnel=WizardFunnelStats(
            starts=wizard_funnel["starts"],
            completions=wizard_funnel["completions"],
            completion_rate=wizard_funnel["completion_rate"],
        ),
        daily_trends=[DailyTrendItem(**item) for item in daily_trends],
    )
