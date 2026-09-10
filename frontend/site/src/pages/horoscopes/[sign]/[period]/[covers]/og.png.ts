// SPDX-License-Identifier: AGPL-3.0-only
/* The picture a shared reading shows.
 *
 * Discord, Bluesky and the rest fetch a page, read <meta property="og:image">
 * and display whatever it names. They accept a RASTER — png or jpeg — and they
 * do not render SVG and do not run scripts. The wheel everywhere else on this
 * site is SVG drawn by the browser, so for this one surface the server has to
 * do the drawing itself.
 *
 * ⚠ The drawing itself now lives in `lib/skycard.ts`, because the practice
 * room needs the same wheel for its Discord announcements. It was extracted
 * rather than copied: the wheel geometry has been copied around this codebase
 * before and came out backwards in half the copies.
 */
import type { APIRoute } from "astro";
import { askAstro } from "../../../../../lib/api";
import { ZODIAC } from "../../../../../lib/signs";
import { SIGN_GLYPH, signIndex } from "../../../../../lib/wheel";
import {
  ACCENT, H, INK, INK_FAINT, INK_SOFT, LINE, PAGE, SHAPE, W,
  esc, instantFor, periodLabel, rasterise, wheelSvg,
  type Placed,
} from "../../../../../lib/skycard";

export const GET: APIRoute = async ({ params }) => {
  const slug = String(params.sign ?? "");
  const period = String(params.period ?? "");
  const covers = String(params.covers ?? "");

  const name = slug.charAt(0).toUpperCase() + slug.slice(1);
  if (!ZODIAC.includes(name as any)) return new Response("no such sign\n", { status: 404 });
  if (!SHAPE[period]?.test(covers)) return new Response("no such period\n", { status: 404 });

  const at = instantFor(period, covers);
  const chart = await askAstro<{ bodies: Placed[] }>(
    `/chart?when=${encodeURIComponent(at)}&lat=51.4779&lon=0` +
    `&tradition=hellenistic&house_system=whole_sign&diagram=false`, 15000);
  const bodies = chart?.data?.bodies ?? [];

  const wheel = wheelSvg(bodies, name, 60, 75, 480);
  const glyph = SIGN_GLYPH[signIndex(name)];
  const label = periodLabel(period, covers);
  const kind = period === "daily" ? "Daily reading"
    : period === "weekly" ? "Weekly reading"
    : period === "monthly" ? "Monthly reading" : "Reading for the year";

  const x = 620;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${PAGE}"/>
  <rect x="0" y="0" width="6" height="${H}" fill="${ACCENT}"/>
  ${wheel}
  <text x="${x}" y="150" font-family="AstroSymbols" font-size="86" fill="${ACCENT}">${glyph}</text>
  <text x="${x}" y="266" font-family="EB Garamond" font-size="96" fill="${INK}">${esc(name)}</text>
  <text x="${x}" y="322" font-family="Commissioner" font-size="30" fill="${INK_SOFT}">${esc(label)}</text>
  <line x1="${x}" y1="368" x2="${W - 60}" y2="368" stroke="${LINE}" stroke-width="1"/>
  <text x="${x}" y="412" font-family="Commissioner" font-size="24" fill="${INK_FAINT}">${esc(kind)}</text>
  <text x="${x}" y="452" font-family="Commissioner" font-size="24" fill="${INK_FAINT}">Written by hand.</text>
  <text x="${x}" y="540" font-family="EB Garamond" font-size="34" fill="${INK}">Shruti</text>
  <text x="${x}" y="574" font-family="Commissioner" font-size="21" fill="${INK_FAINT}">shrutivtuber.com &#183; Soror Eu. A.</text>
</svg>`;

  const png = await rasterise(svg);

  return new Response(png, {
    headers: {
      "Content-Type": "image/png",
      /* A dated reading's sky never changes, so this is safe to keep. */
      "Cache-Control": "public, max-age=86400, s-maxage=604800, immutable",
    },
  });
};
