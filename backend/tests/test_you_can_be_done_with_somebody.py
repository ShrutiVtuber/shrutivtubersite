# SPDX-License-Identifier: AGPL-3.0-only
"""
Blocking a person in the practice room.

⚠ **This is an App Store requirement, not a feature request.** Apple's
guideline 1.2 says an app carrying other people's writing must offer a way to
filter objectionable material, a way to report it, published contact details,
AND the ability to block an abusive user. The room already had the first
three — reports with reasons, an automatic hide once a few people agree, her
address at the foot of every page. This was the fourth, and it is the kind of
gap found by a reviewer rather than by a test suite, which is why there is now
a test suite for it.

⚠ **A block is not a strike.** Nobody is told, nothing is hidden from anybody
else, she is not notified. It is one reader's decision about their own room,
which is exactly why it belongs beside the report queue rather than inside it.

Source-level guards, as everywhere in this suite: the runtime behaviour was
checked against the running stack, and these hold the shape of it in place.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

from shruti.api.routes import practice
from shruti.models.practice import PracticeBlock


def code_of(function) -> str:
    """
    A function's source with its comments and docstring removed.

    ⚠ Not fussiness. A guard that greps for a token finds it in the paragraph
    explaining why the token is there — so the code can be deleted, the prose
    stays, and the test goes on passing. That has happened here more than once.
    """
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


SOURCE = inspect.getsource(practice)


def test_the_block_routes_come_before_the_catch_all() -> None:
    """
    ⚠ FastAPI matches in definition order.

    `/blocks` declared after `/{work_id}` is read as a work whose id is the
    word "blocks" — a 422 about integer parsing, which names nothing that would
    lead anybody to this file. The room has been bitten by exactly this before.
    """
    blocks = SOURCE.index('@router.get("/blocks")')
    catch_all = SOURCE.index('@router.get("/{work_id}")')
    assert blocks < catch_all, (
        "the /blocks routes are below the /{work_id} catch-all and will never "
        "be reached"
    )


def test_the_feed_hides_the_writing_of_a_blocked_person() -> None:
    body = code_of(practice.feed)
    assert "_hidden_from" in body, "the feed does not ask who is blocked"
    assert "not_in" in body, "the feed asks, and then does nothing with it"
    # ⚠ Before the limit. Filtering a page of thirty down to twenty-six gives
    # somebody who has blocked people a shorter feed with a gap in it.
    assert body.index("not_in") < body.index(".limit("), (
        "the block filter is applied after the limit, which shortens the feed"
    )


def test_a_blocked_persons_work_is_not_there_at_all() -> None:
    body = code_of(practice.one)
    assert "_hidden_from" in body
    assert "404" in body, "a blocked author's work must answer like any other"
    assert "403" not in body, (
        "403 tells somebody they are blocked, and by whom"
    )


def test_their_comments_go_too() -> None:
    """
    ⚠ Hiding the work but not the comments would be the worse half.

    Somebody you have blocked turning up under everybody else's writing is the
    case the button is actually pressed for.
    """
    body = code_of(practice.one)
    assert "if c.user_id not in hidden" in body, (
        "comments are not filtered by the block list"
    )


def test_a_bridged_comment_cannot_be_blocked_and_is_not_pretended_otherwise() -> None:
    """
    ⚠ A Discord comment has no site account behind it.

    `user_id` is None, so it is never in the block set — which is correct, and
    is a limit that has to be said rather than left to look like a bug.
    """
    assert "from_discord" in SOURCE
    where = SOURCE.index("if c.user_id not in hidden")
    nearby = SOURCE[where - 600:where]
    assert "bridged" in nearby and "no site account" in nearby, (
        "nothing near the filter explains that a bridged comment has no "
        "account to block"
    )


def test_a_blocked_person_cannot_answer_you() -> None:
    """⚠ Both directions. One alone leaves them still able to reach you."""
    body = code_of(practice.comment)
    assert "_blocked_by" in body, "a blocked person can still comment"
    assert "404" in body


def test_you_cannot_block_yourself() -> None:
    body = code_of(practice.block)
    assert "user.id" in body and "400" in body


def test_blocking_twice_is_not_an_error() -> None:
    """
    ⚠ The button is pressed from a list that may be seconds stale.

    "That failed" for something already true teaches people to press again.
    """
    body = code_of(practice.block)
    assert "IntegrityError" in body, "a second block raises instead of passing"
    assert "rollback" in body


def test_the_pair_is_unique_in_the_database() -> None:
    """
    Without this, a second press adds a duplicate row that one unblock does
    not fully undo — the person stays hidden and nothing explains why.
    """
    versions = Path(__file__).resolve().parents[1] / "alembic" / "versions"
    migration = next(versions.glob("*blocking_a_person.py")).read_text()
    assert "uq_practice_block_pair" in migration
    assert '["user_id", "blocked_id"]' in migration


def test_there_is_a_way_back() -> None:
    """A block nobody can undo is a mistake somebody has to live with."""
    assert hasattr(practice, "unblock")
    assert hasattr(practice, "my_blocks")


def test_a_comment_says_who_wrote_it() -> None:
    """
    ⚠ Without an id the app can name a commenter and do nothing about them.

    Null is the bridged case and is the app's signal that there is no account
    behind the name.
    """
    body = code_of(practice.one)
    assert '"authorId": c.user_id' in body


def test_the_model_indexes_both_directions() -> None:
    """
    Both are asked on hot paths: "whose writing do I hide" on every read, and
    "has this author blocked me" before every comment.
    """
    fields = PracticeBlock.model_fields
    assert fields["user_id"].index is True
    assert fields["blocked_id"].index is True
