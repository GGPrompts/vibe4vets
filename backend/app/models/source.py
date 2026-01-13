"""Source and SourceRecord models."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


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


class Source(Base):
    """Data source with reliability tiers."""

    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), default=SourceType.SCRAPE.value)

    # Trust tier: 1=official (VA/DOL), 2=established, 3=state, 4=community
    tier: Mapped[int] = mapped_column(Integer, default=3)

    # Scrape configuration
    frequency: Mapped[str] = mapped_column(String(20), default="weekly")  # daily/weekly/monthly
    selectors: Mapped[dict | None] = mapped_column(JSONB)  # CSS selectors for scraping

    # Health tracking
    last_run: Mapped[datetime | None] = mapped_column(DateTime)
    last_success: Mapped[datetime | None] = mapped_column(DateTime)
    health_status: Mapped[str] = mapped_column(String(20), default=HealthStatus.HEALTHY.value)
    error_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    resources = relationship("Resource", back_populates="source")
    records = relationship("SourceRecord", back_populates="source")


class SourceRecord(Base):
    """Raw data audit trail."""

    __tablename__ = "source_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False
    )

    url: Mapped[str] = mapped_column(String(500), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    raw_hash: Mapped[str] = mapped_column(String(64))  # SHA-256 for change detection
    raw_path: Mapped[str | None] = mapped_column(String(500))  # S3/local path
    extracted_text: Mapped[str | None] = mapped_column(Text)

    # Relationships
    source = relationship("Source", back_populates="records")
