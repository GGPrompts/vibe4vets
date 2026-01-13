"""Resource service for CRUD operations."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Session, col, select

from app.models import Location, Organization, Resource, Source
from app.models.resource import ResourceStatus
from app.schemas.resource import (
    LocationNested,
    OrganizationNested,
    ResourceCreate,
    ResourceRead,
    ResourceUpdate,
    TrustSignals,
)


class ResourceService:
    """Service for resource CRUD operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_resources(
        self,
        category: str | None = None,
        state: str | None = None,
        status: ResourceStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ResourceRead], int]:
        """List resources with optional filtering."""
        # Build base query
        query = select(Resource).where(Resource.status != ResourceStatus.INACTIVE)

        # Apply filters
        if category:
            query = query.where(Resource.categories.contains([category]))
        if state:
            query = query.where(Resource.states.contains([state]))
        if status:
            query = query.where(Resource.status == status)

        # Get total count
        count_query = select(Resource.id).where(Resource.status != ResourceStatus.INACTIVE)
        if category:
            count_query = count_query.where(Resource.categories.contains([category]))
        if state:
            count_query = count_query.where(Resource.states.contains([state]))
        if status:
            count_query = count_query.where(Resource.status == status)

        total = len(self.session.exec(count_query).all())

        # Apply pagination and ordering
        query = (
            query.order_by(col(Resource.reliability_score).desc())
            .offset(offset)
            .limit(limit)
        )

        resources = self.session.exec(query).all()
        return [self._to_read_schema(r) for r in resources], total

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

    def update_resource(
        self, resource_id: UUID, data: ResourceUpdate
    ) -> ResourceRead | None:
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

        resource.updated_at = datetime.utcnow()
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
        resource.updated_at = datetime.utcnow()
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
                location_nested = LocationNested(
                    id=location.id,
                    city=location.city,
                    state=location.state,
                    address=location.address,
                )

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
