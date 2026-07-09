# Agent email IDLE listener — install (host / devbox)

Real-time email notification for the LIVE agent: the instant mail lands, the IMAP
server pushes `EXISTS`; the listener debounces, dedups (last-UID), rate-caps, then
`tmux send-keys` the note INTO the running `claude` session — the agent is notified
in place. No polling.

- **`idle-listener.py`** runs INSIDE the `docker-vscode-1` container — same tmux
  server + user as the live Claude. It reuses `email_agent.py` (same dir) and the
  mailui credential store `mail/.env` (set via the dashboard's Save-email modal) —
  so the mailbox password lives in exactly one place.
- **PREREQUISITE:** Claude must be running inside a tmux session named `claude`
  (`tmux new -s claude` → run `claude` inside it). No such session → the listener
  logs "no live session" and skips; it never crashes.
- **`agent-idle-listener.service`** is a HOST systemd unit that keeps it alive with
  `Restart=always`, `docker exec`-ing into the container (same pattern as the
  heartbeat timer already on this box).

## Install (run on the devbox host)

Paths here are the **host clone** (`~/AI-Agent-Lab/docker/...`). NB: the unit's own
`ExecStart`/`ExecStartPre` keep `/home/coder/docker/...` on purpose — that is the path
*inside* the vscode container (they run via `docker exec`), so do **not** change those.

```bash
sudo cp ~/AI-Agent-Lab/docker/aiagentui/email-agent/agent-idle-listener.service \
        /etc/systemd/system/agent-idle-listener.service
sudo systemctl daemon-reload
sudo systemctl enable --now agent-idle-listener.service     # NB: --now
```

## Verify

```bash
systemctl status agent-idle-listener.service                # active (running)
# listener log (host-visible via the bind mount):
tail -f ~/AI-Agent-Lab/docker/aiagentui/email-agent/idle-state/idle-listener.log
#   -> "connected — entering IDLE, waiting for new mail..."
```

Send a test mail to the box → within ~debounce seconds the log shows
`NEW MAIL up to uid N -> notifying live agent` and `notified live session 'claude'`,
and the note appears in the live Claude terminal.

## Tuning (optional)

Defaults are sane. To change, edit `ExecStart` in the unit and add `docker exec -e`:

| Env | Default | Meaning |
|-----|---------|---------|
| `CLAUDE_SESSION` | `claude` | tmux session the live Claude runs in |
| `DEBOUNCE_SEC` | 5 | collapse a burst of mails into one notify |
| `MAX_NOTIFY_PER_HOUR` | 20 | hard ceiling on notifications (guard) |
| `IDLE_NOTE` | check-unread note | the text typed into the live session |
| `IDLE_RENEW_SEC` | 1500 | renew IDLE before the ~29-min server timeout |

## State / logs (`idle-state/`)

- `idle-listener.log` — connection + event log
- `last-uid` — dedup marker (highest handled UID)
- `notify-calls` — notify timestamps (rolling 1-hour rate window)

## Notes

- **Single instance:** `ExecStartPre`/`ExecStopPost` `pkill -f idle-listener.py`
  in the container, so a restart never stacks duplicate listeners.
- **Rate ceiling:** `MAX_NOTIFY_PER_HOUR` caps how often the live session is poked
  (burst-debounced + deduped by last UID), so a mail flood can't spam the terminal.
- **Later:** the cleaner form is an in-container service (started at container boot,
  alongside the heartbeat's `claude` tmux session) — no image change needed to ship
  now via this host unit.
