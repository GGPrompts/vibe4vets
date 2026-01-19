"""Resource schemas for API validation.

Defines Pydantic schemas for resource CRUD operations, search results,
and nested entity representations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.models.resource import ResourceScope, ResourceStatus


class OrganizationNested(BaseModel):
    """Organization information nested in resource responses."""

    id: UUID = Field(..., description="Organization unique identifier")
    name: str = Field(..., description="Organization name")
    website: str | None = Field(None, description="Organization website URL")


class BenefitsInfo(BaseModel):
    """Benefits consultation information for a resource location.

    Used for benefits consultation resources to indicate what
    types of benefits they assist with and how they operate.
    """

    benefits_types: list[str] = Field(
        default_factory=list,
        description="Benefits types supported: disability, pension, education, healthcare, burial, survivor, vre",
    )
    representative_type: str | None = Field(
        None, description="Type of representative: vso, attorney, claims_agent, cvso"
    )
    accredited: bool | None = Field(None, description="Whether VA-accredited")
    walk_in_available: bool | None = Field(None, description="Walk-ins accepted")
    appointment_required: bool | None = Field(None, description="Appointment required")
    virtual_available: bool | None = Field(None, description="Virtual consultations offered")
    free_service: bool | None = Field(None, description="Service is free")
    languages: list[str] = Field(default_factory=list, description="Languages supported")


class EligibilityInfo(BaseModel):
    """Eligibility constraints for a resource location.

    Used to match resources with veteran eligibility criteria.
    All fields are optional to support partial matching.
    """

    age_min: int | None = Field(None, description="Minimum age requirement")
    age_max: int | None = Field(None, description="Maximum age limit")
    household_size_min: int | None = Field(None, description="Minimum household size")
    household_size_max: int | None = Field(None, description="Maximum household size")
    income_limit_type: str | None = Field(None, description="Type of income limit (e.g., 'annual', 'monthly')")
    income_limit_value: int | None = Field(None, description="Income limit amount in dollars")
    income_limit_ami_percent: int | None = Field(None, description="Income limit as percentage of Area Median Income")
    housing_status_required: list[str] = Field(default_factory=list, description="Required housing statuses (homeless, at_risk)")
    active_duty_required: bool | None = Field(None, description="Whether active duty status is required")
    discharge_required: str | None = Field(None, description="Required discharge type (honorable, other)")
    veteran_status_required: bool = Field(True, description="Whether veteran status is required")
    docs_required: list[str] = Field(default_factory=list, description="Required documentation (DD-214, proof of income, etc.)")
    waitlist_status: str | None = Field(None, description="Current waitlist status (open, closed, limited)")


class IntakeInfo(BaseModel):
    """Intake and contact information for applying to a resource."""

    phone: str | None = Field(None, description="Intake phone number")
    url: str | None = Field(None, description="Application or intake URL")
    hours: str | None = Field(None, description="Intake hours (e.g., 'Mon-Fri 9am-5pm')")
    notes: str | None = Field(None, description="Additional intake instructions")


class VerificationInfo(BaseModel):
    """Verification metadata tracking when resource info was last confirmed."""

    last_verified_at: datetime | None = Field(None, description="When the resource was last verified")
    verified_by: str | None = Field(None, description="Who performed the verification")
    notes: str | None = Field(None, description="Verification notes or issues found")


class LocationNested(BaseModel):
    """Physical location information for a resource."""

    id: UUID = Field(..., description="Location unique identifier")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="2-letter state code")
    address: str | None = Field(None, description="Street address")
    service_area: list[str] = Field(default_factory=list, description="Areas served (counties, regions)")
    eligibility: EligibilityInfo | None = Field(None, description="Location-specific eligibility requirements")
    intake: IntakeInfo | None = Field(None, description="How to apply at this location")
    verification: VerificationInfo | None = Field(None, description="Verification status")
    benefits: BenefitsInfo | None = Field(None, description="Benefits consultation information")


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
    """Trust scoring signals indicating resource reliability and freshness.

    Every resource has a trust score = reliability × freshness.
    """

    freshness_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Freshness score (0-1) based on time since last verification",
    )
    reliability_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Reliability score (0-1) based on source tier",
    )
    last_verified: datetime | None = Field(
        None,
        description="When the resource was last verified",
    )
    source_tier: int | None = Field(
        None,
        description="Source tier (1=highest trust, 4=lowest)",
    )
    source_name: str | None = Field(
        None,
        description="Name of the data source",
    )


class ResourceRead(BaseModel):
    """Complete resource data returned from the API.

    Includes all resource fields, organization info, location details,
    and trust scoring signals.
    """

    id: UUID = Field(..., description="Resource unique identifier")
    title: str = Field(..., description="Resource title/name")
    description: str = Field(..., description="Full description of the resource")
    summary: str | None = Field(None, description="Brief summary (1-2 sentences)")
    eligibility: str | None = Field(None, description="Who qualifies for this resource")
    how_to_apply: str | None = Field(None, description="Application instructions")

    categories: list[str] = Field(..., description="Categories (employment, training, housing, legal)")
    subcategories: list[str] = Field(..., description="More specific subcategories")
    tags: list[str] = Field(..., description="Searchable tags")

    scope: ResourceScope = Field(..., description="Geographic scope (national, state, local)")
    states: list[str] = Field(..., description="States where available (2-letter codes)")

    website: str | None = Field(None, description="Official website URL")
    phone: str | None = Field(None, description="Contact phone number")
    hours: str | None = Field(None, description="Operating hours")
    languages: list[str] = Field(..., description="Languages supported")
    cost: str | None = Field(None, description="Cost information (free, sliding scale, etc.)")

    status: ResourceStatus = Field(..., description="Resource status (active, inactive, pending)")
    created_at: datetime = Field(..., description="When the resource was added")
    updated_at: datetime = Field(..., description="When the resource was last updated")

    # Nested relations
    organization: OrganizationNested = Field(..., description="Organization providing the resource")
    location: LocationNested | None = Field(None, description="Physical location if applicable")

    # Trust signals
    trust: TrustSignals = Field(..., description="Trust scoring information")

    model_config = {"from_attributes": True}


class ResourceList(BaseModel):
    """Paginated list of resources."""

    resources: list[ResourceRead] = Field(..., description="List of resources")
    total: int = Field(..., description="Total number of matching resources")
    limit: int = Field(..., description="Maximum results per page")
    offset: int = Field(..., description="Current pagination offset")


class MatchExplanation(BaseModel):
    """Explanation of why a resource matched a search query."""

    reason: str = Field(..., description="Human-readable match reason")
    field: str | None = Field(None, description="Which field matched")
    highlight: str | None = Field(None, description="Highlighted matching text")


class MatchReason(BaseModel):
    """Structured match reason for eligibility wizard results."""

    type: str = Field(
        ...,
        description="Match type: location, age, income, housing_status, veteran_status, discharge, category",
    )
    label: str = Field(..., description="Human-readable label for display")


class ResourceSearchResult(BaseModel):
    """Search result with relevance ranking and match explanations."""

    resource: ResourceRead = Field(..., description="The matched resource")
    rank: float = Field(..., ge=0.0, description="Relevance score (higher = better match)")
    explanations: list[MatchExplanation] = Field(
        ...,
        description="Why this resource matched the query",
    )
    match_reasons: list[MatchReason] = Field(
        default_factory=list,
        description="Eligibility match reasons (for eligibility search)",
    )
