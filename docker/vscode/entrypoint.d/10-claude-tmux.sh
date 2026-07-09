#!/usr/bin/env bash
# code-server ENTRYPOINTD startup hook — runs as `coder` at EVERY container boot,
# before code-server starts, and must not block (tmux -d returns immediately).
#
# Auto-start Claude inside a persistent tmux session named `claude` so the running
# agent is ADDRESSABLE + DURABLE:
#   - external events (the email IMAP-IDLE listener, the heartbeat cron) can
#     `tmux send-keys` their notification INTO this live session;
#   - the session survives SSH/terminal drops — reattach with `tmux attach -t claude`.
export PATH="/home/coder/.local/bin:/opt/venv/bin:$PATH"

# Idempotent across restarts: if the session already exists, leave it alone.
tmux has-session -t claude 2>/dev/null && exit 0

# Detached start via the keep-alive wrapper: tmux gives it a pty and -d returns at
# once (no block). claude-session runs claude in a respawn loop, so the session
# survives claude exiting and stays attachable (no restart-vscode-to-recover).
tmux new-session -d -s claude '/usr/local/bin/claude-session'
