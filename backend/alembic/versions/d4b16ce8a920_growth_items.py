"""The growth checklist and the tools queue, seeded from the research.

Revision ID: d4b16ce8a920
Revises: c3f97ba2e6d1

Two lists she asked for and one table holding both. The checklist is the things
no engineer can do for her — the Twitch category, the panel, the lawyer. The
tools queue is what this site could build next.

Every row carries its `why` with the evidence in it, because a checklist read
for motivation is a different object from a checklist read for tracking, and
this one is explicitly the first.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d4b16ce8a920"
down_revision = "c3f97ba2e6d1"
branch_labels = None
depends_on = None


DO = [
    dict(
        title="Change the Twitch category to Software and Game Development",
        summary="The single highest-leverage free change available.",
        effort="two minutes, free", owner="you",
        why="Measured on Twitch: the **Astrology** category has *no ranked channels at all*, "
            "and Tarot's entire top fifty does 9,552 viewer-hours a month — less than half what "
            "the third-place coding streamer does on his own. **Software and Game Development "
            "does 368,185.** You cannot be found by browsing a category nobody browses. "
            "Twitch's own VTuber Club and VTuber Week have both featured tech-flavoured indies.",
    ),
    dict(
        title="Ask a Greek lawyer about the imprint address",
        summary="The only hard blocker left before launch.",
        effort="one email", owner="you",
        why="EU e-commerce rules ask for the geographic address at which the provider is "
            "*established*. A mail-forwarding box may not satisfy that, and the tension between "
            "that and your personal safety is real. The admin's own help text used to recommend "
            "a virtual office; that has been corrected to say the tension exists rather than "
            "picking a side for you.",
    ),
    dict(
        title="Submit a panel to VeXpo 2026",
        summary="Birmingham, 18–20 September 2026. Non-profit, and the closest one to you.",
        effort="an afternoon writing it", owner="you",
        why="Convention programmes in this scene are overwhelmingly **indie-submitted panels**, "
            "and they reward specific competence over follower count — a linguist VTuber got one "
            "on the etymology of VTuber slang. \"Programming for magickal practice\" is exactly "
            "that kind of proposal, and almost nobody else can give it.",
    ),
    dict(
        title="Make the build the content",
        summary="Debug on stream. Take suggestions from chat. The engineering IS the show.",
        effort="a habit, not a task", owner="you",
        why="Vedal's format is literally debugging code on stream, planning the schedule on "
            "stream, and fielding changes from chat — and Neuro-sama is now the **third "
            "most-subscribed Twitch channel of all time**. He appears as a turtle. You already "
            "write the instruments live; this just says stop treating that as the boring part.",
    ),
    dict(
        title="Two to three hours, not nine",
        summary="Shorter streams. They also clip better.",
        effort="free", owner="you",
        why="Vedal deliberately cut stream length from nine hours to two or three to keep them "
            "from becoming boring. Shorter sessions are also far easier for clippers to work "
            "with, and clips are how people who have never heard of you find you.",
    ),
    dict(
        title="Ship one artefact a month and post it",
        summary="Something that can be shown in a single image.",
        effort="ongoing", owner="both",
        why="**Neither Vedal nor CodeMiko was discovered through a category or as a "
            "personality.** Both went viral off an artefact — a thing that existed and could be "
            "shown. That makes the instruments, the charts and the compatibility cards the "
            "discovery mechanism rather than a side project beside the streaming.",
    ),
    dict(
        title="Two membership tiers, not six",
        summary="Participation at the top, plus things people can download.",
        effort="an afternoon in the admin", owner="you",
        why="hololive's own channel runs **exactly two tiers**. The upper one rests on "
            "*questionnaire participation* — surveys that steer content — and *downloadable "
            "artefacts*. Both are cheap to produce and both are delivered better by a website "
            "than by YouTube. You already have polls and a media library.",
    ),
    dict(
        title="First merch drop is acrylics, on a date that already means something",
        summary="Acrylic stands and keychains, pinned to a birthday or an anniversary.",
        effort="a few weeks lead time", owner="you",
        why="Acrylics run $12–25 with **50–100 unit minimums**; plush needs 200. The Japanese "
            "convention is to pin merch to *identity events* — birthday, debut anniversary, "
            "outfit reveal, subscriber milestone — which gives a fixed annual cadence, real "
            "urgency without inventing any, and a natural reason to reveal it live.",
    ),
    dict(
        title="Collab by offering value first",
        summary="Lead with tools, not with \"want to collab?\"",
        effort="ongoing", owner="you",
        why="The documented etiquette is consistent: be in someone's community before reaching "
            "out, use public channels rather than DMs, and lead with art, resources or feedback. "
            "**Yours is tools** — which is a far stronger opening than most people have. "
            "Shipping things other VTubers use enters you as a peer and a supplier rather than "
            "as a supplicant.",
    ),
    dict(
        title="Enter the VTuber Industry Awards as a builder",
        summary="They have a Technical Excellence category, and it is judged on work done for others.",
        effort="a nomination", owner="you",
        why="The awards exist to make *builders* visible — riggers, asset makers, tooling "
            "developers. Technical Excellence went to someone for \"practical stream widgets "
            "which enhance VTubers' setups\", and judging explicitly weighs whether the work was "
            "done for other clients too. That is the category you are already in.",
    ),
]

BUILD = [
    dict(
        title="A commission progress tracker for artists and their clients",
        summary="Low-friction updates on where a commission actually is.",
        effort="a good week", owner="me",
        why="From a VTuber, verbatim: *\"You guys have no idea how happy it makes us as clients "
            "when we get updates on the progression of our comms. I feel like there are times "
            "when I have to beg to see some sort of activity. Especially when there is no trello "
            "or any other sources for tracking.\"*\n\n"
            "The gap is real and it is mutual — artists do not want to write status reports, "
            "clients do not want to chase. Something an artist can update in one tap, that gives "
            "the client a link they can check without asking, would be used by both sides. "
            "It is also exactly the shape of thing that makes other creators link to you.",
    ),
    dict(
        title="A collab timezone planner",
        summary="When can all of us actually stream together?",
        effort="a few days", owner="me",
        why="**No VTuber timezone-coordination tool exists** — the research looked, and the "
            "closest thing died with `kson-schedule.com`, which had multi-platform aggregation "
            "and a timezone selector and now has no DNS at all. You have this problem yourself, "
            "collaborating from Athens with North America. Stateless and shareable by link, so "
            "there is nothing to store and nothing to leak.",
    ),
    dict(
        title="A canonical \"these are my real stores\" page",
        summary="An anti-counterfeit instrument, on a site you own.",
        effort="a day", owner="me",
        why="Counterfeit VTuber merch stores run as **networks**: two share the same four "
            "nameservers and one operator; one claims \"OFFICIAL\" in its page title while its "
            "body says \"Fan\"; one misspells the creator's own name. Ironmouse's site uses its "
            "merch grid as exactly this kind of instrument. You already have /shop and /partners "
            "to host it, and a page on your own domain is the thing you can point at.",
    ),
]


def upgrade() -> None:
    op.create_table(
        "growth_item",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", sa.String(), nullable=False, server_default="do"),
        sa.Column("title", sa.String(), nullable=False, server_default=""),
        sa.Column("summary", sa.String(), nullable=False, server_default=""),
        sa.Column("why", sa.Text(), nullable=False, server_default=""),
        sa.Column("effort", sa.String(), nullable=False, server_default=""),
        sa.Column("owner", sa.String(), nullable=False, server_default="you"),
        sa.Column("done", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_growth_item_kind", "growth_item", ["kind"])
    op.create_index("ix_growth_item_done", "growth_item", ["done"])

    t = sa.table(
        "growth_item",
        sa.column("kind", sa.String), sa.column("title", sa.String),
        sa.column("summary", sa.String), sa.column("why", sa.Text),
        sa.column("effort", sa.String), sa.column("owner", sa.String),
        sa.column("position", sa.Integer), sa.column("visible", sa.Boolean),
        sa.column("created_at", sa.DateTime), sa.column("updated_at", sa.DateTime),
    )
    conn = op.get_bind()
    rows = [dict(r, kind="do", position=(i + 1) * 10) for i, r in enumerate(DO)]
    rows += [dict(r, kind="build", position=(i + 1) * 10) for i, r in enumerate(BUILD)]
    for r in rows:
        conn.execute(t.insert().values(
            visible=True, created_at=sa.func.now(), updated_at=sa.func.now(), **r))


def downgrade() -> None:
    op.drop_index("ix_growth_item_done", table_name="growth_item")
    op.drop_index("ix_growth_item_kind", table_name="growth_item")
    op.drop_table("growth_item")
