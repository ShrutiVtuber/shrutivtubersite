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


def optin_confirm(token: str) -> str:
    url = f"{site_url()}/newsletter/confirm?token={token}"
    return render(
        "optin-confirm.html",
        confirm_url=url,
        # Shown as text for anyone whose client will not make the button work.
        confirm_url_text=url.replace("https://", "").replace("http://", ""),
        report_url=f"{site_url()}/contact",
        site_url=site_url(),
    )


def newsletter_issue() -> str:
    return render("newsletter-issue.html", site_url=site_url())
