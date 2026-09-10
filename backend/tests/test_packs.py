# SPDX-License-Identifier: AGPL-3.0-only
"""
The language packs: what they are, and where they may not go.

Isopsephy needs the letter values for a script and a corpus to find matches in.
Both are theourgia's packs, reused rather than reinvented — a second copy of
the Greek Milesian table is a second place for it to be wrong.

⚠ **The packs are All Rights Reserved and the app is AGPL with a public
repository.** They cannot be committed to it. That is not a preference about
download size; it is the licence. The size argument is real too — the Greek
corpus is 4.3MB and Arabic 2MB, against four to nine kilobytes for the letter
values — but it is the second reason, not the first.
"""
from __future__ import annotations

import re
from pathlib import Path


from conftest import BACKEND, ROOT   # noqa: E402  (see conftest for why)


def test_no_pack_is_committed_anywhere() -> None:
    """Not to this repository, and not to the app's.

    A pack that arrives in a public AGPL tree is a licence problem that a
    `git rm` does not fix, because the history keeps it.
    """
    stray = [
        str(p.relative_to(ROOT))
        for p in ROOT.rglob("*.mbf")
        if ".git" not in p.parts and "node_modules" not in p.parts
    ]
    assert not stray, (
        "All Rights Reserved packs must not live in a public repository; they "
        f"are served from the volume at runtime: {stray}"
    )


def test_the_packs_are_served_from_their_own_volume() -> None:
    """Not from the media volume, and not from the image.

    In the image they would be baked into every deploy and into the layer
    history; in `media` they would sit beside uploads that a person can delete
    from the admin.
    """
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert re.search(r"^\s+packs:\s*$", compose, re.M), "no packs volume"
    assert "packs:/srv/packs:ro" in compose, "caddy cannot read them"
    assert "packs:/app/packs" in compose, "the backend cannot list them"


def test_caddy_serves_them_immutable() -> None:
    """A pack filename carries its version, so a URL's bytes never change.

    `immutable` is an honest claim here and a lie almost everywhere else. A new
    version is a new filename, so nothing ever has to be revalidated — which
    matters on a phone that has just spent four megabytes.
    """
    caddy = (ROOT / "Caddyfile.internal").read_text(encoding="utf-8")
    block = caddy[caddy.index("handle /packs/*"):]
    block = block[: block.index("}")]
    assert "immutable" in block
    assert "max-age=31536000" in block
    # The app is a different origin from the site.
    assert "Access-Control-Allow-Origin" in block


def test_the_sync_is_a_script_rather_than_a_habit() -> None:
    """Drift is prevented by digests, not by somebody remembering to copy.

    The alternative considered was proxying theourgia at request time, which
    would mean the app's isopsephy stops working whenever theourgia is down —
    a strange way for one of her projects to break another.
    """
    sync = ROOT / "scripts" / "sync-packs.sh"
    assert sync.is_file()
    body = sync.read_text(encoding="utf-8")
    assert "sha256sum" in body, "copied bytes must be checkable"
    assert "SHA256SUMS" in body


def test_the_index_reads_the_manifest_rather_than_a_list() -> None:
    """A list kept beside the files is a second place for a version to be
    wrong. The sizes come from the files themselves for the same reason."""
    route = (BACKEND / "api" / "routes" / "packs.py").read_text(
        encoding="utf-8"
    )
    assert "manifest.json" in route
    assert "path.stat().st_size" in route
