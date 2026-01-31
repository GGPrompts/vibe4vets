"""Database connection and session management using SQLModel."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# Configure connection pooling for Railway's memory limits
# - pool_size: Reduced for low-memory environments
# - max_overflow: Minimal overflow to prevent OOM
# - pool_pre_ping: Check connection health before use (handles stale connections)
# - pool_recycle: Recycle connections after 30 minutes (prevents timeouts)
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=2,
    max_overflow=3,
    pool_pre_ping=True,
    pool_recycle=1800,
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
