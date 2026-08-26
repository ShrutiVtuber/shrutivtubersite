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
