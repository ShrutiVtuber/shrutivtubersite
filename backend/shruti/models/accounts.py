# SPDX-License-Identifier: AGPL-3.0-only
"""
Accounts, consents, nativities, the newsletter and the horoscopes.

**Not a social platform.** One person keeping their own chart and their own
reading. There is no public profile, no avatar, no follower count and no public
page, and the absence is deliberate rather than unbuilt.

Three things here are shaped by law rather than by preference, and they are the
parts not to simplify:

  - **Three consents, recorded separately**, each with the version and the exact
    wording that was agreed, when, and from where. Birth data processed to
    produce an astrological reading arguably reveals philosophical belief, which
    would make it special-category data under GDPR Article 9 — so its lawful
    basis is explicit consent, and consent you cannot evidence is consent you do
    not have.
  - **Withdrawing the nativity consent deletes the nativity.** The account
    survives; the birth data does not.
  - **Deletion reaches the newsletter list**, not only the account. A deleted
    account that keeps receiving mail is the failure people actually complain
    about.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from shruti.models import UTC_TS, TimestampMixin


class User(TimestampMixin, table=True):
    """A reader. Nothing here is public."""

    __tablename__ = "site_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    # Null for a magic-link-only account: a password is optional, not required.
    password_hash: Optional[str] = Field(default=None)

    display_name: str = ""
    timezone: str = ""
    reading_language: str = "en"
    # Reading preferences, not settings-page trivia: they decide which of two
    # incompatible reckonings a page shows first.
    preferred_tradition: str = ""     # hellenistic | vedic | ""
    house_system: str = ""
    ayanamsa: str = ""

    email_verified_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    last_seen_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class ConsentRecord(TimestampMixin, table=True):
    """
    One consent decision, as given or withdrawn.

    Append-only: withdrawing writes a new row rather than editing the old one,
    because the question the law asks is "what did they agree to, and when" and
    an overwritten row cannot answer it.

    The WORDING is stored, not a reference to it. If the text on the form
    changes next year, the record still says what this person actually read.
    """

    __tablename__ = "consent_record"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="site_user.id", index=True)
    # Recorded before an account exists, for newsletter-only subscribers.
    email: str = Field(index=True)

    kind: str = Field(index=True)      # account | nativity | newsletter
    granted: bool = True
    version: str = ""                  # the consent text's version
    wording: str = ""                  # verbatim, as shown
    lawful_basis: str = ""             # contract | consent | explicit-consent
    source: str = ""                   # signup-form | account-settings | unsubscribe-link


class Nativity(TimestampMixin, table=True):
    """
    A saved birth moment. Deleted when its consent is withdrawn.

    `birth_time` is nullable and that is a FIRST-CLASS STATE, not missing data:
    the ascendant moves a degree every four minutes, so without a time the
    angles, houses and sect are undefined and the chart says so rather than
    guessing.
    """

    __tablename__ = "nativity"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="site_user.id", index=True)
    label: str = ""

    birth_date: str                                   # ISO date
    birth_time: Optional[str] = Field(default=None)   # HH:MM, or null
    time_unknown: bool = False

    place_name: str = ""
    lat: float = 0.0
    lon: float = 0.0
    elevation: float = 0.0
    # The IANA zone NAME, so the offset can be resolved for that date rather
    # than assumed from today's rules.
    timezone: str = ""
    utc_offset_minutes: Optional[int] = Field(default=None)


class Subscriber(TimestampMixin, table=True):
    """
    A newsletter address.

    **Double opt-in is mandatory**: an unconfirmed address is not consent, so
    nothing is sent until `confirmed_at` is set.
    """

    __tablename__ = "subscriber"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    user_id: Optional[int] = Field(default=None, foreign_key="site_user.id", index=True)

    confirmed_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    unsubscribed_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    # A pause keeps more people than an unsubscribe loses, and nothing is
    # deleted by it — consent stays intact.
    paused_until: Optional[str] = Field(default=None)

    # Which sections they want.
    wants_horoscope: bool = True
    wants_videos: bool = True
    wants_streams: bool = True
    wants_articles: bool = True
    cadence: str = "monthly"           # monthly | paused

    # Single-use, for confirm and for one-click unsubscribe with no login.
    confirm_token: str = Field(default="", index=True)
    unsubscribe_token: str = Field(default="", index=True)


class Horoscope(TimestampMixin, table=True):
    """
    One reading: one sign, one period, one month. Written by hand.

    The period column exists now even though only `monthly` is published, so
    daily, seasonal and yearly are a switch rather than a rebuild.
    """

    __tablename__ = "horoscope"

    id: Optional[int] = Field(default=None, primary_key=True)
    sign: str = Field(index=True)      # aries … pisces
    period: str = Field(default="monthly", index=True)
    # The period this reading is FOR: "2026-09" monthly, "2026-09-14" daily.
    covers: str = Field(index=True)

    body_md: str = ""
    published: bool = False
    published_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class Issue(TimestampMixin, table=True):
    """A newsletter issue. Public in the archive once sent."""

    __tablename__ = "issue"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    subject: str = ""
    # The hand-written part — the reason people subscribe.
    letter_md: str = ""
    sent_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    visible: bool = Field(default=False)


class JournalSky(TimestampMixin, table=True):
    """
    The sky at a moment in a journal entry's life.

    Theourgia stamps every record with what the world was doing when it was
    made, and a journal of practice deserves the same. The rules it follows,
    which this keeps:

      - **The captured instant is the moment being described**, not the moment
        of capture and not a re-reading later. An entry written under a Mars
        hour was written under a Mars hour; re-casting it next year would
        quietly replace that with something else.
      - **It is the machine's half of the record and is not editable.** Being
        able to edit it would make the record untrustworthy. There is no admin
        surface for changing these values, only for capturing them.
      - **Every absence states its reason.** A null sky carries why, so a
        reader sees "the ephemeris could not be reached" rather than a blank.

    Stored rather than recomputed on read, which is the other half of the
    point: rendering a journal index should not cast twelve charts.

    Keyed by the entry's slug and the moment it describes, because the entries
    themselves live in BeeRanked. This table holds only what BeeRanked cannot
    know.

    Two moments are kept, and they are different questions:

      - ``published`` — when it went up. Discoverable: BeeRanked stamps it into
        the synced page, so this one is captured without being asked.
      - ``written`` — when she started writing it. **Not** discoverable:
        BeeRanked records no creation time and exposes none, so this is hers to
        record or it does not exist. The interesting sky for practice is often
        this one — a piece begun under a Mars hour and published on a Thursday
        was begun under a Mars hour.
    """

    __tablename__ = "journal_sky"

    id: Optional[int] = Field(default=None, primary_key=True)
    # The BeeRanked entry this describes. One row per entry per moment.
    slug: str = Field(index=True)
    # Which moment: "published" or "written".
    kind: str = Field(default="published", index=True)

    # The moment described. Not the moment of capture.
    at: datetime = Field(sa_type=UTC_TS)
    lat: float = 0.0
    lon: float = 0.0
    place_name: str = ""

    # The whole reading as the daemon returned it, so a renderer can show more
    # later without a migration and without re-casting anything.
    reading: str = ""            # JSON

    # A short line for indexes and cards, composed once at capture.
    summary: str = ""

    # Why `reading` is empty. Empty itself when the capture succeeded.
    failure_reason: str = ""

    # One record per entry per moment — and never two of the same moment, so a
    # duplicate webhook cannot quietly overwrite a capture with a later sky.
    __table_args__ = (UniqueConstraint("slug", "kind", name="journal_sky_slug_kind_key"),)


class Passkey(TimestampMixin, table=True):
    """
    A registered passkey — WebAuthn credential.

    **Why passkeys rather than "sign in with Google".** A passkey is a keypair
    held by the device or the platform keychain. Signing in with one tells
    Apple or Google nothing about this site, sends them no request, and hands
    this site no third-party identity to store. It is a phone unlock rather
    than a federated login, which is both the nicer experience and the more
    private one — and on a site whose whole posture is minimal data sharing,
    OAuth would have been the odd choice.

    One row per credential, because a person reasonably has several: the phone,
    the laptop, a hardware key in a drawer.

    `sign_count` is the authenticator's own counter. Where a device provides it,
    a value that goes BACKWARDS means the credential has probably been cloned,
    and the sign-in is refused rather than merely logged. Many platform
    authenticators always send zero, which is not a warning and is treated as
    "not supported" rather than as a failure.
    """

    __tablename__ = "passkey"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Exactly one of these. A passkey belongs to a reader or to the operator.
    user_id: Optional[int] = Field(default=None, foreign_key="site_user.id", index=True)
    is_operator: bool = Field(default=False, index=True)

    credential_id: str = Field(index=True, unique=True)   # base64url
    public_key: str = ""                                  # base64url COSE key
    sign_count: int = 0
    transports: str = ""                                  # "internal,hybrid"

    # So a person can tell one key from another when removing it.
    label: str = ""
    last_used_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class Supporter(TimestampMixin, table=True):
    """
    Someone who has given money — once, or every month.

    **Not a copy of Stripe's data.** Stripe is the ledger; this table is the
    minimum needed to answer two questions without a round trip on every page
    load: does this person have an active subscription, and which customer are
    they in Stripe. Anything else — invoices, cards, amounts — is looked up
    live or not at all, because a stale copy of a billing record is worse than
    no copy.

    `user_id` is nullable on purpose. A one-off gift needs no account, and
    requiring one to give someone money would lose most of the gifts.
    """

    __tablename__ = "supporter"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="site_user.id", index=True)
    email: str = Field(default="", index=True)

    stripe_customer_id: str = Field(default="", index=True)
    stripe_subscription_id: str = Field(default="", index=True)

    # Stripe's own vocabulary, kept verbatim: active, trialing, past_due,
    # canceled, incomplete. Translating it here would mean maintaining a
    # mapping that drifts every time Stripe adds a state.
    status: str = ""
    tier: str = ""                       # "lamplighter" | "almanac"
    # Set when someone cancels: the subscription stays active until this date
    # rather than stopping mid-month, and the account page has to say so.
    cancel_at_period_end: bool = False
    current_period_end: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class BannedEmail(TimestampMixin, table=True):
    """
    An address that may not register again.

    **A hash, not the address.** A ban follows a deletion, and the deletion was
    the point — keeping a readable list of the addresses just deleted would
    quietly rebuild the thing that was meant to go. A SHA-256 of the normalised
    address answers the only question ever asked of it, "is this one banned?",
    and cannot be read back into a mailing list.

    Still liftable: she types the address to unban it and the hash matches.

    The reason is kept in the clear because it is her note about a decision she
    made, not data about them — and a ban with no reason recorded is one nobody
    can review later, including her.
    """

    __tablename__ = "banned_email"

    id: Optional[int] = Field(default=None, primary_key=True)
    email_hash: str = Field(index=True, unique=True)
    reason: str = ""
    # Kept so the list can be read at all: "s…a@gmail.com" is enough to
    # recognise one you are looking for without being an address.
    hint: str = ""


class SavedChart(TimestampMixin, table=True):
    """
    A chart somebody kept, with or without an account.

    **Two tokens, not one, and the reason is the whole design.** `owner_token`
    is how the person gets back to their own chart; `share_token` is what they
    hand to a friend. One token would make those the same string, so sharing
    would mean giving away your only way in, and unsharing would be impossible
    — you cannot take a link back out of somebody's messages, but you can stop
    it working.

    Neither token is guessable and neither carries birth data. That keeps the
    date, time and place out of the URL, out of a browser history and out of a
    screenshot of the address bar. It does **not** keep them from a person who
    can read a chart: the ascendant gives the birth time to within a few
    minutes and the planets give the date. So the figure is the data, drawn,
    and the share dialogue says so rather than implying a privacy the drawing
    cannot provide.

    **This row holds special-category data.** Birth data used for an
    astrological reading arguably reveals philosophical belief, so its lawful
    basis is explicit consent — the same rule as `Nativity`. An account holder
    has that consent on record against their account. Somebody without an
    account has no account to hang it on, so the consent is evidenced *here*,
    verbatim and versioned, on the row it justifies. Consent you cannot
    evidence is consent you do not have.

    And because it cannot be renewed by asking somebody we have no address
    for, an ownerless chart **expires**. Opening it puts the clock back.
    """

    __tablename__ = "saved_chart"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Opaque, unguessable, and carrying nothing. See the class docstring.
    owner_token: str = Field(index=True, unique=True)
    # Null until they choose to share; nulled again when they take it back.
    share_token: Optional[str] = Field(default=None, index=True, unique=True)

    # Null for a chart kept without an account. Set when one is made later,
    # so signing up brings the chart along rather than stranding it.
    user_id: Optional[int] = Field(default=None, foreign_key="site_user.id", index=True)

    # Theirs to write. Shown to whoever holds a share link, so it is the one
    # field that must never be pre-filled with anything private.
    label: str = ""

    # Which reckoning, kept so re-opening draws the same chart rather than
    # today's defaults.
    tradition: str = "hellenistic"        # hellenistic | vedic
    house_system: str = "whole_sign"
    # wheel | north | south. North and South Indian are different diagrams,
    # not styles of one, and some people want to see both.
    figure: str = "wheel"

    # The moment. `time_unknown` is a first-class state: without a time the
    # angles are undefined, and the chart says so rather than guessing.
    birth_date: str = ""                              # ISO date
    birth_time: Optional[str] = Field(default=None)   # HH:MM
    time_unknown: bool = False
    place_name: str = ""
    lat: float = 0.0
    lon: float = 0.0

    # The consent that makes holding the above lawful, stored verbatim so the
    # record still says what this person actually read after the wording
    # changes. Empty when the chart belongs to an account, where the consent
    # lives on the account.
    consent_version: str = ""
    consent_wording: str = ""
    consent_source: str = ""
    consent_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)

    shared_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    last_seen_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    # Null for a chart with an owner. Set, and pushed forward on every
    # opening, for one without.
    expires_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
