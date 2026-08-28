# SPDX-License-Identifier: AGPL-3.0-only
"""
A birth time is a wall clock somewhere, not an instant.

**The bug this file exists to keep out.** Seven surfaces each assembled
`f"{date}T{time}:00"` for themselves — the natal tool, the chart figure, the
print sheet, both comparison pages, the Today wheel and the synastry route —
and none of them attached an offset. The ephemeris reads a datetime with no
offset as UTC, so every chart on the site was cast for the wrong moment.

What made it survive is that it does not look like a failure. The planets move
slowly enough that all of them stay very nearly right and only the angles move:

    Athens        18°31′ Leo     should have been   11°46′ Cancer   (37° out)
    London         7°13′ Leo                        26°23′ Cancer   (11° out)
    Mumbai        27°54′ Virgo                      12°22′ Cancer   (76° out)
    Los Angeles    9°42′ Pisces                     16°43′ Cancer   (127° out)

A chart with the right Sun and the wrong rising sign is indistinguishable from
a correct one unless you already know the answer. So the assertions here are
about the SHAPE of what is sent, not about any particular chart: nothing may
leave for the ephemeris without saying which offset it is in.
"""
from __future__ import annotations

import inspect
import re

from shruti.api.routes import charts
from shruti.core.moments import birth_moment, offset_at, timezone_known
from shruti.models.accounts import SavedChart

# An ISO datetime that names its own offset, `Z` included.
HAS_OFFSET = re.compile(r"T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$")


def _chart(**over) -> SavedChart:
    base = dict(
        owner_token="owner-tz", share_token=None, user_id=None,
        label="For me", tradition="hellenistic", house_system="whole_sign",
        figure="wheel", birth_date="1996-05-14", birth_time="09:30",
        time_unknown=False, place_name="Athens, Greece",
        lat=37.9838, lon=23.7275, timezone="Europe/Athens",
    )
    base.update(over)
    return SavedChart(**base)


# ── the instant ─────────────────────────────────────────────────────────────

def test_a_moment_always_names_its_offset():
    """The one invariant. A naive string is read as UTC and is the whole bug."""
    for chart in (_chart(),
                  _chart(timezone=""),                       # never recorded
                  _chart(timezone="Nowhere/Invented"),       # unresolvable
                  _chart(time_unknown=True, birth_time=None),
                  _chart(timezone="America/Los_Angeles")):
        assert HAS_OFFSET.search(charts._moment_of(chart)), chart.timezone


def test_the_offset_is_the_one_that_applied_on_the_day():
    """
    Greece was +02:00 in the January of the same year it was +03:00 in May.
    Storing an offset instead of a zone name would get one of those wrong.
    """
    assert birth_moment("1996-05-14", "09:30", False, "Europe/Athens") \
        == "1996-05-14T09:30:00+03:00"
    assert birth_moment("1996-01-14", "09:30", False, "Europe/Athens") \
        == "1996-01-14T09:30:00+02:00"


def test_the_offset_is_the_birthplaces_not_the_readers():
    """Same wall clock, four birthplaces, four different instants."""
    moments = {tz: birth_moment("1996-05-14", "09:30", False, tz)
               for tz in ("Europe/Athens", "Europe/London",
                          "America/Los_Angeles", "Asia/Kolkata")}
    assert len(set(moments.values())) == 4, moments


def test_an_unknown_time_is_noon_in_the_birthplace_not_noon_utc():
    """
    Noon is the least-wrong instant for the planets. Noon UTC is not noon
    anywhere in particular, which defeats the point of choosing it.
    """
    assert birth_moment("1996-05-14", None, True, "America/Los_Angeles") \
        == "1996-05-14T12:00:00-07:00"


def test_an_unrecorded_zone_says_utc_out_loud():
    """
    The same instant a naive string produced — but stated, so a page can see
    it and warn instead of drawing a confident wheel for the wrong sky.
    """
    assert birth_moment("1996-05-14", "09:30", False, "") \
        == "1996-05-14T09:30:00+00:00"
    assert not timezone_known("")


# ── the clock oddities ──────────────────────────────────────────────────────

def test_an_hour_the_clock_skipped_is_reported():
    """
    02:30 on the morning the clock goes forward never happened. Somebody whose
    certificate says it should be told, not silently moved.
    """
    assert offset_at("America/Los_Angeles", "1996-04-07T02:30").imaginary


def test_an_hour_the_clock_lived_twice_is_reported():
    assert offset_at("America/Los_Angeles", "1996-10-27T01:30").ambiguous


def test_a_gap_is_not_mistaken_for_a_fold():
    """
    Both make the two `fold` readings disagree, so that test alone once
    labelled a skipped London hour as one that occurred twice.
    """
    gap = offset_at("Europe/London", "1981-03-29T01:30")
    assert gap.imaginary and not gap.ambiguous


def test_an_ordinary_hour_reports_nothing():
    quiet = offset_at("Europe/Athens", "1996-05-14T09:30")
    assert not quiet.imaginary and not quiet.ambiguous and quiet.note == ""


# ── nobody assembles their own ──────────────────────────────────────────────

def _code_of(module) -> str:
    """
    A module's source with docstrings and comments stripped.

    Needed because the assertion below is "this file must not contain X" and
    the file's own comments explain X at length. Grepping raw source would
    match the explanation of the bug and report it as the bug — a mistake this
    project has now made often enough to have a helper for it.
    """
    import ast

    tree = ast.parse(inspect.getsource(module))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and ast.get_docstring(node):
            node.body = node.body[1:]
    return ast.unparse(tree)          # `unparse` drops comments entirely


def test_no_route_builds_a_moment_by_hand():
    """
    The failure mode was seven copies of one string, so the test is against
    the copying rather than against any one of them.
    """
    source = _code_of(charts)
    assert "T{clock}" not in source
    assert "birth_date}T" not in source
    assert source.count("_moment_of") >= 5


def test_every_view_hands_over_a_resolved_instant():
    """
    A page given a date and a time will assemble one itself, and the one it
    assembles will be naive. So the views hand over the finished instant.
    """
    chart = _chart()
    for view in (charts._owner_view(chart), charts._shared_view(chart)):
        assert HAS_OFFSET.search(view["when"])
    assert charts._owner_view(chart)["timezoneKnown"] is True
    assert charts._owner_view(_chart(timezone=""))["timezoneKnown"] is False


def test_the_shared_view_still_does_not_spell_out_the_place():
    """
    `when` carries the birth date and time, exactly as `birthDate` always did.
    It must not have brought the place along with it.
    """
    shared = charts._shared_view(_chart())
    assert "placeName" not in shared and "timezone" not in shared
    assert "lat" in shared          # needed to cast, and always was


def test_keeping_a_chart_accepts_the_zone():
    """A body that cannot carry it means a row that cannot be re-cast."""
    assert "timezone" in charts.Keep.model_fields
    assert "timezone" in charts.InviteIn.model_fields


def test_synastry_sends_both_sides_with_offsets():
    """
    Two people in different countries were each cast as though their birth
    time were UTC — wrong twice, and by a different amount on each side.
    """
    source = inspect.getsource(charts._cross)
    assert "_moment_of(left)" in source and "_moment_of(right)" in source
