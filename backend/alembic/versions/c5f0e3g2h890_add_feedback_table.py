"""add feedback table for user-reported resource corrections

Revision ID: c5f0e3g2h890
Revises: b4e9d2f1g789
Create Date: 2026-01-18 19:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5f0e3g2h890"
down_revision: str | Sequence[str] | None = "b4e9d2f1g789"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create feedback table for anonymous user-reported resource corrections."""
    op.create_table(
        "feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "resource_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # What's wrong
        sa.Column("issue_type", sa.String(50), nullable=False, server_default="other"),
        sa.Column("description", sa.String(1000), nullable=False),
        # Optional correction info
        sa.Column("suggested_correction", sa.String(1000), nullable=True),
        sa.Column("source_of_correction", sa.String(255), nullable=True),
        # Review workflow
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewer", sa.String(100), nullable=True),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
        sa.Column("reviewer_notes", sa.String(1000), nullable=True),
        # Timestamp
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Indexes for common queries
    op.create_index("ix_feedback_resource_id", "feedback", ["resource_id"])
    op.create_index("ix_feedback_status", "feedback", ["status"])
    op.create_index("ix_feedback_created_at", "feedback", ["created_at"])


def downgrade() -> None:
    """Drop feedback table."""
    op.drop_index("ix_feedback_created_at", table_name="feedback")
    op.drop_index("ix_feedback_status", table_name="feedback")
    op.drop_index("ix_feedback_resource_id", table_name="feedback")
    op.drop_table("feedback")
