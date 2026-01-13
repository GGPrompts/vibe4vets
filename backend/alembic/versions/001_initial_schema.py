"""Initial schema with all models.

Revision ID: 001_initial
Revises:
Create Date: 2026-01-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Organizations table
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("ein", sa.String(20), nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("phones", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("emails", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Locations table
    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("zip_code", sa.String(10), nullable=False),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column(
            "service_area", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"
        ),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_locations_state", "locations", ["state"])

    # Sources table
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("source_type", sa.String(20), nullable=False, server_default="scrape"),
        sa.Column("tier", sa.Integer, nullable=False, server_default="3"),
        sa.Column("frequency", sa.String(20), nullable=False, server_default="weekly"),
        sa.Column("selectors", postgresql.JSON, nullable=True),
        sa.Column("last_run", sa.DateTime, nullable=True),
        sa.Column("last_success", sa.DateTime, nullable=True),
        sa.Column("health_status", sa.String(20), nullable=False, server_default="healthy"),
        sa.Column("error_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Resources table
    op.create_table(
        "resources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "location_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("locations.id"),
            nullable=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("eligibility", sa.Text, nullable=True),
        sa.Column("how_to_apply", sa.Text, nullable=True),
        sa.Column(
            "categories", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"
        ),
        sa.Column(
            "subcategories", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"
        ),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("scope", sa.String(20), nullable=False, server_default="national"),
        sa.Column("states", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("hours", sa.String(255), nullable=True),
        sa.Column(
            "languages",
            postgresql.ARRAY(sa.String),
            nullable=False,
            server_default='{"en"}',
        ),
        sa.Column("cost", sa.String(100), nullable=True),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id"),
            nullable=True,
        ),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("last_scraped", sa.DateTime, nullable=True),
        sa.Column("last_verified", sa.DateTime, nullable=True),
        sa.Column("freshness_score", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("reliability_score", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_resources_status", "resources", ["status"])
    op.create_index("ix_resources_categories", "resources", ["categories"], postgresql_using="gin")

    # Source records table
    op.create_table(
        "source_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "resource_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resources.id"),
            nullable=False,
        ),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id"),
            nullable=False,
        ),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("fetched_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("raw_hash", sa.String(64), nullable=False),
        sa.Column("raw_path", sa.String(500), nullable=True),
        sa.Column("extracted_text", sa.Text, nullable=True),
    )

    # Review states table
    op.create_table(
        "review_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "resource_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resources.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("reviewer", sa.String(100), nullable=True),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_review_states_status", "review_states", ["status"])

    # Change logs table
    op.create_table(
        "change_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "resource_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resources.id"),
            nullable=False,
        ),
        sa.Column("field", sa.String(100), nullable=False),
        sa.Column("old_value", sa.Text, nullable=True),
        sa.Column("new_value", sa.Text, nullable=True),
        sa.Column("change_type", sa.String(20), nullable=False, server_default="update"),
        sa.Column("timestamp", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_change_logs_resource_id", "change_logs", ["resource_id"])


def downgrade() -> None:
    op.drop_table("change_logs")
    op.drop_table("review_states")
    op.drop_table("source_records")
    op.drop_table("resources")
    op.drop_table("sources")
    op.drop_table("locations")
    op.drop_table("organizations")
    op.execute("DROP EXTENSION IF EXISTS vector")
