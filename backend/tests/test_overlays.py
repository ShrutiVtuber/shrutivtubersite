# SPDX-License-Identifier: AGPL-3.0-only
"""
Overlays: what they may know, and what must never appear on a stream.

Two properties carry everything here. An overlay is fetched by OBS, which has
no session and never will — so the gate must let it through, or every overlay
renders the holding page and the first person to notice is an audience. And a
token is a credential displayed in a program whose settings get screen-shared,
so it is shown once and never again.
"""
from __future__ import annotations

import ast
import inspect
import re
import textwrap
from pathlib import Path

from shruti.api.routes import overlay


def _code(fn) -> str:
    tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)) and ast.get_docstring(node):
            node.body = node.body[1:]
    return ast.unparse(tree)


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()

# The routes and the pages have to agree, so the tests read both.
BACKEND = Path(__file__).resolve().parents[1] / "shruti"


def code_of(path: Path) -> str:
    """
    A file's source with its prose removed.

    Written because this exact trap has now cost several rounds: a test asserts
    a page never says "no supporters yet", and the page's own comment explaining
    WHY it never says that trips the assertion. Rewording the comment to dodge
    the grep would delete the explanation to protect the test — precisely
    backwards. So the tests read code, and the comments are free to say
    anything they need to.
    """
    text = path.read_text(encoding="utf-8")

    if path.suffix == ".py":
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)) and ast.get_docstring(node):
                node.body = node.body[1:]
        # unparse drops comments too, which is the other half of the job.
        return ast.unparse(tree)

    # Astro/TS: block comments, JSX comments, and line comments that are not
    # part of a URL.
    text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(?<![:/])//[^\n]*", "", text)
    return text



def test_obs_can_reach_an_overlay_without_a_session() -> None:
    """
    OBS is a browser with no cookies carrying only a token in the URL. Left to
    the holding-page gate, every overlay would render the holding page — on a
    live stream, which is where it would be noticed.
    """
    mw = (SRC / "middleware.ts").read_text(encoding="utf-8")
    passthrough = re.search(r"const PASS_THROUGH = /\^\\/\(([^)]*)\)", mw)
    assert passthrough, "could not find the pass-through list"
    assert "overlay" in passthrough.group(1), (
        "overlay paths must bypass the gate — OBS has no session")


def test_overlays_are_kept_out_of_search() -> None:
    robots = (SRC / "pages" / "robots.txt.ts").read_text(encoding="utf-8")
    assert "Disallow: /overlay/" in robots


def test_the_listing_never_returns_a_token() -> None:
    """
    The admin renders this. A credential on a page she opens while streaming is
    the failure this whole design is arranged to avoid.
    """
    src = _code(overlay.admin_overlays)
    assert "o.token" not in src and '"token"' not in src


def test_only_creation_reveals_a_token() -> None:
    """Once, at the moment of minting, and never retrievable afterwards."""
    revealing = [
        name for name, fn in vars(overlay).items()
        if callable(fn) and getattr(fn, "__module__", "") == overlay.__name__
        and "token" in _code(fn) and "return" in _code(fn)
        and re.search(r'return \{[^}]*[\'"]token[\'"]', _code(fn))
    ]
    assert revealing == ["create_overlay"], (
        f"these return a token and should not: {revealing}")


def test_no_overlay_route_mutates_anything() -> None:
    """
    A token is a read-only credential. The public routes may record that an
    overlay was seen and nothing else.
    """
    for fn in (overlay.counter, overlay.events):
        src = _code(fn)
        for forbidden in ("session.add(", "session.delete(", ".update("):
            assert forbidden not in src, f"{fn.__name__} mutates state"


def test_an_unknown_token_is_a_404_not_a_403() -> None:
    """
    Whether a token exists is not something a stranger with a guess should be
    able to collect.
    """
    src = _code(overlay._overlay)
    assert "404" in src and "403" not in src


def test_progress_is_never_capped_at_the_target() -> None:
    """
    The overrun is the best moment the design has, and a clamped figure throws
    it away. The FILL is clamped so the bar cannot overflow its track; the
    NUMBERS are not.
    """
    src = _code(overlay._shape)
    assert "min(" not in src


def test_the_unit_is_a_field_and_never_inferred() -> None:
    """
    "14 / 20 people" and "€184 / €300" are one object. Deciding which by
    sniffing for a currency is how the people case becomes an afterthought.
    """
    page = (SRC / "pages" / "overlay" / "counter.astro").read_text(encoding="utf-8")
    assert "counter.unit" in page


