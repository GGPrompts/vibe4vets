"""Search service for full-text, semantic, and hybrid search."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, cast, func, or_, text
from sqlmodel import Session, col, select

from app.models import Location, Organization, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)
from app.schemas.resource import (
    BenefitsInfo,
    EligibilityInfo,
    IntakeInfo,
    LocationNested,
    MatchExplanation,
    MatchReason,
    OrganizationNested,
    ResourceRead,
    ResourceSearchResult,
    TrustSignals,
    VerificationInfo,
)


@dataclass
class EligibilityFilters:
    """Eligibility filter parameters for search."""

    states: list[str] | None = None
    counties: list[str] | None = None
    age_bracket: str | None = None  # under_55, 55_61, 62_plus, 65_plus
    household_size: int | None = None
    income_bracket: str | None = None  # low (<50% AMI), moderate (50-80%), any
    housing_status: str | None = None  # homeless, at_risk, stably_housed
    veteran_status: bool | None = None
    discharge: str | None = None  # honorable, other_than_dis, unknown
    has_disability: bool | None = None


class SearchService:
    """Service for searching resources."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _build_prefix_tsquery(self, query: str) -> str:
        """Convert query to prefix-matching tsquery string.

        E.g., "helm hard" becomes "helm:* & hard:*" to match partial words.
        """
        import re

        # Remove special characters that could break tsquery syntax
        clean_query = re.sub(r"[^\w\s]", " ", query)
        words = clean_query.strip().split()
        if not words:
            return ""
        # Add :* suffix for prefix matching, join with & for AND logic
        return " & ".join(f"{word}:*" for word in words if word)

    def search(
        self,
        query: str,
        categories: list[str] | None = None,
        states: list[str] | None = None,
        scope: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ResourceSearchResult], int]:
        """Search resources using PostgreSQL full-text search.

        Args:
            query: Search query text.
            categories: Optional list of category filters (OR logic - match ANY category).
            states: Optional list of state filters (OR logic - match ANY state, includes national).
            scope: Optional scope filter: 'national', 'state', 'local', or 'all'.
            tags: Optional list of eligibility tags to filter by (AND logic - must match ALL tags).
            limit: Maximum results to return.
            offset: Pagination offset.
        """
        # Build the search query with prefix matching for partial words
        prefix_query = self._build_prefix_tsquery(query)
        search_query = func.to_tsquery("english", prefix_query)

        # Base query with FTS
        stmt = (
            select(
                Resource,
                func.ts_rank(Resource.search_vector, search_query).label("rank"),
            )
            .where(Resource.status == ResourceStatus.ACTIVE)
            .where(Resource.search_vector.op("@@")(search_query))
        )

        # Apply category filter (OR logic - match ANY category)
        if categories:
            category_conditions = [Resource.categories.contains([cat]) for cat in categories]
            stmt = stmt.where(or_(*category_conditions))

        # Apply state filter (OR logic - match ANY state, always includes national resources)
        if states:
            state_conditions = [Resource.scope == ResourceScope.NATIONAL]
            for state in states:
                state_conditions.append(Resource.states.contains([state]))
            stmt = stmt.where(or_(*state_conditions))

        # Apply scope filter
        if scope and scope != "all":
            if scope == "national":
                stmt = stmt.where(Resource.scope == ResourceScope.NATIONAL)
            elif scope == "state":
                stmt = stmt.where(Resource.scope == ResourceScope.STATE)
            elif scope == "local":
                stmt = stmt.where(Resource.scope == ResourceScope.LOCAL)

        # Tag filter: resource must have ALL of the requested tags (AND logic)
        # Uses @> (contains) operator for each tag to ensure all tags are present
        if tags:
            for tag in tags:
                stmt = stmt.where(Resource.tags.contains([tag]))

        # Get total count with same filters
        count_stmt = (
            select(func.count(Resource.id))
            .where(Resource.status == ResourceStatus.ACTIVE)
            .where(Resource.search_vector.op("@@")(search_query))
        )
        if categories:
            category_conditions = [Resource.categories.contains([cat]) for cat in categories]
            count_stmt = count_stmt.where(or_(*category_conditions))
        if states:
            state_conditions = [Resource.scope == ResourceScope.NATIONAL]
            for state in states:
                state_conditions.append(Resource.states.contains([state]))
            count_stmt = count_stmt.where(or_(*state_conditions))
        if scope and scope != "all":
            if scope == "national":
                count_stmt = count_stmt.where(Resource.scope == ResourceScope.NATIONAL)
            elif scope == "state":
                count_stmt = count_stmt.where(Resource.scope == ResourceScope.STATE)
            elif scope == "local":
                count_stmt = count_stmt.where(Resource.scope == ResourceScope.LOCAL)
        if tags:
            # AND logic: each tag must be present
            for tag in tags:
                count_stmt = count_stmt.where(Resource.tags.contains([tag]))

        total = self.session.exec(count_stmt).one()

        # Order by rank, then reliability
        stmt = stmt.order_by(text("rank DESC"), col(Resource.reliability_score).desc()).offset(offset).limit(limit)

        results = self.session.exec(stmt).all()

        # Build search results with explanations
        search_results = []
        # Use first category/state for explanations (backwards compatibility)
        category = categories[0] if categories else None
        state = states[0] if states else None
        for resource, rank in results:
            explanations = self._build_explanations(resource, query, category, state, tags)
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
        tags: list[str] | None = None,
    ) -> list[MatchExplanation]:
        """Build 'Why this matched' explanations."""
        from app.core.taxonomy import get_tag_display_name

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

        # Tag filter explanation
        if tags and resource.tags:
            matched_tags = [t for t in tags if t in resource.tags]
            if matched_tags:
                tag_names = [get_tag_display_name(t) for t in matched_tags[:3]]
                tag_str = ", ".join(tag_names)
                if len(matched_tags) > 3:
                    tag_str += f" +{len(matched_tags) - 3} more"
                explanations.append(
                    MatchExplanation(
                        reason=f"Matches tags: {tag_str}",
                        field="tags",
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
            last_verified = resource.last_verified
            if last_verified.tzinfo is None:
                last_verified = last_verified.replace(tzinfo=UTC)
            days_ago = (datetime.now(UTC) - last_verified).days
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
                location_nested = self._build_location_nested(location)

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

    def _build_location_nested(self, location: Location) -> LocationNested:
        """Build LocationNested with eligibility, intake, and verification info."""
        # Build eligibility info if any fields are set
        eligibility = None
        if any(
            [
                location.age_min,
                location.age_max,
                location.household_size_min,
                location.household_size_max,
                location.income_limit_type,
                location.income_limit_ami_percent,
                location.housing_status_required,
                location.docs_required,
                location.waitlist_status,
                location.distribution_schedule,
                location.serves_dietary,
                location.quantity_limit,
                location.id_required is not None,
            ]
        ):
            eligibility = EligibilityInfo(
                age_min=location.age_min,
                age_max=location.age_max,
                household_size_min=location.household_size_min,
                household_size_max=location.household_size_max,
                income_limit_type=location.income_limit_type,
                income_limit_value=location.income_limit_value,
                income_limit_ami_percent=location.income_limit_ami_percent,
                housing_status_required=location.housing_status_required or [],
                active_duty_required=location.active_duty_required,
                discharge_required=location.discharge_required,
                veteran_status_required=location.veteran_status_required,
                docs_required=location.docs_required or [],
                waitlist_status=location.waitlist_status,
                distribution_schedule=location.distribution_schedule,
                serves_dietary=location.serves_dietary or [],
                quantity_limit=location.quantity_limit,
                id_required=location.id_required,
            )

        # Build intake info if any fields are set
        intake = None
        has_intake = any(
            [
                location.intake_phone,
                location.intake_url,
                location.intake_hours,
                location.intake_notes,
            ]
        )
        if has_intake:
            intake = IntakeInfo(
                phone=location.intake_phone,
                url=location.intake_url,
                hours=location.intake_hours,
                notes=location.intake_notes,
            )

        # Build verification info if any fields are set
        verification = None
        if any([location.last_verified_at, location.verified_by, location.verification_notes]):
            verification = VerificationInfo(
                last_verified_at=location.last_verified_at,
                verified_by=location.verified_by,
                notes=location.verification_notes,
            )

        # Build benefits info if any fields are set
        benefits = None
        if any(
            [
                location.benefits_types_supported,
                location.representative_type,
                location.accredited,
                location.walk_in_available,
                location.appointment_required,
                location.virtual_available,
                location.free_service,
                location.languages_supported,
            ]
        ):
            benefits = BenefitsInfo(
                benefits_types=location.benefits_types_supported or [],
                representative_type=location.representative_type,
                accredited=location.accredited,
                walk_in_available=location.walk_in_available,
                appointment_required=location.appointment_required,
                virtual_available=location.virtual_available,
                free_service=location.free_service,
                languages=location.languages_supported or [],
            )

        return LocationNested(
            id=location.id,
            city=location.city,
            state=location.state,
            address=location.address,
            service_area=location.service_area or [],
            eligibility=eligibility,
            intake=intake,
            verification=verification,
            benefits=benefits,
        )

    def search_with_eligibility(
        self,
        query: str | None = None,
        category: str | None = None,
        eligibility_filters: EligibilityFilters | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ResourceSearchResult], int, list[str]]:
        """Search resources with eligibility filtering and match reasons.

        Args:
            query: Optional search query text.
            category: Optional category filter.
            eligibility_filters: Optional eligibility criteria filters.
            tags: Optional list of eligibility tags to filter by (AND logic - must match ALL tags).
            limit: Maximum results to return.
            offset: Pagination offset.

        Returns:
            Tuple of (results, total, filters_applied)
        """
        filters_applied = []

        # Base query - either FTS or browse all
        if query:
            prefix_query = self._build_prefix_tsquery(query)
            search_query = func.to_tsquery("english", prefix_query)
            stmt = (
                select(
                    Resource,
                    func.ts_rank(Resource.search_vector, search_query).label("rank"),
                )
                .where(Resource.status == ResourceStatus.ACTIVE)
                .where(Resource.search_vector.op("@@")(search_query))
            )
        else:
            # Browse mode - no text query
            stmt = select(
                Resource,
                func.literal(1.0).label("rank"),
            ).where(Resource.status == ResourceStatus.ACTIVE)

        # Apply category filter
        if category:
            stmt = stmt.where(Resource.categories.contains([category]))
            filters_applied.append("category")

        # Apply tag filter (AND logic - must match ALL of the requested tags)
        if tags:
            for tag in tags:
                stmt = stmt.where(Resource.tags.contains([tag]))
            filters_applied.append("tags")

        # Apply eligibility filters if provided
        if eligibility_filters:
            # State filter
            if eligibility_filters.states:
                state_conditions = [Resource.scope == ResourceScope.NATIONAL]
                for state in eligibility_filters.states:
                    state_conditions.append(Resource.states.contains([state]))
                stmt = stmt.where(or_(*state_conditions))
                filters_applied.append("state")

            # Join with locations for eligibility filtering
            if any(
                [
                    eligibility_filters.age_bracket,
                    eligibility_filters.household_size,
                    eligibility_filters.income_bracket,
                    eligibility_filters.housing_status,
                ]
            ):
                stmt = stmt.outerjoin(Location, Resource.location_id == Location.id)

                # Age bracket filter
                if eligibility_filters.age_bracket:
                    age = self._age_bracket_to_age(eligibility_filters.age_bracket)
                    if age:
                        stmt = stmt.where(
                            or_(
                                Location.age_min.is_(None),
                                Location.age_min <= age,
                            )
                        )
                        filters_applied.append("age_bracket")

                # Household size filter
                if eligibility_filters.household_size:
                    hs = eligibility_filters.household_size
                    stmt = stmt.where(
                        or_(
                            Location.household_size_max.is_(None),
                            Location.household_size_max >= hs,
                        )
                    )
                    filters_applied.append("household_size")

                # Income bracket filter
                if eligibility_filters.income_bracket:
                    if eligibility_filters.income_bracket == "low":
                        # User income is low (<50% AMI) - match programs accepting <50% AMI
                        stmt = stmt.where(
                            or_(
                                Location.income_limit_ami_percent.is_(None),
                                Location.income_limit_ami_percent >= 50,
                            )
                        )
                    elif eligibility_filters.income_bracket == "moderate":
                        # User income is moderate (50-80% AMI)
                        stmt = stmt.where(
                            or_(
                                Location.income_limit_ami_percent.is_(None),
                                Location.income_limit_ami_percent >= 80,
                            )
                        )
                    filters_applied.append("income_bracket")

                # Housing status filter
                if eligibility_filters.housing_status:
                    hs = eligibility_filters.housing_status
                    stmt = stmt.where(
                        or_(
                            Location.housing_status_required == [],
                            Location.housing_status_required.contains([hs]),
                        )
                    )
                    filters_applied.append("housing_status")

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.exec(count_stmt).one()

        # Order and paginate
        if query:
            stmt = stmt.order_by(text("rank DESC"), col(Resource.reliability_score).desc())
        else:
            stmt = stmt.order_by(col(Resource.reliability_score).desc(), col(Resource.created_at).desc())

        stmt = stmt.offset(offset).limit(limit)
        results = self.session.exec(stmt).all()

        # Build search results with match reasons
        search_results = []
        for resource, rank in results:
            state_filter = eligibility_filters.states[0] if eligibility_filters and eligibility_filters.states else None
            explanations = self._build_explanations(resource, query or "", category, state_filter)
            match_reasons = self._build_match_reasons(resource, eligibility_filters)
            resource_read = self._to_read_schema(resource)
            search_results.append(
                ResourceSearchResult(
                    resource=resource_read,
                    rank=float(rank),
                    explanations=explanations,
                    match_reasons=match_reasons,
                )
            )

        return search_results, total, filters_applied

    def _age_bracket_to_age(self, bracket: str) -> int | None:
        """Convert age bracket to representative age for filtering."""
        mapping = {
            "under_55": 40,
            "55_61": 58,
            "62_plus": 65,
            "65_plus": 70,
        }
        return mapping.get(bracket)

    def _build_match_reasons(
        self,
        resource: Resource,
        eligibility_filters: EligibilityFilters | None,
    ) -> list[MatchReason]:
        """Build structured match reasons for eligibility filtering."""
        reasons = []

        # Category match reasons
        for cat in resource.categories:
            cat_labels = {
                "housing": "Housing assistance",
                "employment": "Employment services",
                "training": "Training program",
                "legal": "Legal services",
                "food": "Food assistance",
                "benefits": "Benefits consultation",
            }
            if cat in cat_labels:
                reasons.append(MatchReason(type="category", label=cat_labels[cat]))

        # Location-based reasons
        location = None
        if resource.location_id:
            location = self.session.get(Location, resource.location_id)

        if location:
            # Service area
            if location.service_area:
                county = location.service_area[0] if location.service_area else None
                if county:
                    reasons.append(MatchReason(type="location", label=f"Serves {county}"))
            elif location.city and location.state:
                city_state = f"{location.city}, {location.state}"
                reasons.append(MatchReason(type="location", label=f"Available in {city_state}"))

            # Age requirements
            if location.age_min:
                reasons.append(MatchReason(type="age", label=f"{location.age_min}+"))
            else:
                reasons.append(MatchReason(type="age", label="All ages"))

            # Income requirements
            if location.income_limit_ami_percent:
                ami = location.income_limit_ami_percent
                reasons.append(MatchReason(type="income", label=f"Income under {ami}% AMI"))

            # Housing status
            if location.housing_status_required:
                status_labels = {
                    "homeless": "For Veterans experiencing homelessness",
                    "at_risk": "For Veterans at risk of housing instability",
                    "stably_housed": "For stably housed Veterans",
                }
                for status in location.housing_status_required:
                    if status in status_labels:
                        label = status_labels[status]
                        reasons.append(MatchReason(type="housing_status", label=label))
                        break

            # Waitlist status
            if location.waitlist_status == "open":
                reasons.append(MatchReason(type="availability", label="Waitlist open"))

            # Food distribution specific reasons
            if location.distribution_schedule:
                reasons.append(MatchReason(type="schedule", label=location.distribution_schedule))
            if location.serves_dietary:
                dietary_str = ", ".join(location.serves_dietary[:3])
                if len(location.serves_dietary) > 3:
                    dietary_str += f" +{len(location.serves_dietary) - 3}"
                reasons.append(MatchReason(type="dietary", label=f"Offers: {dietary_str}"))
            if location.id_required is False:
                reasons.append(MatchReason(type="access", label="No ID required"))

            # Benefits-specific match reasons
            if location.benefits_types_supported:
                benefit_labels = {
                    "disability": "Disability claims",
                    "pension": "Pension claims",
                    "education": "Education benefits",
                    "healthcare": "Healthcare enrollment",
                    "burial": "Burial benefits",
                    "survivor": "Survivor benefits",
                    "vre": "Voc Rehab (VR&E)",
                }
                # Show up to 2 benefit types
                shown_benefits = []
                for bt in location.benefits_types_supported[:2]:
                    if bt in benefit_labels:
                        shown_benefits.append(benefit_labels[bt])
                if shown_benefits:
                    label = ", ".join(shown_benefits)
                    if len(location.benefits_types_supported) > 2:
                        label += f" +{len(location.benefits_types_supported) - 2}"
                    reasons.append(MatchReason(type="benefits", label=label))

            if location.representative_type:
                rep_labels = {
                    "vso": "VSO representative",
                    "attorney": "Accredited attorney",
                    "claims_agent": "Claims agent",
                    "cvso": "County Veteran service officer",
                }
                if location.representative_type in rep_labels:
                    reasons.append(
                        MatchReason(
                            type="representative",
                            label=rep_labels[location.representative_type],
                        )
                    )

            if location.accredited:
                reasons.append(MatchReason(type="accredited", label="VA-accredited"))

            if location.free_service:
                reasons.append(MatchReason(type="cost", label="Free service"))

            if location.virtual_available:
                reasons.append(MatchReason(type="access", label="Virtual available"))

            if location.walk_in_available:
                reasons.append(MatchReason(type="access", label="Walk-ins welcome"))

        elif resource.scope == ResourceScope.NATIONAL:
            reasons.append(MatchReason(type="location", label="Available nationwide"))
        elif resource.states:
            states_str = ", ".join(resource.states[:3])
            if len(resource.states) > 3:
                states_str += f" +{len(resource.states) - 3} more"
            reasons.append(MatchReason(type="location", label=f"Serves {states_str}"))

        return reasons

    def semantic_search(
        self,
        query_embedding: list[float],
        category: str | None = None,
        state: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ResourceSearchResult], int]:
        """Search resources using vector similarity with pgvector.

        Args:
            query_embedding: The query text embedding vector.
            category: Optional category filter.
            state: Optional state filter.
            limit: Maximum results to return.
            offset: Offset for pagination.

        Returns:
            Tuple of (results, total_count)
        """
        # Use cosine distance for similarity (1 - cosine_distance = cosine_similarity)
        # pgvector uses <=> for cosine distance
        # Cast to Float to prevent pgvector from trying to parse as vector
        distance_col = cast(Resource.embedding.op("<=>")(query_embedding), Float).label("distance")

        # Base query with vector similarity
        stmt = (
            select(Resource, distance_col)
            .where(Resource.status == ResourceStatus.ACTIVE)
            .where(Resource.embedding.isnot(None))
        )

        # Apply filters
        if category:
            stmt = stmt.where(Resource.categories.contains([category]))
        if state:
            stmt = stmt.where(
                or_(
                    Resource.scope == ResourceScope.NATIONAL,
                    Resource.states.contains([state]),
                )
            )

        # Get total count
        count_stmt = (
            select(func.count(Resource.id))
            .where(Resource.status == ResourceStatus.ACTIVE)
            .where(Resource.embedding.isnot(None))
        )
        if category:
            count_stmt = count_stmt.where(Resource.categories.contains([category]))
        if state:
            count_stmt = count_stmt.where(
                or_(
                    Resource.scope == ResourceScope.NATIONAL,
                    Resource.states.contains([state]),
                )
            )
        total = self.session.exec(count_stmt).one()

        # Order by distance (ascending = most similar first)
        stmt = stmt.order_by(text("distance ASC")).offset(offset).limit(limit)
        results = self.session.exec(stmt).all()

        # Build search results
        search_results = []
        for resource, distance in results:
            # Convert distance to similarity score (1 - distance for cosine)
            similarity = 1.0 - float(distance)
            explanations = [
                MatchExplanation(
                    reason=f"Semantic similarity: {similarity:.0%}",
                    field="embedding",
                )
            ]
            if category and category in resource.categories:
                explanations.append(
                    MatchExplanation(
                        reason=f"Covers {category} resources",
                        field="categories",
                    )
                )
            if state and state in resource.states:
                explanations.append(
                    MatchExplanation(
                        reason=f"Serves {state}",
                        field="states",
                    )
                )

            resource_read = self._to_read_schema(resource)
            search_results.append(
                ResourceSearchResult(
                    resource=resource_read,
                    rank=similarity,
                    explanations=explanations,
                )
            )

        return search_results, total

    def hybrid_search(
        self,
        query: str,
        query_embedding: list[float],
        category: str | None = None,
        state: str | None = None,
        limit: int = 20,
        offset: int = 0,
        fts_weight: float = 0.5,
        semantic_weight: float = 0.5,
    ) -> tuple[list[ResourceSearchResult], int]:
        """Hybrid search combining full-text search and semantic similarity.

        Uses Reciprocal Rank Fusion (RRF) to combine FTS and vector rankings.

        Args:
            query: The search query text.
            query_embedding: The query text embedding vector.
            category: Optional category filter.
            state: Optional state filter.
            limit: Maximum results to return.
            offset: Offset for pagination.
            fts_weight: Weight for FTS ranking (default 0.5).
            semantic_weight: Weight for semantic ranking (default 0.5).

        Returns:
            Tuple of (results, total_count)
        """
        # RRF constant (commonly 60)
        k = 60

        # Build FTS query
        prefix_query = self._build_prefix_tsquery(query)
        search_query = func.to_tsquery("english", prefix_query)

        # Vector distance for semantic ranking
        # Cast to Float to prevent pgvector from trying to parse as vector
        distance_col = cast(Resource.embedding.op("<=>")(query_embedding), Float).label("distance")

        # FTS rank
        fts_rank = func.ts_rank(Resource.search_vector, search_query).label("fts_rank")

        # Combined query with both rankings
        stmt = (
            select(Resource, fts_rank, distance_col)
            .where(Resource.status == ResourceStatus.ACTIVE)
            .where(
                or_(
                    Resource.search_vector.op("@@")(search_query),
                    Resource.embedding.isnot(None),
                )
            )
        )

        # Apply filters
        if category:
            stmt = stmt.where(Resource.categories.contains([category]))
        if state:
            stmt = stmt.where(
                or_(
                    Resource.scope == ResourceScope.NATIONAL,
                    Resource.states.contains([state]),
                )
            )

        # Execute to get all matching results for RRF
        results = self.session.exec(stmt).all()

        if not results:
            return [], 0

        # Apply RRF scoring
        scored_results = []
        for resource, fts_r, distance in results:
            # FTS score (already a rank, higher is better)
            fts_score = float(fts_r) if fts_r else 0.0

            # Semantic score (convert distance to similarity)
            semantic_score = 1.0 - float(distance) if distance else 0.0

            # RRF: combine rankings
            # For FTS, use rank directly (higher = better)
            # For semantic, use similarity (higher = better)
            rrf_score = fts_weight * (1.0 / (k + (1.0 / (fts_score + 0.001)))) + semantic_weight * (
                1.0 / (k + (1.0 / (semantic_score + 0.001)))
            )

            scored_results.append((resource, rrf_score, fts_score, semantic_score))

        # Sort by RRF score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        total = len(scored_results)

        # Apply pagination
        paginated = scored_results[offset : offset + limit]

        # Build search results
        search_results = []
        for resource, rrf_score, fts_score, semantic_score in paginated:
            explanations = []

            # Add FTS explanation if matched
            if fts_score > 0:
                if query.lower() in resource.title.lower():
                    explanations.append(
                        MatchExplanation(
                            reason=f'Title matches "{query}"',
                            field="title",
                        )
                    )
                else:
                    explanations.append(
                        MatchExplanation(
                            reason="Matches your search terms",
                            field="description",
                        )
                    )

            # Add semantic explanation if matched
            if semantic_score > 0:
                explanations.append(
                    MatchExplanation(
                        reason=f"Semantic relevance: {semantic_score:.0%}",
                        field="embedding",
                    )
                )

            # Category and state explanations
            if category and category in resource.categories:
                explanations.append(
                    MatchExplanation(
                        reason=f"Covers {category} resources",
                        field="categories",
                    )
                )
            if state and state in resource.states:
                explanations.append(
                    MatchExplanation(
                        reason=f"Serves {state}",
                        field="states",
                    )
                )

            resource_read = self._to_read_schema(resource)
            search_results.append(
                ResourceSearchResult(
                    resource=resource_read,
                    rank=rrf_score,
                    explanations=explanations,
                )
            )

        return search_results, total
