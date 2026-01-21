"""Job scheduler using APScheduler.

Provides scheduling infrastructure for background jobs with:
- Cron-style scheduling
- Manual job triggering
- Job history tracking
- Graceful startup/shutdown
"""

import asyncio
from collections import deque
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from jobs.base import BaseJob, JobResult

if TYPE_CHECKING:
    from apscheduler.job import Job as APSchedulerJob


# Maximum history entries to keep in memory
MAX_HISTORY_SIZE = 100


class JobScheduler:
    """Manages scheduled background jobs.

    Uses APScheduler's BackgroundScheduler for thread-based job execution.
    This works well with FastAPI as jobs run in background threads.

    Attributes:
        scheduler: The APScheduler instance.
        jobs: Registry of available jobs.
        history: Recent job execution history.
    """

    def __init__(self) -> None:
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.jobs: dict[str, BaseJob] = {}
        self.history: deque[JobResult] = deque(maxlen=MAX_HISTORY_SIZE)
        self._running = False

    def register_job(
        self,
        job: BaseJob,
        schedule: str | None = None,
        enabled: bool = True,
    ) -> None:
        """Register a job with optional scheduling.

        Args:
            job: The job instance to register.
            schedule: Cron expression (e.g., "0 2 * * *" for 2am daily).
                     If None, job is registered but not scheduled.
            enabled: Whether to actually schedule the job.
        """
        self.jobs[job.name] = job

        if schedule and enabled:
            self._schedule_job(job, schedule)

    def _schedule_job(self, job: BaseJob, schedule: str) -> None:
        """Schedule a job using cron expression.

        Args:
            job: The job to schedule.
            schedule: Cron expression string.
        """
        # Parse cron expression (minute hour day month day_of_week)
        parts = schedule.split()
        if len(parts) != 5:
            raise ValueError(
                f"Invalid cron expression: {schedule}. Expected 5 parts: minute hour day month day_of_week"
            )

        minute, hour, day, month, day_of_week = parts

        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
        )

        # Wrapper that runs the job and stores the result
        def job_wrapper() -> None:
            result = job.run()
            self.history.append(result)

        self.scheduler.add_job(
            job_wrapper,
            trigger=trigger,
            id=job.name,
            name=job.description,
            replace_existing=True,
        )

    def start(self) -> None:
        """Start the scheduler.

        Should be called during application startup.
        """
        if not self._running:
            self.scheduler.start()
            self._running = True
            print(f"[{datetime.now(UTC).isoformat()}] [INFO] [scheduler] Started")

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the scheduler gracefully.

        Args:
            wait: Whether to wait for running jobs to complete.
        """
        if self._running:
            self.scheduler.shutdown(wait=wait)
            self._running = False
            print(f"[{datetime.now(UTC).isoformat()}] [INFO] [scheduler] Shutdown")

    async def run_job(self, job_name: str, **kwargs: Any) -> JobResult:
        """Run a job immediately.

        Args:
            job_name: Name of the registered job to run.
            **kwargs: Additional arguments passed to the job.

        Returns:
            JobResult from the job execution.

        Raises:
            KeyError: If job_name is not registered.
        """
        if job_name not in self.jobs:
            raise KeyError(f"Job not found: {job_name}")

        job = self.jobs[job_name]

        # Run in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: job.run(**kwargs))

        self.history.append(result)

        # Reschedule the job so next_run resets from now
        # This prevents the job from running again shortly after a manual run
        scheduled_job = self.scheduler.get_job(job_name)
        if scheduled_job and scheduled_job.trigger:
            self.scheduler.reschedule_job(job_name, trigger=scheduled_job.trigger)

        return result

    def get_scheduled_jobs(self) -> list[dict[str, Any]]:
        """Get all scheduled jobs with their next run times.

        Returns:
            List of job info dictionaries.
        """
        result: list[dict[str, Any]] = []

        for job_name, job in self.jobs.items():
            info: dict[str, Any] = {
                "name": job_name,
                "description": job.description,
                "scheduled": False,
                "next_run": None,
            }

            # Check if scheduled in APScheduler
            scheduled_job: APSchedulerJob | None = self.scheduler.get_job(job_name)
            if scheduled_job:
                info["scheduled"] = True
                next_run = scheduled_job.next_run_time
                info["next_run"] = next_run.isoformat() if next_run else None

            result.append(info)

        return result

    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent job execution history.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            List of JobResult dictionaries, newest first.
        """
        # Convert deque to list and reverse for newest first
        history_list = list(self.history)[-limit:]
        history_list.reverse()
        return [result.to_dict() for result in history_list]

    def get_job(self, job_name: str) -> BaseJob | None:
        """Get a registered job by name.

        Args:
            job_name: Name of the job.

        Returns:
            The job instance or None if not found.
        """
        return self.jobs.get(job_name)

    @property
    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self._running


# Global scheduler instance
_scheduler: JobScheduler | None = None


def get_scheduler() -> JobScheduler:
    """Get or create the global scheduler instance.

    Returns:
        The global JobScheduler instance.
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = JobScheduler()
    return _scheduler


def reset_scheduler() -> None:
    """Reset the global scheduler (for testing)."""
    global _scheduler
    if _scheduler and _scheduler.is_running:
        _scheduler.shutdown(wait=False)
    _scheduler = None
