# SPDX-License-Identifier: AGPL-3.0-only
"""
Who may open a course.

The rule she asked for, and the one thing about it that is easy to get wrong:
losing a membership takes the materials and leaves the progress. These check
the shape that makes that possible rather than the wiring that carries it.
"""
from __future__ import annotations

import inspect

from shruti.core import access


def test_permission_and_progress_are_different_tables():
    """
    The whole design in one assertion.

    If progress lived on the entitlement, revoking access would delete how far
    somebody got, and "they keep their progress" would need a special case
    every time anybody wrote a revocation.
    """
    from shruti.models import Entitlement, LessonProgress

    permission = set(Entitlement.model_fields)
    progress = set(LessonProgress.model_fields)

    assert "revoked_at" in permission
    assert "completed_at" in progress
    # Neither knows anything about the other's business.
    assert not {"completed_at", "seconds_watched", "lesson_id"} & permission
    assert not {"revoked_at", "source", "tier_key"} & progress


def test_revoking_never_touches_progress():
    """
    Read the code rather than trust the intent: nothing in the module that
    revokes access mentions progress at all.
    """
    source = inspect.getsource(access)
    assert "LessonProgress" not in source
    assert "Enrolment" not in source


def test_an_entitlement_records_why_it_exists():
    """
    A purchase and a membership expire differently. One "has access" flag
    could not say which of them just ended, and somebody writing to ask why
    they lost a class deserves an answer.
    """
    from shruti.models import Entitlement

    assert "source" in Entitlement.model_fields
    assert "tier_key" in Entitlement.model_fields


def test_access_is_revoked_by_stamping_not_deleting():
    """
    A deleted row cannot answer "when did I lose this, and why". A stamped one
    can, six months later, when they write and ask.
    """
    source = inspect.getsource(access.sync_tier_entitlements)
    assert "revoked_at = now" in source
    assert "session.delete" not in source


def test_a_purchase_is_checked_before_a_membership():
    """
    Somebody who bought a class outright AND had it included with a tier they
    later cancelled must keep it. Checking the tier first would find a dead
    membership and stop, hiding a purchase they actually made.
    """
    source = inspect.getsource(access.may_open)
    bought = source.index('"purchase", "ticket", "gift"')
    tier = source.index('row.source == "tier"')
    assert bought < tier


def test_a_live_membership_is_required_not_just_an_entitlement_row():
    """
    The subscription is the truth and the entitlement is its shadow. A
    cancellation not yet swept up must not keep the door open, so the row alone
    is never enough.
    """
    source = inspect.getsource(access.may_open)
    assert "tier_keys_for" in source


def test_granting_twice_is_granting_once():
    """A repeated Stripe webhook is the ordinary case, not the exception."""
    source = inspect.getsource(access.grant)
    assert "scalar_one_or_none" in source
    assert "revoked_at = None" in source
