"""Add link health tracking columns

Revision ID: f5375g268385
Revises: e4264f267274
Create Date: 2026-01-22 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f5375g268385"
down_revision: str | Sequence[str] | None = "e4264f267274"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add link health tracking columns to resources table."""
    op.add_column("resources", sa.Column("link_checked_at", sa.DateTime(), nullable=True))
    op.add_column("resources", sa.Column("link_http_status", sa.Integer(), nullable=True))
    op.add_column("resources", sa.Column("link_health_score", sa.Float(), nullable=True))
    op.add_column(
        "resources", sa.Column("link_flagged_reason", sa.String(length=500), nullable=True)
    )


def downgrade() -> None:
    """Remove link health tracking columns from resources table."""
    op.drop_column("resources", "link_flagged_reason")
    op.drop_column("resources", "link_health_score")
    op.drop_column("resources", "link_http_status")
    op.drop_column("resources", "link_checked_at")
