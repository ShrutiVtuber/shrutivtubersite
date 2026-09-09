# SPDX-License-Identifier: AGPL-3.0-only
"""
Telling people something happened — browsers and phones, one call.

⚠ **One function, five kinds, and the kind decides who hears it.** Every place
that wants to notify calls `tell()` with a kind; nothing anywhere else reads a
preference flag. Two call sites deciding for themselves who wants a video is how
somebody ends up unsubscribed from one path and not the other.

The kinds, and why each exists as its own switch:

- `live` — she has started streaming. What most people install the app for, and
  the only one that is worthless five minutes late.
- `video` — a new video is up.
- `horoscope` — the readings for a period are published.
- `writing` — a new article.
- `replies` — somebody said something about YOUR practice reading. The only
  account-scoped one; it goes to that person's devices and nobody else's.

⚠ **Nothing here raises.** A notification is a courtesy attached to something
that already happened — a stream that started, a reading that published — and
failing that action because a push service is down would be absurd.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core import fcm, push
from shruti.models import PushSubscription
from shruti.models.devices import AppDevice

log = logging.getLogger(__name__)

# kind → (the column on AppDevice, the column on PushSubscription or None)
#
# ⚠ The web table has only two switches and predates the others. A kind with no
# browser column reaches phones only, which is honest: a browser that never
# offered the choice must not be opted into it silently.
WHO: dict[str, tuple[str, str | None]] = {
    "live": ("wants_live", "wants_live"),
    "video": ("wants_video", None),
    "horoscope": ("wants_horoscope", "wants_writing"),
    "writing": ("wants_writing", "wants_writing"),
    "replies": ("wants_replies", None),
}

# A dead token. FCM says UNREGISTERED; web push says 404 or 410.
GONE = 3


@dataclass
class Sent:
    phones: int = 0
    browsers: int = 0
    pruned: int = 0

    def __bool__(self) -> bool:
        return bool(self.phones or self.browsers)


async def tell(
    session: AsyncSession, kind: str, *, title: str, body: str, url: str,
    to_user: int | None = None,
) -> Sent:
    """
    Tell whoever asked to hear about this kind of thing.

    `to_user` narrows it to one person's devices — for `replies`, which is about
    their own work and nobody else's business.
    """
    if kind not in WHO:
        raise ValueError(f"no such notification kind: {kind!r}")
    phone_flag, browser_flag = WHO[kind]
    out = Sent()

    # ── phones ──────────────────────────────────────────────────────────────
    devices = select(AppDevice).where(
        getattr(AppDevice, phone_flag).is_(True),
        AppDevice.failures < GONE,
    )
    if to_user is not None:
        devices = devices.where(AppDevice.user_id == to_user)
    for device in (await session.execute(devices)).scalars().all():
        ok, dead = await fcm.send(device.token, title=title, body=body, url=url)
        if ok:
            out.phones += 1
            device.failures = 0
            device.last_sent_at = datetime.now(timezone.utc)
        elif dead:
            # ⚠ Deleted, not counted up. FCM rate-limits senders who keep
            # asking about tokens it has already said are gone.
            await session.delete(device)
            out.pruned += 1
        else:
            device.failures += 1

    # ── browsers ────────────────────────────────────────────────────────────
    #
    # ⚠ Only for kinds a browser was actually offered, and never for a
    # person-specific one: a web subscription is not reliably tied to an
    # account, so `replies` would reach the wrong tray.
    if browser_flag and to_user is None:
        rows = (
            await session.execute(
                select(PushSubscription).where(
                    getattr(PushSubscription, browser_flag).is_(True),
                    PushSubscription.failures < GONE,
                )
            )
        ).scalars().all()
        for row in rows:
            ok, status = await push.push_one(row.endpoint)
            if ok:
                out.browsers += 1
                row.failures = 0
                row.last_sent_at = datetime.now(timezone.utc)
            elif status in (404, 410):
                await session.delete(row)
                out.pruned += 1
            else:
                row.failures += 1

    await session.commit()
    log.info("told %s: %d phones, %d browsers, %d pruned",
             kind, out.phones, out.browsers, out.pruned)
    return out
