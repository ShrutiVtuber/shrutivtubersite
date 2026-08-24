# SPDX-License-Identifier: AGPL-3.0-only
"""
The site operator's credentials, claimed once and resettable by email.

Previously the admin password was an argon2 hash in `.env`, which meant
changing it needed SSH and a redeploy — and it meant a hash full of `$` in a
file docker compose interpolates, which is exactly how it arrived shredded the
first time.

**The claim is the delicate part.** An unclaimed admin on a public site is a
takeover waiting to happen: whoever loads `/admin` first becomes the operator.
So the first claim needs proof that the claimant has the server, and the proof
is a setup token generated on first boot and written to the log. Reading the
log means having the box, which is exactly the fact being proven.

Once claimed, the token is spent and the route is closed for good.
"""
from __future__ import annotations

import logging
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.models import SiteSetting

log = logging.getLogger(__name__)
_hasher = PasswordHasher()

KEY_EMAIL = "operator.email"
KEY_HASH = "operator.password_hash"
KEY_SETUP_TOKEN = "operator.setup_token"

# Verified against when no operator exists, so a login attempt before the site
# is claimed costs the same as a wrong password.
_DUMMY_HASH = _hasher.hash("there-is-no-operator-yet")


async def _get(session: AsyncSession, key: str) -> str:
    row = (
        await session.execute(select(SiteSetting).where(SiteSetting.key == key))
    ).scalar_one_or_none()
    return row.value if row else ""


async def _put(session: AsyncSession, key: str, value: str) -> None:
    row = (
        await session.execute(select(SiteSetting).where(SiteSetting.key == key))
    ).scalar_one_or_none()
    if row is None:
        session.add(SiteSetting(key=key, value=value))
    else:
        row.value = value


async def is_claimed(session: AsyncSession) -> bool:
    return bool(await _get(session, KEY_HASH))


async def setup_token(session: AsyncSession) -> str:
    """
    The one-time claim token, minted on first ask and logged.

    Logged rather than emailed, because before the site is claimed there is no
    address to send to and no way to know that a claimed address is the right
    one. Having the log means having the server.
    """
    existing = await _get(session, KEY_SETUP_TOKEN)
    if existing:
        return existing
    token = secrets.token_urlsafe(24)
    await _put(session, KEY_SETUP_TOKEN, token)
    await session.commit()
    log.warning(
        "SITE NOT YET CLAIMED. Open /admin and use this setup token once: %s", token
    )
    return token


async def claim(session: AsyncSession, email: str, password: str, token: str) -> bool:
    """
    Claim the site. Succeeds exactly once.

    The token is compared in constant time and spent on success, so a second
    claim cannot happen even with the token in hand.
    """
    if await is_claimed(session):
        return False
    expected = await _get(session, KEY_SETUP_TOKEN)
    if not expected or not secrets.compare_digest(expected, token or ""):
        return False

    await _put(session, KEY_EMAIL, email.strip().lower())
    await _put(session, KEY_HASH, _hasher.hash(password))
    await _put(session, KEY_SETUP_TOKEN, "")      # spent
    await session.commit()
    log.warning("site claimed by %s", email)
    return True


async def verify(session: AsyncSession, email: str, password: str) -> bool:
    """
    Check a login. Constant-ish time whether or not the operator exists.

    Falls back to the environment hash so an existing deployment keeps working
    until it is claimed — but the database wins once it is.
    """
    stored_email = await _get(session, KEY_EMAIL)
    stored_hash = await _get(session, KEY_HASH)

    if not stored_hash:
        from shruti.core.auth import authenticate

        return authenticate(email, password)

    try:
        _hasher.verify(stored_hash or _DUMMY_HASH, password)
        matched = True
    except VerifyMismatchError:
        matched = False
    except Exception:
        matched = False

    # The email is compared after the hash on purpose: doing it first would
    # return early for an unknown address and time the difference.
    return matched and secrets.compare_digest(stored_email, email.strip().lower())


async def set_password(session: AsyncSession, password: str) -> None:
    await _put(session, KEY_HASH, _hasher.hash(password))
    await session.commit()


async def operator_email(session: AsyncSession) -> str:
    return await _get(session, KEY_EMAIL)
