# SPDX-License-Identifier: AGPL-3.0-only
"""
What the page editor is allowed to change.

`/api/admin/editables` exists so she can edit every word on the site from the
page editor rather than from a database client — tool descriptions and their
FAQs were words on the site that no screen could reach. It is reachable from a
page listing every content row there is, so the field whitelist is the thing
standing between "change this sentence" and "change this price".

These are all pure checks on the map. No fixtures, no database: a typo in a
field name would otherwise show up as a 422 the first time she typed in that
box, which is exactly the kind of thing that goes unnoticed until she finds it.
"""
from __future__ import annotations

import pytest

from shruti.api.routes.admin import PROSE, WITH_PICTURES


# Words that mark a column as NOT prose. A slug is an address and changing one
# breaks every link to it; the rest take money or decide layout.
FORBIDDEN = ("slug", "price", "stripe", "currency", "tax", "token", "secret",
             "email", "hash", "url", "position", "visible", "locale")


def test_every_field_exists_on_its_model() -> None:
    """A typo here is a 422 in her hands, not an error anyone would see first."""
    for source, (model, names, fields) in PROSE.items():
        assert hasattr(model, names), f"{source}: no field {names!r} to name a row by"
        for field, label, _long in fields:
            assert hasattr(model, field), f"{source}: {model.__name__} has no {field!r}"
            assert label.strip(), f"{source}.{field} has no label"


def test_nothing_but_prose_is_offered() -> None:
    """The rule the endpoint exists under, enforced rather than remembered."""
    for source, (_model, _names, fields) in PROSE.items():
        for field, _label, _long in fields:
            for bad in FORBIDDEN:
                assert bad not in field, (
                    f"{source}.{field} is not prose — it looks like a {bad}. "
                    "The page editor may only change words a reader reads."
                )


def test_pictures_are_only_offered_where_there_is_one() -> None:
    for source in WITH_PICTURES:
        assert source in PROSE, f"{source} takes pictures but has no prose entry"
        model = PROSE[source][0]
        assert hasattr(model, "media_id"), (
            f"{source} is offered a picture control but {model.__name__} "
            "has nowhere to keep one"
        )


def test_every_source_offers_something() -> None:
    for source, (_model, _names, fields) in PROSE.items():
        assert fields, f"{source} is listed but offers no fields"


@pytest.mark.parametrize("source", ["tools", "tiers", "questions", "sponsors"])
def test_the_ones_she_named_are_there(source: str) -> None:
    """
    Named explicitly, because these are the gaps she hit while writing the final
    copy: "there is a lot still not editable on the website like the tools
    descriptions questions etc".
    """
    assert source in PROSE


def test_a_tools_questions_and_description_are_both_editable() -> None:
    fields = {f for f, _l, _long in PROSE["tools"][2]}
    assert {"summary", "landing_blurb", "body_md", "faq_md"} <= fields
