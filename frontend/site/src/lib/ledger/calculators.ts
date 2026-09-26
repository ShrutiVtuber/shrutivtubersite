/* The Calculators at /ledger/calculators (handoff README §8): three consoles,
 * each one question, all reckoned by the engine in the browser.
 *
 *   #stair  What price · the staircase   priceStair() drawn by stair.ts, and
 *           the best-price table for the type's products
 *   #camp   Which campaigns               cheapestCampaigns(): all 63 mixes of
 *           the game's six campaigns, the cheapest reaching the target
 *   #rob    Rent or buy                   rentOrBuy() over the years you will play
 *
 * The engine's campaign reach depends on the building (its floor area), not
 * only on the neighbourhood, so #camp and #rob choose a building inside the
 * chosen neighbourhood. "Its week" needs a plan's customers: it is reckoned
 * from the plan in hand (the planner's unsaved plan) when that plan is of the
 * same type in the same neighbourhood, and is a dash otherwise.
 *
 * The pure half (stepTarget, stepYears, campaignHref, unitsAtEdgeFor,
 * defaultBuilding) is tested with `node --test`.
 *
 * ⚠ Every word comes from the page's say() strings (data-words).
 */
import type { Building, BusinessType, Ctx, LedgerData, Plan, StairEvents } from "./types.ts";
import { cheapestCampaigns, priceStair, reckon, rentOrBuy } from "./engine.ts";
import { count, DASH, escape, factor, fill, MARK, money, price } from "./format.ts";
import { fetchPack, type Words } from "./client.ts";
import { drawStair } from "./stair.ts";
import { fullPlan } from "./stream.ts";
import { DRAFT_KEY } from "./places.ts";

export const TARGET = { min: 5, max: 120, step: 5, start: 20 } as const;
export const YEARS = { min: 1, max: 400, start: 5 } as const;

/** The promotion target stepper: 5–120 in steps of 5. */
export const stepTarget = (t: number, dir: 1 | -1): number =>
  Math.min(TARGET.max, Math.max(TARGET.min, Math.round(t / TARGET.step) * TARGET.step + dir * TARGET.step));

/** The years stepper: 1–400, by one up to 20 and by ten beyond. */
export function stepYears(y: number, dir: 1 | -1): number {
  const by = dir > 0 ? (y >= 20 ? 10 : 1) : (y > 20 ? 10 : 1);
  return Math.min(YEARS.max, Math.max(YEARS.min, y + dir * by));
}

/** "Use this mix in the plan": the planner, on this building, with these campaigns on. */
export function campaignHref(buildingId: string, campaigns: string[]): string {
  const q = new URLSearchParams({ building: buildingId, campaigns: campaigns.join(","), section: "campaigns" });
  return `/ledger/plan?${q}`;
}

/** The building a console starts on: the one asked for, the plan's, else the neighbourhood's first shop by address. */
export function defaultBuilding(data: LedgerData, hoodId: string, preferred: (string | null | undefined)[] = []): Building | null {
  for (const id of preferred) {
    const b = id ? data.buildings.find((x) => x.id === id) : null;
    if (b && b.neighbourhood === hoodId) return b;
  }
  const inHood = data.buildings.filter((b) => b.neighbourhood === hoodId).sort((a, b) => a.address.localeCompare(b.address));
  return inHood.find((b) => b.use === "shop") ?? inHood[0] ?? null;
}

/**
 * Units a week if every customer bought, for one product: from the plan in
 * hand, only when it is of this type and its building is in this
 * neighbourhood (the planner's own reading). Null otherwise: no week is shown.
 */
export function unitsAtEdgeFor(data: LedgerData, plan: Plan | null, ctx: Ctx, typeId: string, hoodId: string, productId: string): number | null {
  if (!plan || plan.typeId !== typeId || !plan.buildingId) return null;
  const b = data.buildings.find((x) => x.id === plan.buildingId);
  if (!b || b.neighbourhood !== hoodId) return null;
  const prices = { ...plan.prices };
  delete prices[productId];
  const products = plan.products && !plan.products.includes(productId) ? [...plan.products, productId] : plan.products;
  const r = reckon(data, { ...plan, prices, ...(products ? { products } : {}) }, ctx);
  if (r.state !== "ok") return null;
  return r.products.find((p) => p.id === productId)?.units ?? null;
}

interface CalcState { ctx: Ctx; building: string | null; type: string | null }

