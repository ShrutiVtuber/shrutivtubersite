# SPDX-License-Identifier: AGPL-3.0-only
"""
Why a send failed has to reach the log, and a subscriber's address must not.

Those pull against each other, which is why this file exists. The provider's
own error text is the only thing that says WHY — and it quotes the input back,
so it is also the one place a recipient's address can leak into a log by
accident.

The cost of the first half is not theoretical. A signup during a live campaign
logged `resend rejected the message: HTTP 422` and nothing else, and finding
out that the provider had simply refused the recipient's domain meant
reproducing the call by hand against the production key.
"""
from __future__ import annotations

import httpx

from shruti.core.mail import _reason


def response(payload=None, text="", status=422) -> httpx.Response:
    if payload is not None:
        return httpx.Response(status, json=payload)
    return httpx.Response(status, text=text)


def test_the_providers_reason_reaches_the_log() -> None:
    """The actual 422 that cost an afternoon."""
    said = _reason(response({
        "statusCode": 422, "name": "validation_error",
        "message": "Invalid `to` field. Please use our testing email address "
                   "instead of domains like `example.com`.",
    }))
    assert "validation_error" in said
    assert "example.com" in said


def test_an_address_in_the_reason_is_struck_out() -> None:
    """
    The rule this file guards. A provider that says "sophia@example.org is
    suppressed" is telling us something useful about an address we must not
    write down.
    """
    said = _reason(response({"name": "x", "message": "sophia@example.org is suppressed"}))
    assert "sophia@example.org" not in said
    assert "[address]" in said
    assert "is suppressed" in said


def test_a_page_instead_of_json_is_still_reported() -> None:
    """
    A gateway in front of the provider answers with HTML, not JSON — a real
    403 from Cloudflare came back as `error code: 1010`, which is worth seeing
    precisely because it is not the provider talking.
    """
    assert "1010" in _reason(response(text="<html>error code: 1010</html>", status=403))


def test_an_empty_body_says_so_rather_than_nothing() -> None:
    """An empty log line reads as a bug in the logging, not in the send."""
    assert _reason(response(text="")) == "no reason given"


def test_a_long_body_cannot_become_the_log() -> None:
    from shruti.core.mail import _REASON_MAX
    assert len(_reason(response(text="x" * 5000))) <= _REASON_MAX
