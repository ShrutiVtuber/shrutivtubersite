/* sitemap.xml.
 *
 * Hand-rolled rather than generated at build time, because this site renders
 * on the server: the journal entries and newsletter issues that belong in a
 * sitemap do not exist when the build runs, and a sitemap frozen at build time
 * would list the pages that existed the day it was deployed and nothing since.
 *
 * The backend is asked for what it has published. If it does not answer, the
 * static routes still ship — a partial sitemap is useful and a 500 is not.
 */
import type { APIRoute } from "astro";

/* The origin comes from configuration, NOT from the request.
 *
 * Behind Caddy the Node adapter reports `Astro.url.origin` as
 * "http://localhost" whatever Host says — the same fact that forced Astro's
 * own origin check off in astro.config.mjs. A sitemap full of localhost URLs
 * is invisibly wrong for as long as nobody opens it. */
const SITE = (import.meta.env.SHRUTI_SITE_URL ?? "https://shrutivtuber.com").replace(/\/$/, "");

import { site, SITE_API } from "../lib/api";

/** Weekly-ish reference surfaces, and the pages that are simply always there. */
const STATIC: [path: string, priority: string, changefreq: string][] = [
  ["/", "1.0", "weekly"],
  ["/today", "0.9", "daily"],
  ["/about", "0.7", "monthly"],
  ["/work", "0.7", "monthly"],
  ["/schedule", "0.7", "weekly"],
  ["/videos", "0.7", "weekly"],
  /* Trailing slash deliberate: /journal 301s to /journal/, and a sitemap
     that lists the redirecting form spends a crawl on the hop every time. */
  ["/journal/", "0.8", "weekly"],
  /* The hub the nine instruments hang off. It is the page worth linking to
     from outside, so it outranks any single calculator in this list. */
  ["/tools", "0.9", "monthly"],
  /* Deliberately indexable: somebody checking whether a shop is real should
     be able to find this by searching, not only by already being here. */
  ["/official", "0.6", "monthly"],
  /* The collab planner is for other creators rather than for her audience,
     which is exactly why it is worth being findable: it is the page most
     likely to earn a link from somebody else's site. */
  ["/collab", "0.7", "monthly"],
  ["/horoscopes", "0.8", "weekly"],
  ["/horoscopes/archive", "0.6", "weekly"],
  ["/fan-works", "0.5", "monthly"],
  ["/press", "0.4", "yearly"],
  ["/contact", "0.4", "yearly"],
  ["/support", "0.6", "monthly"],
  ["/newsletter", "0.6", "monthly"],
  ["/guidelines", "0.3", "yearly"],
  ["/privacy", "0.3", "yearly"],
  ["/terms", "0.3", "yearly"],
  // The instruments. These are what the site is for, so they rank with the
  // homepage rather than below the brochure pages.
  ["/tools/solar-stations", "0.9", "monthly"],
  ["/tools/lunar-stations", "0.9", "monthly"],
  ["/tools/planetary-hours", "0.9", "monthly"],
  ["/compatible", "0.8", "monthly"],
  ["/partners", "0.5", "monthly"],
  ["/tools/natal-chart", "0.9", "monthly"],
  ["/tools/attic-calendar", "0.9", "monthly"],
  ["/tools/hindu-calendar", "0.9", "monthly"],
  ["/tools/pancanga", "0.9", "monthly"],
  ["/tools/isopsephy", "0.8", "monthly"],
  ["/tools/sigil-generator", "0.8", "monthly"],
];

const SIGNS = [
  "aries", "taurus", "gemini", "cancer", "leo", "virgo",
  "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
];

const escape = (text: string) =>
  text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

/* A hidden section is not in the sitemap. Listing a URL that returns 404 is
   how a site teaches a crawler to distrust its own sitemap. */
async function hiddenSections(): Promise<Set<string>> {
  try {
    const r = await fetch(`${SITE_API}/api/content/site-state`);
    if (!r.ok) return new Set();
    const body = await r.json();
    return new Set(
      Object.entries(body?.sections ?? {})
        .filter(([, live]) => live === false)
        .map(([name]) => `/${name}`),
    );
  } catch {
    return new Set();
  }
}

export const GET: APIRoute = async () => {
  const origin = SITE;

  const entries: string[] = [];
  const add = (path: string, priority: string, changefreq: string, lastmod?: string) =>
    entries.push(
      `  <url>\n    <loc>${escape(origin + path)}</loc>\n` +
        (lastmod ? `    <lastmod>${lastmod.slice(0, 10)}</lastmod>\n` : "") +
        `    <changefreq>${changefreq}</changefreq>\n    <priority>${priority}</priority>\n  </url>`,
    );

  const hidden = await hiddenSections();
  const reachable = (path: string) =>
    ![...hidden].some((prefix) => path === prefix || path.startsWith(prefix + "/"));

  for (const [path, priority, changefreq] of STATIC) {
    if (reachable(path)) add(path, priority, changefreq);
  }
  if (reachable("/horoscopes")) {
    for (const sign of SIGNS) add(`/horoscopes/${sign}/monthly`, "0.7", "monthly");
  }

  /* Published writing, if the backend is reachable. Absent, the static list
     above is still a valid sitemap. */
  /* The endpoint returns a bare ARRAY, not an object with an `issues` key —
     the shape /newsletter itself reads. Getting that wrong here would have
     produced a sitemap that silently listed no writing at all, which is the
     failure mode a sitemap is least likely to have noticed. */
  const archive = (await site<{ slug: string; sentAt: string | null }[]>(
    "/api/newsletter/archive",
  )) ?? [];
  for (const issue of archive) {
    add(`/newsletter/archive/${issue.slug}`, "0.5", "yearly", issue.sentAt ?? undefined);
  }

  const xml =
    `<?xml version="1.0" encoding="UTF-8"?>\n` +
    `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
    entries.join("\n") +
    `\n</urlset>\n`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
};
