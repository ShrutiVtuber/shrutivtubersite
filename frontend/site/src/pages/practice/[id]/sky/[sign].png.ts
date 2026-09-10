// SPDX-License-Identifier: AGPL-3.0-only
/* The sky for ONE sign's reading, turned to that sign.
 *
 * ⚠ **This is not decoration, and it is not the same picture twelve times.** A
 * horoscope for Taurus is written with Taurus rising: the whole-sign houses
 * start there, so the planet in the tenth for a Taurus reading is a different
 * planet from the one in the tenth for Aries. The wheel is rotated to match,
 * which makes it the chart the reading was actually written from rather than a
 * generic sky pasted beside it.
 *
 * Shown on each reading's own message inside the Discord thread.
 *
 * ⚠ Discord fetches this from the public internet and cannot see localhost —
 * see the note in ../sky.png.ts.
 */
import type { APIRoute } from "astro";
import { askAstro, site } from "../../../../lib/api";
import { ZODIAC } from "../../../../lib/signs";
import { SIGN_GLYPH, signIndex } from "../../../../lib/wheel";
import {
  ACCENT, H, INK, INK_FAINT, INK_SOFT, LINE, PAGE, W,
  esc, instantFor, periodLabel, rasterise, wheelSvg,
  type Placed,
} from "../../../../lib/skycard";

interface Work {
  id: number; author: string; period: string; covers: string;
  title: string; signs: string[];
}

export const GET: APIRoute = async ({ params }) => {
  const id = String(params.id ?? "");
  const slug = String(params.sign ?? "").toLowerCase();
  if (!/^\d+$/.test(id)) return new Response("no\n", { status: 404 });

  const name = slug.charAt(0).toUpperCase() + slug.slice(1);
  if (!ZODIAC.includes(name as any)) {
    return new Response("no such sign\n", { status: 404 });
  }

  const work = await site<Work>(`/api/practice/${id}`);
  if (!work) return new Response("no such work\n", { status: 404 });
  /* ⚠ Only a sign the work actually contains. Otherwise every submission has
     twelve valid card addresses whatever was written, and a thread could show
     a chart for a reading nobody wrote. */
  if (!(work.signs ?? []).some((s) => s.toLowerCase() === slug)) {
    return new Response("not in this work\n", { status: 404 });
  }

  const at = instantFor(work.period, work.covers);
  const chart = await askAstro<{ bodies: Placed[] }>(
    `/chart?when=${encodeURIComponent(at)}&lat=51.4779&lon=0` +
    `&tradition=hellenistic&house_system=whole_sign&diagram=false`, 15000);

  const wheel = wheelSvg(chart?.data?.bodies ?? [], name, 60, 75, 480);
  const glyph = SIGN_GLYPH[signIndex(name)];

  const x = 620;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${PAGE}"/>
  <rect x="0" y="0" width="6" height="${H}" fill="${ACCENT}"/>
  ${wheel}
  <text x="${x}" y="150" font-family="AstroSymbols" font-size="86" fill="${ACCENT}">${glyph}</text>
  <text x="${x}" y="266" font-family="EB Garamond" font-size="96" fill="${INK}">${esc(name)}</text>
  <text x="${x}" y="322" font-family="Commissioner" font-size="30" fill="${INK_SOFT}">${esc(periodLabel(work.period, work.covers))}</text>
  <line x1="${x}" y1="368" x2="${W - 60}" y2="368" stroke="${LINE}" stroke-width="1"/>
  <text x="${x}" y="412" font-family="Commissioner" font-size="24" fill="${INK_FAINT}">Houses from ${esc(name)}, whole sign.</text>
  <text x="${x}" y="452" font-family="Commissioner" font-size="24" fill="${INK_FAINT}">Practice &#183; ${esc(work.author || "somebody")}</text>
  <text x="${x}" y="540" font-family="EB Garamond" font-size="34" fill="${INK}">The practice room</text>
  <text x="${x}" y="574" font-family="Commissioner" font-size="21" fill="${INK_FAINT}">shrutivtuber.com</text>
</svg>`;

  return new Response(await rasterise(svg), {
    headers: {
      "Content-Type": "image/png",
      "Cache-Control": "public, max-age=3600, s-maxage=604800",
    },
  });
};
