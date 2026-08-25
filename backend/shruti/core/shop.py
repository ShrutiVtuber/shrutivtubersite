# SPDX-License-Identifier: AGPL-3.0-only
"""
Keeping a product in step with Stripe.

The row here is what the shop renders from — a page load should not be a
network call — and the Stripe product and price are what actually take the
money. So one has to follow the other, and this is where that happens.

**A price is never edited, it is replaced.** Stripe prices are immutable by
design, because a price that could change under a customer would change what
they agreed to pay. Changing the number here creates a new price and points the
product at it; the old one is archived, and anything already sold at it keeps
its own record of what was paid.
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


def tax_behavior() -> str:
    """
    Whether the listed price already contains the tax.

    Inclusive is what the memberships use and what a European shopper expects:
    the number on the page is the number they pay. It is a setting rather than
    a constant because physical goods sold to other markets often are not
    priced that way, and finding out should not need a migration.
    """
    return get_settings().stripe_tax_behavior or "inclusive"


def sync(product: Any) -> tuple[str, str]:
    """
    Create or update this product in Stripe. Returns (product_id, price_id).

    Safe to call on every save: if nothing that Stripe cares about changed, it
    updates the name and description and hands the same price back.
    """
    stripe = _client()

    payload = {
        "name": product.name,
        "description": product.tagline or None,
        "tax_code": product.tax_code or None,
        "metadata": {"slug": product.slug, "kind": product.kind},
        # Stripe needs to know whether an address is required, and it is the
        # kind of thing that must not be decided in two places.
        "shippable": product.kind == "physical",
    }

    if product.stripe_product_id:
        stripe_product = stripe.Product.modify(product.stripe_product_id, **payload)
    else:
        stripe_product = stripe.Product.create(**payload)

    price_id = product.stripe_price_id
    if price_id:
        try:
            existing = stripe.Price.retrieve(price_id)
        except Exception:                              # noqa: BLE001
            existing = None
        matches = (
            existing is not None
            and existing.get("unit_amount") == product.price_cents
            and existing.get("currency") == product.currency
            and existing.get("tax_behavior") == tax_behavior()
        )
        if matches:
            return stripe_product["id"], price_id

    price = stripe.Price.create(
        product=stripe_product["id"],
        unit_amount=product.price_cents,
        currency=product.currency,
        tax_behavior=tax_behavior(),
    )

    # The old one is archived rather than deleted: an order that was placed at
    # it must keep resolving, and Stripe does not allow deleting a used price.
    if price_id:
        try:
            stripe.Price.modify(price_id, active=False)
        except Exception:                              # noqa: BLE001
            log.info("could not archive the old price %s; leaving it active", price_id)

    return stripe_product["id"], price["id"]


def archive(product: Any) -> None:
    """Take it off sale in Stripe without destroying what was sold."""
    if not product.stripe_product_id:
        return
    stripe = _client()
    try:
        stripe.Product.modify(product.stripe_product_id, active=False)
    except Exception:                                  # noqa: BLE001
        log.info("could not archive %s in Stripe", product.stripe_product_id)
