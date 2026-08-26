"""The merch rows, rewritten now that the printer is a known fact.

Revision ID: b5d24e70f931
Revises: a8f13b6d7e02

The seeded row said "acrylics first, 50–100 unit minimums, plush needs 200".
That is advice about **outsourced** manufacturing and it stopped being true the
moment she said she owns a resin printer: there is no minimum order at all.

The constraint is inverted rather than removed. Most creators are limited by
what they can commit to ordering; she is limited by what is worth her hours.
That makes the answer "sell what nobody else can make" — the instruments are the
design source, and nobody else in this niche can print the object their own
calculator produced.

The two new `do` rows exist because the shop now supports both selling models,
so the plan no longer has to choose between them.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b5d24e70f931"
down_revision = "a8f13b6d7e02"
branch_labels = None
depends_on = None


PRINTER_WHY = (
    "You own the manufacturing, so the usual constraint is inverted: most "
    "creators are limited by what they can commit to *ordering*, you are "
    "limited by what is worth your *hours*.\n\n"
    "**Sell what nobody else can make.** Your instruments are the design "
    "source — a planetary-hour dial, a decan set, sigil tokens generated on "
    "the site and printed by you, a pañcāṅga wheel. Nobody else in this niche "
    "can print the object their own calculator produced, and that is "
    "defensible in a way a hoodie is not.\n\n"
    "**Raw is a stated aesthetic, not a limitation.** \"Unpainted, so you can "
    "finish it yourself\" suits an occult object better than a painted one. "
    "The 40k painter network then becomes an *upsell on commission* rather "
    "than a bottleneck.\n\n"
    "The honest cost: your time is the bottleneck now instead of the minimum "
    "order. Washing, curing, support removal and finishing are all labour, "
    "resin is brittle in the post, and if something sells well you cannot "
    "suddenly make five hundred — outsourced manufacturing becomes the "
    "*upgrade path* rather than the starting point."
)

NEW = [
    dict(
        kind="do", position=85,
        title="Batch-print a first shelf item and leave it always on sale",
        summary="Something small, printed a few at a time, permanently listed.",
        effort="an afternoon", owner="you",
        why="The shop takes always-open items with real stock now. This is the "
            "low-risk half: print four, list them, see what happens. No window, "
            "no announcement, no obligation.\n\nIt also puts something in the "
            "shop, which matters more than it sounds — an empty shop teaches a "
            "visitor that there is never anything there.",
    ),
    dict(
        kind="do", position=86,
        title="Plan one windowed drop around a date that already means something",
        summary="A fortnight, tied to a birthday, an anniversary or an outfit reveal.",
        effort="a few weeks of lead time", owner="you",
        why="The shop now takes an opens and a closes date, and enforces both "
            "at checkout rather than only on the button.\n\nThe convention "
            "worth copying is the **calendar**, not the product: Japanese "
            "VTuber merch is pinned to identity events, which gives a fixed "
            "annual cadence, urgency that is genuinely true rather than "
            "invented, and a natural reason to reveal it live.\n\nA window also "
            "caps your queue. Always-open with no edges becomes an obligation; "
            "a drop ends.",
    ),
    dict(
        kind="build", position=15,
        title="Use the commission tracker on your own commissions first",
        summary="Build it for the custom-model work, then open it to other artists.",
        effort="a good week", owner="me",
        why="You would commission a 3D designer for a custom model and "
            "outsource painting through the 40k network. That is exactly the "
            "workflow the tracker was described for — and the tweet that "
            "prompted it was a client saying they had to *beg* for progress "
            "updates.\n\nBuilding it for your own commissions first means it "
            "ships with real scars on it and a true reason to exist. A tool "
            "whose author uses it is a different object from one built "
            "speculatively for other people.",
    ),
]


def upgrade() -> None:
    t = sa.table(
        "growth_item",
        sa.column("kind", sa.String), sa.column("title", sa.String),
        sa.column("summary", sa.String), sa.column("why", sa.Text),
        sa.column("effort", sa.String), sa.column("owner", sa.String),
        sa.column("position", sa.Integer), sa.column("visible", sa.Boolean),
        sa.column("done", sa.Boolean),
        sa.column("created_at", sa.DateTime), sa.column("updated_at", sa.DateTime),
    )
    conn = op.get_bind()

    # Rewrite the row rather than adding a second one: it is the same decision,
    # answered correctly.
    conn.execute(
        t.update()
        .where(sa.or_(t.c.title.like("First merch drop%"),
                      t.c.title.like("Work out what the resin printer%")))
        .values(
            title="Work out what the resin printer should make",
            summary="Raw resin, made to order, designed from your own instruments.",
            effort="a test print, then a listing",
            owner="you",
            why=PRINTER_WHY,
        )
    )

    existing = {r[0] for r in conn.execute(sa.select(t.c.title))}
    for row in NEW:
        if row["title"] in existing:
            continue
        conn.execute(t.insert().values(
            done=False, visible=True,
            created_at=sa.func.now(), updated_at=sa.func.now(), **row))


def downgrade() -> None:
    t = sa.table("growth_item", sa.column("title", sa.String))
    conn = op.get_bind()
    for row in NEW:
        conn.execute(t.delete().where(t.c.title == row["title"]))
