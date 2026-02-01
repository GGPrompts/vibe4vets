"""Database connection and session management using SQLModel."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# Configure connection pooling for production workloads
# - pool_size: 5 base connections for concurrent requests
# - max_overflow: 5 additional connections under load (10 total)
# - pool_pre_ping: Check connection health before use (handles stale connections)
# - pool_recycle: Recycle connections after 30 minutes (prevents timeouts)
# - connect_timeout: 10 seconds to fail fast if DB is unreachable
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"connect_timeout": 10},  # Fail fast if DB unreachable
)


def create_db_and_tables() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for database sessions."""
    with Session(engine) as session:
        yield session


# Reusable dependency type
SessionDep = Annotated[Session, Depends(get_session)]
