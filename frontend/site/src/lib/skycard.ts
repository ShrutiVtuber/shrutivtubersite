// SPDX-License-Identifier: AGPL-3.0-only
/* Drawing a sky as a PNG, for the surfaces that cannot run a browser.
 *
 * Discord, Bluesky, X and the rest fetch a URL and display whatever pixels come
 * back. They do not render SVG and do not run scripts, so the wheel that every
 * other surface draws in the browser has to be drawn by the server for these.
 *
 * ⚠ **This module exists because the drawing was about to be copied.** It was
 * written inside the horoscope share-card endpoint, and the practice room now
 * needs the same wheel for its Discord announcements — the same wheel, rotated
 * to a different rising sign. The file it came from carries a warning that the
 * eight lines of wheel geometry "were copied into four files and were backwards
 * in two of them", and copying a two-hundred-line drawing would have been that
 * mistake at twenty-five times the size.
 *
 * `resvg` is the rasteriser: compiled Rust, the only native module in the
 * image, and the reason the Dockerfile is Alpine-specific about it — a glibc
 * build installs cleanly and then fails at startup on musl.
 */
import { readdirSync } from "node:fs";
import path from "node:path";

import {
  SIGN_GLYPH, BODY_GLYPH, signIndex, relativeTo, wheelPoint, f,
} from "./wheel";
export { fitLines } from "./fit";

export interface Placed { name: string; longitude: number; retrograde: boolean }

export const W = 1200;
export const H = 630;

/* The site's dusk palette, fixed. A share card is one image seen by everybody,
   so it does not follow a reader's theme — and dark is right for a night sky
   and stands out in a feed of white cards. */
export const PAGE = "#121829";
export const INSET = "#0D1220";
export const INK = "#E9E6F0";
export const INK_SOFT = "#B3B9D2";
export const INK_FAINT = "#8B93AF";
export const LINE = "#2E3752";
export const LINE_STRONG = "#485272";
export const ACCENT = "#8FBEE8";

export const SHAPE: Record<string, RegExp> = {
  daily: /^\d{4}-\d{2}-\d{2}$/,
  weekly: /^\d{4}-W\d{2}$/,
  monthly: /^\d{4}-\d{2}$/,
  yearly: /^\d{4}$/,
};

const MONTH = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"];

/** The middle of the period, as an instant — see oembed.json.ts, same rule. */
export function instantFor(period: string, covers: string): string {
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
export function periodLabel(period: string, covers: string): string {
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

export const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

/**
 * The wheel, drawn into a box of `size` at (ox, oy).
 *
 * Geometry comes from lib/wheel.ts rather than from another copy of the eight
 * lines — those eight lines were copied into four files and were backwards in
 * two of them.
 */
export function wheelSvg(bodies: Placed[], rising: string, ox: number, oy: number, size: number) {
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
export function fonts(): string[] {
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


/**
 * The finished SVG, as PNG bytes.
 *
 * ⚠ `fontFiles`, never `fontBuffers`. resvg accepts both and then quietly
 * ignores the second in this version: the render succeeds, returns a valid
 * PNG, and every piece of text is missing from it. No error, no warning — the
 * first card built that way was a wheel with no glyphs, no name and no byline,
 * and it read as a layout bug rather than a font one.
 */
export async function rasterise(svg: string, width = W): Promise<Uint8Array> {
  const { Resvg } = await import("@resvg/resvg-js");
  const png = new Resvg(svg, {
    fitTo: { mode: "width", value: width },
    font: {
      fontFiles: fonts(),
      defaultFontFamily: "Commissioner",
      loadSystemFonts: false,
    },
    background: PAGE,
  }).render().asPng();
  return new Uint8Array(png);
}
