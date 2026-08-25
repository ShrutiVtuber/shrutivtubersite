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
from urllib.parse import urlparse

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core import emails
from shruti.core.config import get_settings
from shruti.api.deps import require_admin
from shruti.core.db import get_session
from shruti.core.mail import send
from shruti.core.origins import resolve as resolve_origin
from shruti.core.settings_store import imprint as imprint_settings
from shruti.models.accounts import Supporter, User

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/billing", tags=["billing"])

# The tiers the site offers, mapped to the settings that name their Stripe
# price. Adding a tier means adding a price ID, not editing a template.
# The two that predate the tier table. Their price IDs live in the environment
# and are adopted on first read, so a subscription taken out before this keeps
# billing against exactly the price it was taken out against.
LEGACY_PRICE_FIELDS = {
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


async def _tier_row(key: str, session: AsyncSession):
    from shruti.models import Tier

    return (
        await session.execute(select(Tier).where(Tier.key == key, Tier.visible.is_(True)))
    ).scalar_one_or_none()


async def _price_id(tier: str, session: AsyncSession) -> str:
    row = await _tier_row(tier, session)
    if row is None:
        raise HTTPException(404, "no such tier")
    price_id = await _ensure_price(row, session)
    if not price_id:
        raise HTTPException(503, "that tier is not set up yet")
    return price_id


async def _ensure_price(row, session: AsyncSession) -> str:
    """
    The Stripe price for a tier, making one if it has none.

    The two original tiers keep the price they already had — taken from the
    environment where they still live — because a subscription is a standing
    arrangement and moving one to a freshly created price would change what
    somebody agreed to pay without asking them.
    """
    if row.stripe_price_id:
        return row.stripe_price_id

    field = LEGACY_PRICE_FIELDS.get(row.key)
    inherited = getattr(get_settings(), field, "") if field else ""
    if inherited:
        row.stripe_price_id = inherited
        await session.commit()
        return inherited

    from shruti.core import shop as stripe_shop

    try:
        product_id, price_id = stripe_shop.sync(row, interval=row.interval)
    except Exception as exc:                           # noqa: BLE001
        log.warning("tier %s could not be synced: %s", row.key, type(exc).__name__)
        return ""
    row.stripe_product_id, row.stripe_price_id = product_id, price_id
    await session.commit()
    return price_id


def _site_url(request: Request | None = None) -> str:
    """
    Where to send somebody back to after Stripe.

    Follows the origin they actually came from, so a checkout walked on a
    laptop returns to the laptop instead of dumping the payer on whatever is
    currently served at the live domain. Only ever an origin from the
    allowlist — a return URL a header could choose would be a "payment
    complete" page under somebody else's control.

    Without a request — the webhook, the portal's default return — it is the
    configured site, which is the only correct answer there anyway.
    """
    if request is None:
        return (get_settings().site_url or "http://localhost:8200").rstrip("/")

    sent = request.headers.get("origin")
    if not sent and (referer := request.headers.get("referer")):
        # A Referer is a full URL, and the allowlist holds origins. Firefox
        # sends no Origin on a same-site form POST, which is exactly the
        # request this needs to answer, so the scheme and host are taken off
        # the front rather than the header being ignored.
        parsed = urlparse(referer)
        if parsed.scheme and parsed.netloc:
            sent = f"{parsed.scheme}://{parsed.netloc}"
    return resolve_origin(sent)


# ── what the page shows ─────────────────────────────────────────────────────

@router.get("/tiers")
async def tiers(session: AsyncSession = Depends(get_session)) -> dict:
    """
    The tiers, as she has them, priced by Stripe.

    Returns `configured: false` rather than an error when Stripe is not set up:
    the support page has a designed state for that, and a 503 would make the
    whole page look broken when only the buttons are missing.

    The copy comes from here too — name, perks, the words on the button — so
    adding a tier is adding a row rather than editing a page and deploying it.
    """
    from shruti.models import Tier

    s = get_settings()
    rows = (
        await session.execute(
            select(Tier).where(Tier.visible.is_(True)).order_by(Tier.position, Tier.id)
        )
    ).scalars().all()

    listed = [
        {
            "tier": t.key,
            "name": t.name,
            "tagline": t.tagline,
            "perks": [line for line in (t.perks or "").splitlines() if line.strip()],
            "cta": t.cta or f"Become {t.name}",
            "badge": t.badge,
            "featured": t.featured,
            "amount": t.price_cents,
            "currency": (t.currency or "eur").upper(),
            "interval": t.interval,
        }
        for t in rows
    ]

    if not s.stripe_secret_key:
        # The tiers still describe themselves — the page can show what is on
        # offer and say the buttons are not live, which reads better than an
        # empty page that looks broken.
        return {"configured": False, "tiers": listed, "oneOff": None,
                "testMode": s.stripe_is_test}

    # A tier with no Stripe price yet gets one now, so the first person to look
    # at the page is not the one who discovers it was never finished.
    for row in rows:
        await _ensure_price(row, session)

    return {
        # Said on every money screen, because a site taking test cards looks
        # exactly like one that works.
        "testMode": s.stripe_is_test,
        "configured": True,
        "tiers": listed,
        "oneOff": {"min": ONE_OFF_MIN, "max": ONE_OFF_MAX, "default": ONE_OFF_DEFAULT,
                   "currency": "EUR"},
    }


# ── starting a checkout ─────────────────────────────────────────────────────

def _one_off_line_items(amount: int | None) -> dict[str, Any]:
    """
    A gift, for the amount the giver chose.

    This is the ONLY builder that takes an amount, which is the whole of the
    rule: a subscription cannot be given one because the function that builds
    one has nowhere to put it.
    """
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
                # VAT is INSIDE this number, not added to it.
                #
                # EU consumer law wants a price shown to a consumer to be
                # the price they pay, and Managed Payments will otherwise
                # add tax on top — a €4 tier quoted on the page and
                # charged at €4.84 on Stripe's, which is both unlawful for
                # B2C and the exact moment somebody abandons a checkout.
                #
                # The subscription prices carry the same behaviour, set on
                # the price itself in Stripe. It cannot be changed on an
                # existing price, so switching means creating a new one.
                "tax_behavior": "inclusive",
                "product_data": {
                "name": "A one-off gift",
                # Required by Managed Payments, same as the subscription
                # products. A gift that promises a name read on stream is
                # not a no-consideration donation, so it is declared
                # taxable rather than assumed out of scope.
                "tax_code": get_settings().stripe_tax_code,
            },
            },
        }],
    }


