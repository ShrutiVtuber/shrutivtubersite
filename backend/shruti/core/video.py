# SPDX-License-Identifier: AGPL-3.0-only
"""
Where a lesson's video actually plays from.

**Two providers, on purpose.** Courses start on Bunny because at thirty euros
Cloudflare would take a quarter of the sale, and move to Cloudflare when a
course is worth a hundred and fifty and one provider matters more than the
money. That is a planned migration, so both are live at once and a course can
move one lesson at a time.

Everything provider-shaped lives here. A lesson knows a provider and an id and
nothing else, and the player is handed a URL and a kind.

**Playback is signed where the provider allows it.** A paid course served from
a guessable URL is a paid course anybody can have, which is the same failure as
an unlisted video and the reason not to use one.
"""
from __future__ import annotations

import hashlib
import logging
import time

from shruti.core.config import get_settings

log = logging.getLogger(__name__)

# How long a playback URL stays good.
#
# Four hours: long enough to watch a ninety-minute lecture twice with breaks,
# short enough that a link somebody passes on is dead before it has travelled
# far. It is not what limits anybody's access — a fresh one is minted every
# time a lesson is opened, so a student who bought a class in 2026 gets a
# working video in 2030 by the same route they always did.
#
# The one cost of a short life is a tab left open past it, where the token is
# stale by the time somebody presses play. The reader re-fetches on a playback
# failure rather than showing an error, so that is invisible.
TOKEN_LIFE_SECONDS = 4 * 60 * 60


def playback(provider: str, video_id: str, life_seconds: int = TOKEN_LIFE_SECONDS) -> dict:
    """
    What the player needs: a source, its kind, and when it stops working.

    An unknown or unconfigured provider returns `ready: false` with a reason
    rather than a broken URL — a player showing nothing and saying nothing is
    the worst version of this.
    """
    if not video_id:
        return {"ready": False, "reason": "no video on this lesson yet"}

    if provider == "bunny":
        return _bunny(video_id, life_seconds)
    if provider == "cloudflare":
        return _cloudflare(video_id, life_seconds)
    return {"ready": False, "reason": f"unknown video provider {provider!r}"}


def _bunny(video_id: str, life_seconds: int) -> dict:
    """
    A Bunny Stream embed, signed if a token key is configured.

    Their token is a SHA-256 of the key, the path and the expiry — documented
    under Token Authentication. Without the key the embed still plays, so this
    degrades to working-but-unprotected rather than to broken; it says so, and
    the admin surfaces that rather than leaving it quietly open.
    """
    s = get_settings()
    library = s.bunny_library_id
    if not library:
        return {"ready": False, "reason": "Bunny is not set up yet"}

    expires = int(time.time()) + life_seconds
    src = f"https://iframe.mediadelivery.net/embed/{library}/{video_id}"

    key = s.bunny_token_auth_key
    if not key:
        return {
            "ready": True, "kind": "iframe", "src": src, "expiresAt": None,
            # Said out loud rather than assumed: this URL does not expire.
            "unprotected": True,
        }

    token = hashlib.sha256(f"{key}{video_id}{expires}".encode()).hexdigest()
    return {
        "ready": True,
        "kind": "iframe",
        "src": f"{src}?token={token}&expires={expires}",
        "expiresAt": expires,
        "unprotected": False,
    }


def _cloudflare(video_id: str, life_seconds: int) -> dict:
    """
    Cloudflare Stream, for when courses are worth enough to move.

    Their signed playback needs a signing key created through the API, which is
    a thing to set up on the day rather than a thing to half-build now. The
    unsigned embed works and says that it is unsigned.

    **With no domain configured this refuses**, rather than pointing a player at
    a made-up host. It used to fall back to "customer-placeholder…", which is a
    real-looking URL that resolves to nothing: a paid lesson would have shown an
    empty player with no explanation, and the admin had no way to tell that from
    a video still encoding.
    """
    s = get_settings()
    if not s.cloudflare_stream_domain:
        return {
            "ready": False,
            "reason": "Cloudflare Stream is not set up — no stream domain is configured",
        }
    return {
        "ready": True,
        "kind": "iframe",
        "src": f"https://{s.cloudflare_stream_domain}/{video_id}/iframe",
        "expiresAt": None,
        "unprotected": True,
    }


def upload_target(provider: str) -> dict:
    """
    Where the admin sends a file, and whether it can.

    Uploading is done from the admin against the provider directly rather than
    through this box: thirty hours of lecture has no business travelling
    through a server that only needs to know an id afterwards.
    """
    s = get_settings()
    if provider == "bunny":
        if not (s.bunny_library_id and s.bunny_stream_api_key):
            return {"ready": False, "reason": "Bunny is not set up yet"}
        return {
            "ready": True,
            "library": s.bunny_library_id,
            "endpoint": f"https://video.bunnycdn.com/library/{s.bunny_library_id}/videos",
        }
    return {"ready": False, "reason": f"cannot upload to {provider!r} yet"}


def providers() -> list[dict]:
    """
    The video providers that are actually set up, for the admin to choose from.

    Offering an unconfigured provider in a dropdown is how somebody picks it,
    saves a lesson, and finds out weeks later that the player has been empty —
    the option looked exactly as real as the working one.

    `protected` is not decoration: a course sold for money that plays without a
    signed URL is a course anybody can hotlink, and she should see which is
    which before choosing.
    """
    s = get_settings()
    out: list[dict] = []
    if s.bunny_library_id and s.bunny_stream_api_key:
        out.append({
            "key": "bunny",
            "label": "Bunny Stream",
            "protected": bool(s.bunny_token_auth_key),
            "uploads": True,
        })
    if s.cloudflare_stream_domain:
        out.append({
            "key": "cloudflare",
            "label": "Cloudflare Stream",
            # Signed playback is not built; the embed is open by design and
            # says so rather than implying protection it does not have.
            "protected": False,
            "uploads": False,
        })
    return out
