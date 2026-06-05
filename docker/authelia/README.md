# Authelia — SSO for the AI Agent Lab

Single sign-on across the lab's services (Code-Server, QuestDB, Grafana, AI Agent UI).
One login at `auth.<domain>` covers all subdomains; logout at `auth.<domain>/logout`.

## Files
- `configuration.yml` — main config: secrets, access-control rules, session, storage, asset_path
- `users_database.yml` — users + argon2 password hashes (replaces `.htpasswd`)
- `assets/` — custom `logo.png` / `favicon.ico` for the login page
- `db.sqlite3` — Authelia storage (auto-created; do not edit)
- `notification.txt` — file-notifier output (testing only)

## How it's wired
- Service `authelia/authelia:4.39` in `docker-compose.yaml`; mounts `./authelia:/config`; exposes `9091` (internal only).
- nginx: portal at `auth.<domain>` -> `authelia:9091`; forward-auth (`auth_request`) on each gated
  service via `nginx/snippets/authelia-location.conf` + `authelia-authrequest.conf`
  (endpoint `/api/authz/auth-request`).

## Add / change a user
    docker run --rm authelia/authelia:4.39 \
      authelia crypto hash generate argon2 --password 'PASSWORD'
Paste the hash under `users:` in `users_database.yml`, then `docker compose restart authelia`.

## Secrets (configuration.yml)
Three random values, each `openssl rand -hex 64`:
`session.secret`, `storage.encryption_key`, `identity_validation.reset_password.jwt_secret`.

## Session timeouts (per cookie)
`expiration: 12 hours`, `inactivity: 1 hour`, `remember_me: 1 month`.

## Login-page branding (native only)
Drop `logo.png` (PNG, 256px+) and `favicon.ico` into `assets/` (`asset_path: /config/assets/`).
Theme via `theme:` (light | dark | grey | oled). The accent color is fixed — no native option.

## Notes
- Files are usually root-owned (Authelia runs as root and created them) — edit with `sudo`.
- After any change: `docker compose restart authelia && docker logs docker-authelia-1 --tail 20`
  to confirm the config validated.
