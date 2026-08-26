"""
Content model for shrutivtuber.com.

Design rule, driven by one requirement: the site must be editable and
art-incomplete at the same time. Every display record therefore carries

    visible: bool   — hide/unhide without deleting
    position: int   — manual ordering

and every art reference is a NULLABLE foreign key to Media. A page renders
correctly with no art at all; you add it later and unhide the block.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


# TIMESTAMPTZ, not TIMESTAMP.
#
# SQLModel maps a bare `datetime` to TIMESTAMP WITHOUT TIME ZONE, which rejects
# the tz-aware values this app produces. Every instant here is UTC and must stay
# unambiguous — a schedule row that loses its offset is a stream announced at the
# wrong hour.
#
# Use sa_type, not sa_column: TimestampMixin is inherited by every table, and a
# single Column instance cannot be attached to more than one table. A type
# instance can.
UTC_TS = DateTime(timezone=True)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=_now, nullable=False, sa_type=UTC_TS)
    updated_at: datetime = Field(default_factory=_now, nullable=False, sa_type=UTC_TS)


# ── media ───────────────────────────────────────────────────────────────────
class Media(TimestampMixin, table=True):
    """Art uploaded through the admin. Served by Caddy from /media/*."""

    __tablename__ = "media"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True, unique=True)
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: int = 0
    # Where this one actually landed. Files uploaded before R2 was switched
    # on are still on disk, and must keep resolving to /media/* rather than to
    # a bucket that does not contain them.
    storage_backend: str = "local"      # local | r2

    # What she calls it. The filename is a content hash and always will be —
    # that is what makes the URL stable and the same image upload once — so the
    # human name is kept beside it and renaming never touches the file.
    title: str = ""

    # Free tags, comma-separated, for finding things again. A join table is the
    # more correct shape; at a few hundred images a string and an ILIKE is less
    # machinery for the same result. Revisit if tags ever need renaming or
    # merging rather than just matching.
    tags: str = ""

    alt_text: str = ""
    credit: str = ""          # illustrator/rigger attribution, shown where used
    credit_url: str = ""


# ── page sections ───────────────────────────────────────────────────────────
class Section(TimestampMixin, table=True):
    """
    A block on a page. The unit you toggle, reorder and edit in the admin.

    `page` is the route slug ("home", "about", "work"). `key` is stable and
    machine-readable so templates can address a specific block; `kind` tells
    the renderer which component to use.
    """

    __tablename__ = "section"

    id: Optional[int] = Field(default=None, primary_key=True)
    page: str = Field(index=True)
    key: str = Field(index=True)
    kind: str = Field(default="prose")   # prose | hero | gallery | cards | embed
    position: int = Field(default=0)
    visible: bool = Field(default=False)  # ← defaults HIDDEN: nothing ships half-done

    eyebrow: str = ""
    title: str = ""
    body_md: str = ""
    link_url: str = ""
    link_label: str = ""
    media_id: Optional[int] = Field(default=None, foreign_key="media.id")


# ── the VTuber profile block (§03 field vocabulary) ─────────────────────────
class ProfileField(TimestampMixin, table=True):
    """Birthday, height, debut date, fan name, oshi mark, stream tag, fan-art tag."""

    __tablename__ = "profile_field"

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str
    value: str
    position: int = Field(default=0)
    visible: bool = Field(default=True)


class Credit(TimestampMixin, table=True):
    """Illustrator, rigger, 3D, logo, BGM. Community etiquette; often contractual."""

    __tablename__ = "credit"

    id: Optional[int] = Field(default=None, primary_key=True)
    role: str
    name: str
    url: str = ""
    position: int = Field(default=0)
    visible: bool = Field(default=True)


class SocialLink(TimestampMixin, table=True):
    """
    A typed link taxonomy, not one flat "socials" blob.

    Research finding: serious VTuber sites group links as Channels / Socials /
    Supports / Code. Her Supports row legitimately holds GitHub Sponsors and a
    Theourgia hosted tier, which a typical VTuber's cannot — collapsing that
    into one row throws away the thing that differentiates her.
    """

    __tablename__ = "social_link"

    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(default="socials", index=True)  # channels|socials|supports|code
    platform: str            # twitch | youtube | discord | twitter | github | linkedin
    url: str
    label: str = ""
    position: int = Field(default=0)
    visible: bool = Field(default=True)


# ── work: the niche-specific surface ────────────────────────────────────────
class Project(TimestampMixin, table=True):
    """Theourgia, BeeRanked, whatever follows. See plan §04."""

    __tablename__ = "project"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    name: str
    tagline: str = ""
    body_md: str = ""
    repo_url: str = ""
    site_url: str = ""
    status: str = "active"   # active | maintained | archived

    # The credit table the /work design mandates: Name · Role · Stack ·
    # Licence · Status. It is what makes the page read as a portfolio of
    # instruments rather than an app-store listing, and it is the first thing
    # another engineer looks for — so these are columns, not prose buried in
    # body_md where nothing can query or render them consistently.
    role: str = ""           # "Author · maintainer", "Founder · lead developer"
    stack: str = ""          # "Astro · TypeScript · Postgres · Swiss Ephemeris"
    licence: str = ""        # "AGPL-3.0", "Proprietary"
    contributors: str = ""   # the mono footnote under the table

    # Which two lead the landing page. Separate from `position`, which orders
    # the full portfolio on /work — the newest thing is not always the one you
    # want a stranger to meet first, and tying the two together would mean
    # reordering the portfolio to change the front door.
    featured: bool = Field(default=False, index=True)

    position: int = Field(default=0)
    visible: bool = Field(default=True)
    media_id: Optional[int] = Field(default=None, foreign_key="media.id")


class CardDesign(TimestampMixin, table=True):
    """
    A look for the share card.

    **Rows rather than a dict in the code**, so a new design is something she
    makes on a Tuesday instead of something a developer deploys. The two that
    ship — light and dark — are seeded rows like any other, and can be edited
    or hidden the same way.

    The colours are hex, and this is the second place on the site where storing
    one is right: a card design IS a palette, the way a sponsor's brand is.

    `media_id` is an optional full-bleed backdrop, 1200x630. With one, the
    colours still matter — every word on the card is drawn in them, and a
    design whose ink disappears into its own backdrop is the failure this
    invites. The admin shows the card rendered before it is saved.
    """

    __tablename__ = "card_design"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True)
    name: str = ""

    background: str = "#F6F2EF"
    ink: str = "#26304A"
    soft: str = "#4A5470"
    faint: str = "#6E7890"
    line: str = "#DCD6DC"
    accent: str = "#A85A76"
    # One line under the name in the showcase, so a visitor knows what the
    # design is FOR rather than only what it is called.
    blurb: str = ""
    # A backdrop that ships with the application, by filename in
    # `shruti/assets`. `media_id` covers anything she uploads; this covers the
    # one that is part of the design and must exist on a fresh install.
    backdrop_asset: str = ""

    media_id: Optional[int] = Field(default=None, foreign_key="media.id")

    # Anything that would sit on a busy backdrop wants this; flat colours do
    # not. A scrim under the text rather than over the whole image, so the
    # picture is still the picture.
    scrim: bool = Field(default=False)

    position: int = Field(default=0)
    visible: bool = Field(default=True)


class Outfit(TimestampMixin, table=True):
    """
    A costume, and who drew it.

    The About page shipped this as three hard-coded slots — "base model",
    "festival outfit", "dev-stream hoodie", all with no image and a badge
    reading "3 commissions open". That is the design bundle's mock-up, and it
    meant she could not add a fourth, could not upload art she had paid for,
    and could not stop the page claiming three commissions were open.

    **The artist is a column, not a note.** Costume art is commissioned work
    and the person who drew it gets their name on it — the same rule the fan
    works gallery follows, for the same reason.
    """

    __tablename__ = "outfit"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    name: str = ""
    # "in progress", "planned", "retired", or whatever she wants to say. Free
    # text because a fixed list would be wrong the first time a costume is
    # seasonal.
    status: str = ""
    note: str = ""

    artist: str = ""
    artist_url: str = ""

    media_id: Optional[int] = Field(default=None, foreign_key="media.id")

    position: int = Field(default=0)
    visible: bool = Field(default=True)


class Sponsor(TimestampMixin, table=True):
    """
    Somebody paying to keep the channel running, and owed a proper place.

    **The colours are columns, not a stylesheet.** A sponsor arrives with a
    brand and the brand is theirs: BeeRanked's dark plum is not a decision this
    site gets to make, and it will be a different colour for the next one. So
    the background and the ink are stored per sponsor and set inline, which is
    the one place on this site where hard-coded colour is correct.

    `featured` puts them on the landing page — at most three, because a fourth
    turns a thank-you into an ad break. Everyone else is on /partners, which is
    the page that can actually say who they are and why she works with them. A
    logo with no sentence beside it asks a viewer to trust somebody on the
    strength of a rectangle.
    """

    __tablename__ = "sponsor"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    name: str = ""
    # The one line under the logo on the landing page. Short by design.
    tagline: str = ""
    # The real introduction, on /partners. Markdown.
    body_md: str = ""

    url: str = ""
    # What the link says. "Try BeeRanked" reads better than a bare domain, and
    # she is the one who knows what was agreed.
    cta_label: str = ""

    # Theirs, not the site's. Hex, validated at the edge rather than trusted.
    background: str = ""
    ink: str = ""

    # A separate mark for dark backgrounds, where one exists. Without it the
    # single logo is used on both, which is right for a wordmark that already
    # reads either way and wrong for one that does not.
    media_id: Optional[int] = Field(default=None, foreign_key="media.id")
    media_dark_id: Optional[int] = Field(default=None, foreign_key="media.id")

    # On the landing page. Capped in the route, not here — a database
    # constraint would make the fourth one an error rather than a decision.
    featured: bool = Field(default=False, index=True)

    # So a sponsorship can end without the record of it being deleted.
    since: str = ""            # ISO date, or ""
    until: str = ""            # ISO date, or "" while it is running

    position: int = Field(default=0)
    visible: bool = Field(default=True)


class OfficialPlace(TimestampMixin, table=True):
    """
    A place that is genuinely hers, listed so the ones that are not can be told apart.

    Counterfeit VTuber merch stores run as networks rather than one-offs: two of
    them share the same four nameservers and one operator, one carries
    "OFFICIAL" in its page title while its own body text says "Fan", and one
    misspells the creator's name. A creator cannot get those taken down quickly,
    but they can own the page that says which ones are real — and a page on
    their own domain is the thing they can point at.

    `kind` groups them so the page can be read at a glance, and `note` is the
    sentence that says what the place is FOR. A bare list of links asks somebody
    to trust a URL, which is the same thing the fakes are asking.

    Deliberately not merged into `SocialLink`: those are profiles to follow and
    they live in the footer. These are claims about authenticity, and the reason
    for saying them is different.
    """

    __tablename__ = "official_place"

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str = ""
    url: str = ""
    # shop | social | membership | community | other
    kind: str = Field(default="other", index=True)
    note: str = ""
    position: int = Field(default=0)
    visible: bool = Field(default=True)


class GrowthItem(TimestampMixin, table=True):
    """
    Something to do, or something to build, kept where she will see it.

    Two lists in one table because they are the same shape and differ only in
    who does them. `kind="do"` is the growth checklist — the things no engineer
    can do for her: change the Twitch category, submit a panel, ask the lawyer.
    `kind="build"` is the tools queue — ideas for things this site could ship,
    which she can add to whenever she reads a good one.

    **`why` is a column and not a nicety.** A checklist with no reasons stops
    being motivating the moment the reasoning leaves her head, and this one is
    explicitly meant to be read for motivation rather than only ticked. Every
    seeded row carries the evidence it came from.

    `done` rather than deletion: a finished item is a thing she did, and a list
    that only ever shrinks shows no progress.
    """

    __tablename__ = "growth_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    kind: str = Field(default="do", index=True)   # do | build
    title: str = ""
    # One line of what it is.
    summary: str = ""
    # Why it is worth doing, with the evidence. Markdown.
    why: str = ""
    # Rough effort, in her words — "an afternoon", "free", "a weekend".
    effort: str = ""
    # Who it needs. "you" | "me" | "both"
    owner: str = "you"
    done: bool = Field(default=False, index=True)
    position: int = Field(default=0)
    visible: bool = Field(default=True)


class Tool(TimestampMixin, table=True):
    """
    A browser-runnable tool page (planetary hours, Attic calendar, isopsephy...).

    The single strongest site-level idea in the research: each is a bookmarkable
    return-visit asset, an SEO surface, a landing destination for short-form
    clips, and a working demo of Theourgia — all in one page. Precedent:
    kawaentertainment.com ships browser tools as its primary site content.
    """

    __tablename__ = "tool"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    name: str
    # The one line. It is the page's own subtitle, its meta description and its
    # card on /tools — one row, three places, so there is nowhere for them to
    # drift apart. It used to be a literal in each .astro file, which meant a
    # correction had to be made twice and could only be made by an engineer.
    summary: str = ""
    body_md: str = ""

    # The mark beside the name. Type, not an icon — ☉ ◐ Σ.
    glyph: str = "✶"
    # Native-script subtitle where the instrument has one: पञ्चाङ्ग, Ἀττικός.
    native: str = ""
    # How /tools groups them. Not alphabetical — it is how they are used.
    category: str = ""
    # "How it is reckoned" — the passage in the aside explaining the rule the
    # instrument follows. Several hundred words of authored prose per tool, and
    # it lived in the .astro file, which put the most correction-prone writing
    # on the site behind a deploy.
    reckoned: str = ""
    # The landing page's own line for this instrument — shorter and aimed at
    # somebody who has not decided to care yet. A different job from `summary`,
    # which is why it is a different column and not the same one reused.
    landing_blurb: str = ""
    # Questions people actually arrive with, as markdown: each `### ` heading is
    # a question and the prose under it is the answer. Parsed into FAQPage
    # structured data as well as rendered, which is why the shape is fixed —
    # but it is still just markdown in a textarea.
    faq_md: str = ""
    locale: str = Field(default="en", index=True)   # en | el — Greek pages are uncontested
    position: int = Field(default=0)
    visible: bool = Field(default=False)
    media_id: Optional[int] = Field(default=None, foreign_key="media.id")


# ── schedule ────────────────────────────────────────────────────────────────
class ScheduleEntry(TimestampMixin, table=True):
    """
    Stored in UTC, always. The site converts to the visitor's timezone in the
    browser — you author in Athens time, nobody else has to do the arithmetic.
    """

    __tablename__ = "schedule_entry"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    starts_at: datetime = Field(index=True, nullable=False, sa_type=UTC_TS)  # UTC
    duration_minutes: Optional[int] = None
    platform: str = "twitch"
    url: str = ""
    notes_md: str = ""
    visible: bool = Field(default=True)


# ── inbound ─────────────────────────────────────────────────────────────────
class ContactMessage(TimestampMixin, table=True):
    __tablename__ = "contact_message"

    id: Optional[int] = Field(default=None, primary_key=True)
    kind: str = "general"        # general | business
    name: str
    email: str
    subject: str = ""
    body: str
    source_ip: str = ""
    handled: bool = Field(default=False)


class Question(TimestampMixin, table=True):
    """Question box. Nothing is public until approved."""

    __tablename__ = "question"

    id: Optional[int] = Field(default=None, primary_key=True)
    body: str
    asked_by: str = ""
    approved: bool = Field(default=False)
    answered_md: str = ""
    answered_at: Optional[datetime] = Field(default=None, nullable=True, sa_type=UTC_TS)


# ── settings ────────────────────────────────────────────────────────────────
class FanArt(TimestampMixin, table=True):
    """
    One piece in the fan-works gallery.

    The design's rule for this card is that the ARTIST CREDIT IS THE LOUDEST
    TEXT, so the artist is required and their link is a first-class field
    rather than something buried in a caption. Fan art is never recoloured and
    never presented as official.
    """

    __tablename__ = "fan_art"

    id: Optional[int] = Field(default=None, primary_key=True)
    artist: str
    artist_url: str = ""
    platform: str = ""          # where they posted it: twitter, bluesky, ...
    title: str = ""
    # Nullable like every other art reference here: a piece can be recorded
    # before its file is uploaded, and the card has a designed absent state.
    media_id: Optional[int] = Field(default=None, foreign_key="media.id")
    position: int = Field(default=0)
    visible: bool = Field(default=False)   # nothing appears until reviewed


class SiteSetting(TimestampMixin, table=True):
    """Global key/value: tagline, brand colours, feature flags."""

    __tablename__ = "site_setting"

    key: str = Field(primary_key=True)
    value: str = ""


__all__ = [
    "Media", "Section", "ProfileField", "Credit", "SocialLink",
    "Project", "Tool", "ScheduleEntry", "ContactMessage", "Question", "SiteSetting",
]



class Product(TimestampMixin, table=True):
    """
    Something for sale: a physical thing, or a file.

    **One table for both kinds.** They differ in two ways — a physical thing
    needs an address and has a finite number of it, a file needs delivering and
    does not — and are identical in every other way a screen cares about.
    Splitting them would mean writing the shop, the admin and the checkout
    twice to say the same thing.

    **Mirrored to Stripe, not owned by it.** The row here is what the shop
    renders from, so a page load is not a network call; the Stripe product and
    price are what actually take the money. They are kept in step on save.

    **Tax is per product.** Digital goods and physical goods are taxed
    differently, and a jumper is taxed differently from a book — so the code
    lives on the row rather than being a constant somebody has to remember to
    change.
    """

    __tablename__ = "product"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    name: str
    kind: str = Field(default="digital", index=True)      # physical | digital

    tagline: str = ""
    body_md: str = ""

    # Minor units, as Stripe counts them: 1100 is €11.00. Never a float —
    # money in a float is how a cent goes missing.
    price_cents: int = 0
    currency: str = "eur"

    # The picture in the shop.
    media_id: Optional[int] = Field(default=None, foreign_key="media.id")

    # What a buyer of a digital product receives. Not servable from the public
    # media path: a paid file behind a guessable URL is not a paid file.
    file_id: Optional[int] = Field(default=None, foreign_key="product_file.id")

    # How many are left. None means "as many as you like", which is what every
    # digital product is and some physical ones are.
    stock: Optional[int] = None

    # Stripe's own tax code. `txcd_10000000` is general digital goods, which is
    # what the memberships already use; physical things want their own.
    tax_code: str = "txcd_10000000"

    stripe_product_id: str = ""
    stripe_price_id: str = ""

    visible: bool = Field(default=False)
    position: int = Field(default=0)


class Discount(TimestampMixin, table=True):
    """
    A code somebody types at checkout.

    **The terms cannot be changed once it exists.** That is Stripe's rule, not
    a shortcut taken here: a coupon's percentage, amount and duration are fixed
    at creation, because a discount that could be altered afterwards would
    change what somebody was already promised. So this table follows the same
    rule — a code is created, and then it is either on or off. Changing the
    offer means making another one.

    Two things at Stripe stand behind one row: a coupon, which is the discount,
    and a promotion code, which is the word people type. Keeping them together
    here means she thinks about one thing rather than two.
    """

    __tablename__ = "discount"

    id: Optional[int] = Field(default=None, primary_key=True)
    # What they type. Stored as given; Stripe matches case-insensitively.
    code: str = Field(index=True, unique=True)
    # For her own list — never shown to a buyer.
    note: str = ""

    # One or the other, never both.
    percent_off: Optional[float] = None
    amount_off_cents: Optional[int] = None
    currency: str = "eur"

    # everything | shop | memberships
    applies_to: str = "everything"

    # How long it lasts on a subscription. A one-off purchase ignores this
    # entirely — there is no second month to discount.
    duration: str = "once"           # once | repeating | forever
    duration_months: Optional[int] = None

    max_redemptions: Optional[int] = None
    expires_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)

    active: bool = Field(default=True)

    stripe_coupon_id: str = ""
    stripe_promotion_code_id: str = ""


class Tier(TimestampMixin, table=True):
    """
    A membership.

    Was two names in a dict and two price IDs in the environment, which meant a
    third tier needed a deploy and a fourth needed a developer. It is a table
    now, for the same reason products are: what she sells is content, not
    configuration.

    The perks are one per line rather than a related table. They are a short
    list of sentences shown in one place and never queried — a table for them
    would be machinery earning nothing.

    Mirrored to Stripe like a product, except the price recurs. Changing the
    amount makes a new Stripe price and retires the old, so **anyone already
    subscribed keeps paying what they agreed to** — which is not a nicety, it
    is the only honest way to change a price under a standing arrangement.
    """

    __tablename__ = "tier"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Stable and machine-readable. Used in checkout, so changing it breaks a
    # link somebody may have open.
    key: str = Field(index=True, unique=True)
    name: str
    tagline: str = ""
    # One perk per line.
    perks: str = ""
    cta: str = ""
    # "Most common", or blank.
    badge: str = ""
    # The one drawn as the recommended column. At most one, and nothing breaks
    # if none is.
    featured: bool = Field(default=False)

    price_cents: int = 0
    currency: str = "eur"
    interval: str = "month"      # month | year

    tax_code: str = "txcd_10000000"
    stripe_product_id: str = ""
    stripe_price_id: str = ""

    visible: bool = Field(default=False)
    position: int = Field(default=0)


class ProductPhoto(TimestampMixin, table=True):
    """
    One of a product's photographs.

    A table rather than more columns, because "how many pictures does a thing
    get" is not a question with an answer — a jumper wants front, back and a
    detail; a print wants one. Columns would pick a number and be wrong for
    everything else.

    `media_id` on Product stays as the first photograph, so nothing that
    already reads it breaks; the rows here are the gallery, and the first of
    them is the one the shop leads with.
    """

    __tablename__ = "product_photo"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    media_id: int = Field(foreign_key="media.id", index=True)
    position: int = Field(default=0)


class ProductFile(TimestampMixin, table=True):
    """
    The file a digital product delivers.

    Deliberately not a `Media` row. Media is images, served straight off a
    public path by Caddy — exactly what a paid file must not be. These live
    apart, are fetched only through a route that checks the buyer first, and
    keep the original filename because a download called
    `9f2c…d1.zip` is not something anyone can use.
    """

    __tablename__ = "product_file"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Content-hashed on disk or in the bucket, like media.
    stored_name: str = Field(index=True, unique=True)
    # What it is called when it lands in someone's downloads.
    original_name: str
    mime_type: str = ""
    size_bytes: int = 0
    storage_backend: str = "local"


class Order(TimestampMixin, table=True):
    """
    One completed purchase.

    Written from the webhook, never from the browser coming back — a buyer who
    closes the tab has still bought the thing, and a buyer who reloads the
    thank-you page has not bought it twice.

    Holds what is needed to honour the sale and to answer "what did I buy?"
    six months later. The address is here because a physical order cannot be
    posted without one; it is not here for anything else.
    """

    __tablename__ = "product_order"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Stripe's session id, and the thing that makes a repeated webhook a no-op.
    checkout_session_id: str = Field(index=True, unique=True)
    payment_intent_id: str = ""

    email: str = Field(index=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    product_name: str = ""          # kept flat: the product may be renamed later
    quantity: int = 1

    amount_total_cents: int = 0
    currency: str = "eur"

    # Posted, packed, still to do. Physical only; a digital order is done the
    # moment it is paid for.
    fulfilment: str = Field(default="none", index=True)   # none | to_send | sent
    shipping_json: str = ""         # the address as Stripe gave it

    # How a buyer gets back to their file, without an account.
    download_token: str = Field(default="", index=True)
    downloads: int = 0




class Visit(TimestampMixin, table=True):
    """
    One page opened, or one tool used.

    **There is no cookie and no identifier that outlives a day.** `visitor` is a
    hash of the address, the browser string, today's date and a server secret —
    which means the same person is one number today and a different number
    tomorrow, the number cannot be turned back into an address, and nobody who
    stole this table could work out who anybody is.

    That is not an accident of implementation, it is the whole design. It is
    what makes "how many people used the isopsephy tool this week" answerable
    without tracking anybody, and it is why this needs no consent banner: there
    is nothing stored that identifies a person, so there is nothing to consent
    to.

    The cost, stated plainly: returning visitors cannot be told from new ones
    across days. That is the trade, and it is the right way round.
    """

    __tablename__ = "visit"

    id: Optional[int] = Field(default=None, primary_key=True)
    # The date, kept separately so counting by day does not mean date maths on
    # every row of a growing table.
    day: str = Field(index=True)                  # YYYY-MM-DD

    path: str = Field(index=True)
    # Empty for a page being opened; otherwise what happened on it.
    event: str = Field(default="", index=True)
    # A little JSON, for "which tool" or "which sign". Never anything typed by
    # a visitor — a tool's input is theirs, not something to collect.
    props: str = ""

    # Today's hash. Not an account, not a cookie, not reversible.
    visitor: str = Field(index=True)

    # Where they came from, reduced to a host. The full URL of a referring page
    # can carry a search query, which is somebody's words.
    referrer: str = ""


class PushSubscription(TimestampMixin, table=True):
    """
    One browser that asked to be told when she goes live.

    `endpoint` is a URL at Mozilla's or Google's push service, unique per
    browser profile. It is not an identifier of a person and cannot be used to
    reach anything except that browser's notification tray — but it IS stable
    for as long as the subscription lives, so it is the one column here worth
    treating carefully.

    No keys are stored, because nothing is encrypted: the push carries no
    payload and the service worker asks this site what to say. See
    `shruti/core/push.py` for why.

    `user_id` is set when somebody was signed in at the time, only so that
    deleting an account takes their subscriptions with it. Notifying is not
    account-gated and never will be — asking for an account before telling
    somebody a stream started is a toll booth on a favour.
    """

    __tablename__ = "push_subscription"

    id: Optional[int] = Field(default=None, primary_key=True)
    endpoint: str = Field(index=True, unique=True)
    user_id: Optional[int] = Field(default=None, foreign_key="site_user.id", index=True)

    # Which notices they want. Separate flags because "tell me when a stream
    # starts" and "tell me when a horoscope is up" are different appetites.
    wants_live: bool = True
    wants_writing: bool = False

    # For pruning: a subscription that has failed repeatedly is dead, and push
    # services rate-limit senders who keep trying gone endpoints.
    failures: int = Field(default=0)
    last_sent_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


# ── polls ───────────────────────────────────────────────────────────────────

class Poll(TimestampMixin, table=True):
    """
    A question put to whoever is reading, with the answers fixed at creation.

    **The answers cannot be edited once it exists.** Changing a label after
    people have voted silently changes what their vote meant: the count stays
    attached to a row that now says something else, and nobody can tell. A
    different set of answers is a different poll.
    """

    __tablename__ = "poll"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    question: str = ""
    # The line under it — context, or the promise about what she'll do with it.
    note: str = ""

    # ISO instant, or "". Closing by time as well as by hand, so a poll run
    # during a stream stops on its own rather than staying open for a month.
    closes_at: str = ""
    closed: bool = False
    visible: bool = True


class PollOption(TimestampMixin, table=True):
    __tablename__ = "poll_option"

    id: Optional[int] = Field(default=None, primary_key=True)
    poll_id: int = Field(foreign_key="poll.id", index=True)
    label: str = ""
    position: int = Field(default=0)


class PollVote(TimestampMixin, table=True):
    """
    One vote, and the honest limit on what "one" means.

    `voter` is the account when there is one, and otherwise the same
    daily-rotating hash the visit counter uses — address, browser, date and a
    server secret. So a signed-out person votes once a day per browser and
    cannot be recognised tomorrow, which is exactly the trade the counter
    makes. Somebody determined can vote again from another network. This is a
    poll on a VTuber's website, and the alternative is making an account a
    condition of answering a question about which game to play.
    """

    __tablename__ = "poll_vote"

    id: Optional[int] = Field(default=None, primary_key=True)
    poll_id: int = Field(foreign_key="poll.id", index=True)
    option_id: int = Field(foreign_key="poll_option.id", index=True)
    # "user:12" or "day:<hash>". Never an address.
    voter: str = Field(index=True)


# ── classes and workshops ───────────────────────────────────────────────────

class Course(TimestampMixin, table=True):
    """
    A class, or a workshop.

    **One table for both**, because a workshop is a class that happened live
    once: it has a date and a number of seats, and everything else about it —
    modules, lessons, how it is sold, who may open it — is identical. The
    edited recording sold afterwards is a *separate* course, which is what she
    asked for and what keeps this from needing special cases.

    Sold like a product and mirrored to Stripe the same way, or included with
    one or more membership tiers, or both.
    """

    __tablename__ = "course"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    title: str
    kind: str = Field(default="class", index=True)     # class | workshop

    tagline: str = ""
    body_md: str = ""
    media_id: Optional[int] = Field(default=None, foreign_key="media.id")

    price_cents: int = 0
    currency: str = "eur"
    tax_code: str = "txcd_10000000"
    stripe_product_id: str = ""
    stripe_price_id: str = ""

    # Workshops only. A class has no date and no limit.
    starts_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    minutes: Optional[int] = None
    seats: Optional[int] = None
    room_name: str = ""              # the live room, once one exists

    visible: bool = Field(default=False)
    position: int = Field(default=0)


class CourseTier(TimestampMixin, table=True):
    """
    A membership that includes a course.

    A row rather than a column because a course can be included with several
    tiers at once — she said so plainly — and a column would make that a
    comma-separated string nobody can query.
    """

    __tablename__ = "course_tier"

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    tier_key: str = Field(index=True)


class Module(TimestampMixin, table=True):
    """A part of a course. What the reference calls a section."""

    __tablename__ = "course_module"

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    title: str
    position: int = Field(default=0)


class Lesson(TimestampMixin, table=True):
    """
    One thing to watch, read, listen to, download or answer.

    **The video provider is a field.** Courses start on Bunny because at
    thirty euros Cloudflare would take a quarter of the sale, and move to
    Cloudflare when they are worth a hundred and fifty. That is a planned
    migration rather than a hypothetical one, so both can be live at once and a
    course can move one lesson at a time.
    """

    __tablename__ = "lesson"

    id: Optional[int] = Field(default=None, primary_key=True)
    module_id: int = Field(foreign_key="course_module.id", index=True)
    title: str
    kind: str = Field(default="video")      # video | text | audio | pdf | quiz
    position: int = Field(default=0)

    # Shown under a video, and the whole of a text lesson.
    body_md: str = ""

    video_provider: str = ""                # bunny | cloudflare
    video_id: str = ""
    # For the "VIDEO · 96 MIN" line. Stored rather than asked for on render.
    duration_seconds: Optional[int] = None

    # What an audio or pdf lesson hands over. Same store as a paid product
    # file, and served the same guarded way.
    file_id: Optional[int] = Field(default=None, foreign_key="product_file.id")

    # Watchable before buying. One good lesson given away sells more than a
    # locked door does.
    free_preview: bool = Field(default=False)


class QuizQuestion(TimestampMixin, table=True):
    """
    One question, for checking yourself.

    **Not graded and not gateable.** Where she certifies, the examination is a
    live reading watched by her or an assistant, or a written test sent to her,
    and a written lesson explains it. So nothing here has to decide whether
    somebody passed, which is what keeps it small — and means a quiz can never
    make somebody feel they failed a class they paid for.
    """

    __tablename__ = "quiz_question"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id", index=True)
    prompt: str
    # One per line.
    choices: str = ""
    answer_index: int = 0
    # Shown once they have answered, right or wrong. The point of a self-check
    # is the explanation, not the mark.
    explanation: str = ""
    position: int = Field(default=0)


class Entitlement(TimestampMixin, table=True):
    """
    Permission to open a course, and where it came from.

    **Kept apart from progress on purpose.** Access bought with a membership
    ends when the membership does; access bought outright never does; and
    neither has anything to do with how far somebody got. Keeping them in one
    record would make "they lose the materials but not their progress"
    impossible to honour without special cases.

    `source` matters as much as the fact of it — a purchase and a tier expire
    differently, and one "has access" flag cannot say which one just ended.
    """

    __tablename__ = "entitlement"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="site_user.id", index=True)
    course_id: int = Field(foreign_key="course.id", index=True)

    source: str = Field(default="purchase", index=True)  # purchase | tier | ticket | gift
    # Which membership granted it, so losing that one revokes only what it gave.
    tier_key: str = ""

    # Set rather than deleted, so why somebody lost access is still answerable
    # six months later when they write and ask.
    revoked_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class Enrolment(TimestampMixin, table=True):
    """
    How far somebody got, and where to put them back.

    Survives losing access. Somebody who resubscribes lands where they left
    off rather than at the beginning, which is the difference between a
    membership that is worth rejoining and one that punishes you for having
    paused.
    """

    __tablename__ = "enrolment"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="site_user.id", index=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    last_lesson_id: Optional[int] = Field(default=None, foreign_key="lesson.id")
    completed_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class LessonProgress(TimestampMixin, table=True):
    """One tick in the sidebar."""

    __tablename__ = "lesson_progress"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="site_user.id", index=True)
    lesson_id: int = Field(foreign_key="lesson.id", index=True)
    completed_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    # Where to resume a video. Not a tick — somebody can be halfway.
    seconds_watched: int = 0


# Accounts and everything that hangs off them. Imported here so metadata
# sees them and Alembic autogenerate does not miss the tables.
from shruti.models.accounts import (  # noqa: E402,F401
    BannedEmail, ConsentRecord, Horoscope, Issue, JournalSky, Nativity, Passkey,
    Subscriber, Supporter, User,
)
