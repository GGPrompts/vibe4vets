"""AI Chat endpoints for veteran resource assistance.

Provides a conversational interface to help veterans find resources.
Uses Claude for natural language understanding and grounded responses
based on the resource database.
"""

import logging
import time
import uuid
from collections import defaultdict
from threading import Lock

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.database import SessionDep
from app.services.search import SearchService
from llm.client import ClaudeClient, ClaudeModel

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple in-memory rate limiting
# In production, use Redis or similar
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_rate_limit_lock = Lock()
RATE_LIMIT_REQUESTS = 10  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds

# In-memory conversation history (limited size)
# In production, use Redis or database
_conversation_store: dict[str, list[dict]] = {}
_conversation_lock = Lock()
MAX_CONVERSATION_HISTORY = 10  # messages per conversation
MAX_CONVERSATIONS = 1000  # total conversations cached


def _check_rate_limit(client_id: str) -> bool:
    """Check if client has exceeded rate limit.

    Returns True if request is allowed, False if rate limited.
    """
    now = time.time()
    with _rate_limit_lock:
        # Clean old entries
        _rate_limit_store[client_id] = [
            ts for ts in _rate_limit_store[client_id] if now - ts < RATE_LIMIT_WINDOW
        ]
        # Check limit
        if len(_rate_limit_store[client_id]) >= RATE_LIMIT_REQUESTS:
            return False
        # Add current request
        _rate_limit_store[client_id].append(now)
        return True


def _get_conversation(conversation_id: str) -> list[dict]:
    """Get conversation history."""
    with _conversation_lock:
        return _conversation_store.get(conversation_id, []).copy()


def _add_to_conversation(conversation_id: str, role: str, content: str) -> None:
    """Add message to conversation history."""
    with _conversation_lock:
        # Evict oldest conversations if at capacity
        if conversation_id not in _conversation_store and len(_conversation_store) >= MAX_CONVERSATIONS:
            oldest = next(iter(_conversation_store))
            del _conversation_store[oldest]

        if conversation_id not in _conversation_store:
            _conversation_store[conversation_id] = []

        _conversation_store[conversation_id].append({"role": role, "content": content})

        # Trim to max history
        if len(_conversation_store[conversation_id]) > MAX_CONVERSATION_HISTORY:
            _conversation_store[conversation_id] = _conversation_store[conversation_id][
                -MAX_CONVERSATION_HISTORY:
            ]


class ChatMessage(BaseModel):
    """Chat message from user."""

    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = None
    client_id: str | None = Field(
        None, description="Client identifier for rate limiting. If not provided, uses conversation_id."
    )


class ResourceReference(BaseModel):
    """Reference to a resource included in chat response."""

    id: int
    title: str
    url: str | None = None
    phone: str | None = None
    category: str


class ChatResponse(BaseModel):
    """Chat response with resources."""

    response: str
    resources: list[ResourceReference]
    conversation_id: str


SYSTEM_PROMPT = """You are a helpful assistant for Vibe4Vets, a veteran resource directory.
Your role is to help veterans, their families, and case managers find relevant resources.

Guidelines:
- Be warm, respectful, and understanding of veterans' needs
- Provide clear, actionable information
- Always mention specific resources from the database when relevant
- If you mention a resource, include its key contact info (phone, website)
- Be honest if you don't have relevant resources - suggest they broaden their search
- Never provide medical, legal, or financial advice - refer to appropriate professionals
- Keep responses concise but helpful

You have access to a database of veteran resources covering:
- Employment: Job placement, career counseling, resume help
- Training: Vocational programs, certifications, education benefits
- Housing: HUD-VASH, SSVF, transitional housing, emergency shelter
- Legal: VA appeals, discharge upgrades, legal aid

When resources are found, they will be provided to you. Reference them naturally in your response."""


@router.post("", response_model=ChatResponse)
async def chat(message: ChatMessage, session: SessionDep) -> ChatResponse:
    """Chat with AI assistant about veteran resources.

    Rate limited to 10 requests per minute per client.
    Maintains conversation history for context.
    Searches the resource database to provide grounded responses.
    """
    # Rate limiting
    client_id = message.client_id or message.conversation_id or "anonymous"
    if not _check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before sending more messages.",
        )

    # Check API key
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="Chat service is not configured. Please contact support.",
        )

    # Get or create conversation
    conversation_id = message.conversation_id or str(uuid.uuid4())
    history = _get_conversation(conversation_id)

    # Search for relevant resources based on the user's message
    search_service = SearchService(session)
    resources: list[ResourceReference] = []

    try:
        # Search resources to ground the response
        results, _ = search_service.search(
            query=message.message,
            limit=5,
        )

        for result in results:
            r = result.resource
            resources.append(
                ResourceReference(
                    id=r.id,
                    title=r.title,
                    url=r.website,
                    phone=r.phone,
                    category=r.categories[0] if r.categories else "general",
                )
            )
    except Exception as e:
        logger.warning(f"Resource search failed: {e}")
        # Continue without resources - Claude can still help

    # Build context for Claude
    resource_context = ""
    if resources:
        resource_context = "\n\n<available_resources>\n"
        for r in resources:
            contact = r.phone or r.url or "Contact info not available"
            resource_context += f"- {r.title} ({r.category}): {contact}\n"
        resource_context += "</available_resources>\n"

    # Build conversation for Claude
    user_content = message.message
    if resource_context:
        user_content = f"{message.message}\n{resource_context}"

    # Add history context
    history_context = ""
    if history:
        history_context = "\n\n<conversation_history>\n"
        for msg in history[-6:]:  # Last 6 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            history_context += f"{role}: {msg['content'][:500]}\n"
        history_context += "</conversation_history>\n"

    full_prompt = f"{history_context}{user_content}" if history_context else user_content

    try:
        claude = ClaudeClient()
        response = claude.complete(
            prompt=full_prompt,
            system=SYSTEM_PROMPT,
            model=ClaudeModel.HAIKU,  # Fast and cost-effective for chat
            max_tokens=1024,
            temperature=0.7,  # Some creativity for natural conversation
        )
        assistant_response = response.content
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Chat service temporarily unavailable. Please try again.",
        ) from e

    # Store conversation
    _add_to_conversation(conversation_id, "user", message.message)
    _add_to_conversation(conversation_id, "assistant", assistant_response)

    return ChatResponse(
        response=assistant_response,
        resources=resources,
        conversation_id=conversation_id,
    )
