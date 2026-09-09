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

from vcordbot import announce, commands, periods, places, render, storage
from vcordbot.astro import Astro, AstroError
from vcordbot.places import PlaceError

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
# person asking — which is why every command that uses it takes a `place` and
# says which one it answered for.
ATHENS = places.Place(
    name="Athens", region="Attica", country="Greece", country_code="GR",
    lat=37.9838, lon=23.7275, elevation=90.0,
    timezone="Europe/Athens", population=664046,
)


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
            place = await _place(opts)
            result = await astro.planetary_hours(now_iso, place.lat, place.lon)
            return _message(render.planetary_hours(
                result, place.label, bot_url, site_url))

        if name == "panchanga":
            place = await _place(opts)
            result = await astro.panchanga(now_iso, place.lat, place.lon)
            return _message(render.panchanga(
                result, place.label, bot_url, site_url))

        if name == "attic":
            when = (opts.get("date") or "").strip()
            if when:
                # Refused rather than guessed, for the same reason a birth date
                # is: 05/14 and 14/05 are the same characters under two
                # conventions that disagree for most of the year.
                from datetime import date as _date
                try:
                    when = f"{_date.fromisoformat(when).isoformat()}T12:00:00+00:00"
                except ValueError:
                    return _message(render.failure(
                        "I need the date as `YYYY-MM-DD` — `2026-08-28`.",
                        bot_url, site_url), ephemeral=True)
            result = await astro.attic(when or now_iso,
                                       opts.get("reckoning") or "conjunction")
            return _message(render.attic(result, bot_url, site_url))

        if name == "hindu":
            place = await _place(opts)
            result = await astro.hindu(now_iso, place.lat, place.lon,
                                       opts.get("reckoning") or "amanta")
            return _message(render.hindu(
                result, place.label, bot_url, site_url))

        if name == "sigil":
            statement = (opts.get("statement") or "").strip()
            if not statement:
                return _message(render.failure(
                    "Give me a statement of intent.", bot_url, site_url), ephemeral=True)
            if len(statement) > 200:
                return _message(render.failure(
                    "That is longer than this is for — two hundred characters at most.",
                    bot_url, site_url), ephemeral=True)
            result = await astro.sigil(statement)
            return _message(render.sigil(result, bot_url, site_url))

        if name == "stations":
            place = await _place(opts)
            body = opts.get("body") or "sun"
            result = await astro.stations(body, now_iso, place.lat, place.lon)
            return _message(render.stations(
                result, place.label, bot_url, site_url))

        if name == "horoscope":
            # The cheap half of the practice bridge: hand back the material to
            # write from. Reading the channel — the other half — needs a gateway
            # this bot does not have, so this stands alone until it does.
            sign = (opts.get("sign") or "aries").strip().lower()
            period = (opts.get("period") or "weekly").strip().lower()
            if period not in periods.PERIODS:
                period = "weekly"
            covers = periods.current_covers(period)
            start, end = periods.span(period, covers)
            result = await astro.events(f"{start}T00:00:00Z", f"{end}T23:59:59Z")
            return _message(render.horoscope_material(
                result, sign=sign, period_label=periods.label(period, covers),
                start=start, end=end, bot_url=bot_url, site_url=site_url))

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

        if name == "chart":
            return await _chart(opts, astro, bot_url=bot_url, site_url=site_url)

        if name == "help":
            return _message(render.manual(
                commands.COMMANDS, bot_url, site_url,
                only=(opts.get("command") or "").strip().lstrip("/")),
                ephemeral=True)

        if name == "announce":
            return await _announce(interaction, opts, data, bot_url, site_url)

    except PlaceError as exc:
        # Already written to be read by a stranger, and never blaming them for
        # a city the gazetteer spells differently.
        return _message(render.failure(str(exc), bot_url, site_url), ephemeral=True)

    except AstroError as exc:
        # The message is already written to be read by a stranger.
        return _message(render.failure(str(exc), bot_url, site_url), ephemeral=True)

    return _message(render.failure(
        "I do not have that command.", bot_url, site_url), ephemeral=True)


async def _place(opts: dict) -> places.Place:
    """
    Where the answer is for.

    Athens when nobody says. **The option used to be read by nothing at all**:
    the handler took Athens whatever was typed and titled the answer "Athens"
    to match, so `/hour place:Tokyo` was not a missing feature but a confident
    wrong answer — the one shape of failure this project refuses everywhere
    else.
    """
    named = (opts.get("place") or "").strip()
    if not named:
        return ATHENS
    best, _others = await places.lookup(named)
    return best


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


# ── the chart ───────────────────────────────────────────────────────────────

