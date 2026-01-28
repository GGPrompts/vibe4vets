"""Rename underscored categories to camelCase and add new categories

Revision ID: h_rename_categories
Revises: g6486h379496_change_embedding_dimension_384
Create Date: 2026-01-27

Renames:
- mental_health -> mentalHealth
- support_services -> supportServices
- support -> supportServices (merge orphan)

New categories being added via taxonomy.py:
- mentalHealth
- supportServices
- healthcare
- education
- financial
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "h_rename_categories"
down_revision = "g6486h379496"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename mental_health to mentalHealth
    op.execute(
        "UPDATE resources SET categories = array_replace(categories, 'mental_health', 'mentalHealth')"
    )
    # Rename support_services to supportServices
    op.execute(
        "UPDATE resources SET categories = array_replace(categories, 'support_services', 'supportServices')"
    )
    # Merge orphan 'support' into supportServices
    op.execute(
        "UPDATE resources SET categories = array_replace(categories, 'support', 'supportServices')"
    )


def downgrade() -> None:
    # Reverse: rename back to underscored versions
    op.execute(
        "UPDATE resources SET categories = array_replace(categories, 'mentalHealth', 'mental_health')"
    )
    op.execute(
        "UPDATE resources SET categories = array_replace(categories, 'supportServices', 'support_services')"
    )
