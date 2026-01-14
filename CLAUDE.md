# CLAUDE.md - Vibe4Vets

## Overview

Vibe4Vets is an AI-powered veteran resource database focusing on **Employment & Training** and **Housing & Legal** resources nationwide. Transparent about using web scraping and AI to aggregate resources that go beyond VA.gov.

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
| **Resource** | Programs/services veterans can access |
| **Source** | Data sources with reliability tiers |
| **SourceRecord** | Raw data audit trail |
| **ReviewState** | Human review workflow |
| **ChangeLog** | Field-level change history |

### Resource Categories

```python
CATEGORIES = [
    "employment",    # Job placement, career services
    "training",      # Vocational rehab, certifications
    "housing",       # HUD-VASH, SSVF, shelters
    "legal",         # Legal aid, VA appeals
]
```

### Source Tiers (Trust Scoring)

| Tier | Score | Examples |
|------|-------|----------|
| 1 | 1.0 | VA.gov, DOL, HUD |
| 2 | 0.8 | DAV, VFW, American Legion |
| 3 | 0.6 | State veteran agencies |
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

Never store veteran-specific personal data. Search works without accounts.

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
| GET | `/api/v1/resources` | List/search resources |
| GET | `/api/v1/resources/{id}` | Resource detail |
| GET | `/api/v1/search` | Advanced search with filters |
| POST | `/api/v1/chat` | AI chat endpoint |

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
- [ ] Feedback loop
- [ ] Analytics
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
| `backend/scripts/seed_hubs.py` | Hub data seeding script |
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
| `frontend/src/components/DiscoveryFeed.tsx` | Date-grouped resource feed component |
| `frontend/src/app/hubs/*/page.tsx` | Static resource hub pages (employment, housing, legal, training) |
| `frontend/src/components/HubCard.tsx` | Hub resource card component |
| `frontend/src/components/ui/` | shadcn/ui components |

### Infrastructure
| File | Purpose |
|------|---------|
| `docker-compose.yml` | Local dev environment |
| `.github/workflows/ci.yml` | CI pipeline |
| `.env.example` | Environment template |

---

## Explicit Non-Goals

1. **No medical advice** - We don't diagnose or recommend treatments
2. **No eligibility determinations** - We explain, not decide
3. **No PII storage** - No veteran accounts or personal data
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
- State veteran agencies
- VSO websites (DAV, VFW, Legion)
- Legal aid directories

---

## Beads Workflow

Track work with beads (not markdown):

```bash
bd ready           # Find available work
bd show <id>       # Review issue details
bd update <id> --status=in_progress  # Claim it

# After completing work
/conductor:bdw-verify-build
/conductor:bdw-commit-changes
/conductor:bdw-close-issue <id>
bd sync && git push
```

---

## Contact

Built to help veterans find resources beyond VA.gov.
