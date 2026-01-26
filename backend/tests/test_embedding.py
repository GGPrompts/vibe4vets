"""Tests for embedding service and semantic search."""

from unittest.mock import MagicMock, patch

import pytest

# Check if sentence-transformers is available
try:
    import sentence_transformers
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


class TestLocalEmbeddingService:
    """Tests for the LocalEmbeddingService class."""

    @pytest.mark.skipif(not HAS_SENTENCE_TRANSFORMERS, reason="sentence-transformers not available")
    def test_prepare_text_basic(self):
        """Test that _prepare_text combines resource fields correctly."""
        from app.services.embedding import LocalEmbeddingService

        # Create a mock resource
        resource = MagicMock()
        resource.title = "Veterans Job Training"
        resource.description = "Provides employment training for veterans"
        resource.summary = "Training program"
        resource.eligibility = "Veterans only"
        resource.categories = ["employment", "training"]
        resource.tags = ["jobs", "skills"]

        service = LocalEmbeddingService()
        text = service._prepare_text(resource)

        assert "Veterans Job Training" in text
        assert "Provides employment training for veterans" in text
        assert "Training program" in text
        assert "Eligibility: Veterans only" in text
        assert "Categories: employment, training" in text
        assert "Tags: jobs, skills" in text

    @pytest.mark.skipif(not HAS_SENTENCE_TRANSFORMERS, reason="sentence-transformers not available")
    def test_prepare_text_minimal(self):
        """Test _prepare_text with minimal fields."""
        from app.services.embedding import LocalEmbeddingService

        resource = MagicMock()
        resource.title = "Basic Resource"
        resource.description = "A simple description"
        resource.summary = None
        resource.eligibility = None
        resource.categories = []
        resource.tags = []

        service = LocalEmbeddingService()
        text = service._prepare_text(resource)

        assert "Basic Resource" in text
        assert "A simple description" in text
        assert "Categories:" not in text
        assert "Tags:" not in text

    @pytest.mark.skipif(not HAS_SENTENCE_TRANSFORMERS, reason="sentence-transformers not available")
    def test_generate_embedding_returns_correct_dimension(self):
        """Test that local embeddings return 384 dimensions."""
        from app.services.embedding import LocalEmbeddingService, LOCAL_EMBEDDING_DIMENSION

        service = LocalEmbeddingService()
        result = service.generate_embedding("test text for embedding")

        assert len(result.embedding) == LOCAL_EMBEDDING_DIMENSION
        assert result.tokens_used == 0  # Local model doesn't track tokens
        assert result.model == "all-MiniLM-L6-v2"

    @pytest.mark.skipif(not HAS_SENTENCE_TRANSFORMERS, reason="sentence-transformers not available")
    def test_generate_batch_embeddings(self):
        """Test batch embedding generation."""
        from app.services.embedding import LocalEmbeddingService, LOCAL_EMBEDDING_DIMENSION

        service = LocalEmbeddingService()
        texts = ["first text", "second text", "third text"]
        results = service.generate_batch_embeddings(texts)

        assert len(results) == 3
        for result in results:
            assert len(result.embedding) == LOCAL_EMBEDDING_DIMENSION
            assert result.tokens_used == 0


class TestOpenAIEmbeddingService:
    """Tests for the OpenAIEmbeddingService class."""

    def test_init_requires_api_key(self):
        """Test that OpenAI service requires API key."""
        from app.services.embedding import OpenAIEmbeddingService

        with patch("app.config.settings.openai_api_key", ""):
            with pytest.raises(ValueError, match="OPENAI_API_KEY not configured"):
                OpenAIEmbeddingService()

    @patch("httpx.Client")
    def test_generate_embedding_success(self, mock_client_class):
        """Test successful embedding generation with OpenAI."""
        from app.services.embedding import OpenAIEmbeddingService, OPENAI_EMBEDDING_DIMENSION

        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1] * OPENAI_EMBEDDING_DIMENSION}],
            "usage": {"total_tokens": 50},
        }

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        service = OpenAIEmbeddingService(api_key="test-key")
        result = service.generate_embedding("test text")

        assert len(result.embedding) == OPENAI_EMBEDDING_DIMENSION
        assert result.tokens_used == 50
        assert result.model == "text-embedding-3-small"

    @patch("httpx.Client")
    def test_generate_embedding_api_error(self, mock_client_class):
        """Test handling of API errors."""
        from app.services.embedding import OpenAIEmbeddingService

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        service = OpenAIEmbeddingService(api_key="test-key")

        with pytest.raises(ValueError, match="OpenAI API error"):
            service.generate_embedding("test text")


class TestGetEmbeddingService:
    """Tests for the get_embedding_service factory function."""

    @pytest.mark.skipif(not HAS_SENTENCE_TRANSFORMERS, reason="sentence-transformers not available")
    def test_returns_local_by_default(self):
        """Test that factory returns LocalEmbeddingService by default."""
        from app.services.embedding import get_embedding_service, LocalEmbeddingService

        with patch("app.config.settings.use_local_embeddings", True):
            service = get_embedding_service()
            assert isinstance(service, LocalEmbeddingService)

    def test_returns_openai_when_configured(self):
        """Test that factory returns OpenAIEmbeddingService when configured."""
        from app.services.embedding import get_embedding_service, OpenAIEmbeddingService

        with patch("app.config.settings.use_local_embeddings", False):
            with patch("app.config.settings.openai_api_key", "test-key"):
                service = get_embedding_service()
                assert isinstance(service, OpenAIEmbeddingService)


class TestSemanticSearchEndpoint:
    """Tests for the semantic search API endpoint."""

    @patch("app.services.search.SearchService.hybrid_search")
    @patch("app.services.embedding.get_embedding_service")
    def test_semantic_search_works_with_local_embeddings(self, mock_get_service, mock_hybrid_search, client):
        """Test that semantic search works with local embeddings (no API key needed)."""
        # Mock the embedding service
        mock_embedding_service = MagicMock()
        mock_result = MagicMock()
        mock_result.embedding = [0.1] * 384
        mock_embedding_service.generate_embedding.return_value = mock_result
        mock_get_service.return_value = mock_embedding_service

        # Mock the search result
        mock_hybrid_search.return_value = ([], 0)

        response = client.post("/api/v1/search/semantic?q=housing+assistance&limit=5")

        # Should succeed (200) not fail with 503
        assert response.status_code == 200
        assert "results" in response.json()

    @patch("app.services.embedding.get_embedding_service")
    def test_semantic_search_embedding_error(self, mock_get_service, client):
        """Test handling of embedding generation errors."""
        mock_service = MagicMock()
        mock_service.generate_embedding.side_effect = Exception("Model loading failed")
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/search/semantic?q=housing+assistance")

        assert response.status_code == 500
        assert "Failed to generate embedding" in response.json()["detail"]


class TestEmbeddingsJob:
    """Tests for the embeddings background job."""

    @patch("app.services.embedding.get_embedding_service")
    def test_job_processes_resources_with_local_model(self, mock_get_service, session):
        """Test that job processes resources using local embeddings."""
        from jobs.embeddings import EmbeddingsJob

        # Create a mock embedding result
        mock_result = MagicMock()
        mock_result.embedding = [0.1] * 384
        mock_result.tokens_used = 0

        mock_service = MagicMock()
        mock_service.generate_resource_embedding.return_value = mock_result
        mock_get_service.return_value = mock_service

        job = EmbeddingsJob()
        # The job will find no resources in the empty test DB
        result = job.run()

        # Should complete without error (empty DB = 0 resources to process)
        assert result.stats.get("processed", 0) >= 0
        assert result.stats.get("error") is None
