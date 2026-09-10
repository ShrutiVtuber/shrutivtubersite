// SPDX-License-Identifier: AGPL-3.0-only
/* The sky a set of practice readings was written from.
 *
 * Shown on the Discord announcement, where it is the only picture of what the
 * week actually looked like. Nothing about the writer is on it: this is the
 * sky, which belonged to everybody that week.
 *
 * ⚠ **Discord fetches this itself, from the public internet.** It will not see
 * a localhost address, so this renders correctly in a local test only when
 * opened by hand — the embed will show a broken image until the site is
 * deployed. That is worth knowing before it reads as a bug.
 */
import type { APIRoute } from "astro";
import { askAstro, site } from "../../../lib/api";
import {
  ACCENT, H, INK, INK_FAINT, INK_SOFT, LINE, PAGE, W,
  esc, fitLines, instantFor, periodLabel, rasterise, wheelSvg,
  type Placed,
} from "../../../lib/skycard";

interface Work {
  id: number; author: string; period: string; covers: string;
  title: string; signs: string[];
}

export const GET: APIRoute = async ({ params }) => {
  const id = String(params.id ?? "");
  /* ⚠ Numeric or nothing — this goes straight into an API path. */
  if (!/^\d+$/.test(id)) return new Response("no\n", { status: 404 });

  const work = await site<Work>(`/api/practice/${id}`);
  if (!work) return new Response("no such work\n", { status: 404 });

  const at = instantFor(work.period, work.covers);
  const chart = await askAstro<{ bodies: Placed[] }>(
    `/chart?when=${encodeURIComponent(at)}&lat=51.4779&lon=0` +
    `&tradition=hellenistic&house_system=whole_sign&diagram=false`, 15000);

  /* ⚠ No rising sign. A set covering twelve signs has no single one to turn
     the wheel to, so this is the plain zodiacal sky with Aries at the start —
     the same wheel every reader of every sign was looking at. The per-sign
     cards next door are the ones that rotate. */
  const wheel = wheelSvg(chart?.data?.bodies ?? [], "", 60, 75, 480);

  const count = work.signs?.length ?? 0;
  const what = count > 1 ? `${count} signs` : (work.signs?.[0] ?? "a reading");
  const x = 620;

  /* ⚠ The title is the WRITER's, not one of twelve known sign names, so it has
     to be measured. Left unfitted it runs straight off the right edge and the
     PNG is simply cropped — no error, no warning, half a word. */
  const head = fitLines(work.title || what, W - x - 60);
  const title = head.lines
    .map((line, i) =>
      `<text x="${x}" y="${248 + i * (head.size + 8)}" font-family="EB Garamond" ` +
      `font-size="${head.size}" fill="${INK}">${esc(line)}</text>`)
    .join("\n  ");
  /* Everything below the title moves down when it took two lines. */
  const below = 248 + (head.lines.length - 1) * (head.size + 8);
  /* ⚠ And so does the byline, or a two-line title prints straight through it.
     Pinned to the usual place when there is room and pushed down when there is
     not — never above `below`, which is what produced "The sky it was written
     from." overlapping "The practice room". */
  const foot = Math.max(540, below + 226);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${PAGE}"/>
  <rect x="0" y="0" width="6" height="${H}" fill="${ACCENT}"/>
  ${wheel}
  <text x="${x}" y="150" font-family="Commissioner" font-size="24" fill="${ACCENT}">PRACTICE</text>
  ${title}
  <text x="${x}" y="${below + 56}" font-family="Commissioner" font-size="30" fill="${INK_SOFT}">${esc(periodLabel(work.period, work.covers))}</text>
  <line x1="${x}" y1="${below + 102}" x2="${W - 60}" y2="${below + 102}" stroke="${LINE}" stroke-width="1"/>
  <text x="${x}" y="${below + 146}" font-family="Commissioner" font-size="24" fill="${INK_FAINT}">${esc(work.author || "somebody")} &#183; ${esc(what)}</text>
  <text x="${x}" y="${below + 186}" font-family="Commissioner" font-size="24" fill="${INK_FAINT}">The sky it was written from.</text>
  <text x="${x}" y="${foot}" font-family="EB Garamond" font-size="34" fill="${INK}">The practice room</text>
  <text x="${x}" y="${foot + 34}" font-family="Commissioner" font-size="21" fill="${INK_FAINT}">shrutivtuber.com</text>
</svg>`;

  return new Response(await rasterise(svg), {
    headers: {
      "Content-Type": "image/png",
      /* The sky of a past period does not change. */
      "Cache-Control": "public, max-age=3600, s-maxage=604800",
    },
  });
};
