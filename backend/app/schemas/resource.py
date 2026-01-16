"""Resource schemas for API validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.models.resource import ResourceScope, ResourceStatus


class OrganizationNested(BaseModel):
    """Nested organization info in resource response."""

    id: UUID
    name: str
    website: str | None = None


class EligibilityInfo(BaseModel):
    """Eligibility constraints for a location."""

    age_min: int | None = None
    age_max: int | None = None
    household_size_min: int | None = None
    household_size_max: int | None = None
    income_limit_type: str | None = None
    income_limit_value: int | None = None
    income_limit_ami_percent: int | None = None
    housing_status_required: list[str] = Field(default_factory=list)
    active_duty_required: bool | None = None
    discharge_required: str | None = None
    veteran_status_required: bool = True
    docs_required: list[str] = Field(default_factory=list)
    waitlist_status: str | None = None


class IntakeInfo(BaseModel):
    """Intake information for a location."""

    phone: str | None = None
    url: str | None = None
    hours: str | None = None
    notes: str | None = None


class VerificationInfo(BaseModel):
    """Verification metadata for a location."""

    last_verified_at: datetime | None = None
    verified_by: str | None = None
    notes: str | None = None


class LocationNested(BaseModel):
    """Nested location info in resource response."""

    id: UUID
    city: str
    state: str
    address: str | None = None
    service_area: list[str] = Field(default_factory=list)
    eligibility: EligibilityInfo | None = None
    intake: IntakeInfo | None = None
    verification: VerificationInfo | None = None


class ResourceCreate(BaseModel):
    """Schema for creating a new resource."""

    # Required fields
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    organization_name: str = Field(..., min_length=1, max_length=255)

    # Optional content
    summary: str | None = None
    eligibility: str | None = None
    how_to_apply: str | None = None

    # Classification
    categories: list[str] = Field(default_factory=list)
    subcategories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    # Scope
    scope: ResourceScope = ResourceScope.NATIONAL
    states: list[str] = Field(default_factory=list)

    # Contact
    website: HttpUrl | None = None
    phone: str | None = Field(default=None, max_length=50)
    hours: str | None = Field(default=None, max_length=255)
    languages: list[str] = Field(default_factory=lambda: ["en"])
    cost: str | None = Field(default=None, max_length=100)

    # Location (optional)
    address: str | None = None
    city: str | None = None
    state: str | None = Field(default=None, max_length=2)
    zip_code: str | None = Field(default=None, max_length=10)

    model_config = {"str_strip_whitespace": True}


class ResourceUpdate(BaseModel):
    """Schema for updating a resource."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    summary: str | None = None
    eligibility: str | None = None
    how_to_apply: str | None = None

    categories: list[str] | None = None
    subcategories: list[str] | None = None
    tags: list[str] | None = None

    scope: ResourceScope | None = None
    states: list[str] | None = None

    website: HttpUrl | None = None
    phone: str | None = None
    hours: str | None = None
    languages: list[str] | None = None
    cost: str | None = None

    status: ResourceStatus | None = None

    model_config = {"str_strip_whitespace": True}


class TrustSignals(BaseModel):
    """Trust signals for a resource."""

    freshness_score: float = Field(..., ge=0.0, le=1.0)
    reliability_score: float = Field(..., ge=0.0, le=1.0)
    last_verified: datetime | None = None
    source_tier: int | None = None
    source_name: str | None = None


class ResourceRead(BaseModel):
    """Schema for reading a resource."""

    id: UUID
    title: str
    description: str
    summary: str | None = None
    eligibility: str | None = None
    how_to_apply: str | None = None

    categories: list[str]
    subcategories: list[str]
    tags: list[str]

    scope: ResourceScope
    states: list[str]

    website: str | None = None
    phone: str | None = None
    hours: str | None = None
    languages: list[str]
    cost: str | None = None

    status: ResourceStatus
    created_at: datetime
    updated_at: datetime

    # Nested relations
    organization: OrganizationNested
    location: LocationNested | None = None

    # Trust signals
    trust: TrustSignals

    model_config = {"from_attributes": True}


class ResourceList(BaseModel):
    """Paginated list of resources."""

    resources: list[ResourceRead]
    total: int
    limit: int
    offset: int


class MatchExplanation(BaseModel):
    """Explanation of why a resource matched."""

    reason: str
    field: str | None = None
    highlight: str | None = None


class MatchReason(BaseModel):
    """Structured match reason for eligibility wizard results."""

    type: str  # location, age, income, housing_status, veteran_status, discharge, category
    label: str  # Human-readable label


class ResourceSearchResult(BaseModel):
    """Search result with match explanations."""

    resource: ResourceRead
    rank: float = Field(..., ge=0.0)
    explanations: list[MatchExplanation]
    match_reasons: list[MatchReason] = Field(default_factory=list)
