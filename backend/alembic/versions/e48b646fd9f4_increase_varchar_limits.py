"""Increase varchar limits for long content.

Revision ID: e48b646fd9f4
Revises: ebc114bc5743
Create Date: 2026-01-25 22:57:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e48b646fd9f4"
down_revision: str | None = "ebc114bc5743"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Resources table - increase limits for potentially long content
    op.alter_column("resources", "title", type_=sa.VARCHAR(500), existing_type=sa.VARCHAR(255))
    op.alter_column("resources", "phone", type_=sa.VARCHAR(255), existing_type=sa.VARCHAR(150))
    op.alter_column("resources", "hours", type_=sa.VARCHAR(500), existing_type=sa.VARCHAR(255))
    op.alter_column("resources", "website", type_=sa.VARCHAR(1000), existing_type=sa.VARCHAR(500))
    op.alter_column("resources", "source_url", type_=sa.VARCHAR(1000), existing_type=sa.VARCHAR(500))
    op.alter_column("resources", "cost", type_=sa.VARCHAR(255), existing_type=sa.VARCHAR(100))

    # Organizations table
    op.alter_column("organizations", "name", type_=sa.VARCHAR(500), existing_type=sa.VARCHAR(255))
    op.alter_column("organizations", "website", type_=sa.VARCHAR(1000), existing_type=sa.VARCHAR(500))

    # Locations table
    op.alter_column("locations", "address", type_=sa.VARCHAR(1000), existing_type=sa.VARCHAR(500))
    op.alter_column("locations", "intake_url", type_=sa.VARCHAR(1000), existing_type=sa.VARCHAR(500))

    # Sources table
    op.alter_column("sources", "url", type_=sa.VARCHAR(1000), existing_type=sa.VARCHAR(500))


def downgrade() -> None:
    # Revert changes (may truncate data!)
    op.alter_column("resources", "title", type_=sa.VARCHAR(255), existing_type=sa.VARCHAR(500))
    op.alter_column("resources", "phone", type_=sa.VARCHAR(150), existing_type=sa.VARCHAR(255))
    op.alter_column("resources", "hours", type_=sa.VARCHAR(255), existing_type=sa.VARCHAR(500))
    op.alter_column("resources", "website", type_=sa.VARCHAR(500), existing_type=sa.VARCHAR(1000))
    op.alter_column("resources", "source_url", type_=sa.VARCHAR(500), existing_type=sa.VARCHAR(1000))
    op.alter_column("resources", "cost", type_=sa.VARCHAR(100), existing_type=sa.VARCHAR(255))

    op.alter_column("organizations", "name", type_=sa.VARCHAR(255), existing_type=sa.VARCHAR(500))
    op.alter_column("organizations", "website", type_=sa.VARCHAR(500), existing_type=sa.VARCHAR(1000))

    op.alter_column("locations", "address", type_=sa.VARCHAR(500), existing_type=sa.VARCHAR(1000))
    op.alter_column("locations", "intake_url", type_=sa.VARCHAR(500), existing_type=sa.VARCHAR(1000))

    op.alter_column("sources", "url", type_=sa.VARCHAR(500), existing_type=sa.VARCHAR(1000))
