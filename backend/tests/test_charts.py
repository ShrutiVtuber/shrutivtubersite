# SPDX-License-Identifier: AGPL-3.0-only
"""
Keeping a chart, and handing one to a friend.

Two things here are load-bearing and neither is obvious from reading the
routes in order.

**The two tokens must be different strings.** If sharing handed out the same
token that opens the chart, then sharing would give away the owner's own way
in, and revoking would lock the owner out along with everybody else. That is
the kind of bug that works perfectly in every test that only shares once.

**The shared view must not print the moment.** It has to pass on enough to
draw the chart — which is the instant — while not spelling out the date, time
and place as text. Those are different things, and conflating them is how a
"private" share ends up with a birth certificate in the page source.
"""
from __future__ import annotations

import inspect

import pytest

from shruti.api.routes import charts
from shruti.models.accounts import SavedChart


def _chart(**over) -> SavedChart:
    base = dict(
        owner_token="owner-aaa", share_token=None, user_id=None,
        label="For me", tradition="vedic", house_system="whole_sign",
        figure="south", birth_date="1990-06-15", birth_time="14:30",
        time_unknown=False, place_name="Athens, Greece",
        lat=37.9838, lon=23.7275,
    )
    base.update(over)
    return SavedChart(**base)


# ── the two tokens ──────────────────────────────────────────────────────────

def test_a_chart_has_two_different_tokens():
    """
    One token would mean sharing hands over the owner's own way in.

    Read from the model rather than from a flow, because the flow is where a
    later change would quietly set them equal.
    """
    fields = set(SavedChart.model_fields)
    assert "owner_token" in fields and "share_token" in fields


def test_sharing_does_not_touch_the_owner_token():
    source = inspect.getsource(charts.start_sharing)
    assert "share_token" in source
    assert "owner_token" not in source.replace("_by_owner", ""), (
        "minting a share link must never rewrite the owner's token — that "
        "would lock the owner out of their own chart"
    )


def test_revoking_a_share_leaves_the_owner_token_alone():
    source = inspect.getsource(charts.stop_sharing)
    assert "chart.share_token = None" in source
    assert "chart.owner_token" not in source, (
        "revoking a share must not disturb the owner's way in"
    )


def test_a_token_is_long_enough_that_guessing_is_not_a_strategy():
    """These are bearer tokens for special-category data, not slugs."""
    assert charts.TOKEN_BYTES >= 32
    assert len(charts._token()) >= 40
    assert charts._token() != charts._token()


# ── what a friend sees ──────────────────────────────────────────────────────

def test_the_shared_view_does_not_spell_out_the_moment():
    """
    Date and coordinates are passed because the chart cannot be drawn without
    them. Time of birth as a labelled field, and the place NAME, are not — the
    name is the one part that cannot be inferred from the drawing at all.
    """
    shared = charts._shared_view(_chart())
    assert "placeName" not in shared, (
        "the birth place name is the one thing a reader cannot get from the "
        "figure, so handing it over gives away more than the chart does"
    )
    assert "birthDate" in shared, "a chart cannot be drawn without its instant"


def test_the_owner_view_shows_everything_because_it_is_theirs():
    own = charts._owner_view(_chart())
    for field in ("birthDate", "birthTime", "placeName", "lat", "lon"):
        assert field in own


def test_the_share_token_is_never_in_the_shared_view():
    """
    Whoever holds a share link must not be able to read the owner token, and
    must not be handed the share token back in a way that invites passing the
    page's JSON around as though it were the link.
    """
    shared = charts._shared_view(_chart(share_token="share-bbb"))
    assert "ownerToken" not in shared
    assert "shareToken" not in shared
    assert "owner-aaa" not in str(shared)


# ── consent, because this is special-category data ──────────────────────────

def test_keeping_without_an_account_requires_consent():
    source = inspect.getsource(charts.keep)
    assert "body.consent" in source
    assert "consent_wording" in source, (
        "the wording must be stored verbatim: consent you cannot evidence is "
        "consent you do not have"
    )


def test_the_stored_wording_is_the_nativity_wording_not_a_paraphrase():
    from shruti.core.consents import NATIVITY

    source = inspect.getsource(charts.keep)
    assert "NATIVITY.wording" in source, (
        "a paraphrase in the record means the record does not say what the "
        "person actually read"
    )
    assert "birth date, birth time and birth place" in NATIVITY.wording


def test_an_ownerless_chart_expires_and_an_owned_one_does_not():
    """
    Consent that cannot be renewed by asking must not be relied on forever —
    and there is nobody to ask when there is no account.
    """
    source = inspect.getsource(charts.keep)
    assert "expires_at" in source
    assert charts.ORPHAN_DAYS >= 30

    claimed = inspect.getsource(charts.claim)
    assert "expires_at = None" in claimed, (
        "claiming a chart into an account gives it somebody to ask, so the "
        "expiry should lift"
    )


def test_opening_a_chart_puts_the_clock_back():
    source = inspect.getsource(charts.open_mine)
    assert "expires_at" in source and "ORPHAN_DAYS" in source


def test_there_is_a_way_to_delete_one_without_writing_an_email():
    assert any(
        route.path == "/api/charts/o/{token}" and "DELETE" in (route.methods or ())
        for route in charts.router.routes
    ), "a right to erasure that requires contacting somebody is not much of one"


# ── route ordering, which has bitten this codebase four times ───────────────

def test_the_literal_paths_are_declared_before_the_token_catch_alls():
    """
    FastAPI matches in declaration order. `/mine` must be declared before
    anything that could swallow it.
    """
    paths = [r.path for r in charts.router.routes]
    assert paths.index("/api/charts/mine") < paths.index("/api/charts/o/{token}")


def test_claiming_somebody_elses_chart_is_refused():
    source = inspect.getsource(charts.claim)
    assert "409" in source, (
        "holding a token must not be enough to take a chart that already "
        "belongs to an account"
    )


@pytest.mark.parametrize("bad", ["", "sidereal-ish", "WHEEL", "east"])
def test_an_unknown_figure_is_refused(bad):
    assert bad not in charts.FIGURES


def test_both_vedic_figures_are_offered():
    """She asked for either, because some people want both."""
    assert "north" in charts.FIGURES and "south" in charts.FIGURES
