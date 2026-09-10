# SPDX-License-Identifier: AGPL-3.0-only
"""
The few REST calls the bot makes outward.

Posting a message is the only thing it does that Discord did not ask for
first, and it needs no gateway and no privileged intent — a bot with Send
Messages in a channel may post to it.
"""
from __future__ import annotations

import logging

import httpx

log = logging.getLogger("vcordbot.discord")

API = "https://discord.com/api/v10"


class DiscordError(RuntimeError):
    pass


async def post_and_tell_id(
    channel_id: str, token: str, *, content: str = "",
    embed: dict | None = None, allowed_role: str = "",
    client: httpx.AsyncClient | None = None,
) -> str | None:
    """
    Send one message and return its id.

    ⚠ `post_message` answers only whether it landed, which is all an
    announcement needs. A bridge needs the id: a reaction arrives naming a
    message, and with nothing to match it against it is a number on nothing.

    Returns None on any failure, for the same reason `post_message` returns
    False — a Discord outage must not fail somebody's submission.
    """
    payload: dict = {
        "allowed_mentions": {"parse": [],
                             "roles": [allowed_role] if allowed_role else []},
    }
    if content:
        payload["content"] = content
    if embed:
        payload["embeds"] = [embed]

    async def _send(c: httpx.AsyncClient) -> str | None:
        r = await c.post(f"{API}/channels/{channel_id}/messages",
                         json=payload,
                         headers={"Authorization": f"Bot {token}",
                                  "User-Agent": "vcordbot/1.0"},
                         timeout=10.0)
        if r.status_code in (403, 404, 429):
            log.warning("could not post to %s: %s", channel_id, r.status_code)
            return None
        r.raise_for_status()
        return str((r.json() or {}).get("id") or "") or None

    try:
        if client is not None:
            return await _send(client)
        async with httpx.AsyncClient() as c:
            return await _send(c)
    except Exception as exc:                       # noqa: BLE001
        log.warning("could not post: %s", type(exc).__name__)
        return None


#: Which channel a thread hangs under, remembered so Discord is asked once.
#: A plain channel maps to itself; anything unreachable maps to "" and is not
#: asked about again, so a message from a channel we cannot see does not become
#: an API call per message for the life of the process.
_parents: dict[str, str] = {}


async def parent_of(channel_id: str, token: str,
                    client: httpx.AsyncClient | None = None) -> str:
    """
    The channel a thread belongs to, or the channel itself.

    ⚠ **A message posted in a thread carries the THREAD's id as its
    `channel_id`.** Nothing in the payload names the parent. So a reader that
    only compares `channel_id` against the channel it watches drops every reply
    inside every thread — including the threads the bot opened itself, which is
    exactly where the conversation was moved to.

    Asked once per channel and cached. The answer cannot change: a thread does
    not migrate to another parent.
    """
    if not channel_id:
        return ""
    if channel_id in _parents:
        return _parents[channel_id]

    async def _ask(c: httpx.AsyncClient) -> str:
        r = await c.get(f"{API}/channels/{channel_id}",
                        headers={"Authorization": f"Bot {token}",
                                 "User-Agent": "vcordbot/1.0"},
                        timeout=10.0)
        if r.status_code != 200:
            return ""
        data = r.json() or {}
        # `parent_id` is set on a thread and on a channel inside a category.
        # A thread's type is 10, 11 or 12; a channel in a category is not one
        # of those and is its own parent for this purpose.
        if data.get("type") in (10, 11, 12):
            return str(data.get("parent_id") or "")
        return str(data.get("id") or "")

    try:
        if client is not None:
            found = await _ask(client)
        else:
            async with httpx.AsyncClient() as c:
                found = await _ask(c)
    except Exception as exc:                       # noqa: BLE001
        log.warning("could not ask about %s: %s", channel_id, type(exc).__name__)
        return ""

    _parents[channel_id] = found
    return found


async def start_thread(
    channel_id: str, message_id: str, token: str, name: str,
    client: httpx.AsyncClient | None = None,
) -> str | None:
    """
    Open a thread under a message, and say which channel it became.

    ⚠ **A thread IS a channel.** Its id is what you post to, and it is not the
    id of the message it hangs from — posting to the message id instead is a
    404 that reads like a permissions problem.

    ⚠ **Discord cannot nest threads.** This only works on a message sitting in
    a real channel; a message already inside a thread has no thread of its own,
    and there is no setting that changes it. That limit is why a submission is
    one announcement, one thread, and one message per sign inside it, rather
    than a thread per reading.

    `auto_archive_duration` is in minutes and 10080 is the week Discord allows.
    A thread that archives itself mid-conversation is not gone, but it drops
    out of the sidebar, and a practice room where last week's readings vanish
    from view is one nobody goes back to.
    """
    async def _send(c: httpx.AsyncClient) -> str | None:
        r = await c.post(
            f"{API}/channels/{channel_id}/messages/{message_id}/threads",
            json={"name": name[:100], "auto_archive_duration": 10080},
            headers={"Authorization": f"Bot {token}",
                     "User-Agent": "vcordbot/1.0"},
            timeout=10.0)
        if r.status_code in (400, 403, 404, 429):
            log.warning("could not open a thread on %s: %s",
                        message_id, r.status_code)
            return None
        r.raise_for_status()
        return str((r.json() or {}).get("id") or "") or None

    try:
        if client is not None:
            return await _send(client)
        async with httpx.AsyncClient() as c:
            return await _send(c)
    except Exception as exc:                       # noqa: BLE001
        log.warning("could not open a thread: %s", type(exc).__name__)
        return None


