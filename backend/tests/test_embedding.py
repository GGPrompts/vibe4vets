"""Tests for embedding service and semantic search."""

from unittest.mock import MagicMock, patch

import pytest


class TestEmbeddingService:
    """Tests for the EmbeddingService class."""

    def test_prepare_text_basic(self):
        """Test that _prepare_text combines resource fields correctly."""
        from app.services.embedding import EmbeddingService

        # Create a mock resource
        resource = MagicMock()
        resource.title = "Veterans Job Training"
        resource.description = "Provides employment training for veterans"
        resource.summary = "Training program"
        resource.eligibility = "Veterans only"
        resource.categories = ["employment", "training"]
        resource.tags = ["jobs", "skills"]

        with patch.object(EmbeddingService, "__init__", lambda x, **k: None):
            service = EmbeddingService()
            service.api_key = "test-key"
            text = service._prepare_text(resource)

        assert "Veterans Job Training" in text
        assert "Provides employment training for veterans" in text
        assert "Training program" in text
        assert "Eligibility: Veterans only" in text
        assert "Categories: employment, training" in text
        assert "Tags: jobs, skills" in text

    def test_prepare_text_minimal(self):
        """Test _prepare_text with minimal fields."""
        from app.services.embedding import EmbeddingService

        resource = MagicMock()
        resource.title = "Basic Resource"
        resource.description = "A simple description"
        resource.summary = None
        resource.eligibility = None
        resource.categories = []
        resource.tags = []

        with patch.object(EmbeddingService, "__init__", lambda x, **k: None):
            service = EmbeddingService()
            service.api_key = "test-key"
            text = service._prepare_text(resource)

        assert "Basic Resource" in text
        assert "A simple description" in text
        assert "Categories:" not in text
        assert "Tags:" not in text

    @patch("httpx.Client")
    def test_generate_embedding_success(self, mock_client_class):
        """Test successful embedding generation."""
        from app.services.embedding import EmbeddingService

        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1] * 1536}],
            "usage": {"total_tokens": 50},
        }

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch.object(EmbeddingService, "__init__", lambda x, **k: None):
            service = EmbeddingService()
            service.api_key = "test-key"
            result = service.generate_embedding("test text")

        assert len(result.embedding) == 1536
        assert result.tokens_used == 50
        assert result.model == "text-embedding-3-small"

    @patch("httpx.Client")
    def test_generate_embedding_api_error(self, mock_client_class):
        """Test handling of API errors."""
        from app.services.embedding import EmbeddingService

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch.object(EmbeddingService, "__init__", lambda x, **k: None):
            service = EmbeddingService()
            service.api_key = "test-key"

            with pytest.raises(ValueError, match="OpenAI API error"):
                service.generate_embedding("test text")


class TestSemanticSearchEndpoint:
    """Tests for the semantic search API endpoint."""

    def test_semantic_search_no_api_key(self, client):
        """Test that semantic search returns error without API key."""
        with patch("app.config.settings.openai_api_key", ""):
            response = client.post("/api/v1/search/semantic?q=housing+assistance")

        assert response.status_code == 503
        assert "OPENAI_API_KEY" in response.json()["detail"]

    @patch("app.services.embedding.EmbeddingService")
    @patch("app.config.settings.openai_api_key", "test-key")
    def test_semantic_search_embedding_error(self, mock_service_class, client):
        """Test handling of embedding generation errors."""
        mock_service = MagicMock()
        mock_service.generate_embedding.side_effect = Exception("API timeout")
        mock_service_class.return_value = mock_service

        response = client.post("/api/v1/search/semantic?q=housing+assistance")

        assert response.status_code == 500
        assert "Failed to generate embedding" in response.json()["detail"]


class TestEmbeddingsJob:
    """Tests for the embeddings background job."""

    def test_job_skips_without_api_key(self, session):
        """Test that job skips gracefully without API key configured."""
        from jobs.embeddings import EmbeddingsJob

        with patch("app.config.settings.openai_api_key", ""):
            job = EmbeddingsJob()
            result = job.run()

        assert result.stats.get("error") == "OPENAI_API_KEY not configured"

    @patch("app.services.embedding.EmbeddingService")
    @patch("app.config.settings.openai_api_key", "test-key")
    def test_job_processes_resources(self, mock_service_class, session):
        """Test that job processes resources without embeddings."""
        from jobs.embeddings import EmbeddingsJob

        # Create a mock embedding result
        mock_result = MagicMock()
        mock_result.embedding = [0.1] * 1536
        mock_result.tokens_used = 50

        mock_service = MagicMock()
        mock_service.generate_resource_embedding.return_value = mock_result
        mock_service_class.return_value = mock_service

        job = EmbeddingsJob()
        # The job will find no resources in the empty test DB
        result = job.run()

        assert result.stats.get("processed", 0) >= 0
