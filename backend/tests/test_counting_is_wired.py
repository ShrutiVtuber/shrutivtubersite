# SPDX-License-Identifier: AGPL-3.0-only
"""
Every tool reports that it was used, and the beacon is on every page.

Not a test of the counting itself — `test_insight.py` does that — but of the
wiring, which is the part that breaks silently. A new tool page that forgets
`data-track` is not an error, does not fail a build, and produces a dashboard
that is quietly wrong: the tool looks unused, which is the most misleading
answer a usage figure can give.

The same for the beacon. It is mounted once, in BaseLayout, and a page that
stops going through BaseLayout stops being counted without saying so.
"""
from __future__ import annotations

from pathlib import Path

import pytest


def _site() -> Path:
    """Mounted at /app/frontend by scripts/test.sh; in the checkout otherwise."""
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        candidate = base / "frontend" / "site" / "src"
        if candidate.is_dir():
            return candidate
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _site()
TOOLS = SRC / "pages" / "tools"


def _tool_pages() -> list[Path]:
    """
    The instruments themselves. `index.astro` is the hub that lists them — it
    computes nothing, so there is nothing for a visitor to press and nothing to
    report as used.
    """
    if not TOOLS.is_dir():
        return []
    return sorted(p for p in TOOLS.glob("*.astro") if p.name != "index.astro")


def test_the_tools_are_actually_being_read():
    """
    The guard that guards the guard.

    A test container that cannot see the frontend finds no tool pages, passes
    every check below on an empty list, and reports green while the thing it
    exists to catch is happening. That has already happened once here.
    """
    assert len(_tool_pages()) >= 7, (
        f"only {len(_tool_pages())} tool pages found under {TOOLS} — the "
        "frontend is probably not mounted, so the checks below prove nothing"
    )


@pytest.mark.parametrize("page", _tool_pages(), ids=lambda p: p.name)
def test_every_tool_says_when_it_is_used(page: Path):
    text = page.read_text()
    assert 'data-track="tool:used"' in text, (
        f"{page.name} never reports being used, so it will read as unused on "
        "the dashboard. Put data-track=\"tool:used\" data-track-tool=\"<name>\" "
        "on whatever the visitor presses to make it compute."
    )
    assert "data-track-tool=" in text, (
        f"{page.name} reports a use without saying which tool, so it lands in "
        'the dashboard under the bare event name instead of its own row.'
    )


def test_the_beacon_is_mounted_once_for_the_whole_site():
    base = (SRC / "layouts" / "BaseLayout.astro").read_text()
    assert "<Beacon />" in base, (
        "BaseLayout no longer mounts the beacon; nothing on the site is being "
        "counted, and the dashboard will show zeroes rather than an error."
    )


def test_a_refusal_is_checked_before_anything_is_sent():
    """
    The privacy page promises three ways to refuse. This is the promise.

    Order matters as much as presence: the refusal has to be read before the
    first beacon, not after, or the page somebody opened to opt out has already
    counted them.
    """
    beacon = (SRC / "components" / "insight" / "Beacon.astro").read_text()
    for way in ("globalPrivacyControl", "doNotTrack", "shruti_counting"):
        assert way in beacon, f"the beacon no longer honours {way}"
    assert beacon.index("shruti_counting") < beacon.index("navigator.sendBeacon"), (
        "the refusal is read after the first beacon is sent, so opening the "
        "privacy page to opt out counts you first"
    )


def test_the_privacy_page_carries_the_switch():
    privacy = (SRC / "pages" / "privacy.astro").read_text()
    assert "CountingChoice" in privacy, (
        "the privacy copy promises a switch on this page and there is none"
    )
