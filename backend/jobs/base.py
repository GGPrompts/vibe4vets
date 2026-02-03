"""Base job class for background tasks.

Provides common functionality for all scheduled jobs including:
- Logging with structured output
- Error handling and retry logic
- Database session management
- Result tracking
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from sqlmodel import Session

from app.database import engine


class JobStatus(StrEnum):
    """Status of a job run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class JobResult:
    """Result of a job execution.

    Attributes:
        job_name: Name of the job that ran.
        status: Final status of the job.
        started_at: When the job started.
        completed_at: When the job finished (if completed).
        message: Human-readable summary.
        stats: Dictionary of statistics (created, updated, etc.).
        error: Error message if failed.
        run_id: Unique identifier for this run.
    """

    job_name: str
    status: JobStatus
    started_at: datetime
    completed_at: datetime | None = None
    message: str = ""
    stats: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    run_id: UUID = field(default_factory=uuid4)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "run_id": str(self.run_id),
            "job_name": self.job_name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "message": self.message,
            "stats": self.stats,
            "error": self.error,
        }


class BaseJob(ABC):
    """Base class for all background jobs.

    Provides:
    - Database session management
    - Standard logging interface
    - Error handling wrapper
    - Result tracking

    Subclasses must implement:
    - execute(): The main job logic
    - name: Job identifier
    - description: Human-readable description
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the job."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""
        pass

    def run(self, **kwargs: Any) -> JobResult:
        """Run the job with error handling and result tracking.

        Args:
            **kwargs: Additional arguments passed to execute().

        Returns:
            JobResult with status, stats, and any errors.
        """
        started_at = datetime.now(UTC)
        result = JobResult(
            job_name=self.name,
            status=JobStatus.RUNNING,
            started_at=started_at,
        )

        try:
            self._log(f"Starting job: {self.name}")

            with Session(engine) as session:
                stats = self.execute(session, **kwargs)

            result.status = JobStatus.COMPLETED
            result.completed_at = datetime.now(UTC)
            result.stats = stats
            result.message = self._format_message(stats)

            self._log(f"Completed job: {self.name} - {result.message}")

        except Exception as e:
            result.status = JobStatus.FAILED
            result.completed_at = datetime.now(UTC)
            result.error = str(e)
            result.message = f"Job failed: {str(e)}"

            self._log(f"Failed job: {self.name} - {str(e)}", level="error")

        return result

    @abstractmethod
    def execute(self, session: Session, **kwargs: Any) -> dict[str, Any]:
        """Execute the job logic.

        Must be implemented by subclasses.

        Args:
            session: Database session for queries.
            **kwargs: Additional arguments.

        Returns:
            Dictionary of statistics (created, updated, etc.).
        """
        pass

    def _format_message(self, stats: dict[str, Any]) -> str:
        """Format statistics into a human-readable message.

        Can be overridden by subclasses for custom formatting.

        Args:
            stats: Dictionary of statistics.

        Returns:
            Formatted message string.
        """
        if not stats:
            return "Completed with no statistics"

        parts = [f"{k}: {v}" for k, v in stats.items() if v is not None]
        return ", ".join(parts) if parts else "Completed"

    def _log(self, message: str, level: str = "info") -> None:
        """Log a message.

        Currently prints to stdout; can be extended to use proper logging.

        Args:
            message: Message to log.
            level: Log level (info, warning, error).
        """
        timestamp = datetime.now(UTC).isoformat()
        prefix = f"[{timestamp}] [{level.upper()}] [jobs.{self.name}]"
        print(f"{prefix} {message}")
