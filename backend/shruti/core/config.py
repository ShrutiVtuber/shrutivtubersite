"""Settings. Everything comes from the environment; nothing is hardcoded."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SHRUTI_", env_file=".env", extra="ignore", case_sensitive=False
    )

    env: str = "development"
    site_url: str = "http://localhost:8200"
    secret_key: str = ""

    # Postgres. A dedicated instance — never theourgia's.
    database_url: str = "postgresql+asyncpg://shruti:shruti@postgres:5432/shruti"

    # Admin
    admin_email: str = ""
    admin_password_hash: str = ""

    # Twitch — the client secret lives here and only here.
    twitch_client_id: str = ""
    twitch_client_secret: str = ""
    twitch_login: str = "shrutivtuber"
    live_cache_ttl: int = 60

    # YouTube
    youtube_channel_id: str = ""
    youtube_api_key: str = ""

    # Which platform the "watch now" button points at during a simulcast. Both
    # are reported either way; this only decides the single call to action.
    primary_platform: str = "twitch"

    # Contact / transactional email
    contact_to: str = ""
    resend_api_key: str = ""
    # Must be an address on a domain verified in Resend. Never the visitor's
    # own address — that fails SPF for their domain.
    resend_from: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # Media
    media_root: str = "/app/media"
    # ── Cloudflare R2, S3-compatible object storage ─────────────────────
    #
    # All four must be present for R2 to be used at all; with any of them
    # missing, uploads go to local disk exactly as before. That is deliberate:
    # a half-configured bucket should degrade to something that works rather
    # than fail at the moment someone uploads a file.
    r2_account_id: str = ""
    r2_bucket: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    # The public read URL — an r2.dev address or a custom domain. Without it
    # the app serves media itself and R2 is write-only, which works but wastes
    # the point of a CDN.
    r2_public_base: str = ""

    max_upload_mb: int = 25

    @property
    def is_production(self) -> bool:
        return self.env.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
