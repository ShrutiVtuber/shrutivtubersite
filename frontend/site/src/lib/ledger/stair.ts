/* The price staircase (SPEC §3.7), drawn from the engine's `priceStair`.
 *
 * A 190px plot with left and bottom 1px --line-strong axes, and a 1.5px ink
 * stepped path: money a week against the shelf price. On each tread the same
 * share of customers buys, so money rises with the price; at each class edge
 * a class stops buying and it drops. Markers are full-height 1px ink-faint
 * rules with mono 11 labels on a page-coloured capsule: market (dotted),
 * every customer buys (solid), best (solid; merged into the edge's label
 * when they are the same price), competitor (dashed). The axis line reads
 * `$lo · price → money a week ↑ · $hi`.
 *
 * Pure: returns HTML. The planner's Products section and the Calculators
 * page (phase 3) draw the same staircase.
 */
import type { Stair } from "./types.ts";
import { escape, fill, price } from "./format.ts";
import type { Words } from "./client.ts";

/** Defaults for say(). */
export const STAIR_WORDS: Record<string, string> = {
  "mark.market": "market {p}",
  "mark.allBuy": "every customer buys · {p}",
  "mark.best": "best {p}",
  "mark.merged": "best · every customer buys · {p}",
  "mark.competitor": "competitor {p}",
  axis: "price → money a week ↑",
  backorder: "Backordered: there is nothing to sell this week, at any price. The staircase returns when the stock does.",
  aria: "Money a week for {product} against its shelf price",
};

const W = (w: Words, k: string) => (k in w ? w[k] : STAIR_WORDS[k] ?? k);
const VW = 600;
const VH = 190;

/** Money a week at a price: units if every customer bought × the share that buys × the price. */
function shareAt(stair: Stair, p: number): number {
  for (const s of stair.steps) if (p <= s.to + 1e-9) return s.share;
  return 0;
}

export function drawStair(stair: Stair, o: { product: string; unitsAtEdge?: number | null; words?: Words }): string {
  const words = o.words ?? {};
  const units = o.unitsAtEdge && o.unitsAtEdge > 0 ? o.unitsAtEdge : 1;
  const nothing = stair.nothingToSell;
  const tops = stair.steps.map((s) => s.to);
  const edgeHi = Math.max(...tops, stair.markers.market, stair.markers.competitor ?? 0);
  const edgeLo = Math.min(stair.markers.market, stair.markers.allBuy, stair.markers.competitor ?? Infinity);
  const lo = Math.max(0, Math.floor(edgeLo * 0.8 * 100) / 100);
  const hi = Math.ceil(edgeHi * 1.2 * 100) / 100;
  const money = (p: number) => (nothing ? 0 : units * shareAt(stair, p) * p);
  const ymax = Math.max(1e-9, ...stair.steps.map((s) => units * s.share * s.to)) * 1.12;
  const X = (p: number) => ((Math.min(hi, Math.max(lo, p)) - lo) / (hi - lo || 1)) * VW;
  const Y = (m: number) => VH - (Math.max(0, m) / ymax) * VH;

  let d = `M${X(lo).toFixed(1)},${Y(money(lo)).toFixed(1)}`;
  if (!nothing) {
    stair.steps.forEach((s, i) => {
      if (s.to < lo) return;
      const next = stair.steps[i + 1]?.share ?? 0;
      d += ` L${X(s.to).toFixed(1)},${Y(units * s.share * s.to).toFixed(1)} L${X(s.to).toFixed(1)},${Y(units * next * s.to).toFixed(1)}`;
    });
  }
  d += ` L${VW},${VH}`;

  const pct = (p: number) => `${((X(p) / VW) * 100).toFixed(2)}%`;
  const same = Math.abs(stair.markers.best - stair.markers.allBuy) < 0.005;
  const marks: { p: number; label: string; style: string }[] = [
    { p: stair.markers.market, label: fill(W(words, "mark.market"), { p: price(stair.markers.market) }), style: "dotted" },
    { p: stair.markers.allBuy, label: fill(W(words, same ? "mark.merged" : "mark.allBuy"), { p: price(stair.markers.allBuy) }), style: "solid" },
  ];
  if (!same) marks.push({ p: stair.markers.best, label: fill(W(words, "mark.best"), { p: price(stair.markers.best) }), style: "solid" });
  if (stair.markers.competitor != null) marks.push({ p: stair.markers.competitor, label: fill(W(words, "mark.competitor"), { p: price(stair.markers.competitor) }), style: "dashed" });
  const TOPS = [-22, 4, 22, 40];

  return `
    <div class="lg-stair">
      <div class="lg-stair-plot" role="img" aria-label="${escape(fill(W(words, "aria"), { product: o.product }))}">
        <svg viewBox="0 0 ${VW} ${VH}" preserveAspectRatio="none" aria-hidden="true" focusable="false">
          <path d="${d}" fill="none" stroke="currentColor" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
        </svg>
        ${marks.map((m, i) => `
          <div class="lg-stair-mark" data-style="${m.style}" data-side="${X(m.p) / VW > 0.5 ? "left" : "right"}" style="left:${pct(m.p)}">
            <span class="lg-stair-label" style="top:${TOPS[i] ?? 40}px">${escape(m.label)}</span>
          </div>`).join("")}
      </div>
      <p class="lg-stair-axis"><span>${escape(price(lo))}</span><span>${escape(W(words, "axis"))}</span><span>${escape(price(hi))}</span></p>
      ${nothing ? `<p class="lg-stair-note">${escape(W(words, "backorder"))}</p>` : ""}
    </div>`;
}
