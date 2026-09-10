# SPDX-License-Identifier: AGPL-3.0-only
"""
Every endpoint the app calls exists on the backend.

⚠ **The two ship separately and at different speeds.** The app goes out as an
APK through a store review; the site goes out as a deploy. So a phone can be
NEWER than shrutivtuber.com, or older, and an endpoint renamed on one side is
a feature that silently stops working on the other — for everybody who has not
updated, with no error anywhere except a 404 the app turns into "that did not
work".

This reads the Dart source and the FastAPI routers, so it fails at the moment
somebody renames a path rather than when somebody's phone does.

⚠ It cannot check the SHAPE of what comes back. A field renamed inside a JSON
body is invisible here and is caught by the app's own integration tests, which
run against a real backend.
"""
from __future__ import annotations

import re
from pathlib import Path

from conftest import ROOT

def _app_source() -> Path:
    """
    Where the app's Dart is, on a laptop or in the test container.

    ⚠ It is a different repository. `scripts/test.sh` mounts it at
    /app/app-source when it is checked out beside this one.
    """
    for candidate in (ROOT.parent / "shruti-tools" / "lib",
                      ROOT / "app-source"):
        if candidate.is_dir() and any(candidate.rglob("*.dart")):
            return candidate
    return ROOT / "app-source"


APP = _app_source()


def _normalise(path: str) -> str:
    """`/api/practice/{work_id}` and `/api/practice/$id` are the same route."""
    path = re.sub(r"\$\{[^}]*\}", "{}", path)
    path = re.sub(r"\$[A-Za-z_][A-Za-z0-9_]*", "{}", path)
    path = re.sub(r"\{[^}]*\}", "{}", path)
    return path.split("?")[0].rstrip("/") or "/"


def _backend_paths() -> set[str]:
    import importlib
    import pkgutil

    import shruti.api.routes as routes_pkg

    found: set[str] = set()
    for info in pkgutil.iter_modules(routes_pkg.__path__):
        module = importlib.import_module(f"shruti.api.routes.{info.name}")
        router = getattr(module, "router", None)
        if router is None:
            continue
        for route in router.routes:
            if getattr(route, "methods", None):
                found.add(_normalise(route.path))
    return found


def _app_paths() -> set[str]:
    wanted: set[str] = set()
    for file in APP.rglob("*.dart"):
        for match in re.finditer(r"'(/api/[^']*)'", file.read_text(encoding="utf-8")):
            wanted.add(_normalise(match.group(1)))
    return wanted


def test_the_app_calls_nothing_the_backend_does_not_serve() -> None:
    if not APP.is_dir():
        # The app lives in its own repository. Where it is not checked out
        # beside this one there is nothing to compare, and a test that invents
        # a pass here would be worse than one that says it did not run.
        import pytest

        pytest.skip(f"the app is not checked out at {APP}")

    backend = _backend_paths()
    wanted = _app_paths()
    assert wanted, "found no /api calls in the app at all — the scan is broken"

    missing = sorted(p for p in wanted if p not in backend)
    assert not missing, (
        "the app calls endpoints this backend does not serve. Every one of "
        "these is a feature that fails on a phone with no error anywhere:\n  "
        + "\n  ".join(missing)
    )


def test_the_scan_would_notice_a_rename() -> None:
    """
    ⚠ The guard's own guard. A path regex that matches nothing passes this
    file trivially and for ever, which is the way a check like this dies.
    """
    if not APP.is_dir():
        import pytest

        pytest.skip("the app is not checked out")

    wanted = _app_paths()
    assert "/api/practice/draft" in wanted, (
        "the scan no longer finds a path everybody knows is there"
    )
    assert _normalise("/api/practice/${work.id}/vote") == "/api/practice/{}/vote"
    assert _normalise("/api/practice/{work_id}/vote") == "/api/practice/{}/vote"
