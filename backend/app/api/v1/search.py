"""Search endpoints with full-text search."""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.database import SessionDep
from app.schemas.resource import ResourceSearchResult
from app.services.search import SearchService

router = APIRouter()


class SearchResponse(BaseModel):
    """Response for search endpoint."""

    query: str
    results: list[ResourceSearchResult]
    total: int
    limit: int
    offset: int


@router.get("", response_model=SearchResponse)
def search_resources(
    session: SessionDep,
    q: str = Query(..., min_length=1, description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
    state: str | None = Query(None, description="Filter by state (2-letter code)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> SearchResponse:
    """Search resources using PostgreSQL full-text search.

    Returns resources matching the query with 'Why this matched' explanations.
    Results are ranked by relevance and reliability score.
    """
    service = SearchService(session)
    results, total = service.search(
        query=q,
        category=category,
        state=state,
        limit=limit,
        offset=offset,
    )

    return SearchResponse(
        query=q,
        results=results,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/semantic")
def semantic_search(
    session: SessionDep,
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
) -> dict:
    """Semantic search using embeddings (Phase 3).

    This endpoint is a placeholder for future pgvector-based semantic search.
    """
    return {
        "query": query,
        "results": [],
        "total": 0,
        "message": "Semantic search will be available in Phase 3",
    }
