/* The week grid and the hours painter (SPEC §3.1–3.2).
 *
 * The WEEK GRID is 7 × 24: a 32px day label, 24 cells with a 2px gap, a 44px
 * day total. A closed hour is transparent with a 1px --line border; an open
 * one is filled by the grid-intensity rule
 *
 *     color-mix(in srgb, var(--ink) N%, var(--surface-card)),  N = 6 + min(1, served/30) × 26
 *
 * with its number in ink above N 22 and ink-soft below; an hour held at its
 * ceiling adds the ceiling line (inset 0 2px 0 var(--ink)). No new token.
 * Numbers show on the desk only; at 390 the value moves to the cell's title
 * and the ceiling line carries the meaning (CSS hides `.lg-cell-n`).
 *
 * The PAINTER has the same geometry. Fills: closed --surface-inset, one
 * register color-mix(accent 35%, card), two --accent. Pointer: press, then
 * drag across cells (pointer events + elementFromPoint, touch-action none).
 * Keyboard: one tab stop (role="grid"); arrows move a 2px accent ring;
 * Space or Enter paints; 0 / 1 / 2 pick the brush.
 *
 * Both are built once and then only restyled, so a drag is never interrupted
 * by a redraw.
 */
import type { HeldBy, Reckoning } from "./types.ts";
import { count, escape, fill, pad2 } from "./format.ts";
import type { Words } from "./client.ts";

const DAYS = 7;
const HOURS = 24;
const W = (w: Words, k: string, f = "") => (k in w ? w[k] : f);

/** The grid-intensity rule's N, 6 → 32 by customers served ÷ 30. */
export const intensity = (served: number): number => Math.round(6 + Math.min(1, Math.max(0, served) / 30) * 26);
export const cellFill = (served: number): string =>
  `color-mix(in srgb, var(--ink) ${intensity(served)}%, var(--surface-card))`;

const dayShort = (w: Words, d: number) => W(w, `day.${d}`, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d]);
const dayLong = (w: Words, d: number) => W(w, `dayLong.${d}`, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][d]);

/** The hour labels over a grid: every third hour on the desk, every sixth at 390. */
export function hourLabels(): string {
  return `<div class="lg-grid-hours" aria-hidden="true"><span class="lg-grid-day"></span>${Array.from({ length: HOURS }, (_, h) =>
    `<span class="lg-grid-hour"${h % 6 === 0 ? ` data-six="yes"` : ""}>${h % 3 === 0 ? pad2(h) : ""}</span>`).join("")}<span class="lg-grid-sum"></span></div>`;
}

// ── the week grid ────────────────────────────────────────────────────────

export interface GridView { update(rk: Reckoning | null, hours: number[][] | null): void }

/**
 * Mount a WeekGrid.astro. `update(rk, hours)` redraws the served customers
 * and the caption; rk null (or a state that counts nothing) draws every
 * cell closed and the no-building caption.
 */
export function mountWeekGrid(root: HTMLElement): GridView {
  let words: Words = {};
  try { words = JSON.parse(root.dataset.words || "{}"); } catch { /* defaults */ }
  const body = root.querySelector<HTMLElement>("[data-grid-body]")!;
  const caption = root.querySelector<HTMLElement>("[data-grid-caption]");
  body.innerHTML = hourLabels() + Array.from({ length: DAYS }, (_, d) => `
    <div class="lg-grid-row" role="row">
      <span class="lg-grid-day" role="rowheader">${escape(dayShort(words, d))}</span>
      ${Array.from({ length: HOURS }, (_, h) => `<span class="lg-cell" role="cell" data-d="${d}" data-h="${h}" data-open="no"><span class="lg-cell-n"></span></span>`).join("")}
      <span class="lg-grid-sum" data-sum="${d}">—</span>
    </div>`).join("");
  const cells = [...body.querySelectorAll<HTMLElement>(".lg-cell")];
  const sums = [...body.querySelectorAll<HTMLElement>("[data-sum]")];
  const byWord = (by: HeldBy) => (by ? W(words, `by.${by}`, by) : "");

  return {
    update(rk, hours) {
      const counted = !!rk && (rk.state === "ok" || rk.state === "closed");
      for (const cell of cells) {
        const d = Number(cell.dataset.d), h = Number(cell.dataset.h);
        const open = counted && (hours?.[d]?.[h] ?? 0) > 0;
        const n = cell.firstElementChild as HTMLElement;
        const at = `${dayLong(words, d)} ${pad2(h)}:00`;
        if (!open) {
          cell.dataset.open = "no";
          cell.dataset.held = "no";
          cell.style.background = "";
          n.textContent = "";
          cell.title = counted ? fill(W(words, "cell.closed", "{at} · closed"), { at }) : "";
          continue;
        }
        const served = rk!.served[d][h];
        const would = rk!.would[d][h];
        const by = rk!.heldBy[d][h];
        cell.dataset.open = "yes";
        cell.dataset.held = by ? "yes" : "no";
        cell.dataset.ink = intensity(served) > 22 ? "ink" : "soft";
        cell.style.background = cellFill(served);
        n.textContent = String(Math.round(served));
        cell.title = fill(by ? W(words, "cell.held", "{at} · {served} served, {would} would come · held by the {by}")
          : W(words, "cell.open", "{at} · {served} served, {would} would come"),
          { at, served: count(served), would: count(would), by: byWord(by) });
      }
      sums.forEach((s, d) => {
        s.textContent = counted ? count(rk!.served[d].reduce((a, b) => a + b, 0)) : "—";
      });
      if (caption) {
        if (!rk || rk.state === "no-type" || rk.state === "no-building" || rk.state === "not-a-shop" || rk.state === "no-customers") {
          caption.textContent = W(words, "caption.none", "Nothing planned yet: with no building there is no traffic to count.");
        } else if (rk.state === "cannot-open") {
          caption.textContent = W(words, "caption.cannotOpen", "Nothing is served until it can open.");
        } else {
          const held = rk.heldBy.flat().filter(Boolean).length;
          caption.textContent = fill(W(words, "caption", "{n} customers a week, served. A line along the top of a cell means the hour is held at its ceiling: {h} hours this week. Those are the hours money is lost."),
            { n: count(rk.customers.value ?? 0), h: count(held) });
        }
      }
    },
  };
}

