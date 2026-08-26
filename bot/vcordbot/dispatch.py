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

from vcordbot import announce, render, storage
from vcordbot.astro import Astro, AstroError

# Incoming
PING = 1
APPLICATION_COMMAND = 2

# Outgoing
PONG = 1
CHANNEL_MESSAGE = 4

# Message flags
EPHEMERAL = 1 << 6

# Manage Server. Checked in the handler as well as declared on the command:
# `default_member_permissions` hides a command in the picker, which is a UI
# convenience, not an authorisation — an interaction can still be crafted.
MANAGE_GUILD = 1 << 5

# The place used when nobody has said otherwise. Athens because that is where
# the instruments are authored; it is a default, never an assumption about the
# person asking.
ATHENS = {"name": "Athens", "lat": 37.9838, "lon": 23.7275}


def _options(data: dict) -> dict[str, Any]:
    """Discord sends options as a list of dicts; nobody wants to read that."""
    return {o["name"]: o.get("value") for o in (data.get("options") or [])}


def _subcommand(data: dict) -> tuple[str, dict]:
    """The chosen subcommand and its own options."""
    for o in data.get("options") or []:
        if o.get("type") == 1:
            return o.get("name", ""), _options(o)
    return "", {}


def _may_manage(interaction: dict) -> bool:
    """
    Whether this person may change what the server announces.

    Discord sends the invoking member's resolved permissions as a decimal
    string. Administrator implies everything, so it is checked separately —
    otherwise a server owner without an explicit Manage Server bit is refused.
    """
    member = interaction.get("member") or {}
    try:
        perms = int(member.get("permissions", "0"))
    except (TypeError, ValueError):
        return False
    ADMINISTRATOR = 1 << 3
    return bool(perms & (MANAGE_GUILD | ADMINISTRATOR))


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

        if name == "announce":
            return await _announce(interaction, opts, data, bot_url, site_url)

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


async def _announce(interaction: dict, opts: dict, data: dict,
                    bot_url: str, site_url: str) -> dict:
    """
    Configure what a server announces.

    Every reply is ephemeral. Configuration is a conversation between one
    person and the bot, and posting "watching twitch/shruti" into a channel is
    noise for everybody else — and tells the room a little about the setup they
    did not ask for.
    """
    guild_id = interaction.get("guild_id")
    if not guild_id:
        return _message(render.failure(
            "That only works inside a server.", bot_url, site_url), ephemeral=True)

    if not _may_manage(interaction):
        return _message(render.failure(
            "You need Manage Server to change what this server announces.",
            bot_url, site_url), ephemeral=True)

    sub, o = _subcommand(data)

    if sub == "here":
        channel_id = str(interaction.get("channel_id") or "")
        await storage.to_thread(storage.set_channel, guild_id, channel_id)
        role = str(o.get("mention") or "")
        await storage.to_thread(storage.set_mention, guild_id, role)
        said = f"Announcements will appear in <#{channel_id}>."
        if role:
            said += f" <@&{role}> will be pinged — and nothing else can be."
        return _message(render.embed("Set", f"{said}\n\n{render.footer(bot_url, site_url)}"),
                        ephemeral=True)

    if sub in ("watch", "unwatch"):
        platform = str(o.get("platform") or "")
        handle = str(o.get("handle") or "").strip().lstrip("@")
        if not handle:
            return _message(render.failure("Give me a handle to watch.", bot_url, site_url),
                            ephemeral=True)
        # A YouTube channel id, not a @name or a URL. Said now rather than
        # discovered as silence at the next stream.
        if platform == "youtube" and not handle.startswith("UC"):
            return _message(render.failure(
                "YouTube needs the channel ID — the one starting `UC`, from the "
                "channel's About page. A @name or a link will not work.",
                bot_url, site_url), ephemeral=True)

        if sub == "watch":
            g = await storage.to_thread(storage.guild, guild_id)
            added = await storage.to_thread(storage.add_watch, guild_id, platform, handle)
            said = (f"Watching **{handle}** on {platform.title()}."
                    if added else f"Already watching **{handle}** on {platform.title()}.")
            if not (g and g.channel_id):
                said += ("\n\nNothing will be posted yet — run `/announce here` in "
                         "the channel it should go to.")
            else:
                said += ("\n\nThe first announcement comes at the next time it goes "
                         "live. A stream already running is not announced, because "
                         "the bot has nothing to compare against yet.")
            return _message(render.embed("Watching", f"{said}\n\n{render.footer(bot_url, site_url)}"),
                            ephemeral=True)

        gone = await storage.to_thread(storage.remove_watch, guild_id, platform, handle)
        return _message(render.embed(
            "Stopped" if gone else "Not watching",
            f"{'No longer watching' if gone else 'Was not watching'} **{handle}** "
            f"on {platform.title()}.\n\n{render.footer(bot_url, site_url)}"), ephemeral=True)

    if sub == "message":
        template = str(o.get("template") or "").strip()[:400]
        await storage.to_thread(storage.set_template, guild_id, template)
        return _message(render.embed(
            "Set", f"Announcements will say:\n\n{template}\n\n"
                   f"{render.footer(bot_url, site_url)}"), ephemeral=True)

    if sub == "status":
        g = await storage.to_thread(storage.guild, guild_id)
        ws = await storage.to_thread(storage.watches, guild_id)
        lines = []
        lines.append(f"Channel: {'<#' + g.channel_id + '>' if g and g.channel_id else '**not set** — run `/announce here`'}")
        if g and g.mention_role:
            lines.append(f"Pings: <@&{g.mention_role}>")
        lines.append(f"Message: {g.template if g and g.template else '_the default_'}")
        lines.append("")
        if ws:
            for w in ws:
                seen = {"live": "live now", "offline": "offline",
                        "": "not checked yet"}.get(w.last_state, w.last_state)
                lines.append(f"· **{w.handle}** on {w.platform.title()} — {seen}")
        else:
            lines.append("_Nothing watched yet — `/announce watch`._")
        lines += ["", render.footer(bot_url, site_url)]
        return _message(render.embed("Announcements here", "\n".join(lines)), ephemeral=True)

    return _message(render.failure("I do not know that one.", bot_url, site_url),
                    ephemeral=True)
