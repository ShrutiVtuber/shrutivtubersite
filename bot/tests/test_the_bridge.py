# SPDX-License-Identifier: AGPL-3.0-only
"""
The practice bridge, both directions.

Her decision: "truly seamless — someone types normally in Discord and it appears
in the app; somebody posts in the app and it appears in Discord."

The gateway state machine is tested without a socket, because the socket is the
uninteresting part and the protocol is where this goes wrong: a resume that
loses its place, a message relayed twice, the bot's own announcement coming back
in as a comment on itself.

⚠ The one failure that cannot be tested from here is the privileged intent being
off. Discord then sends every message with empty content — no error, nothing in
a log, just a channel that looks quiet. So the reader COUNTS blanks and says so,
and that counting is tested.
"""
from __future__ import annotations

import asyncio

from vcordbot import bridge
from vcordbot.gateway import (
    DISPATCH, HEARTBEAT, HELLO, IDENTIFY, INVALID_SESSION, MESSAGE_CONTENT,
    RESUME, Reader, backoff, identify_payload, is_ours,
)


def _reader(seen: list) -> Reader:
    async def on_message(message):
        seen.append(message)

    r = Reader("tok", channel_id="99", on_message=on_message)
    r.bot_user_id = "me"
    return r


def _drive(reader: Reader, frames: list[dict]) -> list[dict]:
    """Feed frames in, collect what the reader sends back."""
    sent: list[dict] = []

    async def send(payload):
        sent.append(payload)

    async def go():
        for f in frames:
            await reader.handle(f, send)

    asyncio.run(go())
    return sent


# ── the socket's half ───────────────────────────────────────────────────────

def test_hello_is_answered_with_identify() -> None:
    sent = _drive(_reader([]), [{"op": HELLO, "d": {"heartbeat_interval": 41250}}])
    assert sent[0]["op"] == IDENTIFY
    assert sent[0]["d"]["token"] == "tok"


def test_identify_asks_for_message_content() -> None:
    """
    Without it Discord sends every message empty. Asking for GUILD_MESSAGES
    alone gets a stream of blanks that reads exactly like a quiet channel.
    """
    assert identify_payload("t")["d"]["intents"] & MESSAGE_CONTENT


def test_a_reconnect_resumes_where_it_left_off() -> None:
    reader = _reader([])
    sent = _drive(reader, [
        {"op": HELLO, "d": {"heartbeat_interval": 41250}},
        {"op": DISPATCH, "t": "READY", "s": 1,
         "d": {"session_id": "abc", "resume_gateway_url": "wss://x",
               "user": {"id": "me"}}},
        {"op": DISPATCH, "t": "MESSAGE_CREATE", "s": 7,
         "d": {"id": "1", "channel_id": "99", "author": {"id": "you"},
               "content": "hello"}},
        # The socket dropped and came back.
        {"op": HELLO, "d": {"heartbeat_interval": 41250}},
    ])
    assert sent[-1]["op"] == RESUME
    assert sent[-1]["d"]["session_id"] == "abc"
    assert sent[-1]["d"]["seq"] == 7, "resumed from the wrong place"


def test_an_unresumable_session_is_thrown_away() -> None:
    """
    Keeping the session id after `d: false` loops forever on the same refusal.
    """
    reader = _reader([])
    _drive(reader, [
        {"op": DISPATCH, "t": "READY", "s": 1,
         "d": {"session_id": "abc", "resume_gateway_url": "wss://x",
               "user": {"id": "me"}}},
        {"op": INVALID_SESSION, "d": False},
    ])
    assert reader.session.can_resume() is False

    reader2 = _reader([])
    _drive(reader2, [
        {"op": DISPATCH, "t": "READY", "s": 1,
         "d": {"session_id": "abc", "resume_gateway_url": "wss://x",
               "user": {"id": "me"}}},
        {"op": INVALID_SESSION, "d": True},
    ])
    assert reader2.session.can_resume() is True


def test_a_heartbeat_request_is_answered_at_once() -> None:
    sent = _drive(_reader([]), [{"op": HEARTBEAT}])
    assert sent == [{"op": HEARTBEAT, "d": None}]


def test_the_backoff_grows_and_is_jittered() -> None:
    assert backoff(0) < backoff(8)
    assert backoff(50) <= 60
    # Two bots must not reconnect on the same tick.
    assert len({round(backoff(5), 6) for _ in range(20)}) > 1


