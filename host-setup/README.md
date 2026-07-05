# AI Agent Lab — Host Setup

Prepares a fresh **Ubuntu 24.04 (amd64)** host with everything needed to run the
AI Agent Lab — **before** you clone the lab itself. Each component is a
self-contained subdirectory (`install-*.sh` + its config files).

## Quick start
```bash
cd host-setup
chmod +x setup-host.sh */install-*.sh
./setup-host.sh          # runs all installers, in order
```
The host is now ready. **Then, separately, clone the AI Agent Lab** and follow its
README to configure (domain/secrets/certs) and bring up the `docker/` compose project.

## Components (run order)
| Component        | Installs                                                       |
|------------------|---------------------------------------------------------------|
| `git`            | git (to clone the lab)                                         |
| `docker`         | Docker Engine — official Docker apt repo (`docker-ce`)         |
| `docker-compose` | Docker Compose plugin (`docker compose`)                       |
| `rsnapshot`      | rsnapshot + cron, backups → `/backup/rsnapshot`               |
| `recovery-agent` | host-side restore agent (systemd)                             |
| `prometheus`     | Prometheus **3.12.0** (binary + systemd)                      |
| `node-exporter`  | node_exporter **1.11.1** (binary + systemd)                   |

## Run a component on its own
Each subdir is self-contained — run it from inside its folder so it finds its files:
```bash
cd docker
chmod +x install-docker.sh
./install-docker.sh
```

## Notes
- Target: **Ubuntu 24.04, amd64** (Prometheus/node-exporter binaries are amd64).
- TLS is **not** here — it's issued by the lab's certbot container (HTTP-01) at runtime.
- `recovery-agent`: set `TARGET_USER` to your host user before running its installer.

