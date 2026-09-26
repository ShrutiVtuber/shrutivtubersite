# SPDX-License-Identifier: AGPL-3.0-only
"""
Swara Studio: the data is served and never written, a setting is checked, a
song is checked, nobody is walled off, the app signs in with a one-time code,
and everything a person keeps goes with their account.

The facts themselves are built from a private research repository; these
tests read small fixtures written for them (tests/fixtures/carnatic), in the
shape `scripts/carnatic/build_data.py` writes, and that script's own rules
directly.
"""
from __future__ import annotations

import asyncio
import importlib.util
import inspect
import re
from pathlib import Path

import pytest
from fastapi import HTTPException

from conftest import BACKEND, ROOT   # noqa: E402

from shruti.api.routes import carnatic as routes
from shruti.core import carnatic as rules

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "carnatic"


@pytest.fixture()
def published(monkeypatch):
    monkeypatch.setattr(rules, "DATA_DIR", FIXTURES)
    rules._cache.clear()
    yield FIXTURES
    rules._cache.clear()


def _build_data():
    for candidate in (ROOT / "scripts" / "carnatic" / "build_data.py", Path("/app/scripts/carnatic/build_data.py")):
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("build_data", candidate)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    pytest.skip("scripts/carnatic/build_data.py is not mounted")


# ── the data ────────────────────────────────────────────────────────────────

