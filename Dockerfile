FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/pyproject.toml .
COPY backend/app ./app
COPY backend/alembic.cfg .
COPY backend/alembic ./alembic
COPY backend/connectors ./connectors
COPY backend/etl ./etl
COPY backend/jobs ./jobs
COPY backend/llm ./llm
COPY backend/data ./data

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
