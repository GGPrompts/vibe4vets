"""add_zip_codes_table

Revision ID: ebc114bc5743
Revises: f5375g268385
Create Date: 2026-01-25 03:55:16.809016

Creates the zip_codes table with US zip code centroids for lat/lng lookup.
Uses PostGIS geography type for spatial queries when available.
"""

import logging
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ebc114bc5743"
down_revision: str | Sequence[str] | None = "f5375g268385"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

logger = logging.getLogger(__name__)


def _postgis_available() -> bool:
    """Check if PostGIS extension is available on this PostgreSQL instance."""
    conn = op.get_bind()
    result = conn.execute(text("SELECT 1 FROM pg_available_extensions WHERE name = 'postgis'"))
    return result.scalar() is not None


def upgrade() -> None:
    """Create zip_codes table with PostGIS geography column if available."""
    has_postgis = _postgis_available()

    if has_postgis:
        op.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    else:
        logger.warning(
            "PostGIS extension not available. Creating zip_codes table without "
            "geography column. Spatial queries will use lat/lng directly."
        )

    # Create zip_codes table (works with or without PostGIS)
    op.create_table(
        "zip_codes",
        sa.Column("zip_code", sa.String(5), primary_key=True),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
    )

    if has_postgis:
        # Add geography column using raw SQL (PostGIS specific)
        op.execute(text("ALTER TABLE zip_codes ADD COLUMN geog geography(POINT, 4326)"))
        # Create spatial index for fast nearby queries
        op.execute(text("CREATE INDEX idx_zip_codes_geog ON zip_codes USING GIST (geog)"))

    # Create index on state for filtering (always)
    op.create_index("ix_zip_codes_state", "zip_codes", ["state"])


def downgrade() -> None:
    """Drop zip_codes table."""
    op.drop_index("ix_zip_codes_state", table_name="zip_codes")
    # Drop spatial index if it exists (may not if PostGIS wasn't available)
    op.execute(text("DROP INDEX IF EXISTS idx_zip_codes_geog"))
    op.drop_table("zip_codes")
