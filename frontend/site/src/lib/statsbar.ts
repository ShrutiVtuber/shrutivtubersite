/* Drawing the numbers bar from a sheet (README-planners §6).
 *
 * The sheet is the server's; this only draws it. The groups differ per game,
 * so nothing here names a group or a stat — it renders what came back.
 *
 * ⚠ The three honesty states are typographic and share nothing with the
 * state dot's four shapes: ≈ approximate, † not counted, and counted looks
 * like nothing at all. A person must never read "approximate" as "partly".
 */
import type { Sheet, StatRow, Step, Line } from "./planner";
import type { BreakdownLine, Honesty, LineUnit } from "./ledger/types.ts";
import { MARK as FIG_MARK, escape as esc, lineValue, withMark as figWithMark } from "./ledger/format.ts";

const MARK: Record<string, string> = { approximate: "≈", "not-counted": "†" };

const escape = (t: unknown) =>
  String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c] as string));

const figure = (row: Pick<StatRow, "value" | "unit" | "integer" | "state">) => {
  if (row.state === "not-counted" && !row.value) return "—";
  const n = row.integer ? Math.round(row.value) : Math.round(row.value * 10) / 10;
  return `${n.toLocaleString("en-GB")}${row.unit || ""}`;
};

const withMark = (row: StatRow) =>
  `${escape(figure(row))}${MARK[row.state] ? `<sup>${MARK[row.state]}</sup>` : ""}`;

export function rowsOf(sheet: Sheet): Record<string, StatRow> {
  const out: Record<string, StatRow> = {};
  for (const group of sheet.groups) for (const row of group.rows) out[row.stat] = row;
  return out;
}

/** The headline stats, in the order asked for, skipping any this game lacks. */
export function headlineOf(sheet: Sheet, wanted: string[]): StatRow[] {
  const rows = rowsOf(sheet);
  const picked = wanted.map((id) => rows[id]).filter(Boolean) as StatRow[];
  if (picked.length >= 4) return picked.slice(0, 6);
  /* A game whose sheet has none of them still shows something: the rows with
     the most behind them, so the bar is never empty while a plan has numbers.
     ⚠ Never a cap — a cap is the denominator of another row and belongs
     beside it, not as a headline number of its own. */
  const isCap = (r: StatRow) => r.stat.endsWith("-max");
  const rest = Object.values(rows)
    .filter((r) => !picked.includes(r) && !isCap(r))
    .sort((a, b) => b.steps.length - a.steps.length);
  return [...picked, ...rest].slice(0, 6);
}

export function drawHeadline(sheet: Sheet, wanted: string[]): string {
  return headlineOf(sheet, wanted).map((row) => `
    <button type="button" class="sb-stat" data-stat="${escape(row.stat)}" data-state="${escape(row.state)}" aria-expanded="false">
      <span class="sb-name">${escape(row.name)}</span>
      <span class="sb-figure">${withMark(row)}</span>
    </button>`).join("");
}

export function drawGroups(sheet: Sheet): string {
  const rows = rowsOf(sheet);
  return sheet.groups.map((group) => `
    <div class="sb-group">
      <p class="gd-eyebrow">${escape(group.group)}</p>
      ${group.rows.map((row) => {
        const cap = row.cap ? rows[row.cap] : undefined;
        return `<div class="sb-line" data-state="${escape(row.state)}">
          <span>${escape(row.name)}</span>
          <span class="sb-lead" aria-hidden="true"></span>
          ${cap ? `<span class="sb-cap">of ${escape(figure(cap))}</span>` : ""}
          <span class="sb-val">${withMark(row)}</span>
        </div>`;
      }).join("")}
    </div>`).join("");
}

/** What the numbers stand on, repeated so one is never read without them. */
export function drawAssumptions(sheet: Sheet): string {
  const held = sheet.conditions.filter((c) => c.held);
  if (!sheet.conditions.length) return "";
  return held.length
    ? `Against: ${held.map((c) => escape(c.name)).join(" · ")}`
    : `Nothing is assumed — ${sheet.conditions.length} assumption${sheet.conditions.length === 1 ? "" : "s"} this build could turn on`;
}

const SIGN = (step: Step) =>
  step.kind === "increased" || step.kind === "more"
    ? `×${(1 + step.value / 100).toFixed(2)}`
    : `${step.value >= 0 ? "+" : ""}${Math.round(step.value).toLocaleString("en-GB")}`;

const source = (line: Line, out = false) => `
  <div class="sb-src" data-out="${out ? "yes" : "no"}">
    <span>${escape(line.where || line.name || line.kind)}</span>
    <span class="sb-lead" aria-hidden="true"></span>
    <span class="sb-val">${out ? "excluded" : `${line.value >= 0 ? "+" : ""}${Math.round(line.value).toLocaleString("en-GB")}`}</span>
  </div>`;

