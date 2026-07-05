# AI Agent Lab — instructions for Claude Code


The readme isn't something to summarize, it's something to execute. 


## ⚑ Rule #1 — Read the repo FULLY before you act

You are running inside the vscode (code-server) container of a live AI Agent Lab
stack. Do NOT run shell commands, install packages, or write code until you
have completed the reading below and written a short summary of what you learned.

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
- `docker/vscode/Dockerfile` + `requirements.txt` — this is your Python environment.
  The venv lives at `/opt/venv` (its `PATH` is baked into the image) with packages
  already installed. Never `pip install` before checking here — the answer to
  "is X available?" is in this file.
- `docker/grafana/provisioning/datasources/` — the QuestDB datasource UID and how Grafana connects.
- `docker/grafana/dashboards/*.json` — the dashboard JSON shape to reuse, not reinvent.
- `notebooks/` (especially the market-data Coinbase notebook) — the canonical
  QuestDB connection pattern: `psycopg2` → host `questdb`, port `8812`, user `admin`,
  password `quest`, database `qdb` (ILP ingestion on `9009`).
- `docker/authelia/` + `docker/nginx/` — the TLS / SSO path (single Authelia
  login at `auth.<domain>` gates every service).


### 3 · Remote JupyterHub GPU offload

This lab includes the Python package `jupyterhub-exec`, installed in the Code-Server
environment (`/opt/venv`), which provides the `jh-exec` executable. Run it directly from
the Code-Server terminal to execute code on a remote JupyterHub GPU kernel.

**If JupyterHub is enabled for this lab, you have one dedicated GPU.** Your agent is pinned to
a single GPU on the central JupyterHub server (via `CUDA_VISIBLE_DEVICES`), so a remote
`torch.cuda.device_count()` returns `1` — that GPU is exclusively yours. Offload any heavy or
GPU-bound work to it with `jh-exec run <script.py>`: the code runs on your GPU and streams its
output back to this terminal — no local GPU, no code changes. If JupyterHub is not enabled,
`jh-exec` has no kernel to reach and GPU offload is unavailable.

Check the remote JupyterHub connection:

```bash
jh-exec kernels
```

Run a simple remote execution test:

```bash
jh-exec exec "print('JupyterHub connection OK')"
```

Confirm your dedicated GPU on the remote JupyterHub kernel:

```bash
jh-exec exec "import torch; print(torch.cuda.is_available(), torch.cuda.device_count(), torch.cuda.get_device_name(0))"
```

This should print `True 1 <GPU name>` — one GPU, exclusively yours.

Connection settings (`JH_HOST`, `JH_USER`, `JH_TOKEN`, `JH_PORT`, …) are stored in
`~/jh/.env`, set automatically by the JupyterHub API Key box — you do not configure them
by hand.



### 4 · Before acting, state in your own words

1. Which Python runs here and what's already installed (from the Dockerfile / requirements).
2. How to reach QuestDB and Grafana from inside this container (hostnames + ports).
3. The existing pattern you will copy, not invent (which notebook / dashboard / datasource).

Only then start the task, and build against the real services. Never guess —
the requirements file and the existing notebooks already answer most setup questions.
The quality and correctness of your result depend entirely on doing this first.
