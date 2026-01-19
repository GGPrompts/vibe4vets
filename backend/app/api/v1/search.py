"""Search endpoints with full-text search, eligibility filtering, and semantic search."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.database import SessionDep
from app.schemas.resource import ResourceSearchResult
from app.services.search import EligibilityFilters, SearchService

router = APIRouter()


class SearchResponse(BaseModel):
    """Response for search endpoint."""

    query: str
    results: list[ResourceSearchResult]
    total: int
    limit: int
    offset: int


class EligibilitySearchResponse(BaseModel):
    """Response for eligibility-filtered search."""

    query: str | None
    results: list[ResourceSearchResult]
    total: int
    limit: int
    offset: int
    filters_applied: list[str]


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


@router.get("/eligibility", response_model=EligibilitySearchResponse)
def search_with_eligibility(
    session: SessionDep,
    q: str | None = Query(None, description="Optional search query"),
    category: str | None = Query(None, description="Filter by category"),
    states: str | None = Query(
        None, description="Filter by states (comma-separated, e.g., VA,MD,DC)"
    ),
    counties: str | None = Query(
        None, description="Filter by counties (comma-separated, lowercase)"
    ),
    age_bracket: str | None = Query(
        None,
        description="Age bracket: under_55, 55_61, 62_plus, 65_plus",
        pattern="^(under_55|55_61|62_plus|65_plus)$",
    ),
    household_size: int | None = Query(None, ge=1, le=10, description="Household size (1-10)"),
    income_bracket: str | None = Query(
        None,
        description="Income bracket: low (<50% AMI), moderate (50-80% AMI), any",
        pattern="^(low|moderate|any)$",
    ),
    housing_status: str | None = Query(
        None,
        description="Housing status: homeless, at_risk, stably_housed",
        pattern="^(homeless|at_risk|stably_housed)$",
    ),
    veteran_status: bool | None = Query(None, description="Veteran status filter"),
    discharge: str | None = Query(
        None,
        description="Discharge status: honorable, other_than_dis, unknown",
        pattern="^(honorable|other_than_dis|unknown)$",
    ),
    has_disability: bool | None = Query(None, description="Has disability filter"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> EligibilitySearchResponse:
    """Search resources with eligibility filtering.

    This endpoint supports the eligibility wizard by filtering resources based on
    veteran eligibility criteria. All filter inputs are coarse/bucketed to avoid
    collecting PII.

    Returns resources with match_reasons explaining why each resource matched.
    """
    # Parse comma-separated values
    states_list = [s.strip().upper() for s in states.split(",")] if states else None
    counties_list = [c.strip().lower() for c in counties.split(",")] if counties else None

    # Build eligibility filters
    eligibility_filters = EligibilityFilters(
        states=states_list,
        counties=counties_list,
        age_bracket=age_bracket,
        household_size=household_size,
        income_bracket=income_bracket,
        housing_status=housing_status,
        veteran_status=veteran_status,
        discharge=discharge,
        has_disability=has_disability,
    )

    service = SearchService(session)
    results, total, filters_applied = service.search_with_eligibility(
        query=q,
        category=category,
        eligibility_filters=eligibility_filters,
        limit=limit,
        offset=offset,
    )

    return EligibilitySearchResponse(
        query=q,
        results=results,
        total=total,
        limit=limit,
        offset=offset,
        filters_applied=filters_applied,
    )


class SemanticSearchResponse(BaseModel):
    """Response for semantic search endpoint."""

    query: str
    results: list[ResourceSearchResult]
    total: int
    limit: int
    offset: int
    search_mode: str  # "semantic" or "hybrid"


@router.post("/semantic", response_model=SemanticSearchResponse)
def semantic_search(
    session: SessionDep,
    q: str = Query(..., min_length=1, description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
    state: str | None = Query(None, description="Filter by state (2-letter code)"),
    mode: str = Query(
        "hybrid",
        description="Search mode: 'semantic' (vector only) or 'hybrid' (vector + FTS)",
        pattern="^(semantic|hybrid)$",
    ),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> SemanticSearchResponse:
    """Semantic search using pgvector embeddings.

    Supports two modes:
    - semantic: Pure vector similarity search
    - hybrid: Combines full-text search with semantic similarity using RRF

    Requires OPENAI_API_KEY to be configured for embedding generation.
    """
    from app.config import settings

    # Check if OpenAI API key is configured
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="Semantic search requires OPENAI_API_KEY to be configured",
        )

    # Generate embedding for query
    try:
        from app.services.embedding import EmbeddingService

        embedding_service = EmbeddingService()
        result = embedding_service.generate_embedding(q)
        query_embedding = result.embedding
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embedding: {e}",
        ) from e

    service = SearchService(session)

    if mode == "semantic":
        results, total = service.semantic_search(
            query_embedding=query_embedding,
            category=category,
            state=state,
            limit=limit,
            offset=offset,
        )
    else:  # hybrid
        results, total = service.hybrid_search(
            query=q,
            query_embedding=query_embedding,
            category=category,
            state=state,
            limit=limit,
            offset=offset,
        )

    return SemanticSearchResponse(
        query=q,
        results=results,
        total=total,
        limit=limit,
        offset=offset,
        search_mode=mode,
    )
