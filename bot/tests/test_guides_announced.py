"""A published guide is announced, and only by the site."""
from __future__ import annotations

import inspect
import re

from vcordbot import app as app_module
from vcordbot import bridge, config


def test_the_message_says_what_and_where() -> None:
    content, embed = bridge.guide_message({
        "id": 1, "slug": "squirrel", "gameSlug": "diablo-iv",
        "title": "Shruti's Diablo IV Squirrel Guide for Warlocks", "game": "Diablo IV",
        "author": "Shruti", "steps": 78, "phases": 9, "summary": "", "isUpdate": False,
    }, "https://shrutivtuber.com")
    assert content == ""
    assert embed["url"] == "https://shrutivtuber.com/guides/diablo-iv/squirrel"
    assert embed["title"].startswith("Shruti's Diablo IV")
    assert "78 steps" in embed["footer"]["text"] and "new guide" in embed["footer"]["text"]
    assert "9 phases" in embed["description"]


def test_an_update_says_so() -> None:
    _, embed = bridge.guide_message({"id": 2, "isUpdate": True, "steps": 3}, "https://x")
    assert "updated guide" in embed["footer"]["text"]


def test_a_long_summary_is_cut_at_a_word() -> None:
    _, embed = bridge.guide_message({"id": 3, "summary": "word " * 400}, "https://x")
    assert embed["description"].endswith("…") and len(embed["description"]) <= bridge.OPENING + 1


def test_no_channel_is_a_working_state() -> None:
    import asyncio
    assert asyncio.run(bridge.announce_guide({"id": 1}, channel_id="", token="t", site_url="https://x")) == ""


def test_the_endpoint_checks_the_secret_in_constant_time() -> None:
    src = inspect.getsource(app_module.guide_published)
    assert "hmac.compare_digest(x_shruti_internal, secret)" in src
    assert "if not secret or" in src            # a missing secret refuses everything


def test_the_channel_is_configured_by_its_own_variable() -> None:
    src = inspect.getsource(config.load)
    assert 'guides_channel_id=_env("SHRUTI_DISCORD_GUIDES_CHANNEL", "")' in src


def test_the_message_carries_no_step_text() -> None:
    """The guide is a page, and the page is the link."""
    src = inspect.getsource(bridge.guide_message)
    assert not re.search(r'guide\.get\("(steps_text|body|do)"', src)
    assert 'guide.get("summary")' in src
