# SPDX-License-Identifier: AGPL-3.0-only
"""
Where the repository is, asked once.

⚠ **`Path(__file__).parents[2]` is the repository on a laptop and `/` in the
container**, because `scripts/test.sh` mounts `backend/tests` at `/app/tests`
rather than mounting the tree. Eleven guards resolved `ROOT` that way, looked
for `/docker-compose.yml` and `/scripts/check_consent_wording.py`, found
nothing, and failed on the missing file rather than on the thing they guard.

They had stopped guarding anything, and they failed loudly enough to be read as
"those always fail" — which is the worst state for a check to be in: still red,
still ignored, still not checking.

So: one function, and it looks for a marker rather than counting directory
levels.
"""
from __future__ import annotations

from pathlib import Path

# What only the repository root has.
MARKERS = ("docker-compose.yml", "pyproject.toml", ".git")


def repo_root() -> Path:
    """
    The top of the tree, wherever the tests happen to be running.

    Walks up from this file looking for a marker, and falls back to `/app`,
    which is where `scripts/test.sh` mounts everything.
    """
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if any((candidate / marker).exists() for marker in MARKERS):
            # `backend/pyproject.toml` is a marker too, so step over it: the
            # repository root is the one that also has docker-compose.yml or
            # a .git.
            if (candidate / "docker-compose.yml").exists() or (
                    candidate / ".git").exists():
                return candidate
    app = Path("/app")
    return app if app.is_dir() else here.parents[2]


ROOT = repo_root()


def _first_dir(*candidates: str) -> Path:
    for candidate in candidates:
        path = ROOT / candidate
        if path.is_dir():
            return path
    return ROOT / candidates[0]


# ⚠ `backend/shruti` on a laptop, `shruti` in the container — the tree is
# mounted, not copied. A test that hard-codes one of those fails on the other
# with a FileNotFoundError, which reads as the guarded thing being missing
# rather than as the guard being lost.
BACKEND = _first_dir("backend/shruti", "shruti")
SITE = _first_dir("frontend/site")