def _subscription_line_items(price_id: str, tier: str) -> dict[str, Any]:
    """
    A membership, at a price Stripe holds.

    **Takes no amount, and cannot be given one.** That is not a check that
    could be edited away — there is no parameter to pass. A subscriber pays
    what Stripe has recorded for the tier, whatever the browser said.
    """
    return {
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "subscription_data": {"metadata": {"tier": tier}},
    }


async def _line_items(tier: str, amount: int | None,
                      session: AsyncSession) -> dict[str, Any]:
    """
    What is being bought, and for how much.

    Dispatch only. The amount goes to the one-off builder or nowhere, and the
    tier's price is looked up rather than accepted.
    """
    if tier == "one-off":
        return _one_off_line_items(amount)
    return _subscription_line_items(await _price_id(tier, session), tier)


# ── tiers, as she manages them ──────────────────────────────────────────────

class TierIn(BaseModel):
    key: str
    name: str
    tagline: str = ""
    perks: str = ""
    cta: str = ""
    badge: str = ""
    featured: bool = False
    price_cents: int = 0
    currency: str = "eur"
    interval: str = "month"
    tax_code: str = "txcd_10000000"
    visible: bool = False
    position: int = 0


def _tier_payload(t) -> dict:
    return {
        "id": t.id, "key": t.key, "name": t.name, "tagline": t.tagline,
        "perks": t.perks, "cta": t.cta, "badge": t.badge, "featured": t.featured,
        "price_cents": t.price_cents, "currency": t.currency,
        "interval": t.interval, "tax_code": t.tax_code,
        "visible": t.visible, "position": t.position,
        "stripePriceId": t.stripe_price_id,
        "sellable": bool(t.stripe_price_id),
    }