# What somebody types when they do not have a birth time. Accepted as a VALUE
# of the time option rather than as a separate flag, so nobody types 12:00 to
# get past a required field and is handed a fabricated ascendant for it.
UNKNOWN = {"unknown", "unsure", "?", "none", "no", "n/a", "na", "-"}

# Local noon when the time is unknown: the least-wrong instant for the planets,
# and it is stated in the answer rather than hidden.
NOON = "12:00"


def _birth_date(raw: str) -> str:
    """
    An ISO date, or a refusal that says what was wanted.

    Refused rather than guessed. `05/14/1996` and `14/05/1996` are the same
    eight characters arranged by two conventions that disagree about half the
    year, and a chart cast on the wrong one is a chart for a different person.
    """
    from datetime import date

    text = (raw or "").strip()
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        raise PlaceError(
            "I need the birth date as `YYYY-MM-DD` — `1996-05-14`. "
            "I will not guess at `05/14/1996`, because half the world reads "
            "that as the fourteenth of May and half as the fifth of the "
            "fourteenth month."
        ) from None
    # The ephemeris is good for a wide span but not an unbounded one, and a
    # typo in the year is far commoner than a genuine mediaeval nativity.
    if not 1 <= parsed.year <= 2999:
        raise PlaceError("That year is outside what I can compute.")
    return parsed.isoformat()


def _birth_time(raw: str) -> str | None:
    """
    A 24-hour clock time, or None for an unknown one.

    `9:30 pm` is the commonest way this goes wrong, and it is worth catching by
    name: taken as 24-hour it is half past nine in the morning, twelve hours
    and a whole different chart away from what was meant.
    """
    text = (raw or "").strip().lower()
    if text in UNKNOWN:
        return None

    if text.endswith(("am", "pm")) or " am" in text or " pm" in text:
        raise PlaceError(
            "That looks like a 12-hour time. I need it on the 24-hour clock — "
            "half past nine at night is `21:30`, half past nine in the morning "
            "is `09:30`."
        )

    digits = text.replace(".", ":").replace("h", ":").strip(":")
    if ":" not in digits and digits.isdigit() and len(digits) == 4:
        digits = f"{digits[:2]}:{digits[2:]}"

    parts = digits.split(":")
    if len(parts) < 2 or not all(p.isdigit() for p in parts[:2]):
        raise PlaceError("I need the birth time as `HH:MM` on the 24-hour clock — "
                         "`09:30`, or `21:30`. Say `unknown` if you do not have it.")
    hour, minute = int(parts[0]), int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise PlaceError("That is not a time on the 24-hour clock.")
    return f"{hour:02d}:{minute:02d}"


async def _chart(opts: dict, astro: Astro, *, bot_url: str, site_url: str) -> dict:
    """
    Cast one chart and hand it back to the person who asked, and to nobody else.

    **Ephemeral unless they say otherwise.** A chart IS birth data — the
    ascendant gives the time of day to within a few minutes and the planets
    give the date — so posting one into a shared channel by default would put
    somebody's birth record in a room they did not choose. `share:true` is a
    decision, made by the only person entitled to make it.

    Nothing here is written down. No row, no cache, no log line carrying a
    date, a time or a place.
    """
    date = _birth_date(opts.get("date") or "")
    clock = _birth_time(opts.get("time") or "")
    tradition = opts.get("tradition") or "hellenistic"
    share = bool(opts.get("share"))

    place, alternatives = await places.find(
        opts.get("city") or "", opts.get("country") or "", opts.get("state") or "")

    moment = places.at(place, date, clock or NOON)

    data = await astro.chart(moment.when, place.lat, place.lon, tradition=tradition)

    # The Moon moves twelve to fifteen degrees across a day, so with no birth
    # time a single figure for it is precision the chart does not have. Two
    # further reads at the ends of that local day give the range it was really
    # somewhere inside — an honest interval rather than an estimate.
    moon_range = None
    if clock is None:
        try:
            first = places.at(place, date, "00:00")
            last = places.at(place, date, "23:59")
            ends = [await astro.chart(m.when, place.lat, place.lon, tradition=tradition)
                    for m in (first, last)]
            moons = [next((b for b in (e.get("bodies") or [])
                           if b.get("name") == "Moon"), None) for e in ends]
            if all(moons):
                start, end = (render._sign_of(m) for m in moons)
                moon_range = (f"{render._dms(start[1])} {start[0]}",
                              f"{render._dms(end[1])} {end[0]}")
        except (AstroError, PlaceError):
            # A refinement, not the answer. The chart still stands without it.
            moon_range = None

    return _message(
        render.chart(data, place=place, moment=moment, tradition=tradition,
                     time_unknown=clock is None, moon_range=moon_range,
                     alternatives=alternatives, bot_url=bot_url, site_url=site_url),
        ephemeral=not share)
