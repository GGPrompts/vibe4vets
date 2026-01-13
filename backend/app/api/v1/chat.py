"""AI Chat endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message from user."""

    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    """Chat response with resources."""

    response: str
    resources: list[dict]
    conversation_id: str


@router.post("")
async def chat(message: ChatMessage) -> ChatResponse:
    """Chat with AI assistant about veteran resources."""
    # TODO: Implement with Claude API
    return ChatResponse(
        response="I'm here to help you find veteran resources. What are you looking for?",
        resources=[],
        conversation_id=message.conversation_id or "new-conversation",
    )
