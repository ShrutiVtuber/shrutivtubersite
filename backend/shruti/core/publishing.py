# SPDX-License-Identifier: AGPL-3.0-only
"""
Before anything goes public: the person has agreed to what happens to it.

What somebody publishes outlives their account — anonymised, not deleted —
because other people are following it (`accounts.erase`). That is only fair
if they knew before they published, so every endpoint that makes something
public asks here first, and refuses with **428** until the agreement is on
file.

⚠ **The server refuses; the modal only asks.** The website shows the wording
in a dialog and retries after it is agreed to, but the app, the MCP drafter
and anything written later call the same endpoints — a check that lived only
in a modal would be a check the next client forgets.

⚠ **Checked by wording, not by version.** CONSENT_VERSION moves whenever any
of the consents changes; this agreement is current as long as the words the
person read are the words in force. Changing the wording asks everybody once
more, which is exactly right, and nothing else does.
"""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core.consents import PUBLISH
from shruti.models.accounts import ConsentRecord, User

# The detail the app and any other client show as-is: it has to say what to
# do without the website's dialog to explain it.
NEEDS_AGREEMENT = (
    "Before anything of yours goes public, agree to what happens to it if you "
    "delete your account — once, on your account page at shrutivtuber.com."
)


async def has_agreed_to_publish(session: AsyncSession, user: User) -> bool:
    """The latest publish decision is a yes, to the wording in force now."""
    latest = (
        await session.execute(
            select(ConsentRecord)
            .where(ConsentRecord.user_id == user.id, ConsentRecord.kind == PUBLISH.kind)
            .order_by(ConsentRecord.created_at.desc(), ConsentRecord.id.desc())
            .limit(1)
        )
    ).scalars().first()
    return latest is not None and latest.granted and latest.wording == PUBLISH.wording


async def require_publish_agreement(session: AsyncSession, user: User) -> None:
    """Refuse the publish, in words, until the agreement is on file."""
    if not await has_agreed_to_publish(session, user):
        raise HTTPException(428, NEEDS_AGREEMENT)
