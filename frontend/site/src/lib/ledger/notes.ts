/* Before it saves (handoff README, "Nothing is applied silently").
 *
 * Changing a kept business's plan shows, before anything is written, every
 * change as path → sentence, and a comparison of the headline figures
 * (Row · Before · After · Change). `planChanges` compares the kept plan with
 * the current one field by field: type, building, each fixture count, each
 * price, the products stocked, open hours, register-hours, campaigns,
 * satisfaction, staff. `compareRows` reckons both with the same engine.
 *
 * Pure (no DOM): the business page (phase 2) uses the same two functions.
 */
import type { LedgerData, Plan, Reckoning } from "./types.ts";
import { count, days as daysText, DASH, escape, fill, money, price } from "./format.ts";
import type { Words } from "./client.ts";

export type NoteRow = { path: string; text: string };

/** Defaults for say(). */
export const NOTE_WORDS: Record<string, string> = {
  "change.text": "{a} → {b}.",
  "change.buy": "{a} → {b}. Buy the difference in the game before it opens tomorrow.",
  "change.none": "none",
  "change.edge": "the edge",
  "change.on": "on",
  "change.off": "off",
  "path.type": "type",
  "path.building": "building",
  "path.fixture": "fixtures · {name}",
  "path.price": "products · {name}",
  "path.products": "products · stocked",
  "path.open": "hours · open",
  "path.registers": "hours · registers",
  "path.campaign": "campaigns · {name}",
  "path.satisfaction": "assumptions · satisfaction",
  "path.staff": "staff · {name}",
  "path.competitor": "assumptions · {name}",
  "value.hours": "{n} h",
  "value.percent": "{n} %",
  "value.wage": "${n} an hour",
  saved: "Saved. {changes}.",
  "saved.join": "; ",
  "row.week": "The week",
  "row.customers": "Customers a week",
  "row.setup": "Setup",
  "row.payback": "Payback",
  "unit.days": "days",
};

const W = (w: Words, k: string) => (k in w ? w[k] : NOTE_WORDS[k] ?? k);

const openHours = (p: Plan | null | undefined) => (p?.hours ?? []).flat().filter((v) => v > 0).length;
const registerHours = (p: Plan | null | undefined) => (p?.hours ?? []).flat().reduce((a, v) => a + Math.max(0, v), 0);

/** Each field that differs between the kept plan and this one, as a note row. */
export function planChanges(data: LedgerData, kept: Plan | null | undefined, plan: Plan, words: Words = {}): NoteRow[] {
  const out: NoteRow[] = [];
  const text = (a: string, b: string, key = "change.text") => fill(W(words, key), { a, b });
  const k = kept ?? ({} as Plan);
  const name = <T extends { id: string; name?: string; address?: string }>(xs: T[], id: string | null | undefined) =>
    id ? (xs.find((x) => x.id === id)?.name ?? xs.find((x) => x.id === id)?.address ?? id) : W(words, "change.none");

  if ((k.typeId ?? null) !== (plan.typeId ?? null)) {
    out.push({ path: W(words, "path.type"), text: text(name(data.businessTypes, k.typeId), name(data.businessTypes, plan.typeId)) });
  }
  if ((k.buildingId ?? null) !== (plan.buildingId ?? null)) {
    const addr = (id: string | null | undefined) => (id ? data.buildings.find((b) => b.id === id)?.address ?? id : W(words, "change.none"));
    out.push({ path: W(words, "path.building"), text: text(addr(k.buildingId), addr(plan.buildingId)) });
  }
  const fixtureIds = [...new Set([...Object.keys(k.fixtures ?? {}), ...Object.keys(plan.fixtures ?? {})])];
  for (const id of fixtureIds.sort()) {
    const a = Math.floor(k.fixtures?.[id] ?? 0), b = Math.floor(plan.fixtures?.[id] ?? 0);
    if (a === b) continue;
    const f = data.fixtures.find((x) => x.id === id);
    out.push({ path: fill(W(words, "path.fixture"), { name: (f?.name ?? id).toLowerCase() }),
      text: text(String(a), String(b), b > a ? "change.buy" : "change.text") });
  }
  const priceIds = [...new Set([...Object.keys(k.prices ?? {}), ...Object.keys(plan.prices ?? {})])];
  for (const id of priceIds.sort()) {
    const a = k.prices?.[id], b = plan.prices?.[id];
    if (a === b || (a != null && b != null && Math.abs(a - b) < 0.005)) continue;
    const p = data.products.find((x) => x.id === id);
    out.push({ path: fill(W(words, "path.price"), { name: (p?.name ?? id).toLowerCase() }),
      text: text(a == null ? W(words, "change.edge") : price(a), b == null ? W(words, "change.edge") : price(b)) });
  }
  const stock = (p: Plan) => (p.products ? [...p.products].sort().join(",") : "");
  if (stock(k) !== stock(plan)) {
    const names = (p: Plan) => (p.products ?? []).map((id) => data.products.find((x) => x.id === id)?.name ?? id).join(", ") || W(words, "change.none");
    out.push({ path: W(words, "path.products"), text: text(names(k), names(plan)) });
  }
  if (openHours(k) !== openHours(plan)) {
    out.push({ path: W(words, "path.open"), text: text(fill(W(words, "value.hours"), { n: String(openHours(k)) }), fill(W(words, "value.hours"), { n: String(openHours(plan)) })) });
  }
  if (registerHours(k) !== registerHours(plan)) {
    out.push({ path: W(words, "path.registers"), text: text(fill(W(words, "value.hours"), { n: String(registerHours(k)) }), fill(W(words, "value.hours"), { n: String(registerHours(plan)) })) });
  }
  for (const c of data.campaigns) {
    const a = !!k.campaigns?.[c.id], b = !!plan.campaigns?.[c.id];
    if (a !== b) out.push({ path: fill(W(words, "path.campaign"), { name: c.name.toLowerCase() }), text: text(W(words, a ? "change.on" : "change.off"), W(words, b ? "change.on" : "change.off")) });
  }
  if ((k.satisfaction ?? 80) !== (plan.satisfaction ?? 80)) {
    out.push({ path: W(words, "path.satisfaction"), text: text(fill(W(words, "value.percent"), { n: String(k.satisfaction ?? 80) }), fill(W(words, "value.percent"), { n: String(plan.satisfaction ?? 80) })) });
  }
  const roles = [...new Set([...Object.keys(k.staff ?? {}), ...Object.keys(plan.staff ?? {})])];
  for (const id of roles.sort()) {
    const a = k.staff?.[id] ?? {}, b = plan.staff?.[id] ?? {};
    const role = data.staffRoles.find((r) => r.id === id);
    const nm = (role?.name ?? id).toLowerCase();
    if ((a.hours ?? null) !== (b.hours ?? null)) {
      const h = (v: number | undefined) => (v == null ? W(words, "change.none") : fill(W(words, "value.hours"), { n: String(v) }));
      out.push({ path: fill(W(words, "path.staff"), { name: nm }), text: text(h(a.hours), h(b.hours)) });
    }
    if ((a.wage ?? null) !== (b.wage ?? null)) {
      const wv = (v: number | undefined) => (v == null ? W(words, "change.none") : fill(W(words, "value.wage"), { n: v.toFixed(2) }));
      out.push({ path: fill(W(words, "path.staff"), { name: nm }), text: text(wv(a.wage), wv(b.wage)) });
    }
  }
  const comp = [...new Set([...Object.keys(k.competitorPrice ?? {}), ...Object.keys(plan.competitorPrice ?? {})])];
  for (const id of comp.sort()) {
    const a = k.competitorPrice?.[id], b = plan.competitorPrice?.[id];
    if (a === b) continue;
    const p = data.products.find((x) => x.id === id);
    out.push({ path: fill(W(words, "path.competitor"), { name: (p?.name ?? id).toLowerCase() }),
      text: text(a == null ? W(words, "change.none") : price(a), b == null ? W(words, "change.none") : price(b)) });
  }
  return out;
}

