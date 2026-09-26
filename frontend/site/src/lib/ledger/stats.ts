/* The Ledger's stats bar, drawn from a Reckoning (LedgerStats.astro).
 *
 *   const stats = mountLedgerStats(document.querySelector("[data-ledger-stats]"));
 *   stats.update(reckoning, "Normal · satisfaction 80 %");   // null: every figure —
 *
 * The headline figures and their breakdowns are lib/statsbar.ts's Figure
 * drawings; this only chooses which lines go in which group. The open
 * breakdown stays open across re-reckonings and is redrawn with the new
 * figures, so a person can watch a line move as they change the plan.
 */
import type { BreakdownLine, Figure, Limit, Reckoning } from "./types.ts";
import { drawFigureBreakdown, drawFigureHeadline, type FigureGroup, type FigureStat, type FigureWords } from "../statsbar.ts";
import { count, days, DASH, fill, money } from "./format.ts";
import { limitHead } from "./limit.ts";
import type { Words } from "./client.ts";

const W = (w: Words, k: string, f = "") => (k in w ? w[k] : f);

const notEquals = (l: BreakdownLine) => l.op !== "=";
const lineOf = (key: string, label: string, value: number | null, unit: BreakdownLine["unit"], op: BreakdownLine["op"] = "+"): BreakdownLine =>
  ({ key, label, op, value, unit, honesty: value == null ? "not-counted" : "counted" });

export interface StatsView {
  update(rk: Reckoning | null, note?: string, limitWords?: Words): void;
  close(): void;
}

