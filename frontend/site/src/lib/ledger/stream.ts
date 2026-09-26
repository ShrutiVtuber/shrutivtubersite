/* The Ledger on stream: what the overlays say, worked out without a DOM.
 *
 * Pure, like the engine, so `node --test` loads it with no build and the
 * planner can import the same change sentences the overlay prints
 * (design_handoff_ledger_overlays README §2–§4, A1–A3):
 *
 *   plateRows      which businesses the plate shows, and "and N more"
 *   weekWritten    whether a poll brought a newly written week
 *   onScreenMoved  whether the business on screen changed
 *   streamLimit    the limit sentence as chat reads it
 *   changeLabel    the planner's diff of one tap, as a sentence (A2's table)
 *   changeLine     "{change} · the week +$12,845" and its caret
 *   planView       the plan on stream, reckoned with the engine
 *
 * ⚠ Nothing here ranks or sorts by money: the plate's order is the ledger's.
 * ⚠ Every word is a template in WORDS; a caller may pass its own.
 */
import type { Ctx, LedgerData, Limit, Plan, Reckoning } from "./types.ts";
import { fill, money, reckon } from "./engine.ts";

export const WORDS = {
  plateEyebrow: "Big Ambitions · Ledger",
  cardEyebrow: "Big Ambitions · on screen",
  planEyebrow: "Big Ambitions · planning",
  weekLabel: "Week {n} · the company",
  weekLabelLoss: "Week {n} · the company, a loss",
  noWeek: "No week written yet · the company",
  weekShort: "Week {n}",
  noWeekShort: "No week yet",
  more: "and {n} more open, in the ledger's order",
  limitLabel: "What limits it · {business}",
  planLimitLabel: "What limits it",
  dataLine: "{version} · build {build} · written for chat",
  planDataLine: "{version} · build {build} · a plan, not yet open",
  cardLine: "{neighbourhood} · {week} · {company}",
  onScreen: "On screen",
  loss: "loss",
  lineSwitch: "On screen now · {business}",
  lineWeek: "Week {n} · written",
  limitFree: "Nothing binds. Every customer who would come is served, every open hour.",
  limitUnknown: "Not known yet. {reason}",
  limitNoBuilding: "Not known yet. Choose a building and the Ledger works out what holds this business back.",
  limitCannotOpen: "It cannot open yet. It needs {need} first.",
  title: "{type} · {name}",
  building: "{address} · {neighbourhood} · {capacity} an hour",
  buildingNoCapacity: "{address} · {neighbourhood}",
  noBuilding: "No building chosen yet",
  theWeek: "The week",
  setup: "Setup",
  payback: "Payback",
  days: "{n} days",
  gridLabel: "Customers each hour · a top line where it is held",
  change: "{change} · the week {delta}",
  unchanged: "unchanged",
  // A2's change sentences.
  chRegisterUp: "A {ordinal} {station}",
  chRegisterFirst: "A {station}",
  chRegisterDown: "One {station} fewer",
  chRegisterNone: "No {station}",
  chMore: "One more {fixture}",
  chFewer: "One {fixture} fewer",
  chAdd: "{fixtureA}",
  chNone: "No {fixture}",
  chPrice: "Price of {product} {price}",
  chPriceEdge: "Price of {product} back to the edge",
  chCampaignOn: "{campaign} on",
  chCampaignOff: "{campaign} off",
  chSatisfaction: "Satisfaction {n} %",
  chBuilding: "Building {address}",
  chNoBuilding: "No building",
  chType: "Type {type}",
  chNoType: "No business type",
  chHours: "Hours repainted",
  chOther: "The plan changed",
};
export type Words = typeof WORDS;

