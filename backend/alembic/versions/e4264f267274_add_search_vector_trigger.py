"""Add search_vector trigger

Revision ID: e4264f267274
Revises: 6b4c55d1bb4a
Create Date: 2026-01-21 16:38:55.620801

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e4264f267274"
down_revision: str | Sequence[str] | None = "6b4c55d1bb4a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Convert search_vector from computed column to trigger-based.

    The original schema defined search_vector as a GENERATED ALWAYS column,
    which cannot be updated by triggers. We need to:
    1. Drop the computed column
    2. Add a regular tsvector column
    3. Create a trigger to auto-populate it
    """
    # Step 1: Drop the index on search_vector first
    op.execute("DROP INDEX IF EXISTS ix_resources_search_vector_gin;")

    # Step 2: Drop the computed column and recreate as regular column
    op.execute("ALTER TABLE resources DROP COLUMN IF EXISTS search_vector;")
    op.execute("ALTER TABLE resources ADD COLUMN search_vector tsvector;")

    # Step 3: Recreate the GIN index
    op.execute("CREATE INDEX ix_resources_search_vector_gin ON resources USING gin(search_vector);")

    # Step 4: Create function to update search_vector
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

    # Step 5: Create trigger on resources table
    op.execute("""
        CREATE TRIGGER resources_search_vector_update
        BEFORE INSERT OR UPDATE ON resources
        FOR EACH ROW
        EXECUTE FUNCTION update_resource_search_vector();
    """)

    # Step 6: Backfill existing resources by triggering an update
    op.execute("""
        UPDATE resources SET title = title WHERE true;
    """)


def downgrade() -> None:
    """Revert to computed column (original schema)."""
    # Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS resources_search_vector_update ON resources;")
    op.execute("DROP FUNCTION IF EXISTS update_resource_search_vector();")

    # Drop index and column
    op.execute("DROP INDEX IF EXISTS ix_resources_search_vector_gin;")
    op.execute("ALTER TABLE resources DROP COLUMN IF EXISTS search_vector;")

    # Recreate as computed column (matches initial schema)
    op.execute("""
        ALTER TABLE resources ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            to_tsvector('english', coalesce(title, '') || ' ' ||
            coalesce(description, '') || ' ' || coalesce(summary, ''))
        ) STORED;
    """)

    # Recreate index
    op.execute("CREATE INDEX ix_resources_search_vector_gin ON resources USING gin(search_vector);")
