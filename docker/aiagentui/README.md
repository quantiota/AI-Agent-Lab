# AI Agent UI

The web dashboard for the AI Agent Lab — a lightweight **Flask** app that serves the chat interface and the lab's control panel. It talks to **Claude (Anthropic)** directly; there is no separate backend service.

## Features

- **Chat with Claude** — calls the Anthropic Messages API, with model switching across Haiku, Sonnet, and Opus. Conversations are kept in the browser (localStorage).
- **File upload** — upload `.csv` / `.sql` / `.pdf` / `.txt` (max 800 KB) into the shared `uploads/` folder.
- **Backup restore** — list and restore `rsnapshot` snapshots.
- **Service controls** — restart Docker services (VSCode, QuestDB, Grafana, Nginx).
- **Embedded metrics** — live Grafana panels shown on the dashboard.

## Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Dashboard + chat UI |
| `/chat` | POST | Send a conversation to Claude |
| `/upload` | POST | Upload a file |
| `/list-files` | GET | List uploaded files |
| `/delete-file` | POST | Delete an uploaded file |
| `/api/list-backups` | GET | List available backups |
| `/api/restore-backup` | POST | Restore a backup |
| `/restart/<container>` | GET | Restart a Docker service |
| `/restart/nginx` | GET | Restart Nginx |

## Configuration

Set in the lab's `.env` (see `../.sample.env`):

- `ANTHROPIC_API_KEY` — Claude API key.
- `DOMAIN` — base domain used to build the dashboard's service links.
- `APP_SECRET_KEY` — Flask session signing key.

## Run

The UI runs as part of the lab's Docker stack and is served on port **5000**:

```
docker compose up -d aiagentui
```

## Structure

```
aiagentui/
  app.py              # Flask app — routes for chat, files, backups, service restarts
  templates/
    index.html        # dashboard + chat UI
  static/
    css/  js/  img/   # styles, scripts, icons
  uploads/            # uploaded files (shared volume)
```