const ORDINALS = ["zeroth", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"];
const ordinal = (n: number): string => ORDINALS[n] ?? `${n}th`;
const an = (s: string): string => `${/^[aeiou]/i.test(s) ? "an" : "a"} ${s}`;
const capital = (s: string): string => s.charAt(0).toUpperCase() + s.slice(1);

/** "−$1,820" · "$72,880" · "—". Rounded to the dollar, as the Ledger's headlines are. */
export const figure = (n: number | null | undefined): string => money(n ?? null);
export const isLoss = (n: number | null | undefined): boolean => n != null && Number.isFinite(n) && Math.round(n) < 0;

// ── the plate ──────────────────────────────────────────────────────────────

export interface StreamBusiness { id: number; name: string; neighbourhood: string; week: number | null; total: number | null }
export interface StreamWeek { n: number; total: number | null }
export interface LedgerFrame {
  company: string;
  game: { version: string; build: string };
  ctx: Ctx;
  businesses?: StreamBusiness[];
  week?: StreamWeek | null;
  onScreen?: number | null;
  onScreenPlan?: Partial<Plan> | null;
  live?: { plan: Partial<Plan>; name: string; change: { label: string; delta: number | null } | null; updatedAt: string | null } | null;
}

/**
 * README §2.2: at most five rows. More than five open: the first four in the
 * ledger's order, then the business on screen if it is not among them (else
 * the fifth in order), and "and N more" for the rest. Never by money.
 */
export function plateRows<T extends { id: number }>(list: T[], onScreen: number | null | undefined, fits = 5):
  { shown: T[]; more: number } {
  if (list.length <= fits) return { shown: list.slice(), more: 0 };
  const head = list.slice(0, fits - 1);
  const at = list.findIndex((b) => b.id === onScreen);
  head.push(at >= fits - 1 ? list[at] : list[fits - 1]);
  return { shown: head, more: list.length - fits };
}

/** The plate's measures (README §3): row height, limit clamp, company size. */
export function plateMeasure(company: string, count: number) {
  const long = company.length > 24;
  const crowded = count > 5;
  return { long, crowded, rowH: crowded ? 72 : long ? 80 : 92, clamp: crowded || long ? 2 : 3, nameSize: long ? 48 : 64 };
}

/** "Week 6 · the company" · "Week 2 · the company, a loss" · "No week written yet · the company". */
export function weekLabel(week: StreamWeek | null | undefined, w: Words = WORDS): string {
  if (!week) return w.noWeek;
  return fill(isLoss(week.total) ? w.weekLabelLoss : w.weekLabel, { n: String(week.n) });
}

export function dataLine(game: { version: string; build: string } | null | undefined, plan = false, w: Words = WORDS): string {
  if (!game || !game.version) return "";
  const line = fill(plan ? w.planDataLine : w.dataLine, { version: game.version, build: game.build || "" });
  return game.build ? line : line.replace(/ · build [^·]*/, "");
}

/** The business on screen, as its row. */
export function onScreenOf(f: LedgerFrame): StreamBusiness | null {
  const list = f.businesses ?? [];
  return list.find((b) => b.id === f.onScreen) ?? null;
}

/**
 * README §2 ("a week written"): the week number a poll newly brought, or null.
 * A business whose latest week moved on, or whose week was rewritten, counts;
 * a first paint and a business that was not there before do not.
 */
export function weekWritten(prev: LedgerFrame | null | undefined, next: LedgerFrame | null | undefined): number | null {
  if (!prev?.businesses || !next?.businesses) return null;
  const before = new Map(prev.businesses.map((b) => [b.id, b]));
  let n: number | null = null;
  for (const b of next.businesses) {
    const was = before.get(b.id);
    if (!was || b.week == null) continue;
    const moved = was.week == null || b.week > was.week || (b.week === was.week && b.total !== was.total);
    if (moved && (n == null || b.week > n)) n = b.week;
  }
  return n;
}

/** README §2.6: the name of the business now on screen, when the tap moved it; null otherwise. */
export function onScreenMoved(prev: LedgerFrame | null | undefined, next: LedgerFrame | null | undefined): string | null {
  if (!prev || !next || prev.onScreen == null || next.onScreen == null || prev.onScreen === next.onScreen) return null;
  return onScreenOf(next)?.name ?? null;
}

// ── what limits it ─────────────────────────────────────────────────────────

const afterFirstSentence = (s: string): string => {
  const m = /^[^.]*\.\s+(.+)$/s.exec(s);
  return m ? m[1] : s;
};

/** The engine's limit as chat reads it (README §7, A3). */
export function streamLimit(limit: Limit | null | undefined, w: Words = WORDS): string {
  if (!limit) return "";
  if (limit.state === "free") return w.limitFree;
  if (limit.state === "cannot-open") return fill(w.limitCannotOpen, { need: limit.say.params.need ?? "" });
  if (limit.state === "held") return fill(limit.say.template, limit.say.params);
  if (limit.reason === "no-building") return w.limitNoBuilding;
  return fill(w.limitUnknown, { reason: afterFirstSentence(fill(limit.say.template, limit.say.params)) });
}

const HOURS = () => Array.from({ length: 7 }, () => Array.from({ length: 24 }, () => 0));

/** A stored plan with the engine's defaults under it, so an old or partial plan still reckons. */
export function fullPlan(p: Partial<Plan> | null | undefined): Plan {
  const plan = (p && typeof p === "object" ? p : {}) as Partial<Plan>;
  return {
    typeId: null, buildingId: null, prices: {}, fixtures: {}, campaigns: {}, satisfaction: 80, satisfactionTyped: false,
    ...plan,
    hours: Array.isArray(plan.hours) && plan.hours.length === 7 ? plan.hours : HOURS(),
  } as Plan;
}

/** Reckon, or null when the plan cannot be read at all. The overlay never shows a stale figure. */
export function reckonSafely(data: LedgerData | null, plan: Partial<Plan> | null | undefined, ctx: Ctx): Reckoning | null {
  if (!data || !plan) return null;
  try {
    return reckon(data, fullPlan(plan), { difficulty: ctx?.difficulty || "normal", courses: ctx?.courses ?? [], ...(ctx?.custom ? { custom: ctx.custom } : {}) });
  } catch {
    return null;
  }
}

// ── what just changed (A2) ─────────────────────────────────────────────────

const SHORT: Record<string, string> = { "cash-register": "register", "cabinet-with-drawers": "cabinet" };
function fixtureWord(data: LedgerData, id: string): string {
  if (SHORT[id]) return SHORT[id];
  const f = data.fixtures.find((x) => x.id === id);
  const name = (f?.name ?? id).replace(/\s*\(.*\)$/, "").toLowerCase();
  return /loudspeaker/.test(name) ? "speaker" : name;
}

const count = (rec: Record<string, number> | undefined, id: string): number => Math.max(0, Math.floor(Number(rec?.[id] ?? 0)) || 0);

/**
 * The planner's own diff of one tap, as the sentence on stream: the first
 * field that changed, in A2's order of kinds. Built from the pack's names.
 * `after` may carry its reckoning, which prices a product put back to the edge.
 */
export function changeLabel(data: LedgerData, before: Partial<Plan>, after: Partial<Plan>, reckAfter?: Reckoning | null,
  w: Words = WORDS): string {
  const b = fullPlan(before), a = fullPlan(after);
  if ((b.typeId ?? null) !== (a.typeId ?? null)) {
    const t = data.businessTypes.find((x) => x.id === a.typeId);
    return t ? fill(w.chType, { type: t.name.toLowerCase() }) : w.chNoType;
  }
  if ((b.buildingId ?? null) !== (a.buildingId ?? null)) {
    const bl = data.buildings.find((x) => x.id === a.buildingId);
    return bl ? fill(w.chBuilding, { address: bl.address }) : w.chNoBuilding;
  }
  const kind = (id: string) => data.fixtures.find((x) => x.id === id)?.kind;
  const ids = [...new Set([...Object.keys(b.fixtures ?? {}), ...Object.keys(a.fixtures ?? {})])];
  const pos = ids.filter((id) => kind(id) === "pos");
  const posBefore = pos.reduce((s, id) => s + count(b.fixtures, id), 0), posAfter = pos.reduce((s, id) => s + count(a.fixtures, id), 0);
  if (posBefore !== posAfter) {
    const moved = pos.find((id) => count(b.fixtures, id) !== count(a.fixtures, id)) ?? pos[0];
    const station = fixtureWord(data, moved);
    if (posAfter > posBefore) return posAfter === 1 ? fill(w.chRegisterFirst, { station }) : fill(w.chRegisterUp, { ordinal: ordinal(posAfter), station });
    return posAfter === 0 ? fill(w.chRegisterNone, { station }) : fill(w.chRegisterDown, { station });
  }
  for (const id of ids) {
    if (kind(id) === "pos") continue;
    const was = count(b.fixtures, id), now = count(a.fixtures, id);
    if (was === now) continue;
    const fixture = fixtureWord(data, id);
    if (kind(id) === "display") return fill(now > was ? w.chMore : w.chFewer, { fixture });
    if (was === 0) return fill(w.chAdd, { fixtureA: capital(an(fixture)), fixture });
    if (now === 0) return fill(w.chNone, { fixture });
    return fill(now > was ? w.chMore : w.chFewer, { fixture });
  }
  const products = [...new Set([...Object.keys(b.prices ?? {}), ...Object.keys(a.prices ?? {})])];
  for (const id of products) {
    const was = b.prices?.[id], now = a.prices?.[id];
    if (was === now) continue;
    const product = (data.products.find((x) => x.id === id)?.name ?? id).toLowerCase();
    const at = now ?? reckAfter?.products.find((x) => x.id === id)?.price;
    return at == null ? fill(w.chPriceEdge, { product }) : fill(w.chPrice, { product, price: `$${Number(at).toFixed(2)}` });
  }
  const campaigns = [...new Set([...Object.keys(b.campaigns ?? {}), ...Object.keys(a.campaigns ?? {})])];
  for (const id of campaigns) {
    if (!!b.campaigns?.[id] === !!a.campaigns?.[id]) continue;
    const campaign = data.campaigns.find((x) => x.id === id)?.name ?? id;
    return fill(a.campaigns?.[id] ? w.chCampaignOn : w.chCampaignOff, { campaign });
  }
  if (b.satisfaction !== a.satisfaction) return fill(w.chSatisfaction, { n: String(Math.round(a.satisfaction)) });
  if (JSON.stringify(b.hours) !== JSON.stringify(a.hours)) return w.chHours;
  return w.chOther;
}

/** A2: "{change} · the week +$12,845" with ▲, "−$4,210" with ▼, or "unchanged" with no caret. */
export function changeLine(change: { label: string; delta: number | null } | null | undefined, w: Words = WORDS):
  { text: string; caret: string } | null {
  if (!change || !change.label) return null;
  const d = change.delta;
  const r = d == null || !Number.isFinite(d) ? 0 : Math.round(d);
  const delta = r === 0 ? w.unchanged : r > 0 ? `+${money(r)}` : money(r);
  return { text: fill(w.change, { change: change.label, delta }), caret: r > 0 ? "▲" : r < 0 ? "▼" : "" };
}

// ── the plan on stream (A1) ────────────────────────────────────────────────

export interface GridCell { open: boolean; level: number; held: boolean }
export interface PlanView {
  title: string;
  where: string;
  week: string;
  /** The week's figure itself; null when it is a dash. */
  total: number | null;
  loss: boolean;
  dash: boolean;
  setup: string;
  payback: string;
  limit: string;
  grid: GridCell[][] | null;
  long: boolean;
}

const DASHED = new Set(["no-type", "no-building", "not-a-shop", "cannot-open"]);

/** Everything the plan panel and card show, from the engine's reckoning of the live plan. */
export function planView(data: LedgerData, plan: Partial<Plan>, name: string, ctx: Ctx, w: Words = WORDS): PlanView | null {
  const r = reckonSafely(data, plan, ctx);
  if (!r) return null;
  const p = fullPlan(plan);
  const type = data.businessTypes.find((x) => x.id === p.typeId)?.name ?? "";
  const title = type && name ? fill(w.title, { type, name }) : type || name;
  const b = data.buildings.find((x) => x.id === p.buildingId);
  const hood = b ? data.neighbourhoods.find((x) => x.id === b.neighbourhood)?.name ?? "" : "";
  const where = !b ? w.noBuilding
    : fill(b.capacity != null ? w.building : w.buildingNoCapacity, { address: b.address, neighbourhood: hood, capacity: String(b.capacity ?? "") });
  const dash = DASHED.has(r.state);
  const total = dash ? null : r.week.total.value;
  const loss = isLoss(total);
  const days = r.paybackDays.value;
  const payback = dash || loss || days == null || !Number.isFinite(days) ? "—"
    : fill(w.days, { n: (Math.round(days * 10) / 10).toLocaleString("en-US") });
  let grid: GridCell[][] | null = null;
  if (!dash) {
    const cap = b?.capacity ?? Math.max(1, ...r.served.flat());
    grid = r.served.map((row, d) => row.map((v, h) => ({
      open: (p.hours[d]?.[h] ?? 0) > 0,
      level: Math.round(10 + Math.min(1, Math.max(0, v / Math.max(1, cap))) * 50),
      held: r.heldBy[d]?.[h] != null,
    })));
  }
  return {
    title, where, week: figure(total), total, loss, dash,
    setup: dash ? "—" : figure(r.setup.total.value), payback,
    limit: streamLimit(r.limit, w), grid, long: title.length > 32,
  };
}
