"""add embedding column for pgvector semantic search

Revision ID: c5f9e3g2h890
Revises: b4e9d2f1g789
Create Date: 2026-01-18 19:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5f9e3g2h890"
down_revision: str | Sequence[str] | None = "b4e9d2f1g789"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Embedding dimension (matches text-embedding-3-small or Claude embeddings)
EMBEDDING_DIMENSION = 1536


def upgrade() -> None:
    """Add embedding column for semantic search with pgvector."""
    # Enable pgvector extension if not exists
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add embedding column using raw SQL for vector type
    op.execute(
        f"""
        ALTER TABLE resources
        ADD COLUMN embedding vector({EMBEDDING_DIMENSION})
        """
    )

    # Create HNSW index for approximate nearest neighbor search
    # HNSW is faster for search but slower to build than IVFFlat
    op.execute(
        """
        CREATE INDEX ix_resources_embedding_hnsw
        ON resources
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )


def downgrade() -> None:
    """Remove embedding column and index."""
    op.execute("DROP INDEX IF EXISTS ix_resources_embedding_hnsw")
    op.execute("ALTER TABLE resources DROP COLUMN IF EXISTS embedding")
