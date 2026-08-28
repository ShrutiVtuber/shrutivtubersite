# SPDX-License-Identifier: AGPL-3.0-only
"""
The endpoint is a public URL. Anyone can POST to it.

Without signature verification a stranger can make this bot say anything, in
every server it is in, by inventing an interaction — and Discord is not
involved at all. So this is not tested by reading the code. A real key signs a
real body, and then the same body is tampered with.

Discord also refuses to save an interactions endpoint that cannot answer its
signed PING, so a mistake here fails closed rather than quietly.
"""
from __future__ import annotations

import importlib
import json
import os

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient


@pytest.fixture()
def signed(monkeypatch):
    """A bot whose public key we hold the private half of."""
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes_raw().hex()

    monkeypatch.setenv("SHRUTI_DISCORD_APP_ID", "123")
    monkeypatch.setenv("SHRUTI_DISCORD_PUBLIC_KEY", public)
    monkeypatch.setenv("SHRUTI_DISCORD_BOT_TOKEN", "not-a-real-token")

    import vcordbot.app as app_module
    importlib.reload(app_module)
    return private, TestClient(app_module.app)


def post(client, private, payload, *, timestamp="1787000000", tamper=False):
    body = json.dumps(payload).encode()
    signature = private.sign(timestamp.encode() + body).hex()
    if tamper:
        body = json.dumps({**payload, "type": 2}).encode()
    return client.post(
        "/interactions", content=body,
        headers={"X-Signature-Ed25519": signature,
                 "X-Signature-Timestamp": timestamp,
                 "Content-Type": "application/json"})


def test_a_correctly_signed_ping_is_answered(signed) -> None:
    private, client = signed
    r = post(client, private, {"type": 1})
    assert r.status_code == 200
    assert r.json() == {"type": 1}, "Discord will not save an endpoint that gets this wrong"


def test_a_tampered_body_is_refused(signed) -> None:
    """The attack: a real signature reused over a different payload."""
    private, client = signed
    r = post(client, private, {"type": 1}, tamper=True)
    assert r.status_code == 401


def test_a_forged_signature_is_refused(signed) -> None:
    _, client = signed
    other = Ed25519PrivateKey.generate()
    r = post(client, other, {"type": 1})
    assert r.status_code == 401


def test_a_replayed_timestamp_changes_the_signature(signed) -> None:
    """
    The timestamp is signed together with the body, so it cannot be swapped
    for a fresher one without invalidating everything.
    """
    private, client = signed
    body = json.dumps({"type": 1}).encode()
    signature = private.sign(b"1787000000" + body).hex()
    r = client.post("/interactions", content=body,
                    headers={"X-Signature-Ed25519": signature,
                             "X-Signature-Timestamp": "1787999999"})
    assert r.status_code == 401


def test_missing_headers_are_refused(signed) -> None:
    _, client = signed
    assert client.post("/interactions", json={"type": 1}).status_code == 401


def test_no_key_means_nothing_is_answered(monkeypatch) -> None:
    """
    Fail closed. A missing key means we cannot tell Discord from anybody else,
    and the safe reading of "cannot tell" is "do not answer" — not "assume it
    is fine", which is how this sort of check gets disabled in development and
    left that way.
    """
    monkeypatch.setenv("SHRUTI_DISCORD_PUBLIC_KEY", "")
    import vcordbot.app as app_module
    importlib.reload(app_module)
    r = TestClient(app_module.app).post(
        "/interactions", json={"type": 1},
        headers={"X-Signature-Ed25519": "00", "X-Signature-Timestamp": "1"})
    assert r.status_code == 503


def test_a_nonsense_key_does_not_crash_the_service(monkeypatch) -> None:
    """A typo in .env should refuse requests, not take the process down."""
    monkeypatch.setenv("SHRUTI_DISCORD_PUBLIC_KEY", "not-hex-at-all")
    import vcordbot.app as app_module
    importlib.reload(app_module)
    assert TestClient(app_module.app).get("/health").json()["verifying"] is False


def test_health_says_nothing_secret(signed) -> None:
    """
    What must hold is that no CREDENTIAL leaves here, not that the field list
    never changes. Frozen against an exact set, this failed the day the watcher
    added two fields and stayed red — a test nobody can act on teaches people
    to ignore the suite, which costs more than the check was worth.

    So: the token must not appear, in any form, and every field is one somebody
    decided to publish. The application id IS published on purpose — it is in
    every invite link — which is why it is named here rather than assumed.
    """
    _, client = signed
    body = client.get("/health").json()

    PUBLIC = {"ok", "app", "verifying", "watcher", "watching", "store"}
    assert set(body) <= PUBLIC, f"unpublished field(s): {set(body) - PUBLIC}"

    said = json.dumps(body).lower()
    assert "not-a-real-token" not in said        # the token from the fixture
    assert "token" not in said
    assert os.environ["SHRUTI_DISCORD_PUBLIC_KEY"] not in json.dumps(body)


def test_health_answers_even_when_the_store_is_not_there(signed) -> None:
    """
    The one moment a health check exists for is a startup that did not finish.
    This read the store directly and raised, so that was the one moment it
    could not answer — a 500 where the useful reply was "store: unavailable".
    """
    _, client = signed
    body = client.get("/health").json()
    assert body["ok"] is True
    assert body["store"] in ("ready", "unavailable")
