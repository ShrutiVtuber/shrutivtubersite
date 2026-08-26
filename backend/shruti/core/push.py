# SPDX-License-Identifier: AGPL-3.0-only
"""
Web Push, without a payload and without a new dependency.

**Nothing is sent in the push itself.** The message body is empty; the service
worker wakes, asks this site what the notice says, and shows it. That is a
deliberate choice and it buys three things:

  - **No encryption to get wrong.** A push carrying a payload has to be
    encrypted with aes128gcm against a key the browser generated, and getting
    that subtly wrong produces notifications that silently never arrive. The
    empty push needs none of it.
  - **No dependency.** VAPID is an ES256 JWT, and pyjwt[crypto] is already
    here for sessions. `pywebpush` would pull in http-ece for the part we are
    not doing.
  - **Nothing readable in transit.** Mozilla and Google run the push services.
    An empty push tells them a notification happened; it does not tell them
    what it said.

The cost is one extra request per notification, from the reader's browser to
this site, at the moment they are notified. That is a fair trade and it keeps
the content on the site that wrote it.
"""
from __future__ import annotations

import base64
import json
import logging
import time
from urllib.parse import urlparse

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from shruti.core.config import get_settings

log = logging.getLogger(__name__)

# Twelve hours. A "she is live" notice that arrives the next morning is worse
# than one that never arrives — it sends somebody to a stream that ended.
TTL_SECONDS = 12 * 60 * 60

# VAPID JWTs must not outlive 24h by spec; an hour is plenty and keeps a
# stolen header useless quickly.
CLAIM_SECONDS = 60 * 60


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def generate_keys() -> tuple[str, str]:
    """
    A fresh VAPID pair, for `scripts/vapid-keys.py`.

    Returns `(private, public)`, both base64url. **Changing these invalidates
    every existing subscription** — browsers bind a subscription to the key it
    was created with — so they are generated once and kept.
    """
    key = ec.generate_private_key(ec.SECP256R1())
    private = key.private_numbers().private_value.to_bytes(32, "big")
    public = key.public_key().public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.UncompressedPoint,
    )
    return _b64(private), _b64(public)


def _private_key():
    raw = get_settings().vapid_private_key
    if not raw:
        return None
    padded = raw + "=" * (-len(raw) % 4)
    value = int.from_bytes(base64.urlsafe_b64decode(padded), "big")
    return ec.derive_private_key(value, ec.SECP256R1())


def configured() -> bool:
    s = get_settings()
    return bool(s.vapid_private_key and s.vapid_public_key and s.vapid_subject)


def _authorization(endpoint: str) -> str:
    """The `vapid` header for one push service, valid for an hour."""
    s = get_settings()
    origin = urlparse(endpoint)
    token = jwt.encode(
        {
            "aud": f"{origin.scheme}://{origin.netloc}",
            "exp": int(time.time()) + CLAIM_SECONDS,
            "sub": s.vapid_subject,
        },
        _private_key(),
        algorithm="ES256",
    )
    return f"vapid t={token}, k={s.vapid_public_key}"


async def push_one(endpoint: str) -> tuple[bool, int]:
    """
    Wake one browser. Returns `(delivered, status)`.

    **404 and 410 mean the subscription is dead** — the browser was
    uninstalled, the permission revoked, the profile deleted — and the caller
    is expected to delete the row. A push service that keeps being asked to
    deliver to a gone endpoint starts rate-limiting the sender, so this is
    housekeeping with consequences rather than tidiness.
    """
    if not configured():
        return False, 0
    import httpx

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                endpoint,
                headers={
                    "Authorization": _authorization(endpoint),
                    "TTL": str(TTL_SECONDS),
                    # No body, so no Content-Encoding and no payload key.
                    "Content-Length": "0",
                },
            )
        return r.status_code in (200, 201, 202), r.status_code
    except Exception:                                  # noqa: BLE001
        log.info("a push could not be delivered")
        return False, 0


def notice_payload(kind: str, title: str, body: str, url: str) -> str:
    """What the service worker fetches after being woken. Small on purpose."""
    return json.dumps({"kind": kind, "title": title, "body": body, "url": url})
