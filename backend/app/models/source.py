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


class ETLJobStatus(str, Enum):
    """Status of an ETL job run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


class ETLJobRun(SQLModel, table=True):
    """Track ETL job runs for checkpointing and resume capability.

    This model enables idempotent ETL jobs by:
    1. Recording processed source URLs to skip on retry
    2. Checkpointing progress between batches
    3. Enabling resume from failure
    """

    __tablename__ = "etl_job_runs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Job identification
    job_name: str = Field(max_length=100, index=True)  # e.g., "full_refresh", "va_gov_refresh"
    connector_names: list[str] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False)
    )  # List of connector names in this run

    # Status tracking
    status: ETLJobStatus = Field(default=ETLJobStatus.PENDING, index=True)
    started_at: datetime = Field(default_factory=_utc_now)
    completed_at: datetime | None = None

    # Progress tracking
    total_extracted: int = Field(default=0)
    total_processed: int = Field(default=0)
    total_created: int = Field(default=0)
    total_updated: int = Field(default=0)
    total_skipped: int = Field(default=0)
    total_failed: int = Field(default=0)

    # Checkpointing: track processed source URLs to skip on retry
    processed_urls: list[str] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False)
    )

    # Current position for resume (connector index + resource index)
    checkpoint_connector_idx: int = Field(default=0)
    checkpoint_resource_idx: int = Field(default=0)

    # Error details if failed
    error_message: str | None = None
    error_details: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )

    def mark_url_processed(self, url: str) -> None:
        """Mark a source URL as processed for idempotency."""
        if url not in self.processed_urls:
            self.processed_urls = [*self.processed_urls, url]

    def is_url_processed(self, url: str) -> bool:
        """Check if a source URL was already processed in this job run."""
        return url in self.processed_urls

    def update_checkpoint(self, connector_idx: int, resource_idx: int) -> None:
        """Update checkpoint position for resume capability."""
        self.checkpoint_connector_idx = connector_idx
        self.checkpoint_resource_idx = resource_idx