def test_the_overlay_page_does_not_use_the_site_layout() -> None:
    """
    BaseLayout brings a header, a footer, a background and a cookie notice.
    Every one of them is wrong composited over video.
    """
    page = (SRC / "pages" / "overlay" / "counter.astro").read_text(encoding="utf-8")
    # The IMPORT, not the word. The page's own comment explains why it does not
    # use BaseLayout, and searching for the name failed the file for saying so
    # — the fifth time in this project that a comment has tripped its own check.
    assert not re.search(r"^import .*BaseLayout", page, re.M)
    assert "<BaseLayout" not in page


def test_the_overlay_background_is_transparent() -> None:
    css = (SRC / "styles" / "overlay.css").read_text(encoding="utf-8")
    assert "background: transparent !important" in css
    assert "overflow: hidden" in css, "a scrollbar on a stream is a visible bug"


def test_the_instruments_never_ship_an_ephemeris_to_the_browser() -> None:
    """
    The overlay renders on her streaming machine, beside the encoder. Positions
    are computed on the server and pushed as finished numbers; the page draws
    them and does nothing else. An ephemeris running in that browser costs
    frames on the stream.
    """
    for name in ("sky.astro", "hours.astro"):
        page = (SRC / "pages" / "overlay" / name).read_text(encoding="utf-8")
        body = page.split("<script>")[-1] if "<script>" in page else ""
        for forbidden in ("Math.sin", "Math.cos", "julian", "ephemeris"):
            assert forbidden not in body, (
                f"{name}'s client script computes astronomy — it must not")


def test_the_sky_clock_stops_when_the_surface_is_hidden() -> None:
    """
    The seconds digit is the only thing that repaints. An overlay not in the
    scene must compose no frames at all.
    """
    page = (SRC / "pages" / "overlay" / "sky.astro").read_text(encoding="utf-8")
    assert "visibilitychange" in page
    assert "clearInterval" in page


def test_the_hours_strip_composes_nothing_between_turnovers() -> None:
    """
    It shows no seconds, so between one hour and the next there is genuinely
    nothing to repaint — and there must be no interval pretending otherwise.
    """
    page = (SRC / "pages" / "overlay" / "hours.astro").read_text(encoding="utf-8")
    assert "setInterval" not in page


def test_drift_is_reported_rather_than_animated() -> None:
    """
    The Moon moves about half a degree an hour. A moving dot would be a lie at
    stream length, so the honest liveness tell is the rate in words.
    """
    page = (SRC / "pages" / "overlay" / "sky.astro").read_text(encoding="utf-8")
    assert "drift(" in page and "/ h" in page


def test_the_ticker_never_advertises_that_nobody_has_given() -> None:
    """
    Handoff §8. The row runs along the bottom for the whole session, so on the
    first day of a campaign an empty state that says "no supporters yet" tells
    the room nobody has given, at exactly the moment that costs the most. Her
    standing line takes the space instead.
    """
    page = code_of(SRC / "pages" / "overlay" / "ticker.astro")
    assert "no supporters" not in page.lower()
    assert "standing" in page


def test_the_standing_line_is_hers_and_lives_in_one_place() -> None:
    """
    A sentence baked into the page would be a second place to maintain her
    words — the thing she asked never to have to do again.
    """
    route = (BACKEND / "api" / "routes" / "overlay.py").read_text(encoding="utf-8")
    assert "overlay.ticker_standing" in route
    admin = (SRC / "pages" / "admin" / "counters.astro").read_text(encoding="utf-8")
    assert "overlay.ticker_standing" in admin, "she cannot edit it"


def test_the_ticker_shows_no_amounts() -> None:
    """
    Names only. Figures beside names turn everyone who gave a little into a
    small number displayed next to a bigger one, for the whole stream — the
    counter bar carries the total, which is the number that means anything.
    """
    route = code_of(BACKEND / "api" / "routes" / "overlay.py")
    body = route.split("@router.get('/ticker')")[1].split("@router.get")[0]
    assert "amount_minor" not in body, "the ticker payload carries amounts"

    page = (SRC / "pages" / "overlay" / "ticker.astro").read_text(encoding="utf-8")
    assert "amountMinor" not in page


