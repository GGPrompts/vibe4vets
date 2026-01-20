"""Review service for admin review queue management."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from app.models import Organization, Resource
from app.models.resource import ResourceStatus
from app.models.review import ChangeLog, ReviewState, ReviewStatus
from app.schemas.review import ReviewAction, ReviewActionType, ReviewQueueItem


class ReviewService:
    """Service for managing the review queue."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_queue(
        self,
        status: str = "pending",
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ReviewQueueItem], int]:
        """Get items in the review queue."""
        # Build query
        stmt = select(ReviewState)

        if status != "all":
            stmt = stmt.where(ReviewState.status == ReviewStatus(status))

        # Get total count
        count_stmt = select(ReviewState.id)
        if status != "all":
            count_stmt = count_stmt.where(ReviewState.status == ReviewStatus(status))
        total = len(self.session.exec(count_stmt).all())

        # Apply pagination
        stmt = stmt.order_by(ReviewState.created_at.desc()).offset(offset).limit(limit)
        reviews = self.session.exec(stmt).all()

        # Build response items
        items = []
        for review in reviews:
            resource = self.session.get(Resource, review.resource_id)
            if not resource:
                continue

            organization = self.session.get(Organization, resource.organization_id)

            # Get recent changes
            changes_stmt = (
                select(ChangeLog)
                .where(ChangeLog.resource_id == review.resource_id)
                .order_by(ChangeLog.timestamp.desc())
                .limit(5)
            )
            changes = self.session.exec(changes_stmt).all()
            changes_summary = [f"{c.field}: {c.old_value or 'none'} -> {c.new_value or 'none'}" for c in changes]

            items.append(
                ReviewQueueItem(
                    id=review.id,
                    resource_id=review.resource_id,
                    resource_title=resource.title,
                    organization_name=organization.name if organization else "Unknown",
                    reason=review.reason,
                    status=review.status.value,
                    created_at=review.created_at,
                    changes_summary=changes_summary,
                )
            )

        return items, total

    def create_review(
        self,
        resource_id: UUID,
        reason: str,
    ) -> ReviewState:
        """Create a new review request for a resource."""
        # Check if there's already a pending review
        stmt = (
            select(ReviewState)
            .where(ReviewState.resource_id == resource_id)
            .where(ReviewState.status == ReviewStatus.PENDING)
        )
        existing = self.session.exec(stmt).first()
        if existing:
            # Update reason to include new info
            existing.reason = f"{existing.reason}; {reason}" if existing.reason else reason
            self.session.add(existing)
            self.session.commit()
            return existing

        # Create new review
        review = ReviewState(
            resource_id=resource_id,
            status=ReviewStatus.PENDING,
            reason=reason,
        )
        self.session.add(review)

        # Update resource status
        resource = self.session.get(Resource, resource_id)
        if resource:
            resource.status = ResourceStatus.NEEDS_REVIEW
            self.session.add(resource)

        self.session.commit()
        self.session.refresh(review)
        return review

    def process_review(
        self,
        review_id: UUID,
        action: ReviewAction,
    ) -> ReviewState | None:
        """Process a review action (approve or reject)."""
        review = self.session.get(ReviewState, review_id)
        if not review:
            return None

        # Update review state
        if action.action == ReviewActionType.APPROVE:
            review.status = ReviewStatus.APPROVED
        else:
            review.status = ReviewStatus.REJECTED

        review.reviewer = action.reviewer
        review.reviewed_at = datetime.utcnow()
        review.notes = action.notes
        self.session.add(review)

        # Update resource status
        resource = self.session.get(Resource, review.resource_id)
        if resource:
            if action.action == ReviewActionType.APPROVE:
                resource.status = ResourceStatus.ACTIVE
                resource.last_verified = datetime.utcnow()
                resource.freshness_score = 1.0
            else:
                resource.status = ResourceStatus.INACTIVE
            self.session.add(resource)

        self.session.commit()
        self.session.refresh(review)
        return review

    def log_change(
        self,
        resource_id: UUID,
        field: str,
        old_value: str | None,
        new_value: str | None,
        change_type: str = "update",
    ) -> ChangeLog:
        """Log a field change for audit trail."""
        from app.models.review import ChangeType

        change = ChangeLog(
            resource_id=resource_id,
            field=field,
            old_value=old_value,
            new_value=new_value,
            change_type=ChangeType(change_type),
        )
        self.session.add(change)
        self.session.commit()
        self.session.refresh(change)
        return change
