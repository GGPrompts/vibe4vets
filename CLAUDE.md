# CLAUDE.md - Vibe4Vets

## Overview

Vibe4Vets is an AI-powered Veteran resource database focusing on **Employment & Training** and **Housing & Legal** resources nationwide. Transparent about using web scraping and AI to aggregate resources that go beyond VA.gov.

## Style Guide

**Always capitalize "Veteran"** - Per VA style guidelines, "Veteran" is always capitalized when referring to U.S. military Veterans. This applies to all user-facing text, documentation, and code comments.

- ✅ "Resources for Veterans"
- ✅ "Veteran employment services"
- ❌ "resources for veterans"
- ❌ "veteran employment services"

Exceptions: Technical identifiers (variable names, URL slugs, database fields) may use lowercase per coding conventions.

| | |
|--|--|
| **Type** | Veteran Resource Directory |
| **Backend** | Python 3.12 + FastAPI + SQLModel |
| **Frontend** | Next.js 15 + TypeScript + Tailwind + shadcn/ui |
| **Database** | PostgreSQL (Supabase/Railway) |
| **ORM** | SQLModel (unified SQLAlchemy + Pydantic) |
| **Search** | Postgres FTS → OpenSearch (Phase 3) |
| **AI** | Claude API (extraction, search, chat) |

---

## Architecture

### Two-Service Pattern

```
┌─────────────────┐      ┌─────────────────┐
│   Next.js UI    │ ──── │   FastAPI API   │
│   (Vercel)      │      │   (Railway)     │
└─────────────────┘      └────────┬────────┘
                                  │
                         ┌────────┴────────┐
                         │   PostgreSQL    │
                         │   (+ pgvector)  │
                         └─────────────────┘
```

### Directory Layout

```
vibe4vets/
├── frontend/                # Next.js app (Vercel)
│   └── src/
│       ├── app/             # App Router pages
│       ├── components/      # React components
│       └── lib/             # API client, utilities
│
├── backend/                 # FastAPI app (Railway)
│   ├── app/
│   │   ├── api/v1/          # API routes
│   │   ├── models/          # SQLModel models (unified ORM + validation)
│   │   ├── services/        # Business logic
│   │   └── core/            # Taxonomy, geo, utils
│   ├── connectors/          # Data source connectors
│   ├── etl/                 # Normalize, dedupe, enrich
│   ├── jobs/                # Background tasks
│   └── llm/                 # AI abstraction layer
│
├── prompts/                 # Saved AI prompts
├── docs/                    # Architecture docs
└── .beads/                  # Issue tracking
```

---

## Core Data Model

### Entities

| Entity | Purpose |
|--------|---------|
| **Organization** | Parent entity (nonprofits, agencies) |
| **Location** | Physical locations with geocoding |
| **Resource** | Programs/services Veterans can access |
| **Source** | Data sources with reliability tiers |
| **SourceRecord** | Raw data audit trail |
| **ReviewState** | Human review workflow |
| **ChangeLog** | Field-level change history |

### Resource Categories

```python
CATEGORIES = [
    "employment",       # Job placement, career services
    "training",         # Vocational rehab, certifications
    "housing",          # HUD-VASH, SSVF, shelters
    "legal",            # Legal aid, VA appeals
    "food",             # Food pantries, meal programs
    "benefits",         # VA claims, benefits counseling
    "mentalHealth",     # Counseling, PTSD support, crisis services
    "supportServices",  # Peer mentoring, case management
    "healthcare",       # Medical care, VA health services
    "education",        # College programs, scholarships
    "financial",        # Financial counseling, emergency assistance
    "family",           # Spouses, dependents, survivors, childcare
]
```

### Subcategories & Tag Filtering

Resources have three classification arrays that work together:

| Field | Purpose | Example |
|-------|---------|---------|
| `categories` | Primary classification | `["food", "housing"]` |
| `subcategories` | Specific resource type | `["food-pantry", "meal-program"]` |
| `tags` | Additional attributes | `["case-management", "veteran"]` |

**Critical: Keep taxonomy and data aligned**

The frontend tag filters (`/api/v1/taxonomy/tags/{category}`) must match actual values in `subcategories` and `tags` arrays:

