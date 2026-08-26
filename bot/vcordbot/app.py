# SPDX-License-Identifier: AGPL-3.0-only
"""
The web service Discord talks to.

A thin adapter and nothing else: verify the signature, hand the payload to
`dispatch`, return what it gives back. Every decision worth testing lives in
`dispatch`, which knows nothing about HTTP.

**Signature verification is not optional and cannot be "improved" later.** The
endpoint is a public URL that anybody can POST to. Without the check, a
stranger can make this bot say anything, in any server it is in, by sending a
made-up interaction — and Discord will not be involved at all. Discord also
refuses to save an endpoint that does not answer its signed PING correctly, so
getting this wrong fails closed rather than silently.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import FastAPI, Header, HTTPException, Request

from vcordbot import config
from vcordbot.astro import Astro
from vcordbot.dispatch import dispatch

log = logging.getLogger("vcordbot")

CFG = config.load()
app = FastAPI(title="vcordbot", docs_url=None, redoc_url=None, openapi_url=None)


def _verifier() -> Ed25519PublicKey | None:
    if not CFG.public_key:
        return None
    try:
        return Ed25519PublicKey.from_public_bytes(bytes.fromhex(CFG.public_key))
    except ValueError:
        log.error("the configured public key is not valid hex; refusing everything")
        return None


VERIFIER = _verifier()


@app.get("/health")
async def health() -> dict:
    """No secrets, no counts, nothing about who uses it."""
    return {"ok": True, "app": CFG.app_id or None, "verifying": VERIFIER is not None}


@app.post("/interactions")
async def interactions(
    request: Request,
    x_signature_ed25519: str = Header(default=""),
    x_signature_timestamp: str = Header(default=""),
) -> dict:
    body = await request.body()

    # Fail CLOSED. A missing key means we cannot tell Discord from anyone else,
    # and the safe reading of "cannot tell" is "do not answer".
    if VERIFIER is None:
        raise HTTPException(503, "not configured")
    if not x_signature_ed25519 or not x_signature_timestamp:
        raise HTTPException(401, "invalid request signature")

    try:
        VERIFIER.verify(bytes.fromhex(x_signature_ed25519),
                        x_signature_timestamp.encode() + body)
    except (InvalidSignature, ValueError):
        # 401 with exactly Discord's expected wording. Nothing about WHY —
        # a probe learns only that it failed.
        raise HTTPException(401, "invalid request signature")

    payload = await request.json()
    return await dispatch(
        payload,
        Astro(CFG.astro_url),
        bot_url=CFG.bot_url,
        site_url=CFG.site_url,
        now_iso=datetime.now(timezone.utc).isoformat(),
    )
