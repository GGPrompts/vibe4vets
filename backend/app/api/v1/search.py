"""Search endpoints with full-text search, eligibility filtering, and semantic search.

Provides multiple search modes:
- Full-text search with PostgreSQL tsvector
- Eligibility-filtered search for veteran criteria matching
- Semantic search using AI embeddings (requires OpenAI API key)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.database import SessionDep
from app.schemas.resource import ResourceSearchResult
from app.services.search import EligibilityFilters, SearchService

router = APIRouter()


class SearchResponse(BaseModel):
    """Response for search endpoint."""

    query: str = Field(..., description="The search query that was executed")
    results: list[ResourceSearchResult] = Field(..., description="List of matching resources with relevance scores")
    total: int = Field(..., description="Total number of matching results")
    limit: int = Field(..., description="Maximum results returned")
    offset: int = Field(..., description="Pagination offset")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "housing assistance",
                "results": [
                    {
                        "resource": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "HUD-VASH Housing Program",
                            "description": "Combines HUD housing vouchers with VA supportive services.",
                            "categories": ["housing"],
                        },
                        "rank": 0.95,
                        "explanations": [{"reason": "Matches 'housing' in title", "field": "title"}],
                    }
                ],
                "total": 15,
                "limit": 20,
                "offset": 0,
            }
        }
    }


class EligibilitySearchResponse(BaseModel):
    """Response for eligibility-filtered search."""

    query: str | None = Field(None, description="Optional search query if provided")
    results: list[ResourceSearchResult] = Field(..., description="Matching resources with eligibility match reasons")
    total: int = Field(..., description="Total matching results")
    limit: int = Field(..., description="Maximum results returned")
    offset: int = Field(..., description="Pagination offset")
    filters_applied: list[str] = Field(..., description="List of eligibility filters that were applied")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": None,
                "results": [],
                "total": 5,
                "limit": 20,
                "offset": 0,
                "filters_applied": ["state:VA", "housing_status:homeless"],
            }
        }
    }


@router.get(
    "",
    response_model=SearchResponse,
    summary="Full-text search",
    response_description="Search results with relevance ranking and match explanations",
    responses={
        200: {
            "description": "Search completed successfully",
        },
        422: {
            "description": "Invalid query parameters",
        },
    },
)
def search_resources(
    session: SessionDep,
    q: str = Query(
        ...,
        min_length=1,
        description="Search query text",
        examples=["employment assistance VA", "housing help", "HUD-VASH"],
    ),
    category: str | None = Query(
        None,
        description="Filter by category (employment, training, housing, legal)",
        examples=["employment", "housing"],
    ),
    state: str | None = Query(
        None,
        description="Filter by state using 2-letter code",
        examples=["VA", "TX", "CA"],
        min_length=2,
        max_length=2,
    ),
    limit: int = Query(20, ge=1, le=500, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> SearchResponse:
    """Search veteran resources using PostgreSQL full-text search.

    Returns resources matching the query with relevance ranking and
    **"Why this matched"** explanations for each result.

    Results are ranked by:
    1. Text relevance score
    2. Source reliability (Tier 1 sources rank higher)
    3. Freshness score

    **Search tips:**
    - Use multiple keywords: "job training Virginia"
    - Search by program name: "HUD-VASH"
    - Search by eligibility: "disabled veteran housing"
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


