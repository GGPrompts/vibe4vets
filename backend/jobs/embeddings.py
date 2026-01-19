"""Embedding generation job for semantic search.

Generates vector embeddings for resources that don't have them yet.
Uses OpenAI's text-embedding-3-small model via the EmbeddingService.
"""

from typing import Any

from sqlmodel import Session, select

from app.models import Resource
from app.models.resource import ResourceStatus
from jobs.base import BaseJob


class EmbeddingsJob(BaseJob):
    """Job to generate embeddings for resources.

    Processes resources without embeddings in batches to avoid API rate limits.
    Can be run manually or scheduled for incremental updates.
    """

    @property
    def name(self) -> str:
        return "embeddings"

    @property
    def description(self) -> str:
        return "Generate vector embeddings for resources"

    def execute(self, session: Session, **kwargs: Any) -> dict[str, Any]:
        """Generate embeddings for resources without them.

        Args:
            session: Database session.
            **kwargs: Optional arguments:
                - batch_size: Number of resources per batch (default 50)
                - max_resources: Maximum resources to process (default None = all)

        Returns:
            Statistics dictionary with processed, failed, skipped counts.
        """
        from app.config import settings
        from app.services.embedding import EmbeddingService

        batch_size = kwargs.get("batch_size", 50)
        max_resources = kwargs.get("max_resources")

        # Check if OpenAI API key is configured
        if not settings.openai_api_key:
            self._log("OPENAI_API_KEY not configured, skipping embedding generation", "warning")
            return {"skipped": 0, "error": "OPENAI_API_KEY not configured"}

        # Get resources without embeddings
        stmt = (
            select(Resource)
            .where(Resource.status == ResourceStatus.ACTIVE)
            .where(Resource.embedding.is_(None))
            .order_by(Resource.updated_at.desc())
        )

        if max_resources:
            stmt = stmt.limit(max_resources)

        resources = session.exec(stmt).all()
        total = len(resources)

        if total == 0:
            self._log("No resources need embeddings")
            return {"processed": 0, "failed": 0, "skipped": 0, "total": 0}

        self._log(f"Found {total} resources without embeddings")

        # Initialize embedding service
        embedding_service = EmbeddingService()

        processed = 0
        failed = 0
        tokens_used = 0

        # Process in batches
        for i in range(0, total, batch_size):
            batch = resources[i : i + batch_size]
            self._log(f"Processing batch {i // batch_size + 1} ({len(batch)} resources)")

            for resource in batch:
                try:
                    # Generate embedding
                    result = embedding_service.generate_resource_embedding(resource)

                    # Update resource with embedding
                    resource.embedding = result.embedding
                    session.add(resource)

                    processed += 1
                    tokens_used += result.tokens_used

                except Exception as e:
                    self._log(f"Failed to generate embedding for {resource.id}: {e}", "error")
                    failed += 1

            # Commit batch
            session.commit()
            self._log(f"Committed batch, processed {processed}/{total}")

        return {
            "processed": processed,
            "failed": failed,
            "total": total,
            "tokens_used": tokens_used,
        }


def run_embeddings_job(batch_size: int = 50, max_resources: int | None = None) -> dict[str, Any]:
    """Convenience function to run the embeddings job.

    Args:
        batch_size: Number of resources per batch.
        max_resources: Maximum resources to process (None = all).

    Returns:
        Job result dictionary.
    """
    job = EmbeddingsJob()
    result = job.run(batch_size=batch_size, max_resources=max_resources)
    return result.to_dict()