def test_nothing_published_is_a_working_state(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(rules, "DATA_DIR", tmp_path)
    assert rules.manifest() is None and rules.data("ragas.json") is None
    with pytest.raises(HTTPException) as e:
        routes.data_manifest(response=type("R", (), {"headers": {}})())
    assert e.value.status_code == 404


def test_a_published_file_is_served_by_name_and_digest(published) -> None:
    assert rules.data("ragas.json")["janyas"][0]["id"] == "mohanam"
    assert rules.digest_of("ragas.json") and len(rules.digest_of("ragas.json")) == 16


@pytest.mark.parametrize("name", ["../secrets.json", "manifest.json", "RAGAS.json", "ragas.json/..",
                                  "talas.json", "x.txt", ""])
def test_nothing_outside_the_manifest_is_reachable(published, name) -> None:
    """Unlisted, oddly named or escaping paths are not found, whether or not a file exists."""
    assert rules.data_path(name) is None


def test_the_data_is_read_and_never_written() -> None:
    source = inspect.getsource(rules) + inspect.getsource(routes)
    assert "write_text" not in source and "write_bytes" not in source


# ── nobody is walled off ────────────────────────────────────────────────────

def test_a_signed_out_visitor_is_answered_not_refused() -> None:
    out = asyncio.run(routes.me(user=None, session=None))
    assert out == {"signedIn": False, "limits": {"partsPerSong": 2}, "settings": None}


def test_reading_needs_no_account() -> None:
    for fn in (routes.data_manifest, routes.data_file, routes.reviews, routes.sheet, routes.listen,
               routes.comments, routes.redeem):
        params = inspect.signature(fn).parameters
        assert not any("require_user" in str(p.default) for p in params.values()), fn.__name__


def test_the_part_limit_is_two_and_supporters_have_none() -> None:
    assert rules.part_limit(False) == 2 and rules.part_limit(True) is None


def test_a_supporter_is_a_live_subscription_at_any_tier() -> None:
    code = inspect.getsource(routes.is_supporter)
    assert '{"active", "trialing"}' in code and "tier" not in code.split('"""')[2], (
        "every Swaras tier unlocks every gated tool (owner's rule), so the tier must not be checked")


# ── settings ────────────────────────────────────────────────────────────────

def test_settings_are_checked_and_unknown_keys_are_kept() -> None:
    clean = rules.clean_settings({"lang": "ta", "tamilStyle": "pure", "sa": "E5", "tempo": 60, "fromANewerApp": 1})
    assert clean["fromANewerApp"] == 1 and clean["tamilStyle"] == "pure"
    for bad in ({"lang": "fr"}, {"sa": "E9"}, {"sa": "H3"}, {"tempo": 90}, {"tempo": True},
                {"droneTuning": "sa"}, {"tamilStyle": "mixed"}, {"fourthSpeed": "yes"}, []):
        with pytest.raises(rules.Invalid):
            rules.clean_settings(bad)


def test_the_default_sa_follows_the_owners_decisions() -> None:
    assert rules.DEFAULT_SA["voice"] == "C3" and rules.DEFAULT_SA["venu"] == "E5"
    assert rules.DEFAULT_SA["veena"] == "E3" and rules.DEFAULT_SA["violin"].startswith("E")
    assert rules.DEFAULTS["tamilStyle"] == "grantha" and rules.DEFAULTS["playbackTuning"] == "just"


# ── songs ───────────────────────────────────────────────────────────────────

def song(lines=None, per=2, parts=None, tala="adi"):
    count = {"notes": ["kampita:G3", ","] if per == 2 else ["G3"], "sahitya": "கா", "parts": {}}
    return {"format": 1, "title": "Kaalai isai", "raga": "mohanam", "tala": tala,
            "parts": parts or [{"id": "melody", "kind": "melody", "instrument": "venu"}],
            "sections": [{"id": "pallavi", "name": "Pallavi", "notesPerCount": per,
                          "lines": lines if lines is not None else [{"counts": [count] * rules.TALA_COUNTS[tala]}]}]}


def test_a_sound_song_passes() -> None:
    assert rules.check_song(song()) and rules.check_song(song(per=1, tala="misra_chapu"))


@pytest.mark.parametrize("breaks", [
    lambda s: s["sections"][0]["lines"][0]["counts"].pop(),                         # a count short
    lambda s: s["sections"][0]["lines"][0]["counts"][0]["notes"].append("P"),       # too many notes
    lambda s: s["sections"][0]["lines"][0]["counts"][0].update(notes=["X", ","]),   # not a note
    lambda s: s["sections"][0]["lines"][0]["counts"][0].update(notes=["wiggle:G3", ","]),
    lambda s: s["sections"][0]["lines"][0]["counts"][0].update(notes=["M3", ","]),
    lambda s: s["sections"][0]["lines"][0]["counts"][0].update(notes=["P2", ","]),
    lambda s: s.update(tala="nonsense"),
    lambda s: s.update(title=""),
    lambda s: s.update(parts=[{"id": "p2", "kind": "strokes"}]),
    lambda s: s["sections"][0]["lines"][0]["counts"][0].update(parts={"p9": ["tha"]}),
])
def test_a_broken_song_is_refused_in_words(breaks) -> None:
    s = song()
    breaks(s)
    with pytest.raises(rules.Invalid) as e:
        rules.check_song(s)
    assert str(e.value).lstrip("“")[0].isupper(), "the sentence is shown to a person"


def test_octave_dots_are_parsed_never_shown_as_ascii() -> None:
    assert rules.parse_note("S'")["octave"] == 1 and rules.parse_note("..P")["octave"] == -2
    assert rules.parse_note(",") is None and rules.parse_note("jaru-up:D2")["gamaka"] == "jaru-up"


def test_a_note_outside_the_raga_is_kept_and_named(published) -> None:
    s = song()
    s["sections"][0]["lines"][0]["counts"][3]["notes"] = ["M1", "N2"]
    rules.check_song(s)
    mohanam = rules.data("ragas.json")["janyas"][0]
    assert rules.out_of_raga(s, mohanam) == ["M1", "N2"]


def test_parts_beyond_the_limit_are_refused_but_a_kept_song_can_be_saved() -> None:
    code = inspect.getsource(routes._check_body)
    assert "parts > rules.parts_in(before" in code, "a song kept from a supporter year must stay editable"


def test_a_slug_never_collides_and_is_readable() -> None:
    a, b = rules.song_slug("Kaalai isai"), rules.song_slug("Kaalai isai")
    assert a != b and a.startswith("kaalai-isai-") and rules.song_slug("காலை").startswith("song-")


# ── Listen ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("url,player", [
    ("https://www.youtube.com/watch?v=abc", "youtube"), ("https://youtu.be/abc", "youtube"),
    ("https://soundcloud.com/a/b", "soundcloud"), ("https://vimeo.com/1", "vimeo"),
    ("https://artist.bandcamp.com/track/x", "bandcamp"),
    ("http://youtube.com/watch?v=abc", None), ("https://evil.example/youtube.com", None),
    ("https://youtube.com.evil.example/x", None), ("javascript:alert(1)", None),
])
def test_only_the_four_players_are_accepted(url, player) -> None:
    assert rules.player_of(url) == player


