#!/bin/bash
# Database backup script for vibe4vets

BACKUP_DIR="${1:-$(dirname "$0")/../backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/vibe4vets_$TIMESTAMP.sql.gz"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Run pg_dump in docker container, compress output
docker exec vibe4vets-db-1 pg_dump -U vibe4vets vibe4vets | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    echo "✓ Backup created: $BACKUP_FILE ($SIZE)"

    # Keep only last 10 backups
    ls -t "$BACKUP_DIR"/vibe4vets_*.sql.gz 2>/dev/null | tail -n +11 | xargs -r rm
    echo "  (keeping last 10 backups)"
else
    echo "✗ Backup failed"
    rm -f "$BACKUP_FILE"
    exit 1
fi
