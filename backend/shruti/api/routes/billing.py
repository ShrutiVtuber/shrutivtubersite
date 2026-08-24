# SPDX-License-Identifier: AGPL-3.0-only
"""
Stripe — subscriptions and one-off gifts.

**Card details never touch this server.** Paying happens on Stripe's hosted
Checkout; managing or cancelling happens on Stripe's hosted Customer Portal.
That keeps the site outside PCI scope entirely, gets Apple Pay and Google Pay
for nothing, and means the one-click cancellation is a page Stripe maintains
rather than one I have to keep correct.

**The displayed price is read back FROM Stripe.** A price written into the page
and a price configured in the dashboard drift the moment one of them changes,
and the direction that drift breaks in — charging more than the page said — is
the one that must never happen. So the page asks Stripe what the tier costs.

**Nothing is trusted from the browser.** The amount, the price and the mode all
come from configuration or from Stripe; the client sends only which tier it
wants. A checkout whose amount came from the client is a checkout someone can
set to one cent.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core.config import get_settings
from shruti.core.db import get_session
from shruti.models.accounts import Supporter, User

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/billing", tags=["billing"])

# The tiers the site offers, mapped to the settings that name their Stripe
# price. Adding a tier means adding a price ID, not editing a template.
TIERS = {
    "lamplighter": "stripe_price_lamplighter",
    "almanac": "stripe_price_almanac",
}

# One-off gifts, in cents. The floor is Stripe's own minimum charge for EUR;
# below it the payment is refused by Stripe with a message the visitor cannot
# act on, so it is refused here with one they can.
ONE_OFF_MIN = 200
ONE_OFF_MAX = 50_000
ONE_OFF_DEFAULT = 300


def _client() -> Any:
    s = get_settings()
    if not s.stripe_secret_key:
        raise HTTPException(503, "support is not set up yet")
    stripe.api_key = s.stripe_secret_key
    return stripe


def _price_id(tier: str) -> str:
    s = get_settings()
    field = TIERS.get(tier)
    if not field:
        raise HTTPException(404, "no such tier")
    price = getattr(s, field, "")
    if not price:
        raise HTTPException(503, "that tier is not set up yet")
    return price


def _site_url() -> str:
    return (get_settings().site_url or "http://localhost:8200").rstrip("/")


# ── what the page shows ─────────────────────────────────────────────────────

@router.get("/tiers")
async def tiers() -> dict:
    """
    The tiers, priced by Stripe.

    Returns `configured: false` rather than an error when Stripe is not set up:
    the support page has a designed state for that, and a 503 would make the
    whole page look broken when only the buttons are missing.
    """
    s = get_settings()
    if not s.stripe_secret_key:
        return {"configured": False, "tiers": [], "oneOff": None}

    client = _client()
    out = []
    for name, field in TIERS.items():
        price_id = getattr(s, field, "")
        if not price_id:
            continue
        try:
            price = client.Price.retrieve(price_id)
        except Exception as exc:                   # noqa: BLE001
            # One misconfigured price must not take the other tier with it.
            log.warning("stripe price %s could not be read: %s", name, type(exc).__name__)
            continue
        out.append({
            "tier": name,
            "amount": price.get("unit_amount"),
            "currency": (price.get("currency") or "eur").upper(),
            "interval": (price.get("recurring") or {}).get("interval", ""),
        })

    return {
        "configured": True,
        "tiers": out,
        "oneOff": {"min": ONE_OFF_MIN, "max": ONE_OFF_MAX, "default": ONE_OFF_DEFAULT,
                   "currency": "EUR"},
    }


# ── starting a checkout ─────────────────────────────────────────────────────

def _line_items(tier: str, amount: int | None) -> dict[str, Any]:
    """
    What is actually being bought, and for how much.

    Extracted from the route so the rule it enforces can be tested rather than
    read: **`amount` is reachable only on the one-off path.** A subscription's
    price comes from `_price_id` and from nowhere else, so no edit to the form,
    the client, or this signature can make a subscriber pay what their browser
    said they should.
    """
    if tier == "one-off":
        cents = amount or ONE_OFF_DEFAULT
        if not ONE_OFF_MIN <= cents <= ONE_OFF_MAX:
            raise HTTPException(
                422,
                f"a one-off gift has to be between "
                f"€{ONE_OFF_MIN / 100:.2f} and €{ONE_OFF_MAX / 100:.0f}",
            )
        return {
            "mode": "payment",
            "line_items": [{
                "quantity": 1,
                "price_data": {
                    "currency": "eur",
                    "unit_amount": cents,
                    "product_data": {"name": "A one-off gift"},
                },
            }],
        }

    # `amount` is deliberately not consulted here, whatever it holds.
    return {
        "mode": "subscription",
        "line_items": [{"price": _price_id(tier), "quantity": 1}],
        "subscription_data": {"metadata": {"tier": tier}},
    }


class CheckoutIn(BaseModel):
    """The client picks a tier, never an amount — except for a one-off, where
    the amount is the whole point and is clamped server-side."""
    tier: str = Field(default="one-off")
    amount: int | None = None                      # cents, one-off only
    email: EmailStr | None = None


@router.post("/checkout")
async def checkout(
    body: CheckoutIn, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    from shruti.api.routes.accounts import current_user

    client = _client()
    user = await current_user(request, session)
    email = (user.email if user else None) or (str(body.email) if body.email else None)

    common: dict[str, Any] = {
        "success_url": f"{_site_url()}/support/thanks?session={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{_site_url()}/support",
        # Stripe collects the address it needs for tax; asking for more than
        # that on a gift is how a gift stops being given.
        "billing_address_collection": "auto",
        "allow_promotion_codes": False,
    }
    if email:
        common["customer_email"] = email
    if user:
        # Survives the redirect, so the webhook can attach the payment to an
        # account without trusting anything the browser sends back.
        common["client_reference_id"] = str(user.id)

    params = {**common, **_line_items(body.tier, body.amount)}

    try:
        checkout_session = client.checkout.Session.create(**params)
    except Exception as exc:                       # noqa: BLE001
        log.warning("stripe checkout could not be created: %s", type(exc).__name__)
        raise HTTPException(502, "that could not be started — try again in a moment")

    return {"url": checkout_session.url}


# ── managing or cancelling one ──────────────────────────────────────────────

def _portal_configuration(client: Any) -> str:
    """
    The Customer Portal's settings, created here rather than clicked into the
    Stripe dashboard.

    Two reasons. Stripe refuses to open a portal at all until a configuration
    exists, so leaving it to a dashboard visit means the cancel button works on
    the developer's account and 500s on hers. And the cancellation policy is a
    promise the site makes in words — *it stops at the end of the month you
    have already paid for* — which belongs where it can be reviewed next to
    that sentence, not in a checkbox nobody will look at again.

    **No cancellation survey.** Stripe offers one, and asking why on the way
    out is the standard way to make a cancellation not-one-click. The promise
    was one click.
    """
    existing = client.billing_portal.Configuration.list(limit=1, active=True)
    if existing.data:
        return existing.data[0].id

    site = _site_url()
    created = client.billing_portal.Configuration.create(
        business_profile={
            "headline": "Shruti — support the work",
            "privacy_policy_url": f"{site}/privacy",
            "terms_of_service_url": f"{site}/terms",
        },
        default_return_url=f"{site}/account",
        features={
            "subscription_cancel": {
                "enabled": True,
                # Not immediately: they paid for this month.
                "mode": "at_period_end",
                "proration_behavior": "none",
                # Deliberately absent: cancellation_reason.
            },
            "payment_method_update": {"enabled": True},
            "invoice_history": {"enabled": True},
            "customer_update": {
                "enabled": True,
                "allowed_updates": ["email", "address", "name"],
            },
        },
    )
    log.info("created the Stripe customer portal configuration")
    return created.id


@router.post("/portal")
async def portal(
    request: Request, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    A link into Stripe's Customer Portal.

    **This is the one-click cancellation.** Cancelling is one button on a page
    Stripe maintains, it takes effect at the end of the paid period rather than
    stripping access mid-month, and it needs no email to anybody. Building this
    screen here would mean maintaining a worse copy of it.
    """
    from shruti.api.routes.accounts import current_user

    client = _client()
    user = await current_user(request, session)
    if user is None:
        raise HTTPException(401, "sign in first")

    row = (
        await session.execute(
            select(Supporter).where(Supporter.user_id == user.id)
        )
    ).scalars().first()
    if row is None or not row.stripe_customer_id:
        raise HTTPException(404, "there is no subscription on this account")

    try:
        portal_session = client.billing_portal.Session.create(
            customer=row.stripe_customer_id,
            configuration=_portal_configuration(client),
            return_url=f"{_site_url()}/account",
        )
    except Exception as exc:                       # noqa: BLE001
        log.warning("stripe portal could not be created: %s", type(exc).__name__)
        raise HTTPException(502, "that could not be opened — try again in a moment")

    return {"url": portal_session.url}


