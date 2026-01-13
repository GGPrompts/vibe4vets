# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

#### Frontend Improvements (2026-01-13)
- **Admin Dashboard Stats** - Wire up real API data for Approved Today and Total Resources stats (V4V-2d8)
- **Admin Navigation Menu** - Sidebar navigation with links to Review Queue, Sources, and Jobs pages (V4V-ndx)
- **Admin Source Health page** (`frontend/src/app/admin/sources/page.tsx`) - Monitor connector health
- **Admin Job Management page** (`frontend/src/app/admin/jobs/page.tsx`) - View and trigger background jobs
- **Landing Page Redesign** - Editorial aesthetic with custom typography, hero section, category highlights (V4V-nbt)
- **Frontend README** (`frontend/README.md`) - Setup, API client, and component documentation (V4V-4ae)

### Fixed
- **Dropdown styling** - Added solid backgrounds and proper text colors to category/state selects (V4V-8xa)
- **Dropdown positioning** - Changed to popper positioning to prevent page layout shift (V4V-dmr)

#### Phase 2: Automation (COMPLETE)
- **DOL CareerOneStop connector** (`backend/connectors/careeronestop.py`)
  - Fetches American Job Centers from DOL API
  - Covers all 53 US states/territories with deduplication
  - Includes veteran representative contact info
  - 25 unit tests

- **ETL Pipeline** (`backend/etl/`)
  - `normalize.py` - Data validation, phone/state/URL normalization
  - `dedupe.py` - Fuzzy duplicate detection across sources
  - `enrich.py` - Tag extraction, category inference, geocoder stub
  - `loader.py` - Database operations with conflict handling
  - `pipeline.py` - Orchestrator chaining all steps
  - 59 unit tests

- **Scheduled Refresh** (`backend/jobs/`)
  - APScheduler integration with FastAPI lifespan
  - `RefreshJob` - Runs connectors through ETL pipeline
  - `FreshnessJob` - Updates freshness scores hourly
  - Admin API endpoints for job management
  - Configurable via REFRESH_SCHEDULE, FRESHNESS_SCHEDULE env vars
  - 39 unit tests

- **Source Health Dashboard** (`backend/app/services/health.py`)
  - `HealthService` with dashboard stats aggregation
  - Error tracking with `SourceError` model
  - Health status calculation (healthy/degraded/failing)
  - Dashboard API endpoints at `/api/v1/admin/dashboard/*`
  - 24 unit tests

- VA.gov Lighthouse Facilities API connector (`backend/connectors/va_gov.py`)
  - Fetches health, benefits, and vet center facilities
  - Implements Connector protocol with pagination and error handling
  - 17 unit tests with mocked API responses

### Fixed
- Removed duplicate `test_health.py` that failed with SQLite ARRAY types
- Removed machine-specific PRIME.md symlink from git tracking
- SQLModel relationship fixes for SQLite test compatibility

## [0.1.0] - 2026-01-13

### Added

#### Phase 0: Project Scaffolding
- Docker Compose configuration with PostgreSQL (pgvector), backend, and frontend services
- Alembic migrations with full database schema including:
  - Organizations, Locations, Resources tables
  - Sources, SourceRecords for data provenance
  - ReviewState, ChangeLog for audit trail
  - Full-text search with tsvector and GIN indexes
  - PostgreSQL ARRAY fields for categories, tags, states
- GitHub Actions CI pipeline (lint, type-check, tests)
- Core taxonomy definitions (employment, training, housing, legal categories)
- Environment configuration with `.env.example`
- Test infrastructure with pytest

#### Phase 1: MVP - Working Directory
- **Backend API:**
  - Resource CRUD endpoints with pagination (`/api/v1/resources`)
  - Full-text search with category/state filters (`/api/v1/search`)
  - Admin review queue endpoints (`/api/v1/admin`)
  - Trust scoring service with freshness decay
  - Pydantic schemas for request/response validation

- **Frontend UI:**
  - Search page with category filters and state dropdown
  - Resource detail page with trust signals (last verified, source tier)
  - Admin review queue with approve/reject actions
  - shadcn/ui component library (Button, Card, Dialog, Table, etc.)
  - API client library with TypeScript types
  - Responsive design with Tailwind CSS

### Tech Stack
- Backend: Python 3.12, FastAPI, SQLModel, Alembic, PostgreSQL
- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui
- Infrastructure: Docker Compose, GitHub Actions CI
