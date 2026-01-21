"""Source and SourceRecord models using SQLModel."""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


def _utc_now() -> datetime:
    return datetime.now(UTC)

if TYPE_CHECKING:
    from app.models.resource import Resource


class SourceErrorType(str, Enum):
    """Type of source error."""

    CONNECTION = "connection"  # Network/API errors
    PARSE = "parse"  # Data parsing failures
    VALIDATION = "validation"  # Data validation errors
    TIMEOUT = "timeout"  # Request timeouts
    AUTH = "auth"  # Authentication failures
    RATE_LIMIT = "rate_limit"  # Rate limiting
    UNKNOWN = "unknown"  # Unknown errors


class SourceType(str, Enum):
    """Type of data source."""

    API = "api"
    SCRAPE = "scrape"
    MANUAL = "manual"


class HealthStatus(str, Enum):
    """Source health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"


class Source(SQLModel, table=True):
    """Data source with reliability tiers."""

    __tablename__ = "sources"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    url: str = Field(max_length=500)
    source_type: SourceType = Field(default=SourceType.SCRAPE)

    # Trust tier: 1=official (VA/DOL), 2=established, 3=state, 4=community
    tier: int = Field(default=3)

    # Scrape configuration
    frequency: str = Field(default="weekly", max_length=20)  # daily/weekly/monthly
    selectors: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )  # CSS selectors for scraping

    # Health tracking
    last_run: datetime | None = None
    last_success: datetime | None = None
    health_status: HealthStatus = Field(default=HealthStatus.HEALTHY)
    error_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=_utc_now)

    # Relationships
    resources: list["Resource"] = Relationship(back_populates="source")
    records: list["SourceRecord"] = Relationship(back_populates="source")
    errors: list["SourceError"] = Relationship(back_populates="source")


class SourceRecord(SQLModel, table=True):
    """Raw data audit trail."""

    __tablename__ = "source_records"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    resource_id: uuid.UUID = Field(foreign_key="resources.id")
    source_id: uuid.UUID = Field(foreign_key="sources.id")

    url: str = Field(max_length=500)
    fetched_at: datetime = Field(default_factory=_utc_now)
    raw_hash: str = Field(max_length=64)  # SHA-256 for change detection
    raw_path: str | None = Field(default=None, max_length=500)  # S3/local path
    extracted_text: str | None = None

    # Relationships
    source: "Source" = Relationship(back_populates="records")


class SourceError(SQLModel, table=True):
    """Error records for source health tracking."""

    __tablename__ = "source_errors"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    source_id: uuid.UUID = Field(foreign_key="sources.id", index=True)

    error_type: SourceErrorType = Field(default=SourceErrorType.UNKNOWN)
    message: str
    details: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )  # Stack trace, request info, etc.

    job_run_id: str | None = Field(default=None, max_length=50)  # Links to scheduler history
    occurred_at: datetime = Field(default_factory=_utc_now, index=True)

    # Relationships
    source: "Source" = Relationship(back_populates="errors")
