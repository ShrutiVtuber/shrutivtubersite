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
import re
import hmac
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
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


def canonical_query(params: dict[str, str]) -> str:
    """
    The query string as SigV4 wants it: sorted by key, both halves encoded.

    Sorted by the ENCODED key, which is the specification's wording and differs
    from sorting the raw ones whenever a character encodes to something that
    sorts differently. It has never mattered for the keys used here, and it is
    written correctly anyway so it never has to be discovered.
    """
    pairs = sorted(
        (quote(k, safe="~"), quote(v, safe="~")) for k, v in params.items()
    )
    return "&".join(f"{k}={v}" for k, v in pairs)


def authorization_header(
    *, method: str, host: str, path: str, payload: bytes,
    access_key: str, secret_key: str, region: str, service: str,
    amz_date: str, content_type: str, query: str = "",
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
        query,
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


async def delete(filename: str, backend: str) -> None:
    """
    Remove one stored file.

    **The row's backend decides where to look**, not the current
    configuration — a file uploaded before R2 was switched on is on disk, and
    asking the bucket to delete it would report success having done nothing.

    A file that is already gone is not an error. The caller's intent is that it
    should not exist, and it does not; raising here would leave a database row
    that cannot be removed because its file was tidied up by hand.
    """
    if backend == "r2":
        await _delete_r2(filename)
        return

    path = Path(get_settings().media_root) / filename
    try:
        path.unlink()
    except FileNotFoundError:
        log.info("media %s was already gone from disk", filename)


async def _delete_r2(filename: str) -> None:
    s = get_settings()
    host = f"{s.r2_account_id}.r2.cloudflarestorage.com"
    path = f"/{s.r2_bucket}/{filename}"
    amz_date = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    headers = authorization_header(
        method="DELETE", host=host, path=path, payload=b"",
        access_key=s.r2_access_key_id, secret_key=s.r2_secret_access_key,
        region="auto", service="s3",
        amz_date=amz_date,
        # The signer always signs content-type, so it has to be a value that
        # actually goes out on the wire: an empty one risks httpx dropping the
        # header and the signature then covering something that was not sent,
        # which is the usual reason SigV4 is rejected with nothing useful said.
        content_type="application/octet-stream",
    )
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.delete(f"https://{host}{path}", headers=headers)
    # S3 answers 204 for a delete and, by design, also for a key that was never
    # there. 404 is treated the same way for the same reason as on disk.
    if r.status_code not in (200, 204, 404):
        raise RuntimeError(f"R2 returned {r.status_code} deleting {filename}")


async def list_objects(prefix: str = "") -> list[tuple[str, int]]:
    """
    Every key in the bucket, with its size.

    Exists so orphans can be FOUND, not just avoided. Deleting a media row
    removes its object, and has since that route was written — but that only
    protects files deleted through the admin. A failed upload, a database
    restored from before an upload, or somebody clearing rows in SQL all leave
    an object nothing in the database knows about, and without a listing there
    is no way to discover one short of opening the Cloudflare dashboard.

    Paginated properly rather than taking the first page: a truncated listing
    would report a bucket as clean by looking at part of it, which is worse
    than not looking.
    """
    if not r2_configured():
        return []

    s = get_settings()
    host = f"{s.r2_account_id}.r2.cloudflarestorage.com"
    path = f"/{s.r2_bucket}"

    out: list[tuple[str, int]] = []
    token = ""
    for _ in range(200):                     # 200k keys, then something is wrong
        params = {"list-type": "2", "max-keys": "1000"}
        if prefix:
            params["prefix"] = prefix
        if token:
            params["continuation-token"] = token
        query = canonical_query(params)

        headers = authorization_header(
            method="GET", host=host, path=path, payload=b"",
            access_key=s.r2_access_key_id, secret_key=s.r2_secret_access_key,
            region="auto", service="s3",
            amz_date=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            content_type="application/octet-stream",
            query=query,
        )
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"https://{host}{path}?{query}", headers=headers)
        if r.status_code != 200:
            raise RuntimeError(f"R2 returned {r.status_code} listing the bucket")

        body = r.text
        for chunk in re.findall(r"<Contents>(.*?)</Contents>", body, re.S):
            key = re.search(r"<Key>(.*?)</Key>", chunk, re.S)
            size = re.search(r"<Size>(\d+)</Size>", chunk)
            if key:
                out.append((unescape(key.group(1)), int(size.group(1)) if size else 0))

        truncated = "<IsTruncated>true</IsTruncated>" in body
        nxt = re.search(r"<NextContinuationToken>(.*?)</NextContinuationToken>",
                        body, re.S)
        if not truncated or not nxt:
            break
        token = unescape(nxt.group(1))

    return out


def public_url(filename: str, backend: str = "r2") -> str:
    """
    Where a stored file is read from.

    **`backend` is the row's, not the current configuration's.** A file
    uploaded before R2 was switched on is still on disk, and answering for it
    from the current settings would send the browser to /api/media/, which
    reads the bucket, where that file has never been. Every media row records
    its backend precisely so switching R2 on does not 404 what came before —
    and that promise is only kept if this function is told.

    The rule used to live in the two call sites instead, written out twice.

    Three cases, and the middle one is the one that used to be wrong:

      - a public base is set — a custom domain or r2.dev — so use it;
      - R2 is on with no public base, so serve it through this site, because
        `/media/` is Caddy reading local disk and the file is not there;
      - no R2 at all, so `/media/` is right and Caddy has the file.
    """
    if backend != "r2":
        return f"/media/{filename}"
    s = get_settings()
    base = (getattr(s, "r2_public_base", "") or "").rstrip("/")
    if base and r2_configured():
        return f"{base}/{filename}"
    if r2_configured():
        return f"/api/media/{filename}"
    # An R2 row with R2 switched off: the bucket still holds it, but nothing
    # here can reach it. /media/ at least tries disk rather than a path that
    # is guaranteed to fail.
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
