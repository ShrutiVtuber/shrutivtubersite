#!/usr/bin/env python3
"""
Move everything that is sold from test Stripe to live Stripe.

**Stripe's test and live modes are two separate worlds.** Every product, price,
coupon and webhook created against a test key exists only in test mode; the ids
stored in this database point at nothing once live keys are installed. Checkout
would fail on the first customer, which is the worst possible moment to find
out.

So this re-creates them. It reads every tier and product, forgets the ids they
are holding, and asks Stripe for new ones under whichever key is configured
now. Safe to run twice: the second run finds the ids it made and leaves them
alone.

    python scripts/stripe-golive.py            # say what would happen
    python scripts/stripe-golive.py --confirm  # do it

**It refuses to run against test keys** unless you pass --allow-test, because
running it in test mode does nothing useful and looks exactly like success.

What it does NOT do, because these need a browser and your Stripe login:

  - the live secret and publishable keys
  - the live webhook endpoint and its signing secret
  - re-creating any discount codes (Stripe coupons are per-mode too)
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import select                                       # noqa: E402

from shruti.core import shop as stripe_shop                       # noqa: E402
from shruti.core.config import get_settings                       # noqa: E402
from shruti.core.db import SessionLocal                           # noqa: E402
from shruti.models import Product, Tier                           # noqa: E402


def _mode() -> str:
    key = get_settings().stripe_secret_key or ""
    if key.startswith("sk_live"):
        return "live"
    if key.startswith("sk_test"):
        return "test"
    return "unset"


async def main(confirm: bool, allow_test: bool) -> int:
    mode = _mode()
    print(f"  Stripe key in use: {mode}")
    if mode == "unset":
        print("  No secret key is configured. Nothing to do.")
        return 2
    if mode == "test" and not allow_test:
        print("  Refusing: these are TEST keys. Install the live ones first,")
        print("  or pass --allow-test if you really mean to rebuild test mode.")
        return 2

    async with SessionLocal() as session:
        tiers = (await session.execute(select(Tier))).scalars().all()
        products = (await session.execute(select(Product))).scalars().all()

        rows: list[tuple[str, object, str]] = []
        rows += [("tier", t, t.interval or "month") for t in tiers]
        rows += [("product", p, "") for p in products]

        if not rows:
            print("  Nothing is set up to sell yet.")
            return 0

        print(f"  {len(tiers)} membership tier(s), {len(products)} product(s)")
        if not confirm:
            for kind, row, interval in rows:
                name = getattr(row, "name", "") or getattr(row, "key", "")
                print(f"    would re-create  {kind:8} {name}"
                      f"  (was {getattr(row, 'stripe_price_id', '') or 'nothing'})")
            print("\n  Nothing changed. Pass --confirm to do it.")
            return 0

        failures = 0
        for kind, row, interval in rows:
            name = getattr(row, "name", "") or getattr(row, "key", "")
            # Forgetting the old ids is the point: sync would otherwise try to
            # modify something that does not exist in this mode.
            row.stripe_product_id = ""
            row.stripe_price_id = ""
            try:
                product_id, price_id = stripe_shop.sync(row, interval=interval)
            except Exception as exc:                    # noqa: BLE001
                failures += 1
                print(f"    FAILED  {kind:8} {name}: {exc}")
                continue
            row.stripe_product_id = product_id
            row.stripe_price_id = price_id
            print(f"    made    {kind:8} {name}  ->  {price_id}")

        await session.commit()
        print(f"\n  Done. {len(rows) - failures} of {len(rows)} are live.")
        if failures:
            print("  Some failed and were left with no ids; fix and run again.")
        return 1 if failures else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--allow-test", action="store_true")
    args = ap.parse_args()
    raise SystemExit(asyncio.run(main(args.confirm, args.allow_test)))