- **Taxonomy file**: `backend/app/core/taxonomy.py` → `ELIGIBILITY_TAGS`
- **Filter logic**: `backend/app/services/resource.py` → searches both `tags` AND `subcategories`

When adding new connectors or seeding data:
1. Use existing subcategory values from taxonomy (prefer hyphens: `food-pantry` not `food_pantry`)
2. If new subcategories needed, add them to `ELIGIBILITY_TAGS` in taxonomy.py
3. Test filters: `curl "http://localhost:8000/api/v1/resources?categories=X&tags=Y"`

**Common subcategories by category:**
- **food**: `food-pantry`, `meal-program`, `mobile-distribution`, `groceries`, `food-bank`
- **housing**: `hud-vash`, `ssvf`, `emergency-shelter`, `supportive_housing`, `rental_assistance`

### Source Tiers (Trust Scoring)

| Tier | Score | Examples |
|------|-------|----------|
| 1 | 1.0 | VA.gov, DOL, HUD |
| 2 | 0.8 | DAV, VFW, American Legion |
| 3 | 0.6 | State Veteran agencies |
| 4 | 0.4 | Community directories |

---

## Key Design Decisions

### 1. Trust Pipeline

Every resource has a trust score = reliability × freshness:
- **Reliability**: Based on source tier
- **Freshness**: Decays over time since last verification
- **Risky changes** (phone, address, eligibility) trigger human review

### 2. Connector Interface

All data sources implement:
```python
class Connector(Protocol):
    def run(self) -> list[ResourceCandidate]: ...
    def metadata(self) -> SourceMetadata: ...
```

### 3. "Why This Matched"

Search results always explain the match:
- "Matches your location (Texas)"
- "Covers employment resources"
- "Last verified: 3 days ago"

### 4. No PII Storage

Never store Veteran-specific personal data. Search works without accounts.

### 5. Audit Trail

Keep raw scraped content with hashes for traceability.

---

## Commands

### Backend Development

```bash
cd backend

# Setup
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run locally
uvicorn app.main:app --reload

# Database
alembic upgrade head
alembic revision --autogenerate -m "description"

# Tests
pytest
```

### Frontend Development

```bash
cd frontend

# Setup
npm install

# Run locally (connects to backend at localhost:8000)
npm run dev

# Build
npm run build
```

### Docker (Full Stack)

```bash
docker-compose up -d
```

---

## API Structure

### Public Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/resources` | List resources with pagination (limit, offset) and filters (categories, states, scope) |
| GET | `/api/v1/resources/{id}` | Resource detail |
| GET | `/api/v1/search` | Advanced search with filters |
| GET | `/api/v1/search/eligibility` | Eligibility-filtered search with match reasons |
| POST | `/api/v1/chat` | AI chat endpoint |
| POST | `/api/v1/analytics/events` | Record anonymous analytics event |

### Admin Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/admin/review-queue` | Pending reviews |
| POST | `/api/v1/admin/review/{id}` | Approve/reject |
| GET | `/api/v1/admin/sources` | Source health |
| GET | `/api/v1/admin/dashboard/stats` | Aggregated dashboard stats |
| GET | `/api/v1/admin/dashboard/sources` | All sources with health |
| GET | `/api/v1/admin/dashboard/errors` | Recent errors |
| GET | `/api/v1/admin/jobs` | List scheduled jobs |
| POST | `/api/v1/admin/jobs/{name}/run` | Trigger job manually |
| GET | `/api/v1/admin/jobs/history` | Job run history |
| GET | `/api/v1/admin/jobs/connectors` | Available connectors |
| GET | `/api/v1/analytics/admin/dashboard` | Full analytics dashboard data |
| GET | `/api/v1/analytics/admin/summary` | Summary statistics |
| GET | `/api/v1/analytics/admin/popular-searches` | Popular search queries |
| GET | `/api/v1/analytics/admin/popular-categories` | Popular categories |
| GET | `/api/v1/analytics/admin/popular-states` | Popular states |
| GET | `/api/v1/analytics/admin/popular-resources` | Most viewed resources |
| GET | `/api/v1/analytics/admin/wizard-funnel` | Wizard completion funnel |
| GET | `/api/v1/analytics/admin/daily-trends` | Daily event trends |

---

## Phases