@router.get("/me")
async def my_support(
    request: Request, session: AsyncSession = Depends(get_session)
) -> dict:
    """What the account page shows. Quiet when there is nothing."""
    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    if user is None:
        raise HTTPException(401, "sign in first")

    row = (
        await session.execute(
            select(Supporter).where(Supporter.user_id == user.id)
        )
    ).scalars().first()
    if row is None or not row.stripe_subscription_id:
        return {"supporting": False}

    return {
        "supporting": row.status in {"active", "trialing", "past_due"},
        "status": row.status,
        "tier": row.tier,
        "cancelAtPeriodEnd": row.cancel_at_period_end,
        "currentPeriodEnd": (
            row.current_period_end.isoformat() if row.current_period_end else None
        ),
        "canManage": bool(row.stripe_customer_id),
    }


# ── what Stripe tells us afterwards ─────────────────────────────────────────

def _moment(value: int | None) -> datetime | None:
    return datetime.fromtimestamp(value, tz=timezone.utc) if value else None


async def _upsert(
    session: AsyncSession, *, customer_id: str, subscription: dict | None,
    email: str = "", user_id: int | None = None,
) -> None:
    """One row per Stripe customer. Found by customer id, then by account, then
    by email — in that order, because the ids are exact and the email is not."""
    row = (
        await session.execute(
            select(Supporter).where(Supporter.stripe_customer_id == customer_id)
        )
    ).scalars().first()

    if row is None and user_id is not None:
        row = (
            await session.execute(select(Supporter).where(Supporter.user_id == user_id))
        ).scalars().first()
    if row is None and email:
        row = (
            await session.execute(select(Supporter).where(Supporter.email == email))
        ).scalars().first()

    if row is None:
        row = Supporter()
        session.add(row)

    row.stripe_customer_id = customer_id or row.stripe_customer_id
    if user_id is not None:
        row.user_id = user_id
    if email:
        row.email = email

    if subscription is not None:
        row.stripe_subscription_id = subscription.get("id", "")
        row.status = subscription.get("status", "")
        row.cancel_at_period_end = bool(subscription.get("cancel_at_period_end"))
        row.current_period_end = _moment(subscription.get("current_period_end"))
        tier = (subscription.get("metadata") or {}).get("tier", "")
        if tier:
            row.tier = tier


