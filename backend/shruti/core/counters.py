# SPDX-License-Identifier: AGPL-3.0-only
"""
Recording what happened, and summing it into a target.

**A counter holds no total.** It is a query over `support_event`, and that is
the whole design. Incrementing a stored number is the obvious way to build this
and it goes wrong in three ordinary ways: a retried webhook adds twice, a
counter created mid-campaign starts at nought and lies, and changing which
sources count means a migration nobody wants to write. A sum has none of those
problems, and the table it sums is small for years.
"""
from __future__ import annotations

import logging
import secrets
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.models import Counter, SupportEvent

log = logging.getLogger(__name__)

# Everything a counter may be fed by. Named here so the admin can offer a list
# and a typo in a `sources` string is visible rather than silently counting
# nothing.
SOURCES = (
    "stripe.support", "stripe.membership", "stripe.shop",
    "twitch.sub", "twitch.gift", "twitch.bits", "twitch.raid", "twitch.follow",
    "youtube.superchat",
    "course.signup", "workshop.signup",
)

# Which number a source contributes. Money sources contribute their amount;
# everything else contributes its quantity — bits cheered, people signed up,
# viewers raided. A counter in euros should never be fed by a source measured
# in people, and the admin is responsible for not asking for that.
MONEY_SOURCES = {"stripe.support", "stripe.membership", "stripe.shop", "youtube.superchat"}


async def record(
    session: AsyncSession, *, source: str, external_id: str = "",
    amount_minor: int = 0, currency: str = "eur", quantity: int = 0,
    who: str = "", message: str = "",
    occurred_at: datetime | None = None,
) -> bool:
    """
    Note that something happened. True if it was new.

    Idempotent on `(source, external_id)`. Stripe retries webhooks and Twitch
    retries EventSub deliveries — both by design, both routinely — so this is
    not defensive programming. Without it a goal bar drifts upward on every
    retry, which is a wrong that looks like generosity and is very hard to
    notice.

    An `ON CONFLICT DO NOTHING` rather than a select-then-insert: two
    deliveries can arrive at once, and a check followed by an insert has a race
    between them wide enough to drive a duplicate through.
    """
    if source not in SOURCES:
        log.warning("refusing an event from an unknown source: %r", source)
        return False

    # Every event gets an identity, generated when the platform did not supply
    # one. That is what lets the unique index be a plain one — and a partial
    # index here does not merely dedupe less, it makes every insert fail, since
    # ON CONFLICT cannot match a predicate SQLAlchemy emits as a parameter.
    values = dict(
        source=source, external_id=external_id or f"local-{secrets.token_hex(8)}",
        amount_minor=int(amount_minor), currency=currency,
        quantity=int(quantity), who=who[:120], message=message[:500],
        # Never shown until somebody has read it. The default is the safe one
        # and approving is a deliberate act.
        message_approved=False, announced=False,
        occurred_at=occurred_at or datetime.now(timezone.utc),
    )
    stmt = pg_insert(SupportEvent).values(**values).on_conflict_do_nothing(
        index_elements=["source", "external_id"])
    result = await session.execute(stmt)
    await session.commit()
    return bool(result.rowcount)


def _sources_of(counter: Counter) -> list[str]:
    return [s.strip() for s in (counter.sources or "").split(",") if s.strip()]


async def progress(session: AsyncSession, counter: Counter) -> dict:
    """
    Where this counter has got to.

    Returns the raw numbers only. How to phrase "€184 of €300" or "14 of 20
    people" belongs to whatever is rendering it, and putting it here would mean
    the overlay and the website disagreeing about wording eventually.
    """
    sources = _sources_of(counter)
    if not sources:
        return {"current": 0, "target": counter.target, "contributors": 0, "sources": []}

    q = select(SupportEvent).where(SupportEvent.source.in_(sources))
    if counter.starts_at:
        q = q.where(SupportEvent.occurred_at >= counter.starts_at)
    if counter.ends_at:
        q = q.where(SupportEvent.occurred_at < counter.ends_at)

    rows = (await session.execute(q)).scalars().all()

    current = 0
    for e in rows:
        # A source measured in money contributes money; everything else
        # contributes its count. Mixing them in one counter is the admin's
        # decision to make badly, not ours to prevent.
        current += e.amount_minor if e.source in MONEY_SOURCES else e.quantity

    return {
        "current": current,
        "target": counter.target,
        "contributors": len({(e.who or e.external_id or e.id) for e in rows}),
        "sources": sources,
    }
