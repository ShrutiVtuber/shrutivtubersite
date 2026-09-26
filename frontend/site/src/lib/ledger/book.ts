/* The book: a ledger's weeks, and a business's weeks against its plan.
 *
 * Pure (no DOM, no fetch), like the engine, so `node --test` loads it and the
 * server and the page scripts draw with the same functions:
 *
 *   weekTotal       money in minus the lines written; null with no money in
 *   companyWeek     which week counts as the company's latest, and its total
 *   readAmount      "$1,370" · "−1,820" · "(400)" → a number; "" → not written
 *   parsePaste      a paste from a sheet → rows of cells
 *   pasteCells      where those cells land, from the focused cell, clipped
 *   stepCell        Enter down, Shift+Enter up
 *   chartSegments   the written weeks as runs of consecutive week numbers
 *   drawChart       the weeks chart (SPEC §3.5), as HTML
 *   drawBook        the week page (SPEC §3.4, §1.7), as HTML
 *
 * ⚠ A line that was not written is null, never 0 (docs/LEDGER.md). Nothing
 *   here sums a null, and nothing here draws a mark for a week not written.
 * ⚠ Every word is a template in BOOK_WORDS; the page passes its own say().
 */
import { DASH, count, escape, fill, money } from "./format.ts";

export type Words = Record<string, string>;

export const BOOK_WORDS: Words = {
  "line.moneyIn": "Money in",
  "line.goods": "Goods",
  "line.wages": "Wages",
  "line.rent": "Rent",
  "line.ads": "Advertising",
  "line.deliveries": "Deliveries",
  "line.units": "Units",
  "line.customers": "Customers",
  "book.line": "Line",
  "book.plan": "The plan",
  "book.week": "The week",
  "book.against": "Against the plan",
  "book.col": "Week {n}",
  "book.chip": "Week {n}",
  "book.planBeneath": "plan beneath",
  "book.planOf": "plan {x}",
  "book.aria": "Each written week against the plan",
  "chart.week": "wk {n}",
  "chart.aria": "The week as written, week by week, against the plan's week of {plan}",
  "chart.ariaNoPlan": "The week as written, week by week",
  "chart.dot": "Week {n}: {x}",
  loss: "loss",
  saved: "Week {n}: {total}.",
  savedLoss: "Week {n}: {total}, a loss.",
  savedAgainst: "Week {n}: {total}. {diff} {caret} against the plan.",
  savedAgainstLoss: "Week {n}: {total}, a loss. {diff} {caret} against the plan.",
};
const W = (w: Words, k: string) => (k in w ? w[k] : BOOK_WORDS[k] ?? k);

// ── weeks ────────────────────────────────────────────────────────────────

export interface WeekRow {
  n: number;
  moneyIn: number | null;
  goods: number | null;
  wages: number | null;
  rent: number | null;
  ads: number | null;
  deliveries: number | null;
  units?: number | null;
  customers?: number | null;
  note?: string | null;
}

export const OUT_LINES = ["goods", "wages", "rent", "ads", "deliveries"] as const;
export const MONEY_LINES = ["moneyIn", ...OUT_LINES] as const;
export type MoneyLine = (typeof MONEY_LINES)[number];

const num = (v: unknown): number | null => (typeof v === "number" && Number.isFinite(v) ? v : null);

/** Money in minus the lines written. A line not written is left out, never read as 0; no money in, no total. */
export function weekTotal(w: Partial<WeekRow> | null | undefined): number | null {
  const inn = num(w?.moneyIn);
  if (w == null || inn == null) return null;
  let total = inn;
  for (const k of OUT_LINES) {
    const v = num(w[k]);
    if (v != null) total -= v;
  }
  return total;
}

/** The week a business wrote last (the highest number), or null. */
export function latestWeek<T extends { n: number }>(weeks: T[] | null | undefined): T | null {
  let best: T | null = null;
  for (const w of weeks ?? []) if (best == null || w.n > best.n) best = w;
  return best;
}

