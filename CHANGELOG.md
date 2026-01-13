# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- VA.gov Lighthouse Facilities API connector (`backend/connectors/va_gov.py`)
  - Fetches health, benefits, and vet center facilities
  - Implements Connector protocol with pagination and error handling
  - 17 unit tests with mocked API responses

### Fixed
- Removed duplicate `test_health.py` that failed with SQLite ARRAY types
- Removed machine-specific PRIME.md symlink from git tracking

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
