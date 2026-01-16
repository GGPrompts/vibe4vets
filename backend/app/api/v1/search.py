"""Search endpoints with full-text search and eligibility filtering."""

from fastapi import APIRouter, Query
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
    states: str | None = Query(None, description="Filter by states (comma-separated, e.g., VA,MD,DC)"),
    counties: str | None = Query(None, description="Filter by counties (comma-separated, lowercase)"),
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
