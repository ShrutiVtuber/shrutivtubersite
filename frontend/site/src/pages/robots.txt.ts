/* robots.txt.
 *
 * Generated rather than static, because the sitemap URL has to carry the real
 * host and a wrong one in a static file is invisible until it has been wrong
 * for a month.
 *
 * The disallowed paths are not secrets — they are guarded server-side — but a
 * crawler following them produces sign-in pages in search results and a pile
 * of pointless load. `/api/` is excluded because indexing JSON helps nobody.
 *
 * `/chart/` is deliberately NOT disallowed, and that is the opposite of what
 * it used to say. Those pages carry somebody's birth data drawn, so the first
 * instinct is to block the whole prefix — but blocking here is both weaker
 * and more damaging than it looks.
 *
 * Weaker, because a URL disallowed in robots.txt can still be listed in a
 * search result from links alone: the crawler is forbidden to FETCH it, so it
 * never reads the `noindex` that would actually keep it out. Keeping a page
 * out of an index is `noindex`'s job, and `noindex` only works on a page a
 * crawler is allowed to read. Every private chart page sends it.
 *
 * More damaging, because the compatibility share link — the whole point of
 * that feature — lives at `/chart/compare/s/…`, and its card at
 * `/api/charts/compare/…/card.png`. Twitter/X, Discord, Facebook and Slack
 * all check robots.txt before fetching a link to build its preview. Under the
 * old rules every shared comparison unfurled as a bare grey link with no
 * image, on exactly the platforms the feature exists for. Nothing errors,
 * nothing logs, and the page itself is perfectly fine when opened by hand.
 */
import type { APIRoute } from "astro";

import { SITE_API } from "../lib/api";

/* The origin comes from configuration, NOT from the request.
 *
 * Behind Caddy the Node adapter reports `Astro.url.origin` as
 * "http://localhost" whatever Host says — the same fact that forced Astro's
 * own origin check off in astro.config.mjs. A sitemap full of localhost URLs
 * is invisibly wrong for as long as nobody opens it. */
const SITE = (import.meta.env.SHRUTI_SITE_URL ?? "https://shrutivtuber.com").replace(/\/$/, "");


export const GET: APIRoute = async () => {
  const origin = SITE;

  /* While the holding page is up, ask crawlers to stay away entirely.
   *
   * Every real page is behind the gate and would be served the holding page,
   * so a crawler following the sitemap would index one `noindex` page a
   * hundred times over. Worse, anything it did keep would be a snapshot of a
   * site that is not finished — and a stale first impression in search
   * outlives the holding page by months. */
  let holding = false;
  try {
    const r = await fetch(`${SITE_API}/api/content/site-state`);
    if (r.ok) holding = Boolean((await r.json())?.comingSoon);
  } catch {
    /* Unreachable backend: assume live, and let the normal rules apply. A
       robots.txt that disallows everything because of a blip is the more
       expensive mistake — it can take weeks to be re-crawled. */
  }

  if (holding) {
    return new Response(
      `User-agent: *\nDisallow: /\n`,
      { headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" } },
    );
  }

  /* `Allow: /api/charts/compare/` sits under the broader `Disallow: /api/`
     on purpose. RFC 9309 resolves a conflict by the LONGEST matching rule, so
     the share card is reachable while the rest of the JSON stays out. */
  const body = `User-agent: *
Allow: /
Disallow: /admin
Disallow: /account
Disallow: /signin
Disallow: /signup
Disallow: /api/
Allow: /api/charts/compare/

Sitemap: ${origin}/sitemap.xml
`;
  return new Response(body, {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=86400" },
  });
};
