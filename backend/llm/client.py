"""Claude API client for resource discovery and validation.

Provides a simple interface to Claude models with:
- Support for different models (Haiku for high-volume, Opus for accuracy)
- JSON output parsing
- Error handling
"""

import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import anthropic

from app.config import settings


class ClaudeModel(str, Enum):
    """Claude model options."""

    # Fast and cheap - for high-volume discovery
    HAIKU = "claude-3-5-haiku-20241022"

    # Accurate and thorough - for validation
    SONNET = "claude-sonnet-4-20250514"

    # Most capable - for complex validation
    OPUS = "claude-opus-4-20250514"


@dataclass
class ClaudeResponse:
    """Response from Claude API."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str | None = None

    @property
    def json(self) -> Any:
        """Parse response as JSON.

        Attempts to extract JSON from the response, handling cases where
        the model wraps JSON in markdown code blocks.
        """
        text = self.content.strip()

        # Try to extract JSON from code blocks
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if json_match:
            text = json_match.group(1).strip()

        # Try to find JSON array or object
        if not text.startswith(("[", "{")):
            # Look for first [ or {
            array_start = text.find("[")
            object_start = text.find("{")
            if array_start >= 0 and (object_start < 0 or array_start < object_start):
                text = text[array_start:]
            elif object_start >= 0:
                text = text[object_start:]

        return json.loads(text)


class ClaudeClient:
    """Client for Claude API interactions."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the Claude client.

        Args:
            api_key: Optional API key. If not provided, uses settings.
        """
        key = api_key or settings.anthropic_api_key
        if not key:
            raise ValueError(
                "ANTHROPIC_API_KEY not configured. Set it in .env or pass api_key parameter."
            )
        self.client = anthropic.Anthropic(api_key=key)

    def complete(
        self,
        prompt: str,
        model: ClaudeModel = ClaudeModel.HAIKU,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        system: str | None = None,
    ) -> ClaudeResponse:
        """Send a prompt to Claude and get a response.

        Args:
            prompt: The user prompt to send.
            model: Which Claude model to use.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature (0.0 for deterministic).
            system: Optional system prompt.

        Returns:
            ClaudeResponse with the model's response.
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs: dict[str, Any] = {
            "model": model.value,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
        }

        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)

        # Extract text content
        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        return ClaudeResponse(
            content=content,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason,
        )

    def complete_with_template(
        self,
        template_path: str | Path,
        variables: dict[str, str],
        model: ClaudeModel = ClaudeModel.HAIKU,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> ClaudeResponse:
        """Load a prompt template, fill in variables, and get a response.

        Args:
            template_path: Path to the .md template file.
            variables: Dictionary of {{VAR}} -> value replacements.
            model: Which Claude model to use.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.

        Returns:
            ClaudeResponse with the model's response.
        """
        path = Path(template_path)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        template = path.read_text()

        # Replace variables
        prompt = template
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        return self.complete(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )


def get_claude_client() -> ClaudeClient:
    """Factory function to create a Claude client.

    Returns:
        Configured ClaudeClient instance.

    Raises:
        ValueError: If ANTHROPIC_API_KEY is not configured.
    """
    return ClaudeClient()
