"""LLM abstraction layer for Vibe4Vets.

Provides a unified interface for Claude API calls with:
- Model selection (Haiku for discovery, Opus for validation)
- Prompt template rendering
- Structured JSON output parsing
- Error handling and retries
"""

from llm.client import ClaudeClient, ClaudeModel, ClaudeResponse

__all__ = [
    "ClaudeClient",
    "ClaudeModel",
    "ClaudeResponse",
]
