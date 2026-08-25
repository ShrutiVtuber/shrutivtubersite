# SPDX-License-Identifier: AGPL-3.0-only
"""
The shop.

Products live here and are mirrored to Stripe; Stripe takes the money. The
split matters: the site must be able to render a shop without a network call
per page, and nothing that touches a card may ever run on this box.

Physical and digital differ in exactly two places, and both are here rather
than spread out — a physical sale collects an address and decrements stock, a
digital one delivers a file and does neither.
"""
from __future__ import annotations

import json
import logging
import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.core import shop as stripe_shop
from shruti.core.config import get_settings
from shruti.core.db import get_session
from shruti.models import Media, Order, Product, ProductFile

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/shop", tags=["shop"])

KINDS = ("physical", "digital")


def _public(p: Product, media: Media | None) -> dict:
    from shruti.core.storage import public_url

    return {
        "slug": p.slug,
        "name": p.name,
        "kind": p.kind,
        "tagline": p.tagline,
        "bodyMd": p.body_md,
        "priceCents": p.price_cents,
        "currency": p.currency,
        # Sold out is a real state and not the same as absent: a thing that
        # exists and cannot be had right now should say so rather than vanish.
        "soldOut": p.stock is not None and p.stock <= 0,
        "media": None if media is None else {
            "url": public_url(media.filename, media.storage_backend),
            "alt": media.alt_text,
        },
    }


