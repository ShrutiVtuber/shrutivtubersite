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

from sqlmodel import Field

from shruti.models import UTC_TS

from shruti.models import TimestampMixin


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
