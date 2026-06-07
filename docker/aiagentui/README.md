# AI Agent UI

The web dashboard for the AI Agent Lab — a lightweight **Flask** app that serves the chat interface and the lab's control panel. It talks to **Claude (Anthropic)** directly; there is no separate backend service.

## Features

- **Chat with Claude** — calls the Anthropic Messages API, with model switching across Haiku, Sonnet, and Opus. Conversations are kept in the browser (localStorage).
- **Claude API key (bring-your-own-key)** — set your Anthropic key from the dashboard ("Claude API Key" panel). It's stored per-instance and persists across rebuilds/restores; falls back to `ANTHROPIC_API_KEY` in `.env` if unset. No shell or `.env` editing required.
- **File upload** — upload `.csv` / `.sql` / `.pdf` / `.txt` (max 800 KB) into the shared `uploads/` folder.
- **Backup restore** — list and restore `rsnapshot` snapshots.
- **Service controls** — restart Docker services (VSCode, QuestDB, Grafana, Nginx).
- **Embedded metrics** — live Grafana panels shown on the dashboard.
- **CSRF protection** — all state-changing requests require a CSRF token (Flask-WTF).

## Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Dashboard + chat UI |
| `/chat` | POST | Send a conversation to Claude |
| `/upload` | POST | Upload a file |
| `/list-files` | GET | List uploaded files |
| `/delete-file` | POST | Delete an uploaded file |
| `/save-key` | POST | Save the Claude API key (stored on the instance volume) |
| `/api/list-backups` | GET | List available backups |
| `/api/restore-backup` | POST | Restore a backup |
| `/restart/<container>` | POST | Restart a Docker service |
| `/restart/nginx` | POST | Restart Nginx |

All `POST` routes require a CSRF token (sent as the `X-CSRFToken` header by the frontend; the token is rendered into the page via a `csrf-token` meta tag).

## Configuration

Set in the lab's `.env` (see `../.sample.env`):

- `ANTHROPIC_API_KEY` — Claude API key. This is the **fallback**; a key set via the dashboard "Claude API Key" panel takes precedence (and is the only option when there's no shell/`.env` access).
- `DOMAIN` — base domain used to build the dashboard's service links.
- `APP_SECRET_KEY` — Flask session signing key; also signs CSRF tokens — use a strong random value.
- `CLAUDE_KEY_FILE` *(optional)* — path to the stored Claude key (default `instance/claude_api_key`, on the `aiagentui-data` volume).

**Key precedence:** the app reads the stored key first (`instance/claude_api_key`, set by the panel), then falls back to `ANTHROPIC_API_KEY`.

## Run

The UI runs as part of the lab's Docker stack and is served on port **5000**:

```
docker compose up -d aiagentui
```

## Structure

```
aiagentui/
  app.py              # Flask app — routes for chat, files, backups, restarts, save-key
  templates/
    index.html        # dashboard + chat UI (csrf-token meta tag)
  static/
    css/  js/  img/   # styles, scripts, icons
  uploads/            # uploaded files (shared volume)
  instance/           # per-instance store, e.g. claude_api_key (aiagentui-data volume)
```

