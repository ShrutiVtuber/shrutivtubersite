/* robots.txt.
 *
 * Generated rather than static, because the sitemap URL has to carry the real
 * host and a wrong one in a static file is invisible until it has been wrong
 * for a month.
 *
 * The disallowed paths are not secrets — they are guarded server-side — but a
 * crawler following them produces sign-in pages in search results and a pile
 * of pointless load. `/api/` is excluded because indexing JSON helps nobody.
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

  const body = `User-agent: *
Allow: /
Disallow: /admin
Disallow: /account
Disallow: /signin
Disallow: /signup
Disallow: /api/

Sitemap: ${origin}/sitemap.xml
`;
  return new Response(body, {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=86400" },
  });
};
