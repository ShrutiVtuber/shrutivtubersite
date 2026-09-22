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
