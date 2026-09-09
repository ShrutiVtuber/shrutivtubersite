"""
SigV4 signing, checked against Amazon's own published example.

Without a live account this is the only way to know a signer is correct: AWS
documents a complete worked example with the expected signature printed, so a
signer that reproduces it byte for byte is right. A signer that is wrong fails
against R2 with a 403 and no useful message, which is a bad way to find out.
"""
from __future__ import annotations

from types import SimpleNamespace

import hashlib
import hmac

from shruti.core import storage
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


def test_urls_fall_back_to_local_when_r2_is_not_configured(monkeypatch):
    """A half-configured bucket must not produce URLs that 404.

    ⚠ The configuration is forced, not inherited. This used to call
    `public_url` and trust the machine, so it passed on a laptop with no bucket
    and failed on one with `.env` filled in — a red test that says nothing
    about the code is worse than no test, because the next person learns to
    scroll past it.
    """
    monkeypatch.setattr(storage, "r2_configured", lambda: False)
    assert public_url("abc.png") == "/media/abc.png"


def test_urls_go_through_this_site_when_r2_is_on_without_a_public_base(monkeypatch):
    """The other branch, pinned for the same reason."""
    monkeypatch.setattr(storage, "r2_configured", lambda: True)
    monkeypatch.setattr(storage, "get_settings",
                        lambda: SimpleNamespace(r2_public_base=""))
    assert public_url("abc.png") == "/api/media/abc.png"


# ── where a stored file is read from ────────────────────────────────────────

def test_r2_with_no_public_base_serves_through_the_site(monkeypatch) -> None:
    """
    The case that was broken, and broken invisibly.

    R2 configured without a public base used to hand back `/media/<name>`.
    That path is Caddy reading local disk, and with R2 on the file is not
    there — so every uploaded image 404'd while the database row looked
    completely correct.
    """
    from shruti.core.config import get_settings
    from shruti.core.storage import public_url

    for key, value in (
        ("R2_ACCOUNT_ID", "acct"), ("R2_BUCKET", "b"),
        ("R2_ACCESS_KEY_ID", "ak"), ("R2_SECRET_ACCESS_KEY", "sk"),
        ("R2_PUBLIC_BASE", ""),
    ):
        monkeypatch.setenv(f"SHRUTI_{key}", value)
    get_settings.cache_clear()
    try:
        assert public_url("x.png", "r2") == "/api/media/x.png"
        # The promise the storage_backend column exists to keep: a file
        # uploaded before R2 was switched on is still on disk.
        assert public_url("old.png", "local") == "/media/old.png"
    finally:
        get_settings.cache_clear()


def test_a_public_base_is_used_when_there_is_one(monkeypatch) -> None:
    from shruti.core.config import get_settings
    from shruti.core.storage import public_url

    for key, value in (
        ("R2_ACCOUNT_ID", "acct"), ("R2_BUCKET", "b"),
        ("R2_ACCESS_KEY_ID", "ak"), ("R2_SECRET_ACCESS_KEY", "sk"),
        ("R2_PUBLIC_BASE", "https://media.example.com/"),
    ):
        monkeypatch.setenv(f"SHRUTI_{key}", value)
    get_settings.cache_clear()
    try:
        assert public_url("x.png", "r2") == "https://media.example.com/x.png"
        assert public_url("old.png", "local") == "/media/old.png"
    finally:
        get_settings.cache_clear()


def test_without_r2_the_disk_path_is_still_right(monkeypatch) -> None:
    from shruti.core.config import get_settings
    from shruti.core.storage import public_url

    monkeypatch.setenv("SHRUTI_R2_ACCOUNT_ID", "")
    monkeypatch.setenv("SHRUTI_R2_BUCKET", "")
    get_settings.cache_clear()
    try:
        assert public_url("x.png", "r2") == "/media/x.png"
        assert public_url("x.png", "local") == "/media/x.png"
    finally:
        get_settings.cache_clear()


# ── the filename guard ──────────────────────────────────────────────────────

def test_only_generated_filenames_reach_the_bucket() -> None:
    """A key with a slash or a `..` turns a read of one object into a read of
    somebody else's prefix. Uploader-generated names are content-addressed, so
    anything not of that shape is refused rather than forwarded."""
    from shruti.api.routes.media import SAFE

    for good in ("a.png", "abc123.jpg", "x_y-z.webp", "A1.gif"):
        assert SAFE.match(good), good
    for bad in (
        "../secret", "a/b.png", "..", ".hidden", "/etc/passwd",
        "a b.png", "a?b.png", "", "x" * 300,
    ):
        assert not SAFE.match(bad), bad


# ── the bucket listing, and orphans ─────────────────────────────────────────

def test_the_query_string_is_canonical_and_sorted() -> None:
    """
    SigV4 sorts by the ENCODED key and encodes both halves. A listing that gets
    this wrong fails with a 403 and nothing useful said, which is the same bad
    afternoon as a wrong signature.
    """
    from shruti.core.storage import canonical_query

    got = canonical_query({
        "list-type": "2",
        "continuation-token": "1/abc+def=",
        "max-keys": "1000",
    })
    assert got == (
        "continuation-token=1%2Fabc%2Bdef%3D&list-type=2&max-keys=1000"
    )


def test_the_query_string_is_signed() -> None:
    """
    The signer used to hardcode an empty query string, which was correct while
    it only ever did PUT, GET and DELETE on a bare key. A listing carries its
    parameters in the query, so an unsigned one is a signature over a request
    that was not sent.
    """
    common = dict(
        method="GET", host="acct.r2.cloudflarestorage.com", path="/bucket",
        payload=b"", access_key="AK", secret_key="SK",
        region="auto", service="s3", amz_date="20260826T120000Z",
        content_type="application/octet-stream",
    )
    bare = authorization_header(**common)
    listed = authorization_header(**common, query="list-type=2")
    assert bare["Authorization"] != listed["Authorization"], (
        "the query string is not part of what gets signed")


def test_the_listing_pages_rather_than_taking_the_first_page() -> None:
    """
    A truncated listing reports a bucket as clean by looking at part of it —
    worse than not looking, because it is believed.
    """
    import inspect

    from shruti.core.storage import list_objects

    src = inspect.getsource(list_objects)
    assert "IsTruncated" in src
    assert "NextContinuationToken" in src
    assert "continuation-token" in src


def test_sweeping_is_refused_outside_production() -> None:
    """
    Development points at the SAME bucket as the live site, so a laptop's
    database calls every production image an orphan. Found the hard way: this
    check, run locally, listed four live project thumbnails as orphans.

    The listing is safe to read anywhere. Only the environment that owns the
    bucket may act on it.
    """
    import inspect

    from shruti.api.routes.admin import media_orphans, sweep_orphans

    sweep = inspect.getsource(sweep_orphans)
    assert 'env != "production"' in sweep, "the sweep runs anywhere"
    # And the refusal comes before anything is deleted.
    assert sweep.index("production") < sweep.index("delete_stored")

    listing = inspect.getsource(media_orphans)
    assert '"canSweep"' in listing, "the page cannot tell whether it may act"


def test_a_swept_name_is_rechecked_against_the_database() -> None:
    """
    The page she is looking at may be minutes old. A file that has gained a
    row since the listing must be skipped, not deleted because the page was
    stale.
    """
    import inspect

    from shruti.api.routes.admin import sweep_orphans

    src = inspect.getsource(sweep_orphans)
    assert "select(Media).where(Media.filename == name)" in src
    assert "skipped" in src
