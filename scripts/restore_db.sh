#!/bin/bash
# scripts/restore_db.sh
# Restaura um backup gerado pelo backup_db.sh.
# Uso: bash scripts/restore_db.sh backups/rescuehub_20250101_120000.sql.gz

set -euo pipefail

BACKUP_FILE="${1:-}"

if [[ -z "$BACKUP_FILE" || ! -f "$BACKUP_FILE" ]]; then
  echo "Uso: $0 <arquivo_backup.sql.gz>"
  exit 1
fi

DB_NAME="${DATABASE_NAME:-rescuehub}"
DB_USER="${DATABASE_USER:-rescuehub}"
DB_PASSWORD="${DATABASE_PASSWORD:-rescuehub}"
DB_HOST="${DATABASE_HOST:-localhost}"
DB_PORT="${DATABASE_PORT:-5432}"

echo "[restore] Restaurando $BACKUP_FILE → $DB_NAME"

gunzip -c "$BACKUP_FILE" | PGPASSWORD="$DB_PASSWORD" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME"

echo "[restore] Concluído."
