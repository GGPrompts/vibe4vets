"""Freshness score update job.

Updates freshness scores for all active resources based on
time since last verification. Runs more frequently than the
full refresh job (e.g., hourly) to keep trust scores accurate.
"""

from datetime import datetime
from typing import Any

from sqlmodel import Session, func, select

from app.models import Resource
from app.models.resource import ResourceStatus
from app.services.trust import TrustService
from jobs.base import BaseJob


class FreshnessJob(BaseJob):
    """Job to update freshness scores for all resources.

    Uses TrustService to recalculate freshness based on
    time since last verification, applying exponential decay.
    """

    @property
    def name(self) -> str:
        return "freshness"

    @property
    def description(self) -> str:
        return "Update freshness scores for all active resources"

    def execute(
        self,
        session: Session,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run the freshness update job.

        Args:
            session: Database session.
            **kwargs: Additional arguments (ignored).

        Returns:
            Statistics dictionary with counts.
        """
        trust_service = TrustService(session)

        # Get counts before update
        total_active = self._count_active_resources(session)

        self._log(f"Updating freshness for {total_active} active resources")

        # Update freshness scores
        updated_count = trust_service.refresh_all_freshness_scores()

        # Get average freshness score after update
        avg_freshness = self._get_average_freshness(session)

        # Get count of stale resources (< 30 days)
        stale_count = len(trust_service.get_stale_resources(days=30))

        stats: dict[str, Any] = {
            "total_active": total_active,
            "updated": updated_count,
            "unchanged": total_active - updated_count,
            "average_freshness": round(avg_freshness, 3) if avg_freshness else None,
            "stale_count": stale_count,
        }

        return stats

    def _count_active_resources(self, session: Session) -> int:
        """Count active resources in the database."""
        stmt = select(func.count(Resource.id)).where(
            Resource.status == ResourceStatus.ACTIVE
        )
        result = session.exec(stmt).one()
        return result or 0

    def _get_average_freshness(self, session: Session) -> float | None:
        """Get average freshness score for active resources."""
        stmt = select(func.avg(Resource.freshness_score)).where(
            Resource.status == ResourceStatus.ACTIVE
        )
        result = session.exec(stmt).one()
        return float(result) if result else None

    def _format_message(self, stats: dict[str, Any]) -> str:
        """Format freshness statistics into a message."""
        updated = stats.get("updated", 0)
        total = stats.get("total_active", 0)
        avg = stats.get("average_freshness")
        stale = stats.get("stale_count", 0)

        avg_str = f"{avg:.1%}" if avg else "N/A"

        return (
            f"Freshness updated: {updated}/{total} resources changed, "
            f"avg={avg_str}, {stale} stale"
        )
