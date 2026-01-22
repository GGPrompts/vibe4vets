"""add etl_job_runs table for idempotent ETL pipelines

Revision ID: f8i3h6j5k234
Revises: e7h2g5i4j123
Create Date: 2026-01-22 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f8i3h6j5k234"
down_revision: str | Sequence[str] | None = "e7h2g5i4j123"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create etl_job_runs table for checkpointing and idempotency."""
    op.create_table(
        "etl_job_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # Job identification
        sa.Column("job_name", sa.String(100), nullable=False),
        sa.Column("connector_names", postgresql.JSONB, nullable=False, server_default="[]"),
        # Status tracking
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("started_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        # Progress tracking
        sa.Column("total_extracted", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_processed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_created", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_updated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_skipped", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_failed", sa.Integer, nullable=False, server_default="0"),
        # Checkpointing: track processed source URLs to skip on retry
        sa.Column("processed_urls", postgresql.JSONB, nullable=False, server_default="[]"),
        # Current position for resume
        sa.Column("checkpoint_connector_idx", sa.Integer, nullable=False, server_default="0"),
        sa.Column("checkpoint_resource_idx", sa.Integer, nullable=False, server_default="0"),
        # Error details if failed
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_details", postgresql.JSONB, nullable=True),
    )

    # Indexes for common queries
    op.create_index("ix_etl_job_runs_job_name", "etl_job_runs", ["job_name"])
    op.create_index("ix_etl_job_runs_status", "etl_job_runs", ["status"])
    op.create_index("ix_etl_job_runs_started_at", "etl_job_runs", ["started_at"])


def downgrade() -> None:
    """Drop etl_job_runs table."""
    op.drop_index("ix_etl_job_runs_started_at", table_name="etl_job_runs")
    op.drop_index("ix_etl_job_runs_status", table_name="etl_job_runs")
    op.drop_index("ix_etl_job_runs_job_name", table_name="etl_job_runs")
    op.drop_table("etl_job_runs")
