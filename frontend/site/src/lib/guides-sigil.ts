// SPDX-License-Identifier: AGPL-3.0-only
/**
 * The sigil, as the Guides handoff of 20 September 2026 draws it on the site:
 * one arc per part on one circle, and — at 44px and above, and as the 28px
 * lockup mark — the compass ring from the app icon, north lit in gold.
 *
 * A pure function returning markup, so the same drawing serves a server-
 * rendered page, a client script that redraws a sigil live (the tiers
 * stepper), and a plate that depicts the stream. Overlays keep their own
 * drawing in overlay-elements.ts; the theme decides their ring.
 *
 * The arithmetic is the board's, verbatim:
 *   span = 360/n · gap = clamp(2°, 24°/n, 8°) · stroke = 6 (9 below 48px)
 *   radius = 50 − stroke/2 − 1, minus 7 more when the ring is on
 *   arc i from i·span+gap/2 to (i+1)·span−gap/2, starting at −90°
 *   track --guide-track · done --state-done · current or partly --state-now
 *   count in mono at ≥ 60px · filled arcs draw once on first paint
 */

export interface SigilOptions {
  /** Number of parts: phases, categories, tiers. */
  n: number;
  /** Count of leading parts that are done (ignored when `states` is given). */
  done?: number;
  /** Index of the current part; -1 for none. Defaults to the first not-done part. */
  now?: number | null;
  /** One character per part: d done · n now or partly · o open · l locked. */
  states?: string;
  size?: number;
  ring?: boolean;
  showCount?: boolean;
  label?: string;
  /** Fill the parent box (used inside a plate) instead of a fixed size. */
  fill?: boolean;
  /** The accessible name; pass a say() string. */
  aria?: string;
  /** Draw the filled arcs on first paint (the one load-time motion). */
  animate?: boolean;
}

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

export function sigil(o: SigilOptions): string {
  const n = Math.max(1, Math.floor(o.n || 1));
  const size = o.size ?? 104;
  const ring = !!o.ring;
  const done = Math.max(0, Math.min(n, o.done ?? 0));
  const now = o.now === undefined || o.now === null ? (done < n ? done : -1) : o.now;
  const states = o.states && o.states.trim() ? o.states.replace(/\s+/g, "").split("") : null;
  const span = 360 / n;
  const gap = Math.min(8, Math.max(2, 24 / n));
  const stroke = size < 48 ? 9 : 6;
  const r = 50 - stroke / 2 - 1 - (ring ? 7 : 0);
  const pt = (deg: number) => {
    const a = ((deg - 90) * Math.PI) / 180;
    return [50 + r * Math.cos(a), 50 + r * Math.sin(a)];
  };
  const arc = (a0: number, a1: number) => {
    const [x0, y0] = pt(a0), [x1, y1] = pt(a1);
    return `M ${x0.toFixed(3)} ${y0.toFixed(3)} A ${r} ${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${x1.toFixed(3)} ${y1.toFixed(3)}`;
  };
  let tracks = "", fills = "", doneCount = 0;
  for (let i = 0; i < n; i++) {
    const a0 = i * span + gap / 2, a1 = (i + 1) * span - gap / 2;
    const d = arc(a0, a1);
    const len = ((r * (a1 - a0) * Math.PI) / 180).toFixed(3);
    tracks += `<path d="${d}" fill="none" stroke="var(--guide-track)" stroke-width="${stroke}" stroke-linecap="butt"/>`;
    const st = states ? states[i] ?? "o" : i < done ? "d" : i === now ? "n" : "o";
    if (st === "d") doneCount++;
    const colour = st === "d" ? "var(--state-done)" : st === "n" ? "var(--state-now)" : null;
    if (!colour) continue;
    const draw = o.animate === false ? "" : " gd-arc-draw";
    fills += `<path class="gd-arc${draw}" d="${d}" fill="none" stroke="${colour}" stroke-width="${stroke}" stroke-linecap="butt" stroke-dasharray="${len}" style="--gd-len:${len}"/>`;
  }
  const marks = ring
    ? `<circle cx="50" cy="50" r="47.5" fill="none" stroke="var(--guide-ring)" stroke-width="1" vector-effect="non-scaling-stroke"/>` +
      `<rect x="47.5" y="0" width="5" height="5" transform="rotate(45 50 2.5)" fill="var(--guide-gold)"/>` +
      `<rect x="95" y="47.5" width="5" height="5" transform="rotate(45 97.5 50)" fill="var(--guide-ring)"/>` +
      `<rect x="47.5" y="95" width="5" height="5" transform="rotate(45 50 97.5)" fill="var(--guide-ring)"/>` +
      `<rect x="0" y="47.5" width="5" height="5" transform="rotate(45 2.5 50)" fill="var(--guide-ring)"/>`
    : "";
  const showCount = (o.showCount ?? true) && size >= 60;
  const label = o.label || `${doneCount} / ${n}`;
  const countPx = Math.round(size * (ring ? 0.13 : 0.16));
  const aria = esc(o.aria ?? `${doneCount} of ${n}`);
  const box = o.fill
    ? `display:block;position:absolute;inset:0;line-height:0`
    : `display:inline-block;position:relative;width:${size}px;height:${size}px;flex:none;line-height:0`;
  const dim = o.fill ? `width="100%" height="100%"` : `width="${size}" height="${size}"`;
  return (
    `<span class="gd-sigil" role="img" aria-label="${aria}" style="${box}">` +
    `<svg viewBox="0 0 100 100" ${dim} style="display:block;overflow:visible" aria-hidden="true">${marks}${tracks}${fills}</svg>` +
    (showCount
      ? `<span class="gd-sigil-count" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:var(--font-mono);font-variant-numeric:tabular-nums;font-size:${countPx}px;line-height:1;color:var(--ink)">${esc(label)}</span>`
      : "") +
    `</span>`
  );
}

/** A states string for a build: one character per category from its counts. */
export function buildStates(categories: { met: number; total: number; partly?: number; ratio?: number }[]): string {
  return categories
    .map((c) => (c.total > 0 && c.met >= c.total ? "d" : c.met > 0 || (c.partly ?? 0) > 0 || (c.ratio ?? 0) > 0 ? "n" : "o"))
    .join("");
}
