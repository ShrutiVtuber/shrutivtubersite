# SPDX-License-Identifier: AGPL-3.0-only
"""
Twitch: her authorisation, and the deliveries that follow.

Three surfaces, and only one of them is public.

`/api/twitch/eventsub` is where Twitch posts. It is a public URL that moves a
goal bar, so nothing reaches the recorder before the signature is checked.

`/admin/twitch/callback` receives her authorisation once. It holds HER token
for HER channel — which is the ordinary case, and quite unlike holding other
people's, which is why multi-tenant sync was dropped.

`/api/twitch/admin/subscribe` asks Twitch to start sending. Admin only.
"""
from __future__ import annotations

import logging
import os
import secrets
import urllib.parse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from shruti.api.deps import require_admin
from shruti.core import counters, settings_store
from shruti.core.db import get_session
from shruti.models import SupportEvent
from sqlmodel import select
from shruti.core.twitch_events import (NOTIFICATION, REVOCATION, SUBSCRIPTIONS,
                                       TYPE, VERIFICATION, to_event, verify)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/twitch", tags=["twitch"])

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
EVENTSUB_URL = "https://api.twitch.tv/helix/eventsub/subscriptions"

# Settings keys. The token is hers and lives in the database rather than the
# environment, because it is refreshed on a schedule and an environment
# variable cannot be written back.
K_SECRET = "twitch.eventsub_secret"
K_ACCESS = "twitch.access_token"
K_REFRESH = "twitch.refresh_token"
K_BROADCASTER = "twitch.broadcaster_id"
K_STATE = "twitch.oauth_state"


def _cid() -> str:
    return os.environ.get("SHRUTI_TWITCH_CLIENT_ID", "").strip()


def _secret() -> str:
    return os.environ.get("SHRUTI_TWITCH_CLIENT_SECRET", "").strip()


async def _eventsub_secret(session: AsyncSession) -> str:
    """
    The shared secret Twitch signs with. Generated once and then never changed
    casually — changing it silently invalidates every existing subscription's
    signature, and the failure looks like Twitch having gone quiet.
    """
    have = await settings_store.get_many(session, [K_SECRET])
    if have.get(K_SECRET):
        return have[K_SECRET]
    made = secrets.token_urlsafe(32)
    await settings_store.put_many(session, {K_SECRET: made})
    return made


# ── the public endpoint ─────────────────────────────────────────────────────

