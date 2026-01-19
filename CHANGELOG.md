# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

#### Infinite Scroll & Data Fetching (2026-01-18)
- **Infinite scroll pagination** - Load More with useInfiniteQuery, shows "X of Y resources" (V4V-rqr)
- **Server-side filtering** - API supports categories, states, scope params with correct totals (V4V-8mn)
- **TanStack Query** - Data fetching layer with QueryClientProvider (V4V-1zu)

#### Data Sources (2026-01-17)
- **SSVF connector** - Import FY26 grantee data (235 organizations) from Excel (V4V-ct9)
- **AI discovery prompts** - `.prompts/` directory with housing, employment, food discovery prompts (V4V-625)
- **Resource Hub pages** - Static hub pages for employment, housing, legal, training categories (V4V-9fn)

### Fixed

#### UX Fixes (2026-01-18)
- **Infinite scroll UX** - Preserve scroll position, disable animations during pagination (V4V-gey)
- **Sidebar layout shift** - Use invisible class instead of conditional render for Clear Filters (V4V-kgb)
- **Admin dashboard transparency** - Fixed CSS issues with Light Tokyo Night theme (V4V-g2z)
- **Search bar contrast** - Fixed white-on-white text (V4V-search-text-contrast)
- **Skeleton colors** - Changed from yellow to gray (V4V-skeleton-colors)
- **Dropdown placeholders** - Fixed empty state display (V4V-empty-dropdowns)
- **CI failures** - Fixed psycopg2 module import in GitHub Actions (V4V-vcc)

### Changed
- **Search page redesign** - Sidebar filters with card grid layout (V4V-search-redesign)

---

#### UX + Coverage Improvements (2026-01-14)
- **Territory + DC support** - State pickers include DC and territories (PR/GU/VI/AS/MP), and `/map` includes territory links (V4V-07y)
- **Discover page upgrades** - Added search entrypoint and consistent select styling on `/discover` (V4V-a1i)

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
- **Header shift when selects open** - Fixed layout shift caused by scroll-lock scrollbar compensation (V4V-vbt)
- **Scrollbar gutter flash** - Styled scrollbar track to match background (cream) during scroll-lock (V4V-21u)
- **/map runtime errors** - Fixed React setState-in-render and map context errors on Browse by State (V4V-5ts, V4V-9px)
- **/search filtering edge case** - Filters now apply even when a single category/state is selected (V4V-07y)
- **Mobile /search layout** - Responsive filter sheet width and reduced excess padding on small screens (V4V-kgf)

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
