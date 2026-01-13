"""Resource model - the core entity."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ResourceStatus(str, Enum):
    """Resource review status."""

    ACTIVE = "active"
    NEEDS_REVIEW = "needs_review"
    INACTIVE = "inactive"


class ResourceScope(str, Enum):
    """Geographic scope of resource."""

    NATIONAL = "national"
    STATE = "state"
    LOCAL = "local"


class Resource(Base):
    """Veteran resource - a program or service."""

    __tablename__ = "resources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id")
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)  # AI-generated
    eligibility: Mapped[str | None] = mapped_column(Text)
    how_to_apply: Mapped[str | None] = mapped_column(Text)

    # Classification
    categories: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list
    )  # employment, training, housing, legal
    subcategories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Scope
    scope: Mapped[str] = mapped_column(String(20), default=ResourceScope.NATIONAL.value)
    states: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list
    )  # ['*'] for national

    # Contact
    website: Mapped[str | None] = mapped_column(String(500))
    phone: Mapped[str | None] = mapped_column(String(50))
    hours: Mapped[str | None] = mapped_column(String(255))
    languages: Mapped[list[str]] = mapped_column(ARRAY(String), default=["en"])
    cost: Mapped[str | None] = mapped_column(String(100))  # free, sliding scale, etc.

    # Trust signals
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id")
    )
    source_url: Mapped[str | None] = mapped_column(String(500))
    last_scraped: Mapped[datetime | None] = mapped_column(DateTime)
    last_verified: Mapped[datetime | None] = mapped_column(DateTime)
    freshness_score: Mapped[float] = mapped_column(Float, default=1.0)  # 0-1
    reliability_score: Mapped[float] = mapped_column(Float, default=0.5)  # 0-1

    # State
    status: Mapped[str] = mapped_column(String(20), default=ResourceStatus.ACTIVE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Note: embedding column will be added via migration with pgvector

    # Relationships
    organization = relationship("Organization", back_populates="resources")
    location = relationship("Location", back_populates="resources")
    source = relationship("Source", back_populates="resources")
    reviews = relationship("ReviewState", back_populates="resource")
    changes = relationship("ChangeLog", back_populates="resource")
