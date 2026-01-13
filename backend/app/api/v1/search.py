"""Search endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("")
async def search_resources(
    q: str,
    category: str | None = None,
    state: str | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> dict:
    """Search resources with full-text search."""
    # TODO: Implement full-text search
    return {
        "query": q,
        "results": [],
        "total": 0,
        "explanations": [],  # "Why this matched" data
    }


@router.post("/semantic")
async def semantic_search(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> dict:
    """Semantic search using embeddings (Phase 3)."""
    # TODO: Implement with pgvector
    return {"query": query, "results": [], "total": 0}
