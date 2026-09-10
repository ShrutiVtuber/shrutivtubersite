# SPDX-License-Identifier: AGPL-3.0-only
"""
Signing in at the desk also signs her in to her own site.

⚠ **She could administer the practice room and not post in it.** The admin
session and the reader session are two different cookies backed by two
different tables, and holding one never implied the other. So the person who
owns the site could sign in, open it, and be a stranger to it: no account menu,
no kept charts, no practice room — she saved a chart and then could not find a
signed-in page to look at it from.

The fix is not to merge the two systems; they have different lifetimes and
different scopes for good reasons. It is that proving you are the operator also
proves you own that address, and a reader session follows from it.

⚠ **One password, by her decision.** The member account carries the operator's
own password hash, so the password she already types works at the ordinary
sign-in form too. The cost is real and was put to her: that form becomes a
second place her password can be tried. The prize is strictly smaller — a
reader session, never the desk — but it is another door.

These are source-level guards, which is what this suite is: there is no
database fixture here. The runtime behaviour was verified against the running
stack when it was written — the member row appears, the hash matches the
operator's, and a second sign-in does not mint a second account.
"""
from __future__ import annotations

import inspect

from shruti.api.routes import admin


SOURCE = inspect.getsource(admin)
FUNCTION = inspect.getsource(admin._also_a_reader)


def test_every_door_to_the_desk_also_opens_the_site() -> None:
    """
    ⚠ There are THREE ways to become the operator, not one.

    Signing in is the obvious one. Claiming the site during setup and
    completing a password reset each hand out an admin session too, and either
    one left alone would reproduce exactly the bug this fixes — a desk she can
    reach and a site she cannot — reachable by two other routes.
    """
    doors = SOURCE.count('"shruti_session", token')
    calls = SOURCE.count("await _also_a_reader(")
    assert calls == doors, (
        f"{doors} places issue an admin session but {calls} of them also issue "
        "a reader session"
    )


def test_the_member_session_cookie_is_actually_set() -> None:
    """A row in a table nobody is signed in as is not a fix."""
    assert "SESSION_COOKIE, issue_session(" in FUNCTION, (
        "no reader cookie is issued, so she is signed in at the desk and "
        "nowhere else"
    )


def test_the_password_is_copied_from_the_operator() -> None:
    """
    Her decision, and the mechanism that carries it.

    ⚠ Copied, never re-derived. The plaintext is not in scope here and must not
    be — re-hashing would mean this function had to be handed the password, and
    a password travels further every time it is passed to something new. The
    copy also means a changed admin password propagates by itself at her next
    sign-in, with nothing to remember.
    """
    assert "KEY_HASH" in FUNCTION, "the operator's hash is never read"
    assert "user.password_hash = stored" in FUNCTION, (
        "the member account never receives the operator's password, so her one "
        "password does not open the ordinary sign-in form"
    )
    assert "hash_password(" not in FUNCTION, (
        "the password is being re-derived here, which means the plaintext was "
        "passed in; it should be copied from the operator's stored hash"
    )


def test_an_unclaimed_deployment_still_works() -> None:
    """
    ⚠ The hash lives in one of two places depending on age.

    A site that has been claimed keeps it in the database; one that has not yet
    been claimed still runs on `SHRUTI_ADMIN_PASSWORD_HASH`. Reading only the
    first would give the member account no password on exactly the deployments
    where she has not set one through the site.
    """
    assert "SHRUTI_ADMIN_PASSWORD_HASH" in FUNCTION, (
        "only the claimed-site hash is read, so an unclaimed deployment gives "
        "the member account no password at all"
    )


def test_the_address_is_matched_without_regard_to_case() -> None:
    """
    ⚠ `User.email` is unique, and an operator address is typed by hand.

    Matching case-sensitively would either mint a second account for the same
    person or, once the unique constraint refused it, fail the sign-in outright
    — turning a capital letter into a locked door.
    """
    assert "func.lower(User.email)" in FUNCTION, (
        "the member lookup is case-sensitive, so a capital letter makes a "
        "second account or breaks sign-in"
    )
    assert "email.strip().lower()" in FUNCTION, "the address is not normalised"


def test_signing_out_takes_both_sessions() -> None:
    """Sign out must mean signed out, not signed out of one of two things."""
    logout = inspect.getsource(admin.logout)
    assert logout.count("delete_cookie") == 2, (
        "signing out of the desk leaves her signed in as herself on the site"
    )
