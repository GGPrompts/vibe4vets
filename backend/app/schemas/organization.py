"""Organization schemas for API validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""

    name: str = Field(..., min_length=1, max_length=255)
    ein: str | None = Field(default=None, max_length=20)
    website: HttpUrl | None = None
    phones: list[str] = Field(default_factory=list)
    emails: list[str] = Field(default_factory=list)

    model_config = {"str_strip_whitespace": True}


class OrganizationRead(BaseModel):
    """Schema for reading an organization."""

    id: UUID
    name: str
    ein: str | None = None
    website: str | None = None
    phones: list[str]
    emails: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
