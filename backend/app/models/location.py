"""Location model using SQLModel."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.resource import Resource


class IncomeLimitType(str, Enum):
    """Types of income limit specifications."""

    AMI_PERCENT = "ami_percent"
    MONTHLY_ABSOLUTE = "monthly_abs"
    ANNUAL_ABSOLUTE = "annual_abs"
    UNKNOWN = "unknown"


class HousingStatus(str, Enum):
    """Housing status for eligibility filtering."""

    HOMELESS = "homeless"
    AT_RISK = "at_risk"
    STABLY_HOUSED = "stably_housed"


class VerificationSource(str, Enum):
    """Source of verification for location data."""

    OFFICIAL_DIRECTORY = "official_directory"
    PROVIDER_CONTACT = "provider_contact"
    USER_REPORT = "user_report"
    AUTOMATED = "automated"


class WaitlistStatus(str, Enum):
    """Status of waitlist for a program."""

    OPEN = "open"
    CLOSED = "closed"
    UNKNOWN = "unknown"


class BenefitType(str, Enum):
    """Types of VA benefits supported by a consult location."""

    DISABILITY = "disability"
    PENSION = "pension"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    BURIAL = "burial"
    SURVIVOR = "survivor"
    VRE = "vre"  # Vocational Rehabilitation & Employment


class RepresentativeType(str, Enum):
    """Types of accredited representatives."""

    VSO = "vso"  # Veterans Service Organization
    ATTORNEY = "attorney"
    CLAIMS_AGENT = "claims_agent"
    CVSO = "cvso"  # County Veteran Service Officer


class Location(SQLModel, table=True):
    """Physical location with geocoding and eligibility criteria."""

    __tablename__ = "locations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")

    address: str = Field(max_length=500)
    city: str = Field(max_length=100)
    state: str = Field(max_length=2)  # Two-letter code
    zip_code: str = Field(max_length=10)

    latitude: float | None = None
    longitude: float | None = None

    service_area: list[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[])
    )  # Counties/regions served

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # === Eligibility constraints ===
    age_min: int | None = Field(default=None, description="Minimum age requirement")
    age_max: int | None = Field(default=None, description="Maximum age limit")
    household_size_min: int | None = Field(default=None, description="Minimum household size")
    household_size_max: int | None = Field(default=None, description="Maximum household size")
    income_limit_type: str | None = Field(
        default=None, description="Type: ami_percent, monthly_abs, annual_abs"
    )
    income_limit_value: int | None = Field(
        default=None, description="Value for monthly/annual absolute limits"
    )
    income_limit_ami_percent: int | None = Field(
        default=None, description="AMI percentage limit (e.g., 50 for 50% AMI)"
    )
    housing_status_required: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Text), nullable=False, default=[]),
        description="Required housing status: homeless, at_risk, stably_housed",
    )
    active_duty_required: bool | None = Field(
        default=None, description="Whether active duty status is required"
    )
    discharge_required: str | None = Field(
        default=None, description="Required discharge: honorable, other_than_dishonorable"
    )
    veteran_status_required: bool = Field(
        default=True, description="Whether veteran status is required"
    )
    docs_required: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Text), nullable=False, default=[]),
        description="Documents required: DD-214, Income verification, etc.",
    )
    waitlist_status: str | None = Field(
        default=None, description="Waitlist status: open, closed, unknown"
    )

    # === Benefits consultation fields ===
    benefits_types_supported: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Text), nullable=False, default=[]),
        description="Benefits types: disability, pension, education, healthcare, burial, survivor, vre",
    )
    representative_type: str | None = Field(
        default=None, description="Accredited representative type: vso, attorney, claims_agent, cvso"
    )
    accredited: bool | None = Field(
        default=None, description="Whether representatives are VA-accredited"
    )
    walk_in_available: bool | None = Field(
        default=None, description="Whether walk-in appointments are available"
    )
    appointment_required: bool | None = Field(
        default=None, description="Whether appointments are required"
    )
    virtual_available: bool | None = Field(
        default=None, description="Whether virtual consultations are available"
    )
    free_service: bool | None = Field(
        default=None, description="Whether the consultation service is free"
    )
    languages_supported: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Text), nullable=False, default=[]),
        description="Languages supported for consultations",
    )

    # === Intake information ===
    intake_phone: str | None = Field(default=None, max_length=50, description="Intake phone number")
    intake_url: str | None = Field(
        default=None, max_length=500, description="Intake/application URL"
    )
    intake_hours: str | None = Field(
        default=None, max_length=255, description="Intake hours (e.g., Mon-Fri 9am-5pm)"
    )
    intake_notes: str | None = Field(
        default=None, description="Additional intake notes (e.g., Walk-ins welcome Tues/Thurs)"
    )

    # === Verification metadata ===
    last_verified_at: datetime | None = Field(
        default=None, description="When data was last verified"
    )
    verified_by: str | None = Field(
        default=None, description="Verification source: official_directory, provider_contact, etc."
    )
    verification_notes: str | None = Field(default=None, description="Notes about verification")

    # Relationships
    organization: "Organization" = Relationship(back_populates="locations")
    resources: list["Resource"] = Relationship(back_populates="location")
