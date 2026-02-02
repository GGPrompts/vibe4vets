"""add safeguards for tags length and status case

Revision ID: 74e602211084
Revises:
Create Date: 2026-02-01

Adds database-level safeguards to prevent data quality issues:
1. CHECK constraint limiting tags array to 100 items max
2. Trigger to normalize status enum to uppercase

These protect against:
- ETL bugs that accumulate tags across records (caused 145K char tags arrays)
- Raw SQL using wrong case for status enum (SQLAlchemy expects uppercase)
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "74e602211084"
down_revision: str | None = "17780412a17f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # First, fix any existing violations by truncating oversized arrays
    # This ensures the constraint can be added without failing
    op.execute("""
        UPDATE resources
        SET tags = tags[1:100]
        WHERE array_length(tags, 1) > 100
    """)

    op.execute("""
        UPDATE resources
        SET subcategories = subcategories[1:50]
        WHERE array_length(subcategories, 1) > 50
    """)

    # Normalize any lowercase status values to uppercase
    # Status is stored as varchar (Python enum, not Postgres enum)
    op.execute("""
        UPDATE resources
        SET status = UPPER(status)
        WHERE status != UPPER(status)
    """)

    # 1. Add CHECK constraint to limit tags array size
    # Prevents runaway ETL from creating massive arrays that break serialization
    op.execute("""
        ALTER TABLE resources
        ADD CONSTRAINT resources_tags_max_length
        CHECK (array_length(tags, 1) IS NULL OR array_length(tags, 1) <= 100)
    """)

    # Also add for subcategories since it has same risk
    op.execute("""
        ALTER TABLE resources
        ADD CONSTRAINT resources_subcategories_max_length
        CHECK (array_length(subcategories, 1) IS NULL OR array_length(subcategories, 1) <= 50)
    """)

    # 2. Create trigger function to normalize status to uppercase
    # This ensures any insert/update (ORM or raw SQL) uses correct case
    # Status is stored as varchar, so just uppercase it directly
    op.execute("""
        CREATE OR REPLACE FUNCTION normalize_resource_status()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.status IS NOT NULL THEN
                NEW.status := UPPER(NEW.status);
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)

    # 3. Create the trigger
    op.execute("""
        CREATE TRIGGER resources_normalize_status
        BEFORE INSERT OR UPDATE ON resources
        FOR EACH ROW
        EXECUTE FUNCTION normalize_resource_status()
    """)


def downgrade() -> None:
    # Remove trigger first
    op.execute("DROP TRIGGER IF EXISTS resources_normalize_status ON resources")

    # Remove trigger function
    op.execute("DROP FUNCTION IF EXISTS normalize_resource_status()")

    # Remove constraints
    op.execute("ALTER TABLE resources DROP CONSTRAINT IF EXISTS resources_tags_max_length")
    op.execute("ALTER TABLE resources DROP CONSTRAINT IF EXISTS resources_subcategories_max_length")
