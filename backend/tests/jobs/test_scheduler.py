"""Tests for the job scheduler."""

import pytest

from jobs import get_scheduler, reset_scheduler, setup_jobs
from jobs.base import BaseJob, JobStatus
from jobs.scheduler import JobScheduler


@pytest.fixture(autouse=True)
def reset_scheduler_fixture():
    """Reset the global scheduler before and after each test."""
    reset_scheduler()
    yield
    # Ensure scheduler is stopped before reset
    try:
        scheduler = get_scheduler()
        if scheduler.is_running:
            scheduler.shutdown(wait=False)
    except Exception:
        pass
    reset_scheduler()


class MockJob(BaseJob):
    """Mock job for testing."""

    def __init__(self, name: str = "mock_job", should_fail: bool = False):
        self._name = name
        self._should_fail = should_fail
        self.run_count = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return "Mock job for testing"

    def execute(self, session, **kwargs):
        self.run_count += 1
        if self._should_fail:
            raise RuntimeError("Intentional failure")
        return {
            "run_count": self.run_count,
            "kwargs": kwargs,
        }


class TestJobScheduler:
    """Tests for JobScheduler class."""

    def test_scheduler_creation(self):
        """Test that scheduler can be created."""
        scheduler = JobScheduler()
        assert scheduler is not None
        assert not scheduler.is_running
        assert len(scheduler.jobs) == 0

    def test_register_job_without_schedule(self):
        """Test registering a job without scheduling."""
        scheduler = JobScheduler()
        job = MockJob("test_job")

        scheduler.register_job(job)

        assert "test_job" in scheduler.jobs
        assert scheduler.jobs["test_job"] is job

    def test_register_job_with_schedule(self):
        """Test registering a job with a cron schedule."""
        scheduler = JobScheduler()
        job = MockJob("scheduled_job")

        scheduler.register_job(job, schedule="0 * * * *", enabled=True)

        assert "scheduled_job" in scheduler.jobs
        # Job should be in APScheduler
        scheduled = scheduler.scheduler.get_job("scheduled_job")
        assert scheduled is not None

    def test_register_job_disabled(self):
        """Test that disabled jobs are registered but not scheduled."""
        scheduler = JobScheduler()
        job = MockJob("disabled_job")

        scheduler.register_job(job, schedule="0 * * * *", enabled=False)

        assert "disabled_job" in scheduler.jobs
        # Job should NOT be in APScheduler
        scheduled = scheduler.scheduler.get_job("disabled_job")
        assert scheduled is None

    def test_invalid_cron_expression(self):
        """Test that invalid cron expressions raise an error."""
        scheduler = JobScheduler()
        job = MockJob("bad_job")

        with pytest.raises(ValueError, match="Invalid cron expression"):
            scheduler.register_job(job, schedule="invalid", enabled=True)

    def test_start_and_shutdown(self):
        """Test starting and shutting down the scheduler."""
        scheduler = JobScheduler()

        assert not scheduler.is_running
        scheduler.start()
        assert scheduler.is_running

        # Give background thread a moment to start
        import time

        time.sleep(0.1)

        scheduler.shutdown(wait=False)
        assert not scheduler.is_running

    @pytest.mark.asyncio
    async def test_run_job_manually(self):
        """Test running a job manually."""
        scheduler = JobScheduler()
        job = MockJob("manual_job")
        scheduler.register_job(job)

        result = await scheduler.run_job("manual_job")

        assert result.status == JobStatus.COMPLETED
        assert result.job_name == "manual_job"
        assert job.run_count == 1

    @pytest.mark.asyncio
    async def test_run_job_with_kwargs(self):
        """Test running a job with keyword arguments."""
        scheduler = JobScheduler()
        job = MockJob("kwarg_job")
        scheduler.register_job(job)

        result = await scheduler.run_job("kwarg_job", test_arg="test_value")

        assert result.status == JobStatus.COMPLETED
        assert result.stats.get("kwargs") == {"test_arg": "test_value"}

    @pytest.mark.asyncio
    async def test_run_job_not_found(self):
        """Test that running a non-existent job raises an error."""
        scheduler = JobScheduler()

        with pytest.raises(KeyError, match="Job not found"):
            await scheduler.run_job("nonexistent")

    @pytest.mark.asyncio
    async def test_run_failing_job(self):
        """Test that job failures are handled correctly."""
        scheduler = JobScheduler()
        job = MockJob("failing_job", should_fail=True)
        scheduler.register_job(job)

        result = await scheduler.run_job("failing_job")

        assert result.status == JobStatus.FAILED
        assert "Intentional failure" in result.error

    def test_get_scheduled_jobs(self):
        """Test getting list of scheduled jobs."""
        scheduler = JobScheduler()
        job1 = MockJob("job1")
        job2 = MockJob("job2")

        scheduler.register_job(job1, schedule="0 * * * *", enabled=True)
        scheduler.register_job(job2)  # Not scheduled

        # Start scheduler to get next_run_time values
        scheduler.start()
        import time

        time.sleep(0.1)

        jobs = scheduler.get_scheduled_jobs()

        assert len(jobs) == 2

        job1_info = next(j for j in jobs if j["name"] == "job1")
        assert job1_info["scheduled"] is True

        job2_info = next(j for j in jobs if j["name"] == "job2")
        assert job2_info["scheduled"] is False

        scheduler.shutdown(wait=False)

    @pytest.mark.asyncio
    async def test_history_tracking(self):
        """Test that job runs are tracked in history."""
        scheduler = JobScheduler()
        job = MockJob("history_job")
        scheduler.register_job(job)

        await scheduler.run_job("history_job")
        await scheduler.run_job("history_job")

        history = scheduler.get_history(limit=10)

        assert len(history) == 2
        # Most recent first
        assert all(h["job_name"] == "history_job" for h in history)

    def test_get_job(self):
        """Test getting a job by name."""
        scheduler = JobScheduler()
        job = MockJob("findable_job")
        scheduler.register_job(job)

        found = scheduler.get_job("findable_job")
        assert found is job

        not_found = scheduler.get_job("nonexistent")
        assert not_found is None


