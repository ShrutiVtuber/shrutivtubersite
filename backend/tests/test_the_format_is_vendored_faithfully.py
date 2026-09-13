# SPDX-License-Identifier: AGPL-3.0-only
"""
The vendored guide format is a byte-for-byte copy of its source.

⚠ Two copies of a validator is one copy too many, and the only thing that
makes it tolerable is a test that fails on the first byte of difference. The
copy exists because the backend image's build context cannot see the guides
repository; it goes the day that repository is on GitHub and becomes a git
dependency. Until then: edit the original, re-copy, and this test says whether
you remembered.
"""
from __future__ import annotations

import filecmp
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1] / "shrutisguides"
SOURCE = Path.home() / "Documents/development/shrutisgametracker/server/shrutisguides"


def _files(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.name != "VENDORED.md"}


def test_the_vendored_format_matches_its_source() -> None:
    if not SOURCE.exists():
        pytest.skip("the guides repository is not checked out beside this one")
    ours, theirs = _files(HERE), _files(SOURCE)
    assert ours == theirs, (
        f"only here: {sorted(ours - theirs)}; only in the source: {sorted(theirs - ours)}"
    )
    drifted = [f for f in sorted(ours) if not filecmp.cmp(HERE / f, SOURCE / f, shallow=False)]
    assert not drifted, f"vendored copy differs from the source in: {drifted} — re-copy it"


def test_the_image_ships_it() -> None:
    dockerfile = (Path(__file__).resolve().parents[1] / "Dockerfile").read_text()
    assert "COPY shrutisguides ./shrutisguides" in dockerfile
    pyproject = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text()
    assert "jsonschema" in pyproject, "the validator's one dependency is not declared"
