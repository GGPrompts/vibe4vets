"""add analytics tables for privacy-respecting usage tracking

Revision ID: d6g1f4h3i012
Revises: c5f9e3g2h890
Create Date: 2026-01-18 19:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d6g1f4h3i012"
down_revision: str | Sequence[str] | None = "c5f9e3g2h890"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create analytics tables for anonymous usage tracking."""
    # Analytics events table - stores individual anonymous events
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # Event classification
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_name", sa.String(100), nullable=False),
        # Anonymous context (no PII)
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        # For search events
        sa.Column("search_query", sa.String(255), nullable=True),
        # For wizard events
        sa.Column("wizard_step", sa.Integer, nullable=True),
        # Metadata
        sa.Column("page_path", sa.String(255), nullable=True),
        # Timestamp
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Indexes for common queries
    op.create_index("ix_analytics_events_event_type", "analytics_events", ["event_type"])
    op.create_index("ix_analytics_events_created_at", "analytics_events", ["created_at"])
    op.create_index("ix_analytics_events_resource_id", "analytics_events", ["resource_id"])

    # Daily aggregates table - pre-computed summaries for fast dashboard queries
    op.create_table(
        "analytics_daily_aggregates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("date", sa.DateTime, nullable=False),
        # Event counts
        sa.Column("total_searches", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_resource_views", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_chat_sessions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_chat_messages", sa.Integer, nullable=False, server_default="0"),
        sa.Column("wizard_starts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("wizard_completions", sa.Integer, nullable=False, server_default="0"),
        # JSON strings for top items
        sa.Column("top_categories", sa.Text, nullable=True),
        sa.Column("top_states", sa.Text, nullable=True),
        sa.Column("top_searches", sa.Text, nullable=True),
        sa.Column("top_resources", sa.Text, nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Index for date lookups
    op.create_index("ix_analytics_daily_aggregates_date", "analytics_daily_aggregates", ["date"])


def downgrade() -> None:
    """Drop analytics tables."""
    op.drop_index("ix_analytics_daily_aggregates_date", table_name="analytics_daily_aggregates")
    op.drop_table("analytics_daily_aggregates")

    op.drop_index("ix_analytics_events_resource_id", table_name="analytics_events")
    op.drop_index("ix_analytics_events_created_at", table_name="analytics_events")
    op.drop_index("ix_analytics_events_event_type", table_name="analytics_events")
    op.drop_table("analytics_events")
