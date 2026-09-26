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

import { site, SITE_API, SITE_URL } from "../lib/api";
import { paths as journalPaths, read as readJournal } from "../lib/journal/parse";
import { lessons as carnaticLessons, ragas as carnaticRagas, talas as carnaticTalas } from "../lib/carnatic/data";
import { lessonList } from "../lib/carnatic/lessons";


/* One origin for the whole site, read at runtime. See lib/env.ts. */
const SITE = SITE_URL;
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
  /* The games wing's front door: every room on one page. Hidden with the
     guides section, whose gate it sits behind. */
  ["/play", "0.8", "weekly"],
  ["/guides", "0.8", "weekly"],
  /* The Ledger's public doors: the planner, the building finder and the
     calculators. A kept business is private and never listed. */
  ["/ledger", "0.6", "monthly"],
  ["/ledger/plan", "0.7", "monthly"],
  ["/ledger/places", "0.6", "monthly"],
  ["/ledger/calculators", "0.6", "monthly"],
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
  /* The Ledger and the Play hub belong to the guides section and are hidden
     with it (middleware SECTION_PATHS), though their addresses do not start
     /guides. */
  const IN_GUIDES = ["/ledger", "/play"];
  const sectionPath = (path: string) =>
    (IN_GUIDES.some((p) => path === p || path.startsWith(p + "/")) ? "/guides" : path);
  const reachable = (path: string) =>
    ![...hidden].some((prefix) => [path, sectionPath(path)].some((p) => p === prefix || p.startsWith(prefix + "/")));

  for (const [path, priority, changefreq] of STATIC) {
    if (reachable(path)) add(path, priority, changefreq);
  }
  if (reachable("/horoscopes")) {
    /* The undated form for each sign — "whatever is current" — plus every
       reading that has actually been published, at its DATED address.
       The dated one is canonical, so listing only the undated form would
       leave every past reading out of the index while pointing crawlers at a
       URL whose content changes underneath them. */
    for (const sign of SIGNS) {
      for (const period of ["daily", "weekly", "monthly", "yearly"]) {
        add(`/horoscopes/${sign}/${period}`, "0.7", period === "daily" ? "daily" : "weekly");
      }
    }
    /* /published is the flat one WITH timestamps. /archive groups by period
       and has none, so a <lastmod> read from it would not exist. */
    const readings = (await site<{ sign: string; period: string; covers: string;
                                   publishedAt: string | null }[]>(
      "/api/horoscopes/published?limit=500")) ?? [];
    for (const r of readings) {
      add(`/horoscopes/${r.sign}/${r.period}/${r.covers}`, "0.6", "never",
          r.publishedAt ?? undefined);
    }
  }

  if (reachable("/guides")) {
    /* Every published guide at its own address, newest first. A hidden one is
       not in this list because the catalogue does not serve it. */
    const guides = (await site<{ game: { slug: string }; slug: string;
                                 publishedAt: string | null }[]>(
      "/api/guides?sort=new&limit=500")) ?? [];
    for (const g of guides) {
      add(`/guides/${g.game.slug}/${g.slug}`, "0.7", "weekly", g.publishedAt ?? undefined);
    }
    /* And each game's almanac page, for the games that have a guide. */
    const games = (await site<{ slug: string; guides: number }[]>("/api/guides/games")) ?? [];
    for (const g of games) {
      if (g.guides > 0) add(`/guides/${g.slug}`, "0.6", "weekly");
    }
  }

  /* Swara Studio, the Carnatic music school: its front pages, then every
     raga, melakarta, tala and lesson page the synced data has. Each page is
     also served in Tamil, Telugu and Kannada with ?lang= and says so with
     hreflang, so only the English address is listed here. The dashboard,
     settings and the review queue are noindex and left out. Until
     the data is synced (scripts/sync-carnatic-data.sh) only the fixed pages
     are listed. */
  if (reachable("/carnatic")) {
    for (const [path, priority] of [
      ["/carnatic", "0.9"], ["/carnatic/ragas", "0.8"], ["/carnatic/talas", "0.7"],
      ["/carnatic/path", "0.7"], ["/carnatic/lessons", "0.7"], ["/carnatic/gamakas", "0.7"],
      ["/carnatic/practice/tuner", "0.8"], ["/carnatic/practice/tala", "0.7"], ["/carnatic/practice/quiz", "0.6"],
      ["/carnatic/compose", "0.6"], ["/carnatic/listen", "0.5"], ["/carnatic/support", "0.4"],
      ...["voice", "venu", "veena", "violin", "mridangam"].map((i) => [`/carnatic/instruments/${i}`, "0.6"]),
    ]) add(path, priority, "monthly");
    try {
      const [rg, tl, ls] = await Promise.all([carnaticRagas(), carnaticTalas(), carnaticLessons()]);
      for (const m of rg?.melakartas ?? []) add(`/carnatic/ragas/melakarta/${m.number}`, "0.5", "monthly");
      for (const r of [...(rg?.janyas ?? []), ...(rg?.performed ?? [])]) add(`/carnatic/ragas/${encodeURIComponent(r.id)}`, "0.6", "monthly");
      for (const x of tl?.practical ?? []) if (x.slug) add(`/carnatic/talas/${x.slug}`, "0.5", "monthly");
      if (ls) for (const l of lessonList(ls, (id) => id)) add(`/carnatic/lessons/${l.slug}`, "0.5", "monthly");
    } catch {
      /* The data is not synced here; the fixed pages above still stand. */
    }
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

  /* The journal: every page the agent has written, not only its front page.
     Until 26 September 2026 the sitemap listed /journal/ and nothing under
     it, so every entry had to be found by following links. The dates come
     from the journal's own index — the list the feed is built from — and a
     page the index does not date is listed without one rather than with a
     guessed date.
     ⚠ With a trailing slash, as /journal/ itself: the journal answers the
     slashless form with a redirect, and a sitemap of redirects spends a
     crawl on every hop. */
  if (reachable("/journal/")) {
    const dated = new Map<string, string>();
    try {
      for (const e of (await readJournal([]))?.entries ?? []) {
        if (e.href && e.date) dated.set(e.href.replace(/\/?$/, "/"), e.date);
      }
    } catch {
      /* The index could not be read; the pages are still listed, undated. */
    }
    let found: string[] = [];
    try {
      found = await journalPaths();
    } catch {
      found = [];
    }
    for (const raw of found) {
      const path = raw.replace(/\/?$/, "/");
      if (path === "/journal/") continue;          // already a static entry
      add(path, "0.6", "monthly", dated.get(path));
    }
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
