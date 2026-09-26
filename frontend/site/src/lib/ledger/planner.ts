/* The planner at /ledger/plan: mounts onto the server-rendered shell.
 *
 * Planning works signed out. Every change re-reckons at once with the engine
 * (lib/ledger/engine.ts) and redraws what moved: the stats bar, What limits
 * it, It cannot open yet, the rail, the head, and the section in view. There
 * is no debounce and nothing is computed anywhere else.
 *
 * ⚠ Every word drawn here comes from the page's say() strings, handed over as
 * JSON in `data-words` and read with t(key). There is no English in this file:
 * a key missing from the page's WORDS shows as the key, and the test
 * ledger-planner-words fails.
 *
 * Inputs are never rebuilt while a person types into them: a list is drawn
 * again only when what it lists changes (its key), and otherwise its rows are
 * updated in place, so focus and the caret stay where they were.
 */
import type {
  Building, BusinessType, Ctx, LedgerData, Plan, Reckoning, StairEvents,
} from "./types.ts";
import { DEFAULT_DEMAND, DEFAULT_SATISFACTION, priceStair, rankBuildings, reckon } from "./engine.ts";
import { articled, capital, count, days, DASH, escape, factor, fill, listed, money, price, MARK } from "./format.ts";
import { fetchPack, type Words } from "./client.ts";
import { missingRows, mountLimit, type LimitView } from "./limit.ts";
import { mountLedgerStats } from "./stats.ts";
import { mountPainter, mountWeekGrid, type GridView, type PainterView } from "./grid.ts";
import { compareRows, drawCompare, drawNoteRows, planChanges, savedSentence } from "./notes.ts";
import { drawStair } from "./stair.ts";

export const SECTIONS = ["type", "building", "products", "fixtures", "hours", "campaigns", "assumptions", "review"] as const;
export type SectionId = typeof SECTIONS[number];

type LedgerRow = { id: number; name: string; difficulty: string; custom?: Record<string, unknown> | null; courses: string[] };
type BusinessRow = { id: number; name: string; ledgerId: number; opened: boolean; plan: Plan; keptPlan: Plan | null };
export type PlannerState = {
  signedIn: boolean;
  ledgers: LedgerRow[];
  ledgerId: number | null;
  business: BusinessRow | null;
  sample: boolean;
  draft: boolean;
  section: SectionId;
  signInHref: string;
  /** ?building= and ?campaigns=: a building and a campaign mix laid over the plan in hand (Places, Calculators). */
  building?: string | null;
  campaigns?: string[];
};

const DRAFT_KEY = "ledger.plan.draft";
const DAYS = 7;
const HOURS = 24;

export const emptyHours = (): number[][] => Array.from({ length: DAYS }, () => Array(HOURS).fill(0));
export const emptyPlan = (): Plan => ({
  typeId: null, buildingId: null, prices: {}, fixtures: {}, hours: emptyHours(), campaigns: {},
  satisfaction: DEFAULT_SATISFACTION, satisfactionTyped: false,
});

/** The brief's sample (BRIEF §14; test/ledger-engine.test.mjs): a gift shop at
 *  12 2nd Avenue, one register on its cabinet, open 09–21, Normal, 80 / 80.
 *  The brief's wages are its own, so the plan states them. ?sample=1 only. */
export const samplePlan = (): Plan => ({
  typeId: "gift-shop",
  buildingId: "12-2nd-avenue",
  prices: {},
  fixtures: { "cash-register": 1, "cabinet-with-drawers": 1, "shopping-baskets": 1, "rounded-shelf": 4, "product-panel": 3 },
  hours: Array.from({ length: DAYS }, () => Array.from({ length: HOURS }, (_, h) => (h >= 9 && h < 21 ? 1 : 0))),
  campaigns: {},
  satisfaction: 80,
  satisfactionTyped: false,
  staff: { "customer-service": { wage: 20 }, cleaning: { hours: 42, wage: 14 } },
});

const clone = <T>(x: T): T => JSON.parse(JSON.stringify(x));

/** A plan read back from storage or the server, made whole. */
export function wholePlan(p: Partial<Plan> | null | undefined): Plan {
  const base = emptyPlan();
  if (!p || typeof p !== "object") return base;
  const hours = Array.isArray(p.hours) && p.hours.length === DAYS
    ? p.hours.map((row) => Array.from({ length: HOURS }, (_, h) => Math.max(0, Math.floor(Number(row?.[h]) || 0))))
    : base.hours;
  return {
    ...base, ...p,
    prices: { ...(p.prices ?? {}) }, fixtures: { ...(p.fixtures ?? {}) }, campaigns: { ...(p.campaigns ?? {}) }, hours,
    satisfaction: Number.isFinite(p.satisfaction) ? Number(p.satisfaction) : DEFAULT_SATISFACTION,
    satisfactionTyped: !!p.satisfactionTyped,
  };
}

