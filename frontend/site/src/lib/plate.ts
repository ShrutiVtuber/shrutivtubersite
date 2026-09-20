// SPDX-License-Identifier: AGPL-3.0-only
/**
 * A plate: a miniature of the 1920 × 1080 stream canvas in its theme — the
 * only place a stream theme appears on the site. Used for the gallery
 * thumbnail (520), the editor preview (360), the theme tiles (160/120) and
 * the swatch on token rows (72/64/56).
 *
 * The theme table holds the stream's own values. They describe the stream,
 * not the site, which is why they are here and in no page; the plate is
 * stamped data-theme="dark" so the state tokens resolve to the stream values.
 */
import { sigil } from "./guides-sigil";

export interface PlateElement {
  kind: string;
  x: number;
  y: number;
  w: number;
  /** Height on the canvas; the kind's usual height when absent. */
  h?: number;
  n?: number;
  done?: number;
}

export interface PlateOptions {
  theme: string;
  elements: PlateElement[];
  width: number;
  /** Fill the parent's width, up to `width`. */
  fluid?: boolean;
  /** Human labels per kind (say() strings); the kind itself when absent. */
  labels?: Record<string, string>;
  /** The accessible name; pass a say() string. */
  aria: string;
}

interface Theme {
  ground: string; panel: string; inkSoft: string; rule: string; bottom: string; radius: number; ring: boolean;
}

export const THEMES: Record<string, Theme> = {
  grimoire: { ground: "#14100E", panel: "rgba(36,27,22,.92)", inkSoft: "#C4B4A2", rule: "4px solid #C9A227", bottom: "none", radius: 2, ring: true },
  almanac: { ground: "#121829", panel: "rgba(26,33,56,.92)", inkSoft: "#B3B9D2", rule: "none", bottom: "1px solid #8A6880", radius: 16, ring: false },
  plain: { ground: "#000000", panel: "rgba(21,22,26,.88)", inkSoft: "#C8CCD4", rule: "none", bottom: "none", radius: 0, ring: false },
};

/** The usual height of each element kind on the canvas, as the site's overlays draw them. */
export const HEIGHTS: Record<string, number> = {
  "guide-sigil": 224, "guide-path": 96, "guide-now": 200, "guide-routine": 260, "guide-goal": 260, "guide-layout": 1080,
  counter: 140, text: 80, image: 160, ticker: 64, sky: 300, hours: 150, countdown: 130, alerts: 120, wheel: 432, build: 420,
};

/** The board's presets, for tiles that depict no particular layout. */
export const PRESETS: Record<string, PlateElement[]> = {
  now: [{ kind: "guide-now", x: 96, y: 760, w: 720, h: 240 }, { kind: "guide-routine", x: 96, y: 80, w: 420, h: 220 }, { kind: "guide-sigil", x: 1624, y: 80, w: 200, h: 200 }],
  sigil: [{ kind: "guide-sigil", x: 1624, y: 80, w: 200, h: 200 }],
  path: [{ kind: "guide-path", x: 1400, y: 120, w: 424, h: 840 }, { kind: "guide-sigil", x: 96, y: 80, w: 200, h: 200 }],
  grid: [{ kind: "build", x: 96, y: 560, w: 640, h: 440 }, { kind: "guide-sigil", x: 1624, y: 80, w: 200, h: 200 }],
  goal: [{ kind: "guide-sigil", x: 860, y: 300, w: 200, h: 200 }, { kind: "guide-goal", x: 560, y: 560, w: 800, h: 120 }],
  sky: [{ kind: "sky", x: 0, y: 0, w: 1920, h: 220 }, { kind: "guide-now", x: 96, y: 760, w: 720, h: 240 }, { kind: "guide-sigil", x: 1624, y: 80, w: 200, h: 200 }],
};

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
const pc = (v: number, of: number) => `${((v / of) * 100).toFixed(2)}%`;
const isSigil = (k: string) => k === "guide-sigil" || k === "Sigil";
const isSky = (k: string) => k === "sky" || k === "Sky";

export function plate(o: PlateOptions): string {
  const T = THEMES[o.theme] ?? THEMES.almanac;
  const width = o.width;
  let inner = "";
  for (const e of o.elements) {
    const h = e.h ?? HEIGHTS[e.kind] ?? 220;
    if (isSigil(e.kind)) {
      const size = Math.round((e.w / 1920) * width);
      inner +=
        `<div style="position:absolute;left:${pc(e.x, 1920)};top:${pc(e.y, 1080)};width:${pc(e.w, 1920)};aspect-ratio:1/1;line-height:0">` +
        sigil({ n: e.n ?? 9, done: e.done ?? 3, size, ring: T.ring, fill: true, showCount: false, animate: false, aria: "" }) +
        `</div>`;
      continue;
    }
    const sky = isSky(e.kind);
    const bg = sky ? "linear-gradient(180deg,var(--dusk-sky-zenith) 0%,var(--dusk-sky-mid) 58%,var(--dusk-sky-horizon) 100%)" : T.panel;
    const left = sky ? "none" : T.rule;
    const bottom = sky ? "1px solid var(--dusk-horizon-line)" : T.bottom;
    const radius = sky ? "0" : width < 160 ? "2px" : `${(T.radius * (width / 1920) * 4).toFixed(2)}px`;
    const label = width >= 200 && !sky ? `<span style="font-family:var(--font-mono);font-size:10px;line-height:1;color:${T.inkSoft};white-space:nowrap">${esc(o.labels?.[e.kind] ?? e.kind)}</span>` : "";
    inner +=
      `<div style="position:absolute;left:${pc(e.x, 1920)};top:${pc(e.y, 1080)};width:${pc(e.w, 1920)};height:${pc(h, 1080)};background:${bg};border-left:${left};border-bottom:${bottom};border-radius:${radius};box-sizing:border-box;display:flex;align-items:flex-end;padding:${width >= 200 ? "6px" : "0"};overflow:hidden">${label}</div>`;
  }
  const w = o.fluid ? "100%" : `${width}px`;
  const max = o.fluid ? `${width}px` : "100%";
  return `<div class="gd-plate" data-theme="dark" role="img" aria-label="${esc(o.aria)}" style="position:relative;aspect-ratio:16/9;width:${w};max-width:${max};background:${T.ground};border:1px solid var(--line);border-radius:4px;overflow:hidden;flex:none">${inner}</div>`;
}
