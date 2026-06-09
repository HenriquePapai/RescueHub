#!/bin/bash
# scripts/backup_db.sh
# Gera um dump comprimido do PostgreSQL com timestamp.
# Uso local:  bash scripts/backup_db.sh
# Uso no CI:  chamado pelo job backup no pipeline.yaml

set -euo pipefail

DB_NAME="${DATABASE_NAME:-rescuehub}"
DB_USER="${DATABASE_USER:-rescuehub}"
DB_PASSWORD="${DATABASE_PASSWORD:-rescuehub}"
DB_CONTAINER="${DB_CONTAINER:-rescuehub_db}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
BACKUP_FILE="${BACKUP_DIR}/rescuehub_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "[backup] Iniciando dump: $BACKUP_FILE"

docker exec "$DB_CONTAINER" bash -c \
  "PGPASSWORD='$DB_PASSWORD' pg_dump -U $DB_USER -d $DB_NAME --no-owner --no-acl | gzip" \
  > "$BACKUP_FILE"

echo "[backup] Concluído: $(du -sh "$BACKUP_FILE" | cut -f1)"
echo "backup_file=$BACKUP_FILE" >> "${GITHUB_OUTPUT:-/dev/null}"
