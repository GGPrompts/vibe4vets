"""add eligibility fields to locations

Revision ID: a3f8c2d1e456
Revises: d71df951e5d9
Create Date: 2026-01-15 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3f8c2d1e456"
down_revision: str | Sequence[str] | None = "d71df951e5d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add eligibility, intake, and verification fields to locations table."""
    # === Eligibility constraints ===
    op.add_column("locations", sa.Column("age_min", sa.Integer, nullable=True))
    op.add_column("locations", sa.Column("age_max", sa.Integer, nullable=True))
    op.add_column("locations", sa.Column("household_size_min", sa.Integer, nullable=True))
    op.add_column("locations", sa.Column("household_size_max", sa.Integer, nullable=True))
    op.add_column("locations", sa.Column("income_limit_type", sa.String(50), nullable=True))
    op.add_column("locations", sa.Column("income_limit_value", sa.Integer, nullable=True))
    op.add_column("locations", sa.Column("income_limit_ami_percent", sa.Integer, nullable=True))
    op.add_column(
        "locations",
        sa.Column(
            "housing_status_required",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column("locations", sa.Column("active_duty_required", sa.Boolean, nullable=True))
    op.add_column("locations", sa.Column("discharge_required", sa.String(50), nullable=True))
    op.add_column(
        "locations",
        sa.Column("veteran_status_required", sa.Boolean, nullable=False, server_default="true"),
    )
    op.add_column(
        "locations",
        sa.Column(
            "docs_required",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column("locations", sa.Column("waitlist_status", sa.String(20), nullable=True))

    # === Intake information ===
    op.add_column("locations", sa.Column("intake_phone", sa.String(50), nullable=True))
    op.add_column("locations", sa.Column("intake_url", sa.String(500), nullable=True))
    op.add_column("locations", sa.Column("intake_hours", sa.String(255), nullable=True))
    op.add_column("locations", sa.Column("intake_notes", sa.Text, nullable=True))

    # === Verification metadata ===
    op.add_column("locations", sa.Column("last_verified_at", sa.DateTime, nullable=True))
    op.add_column("locations", sa.Column("verified_by", sa.String(50), nullable=True))
    op.add_column("locations", sa.Column("verification_notes", sa.Text, nullable=True))

    # === Create indexes for common eligibility filters ===
    op.create_index("ix_locations_age_min", "locations", ["age_min"])
    op.create_index(
        "ix_locations_income_limit_ami_percent", "locations", ["income_limit_ami_percent"]
    )
    op.create_index("ix_locations_waitlist_status", "locations", ["waitlist_status"])
    op.create_index(
        "ix_locations_housing_status_required_gin",
        "locations",
        ["housing_status_required"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Remove eligibility, intake, and verification fields from locations table."""
    # Drop indexes
    op.drop_index("ix_locations_housing_status_required_gin", table_name="locations")
    op.drop_index("ix_locations_waitlist_status", table_name="locations")
    op.drop_index("ix_locations_income_limit_ami_percent", table_name="locations")
    op.drop_index("ix_locations_age_min", table_name="locations")

    # Drop verification columns
    op.drop_column("locations", "verification_notes")
    op.drop_column("locations", "verified_by")
    op.drop_column("locations", "last_verified_at")

    # Drop intake columns
    op.drop_column("locations", "intake_notes")
    op.drop_column("locations", "intake_hours")
    op.drop_column("locations", "intake_url")
    op.drop_column("locations", "intake_phone")

    # Drop eligibility columns
    op.drop_column("locations", "waitlist_status")
    op.drop_column("locations", "docs_required")
    op.drop_column("locations", "veteran_status_required")
    op.drop_column("locations", "discharge_required")
    op.drop_column("locations", "active_duty_required")
    op.drop_column("locations", "housing_status_required")
    op.drop_column("locations", "income_limit_ami_percent")
    op.drop_column("locations", "income_limit_value")
    op.drop_column("locations", "income_limit_type")
    op.drop_column("locations", "household_size_max")
    op.drop_column("locations", "household_size_min")
    op.drop_column("locations", "age_max")
    op.drop_column("locations", "age_min")
