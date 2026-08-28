# SPDX-License-Identifier: AGPL-3.0-only
"""
Answers that cannot arrive in three seconds.

Discord allows three seconds to say ANYTHING before it declares the
application unresponsive. `/chart` asks a gazetteer and then an ephemeris, and
losing that race does not merely look untidy — the person's typed birth details
are gone and they have to enter them again.

The half worth testing hardest is the flag. Whether a chart is private is
settled at the moment of acknowledgement and cannot be changed afterwards, so a
mistake here would put somebody's birth data in a channel.
"""
from __future__ import annotations

import importlib
import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient


@pytest.fixture()
def signed(monkeypatch):
    private = Ed25519PrivateKey.generate()
    monkeypatch.setenv("SHRUTI_DISCORD_APP_ID", "123")
    monkeypatch.setenv("SHRUTI_DISCORD_PUBLIC_KEY",
                       private.public_key().public_bytes_raw().hex())
    monkeypatch.setenv("SHRUTI_DISCORD_BOT_TOKEN", "not-a-real-token")

    import vcordbot.app as app_module
    importlib.reload(app_module)

    # The work itself is exercised in test_dispatch. What matters here is the
    # acknowledgement, so nothing is allowed to reach the network.
    async def never_runs(payload):
        return None
    monkeypatch.setattr(app_module, "_answer_later", never_runs)
    return private, TestClient(app_module.app), app_module


def post(client, private, payload):
    body = json.dumps(payload).encode()
    timestamp = "1787000000"
    return client.post(
        "/interactions", content=body,
        headers={"X-Signature-Ed25519": private.sign(timestamp.encode() + body).hex(),
                 "X-Signature-Timestamp": timestamp,
                 "Content-Type": "application/json"})


def chart(**options):
    return {"type": 2, "token": "interaction-token",
            "data": {"name": "chart",
                     "options": [{"name": k, "value": v} for k, v in options.items()]}}


BIRTH = {"date": "1996-05-14", "time": "09:30",
         "city": "Athens", "country": "Greece"}


def test_a_chart_is_acknowledged_before_the_work_starts(signed) -> None:
    private, client, app_module = signed
    r = post(client, private, chart(**BIRTH))
    assert r.status_code == 200
    assert r.json()["type"] == app_module.DEFERRED_CHANNEL_MESSAGE


def test_the_acknowledgement_is_ephemeral_by_default(signed) -> None:
    """
    The flag cannot be changed by the followup, so getting it wrong here is
    permanent for that message — and it is somebody's birth data.
    """
    private, client, _ = signed
    assert post(client, private, chart(**BIRTH)).json()["data"]["flags"] == 1 << 6


def test_sharing_is_honoured_at_the_acknowledgement(signed) -> None:
    private, client, _ = signed
    r = post(client, private, chart(**BIRTH, share=True))
    assert r.json()["data"]["flags"] == 0


def test_a_fast_command_is_answered_outright(signed) -> None:
    """Deferring everything would make every quick answer arrive as an edit."""
    private, client, _ = signed
    r = post(client, private, {"type": 2, "token": "t",
                               "data": {"name": "help", "options": []}})
    assert r.json()["type"] == 4                     # CHANNEL_MESSAGE, not deferred


def test_the_ping_is_never_deferred(signed) -> None:
    private, client, _ = signed
    assert post(client, private, {"type": 1}).json() == {"type": 1}
