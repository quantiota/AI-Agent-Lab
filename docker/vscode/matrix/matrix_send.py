#!/usr/bin/env python3
"""matrix_send.py — post ONE message to a Matrix room, then exit.

The LIVE Claude runs this to reply in a room (the Matrix analog of `email_agent reply`):

    python matrix_send.py '<room_id>' '<your reply text>'

Auth: prefer MATRIX_TOKEN (homeserver-issued); user id derived from DOMAIN/callsign unless
MATRIX_USER is set. MATRIX_PASSWORD is a dev fallback only.
Env: MATRIX_HOMESERVER (default https://matrix.microserver.network), MATRIX_TOKEN | MATRIX_PASSWORD,
     MATRIX_SERVER_NAME (default microserver.network), MATRIX_CALLSIGN | DOMAIN, MATRIX_USER (override).
"""
import asyncio
import os
import sys
from nio import AsyncClient

HS          = os.environ.get("MATRIX_HOMESERVER", "https://matrix.microserver.network")
SERVER_NAME = os.environ.get("MATRIX_SERVER_NAME", "microserver.network")
CALLSIGN    = os.environ.get("MATRIX_CALLSIGN") or os.environ.get("DOMAIN", "").split(".")[0]
USER        = os.environ.get("MATRIX_USER") or f"@{CALLSIGN}:{SERVER_NAME}"
TOKEN       = os.environ.get("MATRIX_TOKEN")
PW          = os.environ.get("MATRIX_PASSWORD")


async def main():
    if len(sys.argv) < 3:
        print("usage: matrix_send.py <room_id> <text>")
        sys.exit(1)
    room, text = sys.argv[1], sys.argv[2]
    c = AsyncClient(HS, USER)
    try:
        if TOKEN:
            c.restore_login(USER, os.environ.get("MATRIX_DEVICE", "agent"), TOKEN)
        else:
            await c.login(PW)
        await c.room_send(room, "m.room.message", {"msgtype": "m.text", "body": text})
        print("sent to", room)
    finally:
        await c.close()


asyncio.run(main())
