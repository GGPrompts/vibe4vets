# Vibe4Vets Backend

FastAPI + SQLModel + PostgreSQL backend for the veteran resource directory.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

```bash
uvicorn app.main:app --reload
```

## Database

```bash
alembic upgrade head
```

## Local Development (Docker Compose)

The repo includes `docker-compose.yml` with:
- `db`: Postgres (pgvector image) with a persistent volume (`postgres_data`)
- `backend`: FastAPI app (connects via `DATABASE_URL`)
- `frontend`: Next.js app (calls backend via `NEXT_PUBLIC_API_URL`)

Typical flow:

```bash
docker compose up --build
```

## Data Ingestion: API + Scrape

Resources are persisted in the database (they are not fetched live per user request).

- Connectors (e.g. VA.gov, CareerOneStop) live in `backend/connectors/`
- The refresh job runs connectors through the ETL pipeline: `backend/jobs/refresh.py`
- Normalization supports US states plus territories (`PR`, `GU`, `VI`, `AS`, `MP`): `backend/etl/normalize.py`

State filtering semantics include national resources alongside state/territory matches.
