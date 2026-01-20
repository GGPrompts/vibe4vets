"""Resource model using SQLModel - the core entity."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlmodel import Field, Relationship, SQLModel

# Embedding dimension for text-embedding-3-small (OpenAI) or equivalent
EMBEDDING_DIMENSION = 1536

if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.organization import Organization
    from app.models.program import Program
    from app.models.review import ChangeLog, ReviewState
    from app.models.source import Source


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


class Resource(SQLModel, table=True):
    """Veteran resource - a program or service."""

    __tablename__ = "resources"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")
    program_id: uuid.UUID | None = Field(default=None, foreign_key="programs.id", index=True)
    location_id: uuid.UUID | None = Field(default=None, foreign_key="locations.id")

    # Content
    title: str = Field(max_length=255)
    description: str
    summary: str | None = None  # AI-generated
    eligibility: str | None = None
    how_to_apply: str | None = None

    # Classification - PostgreSQL text arrays
    categories: list[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[])
    )  # employment, training, housing, legal
    subcategories: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[]))
    tags: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[]))

    # Scope
    scope: ResourceScope = Field(default=ResourceScope.NATIONAL)
    states: list[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(Text), nullable=False, default=[])
    )  # ['*'] for national

    # Contact
    website: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=50)
    hours: str | None = Field(default=None, max_length=255)
    languages: list[str] = Field(
        default_factory=lambda: ["en"],
        sa_column=Column(ARRAY(Text), nullable=False, default=["en"]),
    )
    cost: str | None = Field(default=None, max_length=100)  # free, sliding scale, etc.

    # Trust signals
    source_id: uuid.UUID | None = Field(default=None, foreign_key="sources.id")
    source_url: str | None = Field(default=None, max_length=500)
    last_scraped: datetime | None = None
    last_verified: datetime | None = None
    freshness_score: float = Field(default=1.0)  # 0-1
    reliability_score: float = Field(default=0.5)  # 0-1

    # Link health tracking (populated by link_checker job)
    link_checked_at: datetime | None = None
    link_http_status: int | None = None
    link_health_score: float | None = None  # 0-1, AI-determined
    link_flagged_reason: str | None = Field(default=None, max_length=500)

    # State
    status: ResourceStatus = Field(default=ResourceStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Full-text search vector (auto-populated by trigger or manually)
    search_vector: str | None = Field(default=None, sa_column=Column(TSVECTOR))

    # Vector embedding for semantic search (pgvector)
    embedding: Any = Field(
        default=None,
        sa_column=Column(Vector(EMBEDDING_DIMENSION), nullable=True),
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="resources")
    program: Optional["Program"] = Relationship(back_populates="resources")
    location: Optional["Location"] = Relationship(back_populates="resources")
    source: Optional["Source"] = Relationship(back_populates="resources")
    reviews: list["ReviewState"] = Relationship(back_populates="resource")
    changes: list["ChangeLog"] = Relationship(back_populates="resource")
