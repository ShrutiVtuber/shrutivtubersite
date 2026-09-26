/* The record drawer: one building (handoff README §7; RecordDrawer.astro).
 *
 *   desk: fixed on the right, 420px, --surface-card, --shadow-3, padding 24,
 *         over a scrim of color-mix(--surface-inset 50%, transparent)
 *   390:  a bottom sheet, top at 22vh, radius 16 16 0 0
 *
 *   BUILDING · Close
 *   the address (EB Garamond 24/600), one sentence, a mono facts line
 *   The building: neighbourhood · floor area · capacity · traffic · rent ·
 *                 deposit · price customers accept × · advertising ×
 *   Rent or buy: rent a game year · price to buy · game years of rent the
 *                price equals, then the verdict on a left rule
 *   foot: the data line and **Plan a business here** (/ledger/plan?building=ID)
 *
 * A dialog: Escape and the scrim close it, focus goes to Close on opening
 * and back to what opened it on closing. `recordView` is pure (tested).
 */
import type { LedgerData } from "./types.ts";
import { rentOrBuy } from "./engine.ts";
import { count, DASH, escape, factor, fill, money } from "./format.ts";
import type { Words } from "./client.ts";
import { mixClasses, mixWords } from "./places.ts";

/** A game you will finish: past this many game years of rent, buying never repays inside one. */
export const FINISHABLE_YEARS = 100;

/** "A" or "An" before a layout code read letter by letter: an F2, a C2. */
export const layoutArticle = (layout: string): "a" | "an" => (/^[aefhilmnorsx]/i.test(layout.trim()) ? "an" : "a");

export interface RecordView {
  id: string;
  address: string;
  hood: string;
  use: string;
  layout: string | null;
  sqm: number;
  capacity: number | null;
  traffic: number;
  rentDay: number | null;
  deposit: number | null;
  accepts: number | null;
  ads: number | null;
  mix: ("working" | "middle" | "upper")[];
  rentYear: number | null;
  price: number | null;
  repayYears: number | null;
  /** The record's rent-or-buy sentence: repays after n years, and whether renting is plainly cheaper. */
  robKind: "not-for-rent" | "repays" | "repays-rent-cheaper";
}

export function recordView(data: LedgerData, id: string): RecordView | null {
  const b = data.buildings.find((x) => x.id === id);
  if (!b) return null;
  const h = data.neighbourhoods.find((x) => x.id === b.neighbourhood);
  const rob = rentOrBuy(data, b.id, 1);
  const ok = rob?.state === "ok";
  const repay = ok ? rob!.yearsToRepay.value : null;
  return {
    id: b.id, address: b.address, hood: h?.name ?? b.neighbourhood, use: b.use, layout: b.layout, sqm: b.sqm,
    capacity: b.capacity, traffic: b.traffic, rentDay: b.rentDay, deposit: b.deposit,
    accepts: h?.priceIndex ?? null, ads: h?.marketingStrength ?? null, mix: h ? mixClasses(h.mix) : [],
    rentYear: ok ? rob!.rentYear.value : null, price: ok ? rob!.price.value : null, repayYears: repay,
    robKind: !ok || repay == null ? "not-for-rent" : repay > FINISHABLE_YEARS ? "repays-rent-cheaper" : "repays",
  };
}

export interface DrawerView {
  open(id: string, opener?: HTMLElement | null): void;
  close(): void;
  onClose(fn: () => void): void;
}

