# SPDX-License-Identifier: AGPL-3.0-only
"""
Making a discount code exist at Stripe.

Two objects stand behind one row. A **coupon** is the discount itself — how
much comes off, and for how long on a subscription. A **promotion code** is the
word somebody types. They are separate at Stripe because one discount can have
several codes; here it is one of each, because she is offering a code, not
running a campaign.

**Terms are fixed at creation.** Stripe allows a coupon's name and metadata to
change and nothing else, which is the right rule — a discount that could be
altered after the fact would change what somebody was already promised. So this
creates, and after that a code is only turned on or off.
"""
from __future__ import annotations

import logging
from typing import Any

from shruti.core.config import get_settings

log = logging.getLogger(__name__)


class StripeUnavailable(RuntimeError):
    """Stripe is not configured, or would not answer."""


def _client() -> Any:
    import stripe

    s = get_settings()
    if not s.stripe_secret_key:
        raise StripeUnavailable("Stripe is not set up yet")
    stripe.api_key = s.stripe_secret_key
    return stripe


async def product_ids_for(applies_to: str, session) -> list[str]:
    """
    The Stripe products a coupon is confined to, if any.

    An empty list means everything, which is what Stripe understands by leaving
    the restriction off. Anything with no Stripe product yet is simply not in
    the list — a coupon cannot be restricted to something that does not exist
    there, and silently including a blank id would restrict it to nothing.
    """
    from sqlmodel import select

    from shruti.models import Product, Tier

    if applies_to == "shop":
        rows = (await session.execute(select(Product))).scalars().all()
    elif applies_to == "memberships":
        rows = (await session.execute(select(Tier))).scalars().all()
    else:
        return []
    return [r.stripe_product_id for r in rows if r.stripe_product_id]


def create(discount: Any, product_ids: list[str]) -> tuple[str, str]:
    """Create the coupon and its code. Returns (coupon_id, promotion_code_id)."""
    stripe = _client()

    coupon_args: dict[str, Any] = {
        "duration": discount.duration,
        # Her own label, so the Stripe dashboard is legible too.
        "name": discount.note or discount.code,
        "metadata": {"code": discount.code},
    }
    if discount.percent_off is not None:
        coupon_args["percent_off"] = discount.percent_off
    else:
        coupon_args["amount_off"] = discount.amount_off_cents
        coupon_args["currency"] = discount.currency
    if discount.duration == "repeating":
        coupon_args["duration_in_months"] = discount.duration_months or 1
    if product_ids:
        coupon_args["applies_to"] = {"products": product_ids}

    coupon = stripe.Coupon.create(**coupon_args)

    code_args: dict[str, Any] = {
        # This API version wraps the coupon rather than taking it directly.
        # Passing `coupon=` is refused outright as an unknown parameter.
        "promotion": {"type": "coupon", "coupon": coupon["id"]},
        "code": discount.code,
        "active": discount.active,
    }
    if discount.max_redemptions:
        code_args["max_redemptions"] = discount.max_redemptions
    if discount.expires_at:
        code_args["expires_at"] = int(discount.expires_at.timestamp())

    promotion = stripe.PromotionCode.create(**code_args)
    return coupon["id"], promotion["id"]


def set_active(discount: Any, active: bool) -> None:
    """Turn a code on or off. The coupon behind it is left alone."""
    if not discount.stripe_promotion_code_id:
        return
    stripe = _client()
    stripe.PromotionCode.modify(discount.stripe_promotion_code_id, active=active)


def redemptions(discount: Any) -> int | None:
    """
    How many times it has been used, according to Stripe.

    Stripe is asked rather than counted here, because Stripe is where the
    redemption actually happens — a number kept on this side would be a guess
    that drifts the first time a checkout completes and a webhook is missed.
    """
    if not discount.stripe_promotion_code_id:
        return None
    try:
        stripe = _client()
        code = stripe.PromotionCode.retrieve(discount.stripe_promotion_code_id)
        return code.get("times_redeemed")
    except Exception:                                  # noqa: BLE001
        return None


def archive(discount: Any) -> None:
    """
    Take it out of use for good.

    The code is deactivated and the coupon deleted where Stripe allows it. A
    coupon that has been redeemed cannot be deleted, and should not be: it is
    part of the record of what somebody actually paid.
    """
    if not discount.stripe_promotion_code_id and not discount.stripe_coupon_id:
        return
    stripe = _client()
    if discount.stripe_promotion_code_id:
        try:
            stripe.PromotionCode.modify(discount.stripe_promotion_code_id, active=False)
        except Exception:                              # noqa: BLE001
            log.info("promotion code %s could not be deactivated",
                     discount.stripe_promotion_code_id)
    if discount.stripe_coupon_id:
        try:
            stripe.Coupon.delete(discount.stripe_coupon_id)
        except Exception:                              # noqa: BLE001
            log.info("coupon %s was kept; it has probably been used",
                     discount.stripe_coupon_id)
