"""add_zip_codes_table

Revision ID: ebc114bc5743
Revises: f5375g268385
Create Date: 2026-01-25 03:55:16.809016

Creates the zip_codes table with US zip code centroids for lat/lng lookup.
Uses PostGIS geography type for spatial queries.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ebc114bc5743"
down_revision: str | Sequence[str] | None = "f5375g268385"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create zip_codes table with PostGIS geography column."""
    # Enable PostGIS extension if not already enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Create zip_codes table
    op.create_table(
        "zip_codes",
        sa.Column("zip_code", sa.String(5), primary_key=True),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
    )

    # Add geography column using raw SQL (PostGIS specific)
    op.execute(
        "ALTER TABLE zip_codes ADD COLUMN geog geography(POINT, 4326)"
    )

    # Create spatial index for fast nearby queries
    op.execute(
        "CREATE INDEX idx_zip_codes_geog ON zip_codes USING GIST (geog)"
    )

    # Create index on state for filtering
    op.create_index("ix_zip_codes_state", "zip_codes", ["state"])


def downgrade() -> None:
    """Drop zip_codes table."""
    op.drop_index("ix_zip_codes_state", table_name="zip_codes")
    op.drop_index("idx_zip_codes_geog", table_name="zip_codes")
    op.drop_table("zip_codes")
