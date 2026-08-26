# SPDX-License-Identifier: AGPL-3.0-only
"""
Twitch EventSub: proving a delivery is real, and turning it into one of ours.

Two jobs, and both have a trap in them.

**Verification.** The endpoint is a public URL. Without the signature check
anybody can post an invented cheer and move a goal bar — the same shape of
problem as the Discord interactions endpoint, with money attached instead of a
message. Twitch signs the message id, the timestamp and the raw body together,
so all three must be used exactly as received.

**Mapping.** A gifted subscription produces TWO deliveries: `channel.subscribe`
for the recipient with `is_gift` true, and `channel.subscription.gift` for the
giver. Counting both is the obvious bug, it doubles every gift bomb, and it
looks like generosity rather than an error.
"""
from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone

# Twitch's own header names, spelled as they arrive.
ID = "twitch-eventsub-message-id"
TIMESTAMP = "twitch-eventsub-message-timestamp"
SIGNATURE = "twitch-eventsub-message-signature"
TYPE = "twitch-eventsub-message-type"

VERIFICATION = "webhook_callback_verification"
NOTIFICATION = "notification"
REVOCATION = "revocation"

# Twitch's own recommendation. A signature stays valid forever without it, so
# a delivery captured once could be replayed indefinitely.
MAX_AGE = timedelta(minutes=10)

# What we ask Twitch to tell us. Raids need no scope; the rest are on her own
# channel and revocable by her at any time.
SUBSCRIPTIONS = [
    ("channel.subscribe", "1", "channel:read:subscriptions"),
    ("channel.subscription.message", "1", "channel:read:subscriptions"),
    ("channel.subscription.gift", "1", "channel:read:subscriptions"),
    ("channel.cheer", "1", "bits:read"),
    ("channel.raid", "1", ""),
    ("channel.follow", "2", "moderator:read:followers"),
]


def verify(secret: str, headers: dict, body: bytes) -> bool:
    """
    Is this really from Twitch, and is it recent?

    `hmac.compare_digest` rather than `==`: a plain comparison returns early on
    the first differing byte, and the time it takes leaks how much of a guess
    was right. That is a real attack on a public endpoint, if a slow one.
    """
    lower = {k.lower(): v for k, v in headers.items()}
    message_id = lower.get(ID, "")
    stamp = lower.get(TIMESTAMP, "")
    signature = lower.get(SIGNATURE, "")
    if not (secret and message_id and stamp and signature):
        return False

    # Old deliveries are refused even when correctly signed. A signature does
    # not expire on its own.
    try:
        sent = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return False
    if abs(datetime.now(timezone.utc) - sent) > MAX_AGE:
        return False

    expected = "sha256=" + hmac.new(
        secret.encode(), (message_id + stamp).encode() + body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def to_event(kind: str, event: dict) -> dict | None:
    """
    One Twitch notification as one of our support events, or None to ignore it.

    Returning None is a real answer and the important one: a gifted
    subscription arrives twice and only the gifter's delivery may be counted.
    """
    if kind == "channel.subscribe":
        # The recipient's copy of a gift. The giver's own delivery carries the
        # count, so counting this one too doubles every gift.
        if event.get("is_gift"):
            return None
        return {"source": "twitch.sub", "quantity": 1,
                "who": event.get("user_name") or "Someone",
                "extra": {"tier": event.get("tier", "1000")}}

    if kind == "channel.subscription.message":
        # A resub, with however many months they have kept it up.
        months = int((event.get("cumulative_months") or 1))
        return {"source": "twitch.sub", "quantity": 1,
                "who": event.get("user_name") or "Someone",
                "message": ((event.get("message") or {}).get("text") or "")[:500],
                "extra": {"tier": event.get("tier", "1000"), "months": months}}

    if kind == "channel.subscription.gift":
        total = int(event.get("total") or 1)
        # Twitch permits anonymous gifting, and `user_name` is then absent.
        # "Anonymous" is a name and should read as one.
        who = "Anonymous" if event.get("is_anonymous") else (event.get("user_name") or "Someone")
        return {"source": "twitch.gift", "quantity": total, "who": who,
                "extra": {"tier": event.get("tier", "1000"), "total": total}}

    if kind == "channel.cheer":
        bits = int(event.get("bits") or 0)
        who = "Anonymous" if event.get("is_anonymous") else (event.get("user_name") or "Someone")
        return {"source": "twitch.bits", "quantity": bits, "who": who,
                "message": (event.get("message") or "")[:500]}

    if kind == "channel.raid":
        return {"source": "twitch.raid",
                "quantity": int(event.get("viewers") or 0),
                "who": event.get("from_broadcaster_user_name") or "Someone"}

    if kind == "channel.follow":
        return {"source": "twitch.follow", "quantity": 1,
                "who": event.get("user_name") or "Someone"}

    return None
