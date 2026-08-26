# SPDX-License-Identifier: AGPL-3.0-only
"""
The "are we compatible" reading, and the card it travels as.

This is the feature most likely to be screenshotted and posted, which makes it
the one most likely to embarrass her if it overclaims. Every test here is about
the line between *reporting a tradition* and *making a prediction*.
"""
from __future__ import annotations

import inspect
from pathlib import Path

from shruti.core import sharecard, synastry


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()

# Written as bytes rather than as escapes in a string, so no quoting layer
# between here and the file can quietly turn them into text.
PNG_MAGIC = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
TTF_MAGIC = (bytes([0x00, 0x01, 0x00, 0x00]), b"true", b"OTTO")


# ── never a score ───────────────────────────────────────────────────────────

def test_there_is_no_percentage_anywhere():
    """
    A percentage looks like a measurement of a relationship. It compresses a
    dozen incompatible classical judgments into one number and invites the
    reader to believe a machine has weighed them. /terms says this site claims
    no predictive validity for anything.
    """
    import re

    for module in (synastry, sharecard):
        source = inspect.getsource(module)
        # Comments and docstrings stripped: both modules EXPLAIN at length why
        # there is no percentage, and a naive scan flags that explanation.
        code = re.sub(r'"""..*?"""', " ", source, flags=re.S)
        code = re.sub(r"(?m)#.*$", " ", code)
        for banned in ("percent", "score", "/ 100"):
            assert banned not in code.lower(), f"{module.__name__} computes a {banned!r}"


def test_the_headline_is_a_count():
    out = synastry.read(
        [{"from": "A Sun", "to": "B Moon", "aspect": "trine", "orb": 2.0}],
        "Shruti", "Kiyomi",
    )
    assert out["tally"] == {"harmonious": 1, "hard": 0, "neither": 0}
    assert "1" in out["headline"]


def test_the_caveats_travel_with_the_reading():
    out = synastry.read([], "A", "B")
    joined = " ".join(out["caveats"]).lower()
    assert "not a prediction" in joined
    assert "sect" in joined, "the thing it does not model should say so"
    assert "disagree" in joined


def test_the_card_carries_the_disclaimer_itself():
    """A card travels without its page."""
    source = inspect.getsource(sharecard.comparison_card)
    assert "Not a prediction" in source


# ── the classical rule, applied correctly ───────────────────────────────────

def test_a_conjunction_takes_the_nature_of_what_is_conjunct():
    """
    Treating every conjunction as harmonious is the commonest way software
    gets this wrong. Venus conjunct is read kindly; Saturn conjunct is not.
    """
    assert synastry._tone("conjunction", "Venus", "Moon") == "harmonious"
    assert synastry._tone("conjunction", "Saturn", "Moon") == "hard"
    assert synastry._tone("conjunction", "Sun", "Mercury") == "neither"
    # Both a benefic and a malefic: the tradition would argue, so this does not.
    assert synastry._tone("conjunction", "Venus", "Saturn") == "neither"


def test_squares_and_oppositions_are_hard_and_trines_are_not():
    assert synastry._tone("square", "Sun", "Sun") == "hard"
    assert synastry._tone("opposition", "Venus", "Venus") == "hard"
    assert synastry._tone("trine", "Saturn", "Saturn") == "harmonious"


def test_a_marker_is_named_once_however_often_it_recurs():
    """Sun–Moon both ways round is one marker, not two."""
    out = synastry.read([
        {"from": "A Sun", "to": "B Moon", "aspect": "trine", "orb": 1.0},
        {"from": "B Sun", "to": "A Moon", "aspect": "sextile", "orb": 2.0},
    ], "Shruti", "Kiyomi")
    titles = [m["title"] for m in out["markers"]]
    assert titles.count("Luminaries in contact") == 1


def test_the_reading_names_people_not_letters():
    out = synastry.read(
        [{"from": "A Sun", "to": "B Moon", "aspect": "trine", "orb": 1.0}],
        "Shruti", "Kiyomi",
    )
    assert "Shruti's Sun" in out["markers"][0]["detail"]
    assert "Kiyomi's Moon" in out["markers"][0]["detail"]
    assert " A " not in out["markers"][0]["detail"]


def test_nothing_in_contact_is_an_answer_not_a_gap():
    out = synastry.read([], "A", "B")
    assert out["markers"] == []
    assert "its own answer" in out["headline"]


# ── the card ────────────────────────────────────────────────────────────────

def test_the_card_is_the_size_every_platform_accepts():
    assert (sharecard.WIDTH, sharecard.HEIGHT) == (1200, 630)


def test_the_card_renders_without_avatars():
    """Plenty of comparisons will have one side or neither."""
    png = sharecard.comparison_card(
        left_name="Shruti", right_name="Kiyomi",
        headline="Luminaries in contact", band="Well aspected",
        harmonious=7, hard=3,
    )
    assert png.startswith(PNG_MAGIC)
    assert len(png) > 5000


