# SPDX-License-Identifier: AGPL-3.0-only
"""
Keep credentials out of the log.

httpx logs every request at INFO, URL and all — which is genuinely useful, and
it is how several integrations in this codebase were confirmed to be working.
But a key passed as a QUERY PARAMETER ends up in that line verbatim, and the
YouTube Data API takes its key exactly that way. One `docker compose logs`
later, a working key is sitting in a terminal, a scrollback, or wherever the
host ships its logs.

Turning httpx's logging off would work and would throw away the useful half.
Redacting the parameters keeps the request visible and the secret out of it.

Applies to the message as formatted, not just to httpx, because the same shape
turns up wherever a URL is logged.
"""
from __future__ import annotations

import logging
import re

# Names that carry a credential in a query string. Matched case-insensitively,
# and only up to the next & or whitespace so the rest of the URL survives.
SECRET_PARAMS = (
    "key", "api_key", "apikey", "access_token", "token", "secret",
    "client_secret", "password", "sig", "signature", "x-amz-signature",
)

_PATTERN = re.compile(
    r"(?i)\b(" + "|".join(re.escape(p) for p in SECRET_PARAMS) + r")=([^&\s\"']+)"
)


def redact(text: str) -> str:
    return _PATTERN.sub(lambda m: f"{m.group(1)}=<redacted>", text)


class RedactSecrets(logging.Filter):
    """Rewrites the record's message rather than dropping the record."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:                          # noqa: BLE001
            return True
        cleaned = redact(message)
        if cleaned != message:
            # Replace both, or a formatter that re-applies args would put the
            # secret back.
            record.msg = cleaned
            record.args = ()
        return True


def install() -> None:
    """
    Attach to the root handlers, so anything logged anywhere is covered.

    Attached to HANDLERS rather than to a logger: a filter on a logger does not
    run for records that propagate up from its children, which is precisely how
    httpx's records reach the root.
    """
    f = RedactSecrets()
    root = logging.getLogger()
    for handler in root.handlers:
        if not any(isinstance(existing, RedactSecrets) for existing in handler.filters):
            handler.addFilter(f)
