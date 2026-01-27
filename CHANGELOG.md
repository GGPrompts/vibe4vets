# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

#### Embeddings & Semantic Search (2026-01-26)
- **Local SentenceTransformers support** - Run semantic search embeddings locally without external API calls (370018b)
- **Model initialization assertions** - Type-safe model loading with proper null checks (923fed3)
- **Embedding test improvements** - Skip tests gracefully when sentence-transformers unavailable (6d31c3e, b533da3)

#### Geocoding & Distance Search (2026-01-24)
- **PostGIS integration** - Enable geography column for spatial queries (a7c6949)
- **Zip code centroids** - Load US zip code centroids for distance calculations (c18feaa)
- **Census API geocoding** - Geocode all 1,345 locations with Census geocoder (987df5c)
- **Nearby search endpoint** - `/api/v1/resources/nearby` for zip code proximity search (7b5a9a9)
- **Distance sort option** - Sort resources by distance from user's zip code (8bc1d50)
- **Zip code search UI** - Frontend zip code input with distance display (3daaa8a)

#### Connectors (2026-01-23-25)
- **10 new veteran resource connectors** - GPD, VBOC, SkillBridge, StateVA, CVSO, VeteransCourt, Certifications, VeteranEmployers, GIBillSchools, Apprenticeship (48fbd12)
- **211 connector** - 383 veteran resources from 211.org across all 50 states + DC (0fd08df, 1c315ec)
- **United Way connector** - Missions United programs for veteran support (04ec18f, ef56ab9)
- **HUD-VASH PHA contacts** - Add PHA contact lookup to HUD-VASH connector (3759580)
- **Retry logic** - Exponential backoff for API connector resilience (8da73f8)
- **HTTP client cleanup** - Close HTTP clients in connectors to prevent resource leaks (758d411)

#### Saved Resources & Bookmarks (2026-01-20)
- **Bookmark functionality** - Save resources to localStorage with bookmark icon (241f82e, b25873e)
- **Export and email** - Export saved resources as PDF, share via email (241f82e)
- **Bookmark button placement** - Gold bookmark button in resource detail modal header (f496598, 6f4b561)
- **Virtualized grid bookmarks** - Bookmark button stays attached in virtualized grid (3f85c3e)

#### Landing Page & Filter Builder (2026-01-19-21)
- **Homepage redesign** - Filters-first layout with navy header (ea4813d, V4V-kj4m)
- **Live resource count** - Real-time count in header updates with filter changes (0897181, 1d22958)
- **Resource count API** - `/api/v1/resources/count` endpoint for live filter counts (1fbed8f)
- **Category card toggles** - Make category cards toggleable for filter builder (b0149a6)
- **Map multi-select** - Toggle multiple states on US map (daf1132)
- **Sort chips UI** - Sort options on landing page filter builder (0835dc2)
- **Shuffle sort** - Random shuffle option for discovery (8ab414e)
- **DC and territory buttons** - Clickable buttons below US map (5f193cc)
- **How It Works revamp** - Updated for filter builder flow (602505b)
- **New logo** - Full version on landing, wordmark in header (ba5a41c, c906f5b)

#### Admin & Analytics (2026-01-19-21)
- **Admin dashboard revamp** - Improved styling for dashboard and analytics sections (5617454)
- **About page** - Transparency information page (a09bc1c)
- **AI transparency section** - AI usage disclosure on About page (9d1d2cd)
- **API key authentication** - Secure all admin endpoints (b66aaa0)
- **Partner API** - Resource submission API for partners (b9c0d89)

#### Food & Benefits Resources (2026-01-20-21)
- **Food category** - New food assistance category with color styling (decabd9)
- **Benefits category** - New benefits category for veteran benefits resources (decabd9)
- **140 food resources** - National food assistance database for veterans (cdb6615, 7d13df8)
- **Benefits discovery** - Jacksonville, Nashville, and Midwest veteran benefits (def8058)

#### UI Enhancements (2026-01-19-26)
- **Resource logos** - Display organization logos via Google favicon API (2883c7a, 77909ec)
- **Grid virtualization** - @tanstack/react-virtual for efficient rendering (72f0d59)
- **Mobile load more** - Fallback button for mobile infinite scroll (3ef9651)
- **States filter search** - Search input for faster state selection (97b7159)
- **Magnifying glass a11y** - Accessibility feature for text enlargement (b9df1e8)
- **React error boundaries** - Graceful error handling in frontend (8651f92)
- **Hierarchical grouping** - Group resources by organization (ce1a002)

#### ETL & Infrastructure (2026-01-21-24)
- **Custom PostgreSQL image** - PostGIS + pgvector in CI (f642823)
- **ETL checkpointing** - Idempotent pipeline with checkpoint recovery (20153b1)
- **Search vector trigger** - Automatic tsvector updates (4dbf750)
- **Turbopack** - Enable Next.js Turbopack for faster builds (8a757a0)

### Fixed

#### Geocoding & Search (2026-01-24-25)
- **National resources in nearby** - Include national scope resources in proximity search (d5366dd)
- **Timezone-naive dates** - Handle last_verified without timezone in search explanations (9abe809)

