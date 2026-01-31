FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/pyproject.toml .
COPY backend/README.md .
COPY backend/app ./app
COPY backend/alembic.ini .
COPY backend/alembic ./alembic
COPY backend/connectors ./connectors
COPY backend/etl ./etl
COPY backend/jobs ./jobs
COPY backend/llm ./llm
COPY backend/data ./data

RUN pip install --no-cache-dir .

EXPOSE 8000

# Run migrations then start server (with debug output)
CMD echo "Starting app..." && \
    python -c "import app.main; print('Import OK')" && \
    echo "Testing DB connection..." && \
    python -c "from app.database import engine; from sqlmodel import Session, text; s=Session(engine); r=s.exec(text('SELECT 1')); print('DB OK:', list(r))" && \
    echo "Running alembic..." && \
    alembic upgrade head && \
    echo "Starting uvicorn..." && \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
