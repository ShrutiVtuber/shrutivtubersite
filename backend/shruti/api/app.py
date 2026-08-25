"""FastAPI application for shrutivtuber.com."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shruti.api.routes import (
    accounts, admin, billing, content, horoscopes, journal, live, media,
    newsletter, passkeys, places, public, videos,
)
from shruti.core.config import get_settings
from shruti.core.logredact import install as install_log_redaction

logging.basicConfig(level=logging.INFO)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Attached here rather than at import, because uvicorn installs its own
    # handlers on the root logger while starting up — a filter added before
    # that is added to handlers that get replaced.
    install_log_redaction()

    # Schema is owned by alembic, never by create_all — migrations are the
    # only thing allowed to touch production DDL.
    yield


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
app.include_router(public.router)
app.include_router(places.router)
app.include_router(accounts.router)
app.include_router(newsletter.router)
app.include_router(horoscopes.router)
app.include_router(journal.router)
app.include_router(passkeys.router)
app.include_router(billing.router)
app.include_router(media.router)
app.include_router(videos.router)
app.include_router(admin.router)
