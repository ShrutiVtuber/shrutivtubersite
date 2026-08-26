# SPDX-License-Identifier: AGPL-3.0-only
"""
Two charts read against each other, and the reading somebody wrote.

The arithmetic is the easy half. What matters here is what happens around it:
whose data is exposed to whom, what survives a deletion, and whether an unknown
birth time is honoured or papered over.
"""
from __future__ import annotations

import inspect
from pathlib import Path

from shruti.api.routes import charts
from shruti.models.accounts import Comparison, SavedChart


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()


# ── what a comparison is made of ────────────────────────────────────────────

def test_a_comparison_references_charts_rather_than_copying_them():
    """
    A copy of the birth data would survive the chart being deleted, which is
    exactly the thing somebody asking to be forgotten is asking not to happen.
    """
    fields = set(Comparison.model_fields)
    assert {"left_id", "right_id"} <= fields
    for leaked in ("birth_date", "birth_time", "lat", "lon", "place_name"):
        assert leaked not in fields, f"a comparison holds its own {leaked}"


def test_deleting_a_chart_takes_its_comparisons_with_it():
    """Enforced by the database, not by a route remembering to tidy up."""
    import shruti

    root = Path(shruti.__file__).resolve().parent.parent
    migration = (root / "alembic" / "versions" / "c5e83a71d92f_comparisons.py").read_text()
    assert migration.count('ondelete="CASCADE"') == 2


def test_the_reading_lives_on_the_comparison():
    """It is the thing a person actually makes here."""
    assert "reading_md" in Comparison.model_fields


# ── who sees what ───────────────────────────────────────────────────────────

def test_a_shared_comparison_withholds_both_place_names():
    """
    Two people's data, and only one of them pressed share. The place name is
    the one part of a nativity no reader can recover from the figure.
    """
    source = inspect.getsource(charts._comparison_view)
    assert "if owner:" in source
    assert 'out["placeName"]' in source


def test_a_shared_comparison_never_hands_over_the_owner_token():
    source = inspect.getsource(charts._comparison_view)
    assert '"shareToken": row.share_token if owner else None' in source


def test_the_owner_is_warned_before_sharing_two_peoples_charts():
    page = (SRC / "pages" / "chart" / "compare" / "[token].astro").read_text()
    assert "including the one that is not yours" in page, (
        "sharing a comparison exposes somebody who did not press the button, "
        "and the page has to say so before the link is made"
    )


# ── the token that makes it social ──────────────────────────────────────────

def test_a_share_token_can_be_compared_against():
    """
    Comparing what somebody sent you is the point of the feature, and they
    handed you a SHARE token. It must work as one side of a comparison without
    becoming an owner token anywhere.
    """
    source = inspect.getsource(charts._chart_by_any)
    assert "SavedChart.owner_token" in source and "SavedChart.share_token" in source
    # And it is used only where a comparison is built.
    assert "_chart_by_any" in inspect.getsource(charts.compare)
    assert "_chart_by_any" not in inspect.getsource(charts.open_mine)
    assert "_chart_by_any" not in inspect.getsource(charts.forget)


def test_comparing_a_chart_with_itself_is_refused():
    assert "same chart twice" in inspect.getsource(charts.compare)


def test_a_deleted_side_reports_gone_rather_than_half_a_reading():
    source = inspect.getsource(charts._load_comparison)
    assert "410" in source


# ── the astrology ───────────────────────────────────────────────────────────

def test_only_cross_chart_configurations_are_returned():
    """
    Including each chart's own internal aspects would bury the twenty lines
    somebody came for under ninety they can get from the natal pages.
    """
    table = (SRC / "components" / "chart" / "SynastryTable.astro").read_text()
    assert "Only cross-chart configurations" in table


def test_both_readings_are_offered_without_picking_one():
    """
    Whole-sign says whether a configuration exists; degrees say how close it
    is. The tradition does not agree with itself about which is primary, so
    neither is presented as the correct one.
    """
    table = (SRC / "components" / "chart" / "SynastryTable.astro").read_text()
    assert "By degree" in table and "By sign" in table
    assert "does not agree with itself" in table


def test_an_unknown_birth_time_withholds_the_angles():
    """
    Four minutes is a degree of ascendant. A synastry built on an invented one
    is worse than none, because it reads exactly as authoritatively.
    """
    table = (SRC / "components" / "chart" / "SynastryTable.astro").read_text()
    assert "withheld" in table and "assumed noon" in table


# ── consent, as everywhere birth data is kept ───────────────────────────────

def test_keeping_a_comparison_without_an_account_needs_consent():
    source = inspect.getsource(charts.compare)
    assert "body.consent" in source
    assert "expires_at" in source
