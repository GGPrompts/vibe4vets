"""Alembic migration environment for Vibe4Vets."""

import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context

# Load .env file from backend directory (same as app.config)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Import all models so SQLModel.metadata is populated
from app.models import Location, Organization, Resource, Source, SourceRecord  # noqa: F401
from app.models.partner import Partner, PartnerAPILog, PartnerSubmission  # noqa: F401
from app.models.review import ChangeLog, ReviewState  # noqa: F401

# Alembic Config object
config = context.config

# Override sqlalchemy.url from environment if DATABASE_URL is set
# Use psycopg (v3) driver - same as app.config
database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets")
# Convert postgresql:// to postgresql+psycopg:// for psycopg v3
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
config.set_main_option("sqlalchemy.url", database_url)

# Setup loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use SQLModel metadata for autogenerate
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
