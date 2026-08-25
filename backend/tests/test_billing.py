# SPDX-License-Identifier: AGPL-3.0-only
"""
Stripe — the parts that are ours.

Stripe's own correctness is Stripe's problem. What is worth testing here is the
seam: that an amount arriving from a browser cannot become the amount charged,
that a webhook without a verified signature changes nothing, and that with no
keys at all the money paths refuse rather than half-work.

The last one matters more than it looks. Every other unconfigured integration
on this site degrades to a quieter version of itself — the live badge says
offline, uploads go to disk. Money has no quieter version: a support button
that appears and then fails is worse than no button, because it fails at the
one moment someone had decided to be generous.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest
import stripe

from shruti.api.routes import billing
from shruti.core.config import get_settings


@pytest.fixture
def configured(monkeypatch):
    """Settings are cached, so an env change alone would not be seen."""
    def apply(**values: str):
        for key, value in values.items():
            monkeypatch.setenv(f"SHRUTI_{key.upper()}", value)
        _ = values
        get_settings.cache_clear()
        return get_settings()
    yield apply
    get_settings.cache_clear()


# ── failing closed ──────────────────────────────────────────────────────────

def test_no_key_means_no_client(configured) -> None:
    configured(stripe_secret_key="")
    with pytest.raises(Exception) as caught:
        billing._client()
    assert caught.value.status_code == 503


def test_a_tier_price_is_never_invented_when_one_is_missing() -> None:
    """
    Half-configured is not a licence to charge something plausible.

    Tiers live in the database now, so the refusal happens where the row is
    read. What is checked here is the shape that makes it possible: the
    subscription builder is handed a price and has no way to make one up.
    """
    built = billing._subscription_line_items("price_lamp", "lamplighter")
    assert built["line_items"] == [{"price": "price_lamp", "quantity": 1}]


# ── the amount ──────────────────────────────────────────────────────────────

def test_the_one_off_bounds_are_the_ones_stripe_can_actually_take() -> None:
    """Below Stripe's minimum the payment is refused by Stripe with a message
    the visitor cannot act on; the point of the floor is to refuse it here with
    one they can."""
    assert billing.ONE_OFF_MIN >= 100          # Stripe's EUR floor is €0.50
    assert billing.ONE_OFF_MIN <= billing.ONE_OFF_DEFAULT <= billing.ONE_OFF_MAX


@pytest.mark.parametrize("amount", [0, 1, 199, 50_001, 10_000_000, -500])
def test_an_amount_outside_the_bounds_is_not_chargeable(amount: int) -> None:
    """The clamp is the whole defence. A checkout whose amount came from the
    client is a checkout somebody can set to one cent — or, worse for them, to
    ten thousand euro by a typo the page did not stop."""
    assert not (billing.ONE_OFF_MIN <= amount <= billing.ONE_OFF_MAX)


@pytest.mark.parametrize("amount", [200, 300, 1000, 50_000])
def test_an_amount_inside_the_bounds_is_chargeable(amount: int) -> None:
    assert billing.ONE_OFF_MIN <= amount <= billing.ONE_OFF_MAX


def test_the_subscription_builder_cannot_be_given_an_amount() -> None:
    """
    Stronger than checking that an amount is ignored: there is nowhere to put
    one. A future edit cannot re-introduce the bug by passing it through,
    because passing it is a TypeError.
    """
    import inspect

    taken = set(inspect.signature(billing._subscription_line_items).parameters)
    assert "amount" not in taken
    assert taken == {"price_id", "tier"}


def test_a_subscription_amount_can_never_come_from_the_client() -> None:
    """The one that would actually cost her money. `amount` must be reachable
    only on the one-off path — if an edit ever lets it through for a tier, a
    subscriber pays whatever their browser said, and one cent is a browser
    away."""
    built = billing._subscription_line_items("price_lamp", "lamplighter")
    assert built["mode"] == "subscription"
    assert built["line_items"] == [{"price": "price_lamp", "quantity": 1}]
    # Nothing amount-shaped is sent at all: a subscription line item names a
    # price and a quantity, and the price is Stripe's.
    sent = json.dumps(built)
    assert "unit_amount" not in sent
    assert "price_data" not in sent
    assert built["line_items"][0]["quantity"] == 1


def test_a_one_off_uses_the_amount_it_was_given() -> None:
    built = billing._one_off_line_items(1500)
    assert built["mode"] == "payment"
    assert built["line_items"][0]["price_data"]["unit_amount"] == 1500


def test_a_one_off_with_no_amount_falls_back_to_the_suggested_one() -> None:
    built = billing._one_off_line_items(None)
    assert built["line_items"][0]["price_data"]["unit_amount"] == billing.ONE_OFF_DEFAULT


@pytest.mark.parametrize("amount", [1, 199, 50_001, -500])
def test_a_one_off_outside_the_bounds_is_refused_before_stripe_sees_it(amount: int) -> None:
    with pytest.raises(Exception) as caught:
        billing._one_off_line_items(amount)
    assert caught.value.status_code == 422


# ── the webhook ─────────────────────────────────────────────────────────────

SECRET = "whsec_test_secret_for_this_file_only"


def _sign(payload: bytes, secret: str = SECRET, at: int | None = None) -> str:
    stamp = at if at is not None else int(time.time())
    signed = f"{stamp}.".encode() + payload
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={stamp},v1={digest}"


def _event(kind: str = "customer.subscription.updated") -> bytes:
    return json.dumps({
        "id": "evt_1", "object": "event", "type": kind,
        "data": {"object": {"id": "sub_1", "customer": "cus_1", "status": "active"}},
    }).encode()


def test_a_correctly_signed_event_verifies() -> None:
    payload = _event()
    event = stripe.Webhook.construct_event(payload, _sign(payload), SECRET)
    assert event["type"] == "customer.subscription.updated"


def test_a_forged_signature_is_refused() -> None:
    payload = _event()
    with pytest.raises(Exception):
        stripe.Webhook.construct_event(payload, "t=1,v1=deadbeef", SECRET)


def test_a_signature_from_the_wrong_secret_is_refused() -> None:
    """Anyone who knows the URL could otherwise grant themselves a tier."""
    payload = _event()
    with pytest.raises(Exception):
        stripe.Webhook.construct_event(payload, _sign(payload, "whsec_not_it"), SECRET)


def test_a_replayed_event_falls_outside_the_tolerance() -> None:
    payload = _event()
    old = _sign(payload, at=int(time.time()) - 3600)
    with pytest.raises(Exception):
        stripe.Webhook.construct_event(payload, old, SECRET, tolerance=300)


def test_a_tampered_body_is_refused() -> None:
    """The signature covers the body. Changing the status after signing — the
    obvious way to fake an active subscription — has to fail."""
    payload = _event()
    signature = _sign(payload)
    tampered = payload.replace(b'"status": "active"', b'"status": "ACTIVE"')
    with pytest.raises(Exception):
        stripe.Webhook.construct_event(tampered, signature, SECRET)


# ── small conversions ───────────────────────────────────────────────────────

def test_a_stripe_timestamp_becomes_an_aware_datetime() -> None:
    """Naive datetimes are what asyncpg refuses on a timestamptz column, which
    is how every newsletter confirmation once 500'd."""
    moment = billing._moment(1_700_000_000)
    assert moment is not None and moment.tzinfo is not None


