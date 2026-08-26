# SPDX-License-Identifier: AGPL-3.0-only
"""
Configuring announcements, and who is allowed to.

The permission check is the sharp edge. `default_member_permissions` hides a
command in the picker — it is a convenience for the person using Discord, not
an authorisation, and an interaction can be crafted without ever seeing the
picker. So the handler checks too, and this is what proves it.
"""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from vcordbot import announce, dispatch as D, platforms, storage

BOT, SITE = "https://bot.example.test", "https://site.example.test"
NOW = "2026-08-26T12:00:00+03:00"

MANAGE = str(1 << 5)
ADMIN = str(1 << 3)
NOBODY = "0"


@pytest.fixture(autouse=True)
def db(monkeypatch):
    path = Path(tempfile.mkdtemp()) / "t.sqlite3"
    monkeypatch.setattr(storage, "DB", path)
    storage.setup(path)
    return path


def announce_cmd(sub, permissions=MANAGE, guild="g1", channel="c9", **opts):
    return {
        "type": D.APPLICATION_COMMAND,
        "guild_id": guild,
        "channel_id": channel,
        "member": {"permissions": permissions},
        "data": {"name": "announce", "options": [
            {"type": 1, "name": sub,
             "options": [{"name": k, "value": v} for k, v in opts.items()]}]},
    }


def run(interaction):
    return asyncio.run(D.dispatch(interaction, None, bot_url=BOT, site_url=SITE,
                                  now_iso=NOW))


def body(r):
    return r["data"]["embeds"][0]["description"]


# ── who may configure ──────────────────────────────────────────────────────

def test_an_ordinary_member_is_refused() -> None:
    r = run(announce_cmd("here", permissions=NOBODY))
    assert "Manage Server" in body(r)
    assert storage.guild("g1") is None, "nothing should have been written"


def test_manage_server_is_enough() -> None:
    run(announce_cmd("here"))
    assert storage.guild("g1").channel_id == "c9"


def test_an_administrator_is_enough_even_without_the_manage_bit() -> None:
    """
    Administrator implies everything. A server owner without an explicit Manage
    Server bit being refused would be a bug they cannot work around.
    """
    run(announce_cmd("here", permissions=ADMIN, guild="g2"))
    assert storage.guild("g2").channel_id == "c9"


def test_it_refuses_outside_a_server() -> None:
    i = announce_cmd("here")
    del i["guild_id"]
    assert "inside a server" in body(run(i))


# ── configuring ────────────────────────────────────────────────────────────

def test_watch_then_status_reports_it() -> None:
    run(announce_cmd("here"))
    run(announce_cmd("watch", platform="twitch", handle="shruti"))
    said = body(run(announce_cmd("status")))
    assert "shruti" in said and "Twitch" in said
    assert "not checked yet" in said


def test_a_handle_is_cleaned_of_an_at_sign() -> None:
    run(announce_cmd("watch", platform="twitch", handle="@shruti"))
    assert storage.watches("g1")[0].handle == "shruti"


def test_youtube_needs_a_channel_id_and_says_so_now() -> None:
    """
    A @name is the obvious thing to paste and it silently never matches. Better
    to refuse at the moment of typing than to be discovered as silence weeks
    later when a stream is missed.
    """
    r = run(announce_cmd("watch", platform="youtube", handle="@shruti"))
    assert "UC" in body(r)
    assert storage.watches("g1") == []


def test_watching_without_a_channel_says_nothing_will_happen() -> None:
    """Half-configured is the state most likely to be mistaken for broken."""
    said = body(run(announce_cmd("watch", platform="twitch", handle="shruti")))
    assert "/announce here" in said


def test_watching_warns_that_a_running_stream_is_not_announced() -> None:
    run(announce_cmd("here"))
    said = body(run(announce_cmd("watch", platform="twitch", handle="shruti")))
    assert "already running is not announced" in said


def test_unwatch_removes_it() -> None:
    run(announce_cmd("watch", platform="twitch", handle="shruti"))
    run(announce_cmd("unwatch", platform="twitch", handle="shruti"))
    assert storage.watches("g1") == []


def test_every_configuration_reply_is_private() -> None:
    """Setup is between one person and the bot; the channel did not ask."""
    for i in (announce_cmd("here"),
              announce_cmd("watch", platform="twitch", handle="x"),
              announce_cmd("status"),
              announce_cmd("message", template="{handle} live")):
        assert run(i)["data"]["flags"] == D.EPHEMERAL


# ── what gets said ─────────────────────────────────────────────────────────

def test_the_template_is_used_when_given() -> None:
    w = storage.Watch(1, "g1", "twitch", "shruti", "offline", "")
    s = platforms.Status(platforms.LIVE, title="Building a bot", game="Software",
                         url="https://twitch.tv/shruti")
    content, _ = announce.message_for(w, s, "{handle} is on — {title} {url}", "")
    assert content == "shruti is on — Building a bot https://twitch.tv/shruti"


def test_a_mention_is_prefixed_and_is_the_only_thing_pingable() -> None:
    w = storage.Watch(1, "g1", "twitch", "shruti", "offline", "")
    s = platforms.Status(platforms.LIVE, url="https://twitch.tv/shruti")
    content, _ = announce.message_for(w, s, "", "42")
    assert content.startswith("<@&42>")


def test_everyone_can_never_be_pinged_by_a_stream_title() -> None:
    """
    A title, or a template somebody pasted, containing @everyone would ping the
    whole server if allowed_mentions were left to the default. It is set
    explicitly on every post, naming at most the one configured role.
    """
    from conftest import code_of
    from vcordbot import discord_api
    src = code_of(discord_api.post_message)
    assert "allowed_mentions" in src
    assert '"parse": []' in src or "'parse': []" in src
