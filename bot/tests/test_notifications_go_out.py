# SPDX-License-Identifier: AGPL-3.0-only
"""
Telling phones a stream started.

⚠ **The bot is the only thing that knows a stream STARTED.** The site polls a
status and can say whether she is live now; the transition — was offline, is now
live, and not merely a blip — is `platforms.should_announce`, and it lives here.
Deciding it twice would mean two things with two opinions, and one of them
announcing at the wrong moment.

⚠ **Once per sweep, not once per watch.** She is announced in however many
Discord servers have a watch on her; the phones are one audience and must hear
it once. This is the failure that would look completely fine in testing — one
server, one notification — and become five notifications the day a second
server adds the bot.
"""
from __future__ import annotations

import asyncio

from vcordbot import announce


class _Recorder:
    """Stands in for the site, and counts what it was told."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def __call__(self, kind, *, title, body, url, client=None):
        self.calls.append({"kind": kind, "title": title, "body": body, "url": url})
        return True


def test_the_site_is_told_at_the_transition(monkeypatch) -> None:
    told = _Recorder()
    monkeypatch.setattr(announce, "tell_the_site", told)
    _sweep(monkeypatch, watches=1, going_live=True)
    assert [c["kind"] for c in told.calls] == ["live"]
    assert "live" in told.calls[0]["title"]


def test_two_servers_watching_is_still_one_notification(monkeypatch) -> None:
    """
    The one that looks fine with a single server and becomes five the day a
    second one adds the bot.
    """
    told = _Recorder()
    monkeypatch.setattr(announce, "tell_the_site", told)
    _sweep(monkeypatch, watches=3, going_live=True)
    assert len(told.calls) == 1, f"told {len(told.calls)} times for 3 watches"


def test_nothing_is_sent_when_nothing_changed(monkeypatch) -> None:
    told = _Recorder()
    monkeypatch.setattr(announce, "tell_the_site", told)
    _sweep(monkeypatch, watches=2, going_live=False)
    assert told.calls == []


def test_the_site_being_down_does_not_stop_the_discord_post(monkeypatch) -> None:
    """
    The channel post is the thing that must happen. A push service having a bad
    day must not take the announcement with it.
    """
    async def refuses(*a, **k):
        raise RuntimeError("the site is down")

    monkeypatch.setattr(announce, "tell_the_site", refuses)
    posted = _sweep(monkeypatch, watches=1, going_live=True, expect_raise=False)
    assert posted >= 1, "the Discord announcement was lost with the notification"


# ── the harness ─────────────────────────────────────────────────────────────

def _sweep(monkeypatch, *, watches: int, going_live: bool,
           expect_raise: bool = False) -> int:
    """Run one announce sweep with fake storage, platforms and Discord."""
    from vcordbot import platforms, storage

    made = [
        storage.Watch(id=i, guild_id=f"g{i}", platform="twitch",
                      handle="shruti",
                      last_state="offline" if going_live else "live",
                      last_announced="")
        for i in range(1, watches + 1)
    ]
    posts: list = []

    async def to_thread(fn, *a, **k):
        if fn is storage.watches:
            return made
        if fn is storage.guild:
            return storage.Guild(guild_id=a[0], channel_id="chan",
                                 mention_role="", template="")
        return None

    async def check(*a, **k):
        return platforms.Status(state="live" if going_live else "offline",
                                title="Building the site", url="https://twitch.tv/x")

    async def post(*a, **k):
        posts.append(a)
        return True

    monkeypatch.setattr(storage, "to_thread", to_thread)
    monkeypatch.setattr(announce.storage, "to_thread", to_thread)
    monkeypatch.setattr(announce.platforms, "twitch", check)
    monkeypatch.setattr(announce.platforms, "youtube", check)
    monkeypatch.setattr(announce, "post_message", post)

    asyncio.run(announce.check_all(token="t", bot_url="b", site_url="s"))
    return len(posts)