@router.get(
    "/eligibility",
    response_model=EligibilitySearchResponse,
    summary="Eligibility-filtered search",
    response_description="Resources matching veteran eligibility criteria with match reasons",
    responses={
        200: {
            "description": "Search completed with eligibility filters applied",
        },
        422: {
            "description": "Invalid filter parameters",
        },
    },
)
def search_with_eligibility(
    session: SessionDep,
    q: str | None = Query(
        None,
        description="Optional search query to combine with eligibility filters",
        examples=["housing voucher", "job training"],
    ),
    category: str | None = Query(
        None,
        description="Filter by category (employment, training, housing, legal)",
        examples=["housing", "employment"],
    ),
    states: str | None = Query(
        None,
        description="Filter by states (comma-separated 2-letter codes)",
        examples=["VA,MD,DC", "TX", "CA,OR,WA"],
    ),
    counties: str | None = Query(
        None,
        description="Filter by counties (comma-separated, lowercase)",
        examples=["arlington,fairfax", "los angeles"],
    ),
    age_bracket: str | None = Query(
        None,
        description="Age range: under_55, 55_61, 62_plus, 65_plus",
        pattern="^(under_55|55_61|62_plus|65_plus)$",
        examples=["62_plus", "under_55"],
    ),
    household_size: int | None = Query(
        None,
        ge=1,
        le=10,
        description="Number of people in household (1-10)",
        examples=[1, 2, 4],
    ),
    income_bracket: str | None = Query(
        None,
        description="Income level relative to Area Median Income: low (<50%), moderate (50-80%), any",
        pattern="^(low|moderate|any)$",
        examples=["low", "moderate"],
    ),
    housing_status: str | None = Query(
        None,
        description="Current housing situation: homeless, at_risk, stably_housed",
        pattern="^(homeless|at_risk|stably_housed)$",
        examples=["homeless", "at_risk"],
    ),
    veteran_status: bool | None = Query(
        None,
        description="Filter for veteran-only resources",
        examples=[True],
    ),
    discharge: str | None = Query(
        None,
        description="Military discharge status: honorable, other_than_dis, unknown",
        pattern="^(honorable|other_than_dis|unknown)$",
        examples=["honorable", "other_than_dis"],
    ),
    has_disability: bool | None = Query(
        None,
        description="Filter for disability-related resources",
        examples=[True, False],
    ),
    limit: int = Query(20, ge=1, le=500, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> EligibilitySearchResponse:
    """Search resources with eligibility criteria filtering.

    This endpoint powers the **Eligibility Wizard** by filtering resources based on
    veteran-specific criteria. All inputs are **coarse/bucketed** to avoid collecting PII.

    **How it works:**
    1. Filters are applied to find matching resources
    2. Each result includes `match_reasons` explaining the match
    3. Results are ranked by eligibility match quality

    **Eligibility criteria:**
    - **Location**: State and county filters
    - **Demographics**: Age bracket, household size
    - **Financial**: Income bracket (relative to Area Median Income)
    - **Status**: Housing status, veteran status, discharge type, disability

    **Privacy note:** No personal information is stored. Filters use broad
    categories to maintain anonymity.
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

    query: str = Field(..., description="The search query")
    results: list[ResourceSearchResult] = Field(..., description="Matching resources")
    total: int = Field(..., description="Total matching results")
    limit: int = Field(..., description="Maximum results returned")
    offset: int = Field(..., description="Pagination offset")
    search_mode: str = Field(..., description="Search mode used: 'semantic' or 'hybrid'")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "help finding a job after military service",
                "results": [],
                "total": 10,
                "limit": 20,
                "offset": 0,
                "search_mode": "hybrid",
            }
        }
    }


@router.post(
    "/semantic",
    response_model=SemanticSearchResponse,
    summary="Semantic (AI) search",
    response_description="AI-powered search results using natural language understanding",
    responses={
        200: {
            "description": "Semantic search completed",
        },
        503: {
            "description": "Service unavailable - OpenAI API key not configured",
            "content": {
                "application/json": {"example": {"detail": "Semantic search requires OPENAI_API_KEY to be configured"}}
            },
        },
    },
)
def semantic_search(
    session: SessionDep,
    q: str = Query(
        ...,
        min_length=1,
        description="Natural language search query",
        examples=["I need help finding a job after leaving the military", "struggling to pay rent"],
    ),
    category: str | None = Query(
        None,
        description="Filter by category (employment, training, housing, legal)",
        examples=["employment", "housing"],
    ),
    state: str | None = Query(
        None,
        description="Filter by state using 2-letter code",
        examples=["TX", "VA", "CA"],
        min_length=2,
        max_length=2,
    ),
    mode: str = Query(
        "hybrid",
        description="Search strategy: 'semantic' (AI only) or 'hybrid' (AI + keyword)",
        pattern="^(semantic|hybrid)$",
        examples=["hybrid", "semantic"],
    ),
    limit: int = Query(20, ge=1, le=500, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> SemanticSearchResponse:
    """AI-powered semantic search using vector embeddings.

    Uses OpenAI embeddings to understand the **meaning** of your query,
    not just keywords. Great for natural language questions.

    **Search modes:**
    - `semantic` - Pure AI similarity search (best for conversational queries)
    - `hybrid` - Combines AI understanding with keyword matching using
      Reciprocal Rank Fusion (RRF) for balanced results

    **Example queries:**
    - "I'm a veteran struggling to pay rent"
    - "How can I get help with my resume?"
    - "Programs for veterans with PTSD"

    **Note:** Requires `OPENAI_API_KEY` environment variable to be configured.
    Returns 503 if not available.
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
