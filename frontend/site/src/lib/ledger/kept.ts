/* A kept business as the ledger and business pages show it, reckoned with
 * the planner's own engine from the plan it was kept on.
 *
 * Pure (no DOM, no fetch). The pages call it on the server with the pack
 * from `data.ts`, so the rows, the limit and the book's plan column arrive
 * drawn, and nothing the planner would say differently can creep in.
 *
 * ⚠ The plan a business is measured against is the KEPT one (what it opened
 *   on); the working plan is only a fallback when nothing was kept.
 */
import type { Ctx, LedgerData, Limit, Plan, Reckoning } from "./types.ts";
import { reckonSafely } from "./stream.ts";
import { limitNote, limitSentence } from "./limit.ts";
import type { PlanLines } from "./book.ts";
import type { Words } from "./client.ts";

export interface LedgerCtxSource { difficulty?: string | null; courses?: string[] | null; custom?: Record<string, unknown> | null }

export const ctxOf = (l: LedgerCtxSource | null | undefined): Ctx => ({
  difficulty: l?.difficulty || "normal",
  courses: l?.courses ?? [],
  ...(l?.custom ? { custom: l.custom as Ctx["custom"] } : {}),
});

/** The plan a business opened on: the kept one, else the working one. */
export const planOf = (b: { plan?: unknown; keptPlan?: unknown }): Partial<Plan> =>
  ((b.keptPlan && typeof b.keptPlan === "object" ? b.keptPlan : b.plan) ?? {}) as Partial<Plan>;

/** The first sentence of a limit sentence: "Held at 20 customers an hour by one register, for 47 hours of the week." */
export function firstSentence(s: string): string {
  const m = /^(.*?[.!?])(\s|$)/s.exec(s.trim());
  return m ? m[1] : s.trim();
}

const COUNTED = new Set(["ok", "closed"]);

/** The plan's week, line by line, for the book's plan column. Null lines where the plan cannot be reckoned. */
export function planLines(rk: Reckoning | null): PlanLines {
  const ok = !!rk && COUNTED.has(rk.state);
  const v = (f: { value: number | null } | undefined) => (ok && f ? f.value : null);
  const units = ok && rk ? rk.products.reduce((a, p) => a + (p.units || 0), 0) : null;
  return {
    moneyIn: v(rk?.week.moneyIn), goods: v(rk?.week.goods), wages: v(rk?.week.wages), rent: v(rk?.week.rent),
    ads: v(rk?.week.ads), deliveries: v(rk?.week.deliveries),
    units: units != null ? Math.round(units) : null, customers: v(rk?.customers) != null ? Math.round(v(rk?.customers)!) : null,
    total: v(rk?.week.total),
  };
}

export interface KeptView {
  typeName: string;
  address: string;
  neighbourhood: string;
  limit: Limit | null;
  sentence: string;
  first: string;
  note: string;
  lines: PlanLines;
}

/** What the pages show of a business's kept plan. With no pack, every figure is null and the sentence says so. */
export function keptView(data: LedgerData | null, business: { plan?: unknown; keptPlan?: unknown }, ctx: Ctx, words: Words): KeptView {
  const plan = planOf(business);
  const rk = reckonSafely(data, plan, ctx);
  const type = data?.businessTypes.find((t) => t.id === plan.typeId);
  const b = data?.buildings.find((x) => x.id === plan.buildingId);
  const hood = b ? data?.neighbourhoods.find((n) => n.id === b.neighbourhood)?.name ?? "" : "";
  const limit = rk?.limit ?? null;
  const sentence = limitSentence(limit, words);
  return {
    typeName: type?.name ?? "", address: b?.address ?? "", neighbourhood: hood,
    limit, sentence, first: firstSentence(sentence), note: limitNote(limit, words), lines: planLines(rk),
  };
}
