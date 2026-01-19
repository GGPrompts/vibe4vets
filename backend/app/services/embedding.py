"""Embedding service for generating vector embeddings.

Supports OpenAI text-embedding-3-small for high-quality embeddings.
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx

from app.config import settings
from app.models.resource import EMBEDDING_DIMENSION

if TYPE_CHECKING:
    from app.models import Resource

logger = logging.getLogger(__name__)

# OpenAI embedding model
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"


@dataclass
class EmbeddingResult:
    """Result of embedding generation."""

    embedding: list[float]
    model: str
    tokens_used: int


class EmbeddingService:
    """Service for generating embeddings using OpenAI API."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the embedding service.

        Args:
            api_key: OpenAI API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not configured. Set it in .env or pass api_key parameter."
            )

    def _prepare_text(self, resource: "Resource") -> str:
        """Prepare resource text for embedding.

        Combines relevant fields into a single text for embedding.
        """
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

        # Join with newlines for structure
        return "\n".join(parts)

    def generate_embedding(self, text: str) -> EmbeddingResult:
        """Generate an embedding for the given text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.

        Raises:
            ValueError: If the API call fails.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "input": text,
            "model": OPENAI_EMBEDDING_MODEL,
            "dimensions": EMBEDDING_DIMENSION,
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
        """Generate an embedding for a resource.

        Args:
            resource: The resource to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        text = self._prepare_text(resource)
        return self.generate_embedding(text)

    def generate_batch_embeddings(
        self, texts: list[str], batch_size: int = 100
    ) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.
            batch_size: Number of texts per API call (max 2048).

        Returns:
            List of EmbeddingResult objects.
        """
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
                "dimensions": EMBEDDING_DIMENSION,
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


def get_embedding_service() -> EmbeddingService:
    """Factory function to create an embedding service.

    Returns:
        Configured EmbeddingService instance.

    Raises:
        ValueError: If OPENAI_API_KEY is not configured.
    """
    return EmbeddingService()