### Phase 0: Scaffolding (COMPLETE)
- [x] Directory structure
- [x] Docker Compose (pgvector, backend, frontend)
- [x] Database schema (Alembic migrations)
- [x] Connector interface
- [x] CI/CD (GitHub Actions)

### Phase 1: MVP (COMPLETE)
- [x] Manual resource entry
- [x] Basic CRUD API (`backend/app/api/v1/resources.py`)
- [x] Postgres full-text search (`backend/app/services/search.py`)
- [x] Next.js UI (search + results)
- [x] Admin review queue (`frontend/src/app/admin/page.tsx`)

### Phase 2: Automation (COMPLETE)
- [x] VA.gov connector (`backend/connectors/va_gov.py`)
- [x] DOL/CareerOneStop connector (`backend/connectors/careeronestop.py`)
- [x] ETL pipeline (`backend/etl/`)
- [x] Scheduled refresh (`backend/jobs/`)
- [x] Source health dashboard (`backend/app/services/health.py`)

### Phase 3: AI + Scale
- [ ] Claude extraction
- [ ] pgvector semantic search
- [ ] AI chatbot
- [ ] Guided questionnaire
- [ ] OpenSearch (if needed)

### Phase 4: Production
- [ ] Public API docs
- [x] Feedback loop
- [x] Analytics (privacy-respecting usage tracking)
- [ ] Partner contributions

---

## Key Files

### Backend
| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app entry point |
| `backend/app/api/v1/resources.py` | Resource CRUD endpoints |
| `backend/app/api/v1/search.py` | Full-text search endpoint |
| `backend/app/api/v1/admin.py` | Admin endpoints (review, jobs, dashboard) |
| `backend/app/models/resource.py` | Resource SQLModel |
| `backend/app/services/trust.py` | Trust scoring logic |
| `backend/app/services/search.py` | PostgreSQL FTS service |
| `backend/app/services/health.py` | Source health monitoring |
| `backend/app/core/taxonomy.py` | Categories and subcategories |
| `backend/alembic/versions/` | Database migrations |
| `backend/connectors/base.py` | Connector protocol interface |
| `backend/connectors/va_gov.py` | VA.gov Lighthouse API connector |
| `backend/connectors/careeronestop.py` | DOL CareerOneStop API connector |
| `backend/etl/pipeline.py` | ETL orchestrator |
| `backend/etl/normalize.py` | Data normalization |
| `backend/etl/dedupe.py` | Duplicate detection |
| `backend/etl/loader.py` | Database loader |
| `backend/jobs/scheduler.py` | APScheduler integration |
| `backend/jobs/refresh.py` | Full refresh job |
| `backend/jobs/freshness.py` | Freshness update job |
| `backend/app/services/discovery.py` | AI-powered resource discovery service |
| `backend/app/models/analytics.py` | Anonymous analytics models |
| `backend/app/services/analytics.py` | Analytics tracking service |
| `backend/app/api/v1/analytics.py` | Analytics API endpoints |
| `backend/scripts/seed_hubs.py` | Hub data seeding script |
| `backend/scripts/seed_dmv_housing.py` | DC/MD/VA housing seed data with eligibility |
| `backend/.claude/commands/scan-resources.md` | Discovery slash command |

### Frontend
| File | Purpose |
|------|---------|
| `frontend/src/app/page.tsx` | Landing page |
| `frontend/src/app/search/page.tsx` | Search UI with filters |
| `frontend/src/app/discover/page.tsx` | Discovery feed with date-grouped resources |
| `frontend/src/app/resources/[id]/page.tsx` | Resource detail page |
| `frontend/src/app/admin/page.tsx` | Admin review queue |
| `frontend/src/lib/api.ts` | API client with TypeScript types |
| `frontend/src/lib/hooks/useResourcesInfinite.ts` | TanStack Query hook for paginated resource fetching |
| `frontend/src/components/providers.tsx` | QueryClientProvider wrapper for TanStack Query |
| `frontend/src/components/DiscoveryFeed.tsx` | Date-grouped resource feed component |
| `frontend/src/components/EligibilityWizard.tsx` | Eligibility wizard with URL state persistence |
| `frontend/src/components/MatchReasonChips.tsx` | Match reason chips for search results |
| `frontend/src/app/hubs/*/page.tsx` | Static resource hub pages (employment, housing, legal, training) |
| `frontend/src/components/HubCard.tsx` | Hub resource card component |
| `frontend/src/components/ui/` | shadcn/ui components |
| `frontend/src/lib/useAnalytics.ts` | Analytics tracking React hook |
| `frontend/src/app/admin/analytics/page.tsx` | Admin analytics dashboard |