@router.post("/eventsub")
async def eventsub(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Where Twitch posts. Everything here happens after the signature check.

    Three message types arrive on the same URL. The verification challenge must
    be echoed back as PLAIN TEXT — returning it as JSON is the commonest way a
    subscription never activates, and Twitch's error says only that the
    callback failed.
    """
    body = await request.body()
    secret = await _eventsub_secret(session)

    if not verify(secret, dict(request.headers), body):
        # Nothing about why. A prober learns only that it did not work.
        raise HTTPException(403, "bad signature")

    payload = await request.json()
    kind = request.headers.get(TYPE, "")

    if kind == VERIFICATION:
        return Response(content=payload.get("challenge", ""), media_type="text/plain")

    if kind == REVOCATION:
        # Twitch revokes when authorisation is withdrawn or the user is banned.
        # Worth a loud log: the first symptom otherwise is silence.
        sub = payload.get("subscription", {})
        log.warning("twitch revoked %s: %s", sub.get("type"), sub.get("status"))
        return Response(status_code=204)

    if kind != NOTIFICATION:
        return Response(status_code=204)

    sub_type = (payload.get("subscription") or {}).get("type", "")
    mapped = to_event(sub_type, payload.get("event") or {})
    if mapped is None:
        # Deliberately ignored — a gifted sub's recipient copy, or a type we do
        # not count. Not an error.
        return Response(status_code=204)

    # Twitch's own message id is the idempotency key. Deliveries are retried by
    # design, and without this a retry counts again.
    message_id = request.headers.get("twitch-eventsub-message-id", "")
    await counters.record(
        session,
        source=mapped["source"],
        external_id=message_id,
        quantity=mapped.get("quantity", 0),
        who=mapped.get("who", ""),
        message=mapped.get("message", ""),
    )
    return Response(status_code=204)


# ── her authorisation ───────────────────────────────────────────────────────

@router.get("/admin/authorize-url")
async def authorize_url(
    request: Request,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """The link she clicks once. `state` is stored and checked on return."""
    if not _cid():
        raise HTTPException(503, "no Twitch client id configured")
    state = secrets.token_urlsafe(24)
    await settings_store.put_many(session, {K_STATE: state})
    scopes = sorted({s for _t, _v, s in SUBSCRIPTIONS if s})
    site = os.environ.get("SHRUTI_SITE_URL", "https://shrutivtuber.com").rstrip("/")
    query = urllib.parse.urlencode({
        "client_id": _cid(),
        "redirect_uri": f"{site}/admin/twitch/callback",
        "response_type": "code",
        "scope": " ".join(scopes),
        "state": state,
        # So re-authorising after adding a scope actually re-prompts rather
        # than silently returning the old, narrower grant.
        "force_verify": "true",
    })
    return {"url": f"{AUTH_URL}?{query}", "scopes": scopes}


@router.post("/admin/exchange")
async def exchange(
    body: dict,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """Swap the code for tokens. Called by the callback page."""
    code, state = body.get("code", ""), body.get("state", "")
    stored = (await settings_store.get_many(session, [K_STATE])).get(K_STATE, "")
    # A mismatched state means the round trip was not the one we started.
    if not stored or state != stored:
        # Most often innocent: the page was open in two tabs and the older
        # link was used, because each render mints a fresh state. Say what to
        # do rather than only what went wrong.
        raise HTTPException(
            400,
            "That authorisation did not match. If the page was open in more "
            "than one tab, go back to Twitch settings, reload, and use the "
            "link there.")

    site = os.environ.get("SHRUTI_SITE_URL", "https://shrutivtuber.com").rstrip("/")
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(TOKEN_URL, data={
            "client_id": _cid(), "client_secret": _secret(),
            "code": code, "grant_type": "authorization_code",
            "redirect_uri": f"{site}/admin/twitch/callback"})
    if r.status_code >= 400:
        log.warning("twitch token exchange failed: %s", r.status_code)
        raise HTTPException(400, "Twitch refused that code")
    tok = r.json()

    async with httpx.AsyncClient(timeout=15) as c:
        me = await c.get("https://api.twitch.tv/helix/users", headers={
            "Client-ID": _cid(), "Authorization": f"Bearer {tok['access_token']}"})
    who = (me.json().get("data") or [{}])[0]

    await settings_store.put_many(session, {
        K_ACCESS: tok["access_token"],
        K_REFRESH: tok.get("refresh_token", ""),
        K_BROADCASTER: who.get("id", ""),
        K_STATE: "",
    })
    return {"connected": who.get("display_name", ""), "broadcaster": who.get("id", "")}


@router.post("/admin/subscribe")
async def subscribe(
    request: Request,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Ask Twitch to start sending.

    Created with an APP token, not hers — the broadcaster's grant is what makes
    the scope available, and the subscription itself belongs to the
    application. Twitch verifies the callback at this moment, which is why the
    endpoint has to be live and answering before this is called.
    """
    stored = await settings_store.get_many(session, [K_BROADCASTER])
    broadcaster = stored.get(K_BROADCASTER, "")
    if not broadcaster:
        raise HTTPException(400, "not connected to Twitch yet")

    secret = await _eventsub_secret(session)
    site = os.environ.get("SHRUTI_SITE_URL", "https://shrutivtuber.com").rstrip("/")
    callback = f"{site}/api/twitch/eventsub"

    async with httpx.AsyncClient(timeout=20) as c:
        app_token = (await c.post(TOKEN_URL, data={
            "client_id": _cid(), "client_secret": _secret(),
            "grant_type": "client_credentials"})).json()["access_token"]
        headers = {"Client-ID": _cid(), "Authorization": f"Bearer {app_token}",
                   "Content-Type": "application/json"}

        made, already, failed = [], [], []
        for kind, version, _scope in SUBSCRIPTIONS:
            condition = {"broadcaster_user_id": broadcaster}
            if kind == "channel.follow":
                # v2 wants a moderator as well, which for her own channel is
                # herself. Omitting it is a 400 that reads like a scope problem.
                condition["moderator_user_id"] = broadcaster
            if kind == "channel.raid":
                condition = {"to_broadcaster_user_id": broadcaster}

            r = await c.post(EVENTSUB_URL, headers=headers, json={
                "type": kind, "version": version, "condition": condition,
                "transport": {"method": "webhook", "callback": callback,
                              "secret": secret}})
            if r.status_code in (200, 202):
                made.append(kind)
            elif r.status_code == 409:
                already.append(kind)
            else:
                failed.append({"type": kind, "status": r.status_code,
                               "detail": r.text[:200]})

    return {"created": made, "already": already, "failed": failed}


@router.get("/admin/status")
async def status(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """What is connected, without saying anything that is a credential."""
    have = await settings_store.get_many(session, [K_ACCESS, K_BROADCASTER, K_SECRET])
    return {
        "connected": bool(have.get(K_ACCESS)),
        "broadcaster": have.get(K_BROADCASTER, ""),
        "secretSet": bool(have.get(K_SECRET)),
    }


@router.get("/admin/recent")
async def recent(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    """
    The last events that arrived, from any source.

    Not filtered to Twitch: when something has not shown up, the useful
    question is "did anything arrive at all", and a list that hides Stripe
    answers it wrongly.
    """
    rows = (
        await session.execute(
            select(SupportEvent).order_by(SupportEvent.occurred_at.desc()).limit(25)
        )
    ).scalars().all()
    return [{
        "id": e.id, "source": e.source, "who": e.who,
        "amountMinor": e.amount_minor, "currency": e.currency,
        "quantity": e.quantity, "message": e.message,
        "messageApproved": e.message_approved,
        "at": e.occurred_at.isoformat() if e.occurred_at else "",
    } for e in rows]


class TestIn(BaseModel):
    source: str = Field(default="twitch.bits", max_length=40)
    quantity: int = Field(default=100, ge=0, le=1_000_000)
    amount_minor: int = Field(default=0, ge=0, le=1_000_000)
    who: str = Field(default="A test", max_length=120)


@router.post("/admin/test")
async def test_event(
    body: TestIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Record a pretend event, so counters and overlays can be seen working
    without waiting for somebody to actually cheer.

    It is a real row in the real table — which is the point, and also why it is
    marked plainly so it can be found and deleted afterwards.
    """
    ok = await counters.record(
        session, source=body.source, external_id="",
        amount_minor=body.amount_minor, quantity=body.quantity,
        who=body.who or "A test",
        message="(a test event)",
    )
    return {"recorded": ok}


@router.delete("/admin/tests")
async def clear_tests(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """Remove the pretend ones, and only those."""
    from sqlmodel import delete as sqldelete

    result = await session.execute(
        sqldelete(SupportEvent).where(SupportEvent.message == "(a test event)"))
    await session.commit()
    return {"removed": result.rowcount}


@router.get("/admin/subscriptions")
async def subscriptions(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    What Twitch currently holds — asked of Twitch, not of us.

    The page used to report only what the last press did, which answers the
    wrong question. "Did it work?" is about the state now, and a press that
    succeeded looked identical to one that did nothing. Asking the source means
    the page is right even after a restart, a redeploy, or somebody revoking
    the authorisation from their Twitch settings.
    """
    if not _cid():
        return {"configured": False, "subscriptions": []}
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            tok = (await c.post(TOKEN_URL, data={
                "client_id": _cid(), "client_secret": _secret(),
                "grant_type": "client_credentials"})).json()["access_token"]
            r = await c.get(EVENTSUB_URL, headers={
                "Client-ID": _cid(), "Authorization": f"Bearer {tok}"})
            body = r.json()
    except Exception as exc:                        # noqa: BLE001
        log.warning("could not list eventsub subscriptions: %s", type(exc).__name__)
        return {"configured": True, "unreachable": True, "subscriptions": []}

    rows = [{
        "type": e.get("type", ""),
        # "enabled" is the only good one. Anything else — especially
        # `webhook_callback_verification_failed` — means it is not listening,
        # and that reads as silence rather than as an error.
        "status": e.get("status", ""),
        "callback": ((e.get("transport") or {}).get("callback") or ""),
    } for e in body.get("data", [])]
    return {"configured": True, "subscriptions": rows,
            "total": body.get("total", len(rows))}
