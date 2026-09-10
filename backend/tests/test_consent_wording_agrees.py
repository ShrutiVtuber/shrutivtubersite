# SPDX-License-Identifier: AGPL-3.0-only
"""
What a person reads is what gets filed — now in three places.

`scripts/check_consent_wording.py` has held the website's TypeScript against the
backend's Python since the consents were written, and its docstring says "run in
CI". Nothing ran it: grep finds its name nowhere but in itself. A guard nobody
invokes is a comment.

So it runs here, in the suite that actually runs — and the app makes a third
consumer, reading the wording from `GET /api/account/consents` rather than
keeping a copy, so that endpoint is checked against the same source.
"""
from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

from shruti.api.routes.accounts import consent_wording
from shruti.core.consents import ALL, CONSENT_VERSION

from conftest import ROOT   # noqa: E402  (see conftest for why)


def test_the_website_and_the_backend_still_say_the_same_thing() -> None:
    script = ROOT / "scripts" / "check_consent_wording.py"
    done = subprocess.run([sys.executable, str(script)],
                          capture_output=True, text=True)
    assert done.returncode == 0, (
        "the consent wording has drifted between the site and the backend:\n"
        + done.stdout + done.stderr
    )


def test_the_app_is_served_exactly_what_the_backend_files() -> None:
    served = asyncio.run(consent_wording())
    assert served["version"] == CONSENT_VERSION

    by_kind = {c["kind"]: c for c in served["consents"]}
    assert set(by_kind) == {c.kind for c in ALL}
    for spec in ALL:
        got = by_kind[spec.kind]
        assert got["wording"] == spec.wording, f"{spec.kind}: wording differs"
        assert got["label"] == spec.label
        assert got["basis"] == spec.lawful_basis
        assert got["required"] is spec.required
        assert got["explanation"] == spec.explanation


def test_only_the_contract_consent_may_be_required() -> None:
    """
    The rule the module states, checked rather than remembered: a
    special-category consent that blocked a submit would not be freely given,
    and consent that is not freely given is not consent.
    """
    served = asyncio.run(consent_wording())
    for c in served["consents"]:
        if c["required"]:
            assert c["basis"] == "contract", (
                f"{c['kind']} is required but its basis is {c['basis']!r}"
            )
