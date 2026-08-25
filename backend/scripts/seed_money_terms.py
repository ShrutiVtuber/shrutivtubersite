"""
Add the money sections to /terms.

Written to the DATABASE rather than into a template, because that is where the
terms live and because the next edit will be an attorney's. Nothing here should
need a deploy to change.

**These are a starting draft, not advice.** They state what the software
actually does — which is the part I can be sure of — and they use the
directive's own language for the withdrawal right without inventing a position
on anything else. The paragraph an attorney will care about is the one about
immediate performance, and it is marked.
"""
import asyncio

from sqlmodel import select

from shruti.core.db import SessionLocal
from shruti.models import Section

SECTIONS = [
    (
        "support",
        "Supporting the work",
        90,
        """Everything on this site is free. The streams, the instruments, the horoscopes
and the writing are not behind a payment and are not going to be. Supporting is a
gift toward the cost of running it — the ephemeris server, art commissions, and
the hours the software takes — and it buys the small extras named on the support
page, not access to the site.

Payment is handled by **Stripe**, who act as merchant of record. Card details are
entered on Stripe's own pages and never reach this site or its server. Stripe
collects and remits any VAT due. Prices shown include VAT, so the amount on the
page is the amount charged.

Monthly support renews every month until it is stopped. You will be told before
each charge.""",
    ),
    (
        "cancelling",
        "Cancelling",
        91,
        """You can cancel monthly support at any time, in one step, from your account
page — or from the link in any receipt Stripe sends you. No message to me is
needed, no reason is asked for, and nothing is offered to talk you out of it.

**Cancelling takes effect at the end of the period you have already paid for.**
You keep what that period bought until it runs out, and you are not charged
again. You will get an email confirming it, naming the date access ends.

Deleting your account also ends any monthly support. Support that has already
been given is not refunded by deleting the account — see below.""",
    ),
    (
        "withdrawal",
        "Your right to withdraw, and refunds",
        92,
        """If you are a consumer in the EU or the UK, you normally have **fourteen days**
to withdraw from a distance contract without giving a reason.

Monthly support is a service that starts as soon as you pay for it — the members
channel, the schedule a day early, the practice notes. By starting it you are
asking for the service to begin during that fourteen-day period, and once it has
been fully performed for a period you have paid for, the right to withdraw from
that period no longer applies. Where the service has only been partly performed,
any refund is in proportion to what has been supplied.

**A one-off gift is a gift.** It buys nothing, it is not a contract for a
service, and it is not refundable — but if you gave one by mistake, say so and
it will be sent back. That is a promise rather than an obligation, and it will
be kept.

Beyond that: if something here did not work, or you were charged for something
you did not mean to buy, write and it will be put right. I would rather refund
somebody than argue with them.""",
    ),
    (
        "prices-change",
        "If a price changes",
        93,
        """If the price of monthly support changes, existing supporters are told before
it takes effect and are never charged the new amount without having had the
chance to cancel first. A price change is not applied to a period already paid
for.""",
    ),
]


async def main() -> None:
    async with SessionLocal() as session:
        for key, title, position, body in SECTIONS:
            row = (
                await session.execute(
                    select(Section).where(Section.page == "terms", Section.key == key)
                )
            ).scalar_one_or_none()
            if row is None:
                row = Section(page="terms", key=key)
                session.add(row)
            row.kind = "prose"
            row.title = title
            row.position = position
            row.body_md = body.strip()
            # Visible: a site that takes money and does not say these things is
            # the problem this fixes. Editing them is a form in the admin.
            row.visible = True
        await session.commit()
        print(f"  {len(SECTIONS)} money sections written to /terms")


asyncio.run(main())