/** "Saved. building: 12 2nd Avenue → 40 Broadway; fixtures · cash register: 1 → 2." */
export function savedSentence(rows: NoteRow[], words: Words = {}): string {
  const changes = rows.map((r) => `${r.path}: ${r.text.split(". ")[0].replace(/\.$/, "")}`).join(W(words, "saved.join"));
  return fill(W(words, "saved"), { changes });
}

export type CompareRow = { label: string; before: string; after: string; change: string; caret: string };

const caretOf = (d: number) => (Math.abs(d) < 1e-9 ? "" : d > 0 ? "▲" : "▼");
const signedMoney = (d: number) => (Math.round(d) === 0 ? DASH : `${d > 0 ? "+" : "−"}${money(Math.abs(d))}`);
const signedCount = (d: number) => (Math.round(d) === 0 ? DASH : `${d > 0 ? "+" : "−"}${count(Math.abs(d))}`);

/** The comparison table's rows: the week, customers, setup, payback — before and after. */
export function compareRows(before: Reckoning | null, after: Reckoning | null, words: Words = {}): CompareRow[] {
  const row = (label: string, a: number | null | undefined, b: number | null | undefined,
    fmt: (n: number | null) => string, signed: (d: number) => string): CompareRow => {
    const both = a != null && b != null;
    return { label, before: fmt(a ?? null), after: fmt(b ?? null), change: both ? signed(b! - a!) : DASH, caret: both ? caretOf(Math.round((b! - a!) * 10) / 10) : "" };
  };
  const dunit = W(words, "unit.days");
  const d = (n: number | null) => daysText(n, dunit);
  return [
    row(W(words, "row.week"), before?.week.total.value, after?.week.total.value, money, signedMoney),
    row(W(words, "row.customers"), before?.customers.value, after?.customers.value, count, signedCount),
    row(W(words, "row.setup"), before?.setup.total.value, after?.setup.total.value, money, signedMoney),
    row(W(words, "row.payback"), before?.paybackDays.value, after?.paybackDays.value, d,
      (x) => (Math.abs(x) < 0.05 ? DASH : `${x > 0 ? "+" : "−"}${daysText(Math.abs(x), dunit)}`)),
  ];
}

/** The note grid's rows, as HTML for `[data-note-rows]`. */
export function drawNoteRows(rows: NoteRow[]): string {
  return rows.map((r) => `<span class="lg-note-path">${escape(r.path)}</span><span class="lg-note-text">${escape(r.text)}</span>`).join("");
}

/** The comparison table (grid 1fr auto auto auto: Row · Before · After · Change). */
export function drawCompare(rows: CompareRow[], heads: { row: string; before: string; after: string; change: string }): string {
  return `<div class="lg-compare">
    <span class="lg-compare-head">${escape(heads.row)}</span>
    <span class="lg-compare-head">${escape(heads.before)}</span>
    <span class="lg-compare-head">${escape(heads.after)}</span>
    <span class="lg-compare-head">${escape(heads.change)}</span>
    ${rows.map((r) => `
      <span class="lg-compare-cell">${escape(r.label)}</span>
      <span class="lg-compare-cell lg-num lg-before">${escape(r.before)}</span>
      <span class="lg-compare-cell lg-num">${escape(r.after)}</span>
      <span class="lg-compare-cell lg-num">${escape(r.change)}${r.caret ? `<span class="lg-caret">${r.caret}</span>` : ""}</span>`).join("")}
  </div>`;
}
