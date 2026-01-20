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
        _rate_limit_store[client_id] = [ts for ts in _rate_limit_store[client_id] if now - ts < RATE_LIMIT_WINDOW]
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
        is_new = conversation_id not in _conversation_store
        if is_new and len(_conversation_store) >= MAX_CONVERSATIONS:
            oldest = next(iter(_conversation_store))
            del _conversation_store[oldest]

        if conversation_id not in _conversation_store:
            _conversation_store[conversation_id] = []

        _conversation_store[conversation_id].append({"role": role, "content": content})

        # Trim to max history
        if len(_conversation_store[conversation_id]) > MAX_CONVERSATION_HISTORY:
            _conversation_store[conversation_id] = _conversation_store[conversation_id][-MAX_CONVERSATION_HISTORY:]


class ChatMessage(BaseModel):
    """Chat message from user."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's message to the AI assistant",
        json_schema_extra={"example": "I'm a veteran looking for housing assistance in Virginia"},
    )
    conversation_id: str | None = Field(
        None,
        description="Optional ID to continue an existing conversation. Omit for new conversations.",
    )
    client_id: str | None = Field(
        None,
        description=("Optional client identifier for rate limiting. Uses conversation_id if not provided."),
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "What housing programs are available for homeless veterans?",
                "conversation_id": None,
                "client_id": None,
            }
        }
    }


class ResourceReference(BaseModel):
    """Reference to a resource included in chat response."""

    id: int = Field(..., description="Resource database ID")
    title: str = Field(..., description="Resource title")
    url: str | None = Field(None, description="Resource website URL")
    phone: str | None = Field(None, description="Contact phone number")
    category: str = Field(..., description="Resource category")


class ChatResponse(BaseModel):
    """Chat response with resources."""

    response: str = Field(..., description="AI assistant's response text")
    resources: list[ResourceReference] = Field(..., description="Resources referenced in the response")
    conversation_id: str = Field(..., description="Conversation ID for follow-up messages")

    model_config = {
        "json_schema_extra": {
            "example": {
                "response": "There are several housing programs available for homeless veterans...",
                "resources": [
                    {
                        "id": 1,
                        "title": "HUD-VASH Housing Program",
                        "url": "https://www.va.gov/homeless/hud-vash.asp",
                        "phone": "1-877-4AID-VET",
                        "category": "housing",
                    }
                ],
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    }


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

When resources are found, they will be provided to you. \
Reference them naturally in your response."""


@router.post(
    "",
    response_model=ChatResponse,
    summary="Chat with AI assistant",
    response_description="AI response with relevant resource references",
    responses={
        200: {
            "description": "Successful chat response",
        },
        429: {
            "description": "Rate limit exceeded (10 requests/minute)",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded. Please wait before sending more messages."}
                }
            },
        },
        503: {
            "description": "Chat service not configured or temporarily unavailable",
            "content": {
                "application/json": {"example": {"detail": "Chat service is not configured. Please contact support."}}
            },
        },
    },
)
async def chat(message: ChatMessage, session: SessionDep) -> ChatResponse:
    """Chat with the AI assistant about veteran resources.

    The assistant uses Claude (Haiku model) to provide helpful, grounded responses
    based on resources in our database.

    **Features:**
    - Natural conversation about veteran resources
    - Automatic resource search based on your question
    - Conversation history maintained for context
    - Rate limited to 10 requests per minute per client

    **How it works:**
    1. Your message is searched against the resource database
    2. Relevant resources are provided to the AI as context
    3. The AI generates a helpful response referencing specific resources
    4. Resource contact info (phone, website) is included when available

    **Continuing conversations:**
    Save the `conversation_id` from the response and include it in follow-up
    messages to maintain context.

    **Rate limiting:**
    Limited to 10 requests per minute. Use `client_id` to identify your
    application if not using conversation tracking.
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