export function mountLedgerStats(bar: HTMLElement | null): StatsView {
  if (!bar) return { update() {}, close() {} };
  let words: Words = {};
  try { words = JSON.parse(bar.dataset.words || "{}"); } catch { /* the defaults below */ }
  const row = bar.querySelector<HTMLElement>("[data-sb-headline]")!;
  const noteEl = bar.querySelector<HTMLElement>("[data-sb-note]");
  let open = "";
  let last: Reckoning | null = null;
  let limitWords: Words = {};

  const fw: FigureWords = {
    foot: W(words, "foot", "Every line names something you can go and change."),
    key: W(words, "key", "≈ approximate: rests on the satisfaction you set · † not counted"),
    units: { days: W(words, "unit.days", "days"), hours: W(words, "unit.hours", "h"), years: W(words, "unit.years", "game years") },
  };

  const stats = (rk: Reckoning | null): FigureStat[] => {
    const week = rk?.week.total;
    const known = (f: Figure | undefined) => f?.value != null;
    return [
      { id: "week", name: W(words, "stat.week"), text: money(week?.value ?? null), honesty: known(week) ? week!.honesty : undefined,
        loss: rk?.week.loss ? W(words, "loss", "loss") : undefined, empty: !known(week) },
      { id: "setup", name: W(words, "stat.setup"), text: money(rk?.setup.total.value ?? null), desk: true, empty: !known(rk?.setup.total) },
      { id: "payback", name: W(words, "stat.payback"), text: days(rk?.paybackDays.value ?? null, fw.units!.days),
        honesty: known(rk?.paybackDays) ? rk!.paybackDays.honesty : undefined, empty: !known(rk?.paybackDays) },
      { id: "customers", name: W(words, "stat.customers"), text: count(rk?.customers.value ?? null), desk: true,
        honesty: known(rk?.customers) ? rk!.customers.honesty : undefined, empty: !known(rk?.customers) },
      { id: "limit", name: W(words, "stat.limit"), text: limitHead(rk?.limit ?? null, limitWords), empty: rk?.limit.state !== "held" && rk?.limit.state !== "free" },
    ];
  };

  function breakdown(id: string, rk: Reckoning): string | null {
    const title = stats(rk).find((s) => s.id === id);
    if (!title) return null;
    const base = { title: title.name, value: title.text, honesty: title.honesty, words: fw };
    if (id === "week") {
      const w = rk.week;
      if (w.total.value == null) return null;
      const out = w.total.lines.filter((l) => l.op === "−");
      const outSum = out.reduce((a, l) => a + (l.value ?? 0), 0);
      return drawFigureBreakdown({
        ...base,
        groups: [
          { label: W(words, "group.moneyIn"), sub: `+${money(w.moneyIn.value)}`, lines: w.moneyIn.lines },
          { label: W(words, "group.moneyOut"), sub: `−${money(outSum)}`, lines: out },
        ],
        total: { label: title.name, value: title.text, honesty: title.honesty },
      });
    }
    if (id === "setup") {
      const s = rk.setup;
      if (s.total.value == null) return null;
      return drawFigureBreakdown({
        ...base,
        groups: [
          { label: W(words, "group.fixtures"), sub: money(s.fixtures.value), lines: s.fixtures.lines },
          { label: W(words, "group.building"), sub: money(s.deposit.value), lines: s.total.lines.filter((l) => l.key === "setup.deposit" || l.key === "setup.stock") },
        ],
        total: { label: title.name, value: title.text },
      });
    }
    if (id === "payback") {
      const p = rk.paybackDays;
      if (!p.lines.length) return null;
      return drawFigureBreakdown({ ...base, groups: [{ label: W(words, "group.reckoned"), lines: p.lines.filter(notEquals) }],
        total: { label: title.name, value: title.text, honesty: title.honesty } });
    }
    if (id === "customers") {
      const c = rk.customers;
      if (c.value == null) return null;
      return drawFigureBreakdown({
        ...base,
        groups: [
          { label: W(words, "group.byDay"), sub: count(c.value), lines: c.lines.filter((l) => /^customers\.\d$/.test(l.key)) },
          { label: W(words, "group.against"), lines: c.lines.filter((l) => !/^customers\.\d$/.test(l.key)).map((l) => (l.op === "=" ? { ...l, op: "+" as const } : l)) },
        ],
      });
    }
    if (id === "limit") return limitBreakdown(rk.limit, base);
    return null;
  }

  function limitBreakdown(limit: Limit, base: { title: string; value: string; words: FigureWords }): string | null {
    if (limit.state !== "held" && limit.state !== "free") return null;
    const hh = limit.heldHours;
    const held: BreakdownLine[] = [
      lineOf("held.registers", fill(W(words, "held.registers"), { cap: limit.by === "registers" ? count(limit.cap ?? 0) : DASH }), hh.registers, "hours"),
      lineOf("held.displays", W(words, "held.displays"), hh.displays, "hours"),
      lineOf("held.fixtures", W(words, "held.fixtures"), hh.fixtures, "hours"),
      lineOf("held.building", fill(W(words, "held.building"), { cap: limit.by === "building" ? count(limit.cap ?? 0) : DASH }), hh.building, "hours"),
    ].map((l) => ({ ...l, op: "=" as const }));
    const groups: FigureGroup[] = [{ label: W(words, "group.held"), lines: held }];
    const fix = limit.fix;
    if (fix) {
      groups.push({
        label: W(words, "group.fix"),
        lines: [
          { ...lineOf("fix.cost", W(words, "fix.cost"), fix.cost.value, "money"), op: "=" },
          { ...lineOf("fix.weekly", W(words, "fix.weekly"), fix.weeklyCost.value, "money"), op: "=", honesty: fix.weeklyCost.honesty },
          { ...lineOf("fix.worth", W(words, "fix.worth"), fix.worth.value, "money"), op: "=", honesty: fix.worth.value == null ? "not-counted" : fix.worth.honesty },
        ],
      });
    }
    return drawFigureBreakdown({ ...base, groups });
  }

  function draw() {
    bar!.querySelectorAll(".sb-pop").forEach((p) => p.remove());
    row.innerHTML = drawFigureHeadline(stats(last), open);
    if (!open || !last) return;
    const btn = row.querySelector<HTMLElement>(`[data-stat="${open}"]`);
    const html = breakdown(open, last);
    if (!btn || !html) return;
    bar!.insertAdjacentHTML("beforeend", html);
    const pop = bar!.querySelector<HTMLElement>(".sb-pop");
    if (!pop) return;
    /* ⚠ the last figures anchor right, so the popover never leaves the page */
    const b = btn.getBoundingClientRect();
    const box = bar!.getBoundingClientRect();
    const past = b.left - box.left > box.width / 2;
    pop.style.left = past ? "auto" : `${Math.max(0, b.left - box.left)}px`;
    pop.style.right = past ? `${Math.max(0, box.right - b.right)}px` : "auto";
    pop.style.top = `${b.bottom - box.top + 6}px`;
  }

  bar.addEventListener("click", (e) => {
    const btn = (e.target as HTMLElement).closest<HTMLElement>("[data-stat]");
    if (!btn || !row.contains(btn)) return;
    open = open === btn.dataset.stat ? "" : btn.dataset.stat || "";
    draw();
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && open) { open = ""; draw(); } });
  document.addEventListener("click", (e) => {
    /* composedPath, not contains: the bar's own handler has already redrawn
       the row, so the button that was clicked is no longer in the page */
    if (open && !e.composedPath().includes(bar)) { open = ""; draw(); }
  });

  return {
    update(rk, note, lw) {
      last = rk;
      if (lw) limitWords = lw;
      if (noteEl && note !== undefined) noteEl.textContent = note;
      draw();
    },
    close() { open = ""; draw(); },
  };
}
