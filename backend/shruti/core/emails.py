# SPDX-License-Identifier: AGPL-3.0-only
"""
Rendering the designer's email templates.

The HTML in `shruti/emails/` is the design bundle's, verbatim: table layout,
every critical style inlined as well as in `<style>`, no webfonts, no images,
and dark mode handled by `prefers-color-scheme` overrides. Those four
properties are the design, not an implementation detail, and a hostile client
is the assumption — images blocked, `<style>` stripped, dark mode forced.

**There is no tracking pixel and there must not be.** The copy in both
templates says so, and the site's analytics are cookieless; adding one would
contradict both. A test asserts the templates contain no `<img>` at all.

Substitution is a plain `{{slot}}` replace rather than a template engine. There
are four slots across two files; a dependency for that would be silly, and a
templating language with logic in it would invite exactly the kind of edit
these files must not receive.
"""
from __future__ import annotations

import os
from html import escape as _escape
from functools import lru_cache
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "emails"


@lru_cache(maxsize=8)
def _raw(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def site_url() -> str:
    return os.environ.get("SHRUTI_SITE_URL", "http://localhost:8200").rstrip("/")


def render(name: str, **slots: str) -> str:
    """Fill the slots. An unfilled slot is left visible rather than blanked."""
    html = _raw(name)
    for key, value in slots.items():
        html = html.replace("{{" + key + "}}", value)
    return html


def optin_confirm(token: str, imprint: dict | None = None) -> str:
    url = f"{site_url()}/newsletter/confirm?token={token}"
    return render(
        "optin-confirm.html",
        confirm_url=url,
        # Shown as text for anyone whose client will not make the button work.
        confirm_url_text=url.replace("https://", "").replace("http://", ""),
        report_url=f"{site_url()}/contact",
        site_url=site_url(),
        footer_legal=legal_footer(imprint),
    )


def _letter_html(markdown: str) -> str:
    """
    Her prose, in the designer's paragraph style.

    Deliberately not a markdown engine. An email client is hostile ground —
    half the stylesheet is stripped, so every rule that matters has to be
    inlined on the element — and a general renderer produces bare <p> and <h2>
    tags carrying none of that. Paragraphs, a blank-line break and nothing
    else is what a letter needs, and what it cannot get wrong.

    Everything is escaped. What she types is text, and a stray `<` in a letter
    about a `<span>` should read as a `<`, not vanish.
    """
    paras = [p.strip() for p in (markdown or "").replace("\r\n", "\n").split("\n\n")]
    paras = [p for p in paras if p]
    if not paras:
        return ""
    style = ("margin:0 0 14px;font:400 16px/1.7 Georgia,'Times New Roman',serif;"
             "color:#26304A")
    last = ("margin:0;font:400 16px/1.7 Georgia,'Times New Roman',serif;"
            "color:#26304A")
    out = []
    for i, para in enumerate(paras):
        text = _escape(para).replace("\n", "<br>")
        out.append(f'<p class="ink" style="{last if i == len(paras) - 1 else style}">{text}</p>')
    return "\n".join(out)


def newsletter_issue(
    *,
    subject: str,
    letter_md: str,
    issue_line: str = "",
    preheader: str = "",
    unsubscribe_url: str = "",
    preferences_url: str = "",
    browser_url: str = "",
    confirmed_on: str = "",
    reading_html: str = "",
    videos_html: str = "",
    imprint: dict | None = None,
) -> str:
    """
    One issue, for one subscriber.

    **The unsubscribe link is per-subscriber and must be real.** It used to be
    `{{site_url}}` — the designer's stand-in — which would have shipped a
    letter whose one-click unsubscribe went to the front page. That is a legal
    requirement, not a nicety, and it is the kind of thing nobody notices until
    somebody who wants out cannot get out.

    `reading_html` and `videos_html` are empty by default. The mock-up carried
    invented article titles in those places; an empty section is honest and an
    invented one is not.
    """
    return render(
        "newsletter-issue.html",
        subject=_escape(subject),
        preheader=_escape(preheader or subject),
        issue_line=_escape(issue_line),
        letter=_letter_html(letter_md),
        reading=reading_html,
        videos=videos_html,
        unsubscribe_url=_escape(unsubscribe_url, quote=True) or site_url(),
        preferences_url=_escape(preferences_url, quote=True) or site_url(),
        browser_url=_escape(browser_url, quote=True) or site_url(),
        confirmed_on=f" on {_escape(confirmed_on)}" if confirmed_on else "",
        site_url=site_url(),
        footer_legal=legal_footer(imprint),
    )


# ── billing ─────────────────────────────────────────────────────────────────
#
# These are sent whether or not someone takes the newsletter, and that is not a
# loophole: they are messages about money already paid or agreed to be paid,
# which is a contractual necessity rather than marketing. The footer of every
# one says so, because a recipient is owed the reason they are being written to.
#
# **What Stripe sends and what this sends are different things.** Stripe issues
# the receipt and the invoice PDF, with the tax breakdown, and doing that here
# would be a worse copy. What Stripe does not reliably send is the confirmation
# that a recurring contract now exists, the reminder before the next charge,
# and the confirmation that a cancellation was received — and under EU consumer
# law the first of those is owed on a durable medium. So this covers the gap.




def _fact_rows(rows: list[tuple[str, str]]) -> str:
    """The small grey block of particulars. Empty rows are dropped, so a fact
    that is not known simply does not appear rather than printing a blank."""
    if not rows:
        return ""
    cells = "".join(
        f'<tr><td style="padding:3px 0"><span class="faint" style="font:600 11px Helvetica,Arial,sans-serif;'
        f'letter-spacing:1.5px;text-transform:uppercase;color:#6E7890">{_escape(label)}</span></td>'
        f'<td align="right" style="padding:3px 0"><span class="ink" style="font:500 14px '
        f"'JetBrains Mono',Consolas,monospace;color:#26304A\">{_escape(value)}</span></td></tr>"
        for label, value in rows
        if value
    )
    return (
        '<tr><td class="pad" style="padding:0 32px 24px">'
        '<table role="presentation" width="100%" class="inset" style="background:#ECE7EB;border-radius:8px">'
        f'<tr><td style="padding:16px 18px"><table role="presentation" width="100%">{cells}</table>'
        "</td></tr></table></td></tr>"
    )


def _button(url: str, label: str) -> str:
    if not url:
        return ""
    return (
        '<tr><td class="pad" style="padding:0 32px 22px">'
        '<table role="presentation" class="btn" style="background:#33639C;border:1px solid #33639C;border-radius:4px"><tr>'
        '<td align="center" style="padding:13px 26px">'
        f'<a href="{_escape(url, quote=True)}" style="font:600 15px Helvetica,Arial,sans-serif;'
        f'color:#FFFFFF;text-decoration:none;display:inline-block">{_escape(label)}</a>'
        "</td></tr></table></td></tr>"
    )


def legal_footer(imprint: dict | None) -> str:
    """
    The registered-details block, or the contact address alone.

    **Never the designer's bracketed placeholders.** `GEMI [000000000000]` is
    the right convention for a mock-up and the wrong thing to put in a sent
    email: a registry number that looks like one and is not is worse than none.
    This follows exactly the rule the site footer follows — nothing until it is
    filled in and switched on.
    """
    if not (imprint and imprint.get("visible")):
        return (
            '<p class="faint" style="margin:0 0 10px;font:400 11px/1.8 '
            "'JetBrains Mono',Consolas,monospace;color:#6E7890\">"
            "business@shrutivtuber.com</p>"
        )

    where = " · ".join(
        p for p in (
            imprint.get("street", ""),
            " ".join(p for p in (imprint.get("postcode", ""), imprint.get("city", "")) if p),
            imprint.get("country", ""),
        ) if p
    )
    ids = " · ".join(
        p for p in (imprint.get("registry", ""), imprint.get("vat", "")) if p
    )
    lines = [_escape(imprint["entity"])]
    if where:
        lines.append(_escape(where))
    lines.append(_escape(imprint["email"]))
    if ids:
        lines.append(_escape(ids))
    return (
        '<p class="faint" style="margin:0 0 10px;font:400 11px/1.8 '
        "'JetBrains Mono',Consolas,monospace;color:#6E7890\">"
        + "<br>".join(lines)
        + "</p>"
    )


def billing(
    *, glyph: str, heading: str, lede: str, note: str,
    facts: list[tuple[str, str]] | None = None,
    cta_url: str = "", cta_label: str = "",
    preheader: str = "", imprint: dict | None = None,
) -> str:
    return render(
        "billing.html",
        glyph=glyph,
        heading=_escape(heading),
        # The lede carries deliberate markup — a bolded amount, a link to the
        # account page — so it is passed through. Every value that comes from
        # outside this module is escaped by the caller or by _fact_rows.
        lede=lede,
        note=note,
        facts=_fact_rows(facts or []),
        cta=_button(cta_url, cta_label),
        preheader=_escape(preheader or heading),
        footer_legal=legal_footer(imprint),
        contact_url=f"{site_url()}/contact",
        site_url=site_url(),
    )


TIER_NAMES = {"lamplighter": "Lamplighter", "almanac": "Almanac"}


def money(cents: int | None, currency: str = "EUR") -> str:
    if cents is None:
        return ""
    symbol = {"EUR": "€", "GBP": "£", "USD": "$"}.get(currency.upper(), currency.upper() + " ")
    whole, part = divmod(int(cents), 100)
    return f"{symbol}{whole}" if part == 0 else f"{symbol}{whole}.{part:02d}"


def _day(moment) -> str:
    """`14 September 2026`. Long form on purpose: an email read on a phone in
    another timezone should not have to work out what 09/14 means."""
    return moment.strftime("%-d %B %Y") if moment else ""


def subscription_started(
    *, tier: str, amount: int | None, currency: str, renews_on, imprint: dict | None = None
) -> tuple[str, str]:
    """
    The contract confirmation.

    **This one is owed, not optional.** EU consumer law wants confirmation of a
    distance contract on a durable medium, and an email is that. So it states
    the recurring nature, the amount, the date of the next charge and how to
    stop — the four things somebody needs to not feel trapped by a thing they
    just signed up to.
    """
    name = TIER_NAMES.get(tier, "Monthly support")
    subject = f"Your {name} support has started"
    html = billing(
        glyph="&#9789;",
        heading="Thank you — it has started",
        lede=(
            f"You are now a <b style=\"font-weight:600\">{_escape(name)}</b>. That goes to the "
            "ephemeris server, art commissions, and the hours the software takes. "
            "<b style=\"font-weight:600\">This renews every month until you stop it.</b>"
        ),
        facts=[
            ("Tier", name),
            ("Amount", f"{money(amount, currency)} / month"),
            ("Next charge", _day(renews_on)),
        ],
        cta_url=f"{site_url()}/account",
        cta_label="Manage or cancel",
        note=(
            "Cancelling is one button on your account page. It takes effect at the end of the "
            "month you have already paid for rather than the moment you press it, and no message "
            "to me is needed or wanted. Your right to withdraw and the refund terms are on the "
            f'<a href="{site_url()}/terms" style="color:#33639C" class="acc">terms page</a>.'
        ),
        preheader=f"{name} · {money(amount, currency)} a month · cancel any time in one click",
        imprint=imprint,
    )
    return subject, html


def renewal_reminder(
    *, tier: str, amount: int | None, currency: str, charge_on, imprint: dict | None = None
) -> tuple[str, str]:
    """
    Before the money moves, not after.

    A charge nobody remembered agreeing to is the most common reason a
    subscription becomes a chargeback, and several jurisdictions now require
    the reminder outright. Sent whether or not it is required, because being
    surprised by a charge is a bad thing to do to somebody either way.
    """
    name = TIER_NAMES.get(tier, "Monthly support")
    subject = f"Your support renews on {_day(charge_on)}"
    html = billing(
        glyph="&#9682;",
        heading="A heads-up before the next charge",
        lede=(
            f"Your <b style=\"font-weight:600\">{_escape(name)}</b> support renews shortly. "
            "Nothing is needed from you — this is so the charge is not a surprise."
        ),
        facts=[
            ("Tier", name),
            ("Amount", money(amount, currency)),
            ("Charges on", _day(charge_on)),
        ],
        cta_url=f"{site_url()}/account",
        cta_label="Manage or cancel",
        note=(
            "If you would rather stop, cancelling before that date means you are not charged "
            "again and you keep what you have already paid for until it runs out."
        ),
        preheader=f"{money(amount, currency)} on {_day(charge_on)} — nothing needed from you",
        imprint=imprint,
    )
    return subject, html


def subscription_cancelled(
    *, tier: str, ends_on, imprint: dict | None = None
) -> tuple[str, str]:
    """Confirming it was received, and — the part people actually want — the
    date it stops, so nobody spends a month wondering whether it took."""
    name = TIER_NAMES.get(tier, "Monthly support")
    subject = "Your support is cancelled"
    ends = _day(ends_on)
    html = billing(
        glyph="&#9711;",
        heading="Cancelled — and thank you, genuinely",
        lede=(
            "That is done. You will not be charged again."
            + (
                f" Your <b style=\"font-weight:600\">{_escape(name)}</b> access stays until "
                f"<b style=\"font-weight:600\">{_escape(ends)}</b>, because you have already paid "
                "for that month."
                if ends else ""
            )
        ),
        facts=[("Tier", name), ("Access until", ends)],
        cta_url=f"{site_url()}/support",
        cta_label="The work is still free",
        note=(
            "The streams, the tools and the horoscopes do not change — none of it was ever behind "
            "the payment. Coming back later is a button, not a negotiation."
        ),
        preheader="Confirmed. You will not be charged again." + (f" Access until {ends}." if ends else ""),
        imprint=imprint,
    )
    return subject, html


def payment_failed(*, tier: str, imprint: dict | None = None) -> tuple[str, str]:
    """A card expired, almost always. Said without alarm and without shame."""
    name = TIER_NAMES.get(tier, "Monthly support")
    subject = "That payment did not go through"
    html = billing(
        glyph="&#9680;",
        heading="The card was declined",
        lede=(
            "Usually this is an expired card and nothing more. Your "
            f"<b style=\"font-weight:600\">{_escape(name)}</b> support is still on for now — "
            "Stripe will try again, and updating the card fixes it."
        ),
        cta_url=f"{site_url()}/account",
        cta_label="Update the card",
        note=(
            "If you would rather it lapsed, doing nothing is enough. Nothing is sent again after "
            "Stripe stops retrying."
        ),
        preheader="Usually an expired card. Updating it fixes it.",
        imprint=imprint,
    )
    return subject, html


def gift_received(
    *, amount: int | None, currency: str, imprint: dict | None = None
) -> tuple[str, str]:
    """A one-off. Stripe sends the formal receipt; this says thank you and
    records the amount, so there is a record even if Stripe's receipt is
    filtered."""
    subject = "Thank you"
    html = billing(
        glyph="&#9827;",
        heading="Thank you",
        lede=(
            f"<b style=\"font-weight:600\">{_escape(money(amount, currency))}</b>, once. "
            "That goes to the ephemeris server, art commissions, and the hours the software "
            "takes. There is nothing recurring here — this does not repeat."
        ),
        facts=[("Amount", money(amount, currency)), ("Recurring", "No")],
        note=(
            "Stripe sends the formal receipt separately, with the tax breakdown. This is just "
            "the thank you."
        ),
        preheader=f"{money(amount, currency)}, once. Nothing recurring.",
        imprint=imprint,
    )
    return subject, html
