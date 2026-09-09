# SPDX-License-Identifier: AGPL-3.0-only
"""
The language packs, listed.

Isopsephy needs two things per language: the letter values, and a corpus of
words to find matches in. Those are theourgia's packs, in its `.mbf` format,
and they are reused rather than reinvented — a second copy of the Greek
Milesian table is a second place for it to be wrong.

**Why they are served rather than shipped.** The letter values are tiny — four
to nine kilobytes — but the corpora are not: Greek is 4.3MB and Arabic 2MB, and
most people want one language rather than five. Bundling all of them would put
seven megabytes into an app most of which nobody opens.

The second reason is the one with no way around it: the packs are All Rights
Reserved and the app is AGPL with a public repository. They cannot live in it.
Serving them at runtime is what keeps the code free and the corpora hers.

The FILES are served by Caddy straight from disk at `/packs/*` — this route
only says what is there, because a client needs to know the sizes before it
asks somebody to spend them.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/packs", tags=["packs"])

PACKS = Path("/app/packs")


def _describe(path: Path) -> dict | None:
    """What a chooser needs, read out of the container itself.

    Out of the manifest rather than out of a list kept beside it: a list is a
    second place for the version to disagree with the file.
    """
    try:
        with zipfile.ZipFile(path) as z:
            manifest = json.loads(z.read("manifest.json"))
    except (zipfile.BadZipFile, KeyError, json.JSONDecodeError, OSError):
        return None

    payloads = manifest.get("payloads") or []
    return {
        "file": path.name,
        "url": f"/packs/{path.name}",
        "name": manifest.get("name") or path.stem,
        "description": manifest.get("description") or "",
        "version": manifest.get("version") or "",
        # What the pack IS, which is how a chooser groups them: the letter
        # values for a script, or a corpus of words in it.
        "kinds": sorted({p.get("kind", "") for p in payloads if p.get("kind")}),
        "bytes": path.stat().st_size,
        "license": (manifest.get("license") or {}).get("spdx", ""),
    }


@router.get("")
async def list_packs() -> dict:
    """Every pack on offer, with its size.

    The size is the point of this endpoint. A phone about to spend four
    megabytes of somebody's data should say so first, and it cannot say so
    from a filename.
    """
    if not PACKS.is_dir():
        return {"packs": []}
    found = [_describe(p) for p in sorted(PACKS.glob("*.mbf"))]
    return {"packs": [f for f in found if f]}
