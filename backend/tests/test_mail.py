# SPDX-License-Identifier: AGPL-3.0-only
"""
Mail behaviour. These are about failure modes, because the success path is one
HTTP call and the failure paths are where forms quietly eat submissions.
"""

import pytest

from shruti.core import mail


@pytest.mark.asyncio
async def test_unconfigured_mail_reports_rather_than_raises(monkeypatch):
    """
    A missing key must not raise. The message is already stored by the time
    send() is called, and a failed send must not fail the visitor's request.
    """
    from shruti.core.config import Settings, get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SHRUTI_RESEND_API_KEY", "")
    monkeypatch.setenv("SHRUTI_RESEND_FROM", "")
    result = await mail.send("subject", "body")
    assert result.sent is False
    assert "not configured" in result.error
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_a_provider_outage_is_swallowed(monkeypatch):
    """Resend being down must never propagate to the caller."""
    from shruti.core.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SHRUTI_RESEND_API_KEY", "re_test")
    monkeypatch.setenv("SHRUTI_RESEND_FROM", "a@b.com")
    monkeypatch.setenv("SHRUTI_CONTACT_TO", "c@d.com")

    class Boom:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def post(self, *a, **kw): raise RuntimeError("network down")

    monkeypatch.setattr(mail.httpx, "AsyncClient", lambda **kw: Boom())
    result = await mail.send("s", "b")
    assert result.sent is False and result.error == "RuntimeError"
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_the_senders_address_goes_in_reply_to_never_from(monkeypatch):
    """
    Putting a visitor's address in From fails SPF and DKIM for their domain and
    gets the mail filed as spam or rejected. Reply-To is what the header is for.
    """
    from shruti.core.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SHRUTI_RESEND_API_KEY", "re_test")
    monkeypatch.setenv("SHRUTI_RESEND_FROM", "Shruti <hello@shrutivtuber.com>")
    monkeypatch.setenv("SHRUTI_CONTACT_TO", "contact@shrutivtuber.com")

    captured = {}

    class Fake:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def post(self, url, headers=None, json=None):
            captured.update(json)
            class R:
                status_code = 200
                def json(self): return {"id": "abc"}
            return R()

    monkeypatch.setattr(mail.httpx, "AsyncClient", lambda **kw: Fake())
    await mail.send("s", "b", reply_to="visitor@elsewhere.org")

    assert captured["from"] == "Shruti <hello@shrutivtuber.com>"
    assert captured["reply_to"] == ["visitor@elsewhere.org"]
    assert "visitor@elsewhere.org" not in captured["from"]
    get_settings.cache_clear()
