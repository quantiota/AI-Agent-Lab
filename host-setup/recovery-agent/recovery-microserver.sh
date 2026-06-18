#!/bin/bash
# Runs on the HOST as root (invoked by recovery-agent.sh). Restores /home and
# /opt from the selected rsnapshot snapshot, then rebuilds the Docker stack.
# Safe by design: verifies the backup BEFORE deleting anything, stages the copy,
# and keeps the previous tree as <dir>.old for rollback.
#
# Install to: /usr/local/bin/recovery-microserver.sh  (chmod +x)
set -euo pipefail

SELECTED_BACKUP="${SELECTED_BACKUP:-}"
TARGET_USER="devbox"                                  # host user that owns the checkout
COMPOSE_DIR="/home/${TARGET_USER}/AI-Agent-Lab/docker"
BACKUP_ROOT="/backup/rsnapshot"

# 1. Validate input and reject path traversal
[ -n "$SELECTED_BACKUP" ] || { echo "Error: SELECTED_BACKUP not set." >&2; exit 1; }
case "$SELECTED_BACKUP" in
    */*|*..*) echo "Error: invalid backup name '$SELECTED_BACKUP'." >&2; exit 1 ;;
esac

SRC="$BACKUP_ROOT/$SELECTED_BACKUP/localhost"

# 2. Verify the backup has what we need BEFORE touching anything
for d in home opt; do
    [ -d "$SRC/$d" ] || { echo "Error: backup missing '$d' at $SRC/$d. Aborting, nothing changed." >&2; exit 1; }
done

# 3. Stage the copy, then swap — keep the old tree as a rollback
restore_dir() {
    local name="$1" staged="/.${1}.restore.$$"
    rm -rf "$staged"
    cp -a "$SRC/$name" "$staged"        # if this fails, set -e aborts; originals untouched
    rm -rf "/${name}.old"
    [ -e "/$name" ] && mv "/$name" "/${name}.old"
    mv "$staged" "/$name"
}
restore_dir home
restore_dir opt

# 4. Rebuild the stack
cd "$COMPOSE_DIR" || { echo "Error: $COMPOSE_DIR not found." >&2; exit 1; }
docker compose up --build -d

echo "Restore of '$SELECTED_BACKUP' complete. Previous /home and /opt kept as .old"
