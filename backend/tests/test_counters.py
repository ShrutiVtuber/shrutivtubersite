# SPDX-License-Identifier: AGPL-3.0-only
"""
Counting, and the three ways a stored total goes wrong.

The design decision under test is that a counter holds no running total. Each
test below is a failure that a stored total would have, and a sum does not.
"""
from __future__ import annotations

import inspect
import re

from shruti.core import counters


def _code(fn) -> str:
    """Source with the prose removed — a docstring here names what it forbids."""
    import ast, textwrap
    tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)) and ast.get_docstring(node):
            node.body = node.body[1:]
    return ast.unparse(tree)


def test_a_retried_delivery_cannot_count_twice() -> None:
    """
    Stripe retries webhooks and Twitch retries EventSub deliveries, both by
    design. Without idempotency a goal bar drifts upward on every retry — a
    wrong that looks like generosity and goes unnoticed for a long time.
    """
    src = _code(counters.record)
    assert "on_conflict_do_nothing" in src
    assert "external_id" in src


def test_idempotency_is_not_a_check_then_insert() -> None:
    """
    Two deliveries can arrive at once. A select followed by an insert has a
    race between them wide enough for a duplicate, which is why the uniqueness
    is the database's job and not the application's.
    """
    src = _code(counters.record)
    assert "select" not in src.lower(), "the database decides, not a prior read"


def test_no_running_total_is_stored_anywhere() -> None:
    """
    The whole design. A counter created today must count what already happened
    rather than starting at nought, and changing its sources must need no
    migration.
    """
    from shruti.models import Counter
    fields = set(Counter.model_fields)
    for forbidden in ("current", "total", "raised", "progress", "amount"):
        assert forbidden not in fields, (
            f"Counter.{forbidden} would be a stored total — the thing this "
            f"design exists to avoid")


def test_an_unknown_source_is_refused_rather_than_counted_as_nothing() -> None:
    """
    A typo in a sources string should be visible. Silently contributing zero is
    the failure that gets found weeks later when a goal will not move.
    """
    src = _code(counters.record)
    assert "SOURCES" in src


def test_messages_are_never_approved_on_arrival() -> None:
    """
    A stranger's words reaching a live stream without anybody reading them is
    the hazard this site will not take.
    """
    src = _code(counters.record)
    assert "message_approved=False" in src


def test_money_and_counts_are_not_added_together_by_accident() -> None:
    """
    Bits are not euros and people are not euros. Which number a source
    contributes is decided by one table rather than at each call site.
    """
    assert "twitch.bits" not in counters.MONEY_SOURCES
    assert "course.signup" not in counters.MONEY_SOURCES
    assert "stripe.support" in counters.MONEY_SOURCES
    assert "youtube.superchat" in counters.MONEY_SOURCES


def test_every_money_source_is_a_known_source() -> None:
    assert counters.MONEY_SOURCES <= set(counters.SOURCES)


def test_every_event_gets_an_identity() -> None:
    """
    Not a nicety — it is what lets the unique index be a plain one.

    The index began partial (`unique ... where external_id <> ''`) so manual
    events could repeat. Postgres only uses a partial index for ON CONFLICT if
    the statement repeats the predicate exactly, and SQLAlchemy emits that
    predicate as a bound parameter, which never matches a literal one. The
    result was not a missed dedupe — **every insert failed outright.**
    """
    src = _code(counters.record)
    assert "secrets.token_hex" in src, "an event with no platform id still needs one"


def test_the_unique_index_is_not_partial() -> None:
    """
    The bug above, guarded at its source. Source-reading tests could not catch
    it — the earlier idempotency test passed while every insert was failing —
    so this checks the migration that defines the constraint instead.
    """
    from pathlib import Path as _P
    here = _P(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        for candidate in (base / "alembic" / "versions", base / "backend" / "alembic" / "versions"):
            if candidate.is_dir():
                text = (candidate / "f31c8a06d92e_counters_and_support_events.py").read_text()
                assert "ux_support_event_source_external" in text
                # The index creating the uniqueness must carry no predicate.
                block = text.split("ux_support_event_source_external")[1].split(")")[0]
                assert "postgresql_where" not in block
                return
    raise AssertionError("could not find the migration")
