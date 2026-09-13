# SPDX-License-Identifier: AGPL-3.0-only
"""
A theme may change palette, type, ornament and the sigil's stroke. It may
not change layout, legibility or the four state colours.
"""
from __future__ import annotations

from shruti.api.routes import overlay_guides as og


def test_the_state_colours_are_never_editable() -> None:
    assert not any(t.startswith("st-") for t in og.EDITABLE), "stroke is a width, st- is a state"
    for token in ("done", "now", "open", "locked", "st-done", "st-now"):
        assert token not in og.EDITABLE


def test_nothing_that_moves_an_element_is_editable() -> None:
    for token in ("x", "y", "w", "width", "left", "top", "font-size", "size", "display"):
        assert token not in og.EDITABLE


def test_only_colours_lengths_and_numbers_are_kept() -> None:
    assert og.css_value("panel", "rgba(26, 33, 56, .92)") == "rgba(26, 33, 56, .92)"
    assert og.css_value("ink", "#EDE3D6") == "#EDE3D6"
    assert og.css_value("ring", "transparent") == "transparent"
    assert og.css_value("radius", "12px") == "12px" and og.css_value("radius", "12") == ""
    assert og.css_value("stroke", "10") == "10" and og.css_value("stroke", "10px") == ""
    for bad in ("url(http://x)", "red; background: url(x)", "#FFF}", "expression(1)", "var(--st-done)", ""):
        assert og.css_value("ink", bad) == "", bad


def test_the_stylesheet_only_repoints_a_themes_own_tokens() -> None:
    css = og.theme_css(og.clean_themes({"grimoire": {"ink": "#FFFFFF", "st-done": "#FF0000", "x": "9"}, "nope": {"ink": "#000"}}))
    assert css == '.gov[data-theme="grimoire"]{--gt-ink:#FFFFFF;}'
    assert og.theme_css({}) == ""
