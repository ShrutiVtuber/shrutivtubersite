# SPDX-License-Identifier: AGPL-3.0-only
"""
Writing a letter and sending it.

All of this was missing, and nothing said so. The subscribe form, the double
opt-in, the one-click unsubscribe, the preference centre and the public archive
were all built and all worked. Nothing could write an issue or send one — no
code anywhere wrote a row to the `issue` table — so the site was collecting
confirmed addresses against a promise of one letter a month that it had no way
to keep. A half-built feature made of working halves is the hardest kind to
notice.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

from shruti.api.routes import newsletter
from shruti.core import emails


def _routes() -> list[tuple[str, str]]:
    out = []
    for route in newsletter.router.routes:
        for method in sorted(getattr(route, "methods", []) or []):
            if method not in {"HEAD", "OPTIONS"}:
                out.append((method, route.path))
    return out


# ── the gap itself ──────────────────────────────────────────────────────────

def test_an_issue_can_be_written_and_sent():
    """The four verbs that were missing entirely."""
    paths = _routes()
    assert ("POST", "/api/newsletter/admin/issues") in paths, "nothing can create an issue"
    assert ("PUT", "/api/newsletter/admin/issues/{issue_id}") in paths
    assert ("POST", "/api/newsletter/admin/issues/{issue_id}/send") in paths, "nothing can send"
    assert ("POST", "/api/newsletter/admin/issues/{issue_id}/test") in paths, (
        "no way to read it before five hundred people do"
    )


def test_the_admin_routes_come_before_the_archive_catch_all():
    """
    `/archive/{slug}` would swallow nothing here, but `/admin/issues/{id}` and
    the literals around it are exactly the shape that has bitten this codebase
    four times, always as silence.
    """
    paths = [p for _, p in _routes()]
    assert paths.index("/api/newsletter/admin/issues") < paths.index("/api/newsletter/archive/{slug}")
    assert paths.index("/api/newsletter/admin/audience") < paths.index(
        "/api/newsletter/admin/issues/{issue_id}"
    ), "a literal after a catch-all is unreachable"


# ── sending once, and only to people who agreed ─────────────────────────────

def test_sending_twice_is_refused():
    """The mistake that costs a subscriber list."""
    source = inspect.getsource(newsletter.send_issue)
    assert "already been sent" in source
    assert "409" in source


def test_only_confirmed_unpaused_subscribers_are_written_to():
    """
    Four conditions, each of which can lose an address for a reason that is
    the subscriber's rather than ours.
    """
    source = inspect.getsource(newsletter._recipients)
    assert "confirmed_at.is_not(None)" in source, "an unconfirmed address is not consent"
    assert "unsubscribed_at.is_(None)" in source
    assert "paused" in source
    assert "paused_until" in source


def test_a_sent_issue_cannot_be_edited_or_deleted():
    """The archive has to be the letter people actually read."""
    assert "409" in inspect.getsource(newsletter.update_issue)
    assert "409" in inspect.getsource(newsletter.delete_issue)


def test_sending_is_batched_with_a_pause():
    """A provider that decides this looks like a blast starts dropping mail."""
    assert newsletter.BATCH <= 50
    assert newsletter.BREATH_SECONDS > 0
    assert "asyncio.sleep" in inspect.getsource(newsletter.send_issue)


# ── the template, which was a mock-up ───────────────────────────────────────

def _template() -> str:
    here = Path(emails.__file__).resolve().parent.parent
    return (here / "emails" / "newsletter-issue.html").read_text()


def test_the_template_carries_no_invented_content():
    """
    It shipped as the designer's mock-up: a September 2026 issue with three
    fabricated article titles and two paragraphs of prose she never wrote.
    Sending it would have put invented work under her name.
    """
    text = _template()
    for invented in ("sigil compiler", "ayan", "Six divination systems",
                     "September 2026", "Saturn stations on the 9th"):
        assert invented not in text, f"the mock-up's {invented!r} is still in the template"


def test_the_unsubscribe_link_is_per_subscriber():
    """
    Every footer link used to be `{{site_url}}`, the designer's stand-in. A
    one-click unsubscribe that lands on the front page is a legal failure and
    the kind nobody notices until somebody who wants out cannot get out.
    """
    text = _template()
    assert "{{unsubscribe_url}}" in text
    assert "{{preferences_url}}" in text
    body = text.split("Unsubscribe in one click")[0][-400:]
    assert "{{site_url}}" not in body, "the unsubscribe link still points at the front page"


def test_every_slot_is_filled_when_an_issue_is_rendered():
    html = emails.newsletter_issue(
        subject="A letter",
        letter_md="One.\n\nTwo.",
        issue_line="August 2026",
        unsubscribe_url="https://example.test/u?token=t",
        preferences_url="https://example.test/p?token=t",
        browser_url="https://example.test/a/x",
        confirmed_on="1 August 2026",
    )
    assert not re.findall(r"\{\{[a-z_]+\}\}", html), "a slot was left unfilled"
    assert "token=t" in html
    assert "<p" in html


def test_what_she_types_is_escaped_not_interpreted():
    """A letter about a `<span>` should say `<span>`, not lose it."""
    html = emails.newsletter_issue(subject="x", letter_md="About <span> tags & things.")
    assert "&lt;span&gt;" in html
    assert "&amp; things" in html


def test_there_is_no_tracking_pixel():
    """The template says so in its own footer; this is that promise, checked."""
    html = emails.newsletter_issue(subject="x", letter_md="y")
    assert "<img" not in html.lower()
    assert "no tracking pixel" in html.lower()