class TestGlobalScheduler:
    """Tests for global scheduler management."""

    def test_get_scheduler_singleton(self):
        """Test that get_scheduler returns the same instance."""
        scheduler1 = get_scheduler()
        scheduler2 = get_scheduler()

        assert scheduler1 is scheduler2

    def test_reset_scheduler(self):
        """Test that reset_scheduler creates a new instance."""
        scheduler1 = get_scheduler()
        scheduler1.start()
        import time

        time.sleep(0.1)
        scheduler1.shutdown(wait=False)

        reset_scheduler()

        scheduler2 = get_scheduler()
        assert scheduler1 is not scheduler2
        assert not scheduler2.is_running


class TestSetupJobs:
    """Tests for setup_jobs function."""

    def test_setup_jobs_with_schedules(self):
        """Test that setup_jobs registers jobs with schedules."""
        scheduler = JobScheduler()
        config = {
            "REFRESH_SCHEDULE": "0 2 * * *",
            "FRESHNESS_SCHEDULE": "0 * * * *",
            "SCHEDULER_ENABLED": True,
        }

        setup_jobs(scheduler, config)

        assert "refresh" in scheduler.jobs
        assert "freshness" in scheduler.jobs

        # Check they're scheduled
        assert scheduler.scheduler.get_job("refresh") is not None
        assert scheduler.scheduler.get_job("freshness") is not None

    def test_setup_jobs_disabled(self):
        """Test that jobs are registered but not scheduled when disabled."""
        scheduler = JobScheduler()
        config = {
            "REFRESH_SCHEDULE": "0 2 * * *",
            "FRESHNESS_SCHEDULE": "0 * * * *",
            "SCHEDULER_ENABLED": False,
        }

        setup_jobs(scheduler, config)

        # Jobs should be registered
        assert "refresh" in scheduler.jobs
        assert "freshness" in scheduler.jobs

        # But not scheduled
        assert scheduler.scheduler.get_job("refresh") is None
        assert scheduler.scheduler.get_job("freshness") is None

    def test_setup_jobs_no_schedules(self):
        """Test setup_jobs with no schedule configuration."""
        scheduler = JobScheduler()
        config = {
            "SCHEDULER_ENABLED": True,
        }

        setup_jobs(scheduler, config)

        # Jobs should be registered but not scheduled
        assert "refresh" in scheduler.jobs
        assert "freshness" in scheduler.jobs
        assert scheduler.scheduler.get_job("refresh") is None
        assert scheduler.scheduler.get_job("freshness") is None
