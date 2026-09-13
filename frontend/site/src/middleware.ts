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

/* Imported for its side effect: loading it starts warming the festival cache.
 *
 * Middleware is loaded when the server boots; a route module is not loaded
 * until somebody asks for that route. Putting the warm behind the calendar
 * pages meant it fired for the first time on the first request to one of
 * them, so that visitor still waited the full thirty seconds and the warm
 * helped only the second. Here it runs at boot, before anyone has asked. */
import "./lib/festivals";

const ADMIN_COOKIE = "shruti_session";
/** The only admin paths reachable without a session. */
const OPEN_ADMIN = new Set(["/admin/signin", "/admin/signout", "/admin/reset"]);

/* ── the holding page ──────────────────────────────────────────────────────
 *
 * While it is on, every visitor gets it and she gets the real site, so she can
 * finish building in the open without anyone else seeing a half-made page.
 *
 * These paths stay reachable regardless, and each for a reason rather than by
 * habit:
 *
 *   /privacy, /terms      the holding page links to them, and a legal page
 *                         behind a wall is not a legal page
 *   /newsletter/confirm   the double opt-in link, which the holding page's own
 *                         form sends. Gate this and subscribing silently
 *                         cannot complete — the one flow the page exists for
 *   /newsletter/*         unsubscribe and preferences, for the same reason
 *   /admin*               she has to be able to sign in to turn it off
 *   /coming-soon          the page itself, or the rewrite loops
 */
const ALWAYS_OPEN = [
  "/privacy", "/terms", "/coming-soon",
  "/newsletter/confirm", "/newsletter/unsubscribed", "/newsletter/preferences",
];

/** Assets and machine endpoints, which a holding page must not swallow.
 *
 * `/overlay/` is here for a sharper reason than the rest. An overlay is
 * fetched by OBS, which is not signed in and never will be — it is a browser
 * with no session carrying only a token in the URL. Left to the gate, every
 * overlay would render the HOLDING PAGE, and the first place anybody would
 * notice is on a live stream.
 *
 * It is safe to open because it is not open: each overlay authenticates by an
 * unguessable token and returns nothing a stranger could not already see by
 * watching the stream it is drawn on. */
const PASS_THROUGH = /^\/(_astro|_image|api|media|overlay\/|favicon|apple-touch-icon|icon-|social-card|robots\.txt|sitemap\.xml|site\.webmanifest|passkeys\.js|first-paint\.js|brand\/)/;

/* Asked once and remembered briefly. The middleware runs on EVERY request, and
 * a database round trip per asset would be absurd — but the toggle has to take
 * effect quickly enough that she does not think it is broken, so the window is
 * seconds rather than minutes. */
let holdingState: { on: boolean; at: number; sections: Record<string, boolean> } | null = null;
const HOLDING_TTL_MS = 5_000;

/* Sections she can finish in private.
 *
 * Each is a whole area that can be built out — products written, twelve
 * horoscopes drafted, a course recorded — while the public gets a 404. The
 * admin is untouched: hiding a section changes what VISITORS reach and nothing
 * about what she can make.
 *
 * A 404 rather than a "coming soon" page, deliberately. A section that is not
 * ready should not be advertised, and a teaser is a promise with a date on it
 * that nobody agreed to. The links come out of the nav at the same time, so
 * nobody is sent to one.
 *
 * Absent means live: a section that vanished because a settings row was missing
 * would be the worst kind of surprise. */
const SECTION_PATHS: Record<string, string> = {
  "/shop": "shop",
  "/horoscopes": "horoscopes",
  "/classes": "classes",
  "/guides": "guides",
};

function sectionOf(path: string): string | null {
  for (const [prefix, name] of Object.entries(SECTION_PATHS)) {
    if (path === prefix || path.startsWith(prefix + "/")) return name;
  }
  return null;
}

async function siteState(): Promise<{ on: boolean; sections: Record<string, boolean> }> {
  const now = Date.now();
  if (holdingState && now - holdingState.at < HOLDING_TTL_MS) return holdingState;
  try {
    const r = await fetch(`${SITE_API}/api/content/site-state`);
    if (!r.ok) throw new Error(String(r.status));
    const body = await r.json();
    holdingState = {
      on: Boolean(body?.comingSoon),
      sections: body?.sections ?? {},
      at: now,
    };
  } catch {
    /* If the backend cannot be asked, keep the LAST KNOWN answer, and default
     * to showing the site rather than the holding page. Getting this backwards
     * would mean a backend hiccup takes the whole live site down and replaces
     * it with "coming soon", which is far worse than briefly showing a site
     * that was meant to be hidden.
     *
     * Sections default to LIVE for the same reason: a blip should not 404 the
     * shop. */
    holdingState = { on: holdingState?.on ?? false, sections: holdingState?.sections ?? {}, at: now };
  }
  return holdingState;
}

async function isOperator(token: string | undefined): Promise<boolean> {
  if (!token) return false;
  try {
    const r = await fetch(`${SITE_API}/api/admin/me`, {
      headers: { cookie: `${ADMIN_COOKIE}=${token}` },
    });
    return r.ok;
  } catch {
    return false;
  }
}

export const onRequest = defineMiddleware(async (context, next) => {
  const secure =
    context.url.protocol === "https:" ||
    context.request.headers.get("x-forwarded-proto") === "https";
  context.locals.csrf = csrfToken(context.cookies, secure);

  const path = context.url.pathname;
  const token = context.cookies.get(ADMIN_COOKIE)?.value;

  if (path === "/admin" || path.startsWith("/admin/")) {
    if (!OPEN_ADMIN.has(path)) {
      if (!(await isOperator(token))) {
        return context.redirect(`/admin/signin?next=${encodeURIComponent(path)}`, 303);
      }
    }
    return next();
  }

  /* The holding page stands in front of everything else — unless she is signed
   * in, in which case she gets the real site and can work on it in public
   * without publishing it. */
  if (!PASS_THROUGH.test(path) && !ALWAYS_OPEN.includes(path)) {
    const state = await siteState();
    /* Handed to the header and the footer so a hidden section has no link.
       They read what the gate decided rather than asking again — two sources
       for one answer is how a nav ends up pointing at a 404. */
    context.locals.sectionsLive = state.sections;

    /* A section she has not published yet. Checked before the holding page so
       the two do not have to know about each other: while the holding page is
       up nobody reaches either, and after it comes down this still holds. */
    const section = sectionOf(path);
    if (section && state.sections[section] === false) {
      if (!(await isOperator(token))) {
        /* A rewrite so the visitor keeps the URL they asked for — a redirect
           would rewrite the link they were given.
           The status is set HERE rather than trusted to the page: a rewrite
           keeps the status of the request it came from, so /404 rendered
           through one comes back 200. A 200 saying "not found" is a lie told
           to a crawler as much as to a person, and it is exactly how pages
           that do not exist get indexed. */
        const notFound = await context.rewrite("/404");
        return new Response(notFound.body, {
          status: 404,
          headers: notFound.headers,
        });
      }
      context.locals.previewingSection = section;
    }

    if (state.on) {
      if (!(await isOperator(token))) {
        /* A REWRITE, not a redirect: the visitor stays at the URL they asked
         * for. A redirect would rewrite every shared link to /coming-soon and
         * leave those links pointing at a page that will not exist after
         * launch. */
        return context.rewrite("/coming-soon");
      }
      /* She is through the gate. The site has to SAY so — the header only
       * reflects a reader session, so an admin cookie is invisible, and
       * without a marker the honest reading of a normal-looking site is that
       * the holding page is broken. */
      context.locals.bypassingHolding = true;
    }
  }

  return next();
});