export function mountCalculators(root: HTMLElement): void {
  let words: Words = {};
  let state: CalcState;
  try { words = JSON.parse(root.dataset.words || "{}"); } catch { words = {}; }
  try { state = JSON.parse(root.dataset.state || "{}"); } catch { return; }
  const t = (k: string): string => (k in words ? words[k] : k);
  const tf = (k: string, p: Record<string, string | number>) => fill(t(k), Object.fromEntries(Object.entries(p).map(([a, b]) => [a, String(b)])));
  const $ = <T extends HTMLElement = HTMLElement>(sel: string, from: ParentNode = root) => from.querySelector<T>(sel);
  const $$ = <T extends HTMLElement = HTMLElement>(sel: string, from: ParentNode = root) => [...from.querySelectorAll<T>(sel)];

  fetchPack().then((data) => {
    if (!data) { root.dataset.loaded = "no"; return; }
    start(data);
  });

  function start(data: LedgerData) {
    root.dataset.loaded = "yes";
    let plan: Plan | null = null;
    try {
      const stored = JSON.parse(sessionStorage.getItem(DRAFT_KEY) || "null");
      if (stored && typeof stored === "object") plan = fullPlan(stored);
    } catch { plan = null; }
    const typeOf = (id: string | null | undefined): BusinessType | null => data.businessTypes.find((x) => x.id === id) ?? null;
    const buildingOf = (id: string | null | undefined): Building | null => data.buildings.find((x) => x.id === id) ?? null;
    const hoodOf = (id: string) => data.neighbourhoods.find((h) => h.id === id) ?? null;
    const productOf = (id: string) => data.products.find((p) => p.id === id) ?? null;
    const asked = buildingOf(state.building);
    const planBuilding = buildingOf(plan?.buildingId);
    const firstHood = asked?.neighbourhood ?? planBuilding?.neighbourhood ?? data.neighbourhoods.find((h) => h.id === "hells-kitchen")?.id ?? data.neighbourhoods[0].id;
    const sellers = data.businessTypes.filter((ty) => ty.products.some((p) => productOf(p.product)));

    const stair = {
      type: (typeOf(state.type) ?? typeOf(plan?.typeId) ?? typeOf("gift-shop") ?? sellers[0])!,
      product: null as string | null,
      hood: planBuilding?.neighbourhood ?? firstHood,
      events: {} as StairEvents,
    };
    const camp = { target: TARGET.start as number, hood: firstHood, building: defaultBuilding(data, firstHood, [state.building, plan?.buildingId])?.id ?? null };
    const rob = { years: YEARS.start as number, hood: firstHood, building: defaultBuilding(data, firstHood, [state.building, plan?.buildingId])?.id ?? null };

    const chips = (attr: string, items: { id: string; label: string }[], on: string | null) =>
      items.map((x) => `<button type="button" class="lg-chip" ${attr}="${escape(x.id)}" aria-pressed="${x.id === on}">${escape(x.label)}</button>`).join("");
    const hoodItems = data.neighbourhoods.map((h) => ({ id: h.id, label: h.name }));
    const almanac = (rows: [string, string][]) => rows.map(([a, b]) =>
      `<div class="lg-al"><span>${escape(a)}</span><span class="lg-lead" aria-hidden="true"></span><span class="lg-val">${b}</span></div>`).join("");
    const buildingOptions = (hood: string, chosen: string | null) => data.buildings
      .filter((b) => b.neighbourhood === hood)
      .sort((a, b) => a.address.localeCompare(b.address))
      .map((b) => `<option value="${escape(b.id)}" ${b.id === chosen ? "selected" : ""}>${escape(tf("building.option", { address: b.address, use: t(`use.${b.use}`), n: count(b.sqm) }))}</option>`).join("");

    // ── #stair ──
    function stairProducts(): string[] {
      return stair.type.products.map((p) => p.product).filter((id) => productOf(id));
    }
    function drawStairConsole() {
      const typeSel = $<HTMLSelectElement>("[data-stair-type]");
      if (typeSel && !typeSel.options.length) {
        typeSel.innerHTML = sellers.map((ty) => `<option value="${escape(ty.id)}">${escape(ty.name)}</option>`).join("");
      }
      if (typeSel) typeSel.value = stair.type.id;
      const ids = stairProducts();
      if (!stair.product || !ids.includes(stair.product)) stair.product = ids[0] ?? null;
      const prodBox = $("[data-stair-products]");
      if (prodBox) prodBox.innerHTML = chips("data-stair-product", ids.map((id) => ({ id, label: productOf(id)!.name })), stair.product);
      const hoodBox = $("[data-stair-hoods]");
      if (hoodBox) hoodBox.innerHTML = chips("data-stair-hood", hoodItems, stair.hood);
      $$("[data-stair-event]").forEach((c) => c.setAttribute("aria-pressed", String(!!stair.events[c.dataset.stairEvent as keyof StairEvents])));
      const hood = hoodOf(stair.hood);
      const note = $("[data-stair-note]");
      if (note) note.textContent = hood ? tf("stair.note", { hood: hood.name, x: factor(hood.priceIndex) }) : "";
      const plot = $("[data-stair-plot]");
      const prod = stair.product ? productOf(stair.product) : null;
      const ctx = state.ctx;
      if (plot) {
        const units = prod ? unitsAtEdgeFor(data, plan, ctx, stair.type.id, stair.hood, prod.id) : null;
        const s = prod ? priceStair(data, prod.id, stair.hood, stair.events, { competitorPrice: plan?.competitorPrice?.[prod.id], unitsAtEdge: units ?? undefined }) : null;
        plot.innerHTML = s && prod ? drawStair(s, { product: prod.name, unitsAtEdge: units, words }) : "";
      }
      const head = $("[data-best-head]");
      if (head) head.textContent = tf("best.head", { type: stair.type.name });
      const best = $("[data-best]");
      let anyWeek = false;
      if (best) best.innerHTML = ids.map((id) => {
        const units = unitsAtEdgeFor(data, plan, ctx, stair.type.id, stair.hood, id);
        const s = priceStair(data, id, stair.hood, stair.events, { competitorPrice: plan?.competitorPrice?.[id], unitsAtEdge: units ?? undefined });
        const value = !s || s.nothingToSell ? DASH : price(s.best.price);
        const week = s?.best.moneyWeek != null && !s.nothingToSell ? `${escape(money(s.best.moneyWeek))}<sup class="lg-mark">${MARK.approximate}</sup>` : DASH;
        if (week !== DASH) anyWeek = true;
        return `<span class="lc-cell">${escape(productOf(id)!.name)}</span><span class="lc-cell lg-num">${escape(value)}</span><span class="lc-cell lg-num">${week}</span>`;
      }).join("");
      const foot = $("[data-best-foot]");
      if (foot) {
        const customers = anyWeek && plan ? reckon(data, plan, ctx).customers.value : null;
        foot.textContent = customers != null
          ? tf("best.footPlan", { n: count(customers) })
          : tf("best.footNone", { type: stair.type.name.toLowerCase(), hood: hood?.name ?? "" });
      }
    }

    // ── #camp ──
    function drawCampConsole() {
      const hoodBox = $("[data-camp-hoods]");
      if (hoodBox) hoodBox.innerHTML = chips("data-camp-hood", hoodItems, camp.hood);
      const sel = $<HTMLSelectElement>("[data-camp-building]");
      if (sel && sel.dataset.hood !== camp.hood) { sel.innerHTML = buildingOptions(camp.hood, camp.building); sel.dataset.hood = camp.hood; }
      if (sel && camp.building) sel.value = camp.building;
      const hood = hoodOf(camp.hood);
      const note = $("[data-camp-note]");
      if (note) note.textContent = hood ? tf("camp.note", { x: factor(hood.marketingStrength), hood: hood.name }) : "";
      const tv = $("[data-camp-target]");
      if (tv) tv.textContent = tf("camp.targetValue", { n: camp.target });
      ($("[data-camp-dec]") as HTMLButtonElement | null)?.toggleAttribute("disabled", camp.target <= TARGET.min);
      ($("[data-camp-inc]") as HTMLButtonElement | null)?.toggleAttribute("disabled", camp.target >= TARGET.max);
      const found = $("[data-camp-found]");
      const none = $("[data-camp-none]");
      const b = buildingOf(camp.building);
      const answer = b ? cheapestCampaigns(data, b.id, camp.target) : null;
      if (found) found.hidden = !answer?.reached;
      if (none) none.hidden = !answer || answer.reached;
      if (!answer || !b) return;
      const name = (id: string) => data.campaigns.find((c) => c.id === id)?.name ?? id;
      const costOf = (id: string) => data.campaigns.find((c) => c.id === id)?.costDay ?? 0;
      if (answer.reached && answer.mix) {
        const m = answer.mix;
        const reach = $("[data-camp-reach]");
        if (reach) reach.textContent = tf("camp.reaches", { n: m.gain });
        const rows = $("[data-camp-rows]");
        if (rows) rows.innerHTML = almanac(m.campaigns.map((id) => [name(id), escape(tf("camp.perDay", { x: money(costOf(id)) }))]));
        const cost = $("[data-camp-cost]");
        if (cost) cost.textContent = tf("camp.perDay", { x: money(m.costDay) });
        const week = $("[data-camp-week]");
        if (week) week.textContent = tf("camp.perWeek", { x: money(m.costWeek) });
        const use = $<HTMLAnchorElement>("[data-camp-use]");
        if (use) use.href = campaignHref(b.id, m.campaigns);
      } else {
        const refusal = $("[data-camp-refusal]");
        if (refusal) refusal.textContent = tf("camp.unreachable", {
          t: camp.target, address: b.address, max: answer.max.gain, cost: money(answer.max.costDay),
        });
      }
    }

    // ── #rob ──
    function drawRobConsole() {
      const hoodBox = $("[data-rob-hoods]");
      if (hoodBox) hoodBox.innerHTML = chips("data-rob-hood", hoodItems, rob.hood);
      const sel = $<HTMLSelectElement>("[data-rob-building]");
      if (sel && sel.dataset.hood !== rob.hood) { sel.innerHTML = buildingOptions(rob.hood, rob.building); sel.dataset.hood = rob.hood; }
      if (sel && rob.building) sel.value = rob.building;
      const yv = $("[data-rob-years]");
      if (yv) yv.textContent = tf("rob.yearsValue", { n: rob.years });
      ($("[data-rob-dec]") as HTMLButtonElement | null)?.toggleAttribute("disabled", rob.years <= YEARS.min);
      ($("[data-rob-inc]") as HTMLButtonElement | null)?.toggleAttribute("disabled", rob.years >= YEARS.max);
      const r = rob.building ? rentOrBuy(data, rob.building, rob.years) : null;
      const note = $("[data-rob-note]");
      if (note) note.textContent = tf("rob.note", { days: r?.daysPerYear ?? 60 });
      const lines = $("[data-rob-lines]");
      const verdict = $("[data-rob-verdict]");
      if (!r || r.state !== "ok") {
        if (lines) lines.innerHTML = "";
        if (verdict) verdict.textContent = t("rob.notForRent");
        return;
      }
      if (lines) lines.innerHTML = almanac([
        [t("rob.rentYear"), escape(money(r.rentYear.value))],
        [tf("rob.rentOver", { y: count(rob.years) }), escape(money(r.rentOver.value))],
        [t("rob.price"), escape(money(r.price.value))],
        [t("rob.equals"), escape(tf("rob.equalsValue", { n: count(Math.ceil((r.yearsToRepay.value ?? 0) - 1e-9)) }))],
      ]);
      if (verdict) verdict.textContent = r.verdict === "buy"
        ? tf("rob.buy", { y: count(rob.years), d: money(r.difference) })
        : tf("rob.rent", { y: count(rob.years), x: money(r.rentOver.value), d: money(r.difference), n: count(Math.ceil((r.yearsToRepay.value ?? 0) - 1e-9)) });
    }

    root.addEventListener("click", (e) => {
      const target = e.target as HTMLElement;
      const hit = <T extends HTMLElement>(sel: string) => target.closest<T>(sel);
      let x: HTMLElement | null;
      if ((x = hit("[data-stair-product]"))) { stair.product = x.dataset.stairProduct!; drawStairConsole(); return; }
      if ((x = hit("[data-stair-hood]"))) { stair.hood = x.dataset.stairHood!; drawStairConsole(); return; }
      if ((x = hit("[data-stair-event]"))) { const k = x.dataset.stairEvent as keyof StairEvents; stair.events[k] = !stair.events[k]; drawStairConsole(); return; }
      if ((x = hit("[data-camp-hood]"))) {
        camp.hood = x.dataset.campHood!;
        camp.building = defaultBuilding(data, camp.hood, [camp.building, state.building, plan?.buildingId])?.id ?? null;
        drawCampConsole();
        return;
      }
      if (hit("[data-camp-dec]")) { camp.target = stepTarget(camp.target, -1); drawCampConsole(); return; }
      if (hit("[data-camp-inc]")) { camp.target = stepTarget(camp.target, 1); drawCampConsole(); return; }
      if ((x = hit("[data-rob-hood]"))) {
        rob.hood = x.dataset.robHood!;
        rob.building = defaultBuilding(data, rob.hood, [rob.building, state.building, plan?.buildingId])?.id ?? null;
        drawRobConsole();
        return;
      }
      if (hit("[data-rob-dec]")) { rob.years = stepYears(rob.years, -1); drawRobConsole(); return; }
      if (hit("[data-rob-inc]")) { rob.years = stepYears(rob.years, 1); drawRobConsole(); return; }
    });
    root.addEventListener("change", (e) => {
      const sel = e.target as HTMLSelectElement;
      if (sel.matches("[data-stair-type]")) { stair.type = typeOf(sel.value) ?? stair.type; stair.product = null; drawStairConsole(); }
      if (sel.matches("[data-camp-building]")) { camp.building = sel.value || null; drawCampConsole(); }
      if (sel.matches("[data-rob-building]")) { rob.building = sel.value || null; drawRobConsole(); }
    });

    drawStairConsole();
    drawCampConsole();
    drawRobConsole();
    if (location.hash) document.getElementById(location.hash.slice(1))?.scrollIntoView({ block: "start" });
  }
}
