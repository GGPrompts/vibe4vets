"""Tests for the AI chat endpoint."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import chat as chat_module


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Reset rate limiting state between tests."""
    chat_module._rate_limit_store.clear()
    chat_module._conversation_store.clear()
    yield
    chat_module._rate_limit_store.clear()
    chat_module._conversation_store.clear()


def test_chat_requires_message(client: TestClient):
    """Test that chat requires a non-empty message."""
    response = client.post("/api/v1/chat", json={})
    assert response.status_code == 422  # Validation error


def test_chat_rejects_empty_message(client: TestClient):
    """Test that chat rejects empty message."""
    response = client.post("/api/v1/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_rejects_too_long_message(client: TestClient):
    """Test that chat rejects messages over 2000 characters."""
    response = client.post("/api/v1/chat", json={"message": "x" * 2001})
    assert response.status_code == 422


@patch("app.api.v1.chat.settings")
def test_chat_returns_503_without_api_key(mock_settings, client: TestClient):
    """Test that chat returns 503 when API key not configured."""
    mock_settings.anthropic_api_key = ""
    response = client.post("/api/v1/chat", json={"message": "Hello"})
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


@patch("app.api.v1.chat.ClaudeClient")
@patch("app.api.v1.chat.settings")
def test_chat_returns_response(mock_settings, mock_claude_class, client: TestClient):
    """Test that chat returns a valid response."""
    mock_settings.anthropic_api_key = "test-key"

    # Mock the Claude response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "I can help you find veteran resources."
    mock_client.complete.return_value = mock_response
    mock_claude_class.return_value = mock_client

    response = client.post("/api/v1/chat", json={"message": "I need housing help"})

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "resources" in data
    assert "conversation_id" in data
    assert data["response"] == "I can help you find veteran resources."


@patch("app.api.v1.chat.ClaudeClient")
@patch("app.api.v1.chat.settings")
def test_chat_maintains_conversation_id(mock_settings, mock_claude_class, client: TestClient):
    """Test that chat maintains conversation_id across messages."""
    mock_settings.anthropic_api_key = "test-key"

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Response"
    mock_client.complete.return_value = mock_response
    mock_claude_class.return_value = mock_client

    # First message - no conversation_id
    response1 = client.post("/api/v1/chat", json={"message": "Hello"})
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]
    assert conversation_id

    # Second message - use same conversation_id
    response2 = client.post("/api/v1/chat", json={"message": "Help me", "conversation_id": conversation_id})
    assert response2.status_code == 200
    assert response2.json()["conversation_id"] == conversation_id


@patch("app.api.v1.chat.settings")
def test_rate_limiting(mock_settings, client: TestClient):
    """Test that rate limiting works."""
    mock_settings.anthropic_api_key = ""  # Will get 503, but we test rate limit first

    # Override rate limit for faster testing
    original_limit = chat_module.RATE_LIMIT_REQUESTS
    chat_module.RATE_LIMIT_REQUESTS = 3

    try:
        # First 3 requests should work (they'll get 503 for no API key)
        for _ in range(3):
            response = client.post("/api/v1/chat", json={"message": "Test", "client_id": "test-client"})
            # Either 503 (no API key) or 200 is fine, we're testing rate limit
            assert response.status_code in [200, 503]

        # Fourth request should be rate limited
        response = client.post("/api/v1/chat", json={"message": "Test", "client_id": "test-client"})
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
    finally:
        chat_module.RATE_LIMIT_REQUESTS = original_limit


@patch("app.api.v1.chat.ClaudeClient")
@patch("app.api.v1.chat.settings")
def test_chat_handles_claude_error(mock_settings, mock_claude_class, client: TestClient):
    """Test that chat handles Claude API errors gracefully."""
    mock_settings.anthropic_api_key = "test-key"

    mock_client = MagicMock()
    mock_client.complete.side_effect = Exception("API error")
    mock_claude_class.return_value = mock_client

    response = client.post("/api/v1/chat", json={"message": "Hello"})
    assert response.status_code == 503
    assert "temporarily unavailable" in response.json()["detail"]


def test_conversation_store_limits():
    """Test conversation store respects limits."""
    # Test MAX_CONVERSATION_HISTORY
    conversation_id = "test-conv"
    original_max = chat_module.MAX_CONVERSATION_HISTORY
    chat_module.MAX_CONVERSATION_HISTORY = 3

    try:
        for i in range(5):
            chat_module._add_to_conversation(conversation_id, "user", f"msg {i}")

        history = chat_module._get_conversation(conversation_id)
        assert len(history) == 3
        # Should have the last 3 messages
        assert history[0]["content"] == "msg 2"
        assert history[2]["content"] == "msg 4"
    finally:
        chat_module.MAX_CONVERSATION_HISTORY = original_max


def test_conversation_store_eviction():
    """Test conversation store evicts old conversations."""
    original_max = chat_module.MAX_CONVERSATIONS
    chat_module.MAX_CONVERSATIONS = 2
    chat_module._conversation_store.clear()

    try:
        # Add 3 conversations - first should be evicted
        chat_module._add_to_conversation("conv-1", "user", "msg 1")
        chat_module._add_to_conversation("conv-2", "user", "msg 2")
        chat_module._add_to_conversation("conv-3", "user", "msg 3")

        assert "conv-1" not in chat_module._conversation_store
        assert "conv-2" in chat_module._conversation_store
        assert "conv-3" in chat_module._conversation_store
    finally:
        chat_module.MAX_CONVERSATIONS = original_max
        chat_module._conversation_store.clear()
