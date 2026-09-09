# SPDX-License-Identifier: AGPL-3.0-only
"""
The Discord gateway: reading a channel, so Discord can talk back.

⚠ **This is the expensive half of the bridge, and the cost is not the
permission.** The bot has been HTTP-interactions-only: Discord calls it, it
answers, nothing is held open. A gateway is a socket that must be kept alive,
resumed after a drop, and reconnected after an invalidation — a long-running
process with a state machine, which is a different kind of thing to run.

⚠ **MESSAGE_CONTENT is a PRIVILEGED intent.** It has to be switched on in the
Discord developer portal, and for a bot in a hundred servers it needs review.
Until it is on, Discord sends messages with empty content and this consumer sees
nothing — no error, no warning, just silence. So `identify` asks for it
explicitly and the reader says so plainly when every message arrives blank,
because "the bridge does nothing" is otherwise indistinguishable from "the
channel is quiet".

The state machine, briefly:

    connect → HELLO (10) → identify (2) → READY (0/READY)
                        ↘ heartbeat every heartbeat_interval (1)
    drop → resume (6) with the last sequence → RESUMED, or
           INVALID_SESSION (9) → identify again from nothing
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

log = logging.getLogger("vcordbot.gateway")

GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"

# Opcodes, named rather than numbered at the call sites.
DISPATCH = 0
HEARTBEAT = 1
IDENTIFY = 2
RESUME = 6
RECONNECT = 7
INVALID_SESSION = 9
HELLO = 10
HEARTBEAT_ACK = 11

# ⚠ GUILD_MESSAGES puts the events on the socket; MESSAGE_CONTENT is what makes
# them carry any words. Asking for the first without the second gets a stream of
# empty messages, which reads exactly like a quiet channel.
GUILD_MESSAGES = 1 << 9
MESSAGE_CONTENT = 1 << 15
INTENTS = GUILD_MESSAGES | MESSAGE_CONTENT


@dataclass
class Session:
    """What has to survive a dropped socket for a resume to be possible."""

    session_id: str = ""
    resume_url: str = ""
    sequence: int | None = None
    # Counted so the reader can say the intent is off rather than sit quiet.
    blank_messages: int = 0
    read_messages: int = 0
    warned_about_intent: bool = False
    seen: set[str] = field(default_factory=set)

    def can_resume(self) -> bool:
        return bool(self.session_id and self.resume_url)


def identify_payload(token: str) -> dict:
    return {
        "op": IDENTIFY,
        "d": {
            "token": token,
            "intents": INTENTS,
            "properties": {"os": "linux", "browser": "vcordbot",
                           "device": "vcordbot"},
        },
    }


def resume_payload(token: str, session: Session) -> dict:
    return {
        "op": RESUME,
        "d": {"token": token, "session_id": session.session_id,
              "seq": session.sequence},
    }


def backoff(attempt: int) -> float:
    """
    How long to wait before trying again.

    Jittered, because every bot on a shard reconnects at once when Discord
    restarts one, and a synchronised stampede is how a reconnect storm becomes
    a rate limit.
    """
    # ⚠ Capped AFTER the jitter. Capping first and then multiplying by up to
    # 1.5 means the "maximum" is really ninety seconds — which is what this said
    # until a test asked it for backoff(50) and got 66.
    return min(60.0, (1.5 ** min(attempt, 10)) * (0.5 + random.random()))


def is_ours(message: dict, *, channel_id: str, bot_user_id: str) -> bool:
    """
    Whether this message is one the bridge should carry.

    ⚠ Three refusals, and the middle one matters most: a message from THIS bot
    must never come back in, or announcing a submission would relay it to the
    site as a comment on itself, which would announce again.
    """
    if str(message.get("channel_id") or "") != str(channel_id):
        return False
    author = message.get("author") or {}
    if str(author.get("id") or "") == str(bot_user_id):
        return False
    if author.get("bot"):
        return False
    return True


class Reader:
    """
    Holds the socket open and hands each message to `on_message`.

    Given a `connect` callable so it can be driven in a test without a network:
    the state machine is the thing worth testing, and it is entirely separate
    from websockets.
    """

    def __init__(
        self,
        token: str,
        *,
        channel_id: str,
        on_message: Callable[[dict], Awaitable[None]],
        connect: Callable[[str], Any] | None = None,
    ) -> None:
        self.token = token
        self.channel_id = channel_id
        self.on_message = on_message
        self.session = Session()
        self.bot_user_id = ""
        self._connect = connect
        self._closing = False

    async def handle(self, frame: dict, send: Callable[[dict], Awaitable[None]]) -> None:
        """One frame off the socket. The whole protocol, in one place."""
        op = frame.get("op")
        if frame.get("s") is not None:
            self.session.sequence = frame["s"]

        if op == HELLO:
            await send(identify_payload(self.token) if not self.session.can_resume()
                       else resume_payload(self.token, self.session))
            return

        if op == HEARTBEAT:
            # Discord asking for one early. Answer immediately or be dropped.
            await send({"op": HEARTBEAT, "d": self.session.sequence})
            return

        if op == INVALID_SESSION:
            # d=True means resumable. False means start clean — and keeping the
            # old session id would loop forever on the same refusal.
            if not frame.get("d"):
                self.session = Session()
            return

        if op != DISPATCH:
            return

        name = frame.get("t")
        data = frame.get("d") or {}

        if name == "READY":
            self.session.session_id = data.get("session_id", "")
            self.session.resume_url = (data.get("resume_gateway_url") or "")
            self.bot_user_id = str((data.get("user") or {}).get("id") or "")
            log.info("gateway ready")
            return

        if name != "MESSAGE_CREATE":
            return

        if not is_ours(data, channel_id=self.channel_id,
                       bot_user_id=self.bot_user_id):
            return

        # ⚠ Discord redelivers on resume. Without this, one message becomes two
        # comments every time the socket blinks.
        mid = str(data.get("id") or "")
        if mid and mid in self.session.seen:
            return
        if mid:
            self.session.seen.add(mid)
            if len(self.session.seen) > 500:
                self.session.seen = set(list(self.session.seen)[-250:])

        if not (data.get("content") or "").strip():
            self.session.blank_messages += 1
            self._maybe_warn()
            return

        self.session.read_messages += 1
        await self.on_message(data)

    def _maybe_warn(self) -> None:
        """
        Say the intent is off rather than sitting quiet.

        Every message arriving empty is what a bot without MESSAGE_CONTENT sees,
        and it is indistinguishable from a channel where nobody is talking. Ten
        blanks and nothing read is not a coincidence.
        """
        if self.session.warned_about_intent:
            return
        if self.session.blank_messages >= 10 and self.session.read_messages == 0:
            self.session.warned_about_intent = True
            log.warning(
                "every message on this channel has arrived with no content. "
                "MESSAGE_CONTENT is a privileged intent and is probably off — "
                "switch it on for this application in the Discord developer "
                "portal, under Bot → Privileged Gateway Intents."
            )

    async def beat(self, send: Callable[[dict], Awaitable[None]],
                   interval_ms: int) -> None:
        """
        Heartbeat forever, jittered on the first one.

        Discord asks for the jitter, and for the same reason as the backoff:
        every bot heartbeating on the same tick is a thundering herd.
        """
        await asyncio.sleep(interval_ms / 1000 * random.random())
        while not self._closing:
            await send({"op": HEARTBEAT, "d": self.session.sequence})
            await asyncio.sleep(interval_ms / 1000)

    def stop(self) -> None:
        self._closing = True
