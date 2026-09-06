# SPDX-License-Identifier: AGPL-3.0-only
"""
Configuration must be read where it can actually be read.

**`import.meta.env` is substituted when the bundle is COMPILED.** For a
container image that happens before the thing is ever deployed, so a value
handed to the running container does not override it — the literal compiled in
weeks earlier wins. Nothing errors. The site serves the wrong value, cheerfully.

That is not a hypothetical: `SHRUTI_SOURCE_SHA` was read that way and the AGPL
source link fell back to the repository while the container had the exact
commit in its environment the entire time. It looked like it was working, which
is the only reason it survived a deploy and a check.

`SHRUTI_SITE_URL` was read the same way in TEN separate files, each with its own
copy of the same fallback. It happens to be harmless today only because the
fallback and the production value are the same string — so the variable does
nothing, and the day the origin changes, every canonical tag, every sitemap
entry, robots.txt and the structured data all keep pointing at the old one.

So: one module reads configuration, at runtime, and nothing else touches it.
"""
from __future__ import annotations

import re
from pathlib import Path

from tests.test_copy import SRC

ENV_MODULE = SRC / "lib" / "env.ts"

# The build-time read. Anywhere but the one module, it is the bug above.
BUILD_TIME = re.compile(r"import\.meta\.env\.SHRUTI_")

# A hand-rolled origin with its own fallback — the shape that was in ten files.
OWN_FALLBACK = re.compile(r'SHRUTI_SITE_URL\s*\?\?\s*"https://')


def _sources() -> list[Path]:
    return [p for p in SRC.rglob("*")
            if p.suffix in (".ts", ".astro", ".js") and p.is_file()]


def test_only_one_module_reads_configuration() -> None:
    """
    Every other file asks that module. This is the check the codebase already
    wanted — `api.ts` says the origin "lives here once" — and that nine files
    had quietly stopped honouring.
    """
    offenders = [
        str(p.relative_to(SRC)) for p in _sources()
        if p != ENV_MODULE and BUILD_TIME.search(p.read_text(encoding="utf-8"))
    ]
    assert not offenders, (
        "these read configuration at build time, which silently ignores what "
        f"the container is given — use lib/env.ts: {offenders}"
    )


def test_nobody_keeps_their_own_copy_of_the_origin() -> None:
    """
    Ten copies of one fallback is ten places to miss when the domain moves, and
    the ones that are missed do not fail — they serve the old host.
    """
    offenders = [
        str(p.relative_to(SRC)) for p in _sources()
        if p != ENV_MODULE and OWN_FALLBACK.search(p.read_text(encoding="utf-8"))
    ]
    assert not offenders, f"import SITE_URL from lib/api instead: {offenders}"


def test_the_env_module_reads_the_running_process_first() -> None:
    """`process.env` is the runtime half. Without it the module is the bug."""
    said = ENV_MODULE.read_text(encoding="utf-8")
    assert "process.env" in said
    # And it must still fall back, or anything genuinely fixed at build breaks.
    assert "import.meta.env" in said
