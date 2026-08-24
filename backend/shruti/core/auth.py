# SPDX-License-Identifier: AGPL-3.0-only
"""
Admin authentication.

One operator, one password. There is no user table because there is no second
user, and inventing one would be more surface for no benefit.

Three decisions worth stating:

  - **Argon2id, not bcrypt or a bare hash.** The password is the only thing
    between the internet and the ability to rewrite the site.
  - **The comparison is constant-time even when the user does not exist.** A
    login that returns faster for an unknown email than a wrong password leaks
    which is which.
  - **Tokens carry an expiry and are signed with the app secret.** No server-side
    session store: there is one operator and a re-login is cheap.
"""

from __future__ import annotations

import hmac
import logging
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from shruti.core.config import get_settings

log = logging.getLogger(__name__)

_hasher = PasswordHasher()
SESSION_HOURS = 12

# Verified against this when no admin is configured, so an unknown-user login
# costs the same as a wrong-password login. Without it the timing difference
# tells an attacker whether they have the right address.
_DUMMY_HASH = _hasher.hash("there-is-no-such-operator")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        _hasher.verify(stored_hash or _DUMMY_HASH, password)
        return bool(stored_hash)
    except VerifyMismatchError:
        return False
    except Exception:                       # noqa: BLE001 — a malformed hash is a no
        log.warning("stored password hash could not be parsed")
        return False


def authenticate(email: str, password: str) -> bool:
    s = get_settings()
    # Always run the hash comparison, even when the email is wrong, so both
    # failures take the same time.
    password_ok = verify_password(password, s.admin_password_hash)
    email_ok = hmac.compare_digest(
        (email or "").strip().lower(), (s.admin_email or "").strip().lower()
    )
    return bool(s.admin_email and s.admin_password_hash and email_ok and password_ok)


def issue_token(email: str) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": email, "iat": now, "exp": now + timedelta(hours=SESSION_HOURS),
         "scope": "admin"},
        s.secret_key,
        algorithm="HS256",
    )


def read_token(token: str) -> str | None:
    """The subject if the token is valid and unexpired, else None."""
    s = get_settings()
    if not s.secret_key:
        return None
    try:
        claims = jwt.decode(token, s.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    if claims.get("scope") != "admin":
        return None
    return claims.get("sub")
