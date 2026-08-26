# SPDX-License-Identifier: AGPL-3.0-only
"""
The planner works without an account, and the account is worth having anyway.

Both halves matter and they pull in opposite directions. A tool that quietly
needs a login is worse than one that never offered it — and an account benefit
nobody can name is not a benefit. The bargain here is the same one saved charts
make: everything works signed out, and signing in removes a chore.

The chore is real and specific: a plan lives in its URL, which is what makes it
shareable, and a URL cannot follow you to another machine.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

from shruti.api.routes import collab


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()
PAGE = SRC / "pages" / "collab.astro"


def _prose_free(text: str) -> str:
    """Comments discuss the rules; only the code should be searched for them."""
    text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r'"""[\s\S]*?"""', "", text)


def test_saving_needs_an_account() -> None:
    body = _prose_free(inspect.getsource(collab.save_group))
    assert "401" in body, "an anonymous save must be refused, not silently dropped"


def test_a_group_belonging_to_somebody_else_is_not_found_rather_than_forbidden() -> None:
    """
    403 would confirm the row exists. Whether somebody else has a group called
    "Tuesday crew" is not this person's business.
    """
    body = _prose_free(inspect.getsource(collab.delete_group))
    assert "user_id != user.id" in body
    assert "404" in body and "403" not in body


def test_saving_the_same_name_updates_instead_of_duplicating() -> None:
    """
    Somebody adjusting one person's hours and pressing save again means "this
    group, corrected". Two rows with one name is worse than either outcome.
    """
    body = _prose_free(inspect.getsource(collab.save_group))
    assert "CollabGroup.name == name" in body


def test_there_are_caps() -> None:
    assert collab.MAX_PEOPLE <= 24
    assert collab.MAX_GROUPS <= 200


def test_the_page_still_works_signed_out() -> None:
    """
    The grid, the answer and the share link are not inside a signed-in branch.
    If they ever are, the tool has started charging an account for its actual
    function, which is the thing this page exists not to do.
    """
    text = PAGE.read_text(encoding="utf-8")
    assert "cb-grid" in text
    # The one thing gated on an account is keeping a group.
    assert "signedIn" in text
    body = _prose_free(text)
    for gated in ("cb-gridwrap", "cb-share", "cb-answer"):
        # None of the load-bearing sections may sit behind the flag.
        assert not re.search(rf"signedIn\s*&&[\s\S]{{0,400}}{gated}", body), (
            f"{gated} is rendered only when signed in — the planner must work "
            f"for somebody who arrived from a link"
        )


def test_the_page_says_what_the_account_is_for() -> None:
    """An account benefit nobody can name is not a benefit."""
    text = PAGE.read_text(encoding="utf-8")
    assert "Keep this group" in text
