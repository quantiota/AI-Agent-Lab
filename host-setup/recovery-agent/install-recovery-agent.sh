#!/bin/bash
# Install the recovery-agent (host-side restore) — AI Agent Lab.
# Pairs with rsnapshot: the dashboard requests a snapshot restore via a named
# pipe; the recovery-agent performs the privileged restore on the host.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_USER="ubuntu"

# Recovery scripts -> /usr/local/bin (executable)
sudo install -m 0755 "$SCRIPT_DIR/recovery-agent.sh"       /usr/local/bin/recovery-agent.sh
sudo install -m 0755 "$SCRIPT_DIR/recovery-microserver.sh" /usr/local/bin/recovery-microserver.sh

# Point the restore at the right host user (scripts ship with 'devbox';
# COMPOSE_DIR is derived from TARGET_USER, so this one substitution covers both)
sudo sed -i "s/^TARGET_USER=.*/TARGET_USER=\"${TARGET_USER}\"/" /usr/local/bin/recovery-microserver.sh

# systemd unit
sudo install -m 0644 "$SCRIPT_DIR/recovery-agent.service" /etc/systemd/system/recovery-agent.service

# Enable (starts on boot)
sudo systemctl daemon-reload
sudo systemctl enable recovery-agent
