"""Resource service for CRUD operations."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import String, func, or_, text
from sqlmodel import Session, col, select

from app.models import Location, Organization, Program, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus
from app.schemas.resource import (
    EligibilityInfo,
    IntakeInfo,
    LocationNested,
    OrganizationNested,
    ProgramNested,
    ResourceCreate,
    ResourceNearbyList,
    ResourceNearbyResult,
    ResourceRead,
    ResourceUpdate,
    TrustSignals,
    VerificationInfo,
)

# Meters per mile for distance calculations
METERS_PER_MILE = 1609.34


class ResourceService:
    """Service for resource CRUD operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_count(
        self,
        categories: list[str] | None = None,
        states: list[str] | None = None,
        scope: str | None = None,
    ) -> int:
        """Get count of resources matching filters.

        Args:
            categories: Filter by categories (resources must match ANY of the provided categories)
            states: Filter by states (resources must match ANY of the provided states, or be national)
            scope: Filter by resource scope ('national', 'state', 'local', or 'all')

        Returns:
            Count of matching resources
        """
        query = select(func.count(Resource.id)).where(Resource.status != ResourceStatus.INACTIVE)

        # Apply category filter (OR logic: match any of the categories)
        if categories:
            category_conditions = [Resource.categories.contains([cat]) for cat in categories]
            query = query.where(or_(*category_conditions))

        # Apply state filter (resources in those states OR national resources)
        if states:
            state_conditions = [Resource.states.contains([s]) for s in states]
            query = query.where(
                or_(
                    Resource.scope == ResourceScope.NATIONAL,
                    *state_conditions,
                )
            )

        # Apply scope filter
        # 'national' = only national resources
        # 'state' = exclude national (show state + local)
        # 'local' = only local resources
        if scope and scope != "all":
            if scope == "state":
                # Exclude national resources (keep state and local)
                query = query.where(Resource.scope != ResourceScope.NATIONAL)
            else:
                scope_enum = ResourceScope(scope)
                query = query.where(Resource.scope == scope_enum)

        result = self.session.exec(query).one()
        return result

    def list_resources(
        self,
        categories: list[str] | None = None,
        states: list[str] | None = None,
        scope: str | None = None,
        status: ResourceStatus | None = None,
        sort: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ResourceRead], int]:
        """List resources with optional filtering.

        Args:
            categories: Filter by categories (resources must match ANY of the provided categories)
            states: Filter by states (resources must match ANY of the provided states, or be national)
            scope: Filter by resource scope ('national', 'state', 'local', or 'all')
            status: Filter by resource status
            sort: Sort order ('newest', 'alpha', 'shuffle', or 'relevance')
            tags: Filter by eligibility tags (resources must match ALL of the provided tags - AND logic)
            limit: Maximum results to return
            offset: Number of results to skip for pagination

        Returns:
            Tuple of (list of resources, total count matching filters)
        """
        # Build base query
        query = select(Resource).where(Resource.status != ResourceStatus.INACTIVE)

        # Apply category filter (OR logic: match any of the categories)
        if categories:
            category_conditions = [Resource.categories.contains([cat]) for cat in categories]
            query = query.where(or_(*category_conditions))

        # Apply state filter (resources in those states OR national resources)
        if states:
            state_conditions = [Resource.states.contains([s]) for s in states]
            query = query.where(
                or_(
                    Resource.scope == ResourceScope.NATIONAL,
                    *state_conditions,
                )
            )

        # Apply scope filter
        # 'national' = only national resources
        # 'state' = exclude national (show state + local)
        # 'local' = only local resources
        if scope and scope != "all":
            if scope == "state":
                # Exclude national resources (keep state and local)
                query = query.where(Resource.scope != ResourceScope.NATIONAL)
            else:
                scope_enum = ResourceScope(scope)
                query = query.where(Resource.scope == scope_enum)

        # Apply tags filter - search eligibility/title/description text fields and arrays
        # Tags like "hud-vash", "ssvf", "food-pantry" filter by matching content or classifications
        # Uses AND logic: resources must match ALL provided tags (selecting more tags narrows results)
        if tags:
            print(f"[ResourceService] Applying tags filter (AND logic): {tags}")
            for tag in tags:
                # Convert tag to search pattern (hud-vash -> %hud%vash% or %hud-vash%)
                search_term = f"%{tag}%"
                # Also try with spaces instead of hyphens
                search_term_spaced = f"%{tag.replace('-', ' ')}%"
                # Each tag must match - apply as separate WHERE clause (AND logic)
                query = query.where(
                    or_(
                        Resource.eligibility.ilike(search_term),
                        Resource.eligibility.ilike(search_term_spaced),
                        Resource.title.ilike(search_term),
                        Resource.title.ilike(search_term_spaced),
                        Resource.description.ilike(search_term),
                        Resource.description.ilike(search_term_spaced),
                        Resource.tags.contains([tag]),  # Check actual tags array
                        Resource.subcategories.contains([tag]),  # Check subcategories array
                    )
                )

        if status:
            query = query.where(Resource.status == status)

        # Get total count with same filters
        count_query = select(Resource.id).where(Resource.status != ResourceStatus.INACTIVE)
        if categories:
            category_conditions = [Resource.categories.contains([cat]) for cat in categories]
            count_query = count_query.where(or_(*category_conditions))
        if states:
            state_conditions = [Resource.states.contains([s]) for s in states]
            count_query = count_query.where(
                or_(
                    Resource.scope == ResourceScope.NATIONAL,
                    *state_conditions,
                )
            )
        if scope and scope != "all":
            if scope == "state":
                count_query = count_query.where(Resource.scope != ResourceScope.NATIONAL)
            else:
                scope_enum = ResourceScope(scope)
                count_query = count_query.where(Resource.scope == scope_enum)
        if tags:
            # AND logic: each tag must match (apply as separate WHERE clauses)
            for tag in tags:
                search_term = f"%{tag}%"
                search_term_spaced = f"%{tag.replace('-', ' ')}%"
                count_query = count_query.where(
                    or_(
                        Resource.eligibility.ilike(search_term),
                        Resource.eligibility.ilike(search_term_spaced),
                        Resource.title.ilike(search_term),
                        Resource.title.ilike(search_term_spaced),
                        Resource.description.ilike(search_term),
                        Resource.description.ilike(search_term_spaced),
                        Resource.tags.contains([tag]),
                        Resource.subcategories.contains([tag]),  # Also check subcategories
                    )
                )
        if status:
            count_query = count_query.where(Resource.status == status)

        total = len(self.session.exec(count_query).all())

        # Apply ordering based on sort option (secondary sort by id for stable pagination)
        if sort == "newest":
            query = query.order_by(col(Resource.created_at).desc(), col(Resource.id))
        elif sort == "alpha":
            query = query.order_by(col(Resource.title).asc(), col(Resource.id))
        elif sort == "shuffle":
            # Day-seeded random: consistent order within a day, varies day-to-day
            # Uses md5(id::text || current_date::text) for deterministic shuffling
            query = query.order_by(func.md5(func.concat(Resource.id.cast(String), func.current_date().cast(String))))
        else:
            # Default: relevance (by reliability score)
            query = query.order_by(col(Resource.reliability_score).desc(), col(Resource.id))

        query = query.offset(offset).limit(limit)

        resources = self.session.exec(query).all()
        return [self._to_read_schema(r) for r in resources], total

    def list_nearby(
        self,
        zip_code: str,
        radius_miles: int = 25,
        categories: list[str] | None = None,
        scope: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ResourceNearbyList | None:
        """List resources near a zip code, sorted by distance.

        Args:
            zip_code: 5-digit zip code for center point
            radius_miles: Search radius in miles (default 25)
            categories: Filter by categories (optional)
            scope: Filter by scope - 'national' (only nationwide), 'state' (only local/state),
                   or None (local/state + national)
            tags: Filter by eligibility tags (optional)
            limit: Maximum results to return
            offset: Number of results to skip for pagination

        Returns:
            ResourceNearbyList with resources sorted by distance, or None if zip not found
        """
        # Look up zip code center point and state
        zip_result = self.session.execute(
            text("SELECT latitude, longitude, state, geog FROM zip_codes WHERE zip_code = :zip"),
            {"zip": zip_code},
        ).fetchone()

        if not zip_result:
            return None

        center_lat, center_lng = zip_result.latitude, zip_result.longitude
        zip_state = zip_result.state  # 2-letter state code
        radius_meters = radius_miles * METERS_PER_MILE

        nearby_resources = []
        total = 0

        # Helper to build tags SQL condition
        def build_tags_sql(tags: list[str]) -> str:
            """Build SQL condition for tags filtering (matches eligibility, title, description, tags, subcategories).

            Uses AND logic: resources must match ALL provided tags (selecting more tags narrows results).
            """
            tag_conditions = []
            for tag in tags:
                # Match tag in text fields (case-insensitive) or in array fields
                search_term = f"%{tag}%"
                search_term_spaced = f"%{tag.replace('-', ' ')}%"
                tag_conditions.append(
                    f"(r.eligibility ILIKE '{search_term}' OR r.eligibility ILIKE '{search_term_spaced}' "
                    f"OR r.title ILIKE '{search_term}' OR r.title ILIKE '{search_term_spaced}' "
                    f"OR r.description ILIKE '{search_term}' OR r.description ILIKE '{search_term_spaced}' "
                    f"OR r.tags @> ARRAY['{tag}']::text[] "
                    f"OR r.subcategories @> ARRAY['{tag}']::text[])"
                )
            # AND logic: each tag condition must be satisfied
            return " AND ".join(tag_conditions)

        # If scope is 'national', only return national resources (no spatial query)
        if scope == "national":
            national_sql = """
                SELECT r.id as resource_id
                FROM resources r
                WHERE r.scope::text = 'national'
                AND r.status::text != 'inactive'
            """
            params: dict = {}

            if categories:
                category_conditions = " OR ".join([f"r.categories @> ARRAY['{cat}']::text[]" for cat in categories])
                national_sql += f" AND ({category_conditions})"

            if tags:
                tags_condition = build_tags_sql(tags)
                national_sql += f" AND ({tags_condition})"

            count_sql = f"SELECT COUNT(*) FROM ({national_sql}) as subquery"
            total = self.session.execute(text(count_sql), params).scalar() or 0

            results_sql = f"{national_sql} ORDER BY r.title ASC LIMIT :limit OFFSET :offset"
            params["limit"] = limit
            params["offset"] = offset

            results = self.session.execute(text(results_sql), params).fetchall()
            for row in results:
                resource = self.session.get(Resource, row.resource_id)
                if resource:
                    nearby_resources.append(
                        ResourceNearbyResult(
                            resource=self._to_read_schema(resource),
                            distance_miles=0,  # National = available everywhere
                        )
                    )
        else:
            # Build spatial query for local/state resources
            base_sql = """
                SELECT r.id as resource_id,
                       ST_Distance(l.geog, z.geog) / :meters_per_mile as distance_miles
                FROM resources r
                JOIN locations l ON r.location_id = l.id
                CROSS JOIN zip_codes z
                WHERE z.zip_code = :zip
                AND l.geog IS NOT NULL
                AND ST_DWithin(l.geog, z.geog, :radius_meters)
                AND r.status::text != 'inactive'
            """

            params = {
                "zip": zip_code,
                "radius_meters": radius_meters,
                "meters_per_mile": METERS_PER_MILE,
            }

            if categories:
                category_conditions = " OR ".join([f"r.categories @> ARRAY['{cat}']::text[]" for cat in categories])
                base_sql += f" AND ({category_conditions})"

            if tags:
                tags_condition = build_tags_sql(tags)
                base_sql += f" AND ({tags_condition})"

            # Get nearby resources count
            count_sql = f"SELECT COUNT(*) FROM ({base_sql}) as subquery"
            nearby_count = self.session.execute(text(count_sql), params).scalar() or 0

            # Get national resources count (if not filtering to state-only)
            national_count = 0
            if scope != "state":
                national_count_sql = """
                    SELECT COUNT(*) FROM resources r
                    WHERE r.scope::text = 'national'
                    AND r.status::text != 'inactive'
                """
                if categories:
                    category_conditions = " OR ".join([f"r.categories @> ARRAY['{cat}']::text[]" for cat in categories])
                    national_count_sql += f" AND ({category_conditions})"
                if tags:
                    tags_condition = build_tags_sql(tags)
                    national_count_sql += f" AND ({tags_condition})"
                national_count = self.session.execute(text(national_count_sql)).scalar() or 0

            total = nearby_count + national_count

            # Pagination logic: fetch nearby first, then national
            remaining_limit = limit
            current_offset = offset

            # Fetch nearby resources if we're within that range
            if current_offset < nearby_count:
                results_sql = f"""
                    {base_sql}
                    ORDER BY distance_miles ASC
                    LIMIT :limit OFFSET :offset
                """
                params["limit"] = remaining_limit
                params["offset"] = current_offset

                results = self.session.execute(text(results_sql), params).fetchall()
                for row in results:
                    resource = self.session.get(Resource, row.resource_id)
                    if resource:
                        nearby_resources.append(
                            ResourceNearbyResult(
                                resource=self._to_read_schema(resource),
                                distance_miles=round(row.distance_miles, 1),
                            )
                        )
                remaining_limit -= len(nearby_resources)
                current_offset = 0  # Reset for national query
            else:
                current_offset -= nearby_count

            # Fetch national resources if we have room and not filtering to state-only
            if remaining_limit > 0 and scope != "state":
                national_sql = """
                    SELECT r.id as resource_id
                    FROM resources r
                    WHERE r.scope::text = 'national'
                    AND r.status::text != 'inactive'
                """
                if categories:
                    category_conditions = " OR ".join([f"r.categories @> ARRAY['{cat}']::text[]" for cat in categories])
                    national_sql += f" AND ({category_conditions})"
                if tags:
                    tags_condition = build_tags_sql(tags)
                    national_sql += f" AND ({tags_condition})"

                national_sql += " ORDER BY r.title ASC LIMIT :limit OFFSET :offset"

                national_results = self.session.execute(
                    text(national_sql), {"limit": remaining_limit, "offset": current_offset}
                ).fetchall()

                for row in national_results:
                    resource = self.session.get(Resource, row.resource_id)
                    if resource:
                        nearby_resources.append(
                            ResourceNearbyResult(
                                resource=self._to_read_schema(resource),
                                distance_miles=0,  # National = available everywhere
                            )
                        )

        return ResourceNearbyList(
            resources=nearby_resources,
            total=total,
            zip_code=zip_code,
            state=zip_state,
            radius_miles=radius_miles,
            center_lat=center_lat,
            center_lng=center_lng,
        )

    def get_resource(self, resource_id: UUID) -> ResourceRead | None:
        """Get a single resource by ID."""
        resource = self.session.get(Resource, resource_id)
        if not resource:
            return None
        return self._to_read_schema(resource)

    def create_resource(self, data: ResourceCreate) -> ResourceRead:
        """Create a new resource with its organization."""
        # Find or create organization
        org_query = select(Organization).where(Organization.name == data.organization_name)
        organization = self.session.exec(org_query).first()

        if not organization:
            organization = Organization(
                name=data.organization_name,
                website=str(data.website) if data.website else None,
            )
            self.session.add(organization)
            self.session.flush()

        # Create location if address provided
        location = None
        if data.address and data.city and data.state and data.zip_code:
            location = Location(
                organization_id=organization.id,
                address=data.address,
                city=data.city,
                state=data.state,
                zip_code=data.zip_code,
            )
            self.session.add(location)
            self.session.flush()

        # Create resource
        resource = Resource(
            organization_id=organization.id,
            location_id=location.id if location else None,
            title=data.title,
            description=data.description,
            summary=data.summary,
            eligibility=data.eligibility,
            how_to_apply=data.how_to_apply,
            categories=data.categories,
            subcategories=data.subcategories,
            tags=data.tags,
            scope=data.scope,
            states=data.states,
            website=str(data.website) if data.website else None,
            phone=data.phone,
            hours=data.hours,
            languages=data.languages,
            cost=data.cost,
            status=ResourceStatus.ACTIVE,
            freshness_score=1.0,
            reliability_score=0.5,  # Default for manual entry
        )

        self.session.add(resource)
        self.session.commit()
        self.session.refresh(resource)

        return self._to_read_schema(resource)

    def update_resource(self, resource_id: UUID, data: ResourceUpdate) -> ResourceRead | None:
        """Update a resource."""
        resource = self.session.get(Resource, resource_id)
        if not resource:
            return None

        # Update fields that are provided
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "website" and value is not None:
                value = str(value)
            setattr(resource, field, value)

        resource.updated_at = datetime.now(UTC)
        self.session.add(resource)
        self.session.commit()
        self.session.refresh(resource)

        return self._to_read_schema(resource)

    def delete_resource(self, resource_id: UUID) -> bool:
        """Soft delete a resource by setting status to inactive."""
        resource = self.session.get(Resource, resource_id)
        if not resource:
            return False

        resource.status = ResourceStatus.INACTIVE
        resource.updated_at = datetime.now(UTC)
        self.session.add(resource)
        self.session.commit()
        return True

    def _to_read_schema(self, resource: Resource) -> ResourceRead:
        """Convert Resource model to read schema."""
        # Get organization
        organization = self.session.get(Organization, resource.organization_id)
        org_nested = OrganizationNested(
            id=organization.id,
            name=organization.name,
            website=organization.website,
        )

        # Get location if exists
        location_nested = None
        if resource.location_id:
            location = self.session.get(Location, resource.location_id)
            if location:
                location_nested = self._build_location_nested(location)

        # Build trust signals
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

        # Get program if exists
        program_nested = None
        if resource.program_id:
            program = self.session.get(Program, resource.program_id)
            if program:
                program_nested = ProgramNested(
                    id=program.id,
                    name=program.name,
                    program_type=program.program_type.value,
                    description=program.description,
                    services_offered=program.services_offered or [],
                )

        return ResourceRead(
            id=resource.id,
            title=resource.title,
            description=resource.description,
            summary=resource.summary,
            eligibility=resource.eligibility,
            how_to_apply=resource.how_to_apply,
            program_id=resource.program_id,
            program=program_nested,
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
