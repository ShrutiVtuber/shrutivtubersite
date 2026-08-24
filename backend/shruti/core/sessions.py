# SPDX-License-Identifier: AGPL-3.0-only
"""
Reader sessions, and the single-use links that start them.

Separate from `core.auth`, which is the one-operator admin login. A reader is
not an operator: different cookie, different audience claim, different
lifetime. Mixing them would mean a reader token that the admin routes might one
day accept.

Magic links and password reset are the same primitive — a signed, expiring,
single-purpose token — so they are one function with a purpose claim rather
than two that could drift apart.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from shruti.core.config import get_settings

_hasher = PasswordHasher()

SESSION_COOKIE = "shruti_reader"
SESSION_DAYS = 30
# Long enough to walk to another device, short enough that a forwarded mail is
# not a standing key.
LINK_MINUTES = 20

AUDIENCE = "reader"

# Verified against when no such user exists, so an unknown address costs the
# same as a wrong password. Without it the timing says which is which.
_DUMMY_HASH = _hasher.hash("there-is-no-such-reader")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(stored: str | None, password: str) -> bool:
    """Constant-ish time even when the account has no password at all."""
    try:
        _hasher.verify(stored or _DUMMY_HASH, password)
        return stored is not None
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def issue_session(user_id: int, email: str) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id), "email": email, "aud": AUDIENCE,
            "iat": now, "exp": now + timedelta(days=SESSION_DAYS),
        },
        s.secret_key, algorithm="HS256",
    )


def read_session(token: str | None) -> dict | None:
    if not token:
        return None
    try:
        return jwt.decode(
            token, get_settings().secret_key,
            algorithms=["HS256"], audience=AUDIENCE,
        )
    except Exception:
        return None


def issue_link(email: str, purpose: str) -> str:
    """A single-purpose, expiring link token. `purpose` is claimed and checked."""
    s = get_settings()
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "email": email, "aud": AUDIENCE, "purpose": purpose,
            # A nonce, so two links issued in the same second differ and one
            # cannot be guessed from the other.
            "jti": secrets.token_urlsafe(8),
            "iat": now, "exp": now + timedelta(minutes=LINK_MINUTES),
        },
        s.secret_key, algorithm="HS256",
    )


def read_link(token: str | None, purpose: str) -> str | None:
    """The email if the token is valid, unexpired AND for this purpose."""
    if not token:
        return None
    try:
        claims = jwt.decode(
            token, get_settings().secret_key,
            algorithms=["HS256"], audience=AUDIENCE,
        )
    except Exception:
        return None
    # A sign-in link must not double as a password-reset link.
    if claims.get("purpose") != purpose:
        return None
    return claims.get("email")


def new_token() -> str:
    """An opaque token for confirm and unsubscribe links, stored server-side."""
    return secrets.token_urlsafe(24)
