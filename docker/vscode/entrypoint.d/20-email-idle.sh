#!/usr/bin/env bash
# code-server ENTRYPOINTD startup hook — runs as `coder` at EVERY container boot,
# before code-server starts, and must not block.
#
# Start the email IMAP-IDLE listener (baked into the image at /home/coder/email-agent).
# On a new mail it `tmux send-keys` a notification INTO the live `claude` session
# (started by 10-claude-tmux.sh). Creds come from the scoped mail-config volume at
# /home/coder/mail/.env — no docker/ tree mount, no host systemd unit.
export PATH="/opt/venv/bin:$PATH"

# Idempotent across restarts: if a listener is already running, leave it.
pgrep -f idle-listener.py >/dev/null 2>&1 && exit 0

# Detached, non-blocking: nohup + & returns at once; the process is reparented to the
# container init and keeps running for the life of the container (Restart handled by
# recreate). Its own log goes to idle-state/idle-listener.log; stdout/stderr to run.log.
nohup /opt/venv/bin/python /home/coder/email-agent/idle-listener.py \
  >/home/coder/email-agent/idle-state/run.log 2>&1 &
