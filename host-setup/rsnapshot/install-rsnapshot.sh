#!/bin/bash
# Install rsnapshot + config (AI Agent Lab host backups).
# rsnapshot pulls rsync in as a dependency.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install rsnapshot
sudo apt update
sudo apt install -y rsnapshot

# Snapshot root directory (matches snapshot_root in rsnapshot.conf)
sudo mkdir -p /backup/rsnapshot

# Config files (static, shipped with this script)
sudo install -m 0644 "$SCRIPT_DIR/rsnapshot.conf" /etc/rsnapshot.conf
sudo install -m 0644 "$SCRIPT_DIR/rsnapshot"      /etc/cron.d/rsnapshot

# Validate the config (rsnapshot.conf must use tabs between elements)
sudo rsnapshot configtest
