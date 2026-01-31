"""add_geog_auto_populate_trigger

Revision ID: 17780412a17f
Revises: i7597j480597
Create Date: 2026-01-31 02:55:43.868182

"""
from collections.abc import Sequence
from typing import Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '17780412a17f'
down_revision: Union[str, Sequence[str], None] = 'i7597j480597'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add trigger to auto-populate geog from lat/lng."""
    # Create function to update geog from lat/lng
    op.execute("""
        CREATE OR REPLACE FUNCTION update_location_geog()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
                NEW.geog := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
            ELSE
                NEW.geog := NULL;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger on locations table
    op.execute("""
        CREATE TRIGGER locations_geog_update
        BEFORE INSERT OR UPDATE OF latitude, longitude ON locations
        FOR EACH ROW
        EXECUTE FUNCTION update_location_geog();
    """)


def downgrade() -> None:
    """Remove trigger and function."""
    op.execute("DROP TRIGGER IF EXISTS locations_geog_update ON locations;")
    op.execute("DROP FUNCTION IF EXISTS update_location_geog();")
