/* A cacheable JSON answer for the app: an ETag from the body, 304 when the
   app already holds it, and ten minutes of public caching. */
import { createHash } from "node:crypto";

export function cachedJson(request: Request, body: unknown, status = 200): Response {
  const text = JSON.stringify(body);
  const etag = `"${createHash("sha256").update(text).digest("hex").slice(0, 32)}"`;
  const headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "public, max-age=600",
    ETag: etag,
  };
  if (status === 200 && request.headers.get("if-none-match") === etag) {
    return new Response(null, { status: 304, headers });
  }
  return new Response(text, { status, headers: status === 200 ? headers : { "Content-Type": headers["Content-Type"] } });
}