# ── signing the app in ──────────────────────────────────────────────────────

def test_a_code_is_eight_unambiguous_symbols_and_forgiving_to_type() -> None:
    code = rules.new_code()
    assert re.fullmatch(r"[23456789ABCDEFGHJKMNPQRSTVWXYZ]{4}-[23456789ABCDEFGHJKMNPQRSTVWXYZ]{4}", code)
    assert rules.normalise_code(code.lower().replace("-", " ")) == code.replace("-", "")
    for bad in ("K7M4-Q9T", "K7M4-Q9T0", "K7M4-Q9TI", "", "K7M4Q9TXX"):
        assert rules.normalise_code(bad) is None


def test_only_hashes_of_a_link_are_kept() -> None:
    code = inspect.getsource(routes.create_link)
    assert "token_hash=rules.token_hash(token)" in code and "code_hash=rules.code_hash(" in code
    assert rules.code_hash("ABCD2345", "k1") != rules.code_hash("ABCD2345", "k2")


def test_a_link_is_used_once_in_one_statement() -> None:
    code = inspect.getsource(routes.redeem)
    assert "update(CarnaticDeviceLink)" in code and "used_at.is_(None)" in code and ".returning(" in code


def test_every_failed_redeem_says_the_same_thing() -> None:
    code = inspect.getsource(routes.redeem)
    assert code.count("return fail()") >= 4 and "INVALID_LINK" in inspect.getsource(routes)


def test_the_window_fills_and_empties() -> None:
    w = rules.Window(limit=2, seconds=600)
    w.add("x"); w.add("x")
    assert w.full("x") and not w.full("y")


# ── routes and the account ──────────────────────────────────────────────────

def test_literal_routes_come_before_the_ones_that_would_swallow_them() -> None:
    source = inspect.getsource(routes)
    assert source.index('"/listen/comments/{comment_id}"') < source.index('"/listen/{post_id}"')
    assert source.index('"/device-link/redeem"') < source.index('"/device-link/{link_id}/status"')
    assert source.index('"/sheets/{slug}"') < source.index('"/songs/{song_id}"') or "/songs/sheets" not in source


def test_every_table_goes_with_the_account_from_the_first_migration() -> None:
    versions = ROOT / "backend" / "alembic" / "versions"
    if not versions.is_dir():
        versions = ROOT / "alembic" / "versions"
    path = next(versions.glob("n2l8i5j1k187_*.py"))
    text = path.read_text()
    models = (BACKEND / "models" / "carnatic.py").read_text()
    tables = [t for t in re.findall(r'__tablename__ = "(carnatic_\w+)"', models) if t != "carnatic_review"]
    assert len(tables) == 8
    for table in tables:
        assert f'("{table}", "user_id")' in text, f"{table} must be in NOBODYS_BUT_THEIRS"
    assert text.count("ondelete=\"CASCADE\"") >= 3


def test_the_school_keeps_no_streak() -> None:
    for path in (BACKEND / "models" / "carnatic.py", BACKEND / "api" / "routes" / "carnatic.py",
                 BACKEND / "core" / "carnatic.py"):
        code = re.sub(r'""".*?"""', "", path.read_text(), flags=re.S)
        code = re.sub(r"(?m)#.*$", "", code)
        assert "streak" not in code.lower() and "missed" not in code.lower(), path.name


# ── the review queue ────────────────────────────────────────────────────────