/**
 * Which week counts as the company's latest: the highest week any business
 * wrote. Its total is the sum over the businesses that wrote THAT week; a
 * business whose latest week is older is not in the sum and is not a gap.
 * The same rule as the plate's (ledger_stream.company_week).
 */
export function companyWeek(businesses: { weeks?: Partial<WeekRow>[] | null }[]): { n: number; total: number | null } | null {
  let n = 0;
  for (const b of businesses) for (const w of b.weeks ?? []) if (typeof w.n === "number" && w.n > n) n = w.n;
  if (!n) return null;
  const totals = businesses
    .map((b) => (b.weeks ?? []).find((w) => w.n === n))
    .filter((w): w is Partial<WeekRow> => !!w)
    .map((w) => weekTotal(w))
    .filter((t): t is number => t != null);
  return { n, total: totals.length ? totals.reduce((a, b) => a + b, 0) : null };
}

/** The next week to write: one past the company's latest, or week 1. */
export const nextWeekNumber = (businesses: { weeks?: Partial<WeekRow>[] | null }[]): number =>
  (companyWeek(businesses)?.n ?? 0) + 1;

// ── reading what was typed or pasted ─────────────────────────────────────

/**
 * A figure as the game shows it: "$1,370", "1370", "−1,820", "-1820", "(400)".
 * "" and "—" are not written (null). Anything else unreadable is undefined,
 * so the page can refuse it instead of guessing.
 */