#### UI Fixes (2026-01-19-26)
- **Badge contrast** - Improve badge visibility on white header backgrounds (e76d89b)
- **Modal z-index** - Fix resource card modal stacking issues (77909ec)
- **Modal gradient** - Fix resource detail modal gradient transparency (2918d54)
- **Magnifier hide** - Hide magnifier when resource card modal is expanded (98c0c36)
- **Card animation** - Use layoutId shared element transition (b917ff6)
- **Nested anchors** - Prevent invalid anchor nesting in link variant cards (252eaa5)
- **Search button size** - Prevent jumping on homepage (46f0647)
- **Sidebar filters** - Move filters icon to top of collapsed sidebar (52e2de8)
- **Sort dropdown** - Click-to-toggle instead of hover (7e2aecb)
- **Hydration mismatch** - Fix resource count badge hydration (57a8e61)
- **Search page UX** - Sidebar overlay, header always visible, grid performance (ec97320)

#### Admin Panel (2026-01-19-21)
- **Review queue** - Fix content overflow and usability issues (e0d9980)
- **Table columns** - Fix column overlap in review queue (97e048b)
- **Dashboard styling** - Fix table overflow, tabs, error handling (79693a2)
- **Sheet styling** - Fix admin panel loading states and flash (d932f3e)
- **Race condition** - Prevent race condition in resource fetch (567c3ef)
- **Loading state** - Reset resourceLoading on sheet close (270c360)

#### Backend Fixes (2026-01-21-26)
- **Varchar limits** - Increase limits to handle long content (4759950)
- **Phone field** - Increase to 150 chars for complex numbers (ca61655)
- **N+1 query** - Fix N+1 in health service (4297761)
- **Null checks** - Add null checks for organization lookups (511d469)
- **datetime.utcnow()** - Replace deprecated calls with datetime.now(UTC) (0550fa0)
- **Job scheduling** - Reschedule job after manual run (cb48022)
- **ConnectorInfo sync** - Align frontend with backend API fields (1022df9, af39e2c)
- **211 categories** - Complete category mapping for all 211 resources (dd6fdfc)
- **Link health migration** - Add missing tracking columns (83ffde8)

#### CI/CD (2026-01-21-24)
- **CI migrations** - Run Alembic migrations before tests (ef04220)
- **CI failures** - Fix lint errors and search_vector generated column (66a9b1a)
- **Ruff formatting** - Fix lint and mypy errors across codebase (9fdb3ac, b5a3d2b)

#### Accessibility & Content (2026-01-22)
- **Veteran capitalization** - Capitalize Veteran/Veterans throughout UI (61dfd35)
- **ARIA improvements** - Improve frontend accessibility with ARIA and touch targets (76f754a)
- **Uncategorized resources** - Add categories to 10 VA resources (f0dbdea)
- **Taxonomy tests** - Update for 6 categories (benefits, food added) (309f165)

### Changed
- **Landing page search flow** - Unified filter builder experience (ef0e4b3)
- **Zip input placement** - Move into Sort by section (c6dc2ba)

---

#### Infinite Scroll & Data Fetching (2026-01-18)
- **Infinite scroll pagination** - Load More with useInfiniteQuery, shows "X of Y resources" (V4V-rqr)
- **Server-side filtering** - API supports categories, states, scope params with correct totals (V4V-8mn)
- **TanStack Query** - Data fetching layer with QueryClientProvider (V4V-1zu)

#### Data Sources (2026-01-17)
- **SSVF connector** - Import FY26 grantee data (235 organizations) from Excel (V4V-ct9)
- **Legal aid connector** - 129 LSC-funded legal aid programs imported (V4V-6l4)
- **HUD-VASH connector** - 153 PHA-VAMC partnership records imported (V4V-1ta)
- **AI discovery prompts** - `.prompts/` directory with housing, employment, food discovery prompts (V4V-625)
- **AI discovery pipeline** - Automated Haiku discovery → Sonnet validation → review queue (V4V-3ml)
- **Resource Hub pages** - Static hub pages for employment, housing, legal, training categories (V4V-9fn)

#### Search & Discovery UX (2026-01-16)
- **Interactive US map** - SVG map on landing page hero for geographic browsing (V4V-num)
- **Eligibility wizard** - No-PII wizard with location-based eligibility filtering (V4V-d6k)
- **Animated card expansion** - Framer Motion layoutId for resource detail modal (V4V-i59)
- **Horizontal filter bar** - Sort dropdown in search header (V4V-cri)
- **Search filters redesign** - AnimatePresence-based sidebar (V4V-3hw)

#### Resource Display (2026-01-15)
- **Tags and eligibility badges** - Display tags, state badges on resource cards (V4V-wzt)
- **Local provider contacts** - Show provider contact info on cards and detail modal (V4V-v9o)
- **Location eligibility details** - Eligibility info imported with Location entities (V4V-2gn)
- **Provider-to-program model** - Program model with organization relationships (V4V-3cf)
- **pgvector semantic search** - Embedding column and EmbeddingService for similarity matching (V4V-7ke)

### Fixed

#### UX Fixes (2026-01-18)
- **Infinite scroll UX** - Preserve scroll position, disable animations during pagination (V4V-gey)
- **Sidebar layout shift** - Use invisible class instead of conditional render for Clear Filters (V4V-kgb)
- **Admin dashboard transparency** - Fixed CSS issues with Light Tokyo Night theme (V4V-g2z)
- **Search bar contrast** - Fixed white-on-white text (V4V-search-text-contrast)
- **Skeleton colors** - Changed from yellow to gray (V4V-skeleton-colors)
- **Dropdown placeholders** - Fixed empty state display (V4V-empty-dropdowns)
- **CI failures** - Fixed psycopg2 module import in GitHub Actions (V4V-vcc)
- **Person-first language** - Replaced 'homeless' terminology with person-first language (V4V-3wh)

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
