"""Search service for full-text and filtered search."""


from sqlalchemy import func, text
from sqlmodel import Session, col, select

from app.models import Location, Organization, Resource, Source
from app.models.resource import ResourceStatus
from app.schemas.resource import (
    LocationNested,
    MatchExplanation,
    OrganizationNested,
    ResourceRead,
    ResourceSearchResult,
    TrustSignals,
)


class SearchService:
    """Service for searching resources."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def search(
        self,
        query: str,
        category: str | None = None,
        state: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ResourceSearchResult], int]:
        """Search resources using PostgreSQL full-text search."""
        # Build the search query using ts_rank for ranking
        search_query = func.plainto_tsquery("english", query)

        # Base query with FTS
        stmt = (
            select(
                Resource,
                func.ts_rank(Resource.search_vector, search_query).label("rank"),
            )
            .where(Resource.status == ResourceStatus.ACTIVE)
            .where(Resource.search_vector.op("@@")(search_query))
        )

        # Apply filters
        if category:
            stmt = stmt.where(Resource.categories.contains([category]))
        if state:
            stmt = stmt.where(Resource.states.contains([state]))

        # Get total count
        count_stmt = (
            select(func.count(Resource.id))
            .where(Resource.status == ResourceStatus.ACTIVE)
            .where(Resource.search_vector.op("@@")(search_query))
        )
        if category:
            count_stmt = count_stmt.where(Resource.categories.contains([category]))
        if state:
            count_stmt = count_stmt.where(Resource.states.contains([state]))

        total = self.session.exec(count_stmt).one()

        # Order by rank, then reliability
        stmt = (
            stmt.order_by(text("rank DESC"), col(Resource.reliability_score).desc())
            .offset(offset)
            .limit(limit)
        )

        results = self.session.exec(stmt).all()

        # Build search results with explanations
        search_results = []
        for resource, rank in results:
            explanations = self._build_explanations(resource, query, category, state)
            resource_read = self._to_read_schema(resource)
            search_results.append(
                ResourceSearchResult(
                    resource=resource_read,
                    rank=float(rank),
                    explanations=explanations,
                )
            )

        return search_results, total

    def _build_explanations(
        self,
        resource: Resource,
        query: str,
        category: str | None,
        state: str | None,
    ) -> list[MatchExplanation]:
        """Build 'Why this matched' explanations."""
        explanations = []

        # Query match explanation
        query_lower = query.lower()
        if query_lower in resource.title.lower():
            explanations.append(
                MatchExplanation(
                    reason=f'Title contains "{query}"',
                    field="title",
                    highlight=resource.title,
                )
            )
        elif query_lower in resource.description.lower():
            # Find a snippet around the match
            idx = resource.description.lower().find(query_lower)
            start = max(0, idx - 50)
            end = min(len(resource.description), idx + len(query) + 50)
            snippet = resource.description[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(resource.description):
                snippet = snippet + "..."
            explanations.append(
                MatchExplanation(
                    reason="Matches your search terms",
                    field="description",
                    highlight=snippet,
                )
            )

        # Category filter explanation
        if category and category in resource.categories:
            explanations.append(
                MatchExplanation(
                    reason=f"Covers {category} resources",
                    field="categories",
                )
            )

        # State filter explanation
        if state and state in resource.states:
            location = None
            if resource.location_id:
                location = self.session.get(Location, resource.location_id)
            if location:
                explanations.append(
                    MatchExplanation(
                        reason=f"Available in {location.city}, {state}",
                        field="location",
                    )
                )
            else:
                explanations.append(
                    MatchExplanation(
                        reason=f"Serves {state}",
                        field="states",
                    )
                )

        # Trust signal explanation
        if resource.last_verified:
            days_ago = (resource.last_verified.now() - resource.last_verified).days
            if days_ago <= 7:
                explanations.append(
                    MatchExplanation(
                        reason="Recently verified",
                        field="last_verified",
                    )
                )
        elif resource.reliability_score >= 0.8:
            explanations.append(
                MatchExplanation(
                    reason="From a trusted source",
                    field="reliability_score",
                )
            )

        return explanations

    def _to_read_schema(self, resource: Resource) -> ResourceRead:
        """Convert Resource model to read schema."""
        organization = self.session.get(Organization, resource.organization_id)
        org_nested = OrganizationNested(
            id=organization.id,
            name=organization.name,
            website=organization.website,
        )

        location_nested = None
        if resource.location_id:
            location = self.session.get(Location, resource.location_id)
            if location:
                location_nested = LocationNested(
                    id=location.id,
                    city=location.city,
                    state=location.state,
                    address=location.address,
                )

        source_tier = None
        source_name = None
        if resource.source_id:
            source = self.session.get(Source, resource.source_id)
            if source:
                source_tier = source.tier
                source_name = source.name

        trust = TrustSignals(
            freshness_score=resource.freshness_score,
            reliability_score=resource.reliability_score,
            last_verified=resource.last_verified,
            source_tier=source_tier,
            source_name=source_name,
        )

        return ResourceRead(
            id=resource.id,
            title=resource.title,
            description=resource.description,
            summary=resource.summary,
            eligibility=resource.eligibility,
            how_to_apply=resource.how_to_apply,
            categories=resource.categories,
            subcategories=resource.subcategories,
            tags=resource.tags,
            scope=resource.scope,
            states=resource.states,
            website=resource.website,
            phone=resource.phone,
            hours=resource.hours,
            languages=resource.languages,
            cost=resource.cost,
            status=resource.status,
            created_at=resource.created_at,
            updated_at=resource.updated_at,
            organization=org_nested,
            location=location_nested,
            trust=trust,
        )
