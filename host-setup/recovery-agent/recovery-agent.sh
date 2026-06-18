#!/bin/bash
# Runs on the HOST as root, via systemd (see recovery-agent.service).
# Watches a named pipe for a validated snapshot name and runs the restore.
# The container can only WRITE a name into the pipe — it can never run host
# commands. The allowlist and the dangerous capability live here, on the host.
#
# Install to: /usr/local/bin/recovery-agent.sh  (chmod +x)
set -uo pipefail

PIPE=/run/recovery/request.pipe
mkdir -p /run/recovery && chmod 0750 /run/recovery
[ -p "$PIPE" ] || mkfifo -m 0660 "$PIPE"

logger -t recovery "recovery-agent started, watching $PIPE"

while true; do
    read -r name < "$PIPE" || continue
    case "$name" in
        ""|*/*|*..*) logger -t recovery "rejected backup name: '$name'"; continue ;;
    esac
    logger -t recovery "starting restore: $name"
    SELECTED_BACKUP="$name" /usr/local/bin/recovery-microserver.sh \
        >>/var/log/recovery.log 2>&1 \
        && logger -t recovery "restore ok: $name" \
        || logger -t recovery "restore FAILED: $name (see /var/log/recovery.log)"
done
