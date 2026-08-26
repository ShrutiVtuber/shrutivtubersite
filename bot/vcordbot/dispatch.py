# SPDX-License-Identifier: AGPL-3.0-only
"""
An interaction in, a response out.

**A pure function over payloads.** It takes the dict Discord sent and returns
the dict to send back, and it knows nothing about how either arrived. That is
what lets every command be exercised in a test with no token, no server and no
network — and it is what keeps the choice between HTTP interactions and a
gateway a cheap one to reverse.

Discord's interaction types and callback types are small integers; they are
named here rather than written inline, because `{"type": 4}` in a handler is
the sort of thing nobody can read six months later.
"""
from __future__ import annotations

from typing import Any

from vcordbot import render
from vcordbot.astro import Astro, AstroError

# Incoming
PING = 1
APPLICATION_COMMAND = 2

# Outgoing
PONG = 1
CHANNEL_MESSAGE = 4

# Message flags
EPHEMERAL = 1 << 6

# The place used when nobody has said otherwise. Athens because that is where
# the instruments are authored; it is a default, never an assumption about the
# person asking.
ATHENS = {"name": "Athens", "lat": 37.9838, "lon": 23.7275}


def _options(data: dict) -> dict[str, Any]:
    """Discord sends options as a list of dicts; nobody wants to read that."""
    return {o["name"]: o.get("value") for o in (data.get("options") or [])}


async def dispatch(interaction: dict, astro: Astro, *, bot_url: str,
                   site_url: str, now_iso: str) -> dict:
    """
    Answer one interaction.

    `now_iso` is passed in rather than read from the clock so that a test can
    pin it. An instrument whose output depends on the wall clock cannot be
    asserted against otherwise.
    """
    kind = interaction.get("type")

    # Discord PINGs the endpoint to check it is really ours, both when the URL
    # is saved and periodically afterwards. Answering this is the whole of the
    # handshake.
    if kind == PING:
        return {"type": PONG}

    if kind != APPLICATION_COMMAND:
        # Something we have not implemented — a component, a modal. Say so
        # quietly rather than failing in a way the person can see.
        return _message(render.failure(
            "I do not know what to do with that yet.", bot_url, site_url),
            ephemeral=True)

    data = interaction.get("data") or {}
    name = data.get("name")
    opts = _options(data)

    try:
        if name == "hour":
            place = ATHENS
            result = await astro.planetary_hours(now_iso, place["lat"], place["lon"])
            return _message(render.planetary_hours(
                result, place["name"], bot_url, site_url))

        if name == "isopsephy":
            text = (opts.get("text") or "").strip()
            if not text:
                return _message(render.failure(
                    "Give me a word to reckon.", bot_url, site_url), ephemeral=True)
            # Long enough to be a paste rather than a word. Refused before it
            # reaches the ephemeris, so the limit is ours and predictable.
            if len(text) > 200:
                return _message(render.failure(
                    "That is longer than this is for — two hundred characters at most.",
                    bot_url, site_url), ephemeral=True)
            result = await astro.isopsephy(text, opts.get("script") or "greek-iso")
            return _message(render.isopsephy(result, bot_url, site_url))

    except AstroError as exc:
        # The message is already written to be read by a stranger.
        return _message(render.failure(str(exc), bot_url, site_url), ephemeral=True)

    return _message(render.failure(
        "I do not have that command.", bot_url, site_url), ephemeral=True)


def _message(embed: dict, *, ephemeral: bool = False) -> dict:
    data: dict[str, Any] = {"embeds": [embed]}
    if ephemeral:
        data["flags"] = EPHEMERAL
    return {"type": CHANNEL_MESSAGE, "data": data}
