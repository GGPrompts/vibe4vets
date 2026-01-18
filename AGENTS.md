# AGENTS.md - Vibe4Vets

Instructions for AI agents (Claude Code, Codex, Cursor, etc.) working on this project.

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
├── .prompts/                # AI discovery prompts
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
| GET | `/api/v1/search/eligibility` | Eligibility-filtered search with match reasons |
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
| `backend/app/services/discovery.py` | AI-powered resource discovery service |
| `backend/app/core/taxonomy.py` | Categories and subcategories |
| `backend/connectors/base.py` | Connector protocol interface |
| `backend/etl/pipeline.py` | ETL orchestrator |
| `backend/scripts/import_discoveries.py` | Import AI-discovered resources |

### Frontend
| File | Purpose |
|------|---------|
| `frontend/src/app/page.tsx` | Landing page |
| `frontend/src/app/search/page.tsx` | Search UI with filters |
| `frontend/src/app/discover/page.tsx` | Discovery feed |
| `frontend/src/app/resources/[id]/page.tsx` | Resource detail page |
| `frontend/src/app/admin/page.tsx` | Admin review queue |
| `frontend/src/lib/api.ts` | API client with TypeScript types |
| `frontend/src/components/ui/` | shadcn/ui components |

### AI Discovery
| File | Purpose |
|------|---------|
| `.prompts/discovery/` | Resource discovery prompts |
| `.prompts/validation/` | Validation prompts |
| `backend/.claude/commands/scan-resources.md` | Discovery slash command |

---

## Explicit Non-Goals

1. **No medical advice** - We don't diagnose or recommend treatments
2. **No eligibility determinations** - We explain, not decide
3. **No PII storage** - No veteran accounts or personal data
4. **No benefits decision engine** - We're a directory, not a processor

---

## Beads Workflow

Track work with beads (`bd` command). Use `--json` flag for structured output.

### Essential Commands

```bash
bd ready --json              # Find unblocked work
bd show ID --json            # View issue details
bd update ID --status in_progress --json  # Claim work
bd update ID --notes "Progress notes"     # Add context
bd close ID --reason "Done: summary" --json  # Complete
bd create "Title" --deps discovered-from:PARENT --json  # Link new work
bd sync                      # Sync with git
```

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

### Session Close Protocol

**CRITICAL**: Session is NOT complete until `git push` succeeds.

```bash
bd close ID --reason "Done: summary" --json  # Close finished work
bd sync                      # Export/commit/push beads
git push                     # MUST succeed before ending
```

Include issue ID in commits: `git commit -m "Fix bug (bd-abc)"`

---

## AI Resource Discovery Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. DISCOVER                                                     │
│    Run prompts from .prompts/discovery/ (use Haiku for volume)  │
│    Or use /scan-resources slash command                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. SAVE                                                         │
│    Save JSON to: backend/data/discoveries/                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. IMPORT                                                       │
│    python -m backend.scripts.import_discoveries <file.json>     │
│    (use --dry-run to preview first)                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. REVIEW                                                       │
│    Admin UI at /admin or API: GET /api/v1/admin/review-queue    │
│    Approve → Resource goes live                                 │
└─────────────────────────────────────────────────────────────────┘
```

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

Built to help veterans find resources beyond VA.gov.
