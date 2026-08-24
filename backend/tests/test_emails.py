"""The two email templates, and the properties the design says they must keep."""
from __future__ import annotations

import re

import pytest

from shruti.core.emails import newsletter_issue, optin_confirm

TEMPLATES = (optin_confirm("test-token-123"), newsletter_issue())


@pytest.mark.parametrize("html", TEMPLATES)
def test_no_images_at_all(html):
    """
    No image means no tracking pixel, and the copy in both templates says so.
    It also means the mail reads correctly in a client that blocks images,
    which is the assumption the design is built on.
    """
    assert re.search(r"<img\b", html, re.I) is None


@pytest.mark.parametrize("html", TEMPLATES)
def test_no_webfonts(html):
    assert "fonts.googleapis" not in html
    assert "@font-face" not in html


@pytest.mark.parametrize("html", TEMPLATES)
def test_dark_mode_is_handled(html):
    """A dark-mode client that ignores half the CSS must still be readable."""
    assert "prefers-color-scheme:dark" in html.replace(" ", "")
    assert "color-scheme" in html


@pytest.mark.parametrize("html", TEMPLATES)
def test_layout_is_tables_with_inline_styles(html):
    """Inlined as well as in <style>, because <style> gets stripped."""
    assert "<table" in html
    assert html.count('style="') > 20


def test_the_confirm_link_is_filled_in():
    html = optin_confirm("abc123")
    assert "abc123" in html
    # Nothing left unfilled, and no dead demo link.
    assert "{{" not in html
    assert 'href="#"' not in html


def test_the_commercial_intent_is_stated_in_the_optin():
    """
    Not softened, not moved to a tooltip, not deferred to the privacy policy.
    """
    html = optin_confirm("t").lower()
    assert "course" in html or "offer" in html
