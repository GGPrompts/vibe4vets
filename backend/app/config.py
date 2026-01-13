"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database - use psycopg (v3) driver
    database_url: str = "postgresql+psycopg://localhost:5432/vibe4vets"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # AI
    anthropic_api_key: str = ""

    # Environment
    environment: str = "development"
    debug: bool = True

    # Scheduler settings
    # Cron format: minute hour day month day_of_week
    refresh_schedule: str = "0 2 * * *"  # Daily at 2am
    freshness_schedule: str = "0 * * * *"  # Hourly
    scheduler_enabled: bool = True  # Can disable in dev

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def get_scheduler_config(self) -> dict[str, str | bool]:
        """Get scheduler configuration dictionary.

        Returns:
            Dictionary with scheduler settings for jobs.setup_jobs()
        """
        return {
            "REFRESH_SCHEDULE": self.refresh_schedule,
            "FRESHNESS_SCHEDULE": self.freshness_schedule,
            "SCHEDULER_ENABLED": self.scheduler_enabled,
        }


settings = Settings()
