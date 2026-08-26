/* The journal as a feed.
 *
 * Here because it is how somebody follows a person without an algorithm
 * deciding whether they see them — which is the same reason this site counts
 * its own visits and hosts its own fonts. A feed costs one route and asks
 * nothing of the reader.
 *
 * Built from the journal's own index, so an entry appears in the feed for
 * exactly as long as it appears on the site and no separate list can drift.
 */
import type { APIRoute } from "astro";

import { read } from "../../lib/journal/parse";
import { SITE_URL } from "../../lib/api";

export const prerender = false;

/* Twenty is the convention: enough that a new subscriber sees the shape of the
   thing, few enough that the feed stays small when the archive does not. */
const MOST_RECENT = 20;

const escape = (raw: string) =>
  raw
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

/* RFC 822, which is what RSS wants and what `toUTCString` already produces.
   An ISO date here is accepted by tolerant readers and silently dropped by
   strict ones, which is the worst of both. */
const rfc822 = (iso: string): string => {
  const d = new Date(iso.length === 10 ? `${iso}T00:00:00Z` : iso);
  return Number.isNaN(d.getTime()) ? "" : d.toUTCString();
};

export const GET: APIRoute = async () => {
  const hub = await read([]);
  const entries = (hub?.entries ?? []).slice(0, MOST_RECENT);

  const items = entries
    .map((e) => {
      const link = new URL(e.href, SITE_URL).href;
      const when = e.date ? rfc822(e.date) : "";
      return (
        "    <item>\n" +
        `      <title>${escape(e.title)}</title>\n` +
        `      <link>${escape(link)}</link>\n` +
        /* The link is the identity. A guid that changed when a title was
           edited would show every reader the same entry twice. */
        `      <guid isPermaLink="true">${escape(link)}</guid>\n` +
        (when ? `      <pubDate>${when}</pubDate>\n` : "") +
        (e.dek ? `      <description>${escape(e.dek)}</description>\n` : "") +
        "    </item>"
      );
    })
    .join("\n");

  const xml =
    `<?xml version="1.0" encoding="UTF-8"?>\n` +
    `<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n` +
    `  <channel>\n` +
    `    <title>Shruti — the journal</title>\n` +
    `    <link>${SITE_URL}/journal/</link>\n` +
    `    <description>Notes on practice, and on the software written as practice.</description>\n` +
    `    <language>en</language>\n` +
    `    <atom:link href="${SITE_URL}/journal/rss.xml" rel="self" type="application/rss+xml"/>\n` +
    items +
    (items ? "\n" : "") +
    `  </channel>\n</rss>\n`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      /* Short, because the journal is synced from BeeRanked on a timer and a
         long cache would hold a new entry back for no reason. */
      "Cache-Control": "public, max-age=900",
    },
  });
};
