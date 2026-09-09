# SPDX-License-Identifier: AGPL-3.0-only
"""
Everything the bot needs to know, from the environment.

**No URL is written down in this codebase.** The bot will live on a subdomain
first and its own domain later, and the thing that makes such a move painful is
not the code — it is every place a hostname got hard-coded. The website already
learned this when `Astro.url` reported `localhost` behind Caddy.

The token is read here and never logged, never included in an error, and never
put in a message. `ident()` exists so the logs can say *which* application is
running without saying how to be it.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass(frozen=True)
class Config:
    # Public. The application id appears in every invite link; the public key
    # is published by design — it is what verifies Discord's signatures.
    app_id: str
    public_key: str

    # Secret. Never rendered anywhere.
    token: str

    # Where the arithmetic happens. The bot never asks the website to compute
    # anything, and never asks it to store anything.
    astro_url: str

    # The website, for links only. Read-only, public endpoints only, and no
    # credential of any kind — a stronger guarantee than a promise not to write.
    site_url: str

    # Where the bot's own pages live. Separate from `site_url` precisely so
    # that moving it is a config change.
    bot_url: str

    # The channel the practice bridge carries. Empty means no bridge, which is
    # a working state rather than an error — the site simply does not announce.
    practice_channel_id: str = ""

    def configured(self) -> bool:
        return bool(self.app_id and self.token)

    def ident(self) -> str:
        """What may be said out loud about this bot."""
        return f"application {self.app_id or '(unset)'}"


def load() -> Config:
    return Config(
        app_id=_env("SHRUTI_DISCORD_APP_ID"),
        public_key=_env("SHRUTI_DISCORD_PUBLIC_KEY"),
        token=_env("SHRUTI_DISCORD_BOT_TOKEN"),
        practice_channel_id=_env("SHRUTI_DISCORD_PRACTICE_CHANNEL", ""),
        astro_url=_env("SHRUTI_ASTRO_INTERNAL", "http://shruti-astro:8000").rstrip("/"),
        site_url=_env("SHRUTI_SITE_URL", "https://shrutivtuber.com").rstrip("/"),
        bot_url=_env("VCORDBOT_URL", "https://bot.shrutivtuber.com").rstrip("/"),
    )
