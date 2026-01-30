"""change embedding dimension to 384 for local SentenceTransformers model

Revision ID: g6486h379496
Revises: f5375g268385
Create Date: 2026-01-26 18:00:00.000000

"""

import logging
from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "g6486h379496"
down_revision: str | Sequence[str] | None = "e48b646fd9f4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# New dimension for SentenceTransformers all-MiniLM-L6-v2
NEW_DIMENSION = 384
OLD_DIMENSION = 1536

logger = logging.getLogger(__name__)


def _pgvector_available() -> bool:
    """Check if pgvector extension is available on this PostgreSQL instance."""
    conn = op.get_bind()
    result = conn.execute(text("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'"))
    return result.scalar() is not None


def _embedding_column_exists() -> bool:
    """Check if the embedding column exists on resources table."""
    conn = op.get_bind()
    result = conn.execute(
        text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'resources' AND column_name = 'embedding'
        """)
    )
    return result.scalar() is not None


def upgrade() -> None:
    """Change embedding column from 1536 to 384 dimensions.

    NOTE: This clears all existing embeddings since dimensions must match.
    Run the embeddings job after migration to regenerate.
    Skips gracefully if pgvector is not available.
    """
    if not _pgvector_available():
        logger.warning("pgvector extension not available. Skipping embedding dimension change.")
        return

    if not _embedding_column_exists():
        logger.warning(
            "embedding column does not exist (pgvector was likely unavailable when "
            "original migration ran). Skipping dimension change."
        )
        return

    # Drop the existing index
    op.execute(text("DROP INDEX IF EXISTS ix_resources_embedding_hnsw"))

    # Clear existing embeddings (dimensions won't match)
    op.execute(text("UPDATE resources SET embedding = NULL"))

    # Drop and recreate column with new dimension
    op.execute(text("ALTER TABLE resources DROP COLUMN IF EXISTS embedding"))
    op.execute(
        text(f"""
        ALTER TABLE resources
        ADD COLUMN embedding vector({NEW_DIMENSION})
        """)
    )

    # Recreate HNSW index with new dimension
    op.execute(
        text("""
        CREATE INDEX ix_resources_embedding_hnsw
        ON resources
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """)
    )


def downgrade() -> None:
    """Revert to 1536 dimensions (OpenAI)."""
    if not _pgvector_available() or not _embedding_column_exists():
        return

    op.execute(text("DROP INDEX IF EXISTS ix_resources_embedding_hnsw"))
    op.execute(text("UPDATE resources SET embedding = NULL"))
    op.execute(text("ALTER TABLE resources DROP COLUMN IF EXISTS embedding"))
    op.execute(
        text(f"""
        ALTER TABLE resources
        ADD COLUMN embedding vector({OLD_DIMENSION})
        """)
    )
    op.execute(
        text("""
        CREATE INDEX ix_resources_embedding_hnsw
        ON resources
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """)
    )
