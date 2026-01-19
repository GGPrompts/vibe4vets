"""Vibe4Vets API - Veteran Resource Directory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import admin, chat, feedback, resources, search
from app.config import settings
from app.database import create_db_and_tables
from jobs import get_scheduler, setup_jobs


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup - create tables if they don't exist
    create_db_and_tables()

    # Initialize and start the job scheduler
    scheduler = get_scheduler()
    scheduler_config = settings.get_scheduler_config()
    setup_jobs(scheduler, scheduler_config)

    if settings.scheduler_enabled:
        scheduler.start()

    yield

    # Shutdown - stop scheduler gracefully
    if scheduler.is_running:
        scheduler.shutdown(wait=True)


app = FastAPI(
    title="Vibe4Vets API",
    description="Veteran resource directory - Employment, Training, Housing, Legal",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(resources.router, prefix="/api/v1/resources", tags=["resources"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
