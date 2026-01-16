"""Search service for full-text and filtered search."""

from dataclasses import dataclass

from sqlalchemy import func, or_, text
from sqlmodel import Session, col, select

from app.models import Location, Organization, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus
from app.schemas.resource import (
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
            .where(Resource.search_vector.op("@@")(search_query))
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
        if any([
            location.age_min,
            location.age_max,
            location.household_size_min,
            location.household_size_max,
            location.income_limit_type,
            location.income_limit_ami_percent,
            location.housing_status_required,
            location.docs_required,
            location.waitlist_status,
        ]):
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
            )

        # Build intake info if any fields are set
        intake = None
        has_intake = any([
            location.intake_phone, location.intake_url,
            location.intake_hours, location.intake_notes
        ])
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

        return LocationNested(
            id=location.id,
            city=location.city,
            state=location.state,
            address=location.address,
            service_area=location.service_area or [],
            eligibility=eligibility,
            intake=intake,
            verification=verification,
        )

    def search_with_eligibility(
        self,
        query: str | None = None,
        category: str | None = None,
        eligibility_filters: EligibilityFilters | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ResourceSearchResult], int, list[str]]:
        """Search resources with eligibility filtering and match reasons.

        Returns:
            Tuple of (results, total, filters_applied)
        """
        filters_applied = []

        # Base query - either FTS or browse all
        if query:
            search_query = func.plainto_tsquery("english", query)
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
            if any([
                eligibility_filters.age_bracket,
                eligibility_filters.household_size,
                eligibility_filters.income_bracket,
                eligibility_filters.housing_status,
            ]):
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
            stmt = stmt.order_by(
                col(Resource.reliability_score).desc(), col(Resource.created_at).desc()
            )

        stmt = stmt.offset(offset).limit(limit)
        results = self.session.exec(stmt).all()

        # Build search results with match reasons
        search_results = []
        for resource, rank in results:
            state_filter = (
                eligibility_filters.states[0]
                if eligibility_filters and eligibility_filters.states else None
            )
            explanations = self._build_explanations(
                resource, query or "", category, state_filter
            )
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
                reasons.append(
                    MatchReason(type="location", label=f"Available in {city_state}")
                )

            # Age requirements
            if location.age_min:
                reasons.append(MatchReason(type="age", label=f"{location.age_min}+"))
            else:
                reasons.append(MatchReason(type="age", label="All ages"))

            # Income requirements
            if location.income_limit_ami_percent:
                ami = location.income_limit_ami_percent
                reasons.append(
                    MatchReason(type="income", label=f"Income under {ami}% AMI")
                )

            # Housing status
            if location.housing_status_required:
                status_labels = {
                    "homeless": "Serves homeless veterans",
                    "at_risk": "For at-risk housing",
                    "stably_housed": "For housed veterans",
                }
                for status in location.housing_status_required:
                    if status in status_labels:
                        label = status_labels[status]
                        reasons.append(MatchReason(type="housing_status", label=label))
                        break

            # Waitlist status
            if location.waitlist_status == "open":
                reasons.append(MatchReason(type="availability", label="Waitlist open"))

        elif resource.scope == ResourceScope.NATIONAL:
            reasons.append(MatchReason(type="location", label="Available nationwide"))
        elif resource.states:
            states_str = ", ".join(resource.states[:3])
            if len(resource.states) > 3:
                states_str += f" +{len(resource.states) - 3} more"
            reasons.append(MatchReason(type="location", label=f"Serves {states_str}"))

        return reasons
