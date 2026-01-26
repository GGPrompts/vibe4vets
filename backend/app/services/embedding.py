"""Embedding service for generating vector embeddings.

Supports:
- Local: SentenceTransformers (free, 384 dimensions)
- OpenAI: text-embedding-3-small (paid, 1536 dimensions)

Set USE_LOCAL_EMBEDDINGS=true in .env to use local model.
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.config import settings

if TYPE_CHECKING:
    from app.models import Resource

logger = logging.getLogger(__name__)

# Model configurations
LOCAL_MODEL_NAME = "all-MiniLM-L6-v2"
LOCAL_EMBEDDING_DIMENSION = 384

OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_EMBEDDING_DIMENSION = 1536
OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"


@dataclass
class EmbeddingResult:
    """Result of embedding generation."""

    embedding: list[float]
    model: str
    tokens_used: int


class LocalEmbeddingService:
    """Service for generating embeddings using local SentenceTransformers model."""

    _model = None  # Class-level cache for the model

    def __init__(self) -> None:
        """Initialize the local embedding service."""
        if LocalEmbeddingService._model is None:
            logger.info(f"Loading local embedding model: {LOCAL_MODEL_NAME}")
            from sentence_transformers import SentenceTransformer
            LocalEmbeddingService._model = SentenceTransformer(LOCAL_MODEL_NAME)
            logger.info("Local embedding model loaded")

    def _prepare_text(self, resource: "Resource") -> str:
        """Prepare resource text for embedding."""
        parts = [
            resource.title,
            resource.description,
        ]

        if resource.summary:
            parts.append(resource.summary)

        if resource.eligibility:
            parts.append(f"Eligibility: {resource.eligibility}")

        if resource.categories:
            parts.append(f"Categories: {', '.join(resource.categories)}")

        if resource.tags:
            parts.append(f"Tags: {', '.join(resource.tags)}")

        return "\n".join(parts)

    def generate_embedding(self, text: str) -> EmbeddingResult:
        """Generate an embedding for the given text."""
        embedding = LocalEmbeddingService._model.encode(text).tolist()
        return EmbeddingResult(
            embedding=embedding,
            model=LOCAL_MODEL_NAME,
            tokens_used=0,  # Local model doesn't track tokens
        )

    def generate_resource_embedding(self, resource: "Resource") -> EmbeddingResult:
        """Generate an embedding for a resource."""
        text = self._prepare_text(resource)
        return self.generate_embedding(text)

    def generate_batch_embeddings(self, texts: list[str], batch_size: int = 32) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        embeddings = LocalEmbeddingService._model.encode(texts, batch_size=batch_size)
        return [
            EmbeddingResult(
                embedding=emb.tolist(),
                model=LOCAL_MODEL_NAME,
                tokens_used=0,
            )
            for emb in embeddings
        ]


class OpenAIEmbeddingService:
    """Service for generating embeddings using OpenAI API."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the OpenAI embedding service."""
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured. Set it in .env or pass api_key parameter.")

    def _prepare_text(self, resource: "Resource") -> str:
        """Prepare resource text for embedding."""
        parts = [
            resource.title,
            resource.description,
        ]

        if resource.summary:
            parts.append(resource.summary)

        if resource.eligibility:
            parts.append(f"Eligibility: {resource.eligibility}")

        if resource.categories:
            parts.append(f"Categories: {', '.join(resource.categories)}")

        if resource.tags:
            parts.append(f"Tags: {', '.join(resource.tags)}")

        return "\n".join(parts)

    def generate_embedding(self, text: str) -> EmbeddingResult:
        """Generate an embedding for the given text."""
        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "input": text,
            "model": OPENAI_EMBEDDING_MODEL,
            "dimensions": OPENAI_EMBEDDING_DIMENSION,
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                OPENAI_EMBEDDINGS_URL,
                headers=headers,
                json=payload,
            )

            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                raise ValueError(f"OpenAI API error: {response.status_code}")

            data = response.json()

        embedding = data["data"][0]["embedding"]
        tokens_used = data["usage"]["total_tokens"]

        return EmbeddingResult(
            embedding=embedding,
            model=OPENAI_EMBEDDING_MODEL,
            tokens_used=tokens_used,
        )

    def generate_resource_embedding(self, resource: "Resource") -> EmbeddingResult:
        """Generate an embedding for a resource."""
        text = self._prepare_text(resource)
        return self.generate_embedding(text)

    def generate_batch_embeddings(self, texts: list[str], batch_size: int = 100) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        import httpx

        results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "input": batch,
                "model": OPENAI_EMBEDDING_MODEL,
                "dimensions": OPENAI_EMBEDDING_DIMENSION,
            }

            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    OPENAI_EMBEDDINGS_URL,
                    headers=headers,
                    json=payload,
                )

                if response.status_code != 200:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    raise ValueError(f"OpenAI API error: {response.status_code}")

                data = response.json()

            tokens_used = data["usage"]["total_tokens"]

            for item in data["data"]:
                results.append(
                    EmbeddingResult(
                        embedding=item["embedding"],
                        model=OPENAI_EMBEDDING_MODEL,
                        tokens_used=tokens_used // len(batch),
                    )
                )

        return results


# Type alias for either service
EmbeddingService = LocalEmbeddingService | OpenAIEmbeddingService


def get_embedding_service() -> LocalEmbeddingService | OpenAIEmbeddingService:
    """Factory function to create an embedding service.

    Uses local SentenceTransformers if USE_LOCAL_EMBEDDINGS=true,
    otherwise falls back to OpenAI API.

    Returns:
        Configured embedding service instance.
    """
    use_local = getattr(settings, 'use_local_embeddings', False)

    if use_local:
        logger.info("Using local embedding service (SentenceTransformers)")
        return LocalEmbeddingService()

    logger.info("Using OpenAI embedding service")
    return OpenAIEmbeddingService()


def get_embedding_dimension() -> int:
    """Get the embedding dimension for the configured service."""
    use_local = getattr(settings, 'use_local_embeddings', False)
    return LOCAL_EMBEDDING_DIMENSION if use_local else OPENAI_EMBEDDING_DIMENSION
