# SPDX-License-Identifier: AGPL-3.0-only
"""
An account does not work until the address behind it is proved.

⚠ **Her decision, 12 September 2026**: "we need the email verification — on the
site and on the app." The practice room carries other people's writing, and an
unproved address is how that gets abused: somebody suspended makes another
account in seconds with an address nobody can reach.

⚠ **The field was already there.** `email_verified_at` has existed since the
accounts were built, was already set by the password-reset and sign-in-link
flows, and was already shown in the admin. Nothing sent a confirmation and
nothing checked it. A half-built feature made of working halves, which is the
shape this project has been bitten by before and the reason these tests are
about ENFORCEMENT rather than about a column.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

from shruti.api.routes import accounts


def code_of(function) -> str:
    """Source with comments and docstring stripped — as everywhere here."""
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def test_signing_up_does_not_sign_you_in() -> None:
    body = code_of(accounts.sign_up)
    assert "_send_verification" in body, "sign-up sends no confirmation"
    assert "checkEmail" in body
    # ⚠ The whole point: no session and no bearer token comes back.
    assert "_set_session" not in body, "sign-up still starts a session"
    assert "issue_session" not in body, "sign-up still hands out a token"


def test_an_unconfirmed_address_cannot_sign_in() -> None:
    body = code_of(accounts.sign_in)
    assert "email_verified_at is None" in body, "nothing checks confirmation"
    assert "403" in body, "the refusal should be a 403 the app can act on"


def test_the_check_comes_after_the_password() -> None:
    """
    ⚠ **Order matters more than the check does.**

    Refusing an unconfirmed address BEFORE the password is verified would tell
    a stranger which addresses have accounts here — type an address, see a
    different error, learn the answer. Every other reply in this file is
    careful not to say that, and this one must be too.
    """
    body = code_of(accounts.sign_in)
    password_check = body.index("verify_password")
    confirmation_check = body.index("email_verified_at is None")
    assert password_check < confirmation_check, (
        "an unconfirmed address is refused before the password is checked, "
        "which turns the sign-in form into an oracle"
    )


def test_following_the_link_confirms_and_signs_in() -> None:
    body = code_of(accounts.confirm_address)
    assert 'purpose="verify"' in body, "the link is not purpose-scoped"
    assert "email_verified_at" in body
    assert "_set_session" in body, "confirming should sign them in"


def test_confirming_twice_is_not_an_error() -> None:
    """
    ⚠ Mail clients follow links to check them and people press back. A second
    visit answering "that link has expired" about a perfectly good account is
    a support request nobody needed.
    """
    body = code_of(accounts.confirm_address)
    assert "user.email_verified_at or" in body, (
        "confirming a second time overwrites or rejects instead of passing"
    )


def test_asking_again_says_the_same_thing_either_way() -> None:
    body = code_of(accounts.resend_verification)
    assert "checkEmail" in body
    # ⚠ One exit, so there is no shape to read off the answer.
    assert body.count("return") == 1, (
        "resend answers differently depending on whether the account exists"
    )


def test_the_link_cannot_stand_in_for_another_kind() -> None:
    """A confirmation link must not be usable as a sign-in or reset link."""
    source = inspect.getsource(accounts)
    assert 'purpose="verify"' in source
    assert 'purpose="signin"' in source
    assert 'purpose="reset"' in source


def test_everyone_who_already_had_an_account_keeps_it() -> None:
    """
    ⚠ **The failure this migration prevents.** Three accounts existed when the
    rule changed, two of them unconfirmed — one being the App Store reviewer's
    demo account. Enforcing without grandfathering locks them all out, and the
    reviewer's on the first morning.
    """
    versions = Path(__file__).resolve().parents[1] / "alembic" / "versions"
    migration = next(versions.glob("*confirmed_addresses.py")).read_text()
    assert "UPDATE site_user SET email_verified_at" in migration
    assert "WHERE email_verified_at IS NULL" in migration


def test_the_site_stops_saying_you_are_in() -> None:
    """
    ⚠ It used to say "You're in" and offer to add a nativity. That is now
    false, and it is said with NEW copy keys so an admin override written for
    the old wording cannot put it back on a page that means the opposite.
    """
    from conftest import SITE
    page = (SITE / "src" / "pages" / "signup.astro").read_text()
    assert 'say("confirm.title"' in page
    assert "Check your email" in page
    assert '"text.11", "You\'re in"' not in page


def test_the_confirmation_page_exists() -> None:
    from conftest import SITE
    page = (SITE / "src" / "pages" / "verify.astro").read_text()
    assert "/api/account/verify?token=" in page
    assert "redirectWithCookies" in page, "confirming does not carry the session"


def test_a_short_password_is_refused_in_our_own_words() -> None:
    """
    ⚠ **Pydantic's message reached a screen, and then a video.**

    A length constraint on the schema produces "String should have at least 10
    characters". The app shows the server's `detail` verbatim — deliberately,
    so the server can say the useful thing — and that sentence appeared in the
    recording made for App Review. A reviewer reading developer output
    concludes the app is unfinished, and would not be wrong.

    ⚠ Checked against the source with COMMENTS STRIPPED. The fifth time in this
    project that a guard has failed on correct code by finding the forbidden
    token in the prose explaining why it is forbidden.
    """
    source = re.sub(r"(?m)#.*$", " ", inspect.getsource(accounts))
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    assert "min_length=10" not in source, (
        "the schema still words its own failure"
    )
    assert accounts.PASSWORD_TOO_SHORT == "A password needs ten characters or more."
    # ⚠ Both doors: making an account, and setting a new password from a link.
    assert "_refuse_a_short_password" in code_of(accounts.sign_up)
    assert "_refuse_a_short_password" in code_of(accounts.do_reset)


def test_the_rule_is_still_enforced() -> None:
    """Moving the check out of the schema must not move it out of existence."""
    import pytest
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as caught:
        accounts._refuse_a_short_password("short")
    assert caught.value.status_code == 422
    # And a good one passes, and None passes — accounts may have no password.
    accounts._refuse_a_short_password("a-long-enough-one")
    accounts._refuse_a_short_password(None)
