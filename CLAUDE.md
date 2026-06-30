# AI Agent Lab — instructions for Claude Code

## ⚑ Rule #1 — Read the repo FULLY before you act

You are running inside the **vscode (code-server) container of a live AI Agent Lab
stack**. Do **NOT** run shell commands, install packages, or write code until you
have completed the reading below **and** written a short summary of what you learned.

> "I read the top-level files and stopped" is NOT enough — that is the exact
> failure this rule exists to prevent. A shallow read leads to guessing: probing
> for packages that are already installed, `pip install`-ing into a venv that
> needs nothing, and inventing connection patterns the notebooks already define.

### 1 · Clone the repo (ephemeral by design)

```bash
git clone https://github.com/quantiota/AI-Agent-Lab
```

The clone is not persistent — it's wiped when the stack is recreated, so every
fresh stack clones the latest repo.

### 2 · Mandatory reading — every one of these, in full

- `docker/docker-compose.yaml` — service names, ports, networks, volumes (how the stack is wired).
- `docker/vscode/Dockerfile` + `requirements.txt` — **this is your Python environment.**
  The venv lives at **`/opt/venv`** (its `PATH` is baked into the image) with packages
  already installed. **Never `pip install` before checking here** — the answer to
  "is X available?" is in this file.
- `docker/grafana/provisioning/datasources/` — the QuestDB datasource UID and how Grafana connects.
- `docker/grafana/dashboards/*.json` — the dashboard JSON shape to **reuse**, not reinvent.
- `notebooks/` (especially the market-data Coinbase notebook) — the canonical
  QuestDB connection pattern: **`psycopg2` → host `questdb`, port `8812`, user `admin`,
  password `quest`, database `qdb`** (ILP ingestion on `9009`).
- `docker/authelia/` + `docker/nginx/` — the TLS / SSO path (single Authelia
  login at `auth.<domain>` gates every service).

### 3 · Before acting, state in your own words

1. **Which Python runs here and what's already installed** (from the Dockerfile / requirements).
2. **How to reach QuestDB and Grafana** from inside this container (hostnames + ports).
3. **The existing pattern you will copy**, not invent (which notebook / dashboard / datasource).

**Only then** start the task, and build against the **real** services. Never guess —
the requirements file and the existing notebooks already answer most setup questions.
The quality and correctness of your result depend entirely on doing this first.
