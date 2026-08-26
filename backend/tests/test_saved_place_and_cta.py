# SPDX-License-Identifier: AGPL-3.0-only
"""
The instruments open where you are, and the invitation only promises that
because it is true.

These two things shipped together on purpose. The copy at the foot of every
free instrument says an account makes them open at your place; that sentence
was written after the behaviour existed, not before, and this is what keeps
them in step.

The sharp edge is the natal chart. Its place is where somebody was BORN — the
same shape as "where I am" and a completely different fact. Defaulting it to
where they live now would quietly cast the wrong chart for anybody who has
moved, and it would look entirely correct while doing it.
"""
from __future__ import annotations

import re
from pathlib import Path


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()
TOOLS = SRC / "pages" / "tools"

# Everything that needs a horizon to mean anything.
NEEDS_A_HORIZON = [
    "planetary-hours.astro", "pancanga.astro",
    "attic-calendar.astro", "hindu-calendar.astro", "[kind]-stations.astro",
]


def test_the_horizon_instruments_open_at_your_place() -> None:
    for name in NEEDS_A_HORIZON:
        body = (TOOLS / name).read_text(encoding="utf-8")
        assert "savedPlace" in body, (
            f"{name} still defaults to Athens for everybody — the invitation on "
            f"this very page says it does not"
        )


def test_the_natal_chart_does_not() -> None:
    """
    Birth place, not current place. Getting this wrong casts a wrong chart that
    looks right, which is the worst failure available on this site.
    """
    body = (TOOLS / "natal-chart.astro").read_text(encoding="utf-8")
    assert "savedPlace" not in body


def test_a_url_still_wins() -> None:
    """
    A link somebody was sent has to show the place it names. If the reader's
    own place could override it, every shared link would show something
    different to every reader.
    """
    for name in NEEDS_A_HORIZON:
        body = (TOOLS / name).read_text(encoding="utf-8")
        assert re.search(r'q\.get\("lat"\)\s*\?\?', body), (
            f"{name} must read the query string before the saved place"
        )


def test_the_invitation_is_only_shown_to_people_without_an_account() -> None:
    """Showing a sign-up box to somebody signed in is how a site starts
    feeling like it wants something."""
    body = (SRC / "components" / "brand" / "ToolCta.astro").read_text(encoding="utf-8")
    assert "me ? null :" in body


def test_the_remember_control_is_only_shown_to_people_with_one() -> None:
    """
    `savedPlace` returning null is ALSO true for everybody signed out, which is
    what put a sign-in-only control on a public page the first time.
    """
    body = (SRC / "components" / "tools" / "RememberPlace.astro").read_text(encoding="utf-8")
    assert "const me = await account(Astro)" in body
    assert "{me && saved === null" in body


def test_the_place_page_will_not_redirect_off_site() -> None:
    """An open redirect on a signed-in page is how somebody gets walked to a
    convincing copy of it."""
    body = (SRC / "pages" / "account" / "place.astro").read_text(encoding="utf-8")
    assert 'raw.startsWith("/") && !raw.startsWith("//")' in body