### Infrastructure
| File | Purpose |
|------|---------|
| `docker-compose.yml` | Local dev environment |
| `.github/workflows/ci.yml` | CI pipeline |
| `.github/workflows/link-check.yml` | Scheduled external link checker |
| `.env.example` | Environment template |

### Maintenance
```bash
# Check curated external links (requires network access)
python backend/scripts/check_links.py
```

---

## Explicit Non-Goals

1. **No medical advice** - We don't diagnose or recommend treatments
2. **No eligibility determinations** - We explain, not decide
3. **No PII storage** - No Veteran accounts or personal data
4. **No benefits decision engine** - We're a directory, not a processor

---

## Data Sources

### Tier 1: Official APIs
- [VA Developer API](https://developer.va.gov/) - Facilities, services
- [CareerOneStop API](https://www.careeronestop.org/Developers/WebAPI/web-api.aspx) - Job resources
- [USAJobs API](https://developer.usajobs.gov/) - Federal jobs

### Tier 2: Structured Scraping
- VA.gov Employment pages
- DOL VETS Resources
- HUD-VASH program info
- SSVF provider listings

### Tier 3: Nonprofit/Community
- State Veteran agencies
- VSO websites (DAV, VFW, Legion)
- Legal aid directories

---

## Connector → Database Pipeline

### ETL Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CONNECTOR (backend/connectors/*.py)                          │
│    connector.run() → list[ResourceCandidate]                    │
│    - Fetches from APIs, files, or web scraping                  │
│    - Returns normalized candidates with metadata                │
└───────────────────────────────┬─────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. NORMALIZE (backend/etl/normalize.py)                         │
│    - Validates required fields                                  │
│    - Cleans and standardizes data                               │
│    - Outputs NormalizedResource                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. DEDUPLICATE (backend/etl/dedupe.py)                          │
│    - Removes duplicates across sources                          │
│    - Uses title similarity (85% threshold)                      │
│    - Keeps highest-tier source version                          │
└───────────────────────────────┬─────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. ENRICH (backend/etl/enrich.py)                               │
│    - Geocodes addresses (Census API)                            │
│    - Calculates trust scores                                    │
│    - Adds derived tags                                          │
└───────────────────────────────┬─────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. LOAD (backend/etl/loader.py)                                 │
│    - Upserts Resource, Location, SourceRecord                   │
│    - Handles conflicts (update vs create)                       │
│    - Triggers review for risky changes                          │
└─────────────────────────────────────────────────────────────────┘
```

### Running Connectors

**Via Admin API (production):**
```bash
# Run all connectors
POST /api/v1/admin/jobs/refresh/run

# Run specific connector
POST /api/v1/admin/jobs/refresh/run?connector_name=gpd

# Dry run (no DB changes)
POST /api/v1/admin/jobs/refresh/run?dry_run=true
```

**Via Python (development/testing):**
```python
from sqlmodel import Session
from connectors import GPDConnector, VetCentersConnector
from etl import ETLPipeline

with Session(engine) as session:
    pipeline = ETLPipeline(session=session)

    # Dry run - see what would be created
    result = pipeline.dry_run([GPDConnector()])
    print(f"Would create: {result.stats.extracted} resources")

    # Real run - commits to database
    result = pipeline.run([GPDConnector(), VetCentersConnector()])
    print(f"Created: {result.stats.created}, Updated: {result.stats.updated}")
```

**Via CLI script:**
```bash
cd backend
python -c "
from app.db import get_engine
from sqlmodel import Session
from connectors import GPDConnector
from etl import ETLPipeline

engine = get_engine()
with Session(engine) as session:
    result = ETLPipeline(session).run([GPDConnector()])
    print(f'Created: {result.stats.created}')
"
```

### Adding a New Connector

1. **Create connector file** (`backend/connectors/my_connector.py`):
   ```python
   from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

   class MyConnector(BaseConnector):
       @property
       def metadata(self) -> SourceMetadata:
           return SourceMetadata(
               name="My Data Source",
               url="https://example.com",
               tier=2,  # 1=federal, 2=nonprofit, 3=state, 4=community
               frequency="weekly",
           )

       def run(self) -> list[ResourceCandidate]:
           # Fetch and return resources
           return [ResourceCandidate(...)]
   ```

2. **Register in exports** (`backend/connectors/__init__.py`):
   ```python
   from connectors.my_connector import MyConnector
   __all__ = [..., "MyConnector"]
   ```

3. **Register in job system** (`backend/jobs/refresh.py`):
   ```python
   CONNECTOR_REGISTRY = {
       ...,
       "my_connector": MyConnector,
   }
   ```

4. **Add reference data** (if file-based): `backend/data/reference/my_data.json`

5. **Write tests**: `backend/tests/connectors/test_my_connector.py`

### Registered Connectors

| Name | Connector | Source | Tier |
|------|-----------|--------|------|
| `va_gov` | VAGovConnector | VA Lighthouse API | 1 |
| `vet_centers` | VetCentersConnector | VA Lighthouse API | 1 |
| `careeronestop` | CareerOneStopConnector | DOL API | 1 |
| `gi_bill_schools` | GIBillSchoolsConnector | VA GIDS API | 1 |
| `apprenticeship` | ApprenticeshipConnector | CareerOneStop API | 1 |
| `ssvf` | SSVFConnector | VA SSVF Awards | 1 |
| `hud_vash` | HUDVASHConnector | HUD-VASH Awards | 1 |
| `gpd` | GPDConnector | VA GPD Awards | 1 |
| `vboc` | VBOCConnector | SBA.gov | 1 |
| `skillbridge` | SkillBridgeConnector | DOD SkillBridge | 1 |
| `legal_aid` | LegalAidConnector | LSC Directory | 2 |
| `veterans_court` | VeteransCourtConnector | Justice for Vets | 2 |
| `certifications` | CertificationsConnector | Curated | 2 |
| `veteran_employers` | VeteranEmployersConnector | Curated | 2 |
| `state_va` | StateVAConnector | State Agencies | 3 |
| `cvso` | CVSOConnector | NACVSO | 3 |
| `two_one_one` | TwoOneOneConnector | 211.org | 4 |
| `united_way` | UnitedWayConnector | United Way | 4 |

---

## Beads Workflow

Track work with beads (not markdown). Always use `--json` flag for structured output.

### Worker Workflow

1. **Find work**: `bd ready --json`
2. **Claim it**: `bd update ID --status in_progress --json`
3. **Discover new work?** Create linked issue:
   ```bash
   bd create "Found issue" --deps discovered-from:PARENT-ID --json
   ```
4. **Add progress notes** (for context recovery):
   ```bash
   bd update ID --notes "Implemented X, still need Y"
   ```
5. **Complete**: `bd close ID --reason "Done: summary" --json`
6. **Sync**: `bd sync` (commits and pushes)

### Essential Commands

```bash
bd ready --json              # Unblocked issues
bd show ID --json            # Details with notes
bd update ID --status in_progress --json  # Claim
bd update ID --notes "Progress notes"     # Context
bd close ID --reason "Done: what was done" --json
bd create "Title" --deps discovered-from:PARENT --json  # Link discovered work
```

### Session Close Protocol

**CRITICAL**: Session is NOT complete until `git push` succeeds.

```bash
bd close ID --reason "Done: summary" --json  # Close finished work
bd sync                      # Export/commit/push beads
git push                     # MUST succeed before ending
```

Include issue ID in commits: `git commit -m "Fix bug (bd-abc)"`

---

## Documentation Standards

Docs are **LLM-optimized**. README.md is for humans; everything else is for agents.

| File | Update When |
|------|-------------|
| `CLAUDE.md` / `AGENTS.md` | API, schema, workflow, or structure changes |
| `CHANGELOG.md` | Features, fixes, breaking changes (200 line limit) |
| `docs/*.md` | Specs, detailed API docs, architecture decisions |

**Full guide:** `docs/documentation-standards.md`

**After completing work:** Run `/update-docs` to update CHANGELOG and sync docs.

---

## Contact

Built to help Veterans find resources beyond VA.gov.
