/* CSRF protection: signed double-submit token.
 *
 * WHY NOT ASTRO'S BUILT-IN `security.checkOrigin`. It compares the Origin
 * header against `Astro.url.origin`, and behind Caddy the Node adapter reports
 * `http://localhost` no matter what Host or X-Forwarded-Host say. Every form
 * POST was rejected with "Cross-site POST form submissions are forbidden",
 * including same-origin ones from a real browser. Pinning `site` would fix the
 * demo and break production, or the reverse — the origin is not knowable from
 * config when the same build serves both.
 *
 * So the check moves here, where it does not depend on the proxy telling the
 * truth about the host:
 *
 *   - a random 32-byte token is issued in a cookie, HttpOnly and SameSite=Lax;
 *   - the server renders the same value into a hidden field;
 *   - a POST is accepted only when the two match, compared in constant time.
 *
 * SameSite=Lax already stops a cross-site form POST carrying the cookie at
 * all, so this is belt and braces rather than the only line of defence.
 */
import type { AstroCookies } from "astro";

const COOKIE = "shruti_csrf";
const FIELD = "_csrf";

function issue(): string {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

/** The token for this visitor, minting and setting one if there is none. */
export function csrfToken(cookies: AstroCookies, secure: boolean): string {
  const existing = cookies.get(COOKIE)?.value;
  if (existing) return existing;
  const token = issue();
  cookies.set(COOKIE, token, {
    path: "/",
    httpOnly: true,
    sameSite: "lax",
    secure,
    maxAge: 60 * 60 * 8,
  });
  return token;
}

/** Constant-time compare, so a wrong token leaks nothing through timing. */
function sameToken(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export function verifyCsrf(cookies: AstroCookies, form: FormData): boolean {
  const cookie = cookies.get(COOKIE)?.value ?? "";
  const submitted = String(form.get(FIELD) ?? "");
  return cookie.length > 0 && sameToken(cookie, submitted);
}

export const CSRF_FIELD = FIELD;
