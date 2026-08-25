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

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.core import shop as stripe_shop
from shruti.core.config import get_settings
from shruti.core.db import get_session
from shruti.models import Media, Order, Product, ProductFile, ProductPhoto

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/shop", tags=["shop"])

KINDS = ("physical", "digital")


def _public(p: Product, media: Media | None,
            photos: list[Media] | None = None) -> dict:
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
        "photos": [
            {"url": public_url(m.filename, m.storage_backend), "alt": m.alt_text}
            for m in (photos or [])
        ],
    }


async def _photos_for(product_ids: list[int], session: AsyncSession) -> dict[int, list[Media]]:
    """
    Every product's pictures in one query.

    One query per product would be a query per card on the shop page, which is
    the shape of slow that only shows up once there is stock.
    """
    if not product_ids:
        return {}
    rows = (
        await session.execute(
            select(ProductPhoto, Media)
            .join(Media, ProductPhoto.media_id == Media.id)
            .where(ProductPhoto.product_id.in_(product_ids))
            .order_by(ProductPhoto.position, ProductPhoto.id)
        )
    ).all()
    out: dict[int, list[Media]] = {}
    for link, media in rows:
        out.setdefault(link.product_id, []).append(media)
    return out


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
    photos = await _photos_for([p.id for p, _m in rows if p.id], session)
    return [_public(p, m, photos.get(p.id)) for p, m in rows]


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
    photos = await _photos_for([row[0].id], session)
    return _public(row[0], row[1], photos.get(row[0].id))


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
        # A box to type a code into. Stripe checks it — whether it exists, has
        # expired, has run out, or applies to this at all — which is a great
        # deal of rule-following not worth reimplementing here.
        "allow_promotion_codes": True,
    }

    if product.kind == "physical":
        # An address, because it has to be posted. Only for the kind that does
        # — asking a buyer of a PDF where they live is collecting something for
        # no reason.
        from shruti.core.shipping import allowed

        session_args["shipping_address_collection"] = {
            "allowed_countries": allowed(get_settings().shop_ship_to),
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


# ── discount codes ──────────────────────────────────────────────────────────

class DiscountIn(BaseModel):
    code: str = Field(min_length=2, max_length=60)
    note: str = ""
    percent_off: float | None = None
    amount_off_cents: int | None = None
    currency: str = "eur"
    applies_to: str = "everything"
    duration: str = "once"
    duration_months: int | None = None
    max_redemptions: int | None = None
    expires_at: str | None = None
    active: bool = True


def _discount_payload(d, used: int | None = None) -> dict:
    return {
        "id": d.id,
        "code": d.code,
        "note": d.note,
        "percentOff": d.percent_off,
        "amountOffCents": d.amount_off_cents,
        "currency": d.currency,
        "appliesTo": d.applies_to,
        "duration": d.duration,
        "durationMonths": d.duration_months,
        "maxRedemptions": d.max_redemptions,
        "expiresAt": d.expires_at.isoformat() if d.expires_at else None,
        "active": d.active,
        "live": bool(d.stripe_promotion_code_id),
        "timesRedeemed": used,
    }


@router.get("/admin/discounts", dependencies=[Depends(require_admin)])
async def list_discounts(session: AsyncSession = Depends(get_session)) -> list[dict]:
    from shruti.core import discounts as codes
    from shruti.models import Discount

    rows = (
        await session.execute(select(Discount).order_by(Discount.id.desc()))
    ).scalars().all()
    return [_discount_payload(d, codes.redemptions(d)) for d in rows]


@router.post("/admin/discounts", status_code=201, dependencies=[Depends(require_admin)])
async def create_discount(
    body: DiscountIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Make a code.

    Refuses the combinations that would be meaningless rather than passing them
    to Stripe to refuse less clearly — a discount of nothing, or one that is
    both a percentage and an amount, is a mistake worth catching in the form.
    """
    from datetime import datetime

    from shruti.core import discounts as codes
    from shruti.models import Discount

    has_percent = body.percent_off is not None
    has_amount = body.amount_off_cents is not None
    if has_percent == has_amount:
        raise HTTPException(422, "give either a percentage off or an amount off, not both")
    if has_percent and not (0 < body.percent_off <= 100):
        raise HTTPException(422, "a percentage off has to be between 0 and 100")
    if has_amount and body.amount_off_cents <= 0:
        raise HTTPException(422, "an amount off has to be more than nothing")
    if body.duration not in {"once", "repeating", "forever"}:
        raise HTTPException(422, "duration must be once, repeating or forever")
    if body.applies_to not in {"everything", "shop", "memberships"}:
        raise HTTPException(422, "unknown applies-to")

    expires = None
    if body.expires_at:
        try:
            expires = datetime.fromisoformat(body.expires_at.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(422, "that expiry is not a date and time I can read")

    row = Discount(
        **body.model_dump(exclude={"expires_at"}),
        expires_at=expires,
    )
    row.code = row.code.strip()
    session.add(row)
    await session.commit()
    await session.refresh(row)

    try:
        product_ids = await codes.product_ids_for(row.applies_to, session)
        coupon_id, promo_id = codes.create(row, product_ids)
    except Exception as exc:                           # noqa: BLE001
        # The row is kept so she can see what failed and why rather than the
        # code vanishing, but it is plainly not live.
        log.exception("discount %s could not be created at Stripe", row.code)
        return _discount_payload(row) | {"stripeError": f"{type(exc).__name__}: {exc}"}

    row.stripe_coupon_id, row.stripe_promotion_code_id = coupon_id, promo_id
    await session.commit()
    await session.refresh(row)
    return _discount_payload(row, 0)


@router.post("/admin/discounts/{discount_id}/active",
             dependencies=[Depends(require_admin)])
async def set_discount_active(
    discount_id: int, active: bool, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Turn a code on or off.

    The only thing about a live discount that can change. Its terms are fixed
    at Stripe by design, and changing what a code is worth after people have it
    would change what they were promised.
    """
    from shruti.core import discounts as codes
    from shruti.models import Discount

    row = await session.get(Discount, discount_id)
    if row is None:
        raise HTTPException(404, "no such code")
    try:
        codes.set_active(row, active)
    except Exception as exc:                           # noqa: BLE001
        raise HTTPException(502, f"Stripe would not change it: {exc}")
    row.active = active
    await session.commit()
    return {"ok": True, "active": row.active}


@router.delete("/admin/discounts/{discount_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def delete_discount(
    discount_id: int, session: AsyncSession = Depends(get_session)
):
    """
    Remove a code.

    The coupon behind it is deleted where Stripe allows it — one that has been
    redeemed cannot be, and should not be: it is part of the record of what
    somebody actually paid.
    """
    from shruti.core import discounts as codes
    from shruti.models import Discount

    row = await session.get(Discount, discount_id)
    if row is None:
        raise HTTPException(404, "no such code")
    try:
        codes.archive(row)
    except codes.StripeUnavailable:
        pass
    await session.delete(row)
    await session.commit()
    return Response(status_code=204)


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


# ── the file a digital product delivers ─────────────────────────────────────

# What a digital product may be. Deliberately narrow and deliberately not the
# image list: these are things somebody buys and downloads, not things the site
# displays. Anything executable is absent on purpose.
ALLOWED_FILES = {
    "application/pdf": ".pdf",
    "application/epub+zip": ".epub",
    "application/zip": ".zip",
    "audio/mpeg": ".mp3",
    "audio/flac": ".flac",
    "audio/wav": ".wav",
    "video/mp4": ".mp4",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "text/plain": ".txt",
}

# Larger than an image, because an album or a video is not an image.
MAX_FILE_MB = 512


@router.post("/admin/files", status_code=201, dependencies=[Depends(require_admin)])
async def upload_file(
    file: UploadFile = File(...), session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Store a file a digital product will deliver.

    Content-hashed like media, and for the same reasons — the same file
    uploaded twice is stored once. The name it was uploaded under is kept
    separately, because a download called `9f2c…d1.zip` is not something
    anybody can use.

    It never becomes a media row: media is served straight off a public path by
    Caddy, and a paid file behind a guessable URL is not a paid file.
    """
    import hashlib

    if file.content_type not in ALLOWED_FILES:
        raise HTTPException(
            415,
            f"unsupported type {file.content_type!r}; allowed: {sorted(ALLOWED_FILES)}",
        )

    data = await file.read()
    if not data:
        raise HTTPException(422, "the file is empty")
    if len(data) > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(413, f"file is larger than {MAX_FILE_MB} MB")

    digest = hashlib.sha256(data).hexdigest()[:32]
    stored = f"product-{digest}{ALLOWED_FILES[file.content_type]}"

    existing = (
        await session.execute(
            select(ProductFile).where(ProductFile.stored_name == stored)
        )
    ).scalar_one_or_none()
    if existing is not None:
        return _file_payload(existing) | {"deduped": True}

    from shruti.core.storage import put

    put_result = await put(stored, data, file.content_type)
    row = ProductFile(
        stored_name=stored,
        original_name=file.filename or stored,
        mime_type=file.content_type,
        size_bytes=len(data),
        storage_backend=put_result.backend,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return _file_payload(row)


def _file_payload(f: ProductFile) -> dict:
    return {
        "id": f.id,
        "name": f.original_name,
        "mimeType": f.mime_type,
        "sizeBytes": f.size_bytes,
        "storage": f.storage_backend,
    }


@router.get("/admin/files", dependencies=[Depends(require_admin)])
async def list_files(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (
        await session.execute(select(ProductFile).order_by(ProductFile.id.desc()))
    ).scalars().all()
    return [_file_payload(f) for f in rows]


class PhotoIn(BaseModel):
    media_id: int


@router.get("/admin/products/{product_id}/photos", dependencies=[Depends(require_admin)])
async def admin_photos(
    product_id: int, session: AsyncSession = Depends(get_session)
) -> list[dict]:
    from shruti.core.storage import public_url

    rows = (
        await session.execute(
            select(ProductPhoto, Media)
            .join(Media, ProductPhoto.media_id == Media.id)
            .where(ProductPhoto.product_id == product_id)
            .order_by(ProductPhoto.position, ProductPhoto.id)
        )
    ).all()
    return [
        {
            "id": link.id,
            "mediaId": media.id,
            "url": public_url(media.filename, media.storage_backend),
            "alt": media.alt_text,
            "position": link.position,
        }
        for link, media in rows
    ]


@router.post("/admin/products/{product_id}/photos", status_code=201,
             dependencies=[Depends(require_admin)])
async def add_photo(
    product_id: int, body: PhotoIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Add a photograph to the end of a product's set.

    The same picture twice is refused rather than added twice: a gallery that
    shows one thing repeatedly reads as a bug, and a bug in a shop reads as an
    untrustworthy shop.
    """
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(404, "no such product")

    already = (
        await session.execute(
            select(ProductPhoto).where(
                ProductPhoto.product_id == product_id,
                ProductPhoto.media_id == body.media_id,
            )
        )
    ).scalar_one_or_none()
    if already is not None:
        return {"ok": True, "id": already.id, "alreadyThere": True}

    existing = (
        await session.execute(
            select(ProductPhoto).where(ProductPhoto.product_id == product_id)
        )
    ).scalars().all()
    row = ProductPhoto(
        product_id=product_id, media_id=body.media_id,
        position=(max((p.position for p in existing), default=-1) + 1),
    )
    session.add(row)

    # The first one is also the one the shop leads with, so the old column
    # keeps meaning what it always meant.
    if not existing:
        product.media_id = body.media_id

    await session.commit()
    await session.refresh(row)
    return {"ok": True, "id": row.id}


@router.delete("/admin/products/{product_id}/photos/{photo_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def remove_photo(
    product_id: int, photo_id: int, session: AsyncSession = Depends(get_session)
):
    """
    Take a photograph off a product. The picture itself stays in the library.
    """
    row = await session.get(ProductPhoto, photo_id)
    if row is None or row.product_id != product_id:
        raise HTTPException(404, "no such photo")
    await session.delete(row)
    await session.commit()
    await _releads(product_id, session)
    return Response(status_code=204)


class OrderIn(BaseModel):
    """The ids in the order they should appear."""

    photo_ids: list[int]


@router.post("/admin/products/{product_id}/photos/order",
             dependencies=[Depends(require_admin)])
async def reorder_photos(
    product_id: int, body: OrderIn, session: AsyncSession = Depends(get_session)
) -> dict:
    rows = {
        r.id: r
        for r in (
            await session.execute(
                select(ProductPhoto).where(ProductPhoto.product_id == product_id)
            )
        ).scalars().all()
    }
    for index, photo_id in enumerate(body.photo_ids):
        row = rows.get(photo_id)
        if row is not None:
            row.position = index
    await session.commit()
    await _releads(product_id, session)
    return {"ok": True}


async def _releads(product_id: int, session: AsyncSession) -> None:
    """
    Keep `product.media_id` pointing at whichever photograph is now first.

    Reordering or removing changes which one leads, and the column that the
    rest of the site reads has to follow — otherwise the shop card and the
    product page disagree about the same product.
    """
    first = (
        await session.execute(
            select(ProductPhoto)
            .where(ProductPhoto.product_id == product_id)
            .order_by(ProductPhoto.position, ProductPhoto.id)
        )
    ).scalars().first()
    product = await session.get(Product, product_id)
    if product is not None:
        product.media_id = first.media_id if first else None
        await session.commit()


@router.delete("/admin/files/{file_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def delete_file(file_id: int, session: AsyncSession = Depends(get_session)):
    """
    Remove a file, and the stored bytes with it.

    **Refused while a product still delivers it.** Deleting it out from under
    one would leave every buyer of that product with a link to nothing — and
    they would find out, not her, and only after paying.
    """
    row = await session.get(ProductFile, file_id)
    if row is None:
        raise HTTPException(404, "no such file")

    using = (
        await session.execute(select(Product).where(Product.file_id == file_id))
    ).scalars().all()
    if using:
        raise HTTPException(
            409,
            "still delivered by " + ", ".join(f"\u201c{p.name}\u201d" for p in using)
            + ". Point those at another file first, and then this can go.",
        )

    from shruti.core.storage import delete as delete_stored

    await delete_stored(row.stored_name, row.storage_backend)
    await session.delete(row)
    await session.commit()
    return Response(status_code=204)


# ── delivery ────────────────────────────────────────────────────────────────

async def deliver(order: Order, session: AsyncSession) -> None:
    """
    Tell them it worked, and how to get what they bought.

    Sent for both kinds. A physical buyer gets a receipt and what happens next;
    a digital one gets the link. Neither needs an account — asking someone to
    register to collect a thing they have already paid for is a way of losing
    the sale after taking the money.
    """
    from shruti.api.routes.billing import _site_url
    from shruti.core import mail

    if not order.email:
        log.warning("order %s has no address to send to", order.id)
        return

    money = f"{order.amount_total_cents / 100:.2f} {order.currency.upper()}"

    if order.download_token:
        # No request here — this runs from the webhook — so the configured
        # site URL is the only honest answer.
        site = _site_url(None)
        body = (
            f"Thank you — {order.product_name} is yours.\n\n"
            f"Download it here:\n{site}/api/shop/download/{order.download_token}\n\n"
            "The link is yours and does not expire. Keep this message if you "
            "want to download it again later.\n\n"
            f"Paid: {money}"
        )
    else:
        body = (
            f"Thank you — your order for {order.product_name} has been "
            f"received.\n\nIt will be posted to the address you gave at "
            "checkout, and you will hear from me when it goes.\n\n"
            f"Paid: {money}"
        )

    await mail.send(subject=f"Your order — {order.product_name}", to=order.email, body=body)


@router.get("/download/{token}")
async def download(token: str, session: AsyncSession = Depends(get_session)):
    """
    The file somebody bought.

    The token is the proof of purchase. It does not expire, because a thing
    that was bought stays bought — a link that dies in seven days turns a sale
    into a support request. It is long enough not to be guessed, and it is
    counted so an obviously-shared one can be noticed.
    """
    order = (
        await session.execute(
            select(Order).where(Order.download_token == token)
        )
    ).scalar_one_or_none()
    if order is None or not token:
        raise HTTPException(404, "no such download")

    product = await session.get(Product, order.product_id) if order.product_id else None
    file_row = (
        await session.get(ProductFile, product.file_id)
        if product and product.file_id else None
    )
    if file_row is None:
        raise HTTPException(
            410,
            "this download is not available — please reply to your receipt and "
            "it will be sorted out by hand.",
        )

    from shruti.core.storage import fetch

    found = await fetch(file_row.stored_name)
    if found is None:
        raise HTTPException(410, "the file is missing; please reply to your receipt")

    data, content_type = found
    order.downloads += 1
    await session.commit()

    return Response(
        content=data,
        media_type=content_type or file_row.mime_type or "application/octet-stream",
        headers={
            # The name they uploaded, not the hash it is stored under.
            "Content-Disposition":
                f'attachment; filename="{file_row.original_name}"',
            # Never cached by anything in between: it is one person's purchase.
            "Cache-Control": "private, no-store",
        },
    )
