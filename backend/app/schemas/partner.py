"""Partner schemas for API validation.

Defines Pydantic schemas for partner resource submissions, including
request/response schemas for the partner API.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl

from app.models.partner import PartnerTier
from app.models.resource import ResourceScope


class PartnerResourceCreate(BaseModel):
    """Schema for partner resource submission."""

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


class PartnerResourceUpdate(BaseModel):
    """Schema for partner resource update."""

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

    model_config = {"str_strip_whitespace": True}


class PartnerResourceRead(BaseModel):
    """Resource as seen by partner (includes submission metadata)."""

    id: UUID = Field(..., description="Resource unique identifier")
    title: str
    description: str
    summary: str | None = None
    eligibility: str | None = None
    how_to_apply: str | None = None

    categories: list[str] = Field(default_factory=list)
    subcategories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    scope: ResourceScope
    states: list[str] = Field(default_factory=list)

    website: str | None = None
    phone: str | None = None
    hours: str | None = None
    languages: list[str] = Field(default_factory=list)
    cost: str | None = None

    status: str = Field(..., description="Review status: needs_review, active, inactive")

    submitted_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PartnerResourceList(BaseModel):
    """Paginated list of partner's resources."""

    resources: list[PartnerResourceRead]
    total: int
    limit: int
    offset: int


class PartnerCreate(BaseModel):
    """Admin schema for creating a new partner."""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    tier: PartnerTier = PartnerTier.COMMUNITY
    rate_limit: int = Field(default=100, ge=10, le=1000)


class PartnerRead(BaseModel):
    """Partner information returned to admins."""

    id: UUID
    name: str
    email: str
    tier: PartnerTier
    is_active: bool
    rate_limit: int
    created_at: datetime
    created_by: str | None = None
    submission_count: int = 0

    model_config = {"from_attributes": True}


class PartnerWithKey(BaseModel):
    """Partner info with API key (only returned on creation)."""

    partner: PartnerRead
    api_key: str = Field(..., description="API key - store securely, shown only once")


class PartnerSubmissionRead(BaseModel):
    """Partner submission record."""

    id: UUID
    resource_id: UUID
    submitted_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
