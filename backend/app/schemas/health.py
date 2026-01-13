"""Health and dashboard schemas for admin API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorRecord(BaseModel):
    """Record of a source error."""

    id: UUID
    source_id: UUID
    source_name: str
    error_type: str
    message: str
    occurred_at: datetime
    job_run_id: str | None = None

    model_config = {"from_attributes": True}


class JobRunSummary(BaseModel):
    """Summary of a job run for dashboard display."""

    run_id: str
    job_name: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    message: str
    resources_processed: int = 0
    errors: int = 0


class DashboardStats(BaseModel):
    """Aggregated statistics for the admin dashboard."""

    total_sources: int
    sources_by_status: dict[str, int] = Field(
        default_factory=dict,
        description="Count by health status: healthy, degraded, failing",
    )
    total_resources: int
    resources_by_category: dict[str, int] = Field(
        default_factory=dict,
        description="Count by category: employment, training, housing, legal",
    )
    resources_by_status: dict[str, int] = Field(
        default_factory=dict,
        description="Count by resource status: active, needs_review, inactive",
    )
    stale_resources: int = Field(
        description="Resources not verified in 30 days",
    )
    recent_job_runs: list[JobRunSummary] = Field(
        default_factory=list,
        description="Recent job execution summaries",
    )


class SourceHealthDetail(BaseModel):
    """Detailed health information for a single source."""

    source_id: str
    name: str
    url: str
    tier: int
    source_type: str
    frequency: str
    status: str
    resource_count: int
    resources_by_status: dict[str, int] = Field(
        default_factory=dict,
        description="Count by resource status",
    )
    average_freshness: float = Field(
        ge=0.0,
        le=1.0,
        description="Average freshness score of resources (0-1)",
    )
    last_run: datetime | None = None
    last_success: datetime | None = None
    error_count: int = 0
    success_rate: float = Field(
        ge=0.0,
        le=1.0,
        default=1.0,
        description="Success rate over last 10 runs (0-1)",
    )
    errors: list[ErrorRecord] = Field(
        default_factory=list,
        description="Recent error records",
    )

    model_config = {"from_attributes": True}


class SourceHealthListResponse(BaseModel):
    """Response for list of source health details."""

    sources: list[SourceHealthDetail]
    total: int


class ErrorListResponse(BaseModel):
    """Response for list of errors across all sources."""

    errors: list[ErrorRecord]
    total: int