/** The breakdown: every line that made the number, and what it is missing. */
export function drawBreakdown(row: StatRow): string {
  const groups = row.steps.map((step) => `
    <div class="sb-step">
      <p class="sb-step-head"><span>${escape(step.label)}</span><span class="sb-lead" aria-hidden="true"></span><span class="sb-val">${SIGN(step)}</span></p>
      ${step.lines.map((l) => source(l)).join("")}
    </div>`).join("");
  const missing = row.uncounted.length
    ? `<div class="sb-step"><p class="sb-step-head"><span>Not counted</span><span class="sb-lead" aria-hidden="true"></span><span class="sb-val">—</span></p>
        ${row.uncounted.map((l) => source(l, true)).join("")}</div>`
    : "";
  const waiting = row.inactive.length
    ? `<div class="sb-step"><p class="sb-step-head"><span>Waiting on an assumption</span><span class="sb-lead" aria-hidden="true"></span><span class="sb-val">—</span></p>
        ${row.inactive.map((l) => source(l, true)).join("")}</div>`
    : "";
  return `
    <div class="sb-pop" data-pop>
      <div class="sb-pop-head">
        <span class="sb-name">${escape(row.name)}</span>
        <span class="sb-figure">${withMark(row)}</span>
      </div>
      ${row.why ? `<p class="sb-why">${escape(row.why)}</p>` : ""}
      ${groups || `<p class="gd-hint">Nothing has contributed to this yet.</p>`}
      ${missing}${waiting}
      <p class="sb-foot"><span>${escape(row.name)}</span><span class="sb-lead" aria-hidden="true"></span><span class="sb-val">${withMark(row)}</span></p>
      <p class="gd-hint">Every line names something you can go and change.</p>
    </div>`;
}

/* ── the Ledger's figures ─────────────────────────────────────────────────
 *
 * The Ledger's numbers are not a sheet from the server but Figures from its
 * own engine (lib/ledger/engine.ts): a value, how far to trust it, and the
 * lines that add up to it. The bar and the popover are the same drawing as
 * above — the same `.sb-stat` buttons, the same `.sb-pop` — fed from those.
 * Additions carry +, subtractions −, multipliers ×; a not-counted line is
 * struck through in ink-faint and marked †. The ≈/† key sits at the foot of
 * every breakdown, beside "Every line names something you can go and change."
 */

/** One headline figure: an id, its name (eyebrow), its text, and how far to trust it. */
export type FigureStat = {
  id: string;
  name: string;
  text: string;
  honesty?: Honesty;
  /** The word beside a negative headline ("loss"); a loss is never a colour. */
  loss?: string;
  /** Shown on the desk only: at 390 the bar keeps three figures. */
  desk?: boolean;
  /** No figure yet: the button reads — in ink-faint. */
  empty?: boolean;
};

export function drawFigureHeadline(stats: FigureStat[], open = ""): string {
  return stats.map((s) => `
    <button type="button" class="sb-stat" data-stat="${esc(s.id)}" data-empty="${s.empty ? "yes" : "no"}"
            ${s.desk ? `data-desk="yes"` : ""} aria-expanded="${open === s.id ? "true" : "false"}">
      <span class="sb-name">${esc(s.name)}</span>
      <span class="sb-figure">${figWithMark(s.text, s.honesty)}${s.loss ? ` <span class="sb-loss">${esc(s.loss)}</span>` : ""}</span>
    </button>`).join("");
}

/** A group in a breakdown: an eyebrow with a subtotal, over its almanac lines. */
export type FigureGroup = { label: string; sub?: string; lines: BreakdownLine[] };

export type FigureWords = {
  /** "Every line names something you can go and change." */
  foot: string;
  /** "≈ approximate: rests on the satisfaction you set · † not counted" */
  key: string;
  units?: Partial<Record<LineUnit, string>>;
};

const figureLine = (l: BreakdownLine, units?: Partial<Record<LineUnit, string>>) => `
  <div class="sb-fline" data-op="${esc(l.op)}" data-state="${esc(l.honesty)}">
    <span>${esc(l.label)}</span><span class="sb-lead" aria-hidden="true"></span>
    <span class="sb-val">${esc(lineValue(l, units))}${l.value != null && FIG_MARK[l.honesty] ? `<sup>${FIG_MARK[l.honesty]}</sup>` : ""}</span>
  </div>`;

/** The breakdown of one Ledger figure: its title and value, its groups, a total, the foot and the key. */
export function drawFigureBreakdown(o: {
  title: string;
  value: string;
  honesty?: Honesty;
  groups: FigureGroup[];
  total?: { label: string; value: string; honesty?: Honesty };
  words: FigureWords;
}): string {
  const groups = o.groups.filter((g) => g.lines.length).map((g) => `
    <div class="sb-fgroup">
      <p class="sb-fgroup-head"><span class="gd-eyebrow">${esc(g.label)}</span>${g.sub ? `<span class="sb-fsub">${esc(g.sub)}</span>` : ""}</p>
      ${g.lines.map((l) => figureLine(l, o.words.units)).join("")}
    </div>`).join("");
  return `
    <div class="sb-pop" data-pop data-kind="figure" role="dialog" aria-label="${esc(o.title)}">
      <div class="sb-fhead">
        <span class="sb-ftitle">${esc(o.title)}</span>
        <span class="sb-fvalue">${figWithMark(o.value, o.honesty)}</span>
      </div>
      ${groups}
      ${o.total ? `<p class="sb-ftotal"><span>${esc(o.total.label)}</span><span class="sb-val">${figWithMark(o.total.value, o.total.honesty)}</span></p>` : ""}
      <p class="sb-ffoot">${esc(o.words.foot)}</p>
      <p class="sb-fkey">${esc(o.words.key)}</p>
    </div>`;
}
