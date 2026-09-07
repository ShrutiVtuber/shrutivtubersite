// SPDX-License-Identifier: AGPL-3.0-only
/* The picture a shared reading shows.
 *
 * Discord, Bluesky and the rest fetch a page, read <meta property="og:image">
 * and display whatever it names. They accept a RASTER — png or jpeg — and they
 * do not render SVG and do not run scripts. The wheel everywhere else on this
 * site is SVG drawn by the browser, so for this one surface the server has to
 * do the drawing itself.
 *
 * `resvg` is a rasteriser: it turns the vector instructions into actual
 * pixels, fonts and all. It is compiled Rust rather than JavaScript, which is
 * why it is the only native module in this image and why the Dockerfile is
 * Alpine-specific about it — a glibc build would install cleanly and then fail
 * at startup on musl.
 *
 * Fonts are the part with a trap in it. The site serves woff2, which is a
 * web-transport format the rasteriser cannot read, and the subsets it serves
 * are Latin only — no zodiac, no planets. So three files are shipped
 * decompressed alongside this: her two faces for the words, and a 5KB subset
 * of DejaVu Sans holding the seventeen astrological glyphs and nothing else.
 * Without that last one every glyph on the card renders as a hollow box.
 */
import type { APIRoute } from "astro";
import { readdirSync } from "node:fs";
import path from "node:path";
import { askAstro } from "../../../../../lib/api";
import { ZODIAC } from "../../../../../lib/signs";
import {
  SIGN_GLYPH, BODY_GLYPH, signIndex, relativeTo, wheelPoint, f,
} from "../../../../../lib/wheel";

const W = 1200;
const H = 630;

/* The site's dusk palette, fixed. A share card is one image seen by everybody,
   so it does not follow a reader's theme — and dark is right for a night sky
   and stands out in a feed of white cards. */
const PAGE = "#121829";
const INSET = "#0D1220";
const INK = "#E9E6F0";
const INK_SOFT = "#B3B9D2";
const INK_FAINT = "#8B93AF";
const LINE = "#2E3752";
const LINE_STRONG = "#485272";
const ACCENT = "#8FBEE8";

const SHAPE: Record<string, RegExp> = {
  daily: /^\d{4}-\d{2}-\d{2}$/,
  weekly: /^\d{4}-W\d{2}$/,
  monthly: /^\d{4}-\d{2}$/,
  yearly: /^\d{4}$/,
};

const MONTH = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"];

/** The middle of the period, as an instant — see oembed.json.ts, same rule. */
function instantFor(period: string, covers: string): string {
  const noon = (y: number, m: number, d: number) =>
    new Date(Date.UTC(y, m - 1, d, 12)).toISOString().slice(0, 19) + "Z";
  if (period === "daily") {
    const [y, m, d] = covers.split("-").map(Number);
    return noon(y, m, d);
  }
  if (period === "monthly") {
    const [y, m] = covers.split("-").map(Number);
    return noon(y, m, 15);
  }
  if (period === "yearly") return noon(Number(covers), 7, 2);
  const [ys, ws] = covers.split("-W");
  const jan4 = new Date(Date.UTC(Number(ys), 0, 4, 12));
  const dow = (jan4.getUTCDay() + 6) % 7;
  const monday = new Date(jan4.getTime() - dow * 864e5 + (Number(ws) - 1) * 7 * 864e5);
  return new Date(monday.getTime() + 3 * 864e5).toISOString().slice(0, 19) + "Z";
}

/** "September 2026", "Week of 14 September 2026" — what a person would say. */
function periodLabel(period: string, covers: string): string {
  if (period === "yearly") return covers;
  if (period === "monthly") {
    const [y, m] = covers.split("-").map(Number);
    return `${MONTH[m - 1]} ${y}`;
  }
  if (period === "daily") {
    const [y, m, d] = covers.split("-").map(Number);
    return `${d} ${MONTH[m - 1]} ${y}`;
  }
  const at = new Date(instantFor("weekly", covers));
  const monday = new Date(at.getTime() - 3 * 864e5);
  return `Week of ${monday.getUTCDate()} ${MONTH[monday.getUTCMonth()]} ${monday.getUTCFullYear()}`;
}

const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

interface Placed { name: string; longitude: number; retrograde: boolean }

/**
 * The wheel, drawn into a box of `size` at (ox, oy).
 *
 * Geometry comes from lib/wheel.ts rather than from another copy of the eight
 * lines — those eight lines were copied into four files and were backwards in
 * two of them.
 */
