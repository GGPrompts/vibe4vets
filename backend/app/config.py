"""Application configuration."""

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database - use psycopg (v3) driver
    database_url: str = "postgresql+psycopg://localhost:5432/vibe4vets"

    # CORS - accepts comma-separated string or JSON array
    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            # Handle comma-separated format: "http://localhost:3000,http://example.com"
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # AI
    anthropic_api_key: str = ""
    openai_api_key: str = ""  # For embeddings (text-embedding-3-small)

    # Environment
    environment: str = "development"
    debug: bool = True

    # Scheduler settings
    # Cron format: minute hour day month day_of_week
    refresh_schedule: str = "0 2 * * *"  # Daily at 2am
    freshness_schedule: str = "0 * * * *"  # Hourly
    link_checker_schedule: str = "0 3 * * *"  # Daily at 3am
    discovery_schedule: str = "0 4 * * *"  # Daily at 4am
    embeddings_schedule: str = "0 5 * * *"  # Daily at 5am
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
            "LINK_CHECKER_SCHEDULE": self.link_checker_schedule,
            "DISCOVERY_SCHEDULE": self.discovery_schedule,
            "EMBEDDINGS_SCHEDULE": self.embeddings_schedule,
            "SCHEDULER_ENABLED": self.scheduler_enabled,
        }


settings = Settings()
