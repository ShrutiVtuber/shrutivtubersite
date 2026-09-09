# SPDX-License-Identifier: AGPL-3.0-only
"""
Who hears about what.

One function decides, and every place that notifies calls it with a kind. Two
call sites reading preference flags for themselves is how somebody ends up
unsubscribed on one path and not the other — and the person who notices is the
one who turned it off.

⚠ **Unconfigured must be a working state.** Without a Firebase service account
nothing is sent and nothing raises. The alternative is a site that 500s on
publishing a horoscope because a Google credential is missing, which is a
worse failure than a missed notification by a wide margin.
"""
from __future__ import annotations

import inspect

from shruti.core import fcm, notify


def test_every_kind_has_a_switch() -> None:
    for kind, (phone_flag, browser_flag) in notify.WHO.items():
        from shruti.models.devices import AppDevice

        assert hasattr(AppDevice, phone_flag), f"{kind}: no {phone_flag}"
        if browser_flag is not None:
            from shruti.models import PushSubscription

            assert hasattr(PushSubscription, browser_flag), kind


def test_a_kind_nobody_has_heard_of_is_refused() -> None:
    """
    A typo'd kind must not silently reach nobody. It reaches nobody EITHER WAY;
    the difference is whether anybody finds out.
    """
    import asyncio

    async def go():
        await notify.tell(None, "gossip", title="x", body="y", url="/")

    try:
        asyncio.run(go())
    except ValueError as exc:
        assert "gossip" in str(exc)
    else:
        raise AssertionError("an unknown kind was accepted")


def test_the_browser_is_never_opted_into_something_it_was_not_offered() -> None:
    """
    The web table predates three of these kinds and has two switches. A kind
    with no browser column reaches phones only — silently signing browsers up
    for a notice they never agreed to would be worse than not sending it.
    """
    assert notify.WHO["video"][1] is None
    assert notify.WHO["replies"][1] is None


def test_a_reply_never_goes_to_a_browser() -> None:
    """
    A web subscription is not reliably tied to an account, so "somebody replied
    to YOUR reading" sent to browsers reaches the wrong trays.
    """
    source = inspect.getsource(notify.tell)
    assert "to_user is None" in source, (
        "the browser branch no longer checks to_user — a personal notice will "
        "go to everybody's browser"
    )


def test_a_dead_token_is_deleted_rather_than_retried() -> None:
    """
    FCM rate-limits senders that keep asking about tokens it has said are gone.
    """
    source = inspect.getsource(notify.tell)
    assert "session.delete(device)" in source


def test_no_firebase_is_quiet_rather_than_broken() -> None:
    import asyncio

    assert fcm.configured() is False
    delivered, dead = asyncio.run(
        fcm.send("any-token", title="t", body="b", url="/"))
    assert delivered is False
    # ⚠ NOT dead. Saying a token is gone because WE are unconfigured would
    # delete every device row the first time somebody publishes anything.
    assert dead is False


def test_the_message_carries_both_a_notification_and_the_url() -> None:
    """
    The notification is what Android draws in the background; the data is what
    the app reads in the foreground and what carries where to go on a tap.
    """
    m = fcm.message("tok", title="She is live", body="Come and see", url="/videos")
    assert m["message"]["token"] == "tok"
    assert m["message"]["notification"]["title"] == "She is live"
    assert m["message"]["data"]["url"] == "/videos"


def test_nobody_is_notified_about_their_own_comment() -> None:
    """Being told about yourself is the fastest way to turn notifications off."""
    from shruti.api.routes import practice

    source = inspect.getsource(practice.comment)
    assert "work.user_id != user.id" in source


def test_publishing_cannot_be_failed_by_a_push_service() -> None:
    from shruti.api.routes import horoscopes

    source = inspect.getsource(horoscopes.publish)
    where = source.index("tell(")
    # The call is inside a try, and after the commit.
    assert "try:" in source[:where]
    assert source.index("await session.commit()") < where
