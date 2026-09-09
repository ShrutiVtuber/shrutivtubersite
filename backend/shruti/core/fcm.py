# SPDX-License-Identifier: AGPL-3.0-only
"""
Sending a notification to a phone, through Firebase.

⚠ **Unconfigured is a working state, not an error.** Without a service account
this sends nothing and says so once — the app still works, every instrument on
it still computes, and nobody sees a crash because she has not set up Firebase
yet. The alternative is a site that 500s on publishing a horoscope because a
Google credential is missing.

FCM HTTP v1 wants an OAuth2 access token signed with the service account's key,
not the legacy server key. The token lasts an hour and is cached for slightly
less than that, because minting one per notification would be a JWT signature
and a round trip for every phone.
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

log = logging.getLogger(__name__)

_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"
_TOKEN_URL = "https://oauth2.googleapis.com/token"

# The access token and when it stops being usable.
_cached: tuple[str, float] | None = None
_said_unconfigured = False


def _service_account() -> dict[str, Any] | None:
    """
    The credential, from a path or from the variable itself.

    Both, because a file is what Google hands you and an environment variable is
    what a container wants.
    """
    raw = os.environ.get("SHRUTI_FCM_SERVICE_ACCOUNT", "").strip()
    if not raw:
        return None
    try:
        if raw.startswith("{"):
            return json.loads(raw)
        with open(raw, encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:                       # noqa: BLE001
        log.warning("the FCM service account could not be read: %s",
                    type(exc).__name__)
        return None


def configured() -> bool:
    return _service_account() is not None


async def _access_token() -> str | None:
    """A Google access token, minted from the service account and cached."""
    global _cached
    if _cached and _cached[1] > time.time():
        return _cached[0]

    account = _service_account()
    if account is None:
        return None

    import httpx
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    import base64

    def b64(raw: bytes) -> bytes:
        return base64.urlsafe_b64encode(raw).rstrip(b"=")

    now = int(time.time())
    header = b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = b64(json.dumps({
        "iss": account["client_email"],
        "scope": _SCOPE,
        "aud": _TOKEN_URL,
        "iat": now,
        "exp": now + 3600,
    }).encode())
    signing_input = header + b"." + claims

    key = serialization.load_pem_private_key(
        account["private_key"].encode(), password=None)
    signature = key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    assertion = (signing_input + b"." + b64(signature)).decode()

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(_TOKEN_URL, data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": assertion,
            })
        if r.status_code != 200:
            log.warning("google refused the service account (%d)", r.status_code)
            return None
        body = r.json()
    except Exception as exc:                       # noqa: BLE001
        log.warning("could not mint an FCM token: %s", type(exc).__name__)
        return None

    token = body.get("access_token", "")
    # A minute short of the hour, so a send never races the expiry.
    _cached = (token, time.time() + int(body.get("expires_in", 3600)) - 60)
    return token or None


def message(token: str, *, title: str, body: str, url: str) -> dict:
    """
    One FCM message.

    ⚠ Both a notification AND data. The notification is what Android draws when
    the app is in the background; the data is what the app reads when it is in
    the foreground, and what carries where to go when it is tapped.
    """
    return {
        "message": {
            "token": token,
            "notification": {"title": title, "body": body},
            "data": {"url": url},
            "android": {"priority": "high"},
            "apns": {"payload": {"aps": {"sound": "default"}}},
        }
    }


async def send(token: str, *, title: str, body: str,
               url: str) -> tuple[bool, bool]:
    """
    Send one. Returns `(delivered, the token is dead)`.

    ⚠ The second half matters as much as the first. FCM answers UNREGISTERED
    for a token belonging to an app that was uninstalled, and a sender that
    keeps asking about those gets rate-limited — so the caller deletes the row
    rather than counting another failure.
    """
    global _said_unconfigured
    account = _service_account()
    if account is None:
        if not _said_unconfigured:
            _said_unconfigured = True
            log.info("notifications are not configured; nothing is being sent")
        return False, False

    access = await _access_token()
    if access is None:
        return False, False

    import httpx

    project = account.get("project_id", "")
    endpoint = f"https://fcm.googleapis.com/v1/projects/{project}/messages:send"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                endpoint,
                headers={"Authorization": f"Bearer {access}"},
                json=message(token, title=title, body=body, url=url),
            )
    except Exception:                              # noqa: BLE001
        return False, False

    if r.status_code in (200, 201):
        return True, False
    # 404 is a gone token; 400 with UNREGISTERED says so in words.
    dead = r.status_code == 404 or "UNREGISTERED" in r.text.upper()
    if not dead:
        log.info("fcm refused a message (%d)", r.status_code)
    return False, dead
