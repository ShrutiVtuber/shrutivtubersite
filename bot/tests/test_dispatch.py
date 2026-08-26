# SPDX-License-Identifier: AGPL-3.0-only
"""
Every command, answered, without Discord being involved at all.

The ephemeris is a stand-in here. What is under test is the bot's own
behaviour: what it does with an empty argument, an enormous one, an ephemeris
that will not answer, and a command it has never heard of.
"""
from __future__ import annotations

import asyncio

from vcordbot import dispatch as D
from vcordbot.astro import AstroError

BOT, SITE = "https://bot.example.test", "https://site.example.test"
NOW = "2026-08-26T12:00:00+03:00"


class FakeAstro:
    """Answers like the daemon does, or refuses on command."""

    def __init__(self, *, fail: str | None = None) -> None:
        self.fail = fail
        self.calls: list[tuple] = []

    async def planetary_hours(self, when, lat, lon):
        self.calls.append(("hours", when, lat, lon))
        if self.fail:
            raise AstroError(self.fail)
        return {"current": {"index": 5, "ruler": "Mars", "isNight": False,
                            "endsAt": "2026-08-26T09:20:25+00:00"},
                "sunrise": "2026-08-26T03:49:25+00:00",
                "sunset": "2026-08-26T17:03:48+00:00", "dayRuler": "Mercury"}

    async def isopsephy(self, text, cipher="greek-iso"):
        self.calls.append(("iso", text, cipher))
        if self.fail:
            raise AstroError(self.fail)
        return {"text": text, "total": 373, "cipher": {"name": "Isopsephy"},
                "letters": [{"char": "λ", "value": 30}],
                "reduction": {"final": 4}, "unmatched": []}


def cmd(name, **options):
    return {"type": D.APPLICATION_COMMAND,
            "data": {"name": name,
                     "options": [{"name": k, "value": v} for k, v in options.items()]}}


def run(interaction, astro=None):
    """
    Drive one interaction to completion.

    Synchronous on purpose: `pytest-asyncio` would be a plugin dependency for
    the sake of a decorator, and a test suite that needs a plugin to run is one
    more thing standing between somebody and finding out whether the bot works.
    """
    return asyncio.run(D.dispatch(interaction, astro or FakeAstro(),
                                  bot_url=BOT, site_url=SITE, now_iso=NOW))


def test_ping_is_answered_with_pong() -> None:
    """
    The whole handshake. Discord sends this when the endpoint URL is saved and
    periodically after; get it wrong and the URL cannot even be set.
    """
    assert run({"type": D.PING}) == {"type": D.PONG}


def test_the_hour_answers_publicly() -> None:
    r = run(cmd("hour"))
    assert r["type"] == D.CHANNEL_MESSAGE
    assert "Mars" in r["data"]["embeds"][0]["description"]
    # Not ephemeral: the whole point is that a channel sees it.
    assert "flags" not in r["data"]


def test_isopsephy_passes_the_cipher_slug_through() -> None:
    """
    The daemon takes a cipher SLUG. It was sent a language name once, ignored
    it, fell back to Greek, and returned a confident total with every Hebrew
    letter unmatched — a wrong answer that looked entirely right.
    """
    a = FakeAstro()
    run(cmd("isopsephy", text="אמת", script="heb-hechrachi"), a)
    assert a.calls == [("iso", "אמת", "heb-hechrachi")]


def test_isopsephy_defaults_to_greek() -> None:
    a = FakeAstro()
    run(cmd("isopsephy", text="ΛΟΓΟΣ"), a)
    assert a.calls[0][2] == "greek-iso"


def test_every_offered_cipher_is_a_slug_the_daemon_knows() -> None:
    """
    The choices in the picker are sent verbatim as the cipher. A friendly
    language name among them would be silently ignored by the daemon and
    answered in Greek, which is how this broke the first time.
    """
    from vcordbot.commands import COMMANDS
    iso = next(c for c in COMMANDS if c["name"] == "isopsephy")
    script = next(o for o in iso["options"] if o["name"] == "script")
    for choice in script["choices"]:
        assert "-" in choice["value"], (
            f"{choice['value']!r} is not a cipher slug — the daemon takes "
            f"slugs like 'heb-hechrachi', not language names")


def test_an_empty_word_is_refused_before_the_ephemeris() -> None:
    a = FakeAstro()
    r = run(cmd("isopsephy", text="   "), a)
    assert a.calls == [], "nothing should have been asked"
    assert r["data"]["flags"] == D.EPHEMERAL, "a scolding should be private"


def test_a_paste_is_refused_by_us_not_by_the_ephemeris() -> None:
    """Our limit, so the message is ours and predictable."""
    a = FakeAstro()
    r = run(cmd("isopsephy", text="α" * 500), a)
    assert a.calls == []
    assert "two hundred" in r["data"]["embeds"][0]["description"]


def test_an_ephemeris_failure_is_shown_privately_and_kindly() -> None:
    r = run(cmd("hour"), FakeAstro(fail="The ephemeris took too long to answer."))
    body = r["data"]["embeds"][0]["description"]
    assert r["data"]["flags"] == D.EPHEMERAL
    assert "took too long" in body

    # Only the message itself. The footer below it carries links by design, and
    # an earlier version of this test split on the wrong side of them and
    # failed the code for the footer doing its job.
    from vcordbot import render
    said = body.split(render.SUBTEXT)[0]
    assert "Traceback" not in said
    assert "http" not in said, "an internal hostname must not reach a stranger's channel"


def test_an_unknown_command_does_not_raise() -> None:
    r = run(cmd("summon"))
    assert r["type"] == D.CHANNEL_MESSAGE
    assert r["data"]["flags"] == D.EPHEMERAL


def test_every_registered_command_is_actually_implemented() -> None:
    """
    The failure this catches: a command registered with Discord, visible in the
    picker, and answering "I do not have that command" — which looks like a
    broken bot to everyone but us.
    """
    from vcordbot.commands import COMMANDS
    for c in COMMANDS:
        required = {o["name"]: "ΛΟΓΟΣ" for o in c.get("options", []) if o.get("required")}
        r = run(cmd(c["name"], **required))
        body = r["data"]["embeds"][0]["description"]
        assert "I do not have that command" not in body, f"/{c['name']} is not implemented"


def test_every_answer_carries_the_footer() -> None:
    from vcordbot import render
    for interaction in (cmd("hour"), cmd("isopsephy", text="ΛΟΓΟΣ"), cmd("nope")):
        r = run(interaction)
        assert render.footer(BOT, SITE) in r["data"]["embeds"][0]["description"]
