#!/bin/bash
# Monitor Linux Servers with Prometheus Node Exporter — DevOpsCube
# https://devopscube.com/monitor-linux-servers-prometheus-node-exporter/
# Version 1.11.1
# (The node_exporter scrape job is already in the shipped prometheus.yml,
#  so no append/restart of Prometheus is needed here.)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create node_exporter user
sudo useradd -rs /bin/false node_exporter

# Download and install binary
cd /tmp
curl -LO https://github.com/prometheus/node_exporter/releases/download/v1.11.1/node_exporter-1.11.1.linux-amd64.tar.gz
tar -xvf node_exporter-1.11.1.linux-amd64.tar.gz
sudo mv node_exporter-1.11.1.linux-amd64/node_exporter /usr/local/bin/

# Systemd service (static, shipped with this script)
sudo cp "$SCRIPT_DIR/node_exporter.service" /etc/systemd/system/node_exporter.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
