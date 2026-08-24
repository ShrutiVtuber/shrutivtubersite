/* Runs before any page renders.
 *
 * The CSRF token has to be minted here rather than in the component that
 * renders the hidden field. Astro streams responses, so a `cookies.set()` from
 * inside a child component happens after the headers have gone out and the
 * Set-Cookie is silently dropped — the field renders a token the browser never
 * stores, and every submission then fails to match. Middleware runs before the
 * first byte, so the header lands.
 */
import { defineMiddleware } from "astro:middleware";
import { csrfToken } from "./lib/csrf";

export const onRequest = defineMiddleware((context, next) => {
  const secure =
    context.url.protocol === "https:" ||
    context.request.headers.get("x-forwarded-proto") === "https";
  context.locals.csrf = csrfToken(context.cookies, secure);
  return next();
});
