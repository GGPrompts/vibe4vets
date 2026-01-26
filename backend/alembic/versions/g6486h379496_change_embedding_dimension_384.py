"""change embedding dimension to 384 for local SentenceTransformers model

Revision ID: g6486h379496
Revises: f5375g268385
Create Date: 2026-01-26 18:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "g6486h379496"
down_revision: str | Sequence[str] | None = "e48b646fd9f4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# New dimension for SentenceTransformers all-MiniLM-L6-v2
NEW_DIMENSION = 384
OLD_DIMENSION = 1536


def upgrade() -> None:
    """Change embedding column from 1536 to 384 dimensions.

    NOTE: This clears all existing embeddings since dimensions must match.
    Run the embeddings job after migration to regenerate.
    """
    # Drop the existing index
    op.execute("DROP INDEX IF EXISTS ix_resources_embedding_hnsw")

    # Clear existing embeddings (dimensions won't match)
    op.execute("UPDATE resources SET embedding = NULL")

    # Drop and recreate column with new dimension
    op.execute("ALTER TABLE resources DROP COLUMN IF EXISTS embedding")
    op.execute(
        f"""
        ALTER TABLE resources
        ADD COLUMN embedding vector({NEW_DIMENSION})
        """
    )

    # Recreate HNSW index with new dimension
    op.execute(
        """
        CREATE INDEX ix_resources_embedding_hnsw
        ON resources
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )


def downgrade() -> None:
    """Revert to 1536 dimensions (OpenAI)."""
    op.execute("DROP INDEX IF EXISTS ix_resources_embedding_hnsw")
    op.execute("UPDATE resources SET embedding = NULL")
    op.execute("ALTER TABLE resources DROP COLUMN IF EXISTS embedding")
    op.execute(
        f"""
        ALTER TABLE resources
        ADD COLUMN embedding vector({OLD_DIMENSION})
        """
    )
    op.execute(
        """
        CREATE INDEX ix_resources_embedding_hnsw
        ON resources
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )
