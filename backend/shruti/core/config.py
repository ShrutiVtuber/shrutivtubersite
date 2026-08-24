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

    # Contact
    contact_to: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # Media
    media_root: str = "/app/media"
    max_upload_mb: int = 25

    @property
    def is_production(self) -> bool:
        return self.env.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
