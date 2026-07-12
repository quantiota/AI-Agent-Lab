#!/usr/bin/env python3
"""matrix_read.py — read a room's recent messages (the full discussion), as JSON.

The live agent runs this to PULL room context before contributing — the Matrix analog of
`email_agent inbox`. The listener only pings on a mention; this is how the agent reads the
whole thread (other agents' findings, the evolving state) and treats it as DATA.

    python matrix_read.py '<room_id>' [--limit N]

Auth: MATRIX_TOKEN (homeserver-issued) preferred; user id derived from DOMAIN/MATRIX_USER.
"""
import asyncio
import os
import sys
import json
import argparse
from nio import AsyncClient, MessageDirection, RoomMessageText

HS          = os.environ.get("MATRIX_HOMESERVER", "https://matrix.microserver.network")
SERVER_NAME = os.environ.get("MATRIX_SERVER_NAME", "microserver.network")
CALLSIGN    = os.environ.get("MATRIX_CALLSIGN") or os.environ.get("DOMAIN", "").split(".")[0]
USER        = os.environ.get("MATRIX_USER") or f"@{CALLSIGN}:{SERVER_NAME}"
TOKEN       = os.environ.get("MATRIX_TOKEN")
PW          = os.environ.get("MATRIX_PASSWORD")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("room")
    ap.add_argument("--limit", type=int, default=50)
    a = ap.parse_args()

    c = AsyncClient(HS, USER)
    try:
        if TOKEN:
            c.restore_login(USER, os.environ.get("MATRIX_DEVICE", "agent"), TOKEN)
        else:
            await c.login(PW)
        sync = await c.sync(timeout=5000)          # get a position token + room state
        resp = await c.room_messages(a.room, start=sync.next_batch,
                                     direction=MessageDirection.back, limit=a.limit)
        msgs = []
        for ev in getattr(resp, "chunk", []):
            if isinstance(ev, RoomMessageText):
                msgs.append({"sender": ev.sender, "body": ev.body, "ts": ev.server_timestamp})
        msgs.reverse()                             # oldest first
        print(json.dumps({"room": a.room, "count": len(msgs), "messages": msgs}, indent=2))
    finally:
        await c.close()


asyncio.run(main())
