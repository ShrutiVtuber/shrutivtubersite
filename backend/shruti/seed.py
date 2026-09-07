"""
Seed the content model with real data.

Idempotent — safe to re-run. Run with:
    docker compose exec backend python -m shruti.seed

Everything that is a claim about the brand (name, tagline, lore) is left
BLANK on purpose: the naming decision is unresolved, and inventing copy that
then has to be hunted down is worse than an obvious gap. Structure is seeded;
words are not.
"""

from __future__ import annotations

import asyncio

from sqlmodel import select

from shruti.core.db import SessionLocal
from shruti.models import Project, SocialLink, Tool

# ── links, in the typed taxonomy the research recommends ────────────────────
LINKS = [
    ("channels", "twitch",   "https://www.twitch.tv/shrutivtuber",                     "Twitch",   10, True),
    ("channels", "youtube",  "https://www.youtube.com/channel/UCl15ks3uuVLrgpojeLqd2Dg", "YouTube", 20, True),
    ("socials",  "discord",  "https://discord.gg/Q8FW4AZNS6",                          "Discord",  30, True),
    ("socials",  "twitter",  "https://twitter.com/ShrutiVTuber",                       "X",        40, True),
    ("code",     "github",   "https://github.com/ShrutiVtuber",                        "GitHub",   50, True),
    # Hidden by default. The old site linked github.com/ShrutiVtuber, which has
    # none of the actual work on it; the account above does.
    ("code",     "github-brand", "https://github.com/ShrutiVtuber",                    "GitHub (brand)", 51, False),
    # Hidden deliberately: this links a real legal name beside the persona.
    # Publishing it is a pseudonymity decision, not a default.
    ("socials",  "linkedin", "https://www.linkedin.com/in/shruti-swara-4416b42aa/",    "LinkedIn", 60, False),
]

# ── projects — real, verified from the repos and the live sites ─────────────
PROJECTS = [
    dict(
        slug="theourgia", name="Theourgia", position=10, visible=True, status="active",
        tagline="A magickal journal CMS and practitioner's toolkit.",
        site_url="https://theourgia.com",
        # Left blank deliberately: the public repo lives on a separate account
        # and linking it from here reintroduces exactly the cross-account
        # linkage this brand is keeping apart. theourgia.com is enough.
        repo_url="",
        body_md=(
            "Attic lunar calendar with observance days, Swiss Ephemeris astrology, "
            "planetary hours and election finding, six divination systems, sigil "
            "generation, multi-cipher gematria, an offerings ledger and entity "
            "alias-graph, and a journal that stamps every entry with what the sky "
            "was doing.\n\n"
            "Open source, self-hostable, federation-ready. AGPL-3.0."
        ),
    ),
    dict(
        slug="theourgia-mobile", name="Theourgia for phone", position=20, visible=True, status="active",
        tagline="The mobile half — everything works offline.",
        site_url="https://theourgia.com",
        repo_url="",
        body_md=(
            "Lunar and solar rites at moonrise, culmination, moonset and nadir. "
            "Nativities, elections, profections, zodiacal releasing and solar returns. "
            "Festivals from calendar packs, anchored to a date or to the sky.\n\n"
            "The ephemeris, the timezone boundaries and every computation live on the "
            "phone — because the moments this is needed are a rite before dawn and a "
            "chart cast on an aeroplane, which are the moments a network is least "
            "likely."
        ),
    ),
    dict(
        slug="astropractise", name="astropractise", position=30, visible=True, status="active",
        tagline="Learn to reason the way Hellenistic astrologers reasoned.",
        site_url="https://astropractise.theourgia.com",
        repo_url="",
        body_md=(
            "An exercise-first course in Hellenistic astrology. It teaches chart "
            "judgment by making you produce it, one factor at a time — planets, signs, "
            "places and configurations, up to full natal and electional interpretation.\n\n"
            "It makes no claim of predictive validity."
        ),
    ),
    dict(
        slug="rebetichord", name="RebetiChord", position=40, visible=True, status="active",
        tagline="Learn the tri-chord bouzouki.",
        site_url="https://rebetichord.gr",
        repo_url="",
        body_md=(
            "A learning and composition tool for the tri-chord (D–A–D) bouzouki, built "
            "around Greek dromoi, asymmetric meters and the rebetiko tradition of the "
            "1920s–50s.\n\n"
            "Built by a Greek musician for her own community."
        ),
    ),
    dict(
        # Hidden on purpose. The research is explicit: BeeRanked keeps its own
        # domain, entity and Stripe account and does NOT link back. One
        # "everything I do" site makes cross-brand exposure involuntary.
        slug="beeranked", name="BeeRanked", position=90, visible=False, status="active",
        tagline="SEO content engine — deliberately not linked from this site.",
        site_url="https://beeranked.online", repo_url="",
        body_md="Kept unlinked by design. See the hub-and-spoke note in the plan.",
    ),
]

# ── tool pages: browser-runnable demos of Theourgia ─────────────────────────
# Hidden until each is actually built. Seeded so the nav and IA exist.
TOOLS = [
    ("planetary-hours", "Planetary hours, right now",
     "The hour and its ruler for your location, with the high-latitude and DST edge cases handled — and documented.", 10),
    ("attic-calendar", "Today in the Attic calendar",
     "The Athenian lunisolar date, with the intercalation rule shown rather than hidden.", 20),
    ("isopsephy", "Isopsephy calculator",
     "Greek numerology over any text, with the cipher shown.", 30),
    ("ephemeris", "The ephemeris",
     "A month of the sky as a table — a column per body, a row per day, the way "
     "the craft has been learned since the tables were printed.", 25),
    ("natal-chart", "Natal chart",
     "A chart cast against the Swiss Ephemeris, with every point, configuration and lot.", 40),
    ("geomantic-shield", "Geomantic shield chart",
     "Four mothers to the judge, with the full shield.", 50),
    ("sigil-generator", "Sigil generator",
     "Spare's method, kameas, and formula-driven construction.", 60),
]


async def main() -> None:
    async with SessionLocal() as s:
        for category, platform, url, label, pos, visible in LINKS:
            existing = (await s.execute(
                select(SocialLink).where(SocialLink.platform == platform)
            )).scalars().first()
            if existing:
                existing.category, existing.url, existing.label = category, url, label
                existing.position, existing.visible = pos, visible
            else:
                s.add(SocialLink(category=category, platform=platform, url=url,
                                 label=label, position=pos, visible=visible))

        for p in PROJECTS:
            existing = (await s.execute(
                select(Project).where(Project.slug == p["slug"])
            )).scalars().first()
            if existing:
                for k, v in p.items():
                    setattr(existing, k, v)
            else:
                s.add(Project(**p))

        for slug, name, summary, pos in TOOLS:
            existing = (await s.execute(
                select(Tool).where(Tool.slug == slug)
            )).scalars().first()
            if existing:
                existing.name, existing.summary, existing.position = name, summary, pos
            else:
                s.add(Tool(slug=slug, name=name, summary=summary, position=pos, visible=False))

        await s.commit()

    print(f"seeded: {len(LINKS)} links, {len(PROJECTS)} projects, {len(TOOLS)} tool pages")


if __name__ == "__main__":
    asyncio.run(main())
