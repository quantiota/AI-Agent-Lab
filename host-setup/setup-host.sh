#!/bin/bash
# Prepare an Ubuntu 24.04 host for the AI Agent Lab.
# Runs each component installer in order. Run from this folder: ./setup-host.sh
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$DIR/git/install-git.sh"
bash "$DIR/docker/install-docker.sh"
bash "$DIR/docker-compose/install-docker-compose.sh"
bash "$DIR/rsnapshot/install-rsnapshot.sh"
bash "$DIR/recovery-agent/install-recovery-agent.sh"
bash "$DIR/prometheus/install-prometheus.sh"
bash "$DIR/node-exporter/install-node-exporter.sh"

echo "Host setup complete. Next: clone the AI Agent Lab and run 'docker compose up'."
