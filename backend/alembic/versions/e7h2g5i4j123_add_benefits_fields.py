"""add benefits consultation fields to locations

Revision ID: e7h2g5i4j123
Revises: d6g1f4h3i012
Create Date: 2026-01-18 19:45:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7h2g5i4j123"
down_revision: str | Sequence[str] | None = "d6g1f4h3i012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add benefits consultation fields to locations table."""
    # === Benefits consultation fields ===
    op.add_column(
        "locations",
        sa.Column(
            "benefits_types_supported",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "locations", sa.Column("representative_type", sa.String(50), nullable=True)
    )
    op.add_column("locations", sa.Column("accredited", sa.Boolean, nullable=True))
    op.add_column("locations", sa.Column("walk_in_available", sa.Boolean, nullable=True))
    op.add_column(
        "locations", sa.Column("appointment_required", sa.Boolean, nullable=True)
    )
    op.add_column("locations", sa.Column("virtual_available", sa.Boolean, nullable=True))
    op.add_column("locations", sa.Column("free_service", sa.Boolean, nullable=True))
    op.add_column(
        "locations",
        sa.Column(
            "languages_supported",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default="{}",
        ),
    )

    # === Create indexes for common benefits filters ===
    op.create_index(
        "ix_locations_benefits_types_supported_gin",
        "locations",
        ["benefits_types_supported"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_locations_representative_type", "locations", ["representative_type"]
    )
    op.create_index("ix_locations_accredited", "locations", ["accredited"])
    op.create_index("ix_locations_virtual_available", "locations", ["virtual_available"])
    op.create_index("ix_locations_walk_in_available", "locations", ["walk_in_available"])


def downgrade() -> None:
    """Remove benefits consultation fields from locations table."""
    # Drop indexes
    op.drop_index("ix_locations_walk_in_available", table_name="locations")
    op.drop_index("ix_locations_virtual_available", table_name="locations")
    op.drop_index("ix_locations_accredited", table_name="locations")
    op.drop_index("ix_locations_representative_type", table_name="locations")
    op.drop_index("ix_locations_benefits_types_supported_gin", table_name="locations")

    # Drop benefits columns
    op.drop_column("locations", "languages_supported")
    op.drop_column("locations", "free_service")
    op.drop_column("locations", "virtual_available")
    op.drop_column("locations", "appointment_required")
    op.drop_column("locations", "walk_in_available")
    op.drop_column("locations", "accredited")
    op.drop_column("locations", "representative_type")
    op.drop_column("locations", "benefits_types_supported")
