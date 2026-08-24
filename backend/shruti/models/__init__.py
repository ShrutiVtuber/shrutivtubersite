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

from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=_now, nullable=False)
    updated_at: datetime = Field(default_factory=_now, nullable=False)


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
    __tablename__ = "social_link"

    id: Optional[int] = Field(default=None, primary_key=True)
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
    position: int = Field(default=0)
    visible: bool = Field(default=True)
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
    starts_at: datetime = Field(index=True)     # UTC
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
    answered_at: Optional[datetime] = None


# ── settings ────────────────────────────────────────────────────────────────
class SiteSetting(TimestampMixin, table=True):
    """Global key/value: tagline, brand colours, feature flags."""

    __tablename__ = "site_setting"

    key: str = Field(primary_key=True)
    value: str = ""


__all__ = [
    "Media", "Section", "ProfileField", "Credit", "SocialLink",
    "Project", "ScheduleEntry", "ContactMessage", "Question", "SiteSetting",
]
