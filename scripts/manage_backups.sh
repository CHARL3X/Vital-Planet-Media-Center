#!/bin/bash

# Backup management for Asset Hub
# Keeps only the latest N backups and cleans up old ones

BACKUP_DIR="backups"
MAX_BACKUPS=5

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Clean up old backups, keep only the latest N
if ls "$BACKUP_DIR"/assets_index_*.json 1> /dev/null 2>&1; then
    backup_count=$(ls -1 "$BACKUP_DIR"/assets_index_*.json | wc -l)
    if [ "$backup_count" -gt "$MAX_BACKUPS" ]; then
        excess=$((backup_count - MAX_BACKUPS))
        ls -t "$BACKUP_DIR"/assets_index_*.json | tail -n "$excess" | xargs rm -f
        echo "Cleaned up $excess old backup(s)"
    fi
fi
