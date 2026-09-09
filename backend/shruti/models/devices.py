# SPDX-License-Identifier: AGPL-3.0-only
"""
Phones that asked to be told something.

The website's browsers are in `PushSubscription`; this is the app. They are
separate tables because they are separate machinery — a browser has a push
endpoint at Mozilla or Google and is woken with an empty POST, a phone has an
FCM registration token and is sent a message — and squeezing both into one row
would mean a column that means two things.

What they share is the SHAPE of the appetite: several kinds, each its own
switch. "Tell me when a stream starts" and "tell me when somebody replied to my
reading" are different appetites, and one switch for both is how people turn
everything off.

⚠ **A token is not an identity.** It changes when the app is reinstalled, when
the user clears data, and sometimes on its own. So it is unique and replaceable,
never a key anything else points at, and `user_id` is the nullable extra — set
when somebody happens to be signed in, only so that deleting an account takes
their devices with it. Nothing here is account-gated: asking somebody to sign up
before telling them a stream started is a toll booth on a favour.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field

from shruti.models import TimestampMixin, UTC_TS


class AppDevice(TimestampMixin, table=True):
    """One installation of the app that wants to be told things."""

    __tablename__ = "app_device"

    id: Optional[int] = Field(default=None, primary_key=True)
    # FCM's registration token, or APNs'. Unique: the same phone re-registering
    # must update its row rather than collect duplicates and be told twice.
    token: str = Field(index=True, unique=True)
    platform: str = "android"          # android | ios

    user_id: Optional[int] = Field(default=None, foreign_key="site_user.id", index=True)

    # Each its own switch. Defaults chosen by what somebody installing this app
    # plainly came for: she is live, and she has posted.
    wants_live: bool = True
    wants_video: bool = True
    wants_horoscope: bool = False
    wants_writing: bool = False
    # Only meaningful with an account, because it is about THEIR work.
    wants_replies: bool = True

    # For pruning. A token that keeps failing is a phone that is gone, and FCM
    # rate-limits senders who keep asking.
    failures: int = Field(default=0)
    last_sent_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
