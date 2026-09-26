# SPDX-License-Identifier: AGPL-3.0-only
"""
The Guides wing has a vocabulary, and a few words are never in it.

From the 20 September handoff (README §5): *live* is the site's badge word —
a token is `drawing` or `idle`; *offline* never describes a token; and the
brief's oldest rule — nothing measures the person — means no *streak*, no
*missed*, no counts of *days*, no *rank* and no *%* of anybody. `--live`, the
one red on the site, appears nowhere in the wing: nothing in Guides is red.

Checked on the say() defaults and the styles of every page and component in
the wing, so a hurried edit cannot bring one of them back.
"""
from __future__ import annotations

import re
from pathlib import Path

from test_marks_are_type_not_emoji import SRC

WING = [
    *sorted((SRC / "pages" / "guides").rglob("*.astro")),
    *sorted((SRC / "pages" / "builds").rglob("*.astro")),
    *sorted((SRC / "pages" / "groups").rglob("*.astro")),
    SRC / "pages" / "tracker.astro",
    SRC / "pages" / "play.astro",
    *sorted((SRC / "components" / "play").rglob("*.astro")),
    *sorted((SRC / "components" / "guides").rglob("*.astro")),
    SRC / "components" / "chrome" / "GuidesNav.astro",
    SRC / "styles" / "guides-section.css",
    SRC / "styles" / "guides.css",
]
SAY = re.compile(r'say\("[^"]+",\s*"((?:[^"\\]|\\.)*)"')
# Whole words. "ranked" is the wing's own word ("nobody is ranked"). "rank" is left
# out of the sweep on purpose: a guide's seasonal TRACK has a rank — the game's own
# ladder, which the guide format models and a run checks in with — and that is not a
# rank of a person among people, which is the thing the rule forbids.
FORBIDDEN = re.compile(r"\b(live|offline|streak|streaks|missed|days)\b|%(?!\{)", re.I)
# The one place the word "live" is allowed to be typed: a say() KEY that predates the rule.
ALLOWED_DEFAULTS = {"live from Athens"}


def test_no_page_in_the_wing_is_red():
    for p in WING:
        assert "var(--live" not in p.read_text(encoding="utf-8"), f"{p.relative_to(SRC)} uses --live: nothing in Guides is red"


def test_the_words_that_never_appear():
    guilty = []
    for p in WING:
        if p.suffix != ".astro":
            continue
        for m in SAY.finditer(p.read_text(encoding="utf-8")):
            text = m.group(1)
            if any(a in text for a in ALLOWED_DEFAULTS):
                continue
            hit = FORBIDDEN.search(text)
            if hit:
                guilty.append(f"{p.relative_to(SRC)}: {hit.group(0)!r} in {text[:60]!r}")
    assert not guilty, "words the wing never uses:\n" + "\n".join(guilty)
