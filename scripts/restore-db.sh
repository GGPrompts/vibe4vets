#!/bin/bash
# Database restore script for vibe4vets

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lht "$(dirname "$0")/../backups"/vibe4vets_*.sql.gz 2>/dev/null | head -10
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "✗ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  This will DROP and recreate all tables!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo "Restoring from $BACKUP_FILE..."

# Drop and recreate database, then restore
docker exec -i vibe4vets-db-1 psql -U vibe4vets -d postgres -c "DROP DATABASE IF EXISTS vibe4vets"
docker exec -i vibe4vets-db-1 psql -U vibe4vets -d postgres -c "CREATE DATABASE vibe4vets"
gunzip -c "$BACKUP_FILE" | docker exec -i vibe4vets-db-1 psql -U vibe4vets -d vibe4vets

if [ $? -eq 0 ]; then
    echo "✓ Restore complete"
else
    echo "✗ Restore failed"
    exit 1
fi