export function readAmount(raw: string | null | undefined): number | null | undefined {
  let s = String(raw ?? "").trim();
  if (!s || s === DASH || s === "-" || s === "−") return null;
  let neg = false;
  if (/^\(.*\)$/.test(s)) { neg = true; s = s.slice(1, -1).trim(); }
  s = s.replace(/[−‒–—]/g, "-");
  if (s.startsWith("-")) { neg = !neg; s = s.slice(1).trim(); }
  s = s.replace(/^\$/, "").replace(/[\s,  ']/g, "");
  if (s.startsWith("-")) { neg = !neg; s = s.slice(1); }
  if (!/^\d*\.?\d+$|^\d+\.$/.test(s)) return undefined;
  const v = Number(s);
  if (!Number.isFinite(v)) return undefined;
  return neg ? -v : v;
}

/** Whether a paste is a block from a sheet (tabs or newlines) rather than one value. */
export const isBlockPaste = (text: string): boolean => /[\t\r\n]/.test(text);

/** A paste → rows of cells. One trailing newline (a sheet adds it) is not a row. */
export function parsePaste(text: string): string[][] {
  const rows = String(text ?? "").replace(/\r\n?/g, "\n").split("\n");
  if (rows.length > 1 && rows[rows.length - 1] === "") rows.pop();
  return rows.map((r) => r.split("\t").map((c) => c.trim()));
}

/** Where a pasted block lands: from the focused cell, rightwards and downwards, clipped to the grid. */
export function pasteCells(block: string[][], at: { row: number; col: number }, size: { rows: number; cols: number }):
  { row: number; col: number; value: string }[] {
  const out: { row: number; col: number; value: string }[] = [];
  block.forEach((cells, i) => {
    const row = at.row + i;
    if (row < 0 || row >= size.rows) return;
    cells.forEach((value, j) => {
      const col = at.col + j;
      if (col < 0 || col >= size.cols) return;
      out.push({ row, col, value });
    });
  });
  return out;
}

/** Enter moves down, Shift+Enter up; the edges hold. Tab is the browser's own (along the row). */
export function stepCell(at: { row: number; col: number }, up: boolean, rows: number): { row: number; col: number } {
  const row = Math.min(rows - 1, Math.max(0, at.row + (up ? -1 : 1)));
  return { row, col: at.col };
}

// ── against the plan ─────────────────────────────────────────────────────

/** "+$849" ▲ · "−$291" ▼ · "$0" with no caret · "—" when either side is not known. */
export function against(total: number | null | undefined, plan: number | null | undefined): { text: string; caret: string } {
  if (total == null || plan == null || !Number.isFinite(total) || !Number.isFinite(plan)) return { text: DASH, caret: "" };
  const d = Math.round(total) - Math.round(plan);
  if (d === 0) return { text: money(0), caret: "" };
  return { text: `${d > 0 ? "+" : "−"}${money(Math.abs(d))}`, caret: d > 0 ? "▲" : "▼" };
}

/** The SAVED sentence (SPEC §4): "Week 7: $74,020. +$849 ▲ against the plan." Nothing else. */
export function savedSentence(n: number, total: number | null, plan: number | null, words: Words = {}): string {
  const loss = total != null && Math.round(total) < 0;
  const vs = against(total, plan);
  const key = vs.text === DASH ? (loss ? "savedLoss" : "saved") : (loss ? "savedAgainstLoss" : "savedAgainst");
  // $0 against the plan has no caret; the space it leaves is closed up.
  return fill(W(words, key), { n: String(n), total: money(total), diff: vs.text, caret: vs.caret }).replace(/ {2,}/g, " ");
}

// ── the weeks chart (SPEC §3.5) ──────────────────────────────────────────

export interface ChartPoint { n: number; v: number | null }

/**
 * The written weeks as runs of consecutive week numbers. A week not written
 * (a gap in the numbering) ends one run and the next written week starts
 * another: the line breaks there, with no marker and no label.
 */
export function chartSegments(points: ChartPoint[]): ChartPoint[][] {
  const sorted = points.filter((p) => p.v != null && Number.isFinite(p.v)).sort((a, b) => a.n - b.n);
  const out: ChartPoint[][] = [];
  for (const p of sorted) {
    const run = out[out.length - 1];
    if (run && run[run.length - 1].n === p.n - 1) run.push(p);
    else out.push([p]);
  }
  return out;
}

/** A round ceiling for the axis: 75,930 → 80,000; 9,480 → 9,500; 0 → 0. */
export function niceCeil(x: number): number {
  if (!(x > 0)) return 0;
  const m = 10 ** Math.floor(Math.log10(x));
  return (Math.ceil((x / m) * 2 - 1e-9) / 2) * m;
}

/** The value axis: 0 always in it, a round top, and a round bottom when a week (or the plan) is a loss. */
export function chartScale(values: (number | null | undefined)[]): { lo: number; hi: number } {
  const vs = values.filter((v): v is number => v != null && Number.isFinite(v));
  const hi = niceCeil(Math.max(0, ...vs));
  const least = Math.min(0, ...vs);
  const lo = least < 0 ? -niceCeil(-least) : 0;
  return hi === lo ? { lo: 0, hi: 1 } : { lo, hi };
}

/** An SVG path, one `M` per run: a gap in the week numbers is a new `M`, never an `L` across it. */
export function chartPath(points: ChartPoint[], x: (n: number) => number, y: (v: number) => number): string {
  return chartSegments(points)
    .map((run) => run.map((p, i) => `${i ? "L" : "M"}${x(p.n).toFixed(1)} ${y(p.v as number).toFixed(1)}`).join(" "))
    .join(" ");
}

const pct = (v: number) => `${(Math.round(v * 100) / 100).toFixed(2)}%`;

/**
 * The weeks chart as HTML: a 170px plot with a 64px label gutter, ticks at
 * the bottom (a loss), 0, the midpoint and the top; 0 is a solid ink-soft
 * rule, the rest dotted. The written line is 1.5px ink with 7px dots; the
 * plan's week is 1.5px ink-faint, dashed 5/4, across every written week.
 */
export function drawChart(points: ChartPoint[], plan: number | null, words: Words = {}): string {
  const written = points.filter((p) => p.v != null && Number.isFinite(p.v)).sort((a, b) => a.n - b.n);
  if (!written.length) return "";
  const { lo, hi } = chartScale([...written.map((p) => p.v), plan]);
  const first = written[0].n, last = written[written.length - 1].n;
  const X = 600, H = 170;
  const x = (n: number) => (first === last ? X / 2 : ((n - first) / (last - first)) * X);
  const y = (v: number) => H - ((v - lo) / (hi - lo)) * H;
  const ticks = [...new Set([lo, 0, hi / 2, hi].filter((t) => t >= lo && t <= hi))];
  const tickHtml = ticks.map((t) => `<div class="lb-tick" data-zero="${t === 0 ? "yes" : "no"}" style="top:${pct((y(t) / H) * 100)}"><span class="lb-tick-label">${escape(money(t))}</span></div>`).join("");
  const planPath = plan != null && Number.isFinite(plan) ? `M0 ${y(plan).toFixed(1)} L${X} ${y(plan).toFixed(1)}` : "";
  const dots = written.map((p) => `<span class="lb-dot" style="left:${pct((x(p.n) / X) * 100)};top:${pct((y(p.v as number) / H) * 100)}" title="${escape(fill(W(words, "chart.dot"), { n: String(p.n), x: money(p.v) }))}"></span>`).join("");
  const labels = written.map((p) => `<span class="lb-xlabel" style="left:${pct((x(p.n) / X) * 100)}">${escape(fill(W(words, "chart.week"), { n: String(p.n) }))}</span>`).join("");
  const aria = planPath ? fill(W(words, "chart.aria"), { plan: money(plan) }) : W(words, "chart.ariaNoPlan");
  return `<div class="lb-plot">${tickHtml}
    <svg viewBox="0 0 ${X} ${H}" preserveAspectRatio="none" role="img" aria-label="${escape(aria)}">
      ${planPath ? `<path class="lb-plan-line" d="${planPath}" />` : ""}
      <path class="lb-week-line" d="${chartPath(written, x, y)}" />
    </svg>${dots}${labels}</div>`;
}

// ── the book (SPEC §3.4, §1.7) ───────────────────────────────────────────

export interface PlanLines {
  moneyIn: number | null; goods: number | null; wages: number | null; rent: number | null;
  ads: number | null; deliveries: number | null; units: number | null; customers: number | null; total: number | null;
}

const LINES: { key: keyof PlanLines & keyof WeekRow; out: boolean; money: boolean }[] = [
  { key: "moneyIn", out: false, money: true },
  { key: "goods", out: true, money: true },
  { key: "wages", out: true, money: true },
  { key: "rent", out: true, money: true },
  { key: "ads", out: true, money: true },
  { key: "deliveries", out: true, money: true },
  { key: "units", out: false, money: false },
  { key: "customers", out: false, money: false },
];

/** A line's figure as the book writes it: a cost carries its −; $0 is a fact; null is —. */
function cell(v: number | null | undefined, line: (typeof LINES)[number]): string {
  if (v == null || !Number.isFinite(v)) return DASH;
  if (!line.money) return count(v);
  if (line.out) return Math.round(v) === 0 ? money(0) : money(-v);
  return money(v);
}

const figureHtml = (v: number | null, words: Words) =>
  `${escape(money(v))}${v != null && Math.round(v) < 0 ? `<span class="lg-loss">${escape(W(words, "loss"))}</span>` : ""}`;

/**
 * The week page. Desk: a table with the plan's column on the inset ground,
 * closed by the rose margin line, then every written week, newest first; the
 * week over a double rule; against the plan as a signed figure with its
 * caret. Phone: week chips (newest first) and one week at a time, each line's
 * plan figure set small beneath it. Both are drawn; the stylesheet shows one.
 */
export function drawBook(weeks: WeekRow[], plan: PlanLines | null, words: Words = {}, shown?: number): string {
  const cols = [...weeks].sort((a, b) => b.n - a.n);
  const one = cols.find((w) => w.n === shown) ?? cols[0] ?? null;
  const planCell = (k: keyof PlanLines, line: (typeof LINES)[number]) => cell(plan ? plan[k] : null, line);
  const lines = LINES.filter((l) => l.money || cols.some((w) => w[l.key] != null) || (plan && plan[l.key] != null));
  const gtc = `minmax(132px,1.2fr) minmax(112px,1fr)${cols.map(() => " minmax(104px,1fr)").join("")}`;
  const minw = 132 + 112 + cols.length * 104 + 32;
  const rows = lines.map((l) => `<div class="lb-book-row" role="row" style="grid-template-columns:${gtc}">
      <span role="rowheader">${escape(W(words, `line.${l.key}`))}</span>
      <span class="lb-book-plan" role="cell">${escape(planCell(l.key, l))}</span>
      ${cols.map((w) => `<span class="lb-book-num" role="cell">${escape(cell(w[l.key], l))}</span>`).join("")}
    </div>`).join("");
  const desk = `<div class="lb-book-desk"><div class="lb-book-table" role="table" aria-label="${escape(W(words, "book.aria"))}" style="min-width:${minw}px">
    <div class="lb-book-row lb-book-head" role="row" style="grid-template-columns:${gtc}">
      <span role="columnheader">${escape(W(words, "book.line"))}</span>
      <span class="lb-book-plan" role="columnheader">${escape(W(words, "book.plan"))}</span>
      ${cols.map((w) => `<span class="lb-book-num" role="columnheader">${escape(fill(W(words, "book.col"), { n: String(w.n) }))}</span>`).join("")}
    </div>
    ${rows}
    <div class="lb-book-row lb-book-total" role="row" style="grid-template-columns:${gtc}">
      <span role="rowheader">${escape(W(words, "book.week"))}</span>
      <span class="lb-book-plan" role="cell">${figureHtml(plan?.total ?? null, words)}</span>
      ${cols.map((w) => `<span class="lb-book-num" role="cell">${figureHtml(weekTotal(w), words)}</span>`).join("")}
    </div>
    <div class="lb-book-row lb-book-against" role="row" style="grid-template-columns:${gtc}">
      <span role="rowheader">${escape(W(words, "book.against"))}</span>
      <span class="lb-book-plan" role="cell">${DASH}</span>
      ${cols.map((w) => { const a = against(weekTotal(w), plan?.total); return `<span class="lb-book-num" role="cell">${escape(a.text)}${a.caret ? `<span class="lg-caret">${a.caret}</span>` : ""}</span>`; }).join("")}
    </div>
  </div></div>`;

  let phone = "";
  if (one) {
    const a = against(weekTotal(one), plan?.total);
    phone = `<div class="lb-book-phone">
      <div class="lb-book-chips" role="group">${cols.map((w) => `<button type="button" class="lg-chip" data-mono data-book-week="${w.n}" aria-pressed="${w.n === one.n}">${escape(fill(W(words, "book.chip"), { n: String(w.n) }))}</button>`).join("")}</div>
      <div class="lb-book-one">
        <div class="lg-group-head"><span class="gd-eyebrow">${escape(fill(W(words, "book.col"), { n: String(one.n) }))}</span><span class="lg-count">${escape(W(words, "book.planBeneath"))}</span></div>
        ${lines.map((l) => `<div class="lb-book-line"><div class="lg-al"><span>${escape(W(words, `line.${l.key}`))}</span><span class="lg-lead" aria-hidden="true"></span><span class="lg-val">${escape(cell(one[l.key], l))}</span></div>
          <div class="lb-book-beneath">${escape(fill(W(words, "book.planOf"), { x: planCell(l.key, l) }))}</div></div>`).join("")}
        <div class="lg-total"><span>${escape(W(words, "book.week"))}</span><span class="lg-val">${figureHtml(weekTotal(one), words)}</span></div>
        <div class="lb-book-vs"><span>${escape(fill(W(words, "book.planOf"), { x: money(plan?.total ?? null) }))}</span><span>${escape(a.text)}${a.caret ? ` <span class="lg-caret">${a.caret}</span>` : ""}</span></div>
      </div>
    </div>`;
  }
  return desk + phone;
}