export function mountPlanner(root: HTMLElement): void {
  let words: Words = {};
  let state: PlannerState;
  try { words = JSON.parse(root.dataset.words || "{}"); } catch { words = {}; }
  try { state = JSON.parse(root.dataset.state || "{}"); } catch { return; }
  const t = (k: string): string => (k in words ? words[k] : k);
  const tf = (k: string, p: Record<string, string | number>) =>
    fill(t(k), Object.fromEntries(Object.entries(p).map(([a, b]) => [a, String(b)])));

  const $ = <T extends HTMLElement = HTMLElement>(sel: string, from: ParentNode = root) => from.querySelector<T>(sel);
  const $$ = <T extends HTMLElement = HTMLElement>(sel: string, from: ParentNode = root) => [...from.querySelectorAll<T>(sel)];

  fetchPack().then((data) => {
    if (!data) {
      root.dataset.loaded = "no";
      $("[data-limit]") && mountLimit($("[data-limit]")!, () => {}).update(null);
      return;
    }
    start(data);
  });

  function start(data: LedgerData) {
    root.dataset.loaded = "yes";
    /* ── the plan, the kept plan, the context ───────────────────────── */
    let plan: Plan;
    let kept: Plan | null = null;
    let business = state.business;
    if (business) {
      plan = wholePlan(business.plan);
      kept = wholePlan(business.keptPlan ?? business.plan);
    } else if (state.sample) {
      plan = samplePlan();
    } else if (state.draft || state.building || state.campaigns?.length) {
      let stored: Partial<Plan> | null = null;
      try { stored = JSON.parse(sessionStorage.getItem(DRAFT_KEY) || "null"); } catch { stored = null; }
      plan = wholePlan(stored);
    } else {
      plan = emptyPlan();
    }
    if (!business) {
      if (state.building && data.buildings.some((b) => b.id === state.building)) plan.buildingId = state.building;
      const mix = (state.campaigns ?? []).filter((id) => data.campaigns.some((c) => c.id === id));
      if (mix.length) plan.campaigns = Object.fromEntries(mix.map((id) => [id, true]));
      if (state.building || state.campaigns?.length) {
        // laid over once: a reload keeps the plan as it now is, not the link's building again
        const url = new URL(window.location.href);
        url.searchParams.delete("building");
        url.searchParams.delete("campaigns");
        url.searchParams.set("draft", "1");
        history.replaceState(null, "", url);
      }
    }
    let ledgerId: number | null = business?.ledgerId ?? state.ledgerId ?? state.ledgers[0]?.id ?? null;
    const ledger = () => state.ledgers.find((l) => l.id === ledgerId) ?? null;
    const ctxOf = (): Ctx => {
      const l = ledger();
      return l ? { difficulty: l.difficulty || "normal", courses: l.courses ?? [], ...(l.custom ? { custom: l.custom as Ctx["custom"] } : {}) }
        : { difficulty: "normal", courses: [] };
    };
    let ctx = ctxOf();
    let rk: Reckoning = reckon(data, plan, ctx);
    let rkKept: Reckoning | null = kept ? reckon(data, kept, ctx) : null;

    let section: SectionId = SECTIONS.includes(state.section) ? state.section : "type";
    const visited = new Set<SectionId>([section]);
    const finder = { hood: null as string | null, cap: null as number | null, rank: true };
    let stairFor: string | null = null;
    const events: StairEvents = {};
    let savedNote = "";

    /* ── lookups ───────────────────────────────────────────────────── */
    const typeOf = (id: string | null | undefined): BusinessType | null => data.businessTypes.find((x) => x.id === id) ?? null;
    const buildingOf = (id: string | null | undefined): Building | null => data.buildings.find((x) => x.id === id) ?? null;
    const hoodOf = (id: string | null | undefined) => data.neighbourhoods.find((x) => x.id === id) ?? null;
    const productOf = (id: string) => data.products.find((x) => x.id === id) ?? null;
    const fixtureOf = (id: string) => data.fixtures.find((x) => x.id === id) ?? null;
    const roleOf = (id: string) => data.staffRoles.find((x) => x.id === id) ?? null;
    const courseName = (id: string) => data.courses.find((c) => c.id === id)?.name ?? id;
    const primaries = (type: BusinessType) => type.products.filter((p) => p.impact >= 1).map((p) => p.product).filter((id) => productOf(id));
    const stocked = (): string[] => {
      const type = typeOf(plan.typeId);
      if (!type) return [];
      return (plan.products ?? primaries(type)).filter((id) => productOf(id));
    };
    const difficulty = () => {
      const ds = data.difficulties;
      const d = ds.find((x) => x.id === ctx.difficulty) ?? ds.find((x) => x.id === "normal") ?? ds[0];
      return { ...d, ...(ctx.custom ?? {}) };
    };
    const openHours = () => plan.hours.flat().filter((v) => v > 0).length;
    const registerHours = () => plan.hours.flat().reduce((a, v) => a + Math.max(0, v), 0);
    const alts = (s: string | null | undefined) => (s ? s.split("|").filter(Boolean) : []);
    const useA = (use: string) => t(`use.${use}`);

    /* ── mounted pieces ────────────────────────────────────────────── */
    const stats = mountLedgerStats($("[data-ledger-stats]"));
    const limitEl = $("[data-limit]");
    let limitWords: Words = {};
    try { limitWords = JSON.parse(limitEl?.dataset.words || "{}"); } catch { /* defaults */ }
    const limitView: LimitView | null = limitEl ? mountLimit(limitEl, (limit) => {
      if (limit.fix?.kind === "building") {
        finder.rank = true;
        finder.cap = null;
        go("building");
        return;
      }
      if (limit.fix?.plan) set(() => { plan = wholePlan(clone(limit.fix!.plan!)); });
    }, limitWords) : null;
    const painterEl = $("[data-hours-painter]");
    const painter: PainterView | null = painterEl
      ? mountPainter(painterEl, (d, h, v) => set(() => { plan.hours[d][h] = v; }))
      : null;
    const gridEl = $("[data-week-grid]");
    const grid: GridView | null = gridEl ? mountWeekGrid(gridEl) : null;

    /* ── changing the plan ─────────────────────────────────────────── */
    function set(change: () => void) {
      change();
      reckonAll();
    }

    function reckonAll() {
      rk = reckon(data, plan, ctx);
      rkKept = kept ? reckon(data, kept, ctx) : null;
      if (!business) {
        try { sessionStorage.setItem(DRAFT_KEY, JSON.stringify(plan)); } catch { /* private mode: nothing kept */ }
      }
      drawAll();
      /* A hook for whatever else on the page follows the plan (the "Plan on
         stream" switch sends it to the overlay): the plan as it now stands. */
      root.dispatchEvent(new CustomEvent("ledger:plan", { detail: { plan: clone(plan), reckoning: rk, business: business?.id ?? null, ledgerId } }));
    }

    function go(next: SectionId) {
      section = next;
      visited.add(next);
      const url = new URL(window.location.href);
      url.searchParams.set("section", next);
      url.searchParams.delete("sample");
      history.replaceState(null, "", url);
      drawAll();
      const main = $("[data-main]");
      if (main && main.getBoundingClientRect().top < 0) main.scrollIntoView({ block: "start" });
    }

    /* ── drawing ───────────────────────────────────────────────────── */
    function drawAll() {
      const d = difficulty();
      stats.update(rk, tf("stats.note", { difficulty: d?.name ?? ctx.difficulty, s: plan.satisfaction }), limitWords);
      limitView?.update(rk.limit);
      drawMissing();
      drawHead();
      drawRail();
      $$("[data-section]").forEach((el) => { el.hidden = el.dataset.section !== section; });
      drawNav();
      if (section === "type") drawType();
      if (section === "building") drawBuilding();
      if (section === "products") drawProducts();
      if (section === "fixtures") drawFixtures();
      if (section === "hours") drawHours();
      if (section === "campaigns") drawCampaigns();
      if (section === "assumptions") drawAssumptions();
      if (section === "review") drawReview();
    }

    function drawMissing() {
      const box = $("[data-missing]");
      if (!box) return;
      const rows = rk.state === "cannot-open" || rk.missing.length ? missingRows(rk.missing, data, plan, words) : [];
      box.hidden = !rows.length;
      const at = $("[data-note-rows]", box);
      if (at) at.innerHTML = drawNoteRows(rows);
    }

    function drawHead() {
      const type = typeOf(plan.typeId);
      const b = buildingOf(plan.buildingId);
      const title = $("[data-plan-title]");
      if (title) {
        title.textContent = business ? business.name
          : type ? tf("title.type", { type: type.name.toLowerCase() }) : t("title.none");
      }
      const meta = $("[data-plan-meta]");
      if (meta) {
        const parts = [type?.name ?? t("meta.noType"), b ? `${b.address} · ${hoodOf(b.neighbourhood)?.name ?? b.neighbourhood}` : t("meta.noBuilding")];
        const l = ledger();
        if (business) parts.push(tf(business.opened ? "meta.opened" : "meta.kept", { ledger: l?.name ?? "" }));
        else parts.push(t("meta.unsaved"));
        meta.textContent = parts.join(" · ");
      }
    }

    function railCount(id: SectionId): string {
      const type = typeOf(plan.typeId);
      const b = buildingOf(plan.buildingId);
      switch (id) {
        case "type": return type ? type.name.split(" ")[0].toLowerCase() : "";
        case "building": return b ? b.layout ?? `${b.sqm} m²` : t("rail.none");
        case "products": return type ? String(stocked().length) : "";
        case "fixtures": return String(Object.values(plan.fixtures).filter((n) => n > 0).length);
        case "hours": return tf("rail.hours", { n: openHours() });
        case "campaigns": return tf("rail.campaigns", { n: data.campaigns.filter((c) => plan.campaigns[c.id]).length, of: data.campaigns.length });
        case "assumptions": {
          const yours = (plan.satisfactionTyped ? 1 : 0) + Object.keys(plan.competitorPrice ?? {}).length + Object.keys(plan.demand ?? {}).length;
          return yours ? tf("rail.yours", { n: yours }) : "";
        }
        case "review": {
          if (!business) return "";
          const n = planChanges(data, kept, plan, words).length;
          return n ? tf(n === 1 ? "rail.change" : "rail.changes", { n }) : "";
        }
      }
    }

    function drawRail() {
      for (const row of $$("[data-go]")) {
        const id = row.dataset.go as SectionId;
        const now = id === section;
        row.setAttribute("aria-current", now ? "step" : "false");
        const mark = $("[data-rail-mark]", row);
        if (mark) mark.dataset.state = now ? "now" : visited.has(id) ? "done" : "open";
        const c = $("[data-rail-count]", row);
        if (c) c.textContent = railCount(id);
      }
    }

    function drawNav() {
      const i = SECTIONS.indexOf(section);
      const prev = $<HTMLButtonElement>("[data-prev]");
      const next = $<HTMLButtonElement>("[data-next]");
      const nameOf = (id: SectionId) => t(`section.${id}`);
      if (prev) {
        prev.disabled = i === 0;
        prev.textContent = i === 0 ? t("nav.start") : tf("nav.prev", { name: nameOf(SECTIONS[i - 1]) });
      }
      if (next) {
        next.disabled = i === SECTIONS.length - 1;
        next.textContent = i === SECTIONS.length - 1 ? t("nav.end") : tf("nav.next", { name: nameOf(SECTIONS[i + 1]) });
      }
    }

    /** Draw a list again only when what it lists has changed. */
    function keyed(el: HTMLElement | null, key: string, build: () => string): boolean {
      if (!el) return false;
      if (el.dataset.key === key) return false;
      el.dataset.key = key;
      el.innerHTML = build();
      return true;
    }

    // ── Type ──────────────────────────────────────────────────────────
    /** The least a type's required fixtures cost: the cheapest of each "a|b", with what it stands on. */
    function leastToOpen(type: BusinessType): number {
      let sum = 0;
      for (const group of type.requires) {
        let best = Infinity;
        for (const id of alts(group)) {
          const f = fixtureOf(id);
          if (!f) continue;
          const under = alts(f.needs).map(fixtureOf).filter(Boolean).map((x) => x!.price);
          best = Math.min(best, f.price + (under.length ? Math.min(...under) : 0));
        }
        if (Number.isFinite(best)) sum += best;
      }
      return sum;
    }

    function drawType() {
      const box = $("[data-types]");
      if (!box) return;
      const open = data.businessTypes.filter((ty) => !ty.course || ctx.courses.includes(ty.course)).length;
      const note = $("[data-type-note]");
      if (note) note.textContent = tf("type.note", { n: data.businessTypes.length, open });
      box.innerHTML = data.businessTypes.map((ty) => {
        const locked = !!ty.course && !ctx.courses.includes(ty.course);
        const chosen = plan.typeId === ty.id;
        const course = !ty.course ? t("type.noCourse")
          : locked ? tf("type.needs", { course: courseName(ty.course) }) : tf("type.finished", { course: courseName(ty.course) });
        const sells = listed(primaries(ty).map((id) => productOf(id)!.name.toLowerCase()), t("and"));
        const line = tf(sells ? "type.line" : "type.lineNoProducts", { products: sells, useA: useA(ty.uses[0] ?? "shop") });
        const least = leastToOpen(ty);
        return `<div class="lg-choose" data-chosen="${chosen ? "yes" : "no"}" data-locked="${locked ? "yes" : "no"}">
          <span class="lg-ring" aria-hidden="true"></span>
          <button type="button" class="lg-row-pick" data-type="${escape(ty.id)}" ${locked ? "disabled" : ""} aria-pressed="${chosen}">
            ${chosen ? `<span class="lg-chosen-word">${escape(t("chosen"))}</span>` : ""}
            <span class="lg-row-title"><span class="lg-row-name">${escape(ty.name)}</span><span class="lg-row-tag">${escape(course)}</span></span>
            <span class="lg-row-line">${escape(line)}</span>
          </button>
          <span class="lg-row-right">${least ? escape(tf("type.from", { x: money(least) })) : ""}</span>
        </div>`;
      }).join("");
    }

    root.addEventListener("click", (e) => {
      const el = (e.target as HTMLElement).closest<HTMLElement>("[data-type]");
      if (!el || (el as HTMLButtonElement).disabled) return;
      const id = el.dataset.type!;
      if (plan.typeId === id) return;
      set(() => {
        const type = typeOf(id)!;
        const sells = new Set(type.products.map((p) => p.product));
        plan.typeId = id;
        delete plan.products;
        plan.prices = Object.fromEntries(Object.entries(plan.prices).filter(([k]) => sells.has(k)));
        stairFor = null;
      });
    });

    // ── Building ──────────────────────────────────────────────────────
    const CAPS = [15, 30, 40, 75];
    function drawBuilding() {
      const type = typeOf(plan.typeId);
      const use = type?.uses[0] ?? "shop";
      const hoods = $("[data-hoods]");
      keyed(hoods, "hoods", () => `<span class="lg-chip-label">${escape(t("finder.hood"))}</span>` +
        [`<button type="button" class="lg-chip" data-hood="">${escape(t("finder.all"))}</button>`,
          ...data.neighbourhoods.map((h) => `<button type="button" class="lg-chip" data-hood="${escape(h.id)}">${escape(h.name)}</button>`)].join(""));
      $$("[data-hood]").forEach((c) => c.setAttribute("aria-pressed", String((c.dataset.hood || null) === finder.hood)));
      const caps = $("[data-caps]");
      keyed(caps, "caps", () => `<span class="lg-chip-label">${escape(t("finder.capacity"))}</span>` +
        [`<button type="button" class="lg-chip" data-mono data-cap="">${escape(t("finder.any"))}</button>`,
          ...CAPS.map((c) => `<button type="button" class="lg-chip" data-mono data-cap="${c}">${c}</button>`)].join(""));
      $$("[data-cap]").forEach((c) => c.setAttribute("aria-pressed", String((c.dataset.cap ? Number(c.dataset.cap) : null) === finder.cap)));
      const rankBtn = $<HTMLButtonElement>("[data-rank]");
      if (rankBtn) {
        rankBtn.disabled = !type;
        rankBtn.setAttribute("aria-pressed", String(finder.rank && !!type));
        rankBtn.textContent = type ? tf("finder.rankFor", { type: type.name }) : t("finder.rankNone");
      }
      const ranking = finder.rank && !!type;
      const rows = rankBuildings(data, plan, ctx, { neighbourhood: finder.hood, use, capacity: finder.cap, rank: ranking });
      const countEl = $("[data-finder-count]");
      if (countEl) countEl.textContent = tf("finder.count", { n: count(rows.length), of: count(data.buildings.length) });
      const empty = $("[data-finder-empty]");
      const list = $("[data-finder-rows]");
      if (empty) {
        empty.hidden = rows.length > 0;
        const body = $(".gd-empty p", empty);
        if (body) body.textContent = tf("finder.emptyBody", {
          hood: finder.hood ? hoodOf(finder.hood)?.name ?? finder.hood : t("finder.anyHood"),
          cap: finder.cap ?? t("finder.any"),
        });
      }
      const shown = rows.slice(0, 8);
      if (plan.buildingId && !shown.some((r) => r.id === plan.buildingId)) {
        const mine = rankBuildings(data, plan, ctx, { rank: ranking }).find((r) => r.id === plan.buildingId);
        if (mine) shown.unshift(mine);
      }
      if (list) {
        list.hidden = !rows.length && !plan.buildingId;
        list.innerHTML = shown.map((r) => {
          const b = buildingOf(r.id)!;
          const chosen = plan.buildingId === b.id;
          const meta = [b.layout, `${count(b.sqm)} m²`, b.capacity != null ? tf("finder.capacityOf", { n: b.capacity }) : null,
            tf("finder.traffic", { n: b.traffic }), b.rentDay != null ? tf("finder.rentDay", { x: money(b.rentDay) }) : null]
            .filter(Boolean).join(" · ");
          const figure = ranking
            ? { label: t("finder.plannedWeek"), value: r.week != null ? `${money(r.week)}<sup class="lg-mark">${MARK.approximate}</sup>` : escape(t("finder.cannotTrade")) }
            : { label: t("finder.rentWeek"), value: escape(b.rentDay != null ? money(b.rentDay * 7) : DASH) };
          return `<div class="lg-row" data-chosen="${chosen ? "yes" : "no"}">
            <button type="button" class="lg-row-pick" data-building="${escape(b.id)}" aria-pressed="${chosen}">
              ${chosen ? `<span class="lg-chosen-word">${escape(t("chosen"))}</span>` : ""}
              <span class="lg-row-title"><span class="lg-row-name">${escape(b.address)}</span><span class="lg-row-line">${escape(hoodOf(b.neighbourhood)?.name ?? b.neighbourhood)}</span></span>
              <span class="lg-row-meta">${escape(meta)}</span>
            </button>
            <span class="lg-row-figure"><span class="gd-eyebrow">${escape(figure.label)}</span><span class="lg-num">${figure.value}</span></span>
            <a class="lg-link" href="/ledger/places?building=${encodeURIComponent(b.id)}">${escape(t("finder.read"))}</a>
          </div>`;
        }).join("");
      }
      const more = $<HTMLAnchorElement>("[data-finder-more]");
      if (more) {
        const q = new URLSearchParams();
        if (finder.hood) q.set("hood", finder.hood);
        if (finder.cap) q.set("cap", String(finder.cap));
        q.set("use", use);
        more.href = `/ledger/places?${q}`;
        more.textContent = tf("finder.more", { n: count(rows.length) });
      }
      const none = $<HTMLButtonElement>("[data-no-building]");
      if (none) none.disabled = !plan.buildingId;
    }

    root.addEventListener("click", (e) => {
      const target = e.target as HTMLElement;
      const hood = target.closest<HTMLElement>("[data-hood]");
      if (hood) { finder.hood = hood.dataset.hood || null; drawAll(); return; }
      const cap = target.closest<HTMLElement>("[data-cap]");
      if (cap) { finder.cap = cap.dataset.cap ? Number(cap.dataset.cap) : null; drawAll(); return; }
      if (target.closest("[data-rank]")) { finder.rank = !finder.rank; drawAll(); return; }
      if (target.closest("[data-clear-filters]")) { finder.hood = null; finder.cap = null; drawAll(); return; }
      const b = target.closest<HTMLElement>("[data-building]");
      if (b) { const id = b.dataset.building!; if (plan.buildingId !== id) set(() => { plan.buildingId = id; }); return; }
      if (target.closest("[data-no-building]")) { set(() => { plan.buildingId = null; }); return; }
    });

    // ── Products ──────────────────────────────────────────────────────
    function unitsAtEdge(id: string): number | null {
      const line = rk.products.find((p) => p.id === id);
      if (line?.tread && line.tread.share > 0) return line.units / line.tread.share;
      const prices = { ...plan.prices };
      delete prices[id];
      const r = reckon(data, { ...plan, prices }, ctx);
      return r.products.find((p) => p.id === id)?.units ?? null;
    }

    function treadSentence(id: string): string {
      const line = rk.products.find((p) => p.id === id);
      const prod = productOf(id)!;
      const market = tf("products.market", { p: price(prod.marketPrice) });
      if (!line) return `${t(plan.buildingId ? "products.noFigures" : "products.noBuilding")} ${market}`;
      const typed = plan.prices[id] != null;
      let s: string;
      if (!line.tread) s = t("tread.none");
      else if (line.tread.step === 0) s = t("tread.all");
      else if (line.tread.buyers.length === 1) s = tf("tread.only", { cls: t(`class.${line.tread.buyers[0]}`) });
      else {
        const lost = (["working", "middle", "upper"] as const).filter((c) => !line.tread!.buyers.includes(c));
        s = tf("tread.above", { lost: t(`class.${lost[lost.length - 1] ?? "working"}`), still: listed(line.tread.buyers.map((c) => t(`class.${c}`)), t("and")) });
      }
      const edge = typed ? "" : ` ${tf("products.atEdge", { p: price(line.edge) })}`;
      return `${s}${edge} ${market}`;
    }

    function drawProducts() {
      const type = typeOf(plan.typeId);
      const box = $("[data-products]");
      const noType = $("[data-products-none]");
      if (noType) noType.hidden = !!type;
      const stairBox = $("[data-stair-block]");
      if (stairBox) stairBox.hidden = !type;
      const moreBox = $("[data-products-more]");
      if (!box) return;
      if (!type) { box.innerHTML = ""; box.dataset.key = ""; if (moreBox) moreBox.innerHTML = ""; return; }
      const ids = stocked();
      const b = buildingOf(plan.buildingId);
      const hood = b ? hoodOf(b.neighbourhood) : null;
      const note = $("[data-products-note]");
      if (note) note.textContent = hood ? tf("products.noteHood", { hood: hood.name }) : t("products.noteNoHood");
      if (!stairFor || !ids.includes(stairFor)) stairFor = ids[0] ?? null;
      keyed(box, `${type.id}|${ids.join(",")}`, () => ids.map((id) => {
        const prod = productOf(id)!;
        const listedAs = type.products.find((p) => p.product === id);
        const tag = !listedAs ? t("products.unlisted") : listedAs.impact >= 1 ? t("products.primary") : tf("products.impact", { x: factor(listedAs.impact) });
        return `<div class="lg-row" data-product="${escape(id)}">
          <div class="lg-row-main">
            <span class="lg-row-title"><span class="lg-row-name">${escape(prod.name)}</span><span class="lg-row-tag">${escape(tag)}</span></span>
            <span class="lg-row-line" data-tread></span>
            <span class="lg-row-line" data-yours hidden><span class="lg-yours">${escape(t("yours"))}</span> <button type="button" class="lg-link" data-edge="${escape(id)}"></button></span>
          </div>
          <label class="lg-money"><span>$</span><input class="lg-input" type="text" inputmode="decimal" autocomplete="off" placeholder="${DASH}"
            data-price="${escape(id)}" aria-label="${escape(tf("products.priceAria", { name: prod.name }))}"></label>
          <span class="lg-row-right" data-figs></span>
          <button type="button" class="lg-link" data-stair-for="${escape(id)}">${escape(t("products.staircase"))}</button>
          <button type="button" class="lg-link" data-unstock="${escape(id)}">${escape(t("products.unstock"))}</button>
        </div>`;
      }).join(""));
      for (const row of $$("[data-product]", box)) {
        const id = row.dataset.product!;
        const line = rk.products.find((p) => p.id === id);
        const input = $<HTMLInputElement>("[data-price]", row)!;
        const typed = plan.prices[id] != null;
        if (document.activeElement !== input) input.value = typed ? String(plan.prices[id]) : "";
        input.classList.toggle("lg-typed", typed);
        $("[data-tread]", row)!.textContent = treadSentence(id);
        $("[data-figs]", row)!.innerHTML = line
          ? `${escape(tf("products.figs", { units: count(line.units), money: money(line.moneyIn.value) }))}<sup class="lg-mark">${MARK.approximate}</sup>`
          : escape(tf("products.figs", { units: DASH, money: DASH }));
        const yours = $("[data-yours]", row)!;
        yours.hidden = !typed || !line;
        if (typed && line) $("[data-edge]", yours)!.textContent = tf("products.useEdge", { p: price(line.edge) });
        $("[data-stair-for]", row)!.setAttribute("aria-pressed", String(stairFor === id));
        row.dataset.chosen = stairFor === id ? "yes" : "no";
      }
      if (moreBox) {
        const others = type.products.map((p) => p.product).filter((id) => productOf(id) && !ids.includes(id));
        keyed(moreBox, `${type.id}|${others.join(",")}`, () => others.length
          ? `<span class="lg-chip-label">${escape(t("products.alsoSells"))}</span>` + others.map((id) =>
            `<button type="button" class="lg-chip" data-stock="${escape(id)}">+ ${escape(productOf(id)!.name)}</button>`).join("")
          : "");
      }
      drawStairBlock(ids, hood?.id ?? null);
    }

    function drawStairBlock(ids: string[], hoodId: string | null) {
      const name = $("[data-stair-name]");
      const box = $("[data-stair]");
      const best = $("[data-best]");
      const bestCount = $("[data-best-count]");
      const prod = stairFor ? productOf(stairFor) : null;
      if (name) name.textContent = prod?.name ?? DASH;
      $$("[data-event]").forEach((c) => c.setAttribute("aria-pressed", String(!!events[c.dataset.event as keyof StairEvents])));
      if (!box) return;
      if (!hoodId || !prod) {
        box.innerHTML = `<p class="lg-stair-note">${escape(t("stair.noBuilding"))}</p>`;
        if (best) best.innerHTML = "";
        if (bestCount) bestCount.textContent = "";
        return;
      }
      const stair = priceStair(data, prod.id, hoodId, events, { competitorPrice: plan.competitorPrice?.[prod.id], unitsAtEdge: unitsAtEdge(prod.id) ?? undefined });
      box.innerHTML = stair ? drawStair(stair, { product: prod.name, unitsAtEdge: unitsAtEdge(prod.id), words }) : "";
      if (best) {
        best.innerHTML = ids.map((id) => {
          const s = priceStair(data, id, hoodId, events, { competitorPrice: plan.competitorPrice?.[id], unitsAtEdge: unitsAtEdge(id) ?? undefined });
          const p = productOf(id)!;
          const value = !s || s.nothingToSell ? DASH : price(s.best.price);
          const week = s?.best.moneyWeek != null && !s.nothingToSell ? `${money(s.best.moneyWeek)}<sup class="lg-mark">${MARK.approximate}</sup>` : DASH;
          return `<div class="lg-al lg-best"><span>${escape(p.name)}</span><span class="lg-lead" aria-hidden="true"></span><span class="lg-val">${escape(value)}</span><span class="lg-val lg-best-week">${week}</span></div>`;
        }).join("");
      }
      if (bestCount) bestCount.textContent = String(ids.length);
    }

    root.addEventListener("input", (e) => {
      const input = e.target as HTMLInputElement;
      if (input.dataset.price) {
        const id = input.dataset.price;
        const raw = input.value.replace(/[^0-9.,]/g, "").replace(",", ".");
        const v = raw === "" ? NaN : Number(raw);
        set(() => { if (Number.isFinite(v) && v >= 0) plan.prices[id] = Math.round(v * 100) / 100; else delete plan.prices[id]; });
      } else if (input.dataset.competitor != null) {
        const id = stairFor;
        if (!id) return;
        const raw = input.value.replace(/[^0-9.,]/g, "").replace(",", ".");
        const v = raw === "" ? NaN : Number(raw);
        set(() => {
          const c = { ...(plan.competitorPrice ?? {}) };
          if (Number.isFinite(v) && v > 0) c[id] = Math.round(v * 100) / 100; else delete c[id];
          if (Object.keys(c).length) plan.competitorPrice = c; else delete plan.competitorPrice;
        });
      } else if (input.dataset.staffHours || input.dataset.staffWage) {
        const id = input.dataset.staffHours || input.dataset.staffWage!;
        const field = input.dataset.staffHours ? "hours" : "wage";
        const raw = input.value.replace(/[^0-9.,]/g, "").replace(",", ".");
        const v = raw === "" ? NaN : Number(raw);
        set(() => {
          const staff = { ...(plan.staff ?? {}) };
          const line = { ...(staff[id] ?? {}) };
          if (Number.isFinite(v) && v >= 0) line[field] = field === "hours" ? Math.round(v) : Math.round(v * 100) / 100;
          else delete line[field];
          if (Object.keys(line).length) staff[id] = line; else delete staff[id];
          if (Object.keys(staff).length) plan.staff = staff; else delete plan.staff;
        });
      }
    });

    root.addEventListener("click", (e) => {
      const target = e.target as HTMLElement;
      const edge = target.closest<HTMLElement>("[data-edge]");
      if (edge) { const id = edge.dataset.edge!; set(() => { delete plan.prices[id]; }); return; }
      const sf = target.closest<HTMLElement>("[data-stair-for]");
      if (sf) { stairFor = sf.dataset.stairFor!; drawAll(); return; }
      const ev = target.closest<HTMLElement>("[data-event]");
      if (ev) {
        const k = ev.dataset.event as keyof StairEvents;
        events[k] = !events[k];
        drawAll();
        return;
      }
      const add = target.closest<HTMLElement>("[data-stock]");
      if (add) { const id = add.dataset.stock!; set(() => { plan.products = [...stocked(), id]; }); return; }
      const drop = target.closest<HTMLElement>("[data-unstock]");
      if (drop) {
        const id = drop.dataset.unstock!;
        set(() => { plan.products = stocked().filter((x) => x !== id); delete plan.prices[id]; });
        return;
      }
    });

    // ── Fixtures ──────────────────────────────────────────────────────
    function fixtureList(type: BusinessType): { id: string; required: string | null; neededBy: string | null }[] {
      const out = new Map<string, { id: string; required: string | null; neededBy: string | null }>();
      const add = (id: string, required: string | null = null, neededBy: string | null = null) => {
        if (!fixtureOf(id)) return;
        const had = out.get(id);
        if (!had) out.set(id, { id, required, neededBy });
        else { had.required ??= required; had.neededBy ??= neededBy; }
      };
      for (const group of type.requires) for (const id of alts(group)) add(id, group);
      for (const pid of stocked()) for (const d of productOf(pid)?.displays ?? []) add(d.fixture);
      for (const id of Object.keys(plan.fixtures)) add(id);
      for (const f of [...out.values()]) {
        const fx = fixtureOf(f.id);
        if (fx?.needs) for (const id of alts(fx.needs)) add(id, null, f.id);
      }
      return [...out.values()];
    }

    function fixtureNote(id: string): string {
      const f = fixtureOf(id)!;
      const parts: string[] = [];
      if (f.customersPerHour != null) parts.push(tf("fixture.serves", { n: f.customersPerHour }));
      const holds = stocked().flatMap((pid) => (productOf(pid)?.displays ?? [])
        .filter((d) => d.fixture === id)
        .map((d) => (d.units != null ? tf("fixture.holdsUnits", { n: d.units, product: productOf(pid)!.name.toLowerCase() }) : productOf(pid)!.name.toLowerCase())));
      if (holds.length) parts.push(tf("fixture.holds", { list: listed(holds, t("and")) }));
      if (f.needs) parts.push(tf("fixture.standsOn", { x: listed(alts(f.needs).map((x) => articled(fixtureOf(x)?.name ?? x)), t("or")) }));
      parts.push(tf("fixture.store", { store: f.store }));
      return capital(parts.join(" · "));
    }

    function drawFixtures() {
      const type = typeOf(plan.typeId);
      const box = $("[data-fixtures]");
      const none = $("[data-fixtures-none]");
      if (none) none.hidden = !!type;
      if (!box) return;
      const list = type ? fixtureList(type) : [];
      keyed(box, list.map((f) => f.id).join(","), () => list.map((f) => {
        const fx = fixtureOf(f.id)!;
        const others = f.required ? alts(f.required).filter((x) => x !== f.id).map((x) => fixtureOf(x)?.name.toLowerCase() ?? x) : [];
        const tag = f.required ? (others.length ? tf("fixture.requiredOr", { other: listed(others, t("or")) }) : t("fixture.required"))
          : f.neededBy ? tf("fixture.neededBy", { by: (fixtureOf(f.neededBy)?.name ?? f.neededBy).toLowerCase() }) : "";
        return `<div class="lg-row" data-fixture="${escape(f.id)}">
          <span class="lg-stepper">
            <button type="button" class="lg-step" data-dec="${escape(f.id)}" aria-label="${escape(tf("fixture.fewer", { name: fx.name.toLowerCase() }))}">−</button>
            <span class="lg-step-value" data-n>0</span>
            <button type="button" class="lg-step" data-inc="${escape(f.id)}" aria-label="${escape(tf("fixture.more", { name: fx.name.toLowerCase() }))}">+</button>
          </span>
          <span class="lg-row-main">
            <span class="lg-row-title"><span class="lg-row-name">${escape(fx.name)}</span>${tag ? `<span class="lg-row-tag" ${f.required ? "data-required" : ""}>${escape(tag)}</span>` : ""}</span>
            <span class="lg-row-line" data-fixture-note></span>
          </span>
          <span class="lg-row-right" data-line-total></span>
        </div>`;
      }).join(""));
      for (const row of $$("[data-fixture]", box)) {
        const id = row.dataset.fixture!;
        const fx = fixtureOf(id)!;
        const n = Math.max(0, Math.floor(plan.fixtures[id] ?? 0));
        $("[data-n]", row)!.textContent = String(n);
        ($("[data-dec]", row) as HTMLButtonElement).disabled = n === 0;
        $("[data-fixture-note]", row)!.textContent = fixtureNote(id);
        $("[data-line-total]", row)!.textContent = n ? tf("fixture.lineTotal", { n, each: money(fx.price), total: money(n * fx.price) }) : DASH;
      }
      const s = rk.setup;
      const put = (sel: string, v: string) => { const el = $(sel); if (el) el.textContent = v; };
      put("[data-setup-fixtures]", money(s.fixtures.value));
      put("[data-setup-deposit]", money(s.deposit.value));
      put("[data-setup-total]", money(s.total.value));
      const note = $("[data-fixtures-note]");
      if (note) {
        const b = buildingOf(plan.buildingId);
        note.textContent = b?.capacity != null ? tf("fixtures.noteCapacity", { n: b.capacity }) : t("fixtures.note");
      }
    }

    root.addEventListener("click", (e) => {
      const target = e.target as HTMLElement;
      const inc = target.closest<HTMLElement>("[data-inc]");
      const dec = target.closest<HTMLElement>("[data-dec]");
      if (inc || dec) {
        const id = (inc ?? dec)!.dataset[inc ? "inc" : "dec"]!;
        set(() => {
          const n = Math.max(0, Math.floor(plan.fixtures[id] ?? 0) + (inc ? 1 : -1));
          if (n) plan.fixtures[id] = n; else delete plan.fixtures[id];
        });
      }
    });

    // ── Hours and staff ──────────────────────────────────────────────
    function stationRoleId(type: BusinessType): string | null {
      const req = new Set(type.requires.flatMap(alts));
      for (const r of type.staff) {
        const role = roleOf(r);
        if (role && alts(role.station).some((s) => req.has(s))) return r;
      }
      return null;
    }

    function drawHours() {
      painter?.update(plan.hours);
      grid?.update(rk, plan.hours);
      const note = $("[data-hours-note]");
      if (note) note.textContent = tf("hours.note", { open: openHours(), reg: registerHours() });
      const box = $("[data-staff]");
      const type = typeOf(plan.typeId);
      if (!box) return;
      if (!type) { box.innerHTML = ""; box.dataset.key = ""; return; }
      const station = stationRoleId(type);
      const roles = [...new Set([...type.staff, ...Object.keys(plan.staff ?? {})])].filter((r) => roleOf(r));
      const mult = Number(difficulty()?.salaryMultiplier ?? 1);
      keyed(box, `${type.id}|${roles.join(",")}|${ctx.difficulty}`, () => roles.map((r) => {
        const role = roleOf(r)!;
        const isStation = r === station;
        return `<div class="lg-row" data-staff-row="${escape(r)}">
          <span class="lg-row-main">
            <span class="lg-row-name">${escape(role.name)}</span>
            <span class="lg-row-line" data-staff-line></span>
          </span>
          ${isStation ? "" : `<label class="lg-money"><input class="lg-input" type="text" inputmode="numeric" autocomplete="off" placeholder="${DASH}"
            data-staff-hours="${escape(r)}" aria-label="${escape(tf("staff.hoursAria", { name: role.name }))}"><span>${escape(t("staff.hoursUnit"))}</span></label>`}
          <label class="lg-money"><span>$</span><input class="lg-input" type="text" inputmode="decimal" autocomplete="off"
            placeholder="${escape((role.baseWage * mult).toFixed(2))}" data-staff-wage="${escape(r)}"
            aria-label="${escape(tf("staff.wageAria", { name: role.name }))}"></label>
          <span class="lg-yours" data-staff-yours hidden>${escape(t("yours"))}</span>
        </div>`;
      }).join(""));
      for (const row of $$("[data-staff-row]", box)) {
        const r = row.dataset.staffRow!;
        const line = plan.staff?.[r] ?? {};
        const hoursIn = $<HTMLInputElement>("[data-staff-hours]", row);
        const wageIn = $<HTMLInputElement>("[data-staff-wage]", row)!;
        if (hoursIn && document.activeElement !== hoursIn) hoursIn.value = line.hours != null ? String(line.hours) : "";
        if (document.activeElement !== wageIn) wageIn.value = line.wage != null ? String(line.wage) : "";
        wageIn.classList.toggle("lg-typed", line.wage != null);
        $("[data-staff-yours]", row)!.hidden = line.wage == null;
        const isStation = r === station;
        $("[data-staff-line]", row)!.textContent = isStation
          ? tf("staff.station", { h: registerHours() })
          : line.hours ? tf("staff.hours", { h: line.hours }) : t("staff.none");
      }
    }

    root.addEventListener("click", (e) => {
      if ((e.target as HTMLElement).closest("[data-open-usual]")) {
        set(() => { plan.hours = Array.from({ length: DAYS }, () => Array.from({ length: HOURS }, (_, h) => (h >= 9 && h < 21 ? Math.max(1, painter?.brush() || 1) : 0))); });
      }
      if ((e.target as HTMLElement).closest("[data-close-all]")) set(() => { plan.hours = emptyHours(); });
    });

    // ── Campaigns ─────────────────────────────────────────────────────
    function drawCampaigns() {
      const box = $("[data-campaigns]");
      if (!box) return;
      const b = buildingOf(plan.buildingId);
      const hood = b ? hoodOf(b.neighbourhood) : null;
      const note = $("[data-campaigns-note]");
      if (note) note.textContent = hood ? tf("campaigns.note", { x: factor(hood.marketingStrength), hood: hood.name }) : t("campaigns.noteNone");
      keyed(box, data.campaigns.map((c) => c.id).join(","), () => data.campaigns.map((c) => `
        <button type="button" class="lg-toggle" role="switch" aria-checked="false" data-campaign="${escape(c.id)}">
          <span class="lg-pill" aria-hidden="true"></span>
          <span class="lg-row-main"><span class="lg-row-name">${escape(c.name)}</span>
            <span class="lg-row-line">${escape(tf("campaigns.line", { agency: c.agency ?? c.kind, reach: count(c.reach) }))}</span></span>
          <span class="lg-row-right" data-campaign-figs></span>
        </button>`).join(""));
      const counted = rk.state === "ok";
      const base = counted ? rk.customers.value ?? 0 : 0;
      for (const row of $$("[data-campaign]", box)) {
        const id = row.dataset.campaign!;
        const on = !!plan.campaigns[id];
        row.setAttribute("aria-checked", String(on));
        const c = data.campaigns.find((x) => x.id === id)!;
        let added = "";
        if (counted) {
          const other = reckon(data, { ...plan, campaigns: { ...plan.campaigns, [id]: !on } }, ctx);
          const diff = on ? base - (other.customers.value ?? 0) : (other.customers.value ?? 0) - base;
          added = ` · ${tf("campaigns.adds", { n: count(diff) })}<sup class="lg-mark">${MARK.approximate}</sup>`;
        }
        $("[data-campaign-figs]", row)!.innerHTML = `${escape(tf("campaigns.cost", { x: money(c.costDay) }))}${added}`;
      }
    }

    root.addEventListener("click", (e) => {
      const c = (e.target as HTMLElement).closest<HTMLElement>("[data-campaign]");
      if (!c) return;
      const id = c.dataset.campaign!;
      set(() => {
        const next = { ...plan.campaigns };
        if (next[id]) delete next[id]; else next[id] = true;
        plan.campaigns = next;
      });
    });

    // ── Assumptions ───────────────────────────────────────────────────
    function drawAssumptions() {
      const v = $("[data-sat-value]");
      if (v) {
        v.textContent = tf("assume.percent", { n: plan.satisfaction });
        v.classList.toggle("lg-typed", plan.satisfactionTyped);
      }
      const typed = $("[data-sat-typed]");
      if (typed) typed.hidden = !plan.satisfactionTyped;
      ($("[data-sat-dec]") as HTMLButtonElement | null)?.toggleAttribute("disabled", plan.satisfaction <= 0);
      ($("[data-sat-inc]") as HTMLButtonElement | null)?.toggleAttribute("disabled", plan.satisfaction >= 100);
      const demand = $("[data-demand]");
      if (demand) demand.textContent = tf("assume.demandValue", { n: DEFAULT_DEMAND });
      const prod = stairFor ?? stocked()[0] ?? null;
      stairFor = prod;
      const help = $("[data-comp-help]");
      const input = $<HTMLInputElement>("[data-competitor]");
      if (help) help.textContent = prod ? tf("assume.compHelp", { product: productOf(prod)!.name }) : t("assume.compNone");
      if (input) {
        input.disabled = !prod;
        const c = prod ? plan.competitorPrice?.[prod] : undefined;
        if (document.activeElement !== input) input.value = c != null ? String(c) : "";
        input.classList.toggle("lg-typed", c != null);
      }
    }

    root.addEventListener("click", (e) => {
      const target = e.target as HTMLElement;
      if (target.closest("[data-sat-dec]")) set(() => { plan.satisfaction = Math.max(0, plan.satisfaction - 5); plan.satisfactionTyped = plan.satisfaction !== DEFAULT_SATISFACTION; });
      else if (target.closest("[data-sat-inc]")) set(() => { plan.satisfaction = Math.min(100, plan.satisfaction + 5); plan.satisfactionTyped = plan.satisfaction !== DEFAULT_SATISFACTION; });
      else if (target.closest("[data-sat-reset]")) set(() => { plan.satisfaction = DEFAULT_SATISFACTION; plan.satisfactionTyped = false; });
    });

    // ── Review ────────────────────────────────────────────────────────
    function almanac(rows: [string, string][]): string {
      return rows.map(([a, b]) => `<div class="lg-al"><span>${escape(a)}</span><span class="lg-lead" aria-hidden="true"></span><span class="lg-val">${b}</span></div>`).join("");
    }

    function drawReview() {
      const type = typeOf(plan.typeId);
      const b = buildingOf(plan.buildingId);
      const lines = $("[data-review-lines]");
      const approx = `<sup class="lg-mark">${MARK.approximate}</sup>`;
      const w = rk.week;
      const out = w.total.lines.filter((l) => l.op === "−").reduce((a, l) => a + (l.value ?? 0), 0);
      const fixtures = Object.entries(plan.fixtures).filter(([, n]) => n > 0);
      const groups: { label: string; count?: string; rows: [string, string][] }[] = [
        { label: t("review.business"), rows: [
          [t("review.type"), escape(type?.name ?? DASH)],
          [t("review.building"), escape(b?.address ?? DASH)],
          [t("review.layout"), escape(b ? [b.layout, `${count(b.sqm)} m²`, b.capacity != null ? tf("review.perHour", { n: b.capacity }) : null].filter(Boolean).join(" · ") : DASH)],
        ] },
        { label: t("review.products"), count: String(stocked().length), rows: stocked().map((id) => {
          const line = rk.products.find((p) => p.id === id);
          const v = plan.prices[id] ?? line?.price ?? null;
          return [productOf(id)!.name, escape(price(v))] as [string, string];
        }) },
        { label: t("review.fixtures"), count: String(fixtures.length), rows: fixtures.map(([id, n]) =>
          [tf("review.times", { name: fixtureOf(id)?.name ?? id, n }), escape(money(n * (fixtureOf(id)?.price ?? 0)))] as [string, string]) },
        { label: t("review.hours"), rows: [
          [t("review.openHours"), escape(tf("review.h", { n: openHours() }))],
          [t("review.registerHours"), escape(tf("review.h", { n: registerHours() }))],
          [t("review.campaigns"), escape(String(data.campaigns.filter((c) => plan.campaigns[c.id]).length))],
          [t("review.satisfaction"), escape(tf("assume.percent", { n: plan.satisfaction }))],
        ] },
        { label: t("review.week"), rows: [
          [t("review.moneyIn"), w.moneyIn.value != null ? `${escape(money(w.moneyIn.value))}${approx}` : DASH],
          [t("review.moneyOut"), w.total.value != null ? escape(`−${money(out)}`) : DASH],
          [t("review.theWeek"), w.total.value != null ? `${escape(money(w.total.value))}${approx}${w.loss ? ` <span class="lg-loss">${escape(t("loss"))}</span>` : ""}` : DASH],
          [t("review.setup"), escape(money(rk.setup.total.value))],
          [t("review.payback"), rk.paybackDays.value != null ? `${escape(days(rk.paybackDays.value, t("unit.days")))}${approx}` : DASH],
        ] },
      ];
      if (lines) lines.innerHTML = groups.filter((g) => g.rows.length).map((g) => `
        <div class="lg-review-group">
          <div class="lg-group-head"><span class="gd-eyebrow">${escape(g.label)}</span><span class="lg-count">${escape(g.count ?? "")}</span></div>
          ${almanac(g.rows)}
        </div>`).join("");

      const before = $("[data-before]");
      const note = $("[data-review-note]");
      const saved = $("[data-saved]");
      const keepOut = $("[data-keep-out]");
      const keepIn = $("[data-keep-in]");
      const noLedger = $("[data-keep-none]");
      if (saved) {
        saved.hidden = !savedNote;
        const s = $("[data-note-rows]", saved);
        if (s) s.innerHTML = savedNote ? `<span class="lg-note-text" style="grid-column:1/-1">${escape(savedNote)}</span>` : "";
      }
      if (keepOut) keepOut.hidden = state.signedIn;
      if (keepIn) keepIn.hidden = !state.signedIn || !!business || !state.ledgers.length;
      if (noLedger) noLedger.hidden = !state.signedIn || !!business || !!state.ledgers.length;
      if (!state.signedIn) {
        if (before) before.hidden = true;
        if (note) { note.hidden = false; note.textContent = t("review.signedOut"); }
        return;
      }
      if (!business) {
        if (before) before.hidden = true;
        if (note) note.hidden = true;
        return;
      }
      const changes = planChanges(data, kept, plan, words);
      if (before) {
        before.hidden = !changes.length;
        const head = $("[data-note-head]", before);
        if (head) head.textContent = tf(business.opened ? "before.opened" : "before.kept", { name: business.name, ledger: ledger()?.name ?? "" });
        const rows = $("[data-note-rows]", before);
        if (rows) rows.innerHTML = drawNoteRows(changes);
        const cmp = $("[data-compare]", before);
        if (cmp) cmp.innerHTML = drawCompare(compareRows(rkKept, rk, words),
          { row: t("compare.row"), before: t("compare.before"), after: t("compare.after"), change: t("compare.change") });
      }
      if (note) { note.hidden = !!changes.length || !!savedNote; note.textContent = t("review.unchanged"); }
    }

    function refuse(rows: { path: string; text: string }[]) {
      const box = $("[data-refusal]");
      if (!box) return;
      box.hidden = !rows.length;
      const at = $("[data-note-rows]", box);
      if (at) at.innerHTML = drawNoteRows(rows);
    }

    async function send(path: string, method: string, body: unknown): Promise<{ ok: boolean; body: any }> {
      try {
        const r = await fetch(path, { method, credentials: "same-origin", headers: { "content-type": "application/json", accept: "application/json" }, body: JSON.stringify(body) });
        const said = await r.json().catch(() => null);
        return { ok: r.ok, body: said };
      } catch {
        return { ok: false, body: null };
      }
    }

    root.addEventListener("click", async (e) => {
      const target = e.target as HTMLElement;
      if (target.closest("[data-keep]")) {
        const name = ($<HTMLInputElement>("[data-keep-name]")?.value ?? "").trim();
        const lid = Number($<HTMLSelectElement>("[data-keep-ledger]")?.value || ledgerId || 0);
        if (!name) { refuse([{ path: t("refuse.namePath"), text: t("refuse.name") }]); return; }
        if (!lid) { refuse([{ path: t("refuse.ledgerPath"), text: t("refuse.ledger") }]); return; }
        refuse([]);
        const said = await send(`/api/ledger/ledgers/${lid}/businesses`, "POST", { name, plan });
        if (!said.ok || !said.body?.id) {
          refuse([{ path: t("refuse.keepPath"), text: typeof said.body?.detail === "string" ? said.body.detail : t("refuse.failed") }]);
          return;
        }
        business = { id: said.body.id, name: said.body.name, ledgerId: lid, opened: !!said.body.opened, plan: clone(plan), keptPlan: clone(plan) };
        kept = clone(plan);
        ledgerId = lid;
        savedNote = tf("saved.kept", { name: business.name, ledger: ledger()?.name ?? "" });
        try { sessionStorage.removeItem(DRAFT_KEY); } catch { /* nothing kept */ }
        const url = new URL(window.location.href);
        url.searchParams.set("business", String(business.id));
        url.searchParams.delete("draft");
        history.replaceState(null, "", url);
        reckonAll();
        return;
      }
      if (target.closest("[data-save]") && business) {
        const rows = planChanges(data, kept, plan, words);
        const said = await send(`/api/ledger/businesses/${business.id}`, "PUT", { plan, keptPlan: plan });
        if (!said.ok) {
          refuse([{ path: t("refuse.savePath"), text: typeof said.body?.detail === "string" ? said.body.detail : t("refuse.failed") }]);
          return;
        }
        refuse([]);
        kept = clone(plan);
        savedNote = savedSentence(rows, words);
        reckonAll();
        return;
      }
      if (target.closest("[data-put-back]") && kept) {
        savedNote = "";
        set(() => { plan = clone(kept!); });
      }
    });

    root.addEventListener("change", (e) => {
      const sel = e.target as HTMLSelectElement;
      if (sel.matches("[data-keep-ledger]")) {
        ledgerId = Number(sel.value) || null;
        ctx = ctxOf();
        reckonAll();
      }
    });

    // ── the rail and the section buttons ─────────────────────────────
    root.addEventListener("click", (e) => {
      const target = e.target as HTMLElement;
      const row = target.closest<HTMLElement>("[data-go]");
      if (row) { go(row.dataset.go as SectionId); return; }
      const i = SECTIONS.indexOf(section);
      if (target.closest("[data-prev]") && i > 0) go(SECTIONS[i - 1]);
      else if (target.closest("[data-next]") && i < SECTIONS.length - 1) go(SECTIONS[i + 1]);
    });

    reckonAll();
  }
}
