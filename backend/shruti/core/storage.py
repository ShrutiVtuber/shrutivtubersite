# SPDX-License-Identifier: AGPL-3.0-only
"""
Where uploaded media lives.

Two backends behind one interface, chosen by whether R2 is configured:

  - **Local disk**, which is what exists today and what runs in development.
    Files land under `media_root` and Caddy serves them.
  - **Cloudflare R2**, which is S3-compatible. Chosen the moment the four R2
    settings are present, and ignored otherwise — so a missing credential
    degrades to the working local path rather than to an error at upload time.

**Signed by hand rather than with boto3.** boto3 is a large synchronous
dependency in a service that is otherwise async and talks HTTP with httpx, and
it would be pulled in for exactly one operation: PUT an object. SigV4 is
deterministic and specified, so it is implemented here and tested against
Amazon's own published example — the one whose expected signature is printed in
the documentation, which is the only way to be sure a signer is right without
a live account.

Content-addressed either way: the object key is the file's SHA-256, so the same
file uploaded twice is stored once and every URL is stable and cacheable
forever.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import httpx

from shruti.core.config import get_settings

log = logging.getLogger(__name__)


@dataclass
class Stored:
    key: str
    url: str
    backend: str


def _sign(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def signing_key(secret: str, date: str, region: str, service: str) -> bytes:
    """The SigV4 chained signing key. Separate so it can be tested directly."""
    k = _sign(f"AWS4{secret}".encode("utf-8"), date)
    k = _sign(k, region)
    k = _sign(k, service)
    return _sign(k, "aws4_request")


def authorization_header(
    *, method: str, host: str, path: str, payload: bytes,
    access_key: str, secret_key: str, region: str, service: str,
    amz_date: str, content_type: str,
) -> dict[str, str]:
    """
    Build the SigV4 headers for one request.

    Only the headers actually signed are included, and they are signed in the
    order the specification requires — lowercase names, sorted, semicolon
    separated. Getting that order wrong is the usual reason a signature is
    rejected with no useful message.
    """
    date = amz_date[:8]
    payload_hash = hashlib.sha256(payload).hexdigest()

    signed_headers = "content-type;host;x-amz-content-sha256;x-amz-date"
    canonical_headers = (
        f"content-type:{content_type}\n"
        f"host:{host}\n"
        f"x-amz-content-sha256:{payload_hash}\n"
        f"x-amz-date:{amz_date}\n"
    )
    canonical_request = "\n".join([
        method,
        quote(path, safe="/~"),
        "",                                  # no query string
        canonical_headers,
        signed_headers,
        payload_hash,
    ])

    scope = f"{date}/{region}/{service}/aws4_request"
    string_to_sign = "\n".join([
        "AWS4-HMAC-SHA256",
        amz_date,
        scope,
        hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
    ])
    signature = hmac.new(
        signing_key(secret_key, date, region, service),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return {
        "Authorization": (
            f"AWS4-HMAC-SHA256 Credential={access_key}/{scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        ),
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": amz_date,
        "Content-Type": content_type,
    }


def r2_configured() -> bool:
    s = get_settings()
    return all([
        getattr(s, "r2_account_id", ""), getattr(s, "r2_bucket", ""),
        getattr(s, "r2_access_key_id", ""), getattr(s, "r2_secret_access_key", ""),
    ])


async def put(filename: str, data: bytes, content_type: str) -> Stored:
    """Store one file and return where it can be read from."""
    if r2_configured():
        try:
            return await _put_r2(filename, data, content_type)
        except Exception as exc:                   # noqa: BLE001
            # A storage outage must not lose the upload. Fall back to disk and
            # say so loudly; the row still points at a file that exists.
            log.warning("R2 upload failed (%s); storing locally instead", type(exc).__name__)
    return _put_local(filename, data)


def _put_local(filename: str, data: bytes) -> Stored:
    root = Path(get_settings().media_root)
    root.mkdir(parents=True, exist_ok=True)
    (root / filename).write_bytes(data)
    return Stored(key=filename, url=f"/media/{filename}", backend="local")


async def _put_r2(filename: str, data: bytes, content_type: str) -> Stored:
    s = get_settings()
    host = f"{s.r2_account_id}.r2.cloudflarestorage.com"
    path = f"/{s.r2_bucket}/{filename}"
    amz_date = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    headers = authorization_header(
        method="PUT", host=host, path=path, payload=data,
        access_key=s.r2_access_key_id, secret_key=s.r2_secret_access_key,
        # R2 ignores the region but SigV4 requires one, and "auto" is what
        # Cloudflare's own documentation uses.
        region="auto", service="s3",
        amz_date=amz_date, content_type=content_type,
    )
    # Objects are content-addressed, so a URL can never point at different
    # bytes later. A year is conservative; immutable says the rest.
    headers["Cache-Control"] = "public, max-age=31536000, immutable"

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.put(f"https://{host}{path}", content=data, headers=headers)
    if r.status_code >= 300:
        raise RuntimeError(f"R2 returned {r.status_code}")

    return Stored(key=filename, url=public_url(filename), backend="r2")


def public_url(filename: str) -> str:
    """
    Where a stored file is read from, without needing the row's backend.

    Three cases, and the middle one is the one that used to be wrong:

      - a public base is set — a custom domain or r2.dev — so use it;
      - R2 is on with no public base, so serve it through this site, because
        `/media/` is Caddy reading local disk and the file is not there;
      - no R2 at all, so `/media/` is right and Caddy has the file.
    """
    s = get_settings()
    base = (getattr(s, "r2_public_base", "") or "").rstrip("/")
    if base and r2_configured():
        return f"{base}/{filename}"
    if r2_configured():
        return f"/api/media/{filename}"
    return f"/media/{filename}"


async def fetch(filename: str) -> tuple[bytes, str] | None:
    """
    Read one object back out of R2. `(bytes, content type)`, or None.

    **This exists because "R2 write-only" was not a working state.** With the
    bucket configured but no public base, `put` stored the file in R2 and
    handed back `/media/<name>` — a path Caddy serves from local disk, where
    the file is not. Every image uploaded would have 404'd, and the row would
    have looked completely correct while it happened.

    The alternative was Cloudflare's r2.dev subdomain, and serving through the
    site is better anyway: one origin rather than a third-party hostname in the
    markup, no dependence on a dashboard toggle, and r2.dev is rate-limited and
    documented as not for production. The site is already behind Cloudflare, so
    the caching that mattered is not lost.
    """
    if not r2_configured():
        return None
    s = get_settings()
    host = f"{s.r2_account_id}.r2.cloudflarestorage.com"
    path = f"/{s.r2_bucket}/{filename}"
    amz_date = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    headers = authorization_header(
        method="GET", host=host, path=path, payload=b"",
        access_key=s.r2_access_key_id, secret_key=s.r2_secret_access_key,
        region="auto", service="s3", amz_date=amz_date,
        # Signed as empty, because a GET has no body and the signature covers
        # the header list — sending a Content-Type here that was not signed is
        # the usual way this fails with an unhelpful AccessDenied.
        content_type="",
    )
    headers.pop("Content-Type", None)

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(f"https://{host}{path}", headers=headers)
    except Exception as exc:                       # noqa: BLE001
        log.warning("R2 fetch failed (%s)", type(exc).__name__)
        return None
    if r.status_code != 200:
        return None
    return r.content, r.headers.get("content-type", "application/octet-stream")
