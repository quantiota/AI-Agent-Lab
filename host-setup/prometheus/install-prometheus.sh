#!/bin/bash
# Install Prometheus 3.12.0 on Ubuntu (binary + systemd).
# Prometheus 3.x no longer ships consoles/console_libraries, so none are copied
# and the --web.console.* flags are not used. Defaults cover the rest
# (listens on 0.0.0.0:9090, 15d retention).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Download Prometheus
cd /tmp
curl -LO https://github.com/prometheus/prometheus/releases/download/v3.12.0/prometheus-3.12.0.linux-amd64.tar.gz
tar -xvf prometheus-3.12.0.linux-amd64.tar.gz
cd prometheus-3.12.0.linux-amd64

# User + directories
sudo useradd --no-create-home --shell /bin/false prometheus
sudo mkdir -p /etc/prometheus /var/lib/prometheus

# Binaries
sudo cp prometheus promtool /usr/local/bin/

# Config + systemd service (static files shipped with this script)
sudo cp "$SCRIPT_DIR/prometheus.yml"      /etc/prometheus/prometheus.yml
sudo cp "$SCRIPT_DIR/prometheus.service"  /etc/systemd/system/prometheus.service

# Ownership
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus \
    /usr/local/bin/prometheus /usr/local/bin/promtool

# Enable + start
sudo systemctl daemon-reload
sudo systemctl enable --now prometheus
