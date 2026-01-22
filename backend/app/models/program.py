"""Program model using SQLModel - represents funded programs/grants run by organizations."""

import uuid
from datetime import UTC, date, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel


def _utc_now() -> datetime:
    return datetime.now(UTC)


if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.resource import Resource


class ProgramType(str, Enum):
    """Type of veteran program/grant."""

    SSVF = "ssvf"  # Supportive Services for Veteran Families
    HUD_VASH = "hud_vash"  # HUD-VA Supportive Housing
    GPD = "gpd"  # Grant and Per Diem
    HCHV = "hchv"  # Health Care for Homeless Veterans
    VETS = "vets"  # Jobs for Veterans State Grants
    OTHER = "other"


class ProgramStatus(str, Enum):
    """Status of the program/grant."""

    ACTIVE = "active"
    ENDED = "ended"
    PENDING = "pending"  # Awarded but not yet started


class Program(SQLModel, table=True):
    """A funded program or grant operated by an organization.

    Examples: SSVF grants, HUD-VASH programs, etc. One organization
    can run multiple programs serving different geographic areas.
    """

    __tablename__ = "programs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)

    # Program identification
    name: str = Field(max_length=255)
    program_type: ProgramType = Field(default=ProgramType.OTHER)
    grant_number: str | None = Field(default=None, max_length=100, index=True)
    external_id: str | None = Field(default=None, max_length=100)  # Source system ID

    # Description
    description: str | None = None
    services_offered: list[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[])
    )  # Specific services: "rapid re-housing", "homelessness prevention", etc.

    # Geographic coverage
    service_areas: list[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[])
    )  # Counties/regions served
    states: list[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[])
    )  # State codes served

    # Funding period
    start_date: date | None = None
    end_date: date | None = None
    fiscal_year: str | None = Field(default=None, max_length=10)  # e.g., "FY26"

    # Contact for this specific program
    phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=500)

    # Status
    status: ProgramStatus = Field(default=ProgramStatus.ACTIVE)
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)

    # Relationships
    organization: "Organization" = Relationship(back_populates="programs")
    resources: list["Resource"] = Relationship(back_populates="program")
