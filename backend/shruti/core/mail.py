# SPDX-License-Identifier: AGPL-3.0-only
"""
Transactional email, via Resend.

Two rules, both learned from forms that silently ate their submissions:

  - **The database write is the source of truth, not the send.** A contact
    message is stored first and mailed second. If Resend is down, misconfigured
    or rate-limited, the message is still on disk and can be re-sent — a form
    that loses what someone typed because a third party had an outage is worse
    than a form with no email at all.
  - **Never put the sender's address in `From`.** It fails SPF and DKIM for
    their domain and gets the mail filed as spam or rejected outright. Send from
    the verified domain and put their address in `Reply-To`, which is what that
    header exists for.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import httpx

from shruti.core.config import get_settings

log = logging.getLogger(__name__)

RESEND_ENDPOINT = "https://api.resend.com/emails"


@dataclass
class SendResult:
    sent: bool
    provider_id: str = ""
    error: str = ""


# An address, for striking out of anything about to be logged.
_ADDRESS = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")

# Long enough to carry a provider's explanation, short enough that a stray HTML
# error page does not become the log.
_REASON_MAX = 300


def _reason(response: httpx.Response) -> str:
    """
    Why the provider refused, with any address struck out.

    Resend answers `{"name": ..., "message": ...}`; anything else that comes
    back is truncated text, because a gateway in front of it may answer with a
    page rather than JSON and that is itself worth seeing.
    """
    try:
        body = response.json()
    except ValueError:
        body = None
    if isinstance(body, dict):
        said = " ".join(str(body.get(k, "")) for k in ("name", "message")).strip()
    else:
        said = response.text.strip()
    return _ADDRESS.sub("[address]", said)[:_REASON_MAX] or "no reason given"


async def send(
    subject: str,
    body: str,
    reply_to: str | None = None,
    to: str | None = None,
    html: str | None = None,
) -> SendResult:
    """
    Send one message. Never raises — a failed send must not fail the request
    that triggered it, because the message is already stored.
    """
    s = get_settings()
    api_key = s.resend_api_key
    sender = s.resend_from
    recipient = to or s.contact_to

    if not (api_key and sender and recipient):
        missing = [n for n, v in (("SHRUTI_RESEND_API_KEY", api_key),
                                  ("SHRUTI_RESEND_FROM", sender),
                                  ("SHRUTI_CONTACT_TO", recipient)) if not v]
        log.info("mail not configured (%s); message stored only", ", ".join(missing))
        return SendResult(sent=False, error=f"not configured: {', '.join(missing)}")

    payload: dict = {
        "from": sender,
        "to": [recipient],
        "subject": subject,
        # Both parts, always, when there is an HTML one. A client that will not
        # render the HTML gets a real message rather than an empty frame, and
        # the plain part is what a screen reader and a text client see first.
        "text": body,
    }
    if html:
        payload["html"] = html
    if reply_to:
        payload["reply_to"] = [reply_to]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                RESEND_ENDPOINT,
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
        if r.status_code >= 400:
            # A bare status is not diagnosable. "HTTP 422" sent somebody
            # reproducing the call by hand to discover the provider had simply
            # refused the recipient's domain — during a live signup campaign,
            # where a silent rejection is the expensive kind.
            #
            # So the provider's OWN reason is logged, and only that: its error
            # name and message, never the key and never the message body. The
            # reason can quote the input back ("domains like `example.com`"),
            # which is why any address in it is redacted first — the original
            # rule was never to put a subscriber's address in a log, and that
            # still holds.
            log.warning("resend rejected the message: HTTP %s — %s",
                        r.status_code, _reason(r))
            return SendResult(sent=False, error=f"provider returned {r.status_code}")
        return SendResult(sent=True, provider_id=r.json().get("id", ""))
    except Exception as exc:                       # noqa: BLE001 — never propagate
        log.warning("resend send failed: %s", type(exc).__name__)
        return SendResult(sent=False, error=type(exc).__name__)
