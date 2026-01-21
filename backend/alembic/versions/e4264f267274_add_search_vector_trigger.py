"""Add search_vector trigger

Revision ID: e4264f267274
Revises: 6b4c55d1bb4a
Create Date: 2026-01-21 16:38:55.620801

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e4264f267274'
down_revision: Union[str, Sequence[str], None] = '6b4c55d1bb4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create trigger to auto-populate search_vector on insert/update."""
    # Create function to update search_vector
    op.execute("""
        CREATE OR REPLACE FUNCTION update_resource_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english',
                coalesce(NEW.title, '') || ' ' ||
                coalesce(NEW.description, '') || ' ' ||
                coalesce(NEW.summary, '') || ' ' ||
                coalesce((SELECT l.city FROM locations l WHERE l.id = NEW.location_id), '') || ' ' ||
                coalesce((SELECT l.state FROM locations l WHERE l.id = NEW.location_id), '') || ' ' ||
                coalesce((SELECT o.name FROM organizations o WHERE o.id = NEW.organization_id), '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger on resources table
    op.execute("""
        CREATE TRIGGER resources_search_vector_update
        BEFORE INSERT OR UPDATE ON resources
        FOR EACH ROW
        EXECUTE FUNCTION update_resource_search_vector();
    """)

    # Backfill existing resources
    op.execute("""
        UPDATE resources r
        SET search_vector = to_tsvector('english',
            coalesce(r.title, '') || ' ' ||
            coalesce(r.description, '') || ' ' ||
            coalesce(r.summary, '') || ' ' ||
            coalesce((SELECT l.city FROM locations l WHERE l.id = r.location_id), '') || ' ' ||
            coalesce((SELECT l.state FROM locations l WHERE l.id = r.location_id), '') || ' ' ||
            coalesce((SELECT o.name FROM organizations o WHERE o.id = r.organization_id), '')
        )
        WHERE search_vector IS NULL;
    """)


def downgrade() -> None:
    """Remove search_vector trigger."""
    op.execute("DROP TRIGGER IF EXISTS resources_search_vector_update ON resources;")
    op.execute("DROP FUNCTION IF EXISTS update_resource_search_vector();")