def test_the_queue_lists_every_script_name_and_every_uncertain_fact(published) -> None:
    items = routes.queue_items(rules.data("ragas.json"), rules.data("instruments.json"))
    keys = {i["key"] for i in items}
    assert {"script:janya:mohanam:ta", "script:janya:mohanam:te", "script:mela:28:kn",
            "script:mela:15:te", "fact:raga:mohanam", "fact:venu:tara-D1-primary",
            "script:stroke:chapu:kn"} <= keys
    assert "script:janya:mohanam:kn" not in keys, "a name that was never sourced is not queued"
    assert "script:mela:15:kn" not in keys
    assert all(i["level"] != "high" for i in items)


# ── the build script (reads the private research; its rules are tested here) ─

def test_the_known_slips_are_fixed_on_the_way_through() -> None:
    b = _build_data()
    assert b.clean_script("దేశ్ రాగం † ᵃ") == "దేశ్"
    assert b.clean_script("ಖಮಾಸ್ (ರಾಗ) ᵃ") == "ಖಮಾಸ್"
    assert b.clean_script("பைரவி (ராகம்) ᵃ") == "பைரவி"
    assert b.clean_script("ರೇವತಿ ˡ") == "ರೇವತಿ" and b.clean_script("பூபாளம் ˡ143") == "பூபாளம்"
    assert b.clean_script("ಭೈರವಿ (ಕರ್ನಾಟಕ) ᵃ") == "ಭೈರವಿ"
    assert b.SCRIPT_OVERRIDES[("sri", "ta")] == {"grantha": "ஸ்ரீ", "pure": "சிறீ"}


def test_both_tamil_styles_are_kept_where_both_are_sourced() -> None:
    b = _build_data()
    assert b.tamil_pair([("a", "சாவேரி ᵃ"), ("l", "ஸாவேரி ˡ234")]) == {"grantha": "ஸாவேரி", "pure": "சாவேரி"}
    assert b.tamil_pair([("a", "மோகனம் ᵃ"), ("l", "மோகனம் ˡ180")]) == {"grantha": "மோகனம்", "pure": None}
    assert b.tamil_pair([]) == {"grantha": None, "pure": None}


def test_the_janya_table_is_read_with_its_markers(tmp_path) -> None:
    b = _build_data()
    table = "\n".join([
        "## 6. Script names for the 62 janya ragas", "",
        "| id | ta | te | kn | sources |", "|---|---|---|---|---|",
        "| khamas | கமாஸ் ᵃ ; கமாஸ் ˡ25 | ఖమస్ రాగం ᵃ | ಖಮಾಸ್ (ರಾಗ) ᵃ | TA TE KN |",
        "| dwijavanti | த்விஜாவந்தி ˡ77 |  | ಜೈಜೈವಂತಿ †(Hindustani Jaijaivanti article) ᵃ | TA KN |",
        "", "## 7. Swara letters",
    ])
    rows = b.parse_janya_scripts(table)
    assert b.janya_scripts("khamas", rows) == {"ta": {"grantha": "கமாஸ்", "pure": None}, "te": "ఖమస్", "kn": "ಖಮಾಸ್"}
    assert b.janya_scripts("dwijavanti", rows)["kn"] is None, "another raga's article is not this raga's name"


def test_the_repeat_badge_is_the_validators_rule() -> None:
    b = _build_data()
    assert b.repeats_for(16, 8) == {"1": 1, "2": 1, "3": 2}      # sarali 1
    assert b.repeats_for(32, 8) == {"1": 1, "2": 1, "3": 1}      # sarali 2
    assert b.repeats_for(140, 14) == {"1": 1, "2": 1, "3": 2}    # alankaram 1
    with pytest.raises(b.BuildError):
        b.repeats_for(9, 8)


def test_katapayadi_reads_right_to_left() -> None:
    b = _build_data()
    rec = {"number": 28, "katapayadi": {"aksharas": ["ha", "ri"], "rule_applied": "last consonant of each akshara"}}
    assert b.katapayadi(rec)["digits"] == [8, 2]
    with pytest.raises(b.BuildError):
        b.katapayadi({**rec, "number": 82})
