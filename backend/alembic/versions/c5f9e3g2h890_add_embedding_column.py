"""add embedding column for pgvector semantic search

Revision ID: c5f9e3g2h890
Revises: b4e9d2f1g789
Create Date: 2026-01-18 19:00:00.000000

"""

import logging
from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "c5f9e3g2h890"
down_revision: str | Sequence[str] | None = "b4e9d2f1g789"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Embedding dimension (matches text-embedding-3-small or Claude embeddings)
EMBEDDING_DIMENSION = 1536

logger = logging.getLogger(__name__)


def _pgvector_available() -> bool:
    """Check if pgvector extension is available on this PostgreSQL instance."""
    conn = op.get_bind()
    result = conn.execute(
        text("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'")
    )
    return result.scalar() is not None


def upgrade() -> None:
    """Add embedding column for semantic search with pgvector.

    Skips gracefully if pgvector is not available (e.g., Railway standard Postgres).
    Semantic search functionality will be disabled but the app will still work.
    """
    if not _pgvector_available():
        logger.warning(
            "pgvector extension not available on this PostgreSQL instance. "
            "Skipping embedding column creation. Semantic search will be disabled. "
            "To enable, use a PostgreSQL provider with pgvector (Supabase, Neon, etc.)"
        )
        return

    # Enable pgvector extension if not exists
    op.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    # Add embedding column using raw SQL for vector type
    op.execute(
        text(f"""
        ALTER TABLE resources
        ADD COLUMN embedding vector({EMBEDDING_DIMENSION})
        """)
    )

    # Create HNSW index for approximate nearest neighbor search
    # HNSW is faster for search but slower to build than IVFFlat
    op.execute(
        text("""
        CREATE INDEX ix_resources_embedding_hnsw
        ON resources
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """)
    )


def downgrade() -> None:
    """Remove embedding column and index (if they exist)."""
    op.execute(text("DROP INDEX IF EXISTS ix_resources_embedding_hnsw"))
    op.execute(text("ALTER TABLE resources DROP COLUMN IF EXISTS embedding"))
