# SPDX-License-Identifier: AGPL-3.0-only
"""
The sky attached to a journal entry.

Two moments are kept per entry and they are captured very differently. When it
was published is read out of the page BeeRanked syncs; when it was begun is
told to us and cannot be discovered. What the tests here defend is mostly the
first of those, because it is the one that runs unattended.
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from shruti.api.routes import journal


# --- reading the publication time out of a synced page ---------------------

def _page(ld: object) -> str:
    """A page shaped like the agent's output: the block among other scripts."""
    return (
        "<html><head>"
        '<script>window.x=1</script>'
        f'<script type="application/ld+json">{json.dumps(ld)}</script>'
        '<script>window.y=2</script>'
        "</head><body><main>text</main></body></html>"
    )


def test_publication_time_is_found_inside_an_at_graph() -> None:
    """
    The real shape, and the one that broke.

    BeeRanked emits an `@graph` — the entry sits in it beside the site and the
    breadcrumb list — so a search that only looks at the top level of the block
    finds nothing and every entry is silently skipped as untimestamped.
    """
    html = _page({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "name": "Shruti"},
            {"@type": "BlogPosting", "datePublished": "2026-08-25T02:30:47.418Z"},
        ],
    })
    assert journal._published_at(html) == "2026-08-25T02:30:47.418Z"


def test_publication_time_is_found_at_the_top_level_too() -> None:
    html = _page({"@type": "BlogPosting", "datePublished": "2026-08-25T02:30:47Z"})
    assert journal._published_at(html) == "2026-08-25T02:30:47Z"


def test_a_page_without_a_timestamp_yields_nothing() -> None:
    """
    Not an exception and not a guess.

    A missing timestamp has to stay missing: the reconciler treats "" as "no
    honest moment to record" and skips the entry, which is the whole reason it
    is allowed to run unattended.
    """
    assert journal._published_at(_page({"@type": "WebSite"})) == ""
    assert journal._published_at("<html><body>nothing here</body></html>") == ""


def test_unparseable_json_is_skipped_rather_than_raising() -> None:
    """A block that is not JSON is not a timestamp; it is also not a crash."""
    html = (
        '<script type="application/ld+json">{not json at all</script>'
        '<script type="application/ld+json">'
        '{"datePublished":"2026-08-25T02:30:47Z"}</script>'
    )
    assert journal._published_at(html) == "2026-08-25T02:30:47Z"


# --- which paths count as entries ------------------------------------------

def test_only_entries_are_offered_for_capture(monkeypatch) -> None:
    """
    An index is not a thing that was written at a moment.

    The hub, the section listings and the sitemap all have an index.html; none
    of them has a publication instant worth recording, and capturing one would
    put a sky on a page that is regenerated whenever anything changes.
    """
    with tempfile.TemporaryDirectory() as root:
        for path in (
            "index.html",                                  # the hub
            "blog/index.html",                             # a section index
            "sitemap/index.html",
            "blog/nothing-was-ever-retrograde/index.html",  # an entry
            "docs/casting-a-chart/index.html",              # an entry
        ):
            full = os.path.join(root, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf8") as fh:
                fh.write("<html></html>")

        monkeypatch.setattr(journal, "JOURNAL_DIR", root)
        slugs = sorted(slug for slug, _path in journal._entry_slugs())

    assert slugs == ["casting-a-chart", "nothing-was-ever-retrograde"]


# --- the two moments are separate records ----------------------------------

def test_the_two_kinds_are_the_only_two() -> None:
    assert journal.KINDS == ("published", "written")


def test_capture_rejects_a_kind_that_is_not_one_of_them() -> None:
    """
    Guarded at the edge, because a typo would otherwise create a third kind
    silently and it would never be read by anything.
    """
    journal.CaptureIn(slug="x", kind="written")
    journal.CaptureIn(slug="x", kind="published")
    with pytest.raises(ValueError):
        journal.CaptureIn(slug="x", kind="drafted")


def test_a_reading_that_failed_still_says_why() -> None:
    """
    The rule the module is built on: absence states its reason.

    A row with no reading is not a blank in the design — it prints why it is
    blank — so the failure text has to survive into the payload.
    """
    from shruti.models.accounts import JournalSky

    row = JournalSky(
        slug="x", kind="published",
        at=journal.datetime(2026, 8, 25, tzinfo=journal.timezone.utc),
        failure_reason="the ephemeris could not be reached (ConnectError)",
    )
    payload = journal._payload(row)
    assert payload["reading"] is None
    assert payload["failureReason"].startswith("the ephemeris could not be reached")
    assert payload["kind"] == "published"