// ── the painter ──────────────────────────────────────────────────────────

export interface PainterView {
  update(hours: number[][]): void;
  brush(): number;
}

/**
 * Mount an HoursPainter.astro. `paint(d, h, v)` is called for each cell the
 * person paints (the page sets the plan and re-reckons, then calls update).
 * `onBrush` is told when the brush changes, if the page wants to know.
 */
export function mountPainter(root: HTMLElement, paint: (d: number, h: number, v: number) => void,
  onBrush?: (v: number) => void): PainterView {
  let words: Words = {};
  try { words = JSON.parse(root.dataset.words || "{}"); } catch { /* defaults */ }
  const grid = root.querySelector<HTMLElement>("[data-painter]")!;
  const chips = [...root.querySelectorAll<HTMLButtonElement>("[data-brush]")];
  let brush = 1;
  let cursor: [number, number] = [0, 9];
  let hours: number[][] = Array.from({ length: DAYS }, () => Array(HOURS).fill(0));
  let painting = false;

  const prefix = grid.id || "lg-paint";
  grid.innerHTML = hourLabels() + Array.from({ length: DAYS }, (_, d) => `
    <div class="lg-grid-row" role="row">
      <span class="lg-grid-day" role="rowheader">${escape(dayShort(words, d))}</span>
      ${Array.from({ length: HOURS }, (_, h) => `<span class="lg-paint" role="gridcell" id="${prefix}-${d}-${h}" data-d="${d}" data-h="${h}" data-v="0"></span>`).join("")}
      <span class="lg-grid-sum"></span>
    </div>`).join("");
  const cells = [...grid.querySelectorAll<HTMLElement>(".lg-paint")];
  const cellAt = (d: number, h: number) => cells[d * HOURS + h];

  const label = (d: number, h: number, v: number) => fill(
    v === 0 ? W(words, "cell.closed", "{at}, closed") : v === 1 ? W(words, "cell.one", "{at}, 1 register") : W(words, "cell.many", "{at}, {n} registers"),
    { at: `${dayLong(words, d)} ${pad2(h)}:00`, n: String(v) });

  const setBrush = (v: number) => {
    brush = v;
    chips.forEach((c) => c.setAttribute("aria-pressed", String(Number(c.dataset.brush) === v)));
    onBrush?.(v);
  };
  const drawCursor = () => {
    cells.forEach((c) => c.removeAttribute("data-cursor"));
    const at = cellAt(cursor[0], cursor[1]);
    at?.setAttribute("data-cursor", "yes");
    if (at) grid.setAttribute("aria-activedescendant", at.id);
  };
  const put = (d: number, h: number) => {
    if ((hours[d]?.[h] ?? 0) === brush) return;
    paint(d, h, brush);
  };
  const cellFrom = (x: number, y: number) => {
    const el = document.elementFromPoint(x, y) as HTMLElement | null;
    const c = el?.closest<HTMLElement>(".lg-paint");
    return c && grid.contains(c) ? [Number(c.dataset.d), Number(c.dataset.h)] as [number, number] : null;
  };

  chips.forEach((c) => c.addEventListener("click", () => setBrush(Number(c.dataset.brush))));
  grid.addEventListener("pointerdown", (e) => {
    const at = cellFrom(e.clientX, e.clientY);
    if (!at) return;
    e.preventDefault();
    painting = true;
    cursor = at;
    grid.focus({ preventScroll: true });
    drawCursor();
    put(at[0], at[1]);
  });
  grid.addEventListener("pointermove", (e) => {
    if (!painting) return;
    const at = cellFrom(e.clientX, e.clientY);
    if (at) put(at[0], at[1]);
  });
  const stop = () => { painting = false; };
  window.addEventListener("pointerup", stop);
  window.addEventListener("pointercancel", stop);
  grid.addEventListener("keydown", (e) => {
    const mv = ({ ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] } as Record<string, [number, number]>)[e.key];
    if (mv) {
      e.preventDefault();
      cursor = [Math.max(0, Math.min(DAYS - 1, cursor[0] + mv[0])), Math.max(0, Math.min(HOURS - 1, cursor[1] + mv[1]))];
      drawCursor();
    } else if (e.key === " " || e.key === "Enter") {
      e.preventDefault();
      put(cursor[0], cursor[1]);
    } else if (e.key === "0" || e.key === "1" || e.key === "2") {
      e.preventDefault();
      setBrush(Number(e.key));
    }
  });
  grid.addEventListener("focus", () => { grid.dataset.focused = "yes"; drawCursor(); });
  grid.addEventListener("blur", () => { grid.dataset.focused = "no"; });
  setBrush(1);

  return {
    update(next) {
      hours = next;
      for (const c of cells) {
        const d = Number(c.dataset.d), h = Number(c.dataset.h);
        const v = Math.max(0, Math.floor(next?.[d]?.[h] ?? 0));
        const shown = String(Math.min(v, 2));
        if (c.dataset.v !== shown) c.dataset.v = shown;
        c.setAttribute("aria-label", label(d, h, v));
      }
    },
    brush: () => brush,
  };
}
