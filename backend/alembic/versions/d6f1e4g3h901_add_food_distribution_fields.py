"""add food distribution fields to locations

Revision ID: d6f1e4g3h901
Revises: c5f0e3g2h890
Create Date: 2026-01-18 19:36:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d6f1e4g3h901"
down_revision: str | Sequence[str] | None = "c5f0e3g2h890"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add food distribution specific fields to locations table."""
    # === Food distribution fields ===
    op.add_column(
        "locations",
        sa.Column("distribution_schedule", sa.String(500), nullable=True),
    )
    op.add_column(
        "locations",
        sa.Column(
            "serves_dietary",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "locations",
        sa.Column("quantity_limit", sa.String(255), nullable=True),
    )
    op.add_column(
        "locations",
        sa.Column("id_required", sa.Boolean, nullable=True),
    )

    # === Create index for dietary options (GIN for array containment queries) ===
    op.create_index(
        "ix_locations_serves_dietary_gin",
        "locations",
        ["serves_dietary"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Remove food distribution fields from locations table."""
    # Drop index
    op.drop_index("ix_locations_serves_dietary_gin", table_name="locations")

    # Drop food distribution columns
    op.drop_column("locations", "id_required")
    op.drop_column("locations", "quantity_limit")
    op.drop_column("locations", "serves_dietary")
    op.drop_column("locations", "distribution_schedule")
