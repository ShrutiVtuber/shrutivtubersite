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


# ── the registered-details block ────────────────────────────────────────────

def test_no_template_ships_a_bracketed_placeholder() -> None:
    """
    The design bundle's footer carries a bracketed registry number and a
    bracketed street. That is the right convention for a mock-up and the wrong
    thing to send: a registry number that looks like one and is not is worse
    than no imprint at all, and unlike the site footer nobody can take an email
    back down once it is in somebody's inbox.
    """
    from pathlib import Path

    import shruti

    for template in (Path(shruti.__file__).parent / "emails").glob("*.html"):
        body = template.read_text(encoding="utf-8")
        assert "GEMI [" not in body, template.name
        assert "[street" not in body, template.name
        assert "VAT EL[" not in body, template.name


def test_an_unset_imprint_gives_the_contact_address_and_nothing_else() -> None:
    from shruti.core.emails import legal_footer

    footer = legal_footer(None)
    assert "business@shrutivtuber.com" in footer
    assert "GEMI" not in footer
    assert "[" not in footer


def test_a_half_filled_imprint_is_still_nothing() -> None:
    """`imprint()` already refuses to mark a half-filled record visible; this
    asserts the email side trusts that flag rather than second-guessing it."""
    from shruti.core.emails import legal_footer

    assert "Some Entity" not in legal_footer({"visible": False, "entity": "Some Entity"})


def test_a_real_imprint_is_rendered_in_full() -> None:
    from shruti.core.emails import legal_footer

    footer = legal_footer({
        "visible": True, "entity": "ShrutiVTuber P.C.", "street": "Odos 1",
        "postcode": "10001", "city": "Athens", "country": "GR",
        "email": "business@shrutivtuber.com", "registry": "GEMI 123456789",
        "vat": "EL999999999",
    })
    for fragment in ("ShrutiVTuber P.C.", "Odos 1", "10001 Athens", "GEMI 123456789"):
        assert fragment in footer


# ── billing mail ────────────────────────────────────────────────────────────

def _built():
    from datetime import datetime, timezone

    from shruti.core import emails

    when = datetime(2026, 9, 24, tzinfo=timezone.utc)
    return [
        emails.subscription_started(tier="lamplighter", amount=400, currency="EUR", renews_on=when),
        emails.renewal_reminder(tier="almanac", amount=900, currency="EUR", charge_on=when),
        emails.subscription_cancelled(tier="lamplighter", ends_on=when),
        emails.payment_failed(tier="almanac"),
        emails.gift_received(amount=1500, currency="EUR"),
    ]


def test_every_billing_mail_fills_every_slot() -> None:
    """An unfilled slot reaches somebody as literal braces, and these are the
    emails where looking broken costs the most."""
    for _subject, html in _built():
        assert "{{" not in html


def test_no_billing_mail_carries_an_image() -> None:
    """Same rule as the designer's templates, and for the same reason: there is
    no tracking pixel and there must not be."""
    for _subject, html in _built():
        assert "<img" not in html.lower()


def test_every_billing_mail_says_why_it_was_sent() -> None:
    """These go to people who never took the newsletter. Saying that they are
    about money already paid or agreed is what makes that legitimate rather
    than a loophole — and it is what stops a recipient reading it as spam."""
    for _subject, html in _built():
        assert "money you have paid or agreed to pay" in html


def test_the_start_mail_states_the_recurring_nature_and_the_way_out() -> None:
    """The confirmation of a distance contract has a job: say it repeats, say
    what it costs, say when it next charges, and say how to stop."""
    from datetime import datetime, timezone

    from shruti.core import emails

    _subject, html = emails.subscription_started(
        tier="lamplighter", amount=400, currency="EUR",
        renews_on=datetime(2026, 9, 24, tzinfo=timezone.utc),
    )
    assert "renews every month until you stop it" in html
    assert "€4" in html
    assert "24 September 2026" in html
    assert "/terms" in html


def test_money_renders_whole_amounts_without_dead_decimals() -> None:
    from shruti.core.emails import money

    assert money(400, "EUR") == "€4"
    assert money(450, "EUR") == "€4.50"
    assert money(None) == ""


def test_the_text_part_is_readable_and_keeps_its_links() -> None:
    """A link with no destination is useless in text, an undecoded entity
    reaches somebody as six literal characters, and a bolded amount that
    becomes `€15 , once` reads as a typo."""
    from shruti.api.routes.billing import _plain
    from shruti.core.emails import gift_received

    _subject, html = gift_received(amount=1500, currency="EUR")
    text = _plain(html)
    assert "&#" not in text
    assert "<" not in text
    assert "€15 ," not in text
    assert "€15, once" in text
    assert "http" in text          # the contact link kept its destination
