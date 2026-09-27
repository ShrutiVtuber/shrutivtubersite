// SPDX-License-Identifier: AGPL-3.0-only
/* A lesson's Open Graph image, by the logo's template (design/logo/README.md):
 * 1200×630, the dawn sky with a horizon line; a veil of the page colour at
 * 78%, inset 56 px, radius 16; the descriptor lockup top-left at 52%; the
 * eyebrow in Commissioner 600, 22 px, rose, tracked, uppercase, with the unit
 * and lesson; the title in EB Garamond 500, 76 px, one line of up to about 28
 * characters, else two lines at 64 px. The lockup is the logo's own SVG,
 * placed as it is: never recoloured, never re-typeset. */
import type { APIRoute } from "astro";
import lockup from "../../../../assets/carnatic-brand/swara-studio-descriptor-dawn.svg?raw";
import { lesson } from "../../../../lib/carnatic/course";
import { esc, rasterise } from "../../../../lib/skycard";

const W = 1200, H = 630;
const INK = "#26304A", ROSE = "#A85A76", PAGE = "#F8F6F3";

/** The lockup's drawing (its metadata dropped), scaled and placed. */
function placedLockup(x: number, y: number, scale: number): string {
  const inner = lockup.replace(/<metadata>[\s\S]*?<\/metadata>/, "").replace(/^[\s\S]*?<svg[^>]*>/, "").replace(/<\/svg>\s*$/, "");
  return `<g transform="translate(${x} ${y}) scale(${scale})">${inner}</g>`;
}

function titleLines(t: string): { lines: string[]; size: number } {
  if (t.length <= 28) return { lines: [t], size: 76 };
  const words = t.split(/\s+/);
  let a = "";
  while (words.length && (a + " " + words[0]).trim().length <= Math.ceil(t.length / 2) + 4) a = (a + " " + words.shift()).trim();
  return { lines: [a, words.join(" ")].filter(Boolean), size: 64 };
}

export const GET: APIRoute = async ({ params }) => {
  const l = await lesson(String(params.slug ?? ""));
  if (!l) return new Response("no such lesson\n", { status: 404 });
  const { lines, size } = titleLines(l.title);
  const eyebrow = `Unit ${l.unit} · Lesson ${l.order}`.toUpperCase();
  const top = 400 - (lines.length - 1) * (size + 6);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#A9CBEA"/><stop offset="0.55" stop-color="#D9D3EA"/><stop offset="1" stop-color="#F2D9DC"/></linearGradient></defs>
  <rect width="${W}" height="${H}" fill="url(#sky)"/>
  <line x1="0" y1="${H - 36}" x2="${W}" y2="${H - 36}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>
  <rect x="56" y="56" width="${W - 112}" height="${H - 112}" rx="16" fill="${PAGE}" fill-opacity="0.78"/>
  ${placedLockup(96, 92, 0.52)}
  <text x="100" y="${top - 30}" font-family="Commissioner" font-weight="600" font-size="22" letter-spacing="3" fill="${ROSE}">${esc(eyebrow)}</text>
  ${lines.map((t, i) => `<text x="96" y="${top + 40 + i * (size + 6)}" font-family="EB Garamond" font-weight="500" font-size="${size}" fill="${INK}">${esc(t)}</text>`).join("\n  ")}
</svg>`;
  return new Response(await rasterise(svg, W), { headers: { "content-type": "image/png", "cache-control": "public, max-age=3600" } });
};
