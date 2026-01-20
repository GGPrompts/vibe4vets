"""Vibe4Vets API - Veteran Resource Directory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import admin, analytics, chat, email, feedback, partner, resources, search
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


API_DESCRIPTION = """
# Vibe4Vets API

AI-powered veteran resource directory focusing on **Employment & Training** and
**Housing & Legal** resources nationwide.

## Overview

Vibe4Vets aggregates veteran resources from official sources (VA.gov, DOL, HUD) and
community organizations into a searchable database with trust scoring and freshness tracking.

## Key Features

- **Full-text search** with relevance ranking and match explanations
- **Eligibility filtering** - Find resources matching veteran criteria
- **Semantic search** - AI-powered natural language queries (requires API key)
- **AI chat assistant** - Conversational resource discovery
- **Trust scoring** - Resources scored by source reliability and freshness

## Resource Categories

| Category | Description |
|----------|-------------|
| `employment` | Job placement, career counseling, resume help |
| `training` | Vocational programs, certifications, education benefits |
| `housing` | HUD-VASH, SSVF, transitional housing, emergency shelter |
| `legal` | VA appeals, discharge upgrades, legal aid |

## Authentication

Most endpoints are **public** and require no authentication.

Admin endpoints (`/api/v1/admin/*`) are for internal use and may require authentication
in production deployments.

## Rate Limiting

The chat endpoint is rate-limited to **10 requests per minute** per client to ensure
fair usage.

## Data Sources

Resources are aggregated from:
- **Tier 1** (highest trust): VA.gov, DOL, HUD
- **Tier 2**: DAV, VFW, American Legion
- **Tier 3**: State veteran agencies
- **Tier 4**: Community directories

## Privacy

We do not store any veteran PII. All searches work without accounts.
"""

app = FastAPI(
    title="Vibe4Vets API",
    description=API_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Vibe4Vets Support",
        "url": "https://github.com/vibe4vets/vibe4vets",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "resources",
            "description": "CRUD operations for veteran resources. List, search, create, update, and delete resources.",
        },
        {
            "name": "search",
            "description": (
                "Advanced search capabilities including full-text search, eligibility filtering, and semantic search."
            ),
        },
        {
            "name": "chat",
            "description": "AI-powered chat assistant for conversational resource discovery.",
        },
        {
            "name": "feedback",
            "description": "Anonymous feedback system for reporting outdated or incorrect resource information.",
        },
        {
            "name": "admin",
            "description": "Administrative endpoints for review queue, source health monitoring, and job management.",
        },
        {
            "name": "partner",
            "description": (
                "Partner API for trusted organizations (VSOs, nonprofits) to submit "
                "and manage resources via API key authentication."
            ),
        },
    ],
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
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(email.router, prefix="/api/v1/email-resources", tags=["email"])
app.include_router(partner.router, prefix="/api/v1/partner", tags=["partner"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler that preserves CORS headers on errors."""
    # Get the origin from the request
    origin = request.headers.get("origin", "")

    # Check if origin is allowed
    headers = {}
    if origin in settings.cors_origins or "*" in settings.cors_origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"

    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=headers,
    )