@router.post("/webhook", include_in_schema=False)
async def webhook(
    request: Request,
    stripe_signature: str = Header(default="", alias="Stripe-Signature"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Stripe's account of what happened, which is the only account that counts.

    **The signature is checked before anything else, and a missing signing
    secret refuses everything.** An unverified webhook endpoint is a public API
    for inventing subscriptions — anyone who knows the URL could grant
    themselves a tier. Failing closed when unconfigured is the only safe
    default, even though it means the endpoint does nothing until the secret is
    set.
    """
    s = get_settings()
    if not (s.stripe_secret_key and s.stripe_webhook_secret):
        raise HTTPException(503, "billing is not set up")

    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, s.stripe_webhook_secret
        )
    except Exception as exc:                       # noqa: BLE001
        # Never echo why. A precise error is a hint for forging the next one.
        log.warning("stripe webhook rejected: %s", type(exc).__name__)
        raise HTTPException(400, "that could not be verified")

    kind = event["type"]
    obj = event["data"]["object"]
    stripe.api_key = s.stripe_secret_key

    if kind == "checkout.session.completed":
        customer_id = obj.get("customer") or ""
        reference = obj.get("client_reference_id")
        email = (obj.get("customer_details") or {}).get("email", "") or ""
        subscription = None
        if obj.get("mode") == "subscription" and obj.get("subscription"):
            try:
                subscription = stripe.Subscription.retrieve(obj["subscription"])
            except Exception as exc:               # noqa: BLE001
                log.warning("subscription could not be read: %s", type(exc).__name__)

        # A one-off leaves no customer to remember and nothing to manage, so it
        # is recorded only when Stripe made a customer for it.
        if customer_id:
            user_id = int(reference) if reference and reference.isdigit() else None
            if user_id is not None:
                exists = (
                    await session.execute(select(User).where(User.id == user_id))
                ).scalar_one_or_none()
                if exists is None:
                    user_id = None
            await _upsert(
                session, customer_id=customer_id,
                subscription=dict(subscription) if subscription else None,
                email=email, user_id=user_id,
            )
            await session.commit()

    elif kind in {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:
        customer_id = obj.get("customer") or ""
        if customer_id:
            await _upsert(session, customer_id=customer_id, subscription=dict(obj))
            await session.commit()

    # Everything else is acknowledged and ignored. Returning 200 for an event
    # we do not handle is correct: a 4xx makes Stripe retry it for days.
    return {"received": True}
