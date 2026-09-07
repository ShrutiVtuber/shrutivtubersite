// SPDX-License-Identifier: AGPL-3.0-only
/* One feed per sign.
 *
 * A reader who wants Leo wants Leo, and a single site-wide feed would give
 * them eleven twelfths of it as noise. Twelve small feeds are cheap and each
 * one is worth subscribing to.
 *
 * Only PUBLISHED readings appear, and each entry points at its dated URL — a
 * feed entry that moves is a feed entry read twice, and "this week's reading"
 * is a URL whose content changes underneath the reader.
 */
import type { APIRoute } from "astro";
import { site, SITE_URL } from "../../../lib/api";
import { SIGNS } from "../../../lib/signs";

interface Entry {
  sign: string; period: string; covers: string;
  publishedAt: string | null; opening: string;
}

const escape = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
   .replace(/"/g, "&quot;");

export const GET: APIRoute = async ({ params }) => {
  const sign = String(params.sign ?? "");
  if (!SIGNS.includes(sign)) return new Response("no such sign\n", { status: 404 });

  const name = sign.charAt(0).toUpperCase() + sign.slice(1);
  /* /published, not /archive: the archive groups by period and carries no
     timestamp, so it can answer neither "one entry per reading" nor
     <pubDate>. It is already sorted newest-published-first. */
  const rows = (await site<Entry[]>(
    `/api/horoscopes/published?sign=${sign}&limit=50`)) ?? [];

  const self = `${SITE_URL}/horoscopes/${sign}/feed.xml`;
  const items = rows.map((r) => {
    const url = `${SITE_URL}/horoscopes/${sign}/${r.period}/${r.covers}`;
    return `    <item>
      <title>${escape(`${name} — ${r.covers}`)}</title>
      <link>${escape(url)}</link>
      <guid isPermaLink="true">${escape(url)}</guid>
${r.publishedAt ? `      <pubDate>${new Date(r.publishedAt).toUTCString()}</pubDate>\n` : ""}      <description>${escape(r.opening || `The ${r.period} reading for ${name}, ${r.covers}.`)}</description>
    </item>`;
  }).join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${escape(`${name} — Shruti`)}</title>
    <link>${escape(`${SITE_URL}/horoscopes/${sign}`)}</link>
    <atom:link href="${escape(self)}" rel="self" type="application/rss+xml" />
    <description>${escape(`Readings for ${name}, written by hand and signed Soror Eu. A.`)}</description>
    <language>en</language>
${items}
  </channel>
</rss>
`;
  return new Response(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "public, max-age=1800",
    },
  });
};
