#!/usr/bin/env python3
"""Bulk approve pending reviews in the database.

Usage:
    python scripts/bulk_approve_reviews.py          # Show pending reviews
    python scripts/bulk_approve_reviews.py --approve  # Approve all pending
"""

import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select

from app.database import engine
from app.models.resource import Resource
from app.models.review import ReviewState, ReviewStatus


def main():
    approve = "--approve" in sys.argv

    with Session(engine) as session:
        # Get all pending reviews
        stmt = (
            select(ReviewState, Resource)
            .join(Resource)
            .where(ReviewState.status == ReviewStatus.PENDING)
        )
        results = session.exec(stmt).all()

        if not results:
            print("No pending reviews found!")
            return

        print(f"\n{'='*60}")
        print(f"Found {len(results)} pending reviews")
        print(f"{'='*60}\n")

        # Count reasons
        reasons = Counter(r[0].reason for r in results)
        print("Reasons for review:")
        for reason, count in reasons.most_common():
            print(f"  - {reason}: {count}")
        print()

        # Show sample
        print("Sample of pending reviews:")
        print("-" * 60)
        for review, resource in results[:10]:
            print(f"  [{review.id}]")
            print(f"    Resource: {resource.title[:50]}...")
            print(f"    Reason: {review.reason}")
            print()

        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more\n")

        if approve:
            print(f"{'='*60}")
            print("APPROVING ALL PENDING REVIEWS...")
            print(f"{'='*60}\n")

            for review, _ in results:
                review.status = ReviewStatus.APPROVED
                review.reviewer = "bulk_script"
                review.reviewed_at = datetime.now(UTC)
                review.notes = "Bulk approved - category fixes"
                session.add(review)

            session.commit()
            print(f"Successfully approved {len(results)} reviews!")
        else:
            print("Run with --approve to approve all pending reviews")


if __name__ == "__main__":
    main()