async def add_reaction(channel_id: str, message_id: str, token: str,
                       emoji: str,
                       client: httpx.AsyncClient | None = None) -> bool:
    """
    Put the voting reaction on, so nobody has to know which emoji counts.

    ⚠ A vote that only works if you guess the right emoji is a vote nobody
    casts. The bot reacts first and the channel taps what is already there.
    """
    import urllib.parse

    quoted = urllib.parse.quote(emoji)

    async def _send(c: httpx.AsyncClient) -> bool:
        r = await c.put(
            f"{API}/channels/{channel_id}/messages/{message_id}"
            f"/reactions/{quoted}/@me",
            headers={"Authorization": f"Bot {token}",
                     "User-Agent": "vcordbot/1.0"},
            timeout=10.0)
        return r.status_code in (200, 204)

    try:
        if client is not None:
            return await _send(client)
        async with httpx.AsyncClient() as c:
            return await _send(c)
    except Exception as exc:                       # noqa: BLE001
        log.warning("could not react: %s", type(exc).__name__)
        return False


async def post_message(channel_id: str, token: str, *, content: str = "",
                       embed: dict | None = None,
                       allowed_role: str = "",
                       client: httpx.AsyncClient | None = None) -> bool:
    """
    Send one message. True if it landed.

    **`allowed_mentions` is set explicitly and always.** Left to the default, a
    message containing @everyone in a stream title — or in a custom template
    somebody pasted — would ping the entire server. Naming exactly the one role
    that may be pinged makes that impossible rather than unlikely.
    """
    payload: dict = {
        "allowed_mentions": {"parse": [],
                             "roles": [allowed_role] if allowed_role else []},
    }
    if content:
        payload["content"] = content
    if embed:
        payload["embeds"] = [embed]

    async def _send(c: httpx.AsyncClient) -> bool:
        r = await c.post(f"{API}/channels/{channel_id}/messages",
                         json=payload,
                         headers={"Authorization": f"Bot {token}",
                                  "User-Agent": "vcordbot/1.0"},
                         timeout=10.0)
        if r.status_code == 403:
            # The commonest failure by far, and not ours: the bot was invited
            # but cannot see or speak in that channel.
            log.warning("cannot post in channel %s — missing permission", channel_id)
            return False
        if r.status_code == 404:
            log.warning("channel %s no longer exists", channel_id)
            return False
        if r.status_code == 429:
            # Rate limited. Dropping one announcement is better than queuing
            # and posting it an hour late, when the stream may have ended.
            log.warning("rate limited posting to %s", channel_id)
            return False
        r.raise_for_status()
        return True

    try:
        if client is not None:
            return await _send(client)
        async with httpx.AsyncClient() as c:
            return await _send(c)
    except Exception as exc:                        # noqa: BLE001
        log.warning("posting to %s failed: %s", channel_id, type(exc).__name__)
        return False


async def edit_original(app_id: str, interaction_token: str, embed: dict,
                        client: httpx.AsyncClient | None = None) -> bool:
    """
    Fill in an answer the bot already promised.

    Discord allows three seconds to say ANYTHING, which a gazetteer lookup
    followed by an ephemeris call is not reliably inside. The interaction is
    acknowledged immediately and this replaces that acknowledgement with the
    real answer when it arrives.

    **This needs no bot token.** The interaction token is the authority, it is
    scoped to this one interaction, and it expires in fifteen minutes — so a
    followup carries less power than anything else the bot does, not more.

    The ephemeral flag is fixed at the moment of acknowledgement and cannot be
    changed here. Whether a chart is private is therefore decided before any
    work begins, which is the right way round: it can never be leaked by a
    failure partway through.
    """
    url = f"{API}/webhooks/{app_id}/{interaction_token}/messages/@original"

    async def _edit(c: httpx.AsyncClient) -> bool:
        r = await c.patch(url, json={"embeds": [embed],
                                     "allowed_mentions": {"parse": []}},
                          headers={"User-Agent": "vcordbot/1.0"}, timeout=10.0)
        if r.status_code == 404:
            # The token expired, or the interaction was never acknowledged.
            # Nothing to retry: there is no message to edit.
            log.warning("interaction expired before the answer was ready")
            return False
        r.raise_for_status()
        return True

    try:
        if client is not None:
            return await _edit(client)
        async with httpx.AsyncClient() as c:
            return await _edit(c)
    except Exception as exc:                        # noqa: BLE001
        log.warning("could not deliver a deferred answer: %s", type(exc).__name__)
        return False
