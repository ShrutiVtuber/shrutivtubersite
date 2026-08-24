# SPDX-License-Identifier: AGPL-3.0-only
"""
Which origins this site answers as.

One definition, because there are now two places that need it and they must
not disagree: a passkey is scoped to a domain, and a Checkout return URL sends
somebody's browser there after they have paid. Both are cases where trusting a
request header outright would let an attacker choose the destination — a
credential minted for somewhere else, or a "payment complete" page under
somebody else's control.

So the header never introduces an origin. It only ever PICKS one from a list
that configuration decides.

Local development is on that list off production because there is no other way
to try a passkey or walk a test checkout on a laptop, and both of those are
things that must be tried before they are trusted.
"""
from __future__ import annotations

from urllib.parse import urlparse

from shruti.core.config import get_settings

DEV_ORIGINS = (
    "http://localhost:8200", "http://127.0.0.1:8200",
    "http://localhost:4321", "http://127.0.0.1:4321",
)


def allowed() -> list[str]:
    """The configured site first — it stays the default when nothing matches."""
    settings = get_settings()
    origins = [(settings.site_url or "http://localhost:8200").rstrip("/")]
    if not settings.is_production:
        origins += list(DEV_ORIGINS)
    origins += [
        o.strip().rstrip("/")
        for o in (settings.passkey_origins or "").split(",")
        if o.strip()
    ]
    return list(dict.fromkeys(origins))


def resolve(sent: str | None) -> str:
    """
    The origin in play for this request, from its `Origin` header.

    An unrecognised one falls back to the configured site rather than raising:
    for a passkey the WebAuthn check then fails, which is the right outcome,
    and for a return URL the payer lands on the real site, which is also right.
    """
    origins = allowed()
    candidate = (sent or "").rstrip("/")
    return candidate if candidate in origins else origins[0]


def relying_party(sent: str | None) -> tuple[str, str]:
    """`(rp_id, origin)` — the WebAuthn pair."""
    origin = resolve(sent)
    return (urlparse(origin).hostname or "localhost"), origin
