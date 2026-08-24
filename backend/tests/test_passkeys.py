# SPDX-License-Identifier: AGPL-3.0-only
"""
Passkeys.

Two things are worth testing here and they are different in kind.

The **challenge store** is ours, and it is the part that would fail quietly:
a challenge that survives its first use, or that can be spent on a different
purpose than it was issued for, still passes every signature check while no
longer proving anything. So it is tested for being single-use, for expiring,
and for refusing to cross purposes.

The **credential handling** is a contract with the browser, and the way to
test a contract is to hold up the other end of it. `SoftAuthenticator` is a
real one: an ECDSA P-256 keypair, CBOR attestation, a genuine signature over
`authenticatorData || SHA256(clientDataJSON)`. If the base64url translation
or the response shape were wrong, verification would refuse it — which is the
point, because that is the failure this file exists to catch.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os

import cbor2
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from webauthn import verify_authentication_response, verify_registration_response

from shruti.api.routes import passkeys as pk
from shruti.core.config import get_settings

ORIGIN = "http://localhost:8200"
RP_ID = "localhost"


def b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


class SoftAuthenticator:
    """A security key made of arithmetic. Signs for real."""

    def __init__(self) -> None:
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.credential_id = os.urandom(32)
        self.count = 0

    def _cose(self) -> bytes:
        n = self.key.public_key().public_numbers()
        return cbor2.dumps({
            1: 2, 3: -7, -1: 1,
            -2: n.x.to_bytes(32, "big"), -3: n.y.to_bytes(32, "big"),
        })

    def _auth_data(self, attested: bool) -> bytes:
        flags = 0x45 if attested else 0x05          # UP | UV (| AT)
        data = hashlib.sha256(RP_ID.encode()).digest() + bytes([flags])
        data += self.count.to_bytes(4, "big")
        if attested:
            data += b"\x00" * 16
            data += len(self.credential_id).to_bytes(2, "big")
            data += self.credential_id + self._cose()
        return data

    def _client_data(self, kind: str, challenge: str) -> bytes:
        return json.dumps(
            {"type": kind, "challenge": challenge, "origin": ORIGIN, "crossOrigin": False},
            separators=(",", ":"),
        ).encode()

    def create(self, challenge: bytes) -> dict:
        client = self._client_data("webauthn.create", b64(challenge))
        attestation = cbor2.dumps(
            {"fmt": "none", "attStmt": {}, "authData": self._auth_data(True)}
        )
        return {
            "id": b64(self.credential_id), "rawId": b64(self.credential_id),
            "type": "public-key",
            "response": {
                "clientDataJSON": b64(client),
                "attestationObject": b64(attestation),
                "transports": ["internal"],
            },
            "clientExtensionResults": {},
        }

    def get(self, challenge: bytes) -> dict:
        self.count += 1
        client = self._client_data("webauthn.get", b64(challenge))
        auth = self._auth_data(False)
        signature = self.key.sign(
            auth + hashlib.sha256(client).digest(), ec.ECDSA(hashes.SHA256())
        )
        return {
            "id": b64(self.credential_id), "rawId": b64(self.credential_id),
            "type": "public-key",
            "response": {
                "clientDataJSON": b64(client), "authenticatorData": b64(auth),
                "signature": b64(signature), "userHandle": None,
            },
            "clientExtensionResults": {},
        }


# ── the credential round trip ───────────────────────────────────────────────

def test_registration_then_authentication_round_trips() -> None:
    device = SoftAuthenticator()
    challenge = os.urandom(32)

    registered = verify_registration_response(
        credential=device.create(challenge),
        expected_challenge=challenge,
        expected_origin=ORIGIN,
        expected_rp_id=RP_ID,
    )
    # Stored exactly as the route stores it — through our base64, not the
    # library's, because ours is the half that could be wrong.
    stored_key = pk._unb64(pk._b64(registered.credential_public_key))
    assert stored_key == registered.credential_public_key

    second = os.urandom(32)
    result = verify_authentication_response(
        credential=device.get(second),
        expected_challenge=second,
        expected_origin=ORIGIN,
        expected_rp_id=RP_ID,
        credential_public_key=stored_key,
        credential_current_sign_count=0,
    )
    assert result.new_sign_count == 1


def test_a_signature_over_a_different_challenge_is_refused() -> None:
    """The whole point of a challenge: a valid signature over the wrong one is
    still a replay, and must not authenticate anybody."""
    device = SoftAuthenticator()
    challenge = os.urandom(32)
    registered = verify_registration_response(
        credential=device.create(challenge), expected_challenge=challenge,
        expected_origin=ORIGIN, expected_rp_id=RP_ID,
    )
    with pytest.raises(Exception):
        verify_authentication_response(
            credential=device.get(os.urandom(32)),      # signed the wrong one
            expected_challenge=os.urandom(32),
            expected_origin=ORIGIN, expected_rp_id=RP_ID,
            credential_public_key=registered.credential_public_key,
            credential_current_sign_count=0,
        )


def test_a_credential_for_another_origin_is_refused() -> None:
    device = SoftAuthenticator()
    challenge = os.urandom(32)
    with pytest.raises(Exception):
        verify_registration_response(
            credential=device.create(challenge), expected_challenge=challenge,
            expected_origin="https://not-this-site.example",
            expected_rp_id="not-this-site.example",
        )


# ── the challenge store ─────────────────────────────────────────────────────

class _Response:
    def __init__(self) -> None:
        self.cookies: dict[str, str] = {}

    def set_cookie(self, name, value, **_):     # noqa: ANN001
        self.cookies[name] = value


class _Request:
    def __init__(self, cookies=None, headers=None):     # noqa: ANN001
        self.cookies = cookies or {}
        self.headers = headers or {}


def _issue(purpose: str = "signin") -> tuple[_Request, bytes]:
    response = _Response()
    challenge = os.urandom(32)
    pk._store_challenge(response, challenge, purpose, secure=False)
    return _Request({pk.CHALLENGE_COOKIE: response.cookies[pk.CHALLENGE_COOKIE]}), challenge


def test_a_challenge_is_spent_by_its_first_use() -> None:
    request, challenge = _issue()
    assert pk._take_challenge(request, "signin") == challenge
    with pytest.raises(Exception):
        pk._take_challenge(request, "signin")


def test_a_challenge_cannot_be_spent_on_a_different_purpose() -> None:
    """A sign-in challenge redeemed as a registration would let anyone holding
    one mint a credential — bound purposes are what stop that."""
    request, _ = _issue("signin")
    with pytest.raises(Exception):
        pk._take_challenge(request, "register")


def test_an_expired_challenge_is_refused() -> None:
    request, _ = _issue()
    key = request.cookies[pk.CHALLENGE_COOKIE]
    challenge, _expires, purpose = pk._challenges[key]
    pk._challenges[key] = (challenge, 0.0, purpose)         # already stale
    with pytest.raises(Exception):
        pk._take_challenge(request, "signin")


def test_no_cookie_means_no_challenge() -> None:
    with pytest.raises(Exception):
        pk._take_challenge(_Request(), "signin")


# ── the relying party ───────────────────────────────────────────────────────

@pytest.fixture
def configured(monkeypatch):
    """Settings are cached, so an env change alone would not be seen."""
    def apply(env: str, site: str = "https://shrutivtuber.com"):
        monkeypatch.setenv("SHRUTI_SITE_URL", site)
        monkeypatch.setenv("SHRUTI_ENV", env)
        get_settings.cache_clear()
        return get_settings()
    yield apply
    get_settings.cache_clear()


def test_an_unknown_origin_cannot_introduce_itself(configured) -> None:
    """A forged Origin must not be able to scope a credential elsewhere. The
    header only ever PICKS from the allowlist."""
    configured("prod")
    rp_id, origin = pk._relying_party(_Request(headers={"origin": "https://evil.example"}))
    assert rp_id == "shrutivtuber.com"
    assert origin == "https://shrutivtuber.com"


def test_localhost_is_allowed_off_production(configured) -> None:
    configured("development")
    rp_id, origin = pk._relying_party(_Request(headers={"origin": ORIGIN}))
    assert (rp_id, origin) == ("localhost", ORIGIN)


@pytest.mark.parametrize("env", ["prod", "production"])
def test_localhost_is_not_allowed_in_production(configured, env: str) -> None:
    """BOTH spellings. `is_production` accepts "prod" and "production", and a
    second definition of production living in this module would have quietly
    allowed localhost passkeys on a server whose env said the longer word."""
    configured(env)
    rp_id, _ = pk._relying_party(_Request(headers={"origin": ORIGIN}))
    assert rp_id == "shrutivtuber.com"
