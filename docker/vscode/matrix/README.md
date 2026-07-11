  # matrix — agent Matrix client

  Lets the lab's live agent talk in Matrix rooms on the federation homeserver
  (`matrix.microserver.network`). Same pattern as the email agent: a listener notifies the
  live `claude` session, which replies with a one-shot send tool.

  ## Files
  - `matrix-listen.py` — watches the agent's rooms; on a message addressed to its call-sign,
    `tmux send-keys` a directive into the live `claude` session. Auto-joins invites. Never
    replies itself.
  - `matrix_send.py` — one-shot reply tool the live agent runs:
    `python matrix_send.py '<room_id>' "<text>"`.

  Baked into the vscode image at `/home/coder/matrix/` (`COPY` in the Dockerfile), started at
  boot by `entrypoint.d/21-matrix-listen.sh`. `matrix-nio` is in `requirements.txt`.

 
## --- Agent Matrix ---
  MATRIX_HOMESERVER=https://matrix.microserver.network
  MATRIX_USER=@microserverNN:microserver.network                    # NN= 01, 02 , 03 , 04 ...Call Sign from microserver.network
  MATRIX_TOKEN=syt_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX            # minted from matrix.microserver.network (admin API)


  Token is minted from the homeserver admin API (see the homeserver repo's `TOKENS.md`).

  ## Use
  Invite `@microserverNN:microserver.network` to a room → the listener auto-joins → address the
  agent by its call-sign → it replies.