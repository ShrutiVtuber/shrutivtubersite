/* Places at /ledger/places: the building finder (handoff README §6, SPEC §3.8).
 *
 *   h1 Find a building · `N of 883`
 *   the index strip: the seven neighbourhoods as filter tiles, not a map
 *   chip rows: use · capacity · rank for
 *   the table: sort buttons with carets, a virtual list (56px rows on the
 *   desk, 88px at 390; only the rows in view ± 6 are drawn), scroll back to
 *   the top whenever a filter changes
 *   no results: the empty state, "Widen one filter."
 *   a row, or ?building=ID, opens the record drawer (lib/ledger/drawer.ts)
 *
 * The pure half (virtualWindow, placesRows, nextSort, hoodTiles, mixClasses)
 * has no DOM and is tested with `node --test`; `mountPlaces` draws.
 *
 * "Ranked for the plan in hand": the planner keeps its unsaved plan in
 * sessionStorage (planner.ts, DRAFT_KEY), and this page ranks for that plan
 * when it has a type. Without one, the rank chip says so and the table lists.
 *
 * ⚠ Every word comes from the page's say() strings (data-words), read by key.
 */
import type { BuildingUse, ClassId, Ctx, LedgerData, Plan, RankRow } from "./types.ts";
import { rankBuildings } from "./engine.ts";
import { count, DASH, escape, factor, fill, MARK, money } from "./format.ts";
import { fetchPack, type Words } from "./client.ts";
import { fullPlan } from "./stream.ts";
import { mountDrawer } from "./drawer.ts";

export const USES = ["any", "shop", "office", "warehouse", "home", "cinema", "theatre"] as const;
export type UseChip = typeof USES[number];
export const CAPS = [15, 30, 40, 75] as const;
export const OVERSCAN = 6;
export const ROW_DESK = 56;
export const ROW_PHONE = 88;
export const DRAFT_KEY = "ledger.plan.draft";

// ── the virtual window ─────────────────────────────────────────────────────

/** Which rows to draw: those in view plus `overscan` above and below. `end` is exclusive. */
export function virtualWindow(scrollTop: number, viewHeight: number, rowHeight: number, total: number, overscan = OVERSCAN):
  { start: number; end: number; height: number } {
  const rows = Math.max(0, Math.floor(total));
  const h = Math.max(1, rowHeight);
  const top = Math.max(0, scrollTop);
  const first = Math.floor(top / h);
  const last = Math.ceil((top + Math.max(0, viewHeight)) / h);
  const start = Math.min(rows, Math.max(0, first - overscan));
  const end = Math.min(rows, Math.max(start, last + overscan));
  return { start, end, height: rows * h };
}

// ── filters and sort ───────────────────────────────────────────────────────

export type SortKey = "address" | "capacity" | "traffic" | "rent" | "week";
export interface PlaceFilters {
  hood: string | null;
  use: UseChip;
  cap: number | null;
  rank: boolean;
  sort: SortKey | null;
  dir: 1 | -1;
}

export const defaultFilters = (): PlaceFilters => ({ hood: null, use: "shop", cap: null, rank: true, sort: null, dir: -1 });

/** Whether this plan can be ranked for: it needs a type. */
export const canRank = (plan: Plan | null | undefined): boolean => !!plan?.typeId;

/** The sort in force: the one chosen, else the planned week when ranking, else the address. */
export function sortInForce(f: PlaceFilters, ranking: boolean): { sort: SortKey; dir: 1 | -1 } {
  if (f.sort && (f.sort !== "week" || ranking)) return { sort: f.sort, dir: f.dir };
  return ranking ? { sort: "week", dir: -1 } : { sort: "address", dir: 1 };
}

/** A head pressed: the same key flips its direction; a new key starts where it reads best. */
export function nextSort(current: { sort: SortKey; dir: 1 | -1 }, key: SortKey): { sort: SortKey; dir: 1 | -1 } {
  if (current.sort === key) return { sort: key, dir: current.dir === 1 ? -1 : 1 };
  return { sort: key, dir: key === "address" ? 1 : -1 };
}

