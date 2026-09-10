# SPDX-License-Identifier: AGPL-3.0-only
"""
The half of the bridge that comes back: votes, replies and reports.

Half the room reads in Discord. A bridge that carries readings out and nothing
in makes the highest-voted list a measurement of which half of the audience
happened to be in the app — and that number is the one she picks readings from.

Every claim here is one that fails SILENTLY when it breaks: nothing errors,
the channel simply stops mattering.
"""
from __future__ import annotations

import asyncio
import inspect

from vcordbot import app, bridge, gateway


def test_reactions_do_not_need_a_privileged_intent() -> None:
    """
    ⚠ GUILD_MESSAGE_REACTIONS is not privileged; MESSAGE_CONTENT is. So votes
    from the channel work the day the bot connects, while replies wait on a
    switch in the developer portal. Losing this distinction means the whole
    inbound bridge appears blocked on something it is not.
    """
    assert gateway.GUILD_MESSAGE_REACTIONS == 1 << 10
    assert gateway.INTENTS & gateway.GUILD_MESSAGE_REACTIONS
    assert gateway.INTENTS & gateway.MESSAGE_CONTENT


def test_the_announcement_returns_the_message_id() -> None:
    """
    ⚠ Without it every reaction arrives naming a message nothing can
    attribute, and is dropped as a reaction to nothing — with no error
    anywhere.
    """
    source = inspect.getsource(bridge.announce_submission)
    assert "-> str | None" in source
    assert "post_and_tell_id" in source


def test_the_bot_reacts_first() -> None:
    """A vote that only works if you guess the right emoji is a vote nobody
    casts."""
    source = inspect.getsource(bridge.announce_submission)
    assert "add_reaction" in source


def test_only_the_vote_emoji_is_a_vote() -> None:
    seen: list[dict] = []

    async def fake(path, payload, *, site_url, secret, client=None):
        seen.append({"path": path, **payload})

    original = bridge.tell_the_site
    bridge.tell_the_site = fake
    try:
        asyncio.run(app._channel_voted(
            {"emoji": {"name": "🎉"}, "message_id": "1", "user_id": "u"}, True))
        assert seen == [], "any reaction counted as a vote"
        asyncio.run(app._channel_voted(
            {"emoji": {"name": bridge.VOTE}, "message_id": "1", "user_id": "u"},
            True))
        assert len(seen) == 1 and seen[0]["path"] == "vote"
        assert seen[0]["on"] is True
    finally:
        bridge.tell_the_site = original


def test_removing_the_reaction_takes_the_vote_back() -> None:
    seen: list[dict] = []

    async def fake(path, payload, *, site_url, secret, client=None):
        seen.append(payload)

    original = bridge.tell_the_site
    bridge.tell_the_site = fake
    try:
        asyncio.run(app._channel_voted(
            {"emoji": {"name": bridge.VOTE}, "message_id": "1", "user_id": "u"},
            False))
        assert seen and seen[0]["on"] is False
    finally:
        bridge.tell_the_site = original


def test_only_replies_become_comments() -> None:
    """
    ⚠ The channel is a channel. Sweeping every message into somebody's reading
    would fill the room with conversation that was never about it.
    """
    seen: list[dict] = []

    async def fake(path, payload, *, site_url, secret, client=None):
        seen.append(payload)

    original = bridge.tell_the_site
    bridge.tell_the_site = fake
    try:
        asyncio.run(app._channel_said(
            {"content": "just chatting", "author": {"username": "a"}}))
        assert seen == [], "a message that replies to nothing became a comment"

        asyncio.run(app._channel_said({
            "content": "the Saturn bit is the good bit",
            "author": {"username": "korax"},
            "message_reference": {"message_id": "77"},
        }))
        assert len(seen) == 1
        assert seen[0]["message_id"] == "77"
        assert seen[0]["who"] == "korax"
    finally:
        bridge.tell_the_site = original


def test_the_bots_own_reaction_is_not_a_vote() -> None:
    """It puts the star there itself; counting it would give everything one."""
    source = inspect.getsource(gateway.Reader.handle)
    assert "self.bot_user_id" in source
    assert "MESSAGE_REACTION_ADD" in source


def test_the_reader_is_actually_started() -> None:
    """
    ⚠ The failure this exists for: every piece of the inbound bridge was
    written — protocol, resume, deduplication, intent warning — and nothing
    called it. The channel could be read from and never was, and nothing
    anywhere said so.
    """
    source = inspect.getsource(app.lifespan)
    assert "gateway.Reader" in source
    assert "_reader.run()" in source or ".run()" in source
    assert "practice_channel_id" in source


def test_the_reader_reconnects_for_ever() -> None:
    """A bridge that gives up is down every time Discord has a bad ten
    minutes, and nobody notices until somebody asks where their reply went."""
    source = inspect.getsource(gateway.Reader.run)
    assert "while not self._closing" in source
    assert "backoff(" in source
