"""initial schema

Revision ID: d71df951e5d9
Revises:
Create Date: 2026-01-13 02:25:57.618870

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d71df951e5d9"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial schema with full-text search support."""
    # Organizations table
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("ein", sa.String(20), nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("phones", postgresql.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("emails", postgresql.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_organizations_name", "organizations", ["name"])

    # Locations table
    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("zip_code", sa.String(10), nullable=False),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("service_area", postgresql.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_locations_state", "locations", ["state"])
    op.create_index("ix_locations_city", "locations", ["city"])
    op.create_index("ix_locations_organization_id", "locations", ["organization_id"])

    # Sources table
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("source_type", sa.String(20), nullable=False, server_default="scrape"),
        sa.Column("tier", sa.Integer, nullable=False, server_default="3"),
        sa.Column("frequency", sa.String(20), nullable=False, server_default="weekly"),
        sa.Column("selectors", postgresql.JSONB, nullable=True),
        sa.Column("last_run", sa.DateTime, nullable=True),
        sa.Column("last_success", sa.DateTime, nullable=True),
        sa.Column("health_status", sa.String(20), nullable=False, server_default="healthy"),
        sa.Column("error_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sources_tier", "sources", ["tier"])
    op.create_index("ix_sources_health_status", "sources", ["health_status"])

    # Resources table - main entity
    op.create_table(
        "resources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "location_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("locations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Content
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("eligibility", sa.Text, nullable=True),
        sa.Column("how_to_apply", sa.Text, nullable=True),
        # Classification
        sa.Column("categories", postgresql.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("subcategories", postgresql.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("tags", postgresql.ARRAY(sa.Text), nullable=False, server_default="{}"),
        # Scope
        sa.Column("scope", sa.String(20), nullable=False, server_default="national"),
        sa.Column("states", postgresql.ARRAY(sa.Text), nullable=False, server_default="{}"),
        # Contact
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("hours", sa.String(255), nullable=True),
        sa.Column("languages", postgresql.ARRAY(sa.Text), nullable=False, server_default='{"en"}'),
        sa.Column("cost", sa.String(100), nullable=True),
        # Trust signals
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("last_scraped", sa.DateTime, nullable=True),
        sa.Column("last_verified", sa.DateTime, nullable=True),
        sa.Column("freshness_score", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("reliability_score", sa.Float, nullable=False, server_default="0.5"),
        # State
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Full-text search vector
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR,
            sa.Computed(
                "to_tsvector('english', coalesce(title, '') || ' ' || "
                "coalesce(description, '') || ' ' || coalesce(summary, ''))",
                persisted=True,
            ),
        ),
    )

    # Indexes for resources
    op.create_index("ix_resources_organization_id", "resources", ["organization_id"])
    op.create_index("ix_resources_location_id", "resources", ["location_id"])
    op.create_index("ix_resources_source_id", "resources", ["source_id"])
    op.create_index("ix_resources_status", "resources", ["status"])
    op.create_index("ix_resources_scope", "resources", ["scope"])
    op.create_index("ix_resources_freshness_score", "resources", ["freshness_score"])
    op.create_index("ix_resources_reliability_score", "resources", ["reliability_score"])

    # GIN indexes for array fields and full-text search
    op.create_index(
        "ix_resources_categories_gin",
        "resources",
        ["categories"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_resources_states_gin",
        "resources",
        ["states"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_resources_tags_gin",
        "resources",
        ["tags"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_resources_search_vector_gin",
        "resources",
        ["search_vector"],
        postgresql_using="gin",
    )

    # Source records table - audit trail
    op.create_table(
        "source_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "resource_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("fetched_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("raw_hash", sa.String(64), nullable=False),
        sa.Column("raw_path", sa.String(500), nullable=True),
        sa.Column("extracted_text", sa.Text, nullable=True),
    )
    op.create_index("ix_source_records_resource_id", "source_records", ["resource_id"])
    op.create_index("ix_source_records_source_id", "source_records", ["source_id"])
    op.create_index("ix_source_records_raw_hash", "source_records", ["raw_hash"])

    # Review states table
    op.create_table(
        "review_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "resource_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("reviewer", sa.String(100), nullable=True),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_review_states_resource_id", "review_states", ["resource_id"])
    op.create_index("ix_review_states_status", "review_states", ["status"])

    # Change logs table
    op.create_table(
        "change_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "resource_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("field", sa.String(100), nullable=False),
        sa.Column("old_value", sa.Text, nullable=True),
        sa.Column("new_value", sa.Text, nullable=True),
        sa.Column("change_type", sa.String(20), nullable=False, server_default="update"),
        sa.Column("timestamp", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_change_logs_resource_id", "change_logs", ["resource_id"])
    op.create_index("ix_change_logs_field", "change_logs", ["field"])
    op.create_index("ix_change_logs_timestamp", "change_logs", ["timestamp"])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("change_logs")
    op.drop_table("review_states")
    op.drop_table("source_records")
    op.drop_table("resources")
    op.drop_table("sources")
    op.drop_table("locations")
    op.drop_table("organizations")
