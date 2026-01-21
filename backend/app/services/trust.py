"""Trust scoring service for resource reliability calculations."""

from datetime import UTC, datetime, timedelta

from sqlmodel import Session

from app.models import Resource, Source

# Tier-based reliability scores
TIER_SCORES = {
    1: 1.0,  # VA.gov, DOL, HUD
    2: 0.8,  # DAV, VFW, American Legion
    3: 0.6,  # State veteran agencies
    4: 0.4,  # Community directories
}

# Freshness decay constants (in days)
FRESHNESS_HALF_LIFE = 30  # Score halves every 30 days without verification


class TrustService:
    """Service for calculating and updating trust scores."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def calculate_trust_score(self, resource: Resource) -> float:
        """Calculate overall trust score = reliability * freshness."""
        return resource.reliability_score * resource.freshness_score

    def update_freshness(self, resource: Resource) -> float:
        """Update freshness score based on time since last verification."""
        if resource.last_verified is None:
            # Never verified - use created_at
            reference_date = resource.created_at
        else:
            reference_date = resource.last_verified

        days_old = (datetime.now(UTC) - reference_date).days

        # Exponential decay with half-life
        freshness = 0.5 ** (days_old / FRESHNESS_HALF_LIFE)

        # Clamp between 0.1 and 1.0
        freshness = max(0.1, min(1.0, freshness))

        resource.freshness_score = freshness
        return freshness

    def update_reliability_from_source(self, resource: Resource, source: Source) -> float:
        """Update reliability score based on source tier."""
        reliability = TIER_SCORES.get(source.tier, 0.4)

        # Adjust based on source health
        if source.health_status.value == "degraded":
            reliability *= 0.9
        elif source.health_status.value == "failing":
            reliability *= 0.7

        resource.reliability_score = reliability
        resource.source_id = source.id
        return reliability

    def mark_verified(self, resource: Resource) -> None:
        """Mark a resource as verified, resetting freshness."""
        resource.last_verified = datetime.now(UTC)
        resource.freshness_score = 1.0
        self.session.add(resource)

    def refresh_all_freshness_scores(self) -> int:
        """Refresh freshness scores for all active resources."""
        from sqlmodel import select

        from app.models.resource import ResourceStatus

        stmt = select(Resource).where(Resource.status == ResourceStatus.ACTIVE)
        resources = self.session.exec(stmt).all()

        count = 0
        for resource in resources:
            old_score = resource.freshness_score
            new_score = self.update_freshness(resource)
            if abs(old_score - new_score) > 0.01:
                self.session.add(resource)
                count += 1

        if count > 0:
            self.session.commit()

        return count

    def get_stale_resources(self, days: int = 30) -> list[Resource]:
        """Get resources that haven't been verified in the given number of days."""
        from sqlmodel import select

        from app.models.resource import ResourceStatus

        cutoff = datetime.now(UTC) - timedelta(days=days)

        stmt = (
            select(Resource)
            .where(Resource.status == ResourceStatus.ACTIVE)
            .where((Resource.last_verified < cutoff) | (Resource.last_verified.is_(None)))
            .order_by(Resource.freshness_score.asc())
        )

        return list(self.session.exec(stmt).all())

    def is_risky_change(self, field: str) -> bool:
        """Check if a field change should trigger review."""
        risky_fields = {
            "phone",
            "website",
            "address",
            "eligibility",
            "how_to_apply",
            "cost",
        }
        return field in risky_fields