export function mountDrawer(el: HTMLElement, data: LedgerData): DrawerView {
  let words: Words = {};
  try { words = JSON.parse(el.dataset.words || "{}"); } catch { words = {}; }
  const t = (k: string): string => (k in words ? words[k] : k);
  const tf = (k: string, p: Record<string, string | number>) => fill(t(k), Object.fromEntries(Object.entries(p).map(([a, b]) => [a, String(b)])));
  const $ = <T extends HTMLElement = HTMLElement>(sel: string) => el.querySelector<T>(sel);
  const panel = $("[data-drawer-panel]")!;
  const listeners: (() => void)[] = [];
  let back: HTMLElement | null = null;

  const almanac = (rows: [string, string][]) => rows.map(([a, b]) =>
    `<div class="lg-al"><span>${escape(a)}</span><span class="lg-lead" aria-hidden="true"></span><span class="lg-val">${escape(b)}</span></div>`).join("");

  function fillIn(v: RecordView) {
    const useWord = t(`noun.${v.use}`);
    const what = v.layout ? `${v.layout} ${useWord}` : useWord;
    const article = v.layout ? layoutArticle(v.layout) : /^[aeiou]/i.test(useWord) ? "an" : "a";
    const mix = mixWords(v.mix, { class: { working: t("class.working"), middle: t("class.middle"), upper: t("class.upper") }, and: t("and"), template: t("mix.template"), none: t("mix.none") });
    const put = (sel: string, text: string) => { const x = $(sel); if (x) x.textContent = text; };
    put("[data-drawer-address]", v.address);
    put("[data-drawer-line]", tf("line", { article: t(`article.${article}`), what, hood: v.hood, mix }).replace(/^./, (c) => c.toUpperCase()));
    put("[data-drawer-facts]", [v.layout, tf("facts.area", { n: count(v.sqm) }), v.capacity != null ? tf("facts.capacity", { n: v.capacity }) : null,
      tf("facts.traffic", { n: v.traffic })].filter(Boolean).join(" · "));
    const facts = $("[data-drawer-building]");
    if (facts) facts.innerHTML = almanac([
      [t("b.hood"), v.hood],
      [t("b.area"), tf("b.areaValue", { n: count(v.sqm) })],
      [t("b.capacity"), v.capacity != null ? tf("b.capacityValue", { n: v.capacity }) : DASH],
      [t("b.accepts"), factor(v.accepts)],
      [t("b.ads"), factor(v.ads)],
      [t("b.traffic"), count(v.traffic)],
      [t("b.rent"), v.rentDay != null ? tf("b.rentValue", { x: money(v.rentDay) }) : DASH],
      [t("b.deposit"), money(v.deposit)],
    ]);
    const rob = $("[data-drawer-rob]");
    if (rob) rob.innerHTML = v.robKind === "not-for-rent" ? "" : almanac([
      [t("rob.rentYear"), money(v.rentYear)],
      [t("rob.price"), money(v.price)],
      [t("rob.years"), tf("rob.yearsValue", { n: count(Math.ceil(v.repayYears ?? 0)) })],
    ]);
    const n = count(Math.ceil(v.repayYears ?? 0));
    put("[data-drawer-verdict]", v.robKind === "not-for-rent" ? t("rob.notForRent")
      : v.robKind === "repays-rent-cheaper" ? `${tf("rob.repays", { n })} ${t("rob.rentCheaper")}` : tf("rob.repays", { n }));
    const weigh = $<HTMLAnchorElement>("[data-drawer-weigh]");
    if (weigh) { weigh.href = `/ledger/calculators?building=${encodeURIComponent(v.id)}#rob`; weigh.hidden = v.robKind === "not-for-rent"; }
    const plan = $<HTMLAnchorElement>("[data-drawer-plan]");
    if (plan) plan.href = `/ledger/plan?building=${encodeURIComponent(v.id)}&section=building`;
    panel.setAttribute("aria-label", v.address);
  }

  function open(id: string, opener: HTMLElement | null = null) {
    const v = recordView(data, id);
    if (!v) return;
    fillIn(v);
    back = opener ?? (document.activeElement as HTMLElement | null);
    el.hidden = false;
    document.documentElement.dataset.drawer = "open";
    panel.scrollTop = 0;
    $<HTMLButtonElement>("[data-drawer-close]")?.focus();
  }

  function close() {
    if (el.hidden) return;
    el.hidden = true;
    delete document.documentElement.dataset.drawer;
    listeners.forEach((fn) => fn());
    if (back && document.contains(back)) back.focus();
    back = null;
  }

  el.addEventListener("click", (e) => {
    const target = e.target as HTMLElement;
    if (target.closest("[data-drawer-close]") || target.matches("[data-drawer-scrim]")) close();
  });
  document.addEventListener("keydown", (e) => {
    if (el.hidden) return;
    if (e.key === "Escape") { e.preventDefault(); close(); return; }
    if (e.key === "Tab") {
      // keep focus inside the dialog
      const focusable = [...panel.querySelectorAll<HTMLElement>("a[href]:not([hidden]), button:not([disabled])")].filter((x) => x.offsetParent !== null);
      if (!focusable.length) return;
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  return { open, close, onClose: (fn) => { listeners.push(fn); } };
}
