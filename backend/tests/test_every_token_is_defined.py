# SPDX-License-Identifier: AGPL-3.0-only
"""
A token the site never defines is not a style; it is the browser's default.

Nine pages of the guides section were written against `--rule` and `--paper`,
two names that do not exist in the shared tokens. Borders vanished and every
<select> came out in the browser's own white, on the dark theme, with white
text — "the dropdowns are white on white". Nothing warned: an undefined custom
property is simply an empty value.

So: every `var(--name)` used anywhere in the frontend, without a fallback, is
a name defined in the shared tokens, the site's stylesheets, or some source
file (components set their own scoped tokens; that counts). A `var(--name,
fallback)` is allowed to name a token that may be absent — that is what the
fallback is for.
"""
from __future__ import annotations

import re
from pathlib import Path

from test_marks_are_type_not_emoji import SRC

SHARED = SRC.parents[1] / "shared" / "src" / "tokens"
DEFINES = re.compile(r"--([A-Za-z0-9_-]+)\s*:")
USES = re.compile(r"var\(\s*--([A-Za-z0-9_-]+)\s*\)")  # no fallback


def _files():
    yield from sorted(SHARED.glob("*.css"))
    for p in sorted(SRC.rglob("*")):
        if p.suffix in {".astro", ".css", ".ts", ".tsx", ".js"} and "node_modules" not in p.parts:
            yield p


def test_every_token_used_without_a_fallback_is_defined():
    defined: set[str] = set()
    used: dict[str, set[str]] = {}
    for p in _files():
        text = p.read_text(encoding="utf-8")
        defined.update(DEFINES.findall(text))
        for name in USES.findall(text):
            used.setdefault(name, set()).add(str(p.relative_to(SRC.parents[2])))
    # `var(--body-${hue})` and friends are built at render time from a prefix.
    missing = {n: f for n, f in used.items() if n not in defined and not n.endswith("-")}
    lines = [f"--{n}: {', '.join(sorted(f))}" for n, f in sorted(missing.items())]
    assert not missing, "tokens used but never defined:\n" + "\n".join(lines)
