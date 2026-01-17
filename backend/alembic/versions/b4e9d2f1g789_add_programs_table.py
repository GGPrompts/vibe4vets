"""add programs table for provider-to-program relationships

Revision ID: b4e9d2f1g789
Revises: a3f8c2d1e456
Create Date: 2026-01-17 20:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b4e9d2f1g789"
down_revision: str | Sequence[str] | None = "a3f8c2d1e456"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create programs table and add program_id FK to resources."""
    # Create programs table
    op.create_table(
        "programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
            index=True,
        ),
        # Program identification
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("program_type", sa.String(50), nullable=False, server_default="other"),
        sa.Column("grant_number", sa.String(100), nullable=True, index=True),
        sa.Column("external_id", sa.String(100), nullable=True),
        # Description
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "services_offered",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default="{}",
        ),
        # Geographic coverage
        sa.Column(
            "service_areas",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "states",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default="{}",
        ),
        # Funding period
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("fiscal_year", sa.String(10), nullable=True),
        # Contact
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        # Status and timestamps
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Create index on program_type for filtering
    op.create_index("ix_programs_program_type", "programs", ["program_type"])
    op.create_index("ix_programs_fiscal_year", "programs", ["fiscal_year"])
    op.create_index("ix_programs_status", "programs", ["status"])

    # GIN index for service_areas array containment queries
    op.create_index(
        "ix_programs_service_areas_gin",
        "programs",
        ["service_areas"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_programs_states_gin",
        "programs",
        ["states"],
        postgresql_using="gin",
    )

    # Add program_id FK to resources table
    op.add_column(
        "resources",
        sa.Column(
            "program_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("programs.id"),
            nullable=True,
            index=True,
        ),
    )


def downgrade() -> None:
    """Remove programs table and program_id FK from resources."""
    # Remove program_id from resources
    op.drop_column("resources", "program_id")

    # Drop indexes
    op.drop_index("ix_programs_states_gin", table_name="programs")
    op.drop_index("ix_programs_service_areas_gin", table_name="programs")
    op.drop_index("ix_programs_status", table_name="programs")
    op.drop_index("ix_programs_fiscal_year", table_name="programs")
    op.drop_index("ix_programs_program_type", table_name="programs")

    # Drop programs table
    op.drop_table("programs")
