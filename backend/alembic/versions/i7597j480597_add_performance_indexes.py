"""add performance indexes

Revision ID: i7597j480597
Revises: ebc114bc5743
Create Date: 2026-01-30 10:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "i7597j480597"
down_revision: str | Sequence[str] | None = "h_rename_categories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add indexes for better query performance."""
    # GIN index on subcategories for tag filtering
    # (tags already has a GIN index, but subcategories is also checked)
    op.create_index(
        "ix_resources_subcategories_gin",
        "resources",
        ["subcategories"],
        postgresql_using="gin",
        if_not_exists=True,
    )

    # Index on created_at for "newest" sort order
    op.create_index(
        "ix_resources_created_at",
        "resources",
        ["created_at"],
        if_not_exists=True,
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index("ix_resources_created_at", table_name="resources", if_exists=True)
    op.drop_index("ix_resources_subcategories_gin", table_name="resources", if_exists=True)