/** The rows the table lists, filtered and sorted by the engine (memoised there). */
export function placesRows(data: LedgerData, plan: Plan | null, ctx: Ctx, f: PlaceFilters): RankRow[] {
  const ranking = f.rank && canRank(plan);
  const { sort, dir } = sortInForce(f, ranking);
  return rankBuildings(data, plan ?? fullPlan(null), ctx, {
    neighbourhood: f.hood, use: f.use === "any" ? null : (f.use as BuildingUse), capacity: f.cap, rank: ranking, sort, dir,
  });
}

// ── the index strip ────────────────────────────────────────────────────────

/** The classes a neighbourhood's customers mostly are: a tenth or more, the largest first. */
export function mixClasses(mix: Record<ClassId, number>): ClassId[] {
  return (["working", "middle", "upper"] as ClassId[])
    .filter((c) => (mix?.[c] ?? 0) >= 0.1)
    .sort((a, b) => (mix[b] ?? 0) - (mix[a] ?? 0));
}

export type Level = "low" | "middling" | "high";
export interface HoodTile { id: string; name: string; count: number; accepts: number; mix: ClassId[]; rent: Level | null; ads: number }

const median = (xs: number[]): number | null => {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b);
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};

/**
 * One tile per neighbourhood: the count for the current use, the price its
 * customers accept (×, its price index), the class mix, the rent level (the
 * median rent a m² for this use, in thirds across the seven) and advertising ×.
 */
export function hoodTiles(data: LedgerData, use: UseChip): HoodTile[] {
  const fits = (u: string) => use === "any" || u === use;
  const perSqm = data.neighbourhoods.map((h) => median(data.buildings
    .filter((b) => b.neighbourhood === h.id && fits(b.use) && b.rentDay != null && b.sqm > 0)
    .map((b) => b.rentDay! / b.sqm)));
  const known = perSqm.map((v, i) => ({ v, i })).filter((x) => x.v != null).sort((a, b) => a.v! - b.v!);
  const level = new Map<number, Level>();
  known.forEach((x, pos) => level.set(x.i, pos < known.length / 3 ? "low" : pos >= (2 * known.length) / 3 ? "high" : "middling"));
  return data.neighbourhoods.map((h, i) => ({
    id: h.id, name: h.name,
    count: data.buildings.filter((b) => b.neighbourhood === h.id && fits(b.use)).length,
    accepts: h.priceIndex, mix: mixClasses(h.mix), rent: level.get(i) ?? null, ads: h.marketingStrength,
  }));
}

/** "middle and upper class" from the class words. */
export function mixWords(classes: ClassId[], w: { class: Record<ClassId, string>; and: string; template: string; none: string }): string {
  const names = classes.map((c) => w.class[c]);
  if (!names.length) return w.none;
  const list = names.length === 1 ? names[0] : `${names.slice(0, -1).join(", ")} ${w.and} ${names[names.length - 1]}`;
  return fill(w.template, { classes: list });
}

// ── the page ───────────────────────────────────────────────────────────────

interface PlacesState { ctx: Ctx; building: string | null; hood: string | null; use: string | null; cap: number | null }