function wheelSvg(bodies: Placed[], rising: string, ox: number, oy: number, size: number) {
  const R = size / 2;
  const cx = ox + R;
  const cy = oy + R;
  const rIdx = rising ? signIndex(rising) : null;
  const at = (deg: number, rad: number) => wheelPoint(deg, rad, cx, cy);

  const out: string[] = [];

  out.push(`<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(R)}" fill="${INSET}" stroke="${LINE}" stroke-width="1.5"/>`);
  out.push(`<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(R * 0.78)}" fill="none" stroke="${LINE}" stroke-width="1"/>`);
  out.push(`<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(R * 0.30)}" fill="none" stroke="${LINE}" stroke-width="1"/>`);

  /* Twelve spokes and twelve sign glyphs, rotated so the reading's own sign
     begins the wheel. */
  for (let i = 0; i < 12; i++) {
    const deg = i * 30;
    const [x1, y1] = at(deg, R * 0.30);
    const [x2, y2] = at(deg, R);
    out.push(`<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke="${LINE}" stroke-width="1"/>`);

    const zodiac = ((rIdx ?? 0) + i) % 12;
    const [gx, gy] = at(deg + 15, R * 0.89);
    const own = i === 0 && rising !== "";
    out.push(
      `<text x="${f(gx)}" y="${f(gy)}" font-family="AstroSymbols" font-size="${f(R * 0.15)}" ` +
      `fill="${own ? ACCENT : INK_FAINT}" text-anchor="middle" dominant-baseline="central">` +
      `${SIGN_GLYPH[zodiac]}</text>`);
  }

  /* Degree ticks, every 5°, longer every 30°. */
  for (let i = 0; i < 72; i++) {
    const deg = i * 5;
    const long = i % 6 === 0;
    const [x1, y1] = at(deg, R * 0.78);
    const [x2, y2] = at(deg, R * 0.78 - (long ? R * 0.05 : R * 0.025));
    out.push(`<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke="${LINE_STRONG}" stroke-width="${long ? 1.2 : 0.7}"/>`);
  }

  /* Bodies, spread so two a degree apart do not print on top of each other.
     Same deterministic relaxation as the interactive wheel: sort by angle,
     push apart until every neighbour clears the minimum, and draw a leader
     back to the true position so the spreading never lies about where a
     planet is. */
  const MIN_GAP = 13;
  const placed = bodies
    .map((b) => ({ ...b, true_: relativeTo(b.longitude, rIdx) }))
    .sort((a, b) => a.true_ - b.true_);
  const shown = placed.map((p) => p.true_);
  for (let pass = 0; pass < 60; pass++) {
    let moved = false;
    for (let i = 0; i < shown.length; i++) {
      const j = (i + 1) % shown.length;
      let gap = shown[j] - shown[i];
      if (j === 0) gap += 360;
      if (gap < MIN_GAP) {
        const push = (MIN_GAP - gap) / 2;
        shown[i] = (shown[i] - push + 360) % 360;
        shown[j] = (shown[j] + push) % 360;
        moved = true;
      }
    }
    if (!moved) break;
  }

  placed.forEach((b, i) => {
    const [tx, ty] = at(b.true_, R * 0.78);
    const [lx, ly] = at(shown[i], R * 0.64);
    out.push(`<line x1="${f(tx)}" y1="${f(ty)}" x2="${f(lx)}" y2="${f(ly)}" stroke="${LINE_STRONG}" stroke-width="0.8"/>`);
    out.push(`<circle cx="${f(tx)}" cy="${f(ty)}" r="1.8" fill="${ACCENT}"/>`);
    const glyph = BODY_GLYPH[b.name] ?? b.name.slice(0, 2);
    out.push(
      `<text x="${f(lx)}" y="${f(ly)}" font-family="AstroSymbols" font-size="${f(R * 0.135)}" ` +
      `fill="${INK}" text-anchor="middle" dominant-baseline="central">${glyph}</text>`);
    if (b.retrograde) {
      out.push(
        `<text x="${f(lx + R * 0.085)}" y="${f(ly + R * 0.075)}" font-family="AstroSymbols" ` +
        `font-size="${f(R * 0.07)}" fill="${INK_FAINT}" text-anchor="middle" ` +
        `dominant-baseline="central">℞</text>`);
    }
  });

  return out.join("");
}

/* Paths, not buffers, and found once per process.
 *
 * resvg takes either, but `fontBuffers` is accepted and then quietly ignored
 * in this version: the render succeeds, returns a valid PNG, and every single
 * piece of text is missing from it. There is no error and no warning — the
 * first card built that way was a wheel with no glyphs, no sign name and no
 * byline, and it looked like a layout bug rather than a font one.
 */
let FONTS: string[] | null = null;
function fonts(): string[] {
  if (FONTS) return FONTS;
  const dirs = [
    path.resolve(process.cwd(), "fonts-render"),
    path.resolve(process.cwd(), "frontend/site/fonts-render"),
  ];
  for (const dir of dirs) {
    try {
      const files = readdirSync(dir).filter((n) => n.endsWith(".ttf"));
      if (files.length) {
        FONTS = files.map((n) => path.join(dir, n));
        return FONTS;
      }
    } catch { /* try the next */ }
  }
  FONTS = [];
  return FONTS;
}

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

  const { Resvg } = await import("@resvg/resvg-js");
  const png = new Resvg(svg, {
    fitTo: { mode: "width", value: W },
    font: {
      fontFiles: fonts(),
      defaultFontFamily: "Commissioner",
      loadSystemFonts: false,
    },
    background: PAGE,
  }).render().asPng();

  return new Response(new Uint8Array(png), {
    headers: {
      "Content-Type": "image/png",
      /* A dated reading's sky never changes, so this is safe to keep. */
      "Cache-Control": "public, max-age=86400, s-maxage=604800, immutable",
    },
  });
};