# ── which messages cross ────────────────────────────────────────────────────

def test_the_bots_own_message_never_comes_back_in() -> None:
    """
    The loop that would otherwise announce a submission, read its own
    announcement as a comment, and announce that.
    """
    assert is_ours({"channel_id": "99", "author": {"id": "me"}},
                   channel_id="99", bot_user_id="me") is False


def test_other_bots_are_ignored_too() -> None:
    assert is_ours({"channel_id": "99", "author": {"id": "x", "bot": True}},
                   channel_id="99", bot_user_id="me") is False


def test_another_channel_is_not_the_practice_channel() -> None:
    assert is_ours({"channel_id": "12", "author": {"id": "you"}},
                   channel_id="99", bot_user_id="me") is False


def test_a_redelivered_message_is_not_relayed_twice() -> None:
    """Discord redelivers on resume. Without this, one message is two comments."""
    seen: list = []
    reader = _reader(seen)
    frame = {"op": DISPATCH, "t": "MESSAGE_CREATE", "s": 2,
             "d": {"id": "same", "channel_id": "99",
                   "author": {"id": "you"}, "content": "once"}}
    _drive(reader, [frame, frame, frame])
    assert len(seen) == 1


def test_blank_messages_are_counted_and_explained() -> None:
    """
    The privileged intent being off looks exactly like a quiet channel. Ten
    blanks and nothing read is not a coincidence, and the log says so.
    """
    reader = _reader([])
    blanks = [
        {"op": DISPATCH, "t": "MESSAGE_CREATE", "s": i,
         "d": {"id": str(i), "channel_id": "99",
               "author": {"id": "you"}, "content": ""}}
        for i in range(12)
    ]
    _drive(reader, blanks)
    assert reader.session.blank_messages == 12
    assert reader.session.read_messages == 0
    assert reader.session.warned_about_intent is True


def test_a_real_message_stops_it_looking_like_the_intent() -> None:
    reader = _reader([])
    _drive(reader, [
        {"op": DISPATCH, "t": "MESSAGE_CREATE", "s": 1,
         "d": {"id": "a", "channel_id": "99", "author": {"id": "you"},
               "content": "words"}},
        *[{"op": DISPATCH, "t": "MESSAGE_CREATE", "s": i,
           "d": {"id": f"b{i}", "channel_id": "99",
                 "author": {"id": "you"}, "content": ""}} for i in range(12)],
    ])
    assert reader.session.warned_about_intent is False


# ── the app's half ──────────────────────────────────────────────────────────

def test_a_submission_reads_as_itself_in_the_channel() -> None:
    _, embed = bridge.submission_message(
        {"id": 7, "author": "Alex", "title": "Week of 7 September",
         "signs": ["aries", "leo"], "opening": "Aries: finish something."},
        "https://shrutivtuber.com")
    assert embed["title"] == "Week of 7 September"
    assert "Alex" in embed["footer"]["text"]
    assert "2 signs" in embed["footer"]["text"]
    assert embed["url"].endswith("/practice/7")


def test_a_single_reading_names_its_sign() -> None:
    _, embed = bridge.submission_message(
        {"id": 1, "author": "Blair", "title": "", "signs": ["virgo"],
         "opening": "Virgo: ..."}, "https://x")
    assert "Virgo" in embed["footer"]["text"]
    assert embed["title"] == "Virgo"


def test_a_long_opening_is_cut_at_a_word() -> None:
    long = " ".join(["word"] * 500)
    _, embed = bridge.submission_message(
        {"id": 1, "author": "A", "signs": ["leo"], "opening": long}, "https://x")
    assert len(embed["description"]) <= bridge.OPENING + 2
    assert embed["description"].endswith("…")
    assert "wor…" not in embed["description"], "cut mid-word"


def test_discord_being_down_does_not_fail_a_submission() -> None:
    """
    They wrote it and it is saved. Losing the announcement is a small thing;
    losing the work is not.
    """
    async def go():
        return await bridge.announce_submission(
            {"id": 1, "author": "A", "signs": ["leo"], "opening": "x"},
            channel_id="", token="", site_url="https://x")

    # ⚠ None, not False. The announcement now returns the MESSAGE ID, because
    # every vote and reply coming back from the channel names a message and
    # needs something to be matched against. The claim under test is unchanged:
    # a failure here is quiet and the submission is already saved.
    assert asyncio.run(go()) is None
