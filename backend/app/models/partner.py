"""Partner model for API key authentication and resource submissions."""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel


def _utc_now() -> datetime:
    return datetime.now(UTC)


if TYPE_CHECKING:
    from app.models.resource import Resource


class PartnerTier(int, Enum):
    """Partner trust tier - maps to source tiers."""

    ESTABLISHED = 2  # DAV, VFW, American Legion
    STATE = 3  # State veteran agencies
    COMMUNITY = 4  # Community organizations


class Partner(SQLModel, table=True):
    """Partner organization with API key for resource submissions."""

    __tablename__ = "partners"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    email: str = Field(max_length=255, unique=True, index=True)

    # API key stored as SHA-256 hash
    api_key_hash: str = Field(max_length=64)

    # Trust tier for submitted resources
    tier: PartnerTier = Field(default=PartnerTier.COMMUNITY)

    # Status
    is_active: bool = Field(default=True)

    # Rate limiting - requests per hour
    rate_limit: int = Field(default=100)
    rate_limit_count: int = Field(default=0)
    rate_limit_reset_at: datetime | None = None

    # Audit
    created_at: datetime = Field(default_factory=_utc_now)
    created_by: str | None = Field(default=None, max_length=100)  # Admin who created

    # Relationships
    submissions: list["PartnerSubmission"] = Relationship(back_populates="partner")
    api_logs: list["PartnerAPILog"] = Relationship(back_populates="partner")

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key using SHA-256."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key."""
        return f"v4v_{secrets.token_urlsafe(32)}"


class PartnerSubmission(SQLModel, table=True):
    """Track partner resource submissions."""

    __tablename__ = "partner_submissions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    partner_id: uuid.UUID = Field(foreign_key="partners.id", index=True)
    resource_id: uuid.UUID = Field(foreign_key="resources.id", index=True)

    submitted_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime | None = None

    # Relationships
    partner: "Partner" = Relationship(back_populates="submissions")
    resource: "Resource" = Relationship()


class PartnerAPILog(SQLModel, table=True):
    """Audit log for partner API calls."""

    __tablename__ = "partner_api_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    partner_id: uuid.UUID = Field(foreign_key="partners.id", index=True)

    endpoint: str = Field(max_length=100)
    method: str = Field(max_length=10)
    status_code: int
    request_summary: str | None = Field(default=None, max_length=500)

    timestamp: datetime = Field(default_factory=_utc_now, index=True)

    # Relationships
    partner: "Partner" = Relationship(back_populates="api_logs")
