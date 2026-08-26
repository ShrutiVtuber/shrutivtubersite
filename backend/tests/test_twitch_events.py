# SPDX-License-Identifier: AGPL-3.0-only
"""
Twitch deliveries: proving they are real, and not counting gifts twice.

The endpoint is public and moves a goal bar, so the signature check is tested
with a real HMAC rather than by reading the code.
"""
from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone

from shruti.core.twitch_events import to_event, verify

SECRET = "a-secret-of-some-length"


def signed(body: bytes, *, secret=SECRET, when=None, message_id="abc-123"):
    stamp = (when or datetime.now(timezone.utc)).isoformat().replace("+00:00", "Z")
    sig = "sha256=" + hmac.new(secret.encode(), (message_id + stamp).encode() + body,
                               hashlib.sha256).hexdigest()
    return {"Twitch-Eventsub-Message-Id": message_id,
            "Twitch-Eventsub-Message-Timestamp": stamp,
            "Twitch-Eventsub-Message-Signature": sig}


def test_a_real_delivery_is_accepted() -> None:
    body = b'{"hello":"world"}'
    assert verify(SECRET, signed(body), body) is True


def test_a_tampered_body_is_refused() -> None:
    """The attack: a genuine signature reused over different content."""
    headers = signed(b'{"bits":100}')
    assert verify(SECRET, headers, b'{"bits":100000}') is False


def test_the_wrong_secret_is_refused() -> None:
    body = b"{}"
    assert verify(SECRET, signed(body, secret="not-the-secret"), body) is False


def test_an_old_delivery_is_refused_even_when_correctly_signed() -> None:
    """
    A signature does not expire on its own, so a delivery captured once could
    otherwise be replayed forever — moving a goal bar every time.
    """
    body = b"{}"
    old = datetime.now(timezone.utc) - timedelta(hours=2)
    assert verify(SECRET, signed(body, when=old), body) is False


def test_missing_headers_are_refused() -> None:
    assert verify(SECRET, {}, b"{}") is False


def test_the_comparison_is_constant_time() -> None:
    """A plain `==` returns early and leaks how much of a guess was right."""
    import ast, inspect, textwrap
    from shruti.core import twitch_events
    tree = ast.parse(textwrap.dedent(inspect.getsource(twitch_events.verify)))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and ast.get_docstring(node):
            node.body = node.body[1:]
    assert "compare_digest" in ast.unparse(tree)


# ── mapping ────────────────────────────────────────────────────────────────

def test_a_gifted_subscription_is_not_counted_twice() -> None:
    """
    A gift produces TWO deliveries: the recipient's `channel.subscribe` with
    `is_gift`, and the giver's `channel.subscription.gift`. Counting both
    doubles every gift bomb, and it looks like generosity rather than a bug.
    """
    assert to_event("channel.subscribe", {"is_gift": True, "user_name": "them"}) is None
    given = to_event("channel.subscription.gift", {"total": 5, "user_name": "her"})
    assert given["quantity"] == 5


def test_an_ordinary_subscription_counts_once() -> None:
    e = to_event("channel.subscribe", {"is_gift": False, "user_name": "them"})
    assert e["source"] == "twitch.sub" and e["quantity"] == 1


def test_bits_are_counted_as_bits_not_money() -> None:
    e = to_event("channel.cheer", {"bits": 1000, "user_name": "them"})
    assert e["source"] == "twitch.bits" and e["quantity"] == 1000


def test_an_anonymous_gift_has_a_name() -> None:
    """Twitch permits it, and a blank where a name goes looks broken."""
    e = to_event("channel.subscription.gift", {"total": 1, "is_anonymous": True})
    assert e["who"] == "Anonymous"


def test_an_anonymous_cheer_has_a_name() -> None:
    e = to_event("channel.cheer", {"bits": 100, "is_anonymous": True})
    assert e["who"] == "Anonymous"


def test_a_raid_carries_its_viewers() -> None:
    e = to_event("channel.raid", {"viewers": 42, "from_broadcaster_user_name": "them"})
    assert e["source"] == "twitch.raid" and e["quantity"] == 42


def test_a_resub_keeps_its_months_and_its_message() -> None:
    e = to_event("channel.subscription.message",
                 {"cumulative_months": 7, "user_name": "them",
                  "message": {"text": "still here"}})
    assert e["extra"]["months"] == 7
    assert e["message"] == "still here"


def test_an_unknown_kind_is_ignored_rather_than_guessed() -> None:
    assert to_event("channel.something.new", {"user_name": "them"}) is None
