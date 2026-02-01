"""Internal DTOs for ETL pipeline."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class NormalizedResource:
    """Normalized and validated resource ready for database insertion.

    This is the internal representation after normalization but before
    database loading.
    """

    # Required fields
    title: str
    description: str
    source_url: str
    org_name: str

    # Organization
    org_website: str | None = None

    # Location (optional)
    address: str | None = None
    city: str | None = None
    state: str | None = None  # 2-letter code
    zip_code: str | None = None

    # Classification
    categories: list[str] = field(default_factory=list)
    subcategories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    # Contact
    phone: str | None = None
    email: str | None = None
    hours: str | None = None

    # Content
    eligibility: str | None = None
    how_to_apply: str | None = None

    # Scope
    scope: str = "national"  # national, state, local
    states: list[str] = field(default_factory=list)

    # Trust signals (set by enricher)
    reliability_score: float = 0.5
    source_tier: int = 4

    # Geo (set by enricher)
    latitude: float | None = None
    longitude: float | None = None

    # Metadata
    raw_data: dict[str, Any] | None = None
    fetched_at: datetime | None = None
    source_name: str | None = None
    content_hash: str | None = None  # For deduplication

    def has_location(self) -> bool:
        """Check if resource has address info for a Location record."""
        return bool(self.address and self.city and self.state and self.zip_code)

    def location_key(self) -> str | None:
        """Generate a key for location matching."""
        if not self.has_location():
            return None
        return f"{self.address}|{self.city}|{self.state}|{self.zip_code}".lower()

    def org_key(self) -> str:
        """Generate a key for organization matching."""
        return self.org_name.lower().strip()

    def dedup_key(self) -> str:
        """Generate a key for deduplication.

        Uses org + location + title similarity.
        """
        loc = self.location_key() or "no-location"
        return f"{self.org_key()}|{loc}|{self.title.lower().strip()}"


@dataclass
class ETLStats:
    """Statistics for an ETL run."""

    extracted: int = 0
    normalized: int = 0
    normalized_failed: int = 0
    deduplicated: int = 0  # Number removed as duplicates
    enriched: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0

    @property
    def total_processed(self) -> int:
        """Total successfully processed records."""
        return self.created + self.updated + self.skipped


@dataclass
class ETLError:
    """Error during ETL processing."""

    stage: str  # extract, normalize, dedupe, enrich, load
    message: str
    resource_title: str | None = None
    source_url: str | None = None
    exception: str | None = None
    category: str | None = None  # transient, network, auth_failure, http_error, parse, unknown


@dataclass
class ETLResult:
    """Result of an ETL pipeline run."""

    success: bool
    stats: ETLStats
    errors: list[ETLError] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    source_name: str | None = None

    @property
    def duration_seconds(self) -> float | None:
        """Calculate duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class LoadResult:
    """Result of loading a single resource."""

    resource_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None
    action: str = "skipped"  # created, updated, skipped, failed
    error: str | None = None
    retriable: bool = False  # True if error is transient and operation can be retried
