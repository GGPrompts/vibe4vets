"""Background job system for Vibe4Vets.

This module provides:
- Job scheduler using APScheduler
- Refresh job for connector data sync
- Freshness job for trust score updates
- Link checker job for URL health validation
- Discovery job for AI-powered resource discovery
- Job registry and configuration
"""

from jobs.base import BaseJob, JobResult, JobStatus
from jobs.discovery import DiscoveryJob
from jobs.freshness import FreshnessJob
from jobs.link_checker import LinkCheckerJob
from jobs.refresh import RefreshJob, get_available_connectors
from jobs.scheduler import JobScheduler, get_scheduler, reset_scheduler


def setup_jobs(scheduler: JobScheduler, config: dict[str, str | bool]) -> None:
    """Configure and register all jobs with the scheduler.

    Reads configuration to determine schedules and whether jobs
    should be enabled.

    Args:
        scheduler: The JobScheduler instance to configure.
        config: Configuration dictionary with keys:
            - REFRESH_SCHEDULE: Cron expression for refresh job
            - FRESHNESS_SCHEDULE: Cron expression for freshness job
            - SCHEDULER_ENABLED: Whether to enable scheduling

    Example config:
        {
            "REFRESH_SCHEDULE": "0 2 * * *",     # Daily at 2am
            "FRESHNESS_SCHEDULE": "0 * * * *",   # Hourly
            "SCHEDULER_ENABLED": True,
        }
    """
    enabled = config.get("SCHEDULER_ENABLED", True)

    # Register refresh job
    refresh_schedule = config.get("REFRESH_SCHEDULE")
    scheduler.register_job(
        RefreshJob(),
        schedule=refresh_schedule if isinstance(refresh_schedule, str) else None,
        enabled=bool(enabled) and bool(refresh_schedule),
    )

    # Register freshness job
    freshness_schedule = config.get("FRESHNESS_SCHEDULE")
    scheduler.register_job(
        FreshnessJob(),
        schedule=freshness_schedule if isinstance(freshness_schedule, str) else None,
        enabled=bool(enabled) and bool(freshness_schedule),
    )

    # Register link checker job
    link_checker_schedule = config.get("LINK_CHECKER_SCHEDULE")
    scheduler.register_job(
        LinkCheckerJob(),
        schedule=link_checker_schedule if isinstance(link_checker_schedule, str) else None,
        enabled=bool(enabled) and bool(link_checker_schedule),
    )

    # Register discovery job
    discovery_schedule = config.get("DISCOVERY_SCHEDULE")
    scheduler.register_job(
        DiscoveryJob(),
        schedule=discovery_schedule if isinstance(discovery_schedule, str) else None,
        enabled=bool(enabled) and bool(discovery_schedule),
    )


__all__ = [
    # Base
    "BaseJob",
    "JobResult",
    "JobStatus",
    # Jobs
    "DiscoveryJob",
    "FreshnessJob",
    "LinkCheckerJob",
    "RefreshJob",
    "get_available_connectors",
    # Scheduler
    "JobScheduler",
    "get_scheduler",
    "reset_scheduler",
    "setup_jobs",
]
