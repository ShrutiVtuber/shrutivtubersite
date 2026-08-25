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
    summary: str = ""
    body_md: str = ""
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


# Accounts and everything that hangs off them. Imported here so metadata
# sees them and Alembic autogenerate does not miss the tables.
from shruti.models.accounts import (  # noqa: E402,F401
    BannedEmail, ConsentRecord, Horoscope, Issue, JournalSky, Nativity, Passkey,
    Subscriber, Supporter, User,
)
