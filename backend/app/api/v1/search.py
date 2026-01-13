"""Search endpoints."""

from fastapi import APIRouter

from app.database import SessionDep

router = APIRouter()


@router.get("")
def search_resources(
    session: SessionDep,
    q: str,
    category: str | None = None,
    state: str | None = None,
    limit: int = 20,
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
def semantic_search(
    session: SessionDep,
    query: str,
    limit: int = 10,
) -> dict:
    """Semantic search using embeddings (Phase 3)."""
    # TODO: Implement with pgvector
    return {"query": query, "results": [], "total": 0}
