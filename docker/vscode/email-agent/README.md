# Email IDLE listener

Real-time mail notification for the live agent. When mail arrives the IMAP server pushes
`EXISTS`; the listener debounces, dedups (last-UID), rate-caps, then `tmux send-keys` the
note INTO the running `claude` session. No polling.

## How it runs

- **`idle-listener.py`** is baked into the vscode image at `/home/coder/email-agent/`
  and runs as `coder` — same tmux server as the live Claude. It reuses `email_agent.py`.
- **Starter:** `entrypoint.d/20-email-idle.sh` launches it at container boot
  (idempotent, non-blocking), next to the `claude` session from `10-claude-tmux.sh`.
- **Creds:** `/home/coder/mail/.env` (the `mail-config` volume), set via the dashboard
  Save-email modal.
- Needs the `claude` tmux session to exist; if it doesn't, the listener logs
  "no live session" and skips — it never crashes.

## First run

Open the dashboard **Save-email** modal once to store the mailbox password (written to the
`mail-config` volume). That's the only email-specific step — the listener itself ships with
the lab image and starts on its own.

## Verify

Send a test mail → `idle-state/idle-listener.log` shows `NEW MAIL up to uid N -> notifying
live agent` and `notified live session 'claude'`, and the note appears in the live Claude terminal.

## Tuning

Set env on the **vscode service** in `docker-compose.yaml` (the starter inherits it):

| Env | Default | Meaning |
|-----|---------|---------|
| `CLAUDE_SESSION` | `claude` | tmux session the live Claude runs in |
| `DEBOUNCE_SEC` | 5 | collapse a burst of mails into one notify |
| `MAX_NOTIFY_PER_HOUR` | 20 | ceiling on notifications (guard) |
| `IDLE_NOTE` | check-unread note | text typed into the live session |
| `IDLE_RENEW_SEC` | 1500 | renew IDLE before the ~29-min server timeout |
| `EMAIL_CONFIG_FILE` | `/home/coder/mail/.env` | cred store (mail-config volume) |

## State (`idle-state/`)

- `idle-listener.log` — connection + event log
- `run.log` — starter stdout/stderr
- `last-uid` — dedup marker (highest handled UID)
- `notify-calls` — notify timestamps (rolling 1-hour rate window)

## Notes

- **Single instance:** the starter guards with `pgrep -f idle-listener.py` before launching,
  so a restart never stacks duplicates.
- **Rate ceiling:** `MAX_NOTIFY_PER_HOUR` caps how often the live session is poked
  (burst-debounced + deduped), so a mail flood can't spam the terminal.