def test_an_avatar_is_cropped_to_a_square_not_squashed():
    """A portrait squeezed into a square is somebody's art distorted, and for
    a VTuber that art is their face."""
    source = inspect.getsource(sharecard._circle)
    assert "min(w, h)" in source and "crop" in source


def test_a_broken_avatar_does_not_break_the_card():
    png = sharecard.comparison_card(
        left_name="A", right_name="B", headline="x", band="Mixed testimony",
        harmonious=1, hard=1, left_avatar=b"this is not an image",
    )
    assert png.startswith(PNG_MAGIC)


def test_the_fonts_are_actually_shipped():
    """A container has no fonts at all; the default bitmap face looks like a
    1997 error dialogue."""
    for name in ("EBGaramond-SemiBold.ttf", "Commissioner.ttf"):
        path = sharecard.FONTS / name
        assert path.is_file(), f"{name} is not in the image"
        assert path.read_bytes()[:4] in TTF_MAGIC


# ── avatars are uploaded, never fetched ─────────────────────────────────────

def test_nothing_fetches_an_avatar_from_a_social_account():
    """
    Pulling somebody's picture off Twitter or YouTube because a third person
    typed their handle puts a face on a shareable image without its owner
    agreeing — and for a VTuber that image is usually commissioned art.
    """
    from shruti.api.routes import charts

    source = inspect.getsource(charts)
    for host in ("twitter.com", "x.com", "googleusercontent", "youtube.com/channel"):
        assert host not in source
    from shruti.models.accounts import SavedChart

    assert "avatar_media_id" in SavedChart.model_fields, (
        "the avatar should be a reference to media SHE holds, uploaded by the "
        "chart's own owner"
    )


# ── the band ────────────────────────────────────────────────────────────────

def test_there_are_five_bands_worst_to_best():
    assert len(synastry.BANDS) == 5
    keys = [k for k, _n, _s in synastry.BANDS]
    assert keys[0] == "contrary-to-sect" and keys[-1] == "same-sky"


def test_the_bands_use_the_traditions_own_words():
    """
    "Mixed testimony" and "contrary to sect" are terms of art, not invented
    whimsy — testimonies are how horary weighs a question, sect is the
    day/night division. Using the real vocabulary is the difference between
    a fun band and a made-up one.
    """
    names = " ".join(n for _k, n, _s in synastry.BANDS).lower()
    assert "testimony" in names and "sect" in names


def test_a_tiny_sample_never_reaches_an_extreme():
    """
    Two aspects both harmonious is not "written in the same sky", it is a
    small sample — and a verdict that swings on one contact is one nobody
    should post.
    """
    top = synastry.band({"harmonious": 2, "hard": 0, "neither": 0})
    assert top["key"] != "same-sky"
    bottom = synastry.band({"harmonious": 0, "hard": 2, "neither": 0})
    assert bottom["key"] != "contrary-to-sect"


def test_a_big_lopsided_sample_does_reach_one():
    assert synastry.band({"harmonious": 14, "hard": 3, "neither": 0})["key"] == "same-sky"
    assert synastry.band({"harmonious": 2, "hard": 14, "neither": 0})["key"] == "contrary-to-sect"


def test_nothing_in_contact_lands_in_the_middle_and_says_why():
    out = synastry.band({"harmonious": 0, "hard": 0, "neither": 0})
    assert out["key"] == "mixed-testimony"
    assert "its own answer" in out["says"]
    assert out["ratio"] is None


def test_the_band_always_carries_its_evidence():
    """
    A band with the count beside it can be argued with. A number out of a
    hundred cannot, which is the whole reason there isn't one.
    """
    out = synastry.band({"harmonious": 9, "hard": 6, "neither": 0})
    assert out["sample"] == 15
    assert out["ratio"] == 0.6


# ── the invitation ──────────────────────────────────────────────────────────

def test_an_invitation_is_the_inviters_share_token():
    """One token, so taking the share back cancels every invitation from it."""
    from shruti.api.routes import charts

    source = inspect.getsource(charts.accept_invite)
    assert "SavedChart.share_token == token" in source


def test_the_guest_owns_the_chart_they_cast():
    """
    They get its owner token back, so deleting it later is theirs to do. The
    inviter holds a share token and a share token has never been able to act
    as an owner anywhere in that file.
    """
    from shruti.api.routes import charts

    source = inspect.getsource(charts.accept_invite)
    assert '"chartToken": mine.owner_token' in source


def test_accepting_needs_consent_when_there_is_no_account():
    from shruti.api.routes import charts

    source = inspect.getsource(charts.accept_invite)
    assert "body.consent" in source
    assert "chart-invite" in source, "the consent record should say where it came from"


def test_the_result_is_shared_immediately():
    """An invitation whose result only one person can see is not one."""
    from shruti.api.routes import charts

    assert "both.share_token = _token()" in inspect.getsource(charts.accept_invite)


def test_the_invitation_page_reveals_nothing_but_a_name():
    """Their birth moment is theirs until a comparison exists."""
    from shruti.api.routes import charts

    source = inspect.getsource(charts.read_invite)
    for leaked in ("birth_date", "birth_time", "place_name", "lat", "lon"):
        assert leaked not in source