@router.get("/products")
async def list_products(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """What is for sale. Hidden products are not mentioned at all."""
    rows = (
        await session.execute(
            select(Product, Media)
            .join(Media, Product.media_id == Media.id, isouter=True)
            .where(Product.visible.is_(True))
            .order_by(Product.position, Product.id)
        )
    ).all()
    return [_public(p, m) for p, m in rows]


@router.get("/products/{slug}")
async def read_product(slug: str, session: AsyncSession = Depends(get_session)) -> dict:
    row = (
        await session.execute(
            select(Product, Media)
            .join(Media, Product.media_id == Media.id, isouter=True)
            .where(Product.slug == slug, Product.visible.is_(True))
        )
    ).first()
    if row is None:
        raise HTTPException(404, "no such product")
    return _public(row[0], row[1])


# ── buying ──────────────────────────────────────────────────────────────────

class BuyIn(BaseModel):
    slug: str
    quantity: int = Field(default=1, ge=1, le=20)


@router.post("/checkout")
async def checkout(
    body: BuyIn, request: Request, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Send them to Stripe to pay.

    Stock is checked here and again when the webhook lands. Checking only here
    would let two people buy the last one in the seconds between; checking only
    there would take their money first and tell them afterwards.
    """
    product = (
        await session.execute(
            select(Product).where(Product.slug == body.slug, Product.visible.is_(True))
        )
    ).scalar_one_or_none()
    if product is None:
        raise HTTPException(404, "no such product")
    if product.stock is not None and product.stock < body.quantity:
        raise HTTPException(409, "there are not that many left")
    if not product.stripe_price_id:
        raise HTTPException(503, "that product is not finished being set up")

    from shruti.api.routes.billing import _site_url

    site = _site_url(request)
    stripe = stripe_shop._client()

    session_args: dict[str, Any] = {
        "mode": "payment",
        "line_items": [{"price": product.stripe_price_id, "quantity": body.quantity}],
        "success_url": f"{site}/shop/thank-you?session={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{site}/shop/{product.slug}",
        # Stripe works the tax out from where they are and what this is; the
        # code that says what this is lives on the product.
        "automatic_tax": {"enabled": True},
        "metadata": {"product_slug": product.slug, "kind": product.kind},
    }

    if product.kind == "physical":
        # An address, because it has to be posted. Only for the kind that does
        # — asking a buyer of a PDF where they live is collecting something for
        # no reason.
        session_args["shipping_address_collection"] = {
            "allowed_countries": get_settings().shop_ship_to or ["GR"],
        }
        # Managed Payments makes Stripe the merchant of record, which is why
        # the memberships need no VAT registration of their own — and it does
        # not support shipping at all. So a physical sale opts out of it, and
        # is hers as the seller: her VAT, her obligations, her paperwork.
        #
        # This is a real difference between the two kinds of thing in this
        # shop, not a workaround. It is written here because this is where it
        # takes effect, and it is worth an accountant's attention before the
        # first physical thing actually sells.
        session_args["managed_payments"] = {"enabled": False}

    checkout_session = stripe.checkout.Session.create(**session_args)
    return {"url": checkout_session["url"]}


# ── the admin's half ────────────────────────────────────────────────────────

class ProductIn(BaseModel):
    slug: str
    name: str
    kind: str = "digital"
    tagline: str = ""
    body_md: str = ""
    price_cents: int = 0
    currency: str = "eur"
    media_id: int | None = None
    file_id: int | None = None
    stock: int | None = None
    tax_code: str = "txcd_10000000"
    visible: bool = False
    position: int = 0


def _admin_payload(p: Product) -> dict:
    return {
        "id": p.id, "slug": p.slug, "name": p.name, "kind": p.kind,
        "tagline": p.tagline, "body_md": p.body_md,
        "price_cents": p.price_cents, "currency": p.currency,
        "media_id": p.media_id, "file_id": p.file_id, "stock": p.stock,
        "tax_code": p.tax_code, "visible": p.visible, "position": p.position,
        "stripeProductId": p.stripe_product_id,
        "stripePriceId": p.stripe_price_id,
        # What the shop will not show, and why — so a product that is invisible
        # for a reason says the reason rather than looking broken.
        "sellable": bool(p.stripe_price_id) and (
            p.kind != "digital" or p.file_id is not None
        ),
    }


@router.get("/admin/products", dependencies=[Depends(require_admin)])
async def admin_list(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (
        await session.execute(select(Product).order_by(Product.position, Product.id))
    ).scalars().all()
    return [_admin_payload(p) for p in rows]


@router.post("/admin/products", status_code=201, dependencies=[Depends(require_admin)])
async def admin_create(
    body: ProductIn, session: AsyncSession = Depends(get_session)
) -> dict:
    if body.kind not in KINDS:
        raise HTTPException(422, f"kind must be one of {KINDS}")
    row = Product(**body.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return await _sync_and_return(row, session)


@router.patch("/admin/products/{product_id}", dependencies=[Depends(require_admin)])
async def admin_update(
    product_id: int, body: dict, session: AsyncSession = Depends(get_session)
) -> dict:
    row = await session.get(Product, product_id)
    if row is None:
        raise HTTPException(404, "no such product")
    if "kind" in body and body["kind"] not in KINDS:
        raise HTTPException(422, f"kind must be one of {KINDS}")

    for key, value in body.items():
        if key in {"id", "created_at", "stripe_product_id", "stripe_price_id"}:
            continue
        if hasattr(row, key):
            setattr(row, key, value)
    await session.commit()
    await session.refresh(row)
    return await _sync_and_return(row, session)


async def _sync_and_return(row: Product, session: AsyncSession) -> dict:
    """
    Push to Stripe, and say so if it did not go.

    A product saved here but missing there is not sellable, and the admin has
    to be told that plainly rather than showing a saved row that quietly cannot
    be bought.
    """
    try:
        product_id, price_id = stripe_shop.sync(row)
    except stripe_shop.StripeUnavailable as exc:
        return _admin_payload(row) | {"stripeError": str(exc)}
    except Exception as exc:                           # noqa: BLE001
        log.exception("Stripe sync failed for product %s", row.slug)
        return _admin_payload(row) | {"stripeError": f"{type(exc).__name__}: {exc}"}

    row.stripe_product_id, row.stripe_price_id = product_id, price_id
    await session.commit()
    await session.refresh(row)
    return _admin_payload(row)


@router.delete("/admin/products/{product_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def admin_delete(
    product_id: int, session: AsyncSession = Depends(get_session)
):
    """
    Remove a product that was never sold; take a sold one off sale instead.

    An order points at its product, and deleting the thing somebody bought
    would leave their order pointing at nothing — which is exactly the record
    they might need if they ask what happened to their money.
    """
    from fastapi import Response

    row = await session.get(Product, product_id)
    if row is None:
        raise HTTPException(404, "no such product")

    sold = (
        await session.execute(select(Order).where(Order.product_id == product_id))
    ).scalars().first()
    if sold is not None:
        raise HTTPException(
            409,
            "this has been bought at least once, so it cannot be deleted — "
            "untick “on sale” to take it out of the shop and keep the orders "
            "pointing at something.",
        )

    try:
        stripe_shop.archive(row)
    except stripe_shop.StripeUnavailable:
        pass
    await session.delete(row)
    await session.commit()
    return Response(status_code=204)


@router.get("/admin/orders", dependencies=[Depends(require_admin)])
async def admin_orders(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (
        await session.execute(select(Order).order_by(Order.id.desc()).limit(500))
    ).scalars().all()
    return [
        {
            "id": o.id,
            "email": o.email,
            "product": o.product_name,
            "quantity": o.quantity,
            "amount": o.amount_total_cents,
            "currency": o.currency,
            "fulfilment": o.fulfilment,
            "shipping": json.loads(o.shipping_json) if o.shipping_json else None,
            "placedAt": o.created_at.isoformat() if o.created_at else None,
        }
        for o in rows
    ]


class FulfilIn(BaseModel):
    fulfilment: str


@router.post("/admin/orders/{order_id}/fulfilment", dependencies=[Depends(require_admin)])
async def set_fulfilment(
    order_id: int, body: FulfilIn, session: AsyncSession = Depends(get_session)
) -> dict:
    if body.fulfilment not in {"none", "to_send", "sent"}:
        raise HTTPException(422, "unknown fulfilment state")
    row = await session.get(Order, order_id)
    if row is None:
        raise HTTPException(404, "no such order")
    row.fulfilment = body.fulfilment
    await session.commit()
    return {"ok": True, "fulfilment": row.fulfilment}


# ── what the webhook calls when a purchase completes ────────────────────────

async def record_order(event_object: dict, session: AsyncSession) -> Order | None:
    """
    Write the order, once.

    Keyed on the checkout session, so a webhook Stripe retries — which it will,
    by design — finds the order already there and changes nothing. Stock comes
    off here rather than at checkout, because until this arrives nobody has
    paid for anything.
    """
    session_id = event_object.get("id") or ""
    if not session_id:
        return None

    existing = (
        await session.execute(
            select(Order).where(Order.checkout_session_id == session_id)
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    slug = (event_object.get("metadata") or {}).get("product_slug") or ""
    product = (
        await session.execute(select(Product).where(Product.slug == slug))
    ).scalar_one_or_none()
    if product is None:
        return None

    details = event_object.get("customer_details") or {}
    shipping = event_object.get("shipping_details") or details.get("address") or {}
    quantity = 1
    for line in ((event_object.get("line_items") or {}).get("data") or []):
        quantity = line.get("quantity") or 1

    order = Order(
        checkout_session_id=session_id,
        payment_intent_id=event_object.get("payment_intent") or "",
        email=(details.get("email") or "").lower(),
        product_id=product.id,
        product_name=product.name,
        quantity=quantity,
        amount_total_cents=event_object.get("amount_total") or 0,
        currency=(event_object.get("currency") or "eur").lower(),
        fulfilment="to_send" if product.kind == "physical" else "none",
        shipping_json=json.dumps(shipping, ensure_ascii=False) if shipping else "",
        # A buyer needs their file without making an account for it.
        download_token=secrets.token_urlsafe(32) if product.kind == "digital" else "",
    )
    session.add(order)

    if product.stock is not None:
        product.stock = max(0, product.stock - quantity)

    await session.commit()
    await session.refresh(order)
    return order
