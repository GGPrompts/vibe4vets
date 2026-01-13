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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
