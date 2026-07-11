#!/usr/bin/env bash
# code-server ENTRYPOINTD startup hook — runs as `coder` at EVERY container boot,
# before code-server starts, and must not block.
#
# Start the Matrix room listener (baked into the image at /home/coder/matrix). On a room
# message addressed to this node's call-sign it `tmux send-keys` a directive INTO the live
# `claude` session (started by 10-claude-tmux.sh); the live Claude replies via matrix_send.py.
# Auth from the container env: MATRIX_TOKEN (homeserver-issued) — user id derived from DOMAIN.
export PATH="/opt/venv/bin:$PATH"

# Only start if this node actually has Matrix creds (token preferred, password dev-fallback).
if [ -z "$MATRIX_TOKEN" ] && [ -z "$MATRIX_PASSWORD" ]; then
  echo "no MATRIX_TOKEN/MATRIX_PASSWORD -- matrix listener not started"
  exit 0
fi

# Idempotent across restarts.
pgrep -f matrix-listen.py >/dev/null 2>&1 && exit 0

nohup /opt/venv/bin/python /home/coder/matrix/matrix-listen.py \
  >/home/coder/matrix/listen.log 2>&1 &
