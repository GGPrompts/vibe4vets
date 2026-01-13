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