export function mountPlaces(root: HTMLElement): void {
  let words: Words = {};
  let state: PlacesState;
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
    const type = plan?.typeId ? data.businessTypes.find((x) => x.id === plan!.typeId) ?? null : null;
    if (plan && !type) plan = { ...plan, typeId: null };

    const f = defaultFilters();
    if (state.hood && data.neighbourhoods.some((h) => h.id === state.hood)) f.hood = state.hood;
    if (state.use && (USES as readonly string[]).includes(state.use)) f.use = state.use as UseChip;
    else if (type?.uses[0] && (USES as readonly string[]).includes(type.uses[0])) f.use = type.uses[0] as UseChip;
    if (state.cap && (CAPS as readonly number[]).includes(state.cap)) f.cap = state.cap;

    const hoodName = (id: string | null) => (id ? data.neighbourhoods.find((h) => h.id === id)?.name ?? id : t("finder.anyHood"));
    const byId = new Map(data.buildings.map((b) => [b.id, b]));
    const phone = window.matchMedia("(max-width: 899px)");
    const scroller = $("[data-places-scroll]")!;
    const inner = $("[data-places-inner]")!;
    const table = $("[data-places-table]");
    const empty = $("[data-places-empty]");
    let rows: RankRow[] = [];
    let ranking = false;

    const drawerEl = $("[data-record-drawer]") ?? document.querySelector<HTMLElement>("[data-record-drawer]");
    const drawer = drawerEl ? mountDrawer(drawerEl, data) : null;

    function setUrl(p: { building?: string | null }) {
      const url = new URL(window.location.href);
      if (p.building !== undefined) { if (p.building) url.searchParams.set("building", p.building); else url.searchParams.delete("building"); }
      if (f.hood) url.searchParams.set("hood", f.hood); else url.searchParams.delete("hood");
      url.searchParams.set("use", f.use);
      if (f.cap) url.searchParams.set("cap", String(f.cap)); else url.searchParams.delete("cap");
      history.replaceState(history.state, "", url);
    }

    // ── the index strip and the chips ──
    function drawStrip() {
      const box = $("[data-hood-tiles]");
      if (!box) return;
      const tiles = hoodTiles(data, f.use);
      const things = t(`things.${f.use}`);
      const cw = { class: { working: t("class.working"), middle: t("class.middle"), upper: t("class.upper") }, and: t("and"), template: t("mix.template"), none: t("mix.none") };
      box.innerHTML = tiles.map((h) => `
        <button type="button" class="lp-tile" data-hood="${escape(h.id)}" aria-pressed="${f.hood === h.id}">
          <span class="lp-tile-name">${escape(h.name)}</span>
          <span class="lp-tile-count">${escape(tf("tile.count", { n: count(h.count), things }))}</span>
          <span class="lp-tile-accepts">${escape(tf("tile.accepts", { x: factor(h.accepts) }))}</span>
          <span class="lp-tile-mix">${escape(mixWords(h.mix, cw))}</span>
          <span class="lp-tile-rent">${escape(tf("tile.levels", { rent: h.rent ? t(`level.${h.rent}`) : DASH, ads: factor(h.ads) }))}</span>
        </button>`).join("");
    }

    function drawChips() {
      $$("[data-use]").forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.use === f.use)));
      $$("[data-cap]").forEach((c) => c.setAttribute("aria-pressed", String((c.dataset.cap ? Number(c.dataset.cap) : null) === f.cap)));
      const rank = $<HTMLButtonElement>("[data-rank]");
      if (rank) {
        rank.disabled = !type;
        rank.setAttribute("aria-pressed", String(!!type && f.rank));
        rank.textContent = type ? tf("finder.rankFor", { type: type.name }) : t("finder.rankNone");
      }
    }

    // ── the table ──
    function drawHeads() {
      const now = sortInForce(f, ranking);
      for (const h of $$("[data-sort]")) {
        const key = h.dataset.sort as SortKey;
        const on = now.sort === key;
        h.setAttribute("aria-sort", on ? (now.dir === 1 ? "ascending" : "descending") : "none");
        h.dataset.on = on ? "yes" : "no";
        const caret = $("[data-caret]", h);
        if (caret) caret.textContent = on ? (now.dir === 1 ? "▲" : "▼") : "";
        (h as HTMLButtonElement).disabled = key === "week" && !ranking;
      }
    }

    const rowH = () => (phone.matches ? ROW_PHONE : ROW_DESK);

    function rowHtml(r: RankRow, i: number): string {
      const b = byId.get(r.id)!;
      const top = i * rowH();
      const hood = hoodName(b.neighbourhood);
      const use = t(`use.${b.use}`);
      const area = tf("row.area", { n: count(b.sqm) });
      const meta = [hood, use, b.layout, area].filter(Boolean).join(" · ");
      const week = !ranking ? DASH : r.week != null ? `${escape(money(r.week))}<sup class="lg-mark">${MARK.approximate}</sup>` : escape(t("finder.cannotTrade"));
      const rent = b.rentDay != null ? money(b.rentDay) : DASH;
      const cap = b.capacity != null ? count(b.capacity) : DASH;
      const chosen = plan?.buildingId === b.id ? " data-chosen=\"yes\"" : "";
      if (phone.matches) {
        const phoneMeta = [b.layout, area, b.capacity != null ? tf("row.capacity", { n: b.capacity }) : null, tf("row.traffic", { n: b.traffic }),
          b.rentDay != null ? tf("row.rent", { x: rent }) : null].filter(Boolean).join(" · ");
        return `<button type="button" class="lp-row lp-row-phone" style="top:${top}px;height:${rowH()}px" data-read="${escape(b.id)}"${chosen}>
          <span class="lp-row-top"><span class="lp-addr">${escape(b.address)}</span><span class="lp-week">${ranking ? week : ""}</span></span>
          <span class="lp-hood">${escape(hood)}</span>
          <span class="lp-meta">${escape(phoneMeta)}</span>
        </button>`;
      }
      return `<div class="lp-row lp-grid" style="top:${top}px;height:${rowH()}px"${chosen}>
        <button type="button" class="lp-pick" data-read="${escape(b.id)}"><span class="lp-addr">${escape(b.address)}</span><span class="lp-meta">${escape(meta)}</span></button>
        <span class="lp-n">${escape(cap)}</span><span class="lp-n">${escape(count(b.traffic))}</span><span class="lp-n">${escape(rent)}</span>
        <span class="lp-n">${week}</span>
        <button type="button" class="lg-link lp-read" data-read="${escape(b.id)}" tabindex="-1">${escape(t("finder.read"))}</button>
      </div>`;
    }

    let drawn = "";
    function drawWindow(force = false) {
      const w = virtualWindow(scroller.scrollTop, scroller.clientHeight || (phone.matches ? 520 : 600), rowH(), rows.length);
      const key = `${w.start}:${w.end}:${rowH()}`;
      if (!force && key === drawn) return;
      drawn = key;
      inner.style.height = `${w.height}px`;
      inner.innerHTML = rows.slice(w.start, w.end).map((r, k) => rowHtml(r, w.start + k)).join("");
    }

    function reflow() {
      ranking = f.rank && canRank(plan);
      rows = placesRows(data, plan, state.ctx, f);
      const countEl = $("[data-places-count]");
      if (countEl) countEl.textContent = tf(ranking ? "count.ranked" : "count", { n: count(rows.length), of: count(data.buildings.length) });
      if (empty) {
        empty.hidden = rows.length > 0;
        const body = $(".gd-empty p", empty);
        if (body) body.textContent = f.cap != null
          ? tf("empty.bodyCap", { hood: hoodName(f.hood), cap: f.cap })
          : tf("empty.bodyUse", { hood: hoodName(f.hood), things: t(`things.${f.use}`) });
      }
      if (table) table.hidden = rows.length === 0;
      drawStrip();
      drawChips();
      drawHeads();
      scroller.scrollTop = 0; // a filter changed: back to the top
      drawWindow(true);
    }

    let raf = 0;
    scroller.addEventListener("scroll", () => {
      if (raf) return;
      raf = requestAnimationFrame(() => { raf = 0; drawWindow(); });
    }, { passive: true });
    phone.addEventListener("change", () => drawWindow(true));

    root.addEventListener("click", (e) => {
      const target = e.target as HTMLElement;
      const tile = target.closest<HTMLElement>("[data-hood]");
      if (tile) { const id = tile.dataset.hood!; f.hood = f.hood === id ? null : id; setUrl({}); reflow(); return; }
      const use = target.closest<HTMLElement>("[data-use]");
      if (use) { f.use = use.dataset.use as UseChip; setUrl({}); reflow(); return; }
      const cap = target.closest<HTMLElement>("[data-cap]");
      if (cap) { f.cap = cap.dataset.cap ? Number(cap.dataset.cap) : null; setUrl({}); reflow(); return; }
      if (target.closest("[data-rank]")) { f.rank = !f.rank; reflow(); return; }
      if (target.closest("[data-clear-filters]")) { f.hood = null; f.cap = null; f.use = "any"; setUrl({}); reflow(); return; }
      const head = target.closest<HTMLElement>("[data-sort]");
      if (head) {
        const next = nextSort(sortInForce(f, ranking), head.dataset.sort as SortKey);
        f.sort = next.sort; f.dir = next.dir;
        reflow();
        return;
      }
      const read = target.closest<HTMLElement>("[data-read]");
      if (read && drawer) { drawer.open(read.dataset.read!, read); setUrl({ building: read.dataset.read! }); }
    });

    drawer?.onClose(() => setUrl({ building: null }));
    reflow();
    if (state.building && byId.has(state.building)) drawer?.open(state.building, null);
  }
}
