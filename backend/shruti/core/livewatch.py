# SPDX-License-Identifier: AGPL-3.0-only
"""
Notice when she goes live, and tell the people who asked.

**A false "she is live" is expensive.** It sends people to an empty channel and
teaches them to ignore the next one, which is the only thing a notification has
to be trusted about. So this is deliberately conservative:

  - It fires on a **transition**, offline to live, and never on a state it
    already knew about.
  - The last state is **written down**, so a restart or a deploy does not
    re-announce a stream that has been running for an hour.
  - Two platforms flapping do not double-send: one notice per going-live, with
    a floor on how soon another can follow.
  - A platform erroring is **not** offline. Twitch returning 500 must not read
    as "the stream ended" and then as "she is live!" a minute later.

The check itself is the same one the site already makes for the badge, so this
adds a poll rather than a second source of truth.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

log = logging.getLogger(__name__)

# The state we remember between passes, so a restart does not re-announce.
LAST_STATE = "live.last_state"          # "live" | "offline"
LAST_NOTIFIED = "live.last_notified"    # ISO instant

# Long enough that a flapping API cannot spam, short enough that a genuine
# second stream in a day still gets announced.
QUIET_HOURS = 6


async def _remember(session, key: str, value: str) -> None:
    from shruti.core.settings_store import put_many

    await put_many(session, {key: value})


async def check_once() -> dict:
    """
    One pass. Returns what it saw and what it did, for the admin and for tests.

    Never raises: this runs on a timer inside the app, and an exception here
    would kill the loop silently and leave notifications quietly not happening.
    """
    from sqlmodel import select

    from shruti.core import live
    from shruti.core.db import SessionLocal
    from shruti.core.settings_store import get_many

    try:
        status = await live.status()
    except Exception:                                  # noqa: BLE001
        log.info("live check failed; leaving the remembered state alone")
        return {"checked": False}

    platforms = getattr(status, "platforms", []) or []
    # A platform that errored is UNKNOWN, not offline. Treating an outage as
    # "the stream ended" is how a watcher invents a going-live event the
    # moment the outage clears.
    known = [p for p in platforms if not getattr(p, "error", None)]
    if not known:
        return {"checked": False, "reason": "every platform errored"}

    is_live = any(getattr(p, "is_live", False) for p in known)
    now = datetime.now(timezone.utc)

    async with SessionLocal() as session:
        state = await get_many(session, (LAST_STATE, LAST_NOTIFIED))
        was = state.get(LAST_STATE, "")
        last_at = state.get(LAST_NOTIFIED, "")

        await _remember(session, LAST_STATE, "live" if is_live else "offline")

        if not is_live or was == "live":
            return {"checked": True, "live": is_live, "sent": 0}

        # First pass after a restart with no remembered state: record it and
        # say nothing. Otherwise every deploy during a stream announces it.
        if was == "":
            log.info("first live check; recording state without announcing")
            return {"checked": True, "live": is_live, "sent": 0, "reason": "first pass"}

        if last_at:
            try:
                since = now - datetime.fromisoformat(last_at)
                if since < timedelta(hours=QUIET_HOURS):
                    return {"checked": True, "live": True, "sent": 0,
                            "reason": "within the quiet window"}
            except ValueError:
                pass

        title = ""
        # The site's own page rather than the platform's: it carries the
        # embed and the links, and it is the address that keeps working when
        # she moves platforms.
        url = "/videos"
        for p in known:
            if getattr(p, "is_live", False):
                title = getattr(p, "title", "") or ""
                break

        from shruti.api.routes import community
        from shruti.core.push import configured, push_one
        from shruti.models import PushSubscription

        if not configured():
            return {"checked": True, "live": True, "sent": 0,
                    "reason": "push is not set up"}

        community._notice.update({
            "kind": "live",
            "title": "Shruti is live",
            "body": title[:200] or "The stream has started.",
            "url": url,
            "at": __import__("time").monotonic(),
        })

        rows = (
            await session.execute(select(PushSubscription))
        ).scalars().all()
        rows = [r for r in rows if r.wants_live]

        sent = gone = 0
        for row in rows:
            ok, code = await push_one(row.endpoint)
            if ok:
                sent += 1
                row.last_sent_at = now
            elif code in (404, 410):
                gone += 1
                await session.delete(row)
        await _remember(session, LAST_NOTIFIED, now.isoformat())
        await session.commit()

        log.info("announced a stream to %s subscriber(s)", sent)
        return {"checked": True, "live": True, "sent": sent, "gone": gone,
                "of": len(rows), "title": title}


async def watcher(interval_seconds: int) -> None:
    """The loop. Sleeps first, so a restart storm does not hammer Twitch."""
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            await check_once()
        except asyncio.CancelledError:
            raise
        except Exception:                              # noqa: BLE001
            log.exception("the live watcher hit something and will keep going")