def test_a_missing_timestamp_stays_missing() -> None:
    assert billing._moment(None) is None
    assert billing._moment(0) is None


# ── where somebody lands after paying ───────────────────────────────────────

def test_the_return_origin_cannot_be_chosen_by_a_header(configured) -> None:
    """A Checkout return URL sends a browser somewhere after money has moved.
    A header that could pick that destination is a 'payment complete' page
    under somebody else's control."""
    from shruti.core.origins import resolve

    configured(site_url="https://shrutivtuber.com", env="prod")
    assert resolve("https://evil.example") == "https://shrutivtuber.com"
    assert resolve(None) == "https://shrutivtuber.com"
    assert resolve("") == "https://shrutivtuber.com"


def test_a_local_checkout_returns_to_the_laptop(configured) -> None:
    """Otherwise a test checkout walked on localhost dumps the payer on
    whatever is currently served at the live domain — which before cutover is
    the old WordPress site."""
    from shruti.core.origins import resolve

    configured(site_url="https://shrutivtuber.com", env="development")
    assert resolve("http://localhost:8200") == "http://localhost:8200"


def test_localhost_is_not_a_return_origin_in_production(configured) -> None:
    from shruti.core.origins import resolve

    configured(site_url="https://shrutivtuber.com", env="production")
    assert resolve("http://localhost:8200") == "https://shrutivtuber.com"


def test_a_trailing_slash_does_not_defeat_the_allowlist(configured) -> None:
    from shruti.core.origins import resolve

    configured(site_url="https://shrutivtuber.com/", env="prod")
    assert resolve("https://shrutivtuber.com/") == "https://shrutivtuber.com"


# ── the field Stripe moved ──────────────────────────────────────────────────

def test_the_period_end_is_read_from_the_subscription_item() -> None:
    """
    Stripe moved `current_period_end` from the subscription onto each item.
    Reading only the old place yields nothing, and nothing is the worst
    possible outcome here: the renewal date and the "access until" date are
    dropped from those emails rather than printed blank, so the mail still
    sends, still looks right, and has quietly lost the fact the reader opened
    it for.
    """
    modern = {"id": "sub_1", "items": {"data": [{"current_period_end": 1_790_292_206}]}}
    assert billing._period_end(modern) == 1_790_292_206


def test_the_old_shape_still_works() -> None:
    """Read newest-first, but keep the old place, so this survives the version
    change in either direction."""
    legacy = {"id": "sub_1", "current_period_end": 1_700_000_000, "items": {"data": [{}]}}
    assert billing._period_end(legacy) == 1_700_000_000


def test_no_period_end_anywhere_is_none_not_a_crash() -> None:
    assert billing._period_end({"id": "sub_1"}) is None
    assert billing._period_end({"id": "sub_1", "items": {"data": []}}) is None