@router.get("/admin/tiers", dependencies=[Depends(require_admin)])
async def admin_tiers(session: AsyncSession = Depends(get_session)) -> list[dict]:
    from shruti.models import Tier

    rows = (
        await session.execute(select(Tier).order_by(Tier.position, Tier.id))
    ).scalars().all()
    return [_tier_payload(t) for t in rows]


@router.post("/admin/tiers", status_code=201, dependencies=[Depends(require_admin)])
async def create_tier(
    body: TierIn, session: AsyncSession = Depends(get_session)
) -> dict:
    from shruti.models import Tier

    if body.interval not in {"month", "year"}:
        raise HTTPException(422, "interval must be month or year")
    row = Tier(**body.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return await _sync_tier(row, session)


@router.patch("/admin/tiers/{tier_id}", dependencies=[Depends(require_admin)])
async def update_tier(
    tier_id: int, body: dict, session: AsyncSession = Depends(get_session)
) -> dict:
    from shruti.models import Tier

    row = await session.get(Tier, tier_id)
    if row is None:
        raise HTTPException(404, "no such tier")
    if body.get("interval") and body["interval"] not in {"month", "year"}:
        raise HTTPException(422, "interval must be month or year")

    for key, value in body.items():
        if key in {"id", "created_at", "stripe_product_id", "stripe_price_id"}:
            continue
        if hasattr(row, key):
            setattr(row, key, value)
    await session.commit()
    await session.refresh(row)
    return await _sync_tier(row, session)


async def _sync_tier(row, session: AsyncSession) -> dict:
    from shruti.core import shop as stripe_shop

    try:
        product_id, price_id = stripe_shop.sync(row, interval=row.interval)
    except Exception as exc:                           # noqa: BLE001
        log.warning("tier %s could not be synced: %s", row.key, type(exc).__name__)
        return _tier_payload(row) | {"stripeError": f"{type(exc).__name__}: {exc}"}
    row.stripe_product_id, row.stripe_price_id = product_id, price_id
    await session.commit()
    await session.refresh(row)
    return _tier_payload(row)


@router.delete("/admin/tiers/{tier_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def delete_tier(tier_id: int, session: AsyncSession = Depends(get_session)):
    """
    Remove a tier nobody is on.

    **Refused while anyone is subscribed to it.** Their subscription lives at
    Stripe and would go on billing whether or not this row exists — deleting it
    here would only mean the site could no longer say what they are paying for.
    Hide it instead: nobody new can join, and everybody on it keeps what they
    have.
    """
    from shruti.models import Supporter, Tier

    row = await session.get(Tier, tier_id)
    if row is None:
        raise HTTPException(404, "no such tier")

    on_it = (
        await session.execute(select(Supporter).where(Supporter.tier == row.key))
    ).scalars().first()
    if on_it is not None:
        raise HTTPException(
            409,
            "somebody is subscribed to this, and their subscription lives at "
            "Stripe whether or not this row does. Untick \u201con offer\u201d "
            "instead — nobody new can join and everybody on it keeps what they "
            "have.",
        )

    await session.delete(row)
    await session.commit()
    return Response(status_code=204)


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

    here = _site_url(request)
    common: dict[str, Any] = {
        "success_url": f"{here}/support/thanks?session={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{here}/support",
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

    params = {**common, **await _line_items(body.tier, body.amount, session)}

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
            return_url=f"{_site_url(request)}/account",
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


def _period_end(subscription: dict) -> int | None:
    """
    When the paid period runs out.

    **Stripe moved this.** It used to sit on the subscription; on current API
    versions it lives on each subscription ITEM, and reading only the old
    place silently yields nothing. Silently is the problem — the renewal date
    and the "your access lasts until" date are the single most useful fact in
    the reminder and the cancellation email, and a missing fact is dropped
    from those templates rather than printed blank. The email still sends and
    still looks fine, having quietly lost the thing the reader wanted.

    Both places are read, newest first, so this keeps working across the
    version change in either direction.
    """
    items = (subscription.get("items") or {}).get("data") or []
    for item in items:
        if item.get("current_period_end"):
            return item["current_period_end"]
    return subscription.get("current_period_end")


async def _tell(
    session: AsyncSession, to: str, built: tuple[str, str] | None
) -> None:
    """
    Send one billing email, if there is somewhere to send it.

    A failed send must never fail the webhook. Stripe retries a non-2xx for
    days, and retrying a webhook because an email bounced would re-run the
    database work over and over to fix something the database was never wrong
    about.
    """
    if not (to and built):
        return
    subject, html = built
    result = await send(subject=subject, body=_plain(html), to=to, html=html)
    if not result.sent:
        log.warning("billing mail '%s' not sent: %s", subject, result.error)


def _plain(html: str) -> str:
    """
    The text part.

    Both parts, always — a client that will not render the HTML gets a real
    message rather than an empty frame, and a screen reader meets this first.
    Crude on purpose: a real HTML-to-text dependency for five templates whose
    structure is known would be the wrong trade.

    Three details that are not cosmetic. Entities are UNESCAPED, or `&#9827;`
    reaches somebody as those six characters. Inline tags close up rather than
    becoming spaces, or a bolded amount reads `€15 , once`. And a line holding
    nothing but the decorative glyph is dropped, because in text it is a
    stray symbol on a line of its own with no way to tell it was ornament.
    """
    import re
    from html import unescape

    text = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", html)
    # A link with no destination is useless in text. `Label (https://…)`,
    # unless the label already IS the destination.
    def _link(match: "re.Match[str]") -> str:
        href, label = match.group(1), re.sub(r"<[^>]+>", "", match.group(2)).strip()
        if not label:
            return href
        return label if href in label else f"{label} ({href})"

    text = re.sub(r'(?is)<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', _link, text)
    text = re.sub(r"(?i)<br\s*/?>|</p>|</tr>|</h1>|</div>", "\n", text)
    # Inline tags vanish; everything else becomes a space.
    text = re.sub(r"(?i)</?(b|strong|i|em|span|a|u)\b[^>]*>", "", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)

    lines = []
    for line in text.splitlines():
        line = " ".join(line.split())
        line = re.sub(r"\s+([,.;:!?])", r"\1", line)
        # A lone ornament, or nothing at all.
        if len(line) <= 1:
            continue
        lines.append(line)
    return "\n".join(lines).strip()


async def _current_imprint(session: AsyncSession) -> dict:
    """The registered details, or nothing. Never the bracketed placeholders."""
    try:
        return await imprint_settings(session)
    except Exception:                              # noqa: BLE001
        return {"visible": False}


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
        row.current_period_end = _moment(_period_end(subscription))
        tier = (subscription.get("metadata") or {}).get("tier", "")
        if tier:
            row.tier = tier


async def _supporter(session: AsyncSession, customer_id: str) -> Supporter | None:
    if not customer_id:
        return None
    return (
        await session.execute(
            select(Supporter).where(Supporter.stripe_customer_id == customer_id)
        )
    ).scalars().first()


async def _email_for(session: AsyncSession, customer_id: str) -> str:
    """
    Where to write.

    The account's address is preferred over the one Stripe holds: somebody who
    changed their email here and not there should still be reachable, and this
    is the address they see on their own account page.

    **Falling back to Stripe is not belt-and-braces, it is the fix for a real
    silent failure.** The address arrives with `checkout.session.completed`,
    and it is tempting to assume that always lands before
    `customer.subscription.created`. Stripe does not order webhooks, and a
    subscription made from the dashboard produces no checkout event at all —
    so the row can genuinely have no address when the cancellation email is
    due. `_tell` does nothing without one, which means the person who just
    cancelled hears nothing and the failure looks exactly like success. Asking
    Stripe costs one call, only when the address is missing, and it is then
    remembered.
    """
    row = await _supporter(session, customer_id)
    if row is None:
        return ""
    if row.user_id:
        user = (
            await session.execute(select(User).where(User.id == row.user_id))
        ).scalar_one_or_none()
        if user and user.email:
            return user.email
    if row.email:
        return row.email

    try:
        customer = stripe.Customer.retrieve(customer_id)
    except Exception as exc:                       # noqa: BLE001
        log.warning("customer %s could not be read: %s", customer_id, type(exc).__name__)
        return ""
    found = (customer.get("email") or "") if not customer.get("deleted") else ""
    if found:
        row.email = found
        await session.commit()
    return found


async def _tier_for(session: AsyncSession, customer_id: str) -> str:
    row = await _supporter(session, customer_id)
    return row.tier if row else ""


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

    imprint = await _current_imprint(session)

    if kind == "checkout.session.completed":
        # A shop purchase carries the product on the session. It is handled
        # first and separately: a jumper is not a membership, and running it
        # through the supporter path would make a one-off purchase look like
        # somebody subscribing.
        if (obj.get("metadata") or {}).get("product_slug"):
            from shruti.api.routes.shop import deliver, record_order

            order = await record_order(obj, session)
            if order is not None:
                await deliver(order, session)
            return {"received": True}

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

        # The contract confirmation is owed even when Stripe made no customer
        # — which is the ordinary shape of a one-off gift — so this sits
        # outside the `if customer_id` above rather than inside it.
        if email and subscription is not None:
            item = ((subscription.get("items") or {}).get("data") or [{}])[0]
            price = item.get("price") or {}
            await _tell(session, email, emails.subscription_started(
                tier=(subscription.get("metadata") or {}).get("tier", ""),
                amount=price.get("unit_amount"),
                currency=price.get("currency", "eur"),
                renews_on=_moment(_period_end(subscription)),
                imprint=imprint,
            ))
        elif email and obj.get("mode") == "payment":
            await _tell(session, email, emails.gift_received(
                amount=obj.get("amount_total"),
                currency=obj.get("currency", "eur"),
                imprint=imprint,
            ))

    elif kind in {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:
        customer_id = obj.get("customer") or ""
        if customer_id:
            await _upsert(session, customer_id=customer_id, subscription=dict(obj))
            await session.commit()

            tier = (obj.get("metadata") or {}).get("tier", "")

            # A cancellation is the TRANSITION, not the state. Stripe sends
            # `updated` for many reasons and this event arrives again on every
            # later change; without checking what actually changed, somebody
            # who cancelled once would be told so repeatedly.
            changed = (event["data"].get("previous_attributes") or {})
            just_cancelled = (
                kind == "customer.subscription.updated"
                and obj.get("cancel_at_period_end")
                and changed.get("cancel_at_period_end") is False
            )
            if just_cancelled:
                await _tell(
                    session, await _email_for(session, customer_id),
                    emails.subscription_cancelled(
                        tier=tier,
                        ends_on=_moment(_period_end(obj)),
                        imprint=imprint,
                    ),
                )

    elif kind == "invoice.upcoming":
        # Stripe fires this a few days before it charges. The gap it fills:
        # a charge nobody remembered agreeing to is the commonest route to a
        # chargeback, and being surprised by money leaving is a bad thing to do
        # to somebody whether or not the law requires the warning.
        customer_id = obj.get("customer") or ""
        to = obj.get("customer_email") or await _email_for(session, customer_id)
        line = ((obj.get("lines") or {}).get("data") or [{}])[0]
        await _tell(session, to, emails.renewal_reminder(
            tier=((line.get("metadata") or {}).get("tier")
                  or await _tier_for(session, customer_id)),
            amount=obj.get("amount_due"),
            currency=obj.get("currency", "eur"),
            charge_on=_moment(obj.get("next_payment_attempt")
                              or obj.get("period_end")),
            imprint=imprint,
        ))

    elif kind == "invoice.payment_failed":
        customer_id = obj.get("customer") or ""
        to = obj.get("customer_email") or await _email_for(session, customer_id)
        await _tell(session, to, emails.payment_failed(
            tier=await _tier_for(session, customer_id), imprint=imprint,
        ))

    # Everything else is acknowledged and ignored. Returning 200 for an event
    # we do not handle is correct: a 4xx makes Stripe retry it for days.
    return {"received": True}