def test_the_countdown_sends_two_instants_not_a_remaining_count() -> None:
    """
    Her streaming PC's clock and the server's disagree. A remaining-seconds
    figure computed here and ticked down there compounds that for the length of
    a stream; two instants let the page correct the offset once, at load.
    """
    route = code_of(BACKEND / "api" / "routes" / "overlay.py")
    body = route.split("@router.get('/countdown')")[1].split("@router.get")[0]
    # unparse normalises quotes, so the key is matched without them.
    assert "'now'" in body and "endsAt" in body
    for guess in ("remaining", "seconds_left", "secondsLeft"):
        assert guess not in body, "the server is counting down for the client"

    page = (SRC / "pages" / "overlay" / "countdown.astro").read_text(encoding="utf-8")
    assert "offset" in page and "data-now" in page


def test_a_closed_window_says_so_rather_than_counting_backwards() -> None:
    page = (SRC / "pages" / "overlay" / "countdown.astro").read_text(encoding="utf-8")
    assert "Window closed" in page
    assert "left <= 0" in page, "nothing stops the face going negative"


def test_neither_surface_repaints_when_it_is_not_in_the_scene() -> None:
    """
    An idle overlay composes no frames (§11). The countdown is the one place a
    per-second repaint is honest — and only while a seconds digit is on the
    face.
    """
    cd = (SRC / "pages" / "overlay" / "countdown.astro").read_text(encoding="utf-8")
    assert "visibilitychange" in cd and "clearInterval" in cd
    assert "30000" in cd, "it ticks per second even when showing days"

    tick = (SRC / "pages" / "overlay" / "ticker.astro").read_text(encoding="utf-8")
    assert "setInterval" in tick and "4 * 60 * 1000" in tick, (
        "a row of words must not poll faster than names arrive")


def test_the_web_variants_and_the_overlay_share_one_ephemeris() -> None:
    """
    Two code paths computing where the Moon is would eventually disagree, and
    the one that disagreed would be the one on the stream — found by somebody
    in chat rather than by a test.
    """
    public = code_of(BACKEND / "api" / "routes" / "public.py")
    assert "sky_now" in public, "the web card computes its own sky"

    overlay = code_of(BACKEND / "api" / "routes" / "overlay.py")
    assert "async def sky_now" in overlay


def test_the_web_variants_obey_the_reader_not_the_encoder() -> None:
    """
    §11: the overlay's motion setting is about her streaming machine; the media
    query is about her reader. A web card taking `motion` would be applying the
    wrong person's preference.
    """
    comp = SRC / "components" / "counters"
    for name in ("CounterCard.astro", "SkyCard.astro"):
        page = code_of(comp / name)
        assert "data-motion" not in page, f"{name} reads the encoder's setting"
    card = code_of(comp / "CounterCard.astro")
    assert "prefers-reduced-motion" in card


def test_the_web_variants_show_both_clocks() -> None:
    """
    §12: the site's dual-time rule does not apply on the overlay — it is her
    screen, in her timezone — but it DOES apply to the two web variants.
    """
    comp = SRC / "components" / "counters"
    for name in ("CounterCard.astro", "SkyCard.astro"):
        page = code_of(comp / name)
        assert "Europe/Athens" in page, f"{name} does not author in Athens"
        assert "resolvedOptions" in page, f"{name} never shows the reader's zone"
        # Server-rendered first, so a reader without JavaScript still gets a
        # time rather than an empty element the script was meant to fill.
        assert "Intl.DateTimeFormat" in page.split("<script>")[0]


def test_the_counter_card_clamps_the_bar_and_not_the_number() -> None:
    """
    The overrun is the best thing that can happen to a goal. The fill must stay
    inside its track; the figure must not.
    """
    card = code_of(SRC / "components" / "counters" / "CounterCard.astro")
    assert "Math.min(100, pct)" in card, "the fill can leave its track"
    assert "const current = counter.current ?? 0;" in card
    assert "Math.min(100, current" not in card


def test_the_web_variants_are_reachable() -> None:
    """
    Written because it has already happened once: /collab and /official were
    built, deployed and linked from nowhere, and she found them, not a test.
    A component nothing imports is the same bug one level down.
    """
    pages = (SRC / "pages")
    used = "\n".join(
        p.read_text(encoding="utf-8")
        for p in pages.rglob("*.astro")
    )
    assert "CounterCard" in used, "CounterCard is on no page"
    assert "SkyCard" in used, "SkyCard is on no page"
