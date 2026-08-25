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

    # ── Stripe ──────────────────────────────────────────────────────────
    #
    # Subscriptions and one-off gifts. As with R2, a half-configured Stripe
    # degrades to the page's honest absent state rather than to a button that
    # fails at the moment someone tries to give money — which is the single
    # worst moment for anything on this site to break.
    #
    # Card details never reach this server: payment happens on Stripe's hosted
    # Checkout, and managing or cancelling a subscription happens on Stripe's
    # hosted Customer Portal. That is not laziness — it keeps the site outside
    # PCI scope entirely, and the Portal IS the one-click cancellation.
    # ── video, for classes ──────────────────────────────────────────────
    # Bunny first because at thirty euros a course Cloudflare would take a
    # quarter of the sale. Cloudflare later, when a course is worth a hundred
    # and fifty and one provider matters more than the money.
    bunny_library_id: str = ""
    bunny_stream_api_key: str = ""
    bunny_cdn_hostname: str = ""
    # What makes a playback URL expire. Without it a paid lecture is one
    # copied link from being public.
    bunny_token_auth_key: str = ""
    cloudflare_stream_domain: str = ""

    # ── the live room, for workshops ────────────────────────────────────
    # The subdomain only, not the whole host: the API wants the name and the
    # embed wants the host, and normalising once here beats remembering which
    # is which at every call site.
    daily_domain: str = ""
    daily_api_key: str = ""

    stripe_secret_key: str = ""
    # Whether a listed price already contains the tax. Inclusive is what the
    # memberships use and what a European shopper expects — the number on the
    # page is the number they pay. A setting rather than a constant because
    # physical goods sold elsewhere often are not priced that way, and finding
    # that out should not need a migration.
    stripe_tax_behavior: str = "inclusive"
    # Where physical things can be posted. Empty means everywhere Stripe will
    # take an address for, which is the honest reading of "I have not said".
    # Narrowing it is a decision to make deliberately, not one to arrive at by
    # leaving a default alone.
    shop_ship_to: list[str] = []
    stripe_publishable_key: str = ""
    # Signs the webhook. Without it every webhook is refused, because an
    # unverified webhook is an open endpoint for inventing subscriptions.
    stripe_webhook_secret: str = ""
    # Price IDs from the Stripe dashboard. Kept in configuration rather than
    # in code so a price can change without a deploy — and the page reads the
    # amount back FROM Stripe, so what is displayed is always what will be
    # charged.
    stripe_price_lamplighter: str = ""
    stripe_price_almanac: str = ""
    # The product tax code, required because Managed Payments is on: Stripe
    # acts as merchant of record and settles VAT, which for a Greek creator
    # selling digital subscriptions across the EU is the difference between
    # this being simple and it being a MOSS registration.
    #
    # `txcd_10000000` is Stripe's general "Electronically Supplied Services",
    # which is how a creator membership is treated for EU VAT. **Confirm it
    # with an accountant** — it decides what VAT gets charged, which is not a
    # decision that belongs in a default. Configurable so changing it is not a
    # deploy.
    stripe_tax_code: str = "txcd_10000000"

    # Extra origins this site answers as, comma separated. Normally blank; see
    # shruti/core/origins.py for why a request header can never add one.
    passkey_origins: str = ""

    @property
    def stripe_enabled(self) -> bool:
        """Checkout needs a key. Subscriptions additionally need a price."""
        return bool(self.stripe_secret_key)

    @property
    def stripe_is_test(self) -> bool:
        """
        Whether the keys in use are test keys.

        Worth asking out loud, because a production site running test keys
        looks exactly like one that works: checkout opens, the card form
        accepts a test number, the thank-you page appears — and no money moves.
        The failure is silent and on the wrong side of the sale, so it is
        surfaced rather than left to be noticed.
        """
        return self.stripe_secret_key.startswith("sk_test")

    @property
    def is_production(self) -> bool:
        return self.env.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
