# PostgreSQL 16 with pgvector AND PostGIS
FROM pgvector/pgvector:pg16

# Install PostGIS
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-16-postgis-3 \
        postgresql-16-postgis-3-scripts \
    && rm -rf /var/lib/apt/lists/*
