"""
SigV4 signing, checked against Amazon's own published example.

Without a live account this is the only way to know a signer is correct: AWS
documents a complete worked example with the expected signature printed, so a
signer that reproduces it byte for byte is right. A signer that is wrong fails
against R2 with a 403 and no useful message, which is a bad way to find out.
"""
from __future__ import annotations

import hashlib
import hmac

from shruti.core.storage import authorization_header, public_url, signing_key


def test_signing_key_matches_the_published_example():
    """
    From AWS's "Examples of the complete Signature Version 4 signing process":
    secret wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY, date 20150830,
    region us-east-1, service iam.
    """
    key = signing_key(
        "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY",
        "20150830", "us-east-1", "iam",
    )
    assert key.hex() == (
        "c4afb1cc5771d871763a393e44b703571b55cc28424d1a5e86da6ed3c154a4b9"
    )


def test_the_header_has_the_shape_r2_requires():
    headers = authorization_header(
        method="PUT", host="acct.r2.cloudflarestorage.com",
        path="/bucket/abc123.png", payload=b"hello",
        access_key="AKIAEXAMPLE", secret_key="secret",
        region="auto", service="s3",
        amz_date="20260824T120000Z", content_type="image/png",
    )
    auth = headers["Authorization"]
    assert auth.startswith("AWS4-HMAC-SHA256 Credential=AKIAEXAMPLE/20260824/auto/s3/aws4_request")
    # Signed headers must be lowercase, sorted and semicolon separated. Getting
    # this wrong is the usual cause of a 403 with no explanation.
    assert "SignedHeaders=content-type;host;x-amz-content-sha256;x-amz-date" in auth
    assert headers["x-amz-content-sha256"] == hashlib.sha256(b"hello").hexdigest()
    assert headers["x-amz-date"] == "20260824T120000Z"


def test_the_payload_hash_is_of_the_actual_body():
    """An unsigned-payload placeholder would let a proxy alter the bytes."""
    a = authorization_header(
        method="PUT", host="h", path="/b/k", payload=b"one",
        access_key="k", secret_key="s", region="auto", service="s3",
        amz_date="20260824T120000Z", content_type="image/png",
    )
    b = authorization_header(
        method="PUT", host="h", path="/b/k", payload=b"two",
        access_key="k", secret_key="s", region="auto", service="s3",
        amz_date="20260824T120000Z", content_type="image/png",
    )
    assert a["Authorization"] != b["Authorization"]


def test_urls_fall_back_to_local_when_r2_is_not_configured():
    """A half-configured bucket must not produce URLs that 404."""
    assert public_url("abc.png") == "/media/abc.png"
