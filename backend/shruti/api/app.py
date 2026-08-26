"""FastAPI application for shrutivtuber.com."""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shruti.api.routes import (
    accounts, admin, billing, charts, classes, collab, community, content,
    horoscopes,
    insight, journal, live, media, newsletter, passkeys, places, public,
    overlay, shop, twitch, videos
)
from shruti.core.config import get_settings
from shruti.core.db import SessionLocal
from shruti.core.logredact import install as install_log_redaction

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Attached here rather than at import, because uvicorn installs its own
    # handlers on the root logger while starting up — a filter added before
    # that is added to handlers that get replaced.
    install_log_redaction()

    # Schema is owned by alembic, never by create_all — migrations are the
    # only thing allowed to touch production DDL.

    sky = asyncio.create_task(_sky_reconciler())
    watch = asyncio.create_task(_live_watcher())
    try:
        yield
    finally:
        sky.cancel()
        watch.cancel()


# How often to look for entries published since the last pass. The work is
# trivial when there is nothing to do — one query and a directory walk — so
# this is about how soon a new entry gets its sky, not about load.
# How often to look for a stream starting. A minute is late enough to be
# polite to Twitch and early enough that a notification still means "now".
LIVE_INTERVAL_S = int(os.environ.get("SHRUTI_LIVE_WATCH_SECONDS", "60"))


async def _live_watcher() -> None:
    """
    Tell the people who asked, when a stream starts.

    On a timer rather than on the page-load check, because the page-load check
    only happens when somebody is already on the site — and the whole point of
    the notification is to reach people who are not.
    """
    from shruti.core.livewatch import watcher

    await watcher(LIVE_INTERVAL_S)


SKY_INTERVAL_S = int(os.environ.get("SHRUTI_SKY_RECONCILE_SECONDS", "900"))


async def _sky_reconciler() -> None:
    """
    Capture the publication sky for entries that do not have one yet.

    It runs on a timer rather than on a webhook because BeeRanked's agent syncs
    pages to a volume and tells us nothing when it does. A timer is late; a
    webhook we do not receive is never.

    Being late costs nothing here. The moment captured is the entry's own
    published timestamp, read from the page, so a pass that runs an hour after
    publication records the same sky as one that runs a second after it.
    """
    from shruti.api.routes.journal import reconcile_published

    # The documented deploy is `up -d --build` and then `alembic upgrade head`,
    # so on any deploy carrying a migration this task starts against a schema
    # that is a minute behind the code. It recovers on its own — the failure is
    # caught and the next pass is fine — but it recovers a quarter of an hour
    # later and leaves a traceback that looks like something is wrong. Waiting
    # out the window costs nothing: no entry needs its sky in the first minute.
    await asyncio.sleep(int(os.environ.get("SHRUTI_SKY_FIRST_PASS_SECONDS", "90")))

    while True:
        try:
            async with SessionLocal() as session:
                result = await reconcile_published(session)
            if result.get("captured") or result.get("failed"):
                log.info("[sky] %s", result)
        except asyncio.CancelledError:
            raise
        except Exception:                              # noqa: BLE001
            # A failed pass is not worth taking the API down for; the next one
            # is fifteen minutes away and the work is idempotent.
            log.exception("[sky] reconcile failed")
        await asyncio.sleep(SKY_INTERVAL_S)


app = FastAPI(
    title="shrutivtuber.com",
    version="0.1.0-dev",
    lifespan=lifespan,
    # Don't advertise the schema in production.
    docs_url=None if settings.is_production else "/api/docs",
    openapi_url=None if settings.is_production else "/api/openapi.json",
)

if not settings.is_production:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4321", "http://127.0.0.1:4321"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/api/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.env}


app.include_router(live.router)
app.include_router(content.router)
app.include_router(shop.router)
app.include_router(classes.router)
app.include_router(insight.router)
app.include_router(charts.router)
app.include_router(community.router)
app.include_router(collab.router)
app.include_router(public.router)
app.include_router(places.router)
app.include_router(twitch.router)
app.include_router(overlay.router)
app.include_router(accounts.router)
app.include_router(newsletter.router)
app.include_router(horoscopes.router)
app.include_router(journal.router)
app.include_router(passkeys.router)
app.include_router(billing.router)
app.include_router(media.router)
app.include_router(videos.router)
app.include_router(admin.router)
