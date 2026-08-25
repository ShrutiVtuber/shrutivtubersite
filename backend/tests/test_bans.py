# SPDX-License-Identifier: AGPL-3.0-only
"""
Barring an address, and what the list is allowed to remember.

Banning deletes the account, so the ban has to outlive it — and that puts the
list in an awkward position: it must recognise an address it is not supposed
to be keeping. Hence a hash. These are the properties that makes it hold.
"""
from __future__ import annotations

from shruti.core import bans


def test_the_same_address_always_makes_the_same_fingerprint():
    assert bans.fingerprint("Sophia@Example.ORG") == bans.fingerprint("  sophia@example.org  ")


def test_different_addresses_do_not_collide():
    assert bans.fingerprint("a@example.org") != bans.fingerprint("b@example.org")


def test_the_fingerprint_is_not_the_address():
    """
    The whole point.

    A ban follows a deletion; a list holding the addresses in readable form
    would quietly rebuild the thing the deletion was for.
    """
    printed = bans.fingerprint("sophia@example.org")
    assert "sophia" not in printed
    assert "@" not in printed
    assert len(printed) == 64


def test_the_hint_is_recognisable_but_not_writable():
    """
    Enough to pick a ban out of a list; not enough to send anything to.

    A list of opaque hashes is one she cannot review at all, which is its own
    failure — an unban she cannot find is an unban she cannot grant.
    """
    hint = bans.hint("sophia@example.org")
    assert hint == "s…a@example.org"
    assert "sophia" not in hint


def test_a_two_letter_local_part_is_still_not_spelled_out():
    assert bans.hint("jo@example.org") == "j…@example.org"


def test_a_hint_of_something_that_is_not_an_address_says_nothing():
    assert bans.hint("not-an-address") == "…"
    assert bans.hint("") == "…"


def test_normalising_is_what_makes_a_ban_stick():
    """
    Someone barred as `Sophia@Example.org` must not walk back in as
    `sophia@example.org`, which is the same mailbox by every rule that matters.
    """
    variants = [
        "sophia@example.org", "SOPHIA@EXAMPLE.ORG",
        " Sophia@Example.Org ", "sophia@example.org\t",
    ]
    assert len({bans.fingerprint(v) for v in variants}) == 1
