/* Runs before any page renders.
 *
 * Two jobs, and both have to happen HERE rather than in a component:
 *
 * 1. The CSRF token. Astro streams responses, so a `cookies.set()` from inside
 *    a child component happens after the headers have gone out and the
 *    Set-Cookie is silently dropped — the field renders a token the browser
 *    never stores, and every submission then fails to match.
 *
 * 2. The admin guard. Returning `Astro.redirect()` from a LAYOUT does not
 *    short-circuit anything: the page has already begun streaming by then, so
 *    the redirect throws mid-response and the visitor gets a 200 carrying
 *    "Internal server error". No content leaked, but nothing worked either.
 *    Middleware runs before the first byte, so a redirect here is a real
 *    redirect.
 */
import { defineMiddleware } from "astro:middleware";
import { csrfToken } from "./lib/csrf";
import { SITE_API } from "./lib/api";

const ADMIN_COOKIE = "shruti_session";
/** The only admin paths reachable without a session. */
const OPEN_ADMIN = new Set(["/admin/signin", "/admin/signout"]);

export const onRequest = defineMiddleware(async (context, next) => {
  const secure =
    context.url.protocol === "https:" ||
    context.request.headers.get("x-forwarded-proto") === "https";
  context.locals.csrf = csrfToken(context.cookies, secure);

  const path = context.url.pathname;
  if (path === "/admin" || path.startsWith("/admin/")) {
    if (!OPEN_ADMIN.has(path)) {
      const token = context.cookies.get(ADMIN_COOKIE)?.value;
      let ok = false;
      if (token) {
        try {
          const r = await fetch(`${SITE_API}/api/admin/me`, {
            headers: { cookie: `${ADMIN_COOKIE}=${token}` },
          });
          ok = r.ok;
        } catch {
          ok = false;
        }
      }
      if (!ok) {
        return context.redirect(`/admin/signin?next=${encodeURIComponent(path)}`, 303);
      }
    }
  }

  return next();
});
