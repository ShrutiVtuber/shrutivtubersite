# SPDX-License-Identifier: AGPL-3.0-only
"""
The three consents, the one acknowledgement before publishing, and their
exact wording.

**Three decisions, never one.** Someone must be able to say yes to one and no
to another, so these are three separate records with three different lawful
bases — not one checkbox that means "I agree to everything".

The wording lives here so it can be VERSIONED and stored verbatim with each
record. If it changes, the version changes, and every existing record still
says what that person actually read.

Only the CONTRACT consent can ever be required. A special-category consent that
blocked a submit would not be freely given, and consent that is not freely
given is not consent.
"""
from __future__ import annotations

from dataclasses import dataclass

# Bump when any wording below changes. Records keep the version they were
# given under.
CONSENT_VERSION = "2026-09-26.1"


@dataclass(frozen=True)
class ConsentSpec:
    kind: str
    label: str
    wording: str
    lawful_basis: str
    required: bool
    explanation: str


ACCOUNT = ConsentSpec(
    kind="account",
    label="Create the account",
    wording=(
        "I want an account on shrutivtuber.com. My email address and the "
        "preferences I set are stored so I can sign in and read what I have "
        "saved."
    ),
    lawful_basis="contract",
    required=True,
    explanation=(
        "This is the account itself — an email address and the settings you "
        "choose. Without it there is nothing to sign in to."
    ),
)

NATIVITY = ConsentSpec(
    kind="nativity",
    label="Store my birth data for astrological readings",
    wording=(
        "I consent to shrutivtuber.com storing my birth date, birth time and "
        "birth place, and using them to compute astrological readings for me. "
        "I understand this may reveal something about my philosophical beliefs, "
        "and that I can withdraw this consent at any time, which deletes the "
        "birth data."
    ),
    lawful_basis="explicit-consent",
    required=False,
    explanation=(
        "Birth data used to produce an astrological reading arguably reveals "
        "philosophical belief, which makes it special-category data. So it "
        "gets its own decision, it is never required, and withdrawing it "
        "deletes the saved nativity — the account survives."
    ),
)

NEWSLETTER = ConsentSpec(
    kind="newsletter",
    label="Send me the monthly letter",
    wording=(
        "I want the monthly letter by email, including offers for astrological "
        "courses and magickal services when those open. I can unsubscribe in "
        "one click from any issue."
    ),
    lawful_basis="consent",
    required=False,
    explanation=(
        "One letter a month. It carries commercial offers when there are any, "
        "and that is said here rather than buried in the privacy policy."
    ),
)

# ⚠ Asked the first time somebody makes anything public — never at signup,
# which is why it is not in ALL: signup, the account settings list and the
# app's consent screen all render ALL, and none of them is the moment this
# decision belongs to. It is filed as a ConsentRecord like the others, with
# its wording verbatim, and it is checked by WORDING rather than by version,
# so a change to one of the three above does not ask everybody again.
PUBLISH = ConsentSpec(
    kind="publish",
    label="What happens to what I publish",
    wording=(
        "I understand that what I make public on shrutivtuber.com — a guide, "
        "a change to somebody's guide, a reading, a comment, a group, a "
        "contribution to a group, a shared build — is read and relied on by "
        "other people. If I delete my account, my account and everything "
        "private go, and what I made public stays up with my name taken off "
        "it. Copies already posted to Discord cannot be called back."
    ),
    lawful_basis="contract",
    required=False,
    explanation=(
        "People follow a guide for weeks and answer each other's readings. "
        "Deleting an account removes you, not the thing they are in the "
        "middle of using. You are asked once, before the first thing you make "
        "public, and it stays readable on your account page."
    ),
)

ALL = (ACCOUNT, NATIVITY, NEWSLETTER)
ON_PUBLISH = (PUBLISH,)
BY_KIND = {c.kind: c for c in (*ALL, *ON_PUBLISH)}
