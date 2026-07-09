#!/usr/bin/env bash
# claude-session — keep-alive wrapper for the live agent.
#
# Runs `claude` in a respawn loop so the tmux `claude` session SURVIVES claude
# exiting (crash, /exit, double Ctrl-C). Without this the session's only process is
# claude itself, and in tmux a session dies when its root process exits — leaving
# nothing to re-attach to until the container is restarted. With this wrapper the
# session root is a shell loop that never exits, so `tmux attach -t claude` always works.
#
# Back-off guard: a fast repeated exit (crash-loop) waits progressively longer instead
# of spinning — protects against burning API tokens if claude can't start.
export PATH="/home/coder/.local/bin:/opt/venv/bin:$PATH"

trap 'echo "[claude-session stopped]"; exit 0' INT   # Ctrl-C during the countdown stops the loop

delay=3
while true; do
  start=$(date +%s)
  claude "$@"
  ran=$(( $(date +%s) - start ))
  if [ "$ran" -ge 20 ]; then
    delay=3                                    # healthy run → reset back-off
  else
    delay=$(( delay * 2 ))                      # quick exit → exponential back-off ...
    [ "$delay" -gt 60 ] && delay=60            # ... clamped at 60s
  fi
  echo "[claude exited after ${ran}s — relaunching in ${delay}s; press Ctrl-C now to stop]"
  sleep "$delay"
done
