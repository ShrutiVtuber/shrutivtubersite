/* Redirect while keeping the cookies the backend just set.
 *
 * `Astro.redirect()` returns a NEW Response, so anything appended to
 * `Astro.response.headers` before it is discarded — including the Set-Cookie
 * that just authenticated someone. The symptom is a login that redirects
 * cleanly and lands you back on the sign-in form, which reads like a wrong
 * password rather than a dropped header.
 *
 * `getSetCookie()` rather than `get()`: a response may carry several cookies
 * and `get()` folds them into one comma-joined string that no browser parses
 * back correctly.
 */
export function redirectWithCookies(
  location: string, from: Response, status: 302 | 303 = 303,
): Response {
  const headers = new Headers({ Location: location });
  const cookies =
    typeof (from.headers as any).getSetCookie === "function"
      ? (from.headers as any).getSetCookie()
      : [from.headers.get("set-cookie")].filter(Boolean);
  for (const cookie of cookies) headers.append("set-cookie", cookie as string);
  return new Response(null, { status, headers });
}
