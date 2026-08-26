# SPDX-License-Identifier: AGPL-3.0-only
"""
Managing media: naming, tagging, and getting rid of things.

The filename is a content hash and stays one — that is what dedupes an image
uploaded twice and what keeps a URL stable forever. Everything here is about
the human half that sits beside it.
"""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from shruti.api.routes import admin


# ── tags ────────────────────────────────────────────────────────────────────

def test_tags_are_trimmed_and_deduplicated():
    assert admin._clean_tags("overlay, stream,  overlay ,twitch") == "overlay,stream,twitch"


def test_tag_order_is_the_order_they_were_typed():
    """
    Not sorted.

    Sorting would be tidier and would also quietly rearrange what she wrote
    every time she saved, which reads as the field having a mind of its own.
    """
    assert admin._clean_tags("zeta, alpha, mu") == "zeta,alpha,mu"


def test_duplicate_tags_differing_only_in_case_are_one_tag():
    assert admin._clean_tags("Overlay, overlay, OVERLAY") == "Overlay"


def test_empty_and_whitespace_tags_disappear():
    assert admin._clean_tags("") == ""
    assert admin._clean_tags("  ,  , ") == ""
    assert admin._clean_tags("a,,b") == "a,b"


def test_inner_whitespace_is_collapsed_not_stripped():
    """A tag may be two words; it may not be two words and four spaces."""
    assert admin._clean_tags("  stream   overlay  ") == "stream overlay"


# ── deletion checks every table that can point at an image ──────────────────

def test_every_model_with_a_media_id_is_checked_before_deleting():
    """
    The guard is a hand-written list, so this is the thing that rots.

    Adding a fifth table with a `media_id` and forgetting to add it here would
    not fail loudly — deletion would simply stop noticing that table, and the
    first sign would be a blank picture on a live page.
    """
    import shruti.models as models
    import shruti.models.accounts as account_models

    # BOTH modules. Scanning only `shruti.models` and calling the result
    # "every model" is how SavedChart gained an avatar column and stayed
    # unguarded while this test went on passing.
    modules = (models, account_models)

    def media_columns(model: type) -> set[str]:
        # Only real tables. A SQLModel declared with table=False can still carry
        # a __tablename__ and has no __table__ at all.
        table = getattr(model, "__table__", None)
        if table is None:
            return set()
        out = set()
        for column in table.columns:
            for fk in column.foreign_keys:
                if fk.target_fullname == "media.id":
                    out.add(column.name)
        return out

    with_media = {
        model.__name__: media_columns(model)
        for module in modules
        for model in vars(module).values()
        if isinstance(model, type)
        and getattr(model, "__tablename__", None)
        and media_columns(model)
    }
    checked = {model.__name__ for model, _noun in admin.MEDIA_USERS}

    assert with_media, "no model points at media — this test is looking in the wrong place"
    assert set(with_media) == checked, (
        f"not checked before deleting media: {sorted(set(with_media) - checked)}; "
        f"checked but no longer points at media: {sorted(checked - set(with_media))}"
    )

    # And every COLUMN, not just every model. Sponsor carries two — a mark for
    # light backgrounds and one for dark — and a guard that only looked at
    # `media_id` would have deleted the dark one without noticing.
    for model, _noun in admin.MEDIA_USERS:
        found = set(admin._media_columns(model))
        assert found == with_media[model.__name__], (
            f"{model.__name__}: the guard checks {sorted(found)} but the table "
            f"points at media from {sorted(with_media[model.__name__])}"
        )


# ── removing the file itself ────────────────────────────────────────────────

def test_deleting_a_local_file_removes_it():
    from shruti.core import storage
    from shruti.core.config import get_settings

    with tempfile.TemporaryDirectory() as root:
        settings = get_settings()
        original = settings.media_root
        try:
            settings.media_root = root
            target = Path(root) / "abc123.png"
            target.write_bytes(b"not really a png")
            asyncio.run(storage.delete("abc123.png", "local"))
            assert not target.exists()
        finally:
            settings.media_root = original


def test_deleting_a_file_that_is_already_gone_is_not_an_error():
    """
    The caller's intent is that it should not exist, and it does not.

    Raising would leave a row that cannot be deleted because somebody tidied
    its file up by hand — the database would be stuck holding a reference to
    nothing, which is the state this whole feature exists to get out of.
    """
    from shruti.core import storage
    from shruti.core.config import get_settings

    with tempfile.TemporaryDirectory() as root:
        settings = get_settings()
        original = settings.media_root
        try:
            settings.media_root = root
            asyncio.run(storage.delete("never-existed.png", "local"))
        finally:
            settings.media_root = original


# ── the payload one shape ───────────────────────────────────────────────────

def test_media_payload_gives_tags_as_a_list():
    """
    Upload, patch and the listing all answer with this, so a caller's handling
    cannot depend on which one it happened to come from. Before, one returned a
    comma-separated string and another a list.
    """
    from shruti.models import Media

    row = Media(id=1, filename="x.png", mime_type="image/png",
                tags="overlay,twitch", title="Corner frame")
    payload = admin._media_payload(row)

    assert payload["tags"] == ["overlay", "twitch"]
    assert payload["title"] == "Corner frame"
    assert "url" in payload


def test_media_payload_of_an_untagged_row_is_an_empty_list_not_one_empty_string():
    from shruti.models import Media

    row = Media(id=1, filename="x.png", mime_type="image/png", tags="")
    assert admin._media_payload(row)["tags"] == []
