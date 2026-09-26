/* The Ledger's seven overlay elements, drawn into a slot (README §3, A1).
 *
 * Called from drawElement (overlay-elements.ts), so the single source
 * (/overlay/ledger) and a layout (/overlay/guide-layout) draw them the same
 * way. The frame is the server's (ledger_stream.frame); the limit sentence and
 * the plan on stream are reckoned HERE, in the browser, with the planner's own
 * engine, from the game's data pack fetched once per page.
 *
 * ⚠ Figures change in one frame. No count-up, no flash, no colour for better
 * or worse: a loss is the sign and the word. The only timed things are the
 * mono line (2 s: the business on screen, a week written) and the plan's
 * change line (8 s), and under Still neither is said.
 *
 * ⚠ Nothing drawn means the empty frame: the theme's dim panel, no text, no
 * dot, no motion. It never says waiting or connecting.
 */
import type { LedgerData } from "./ledger/types";
import {
  WORDS, type LedgerFrame, type Words, changeLine, dataLine, figure, isLoss, onScreenMoved, onScreenOf,
  planView, plateMeasure, plateRows, reckonSafely, streamLimit, weekLabel, weekWritten,
} from "./ledger/stream";
import { fill } from "./ledger/engine";

export const LEDGER_KINDS = ["ledger-plate", "ledger-card", "ledger-strip", "ledger-limit", "ledger-counter", "ledger-plan-panel", "ledger-plan-card"];
const PLAN_KINDS = ["ledger-plan-panel", "ledger-plan-card"];

const esc = (s: unknown) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

interface Opts { still: boolean; reduced: boolean; line?: HTMLElement | null; words?: Words }

// ── the data pack, once per page ─────────────────────────────────────────

let asked: Promise<LedgerData | null> | null = null;
function pack(): Promise<LedgerData | null> {
  if (!asked) {
    asked = fetch("/api/ledger/data", { headers: { accept: "application/json" } })
      .then(async (r) => (r.ok ? ((await r.json()) as LedgerData) : null))
      .then((d) => (d && Array.isArray(d.businessTypes) ? d : null))
      .catch(() => null);
    /* A pack that did not load is asked again at the next paint, not never. */
    asked.then((d) => { if (!d) window.setTimeout(() => { asked = null; }, 30_000); });
  }
  return asked;
}

/* The on-screen business's limit, reckoned once per plan. */
const limits = new Map<string, string>();
function limitOf(data: LedgerData | null, f: LedgerFrame, w: Words): string {
  if (!data || !f.onScreenPlan) return "";
  const key = JSON.stringify([f.onScreenPlan, f.ctx]);
  if (!limits.has(key)) {
    if (limits.size > 32) limits.clear();
    limits.set(key, streamLimit(reckonSafely(data, f.onScreenPlan, f.ctx)?.limit, w));
  }
  return limits.get(key)!;
}

// ── pieces ───────────────────────────────────────────────────────────────

const fig = (n: number | null | undefined, cls: string, w: Words) => {
  const dash = n == null;
  return `<span class="gov-mono ${cls}${dash ? " dash" : ""}">${esc(figure(n))}</span>${isLoss(n) ? `<span class="glg-loss">${esc(w.loss)}</span>` : ""}`;
};

const empty = (kind: string, extra = "") => `<div class="gov-plate glg glg-${kind.slice(7)} glg-empty${extra}" aria-hidden="true"></div>`;

function showLine(line: HTMLElement | null | undefined, text: string, ms = 2000) {
  if (!line) return;
  const anyLine = line as any;
  if (anyLine._t) window.clearTimeout(anyLine._t);
  line.textContent = text;
  line.hidden = false;
  anyLine._t = window.setTimeout(() => { line.hidden = true; anyLine._t = 0; }, ms);
}

// ── the elements ─────────────────────────────────────────────────────────

function plate(f: LedgerFrame, limit: string, w: Words): string {
  const list = f.businesses ?? [];
  const m = plateMeasure(f.company, list.length);
  const { shown, more } = plateRows(list, f.onScreen);
  const on = onScreenOf(f);
  const rows = shown.map((b) => `<div class="glg-row${b.id === f.onScreen ? " on" : ""}" style="height:${m.rowH}px">
      <span class="glg-who"><span class="glg-name">${esc(b.name)}</span><span class="glg-hood">${esc(b.neighbourhood)}</span></span>
      <span class="glg-rowfig">${fig(b.week == null ? null : b.total, "glg-fig", w)}</span></div>`).join("");
  return `<div class="gov-plate glg glg-plate${m.crowded ? " crowded" : ""}${m.long ? " long" : ""}">
    <span class="gov-eyebrow glg-eyebrow">${esc(w.plateEyebrow)}</span>
    <span class="glg-company" style="font-size:${m.nameSize}px">${esc(f.company)}</span>
    <div class="glg-weekblock"><span class="glg-weeklabel">${esc(weekLabel(f.week, w))}</span>
      <span class="glg-total">${fig(f.week ? f.week.total : null, "glg-bigfig", w)}</span></div>
    <div class="glg-rows">${rows}${more > 0 ? `<div class="glg-more">${esc(fill(w.more, { n: String(more) }))}</div>` : ""}</div>
    <div class="glg-double"></div>
    <div class="glg-foot">${on ? `<span class="glg-label">${esc(fill(w.limitLabel, { business: on.name }))}</span>
      <span class="glg-limit" style="-webkit-line-clamp:${m.clamp}">${esc(limit)}</span>` : ""}
      <span class="gov-mono glg-data">${esc(dataLine(f.game, false, w))}</span></div>
  </div>`;
}

function card(f: LedgerFrame, limit: string, w: Words): string {
  const on = onScreenOf(f)!;
  const line = [on.neighbourhood, on.week != null ? fill(w.weekShort, { n: String(on.week) }) : w.noWeekShort, f.company].filter(Boolean).join(" · ");
  return `<div class="gov-plate glg glg-card">
    <span class="gov-eyebrow glg-eyebrow">${esc(w.cardEyebrow)}</span>
    <div class="glg-head"><span class="glg-title">${esc(on.name)}</span><span class="glg-headfig">${fig(on.week == null ? null : on.total, "glg-fig54", w)}</span></div>
    <span class="glg-line">${esc(line)}</span>
    <span class="glg-limit">${esc(limit)}</span>
    <span class="gov-mono glg-data">${esc(dataLine(f.game, false, w))}</span>
  </div>`;
}

function strip(f: LedgerFrame, top: boolean, w: Words): string {
  const on = onScreenOf(f);
  return `<div class="gov-plate glg glg-strip${top ? " top" : ""}">
    <span class="glg-company">${esc(f.company)}</span>
    <span class="glg-week">${esc(f.week ? fill(w.weekShort, { n: String(f.week.n) }) : w.noWeekShort)}</span>
    <span class="glg-total">${fig(f.week ? f.week.total : null, "glg-fig44", w)}</span>
    <span class="glg-spacer"></span>
    ${on ? `<span class="glg-divider"></span>
    <span class="glg-on"><span class="glg-onword">${esc(w.onScreen)}</span><span class="glg-name">${esc(on.name)}</span>${fig(on.week == null ? null : on.total, "glg-fig36", w)}</span>` : ""}
  </div>`;
}

function limitLine(f: LedgerFrame, limit: string, w: Words): string {
  const on = onScreenOf(f)!;
  return `<div class="gov-plate glg glg-limit-line">
    <span class="glg-label">${esc(fill(w.limitLabel, { business: on.name }))}</span>
    <span class="glg-limit">${esc(limit)}</span>
  </div>`;
}

function counter(f: LedgerFrame, w: Words): string {
  return `<div class="gov-plate glg glg-counter">
    <span class="glg-label">${esc(weekLabel(f.week, w))}</span>
    <span class="glg-count">${fig(f.week ? f.week.total : null, "glg-fig72", w)}</span>
  </div>`;
}

function changeBox(slot: HTMLElement): string {
  const c = (slot as any)._chg;
  if (!c || Date.now() >= c.until) return "";
  return `<div class="glg-change${c.fading ? " fading" : ""}" data-change><span class="glg-changetext">${esc(c.text)}${c.caret ? `<span class="gov-mono glg-caret">${esc(c.caret)}</span>` : ""}</span></div>`;
}

function planPanel(slot: HTMLElement, data: LedgerData, f: LedgerFrame, w: Words): string {
  const live = f.live!;
  const v = planView(data, live.plan, live.name, f.ctx, w);
  if (!v) return empty("ledger-plan-panel");
  const grid = v.grid ? `<div class="glg-grid-block"><span class="glg-gridlabel">${esc(w.gridLabel)}</span>
      <div class="glg-grid">${v.grid.map((row) => `<div class="glg-gridrow">${row.map((c) =>
        `<span class="glg-cell${c.open ? " open" : ""}${c.open && c.held ? " held" : ""}"${c.open ? ` style="--lvl:${c.level}%"` : ""}></span>`).join("")}</div>`).join("")}</div>
      <div class="gov-mono glg-ticks"><span>00</span><span>06</span><span>12</span><span>18</span><span>24</span></div></div>` : "";
  return `<div class="gov-plate glg glg-plan-panel${v.long ? " long" : ""}">
    <span class="gov-eyebrow glg-eyebrow">${esc(w.planEyebrow)}</span>
    <span class="glg-title">${esc(v.title)}</span>
    <span class="glg-where">${esc(v.where)}</span>
    <div class="glg-weekrow"><span class="glg-weekword">${esc(w.theWeek)}</span><span class="glg-total">${fig(v.total, "glg-fig72", w)}</span></div>
    ${changeBox(slot)}
    <div class="glg-lines">
      <div class="glg-lineitem"><span>${esc(w.setup)}</span><span class="gov-mono${v.setup === "—" ? " dash" : ""}">${esc(v.setup)}</span></div>
      <div class="glg-lineitem"><span>${esc(w.payback)}</span><span class="gov-mono${v.payback === "—" ? " dash" : ""}">${esc(v.payback)}</span></div>
    </div>
    ${grid}
    <div class="glg-double"></div>
    <div class="glg-foot"><span class="glg-label">${esc(w.planLimitLabel)}</span><span class="glg-limit">${esc(v.limit)}</span>
      <span class="gov-mono glg-data">${esc(dataLine(f.game, true, w))}</span></div>
  </div>`;
}

function planCard(slot: HTMLElement, data: LedgerData, f: LedgerFrame, w: Words): string {
  const live = f.live!;
  const v = planView(data, live.plan, live.name, f.ctx, w);
  if (!v) return empty("ledger-plan-card");
  return `<div class="gov-plate glg glg-plan-card">
    <span class="gov-eyebrow glg-eyebrow">${esc(w.planEyebrow)}</span>
    <div class="glg-head"><span class="glg-title">${esc(v.title)}</span><span class="glg-headfig">${fig(v.total, "glg-fig54", w)}</span></div>
    <span class="glg-where">${esc(v.where)}</span>
    ${changeBox(slot)}
    <span class="glg-limit">${esc(v.limit)}</span>
  </div>`;
}

// ── the one entry point ──────────────────────────────────────────────────

export async function drawLedger(slot: HTMLElement, kind: string, prev: any, next: any, o: Opts): Promise<void> {
  const w = o.words ?? WORDS;
  const f: LedgerFrame | null = next && typeof next.company === "string" ? next : null;
  const p: LedgerFrame | null = prev && typeof prev.company === "string" ? prev : null;
  const top = slot.dataset.shows === "top";

  if (PLAN_KINDS.includes(kind)) {
    const anySlot = slot as any;
    const data = f?.live ? await pack() : null;
    if (!f?.live || !data) {
      /* Off, or nothing to reckon with: the empty frame at once, and the last plan is not kept. */
      if (anySlot._chgT) { window.clearTimeout(anySlot._chgT); anySlot._chgT = 0; }
      anySlot._chg = null;
      slot.innerHTML = empty(kind);
      return;
    }
    /* A2: a change arrives with a newer live clock. A new plan on stream carries none, so it says nothing. */
    const fresh = p?.live && f.live.change && f.live.updatedAt !== p.live.updatedAt;
    const said = fresh ? changeLine(f.live.change, w) : null;
    if (said && !o.still) {
      if (anySlot._chgT) window.clearTimeout(anySlot._chgT);
      anySlot._chg = { ...said, until: Date.now() + 8000, fading: false };
      const hide = () => { anySlot._chg = null; slot.querySelector("[data-change]")?.remove(); anySlot._chgT = 0; };
      anySlot._chgT = window.setTimeout(() => {
        if (o.reduced) { hide(); return; }
        /* Full: it fades out over 240 ms. */
        if (anySlot._chg) anySlot._chg.fading = true;
        slot.querySelector("[data-change]")?.classList.add("fading");
        anySlot._chgT = window.setTimeout(hide, 240);
      }, 8000);
    }
    slot.innerHTML = kind === "ledger-plan-panel" ? planPanel(slot, data, f, w) : planCard(slot, data, f, w);
    return;
  }

  if (!f) { slot.innerHTML = empty(kind, top ? " top" : ""); return; }
  const on = onScreenOf(f);
  const needsLimit = kind === "ledger-plate" || kind === "ledger-card" || kind === "ledger-limit";
  const data = needsLimit && on ? await pack() : null;
  const limit = limitOf(data, f, w);
  if (kind === "ledger-plate") slot.innerHTML = plate(f, limit, w);
  else if (kind === "ledger-card") slot.innerHTML = on ? card(f, limit, w) : empty(kind);
  else if (kind === "ledger-strip") slot.innerHTML = strip(f, top, w);
  else if (kind === "ledger-limit") slot.innerHTML = on && limit ? limitLine(f, limit, w) : empty(kind);
  else if (kind === "ledger-counter") slot.innerHTML = counter(f, w);

  /* README §2.6 and §2 (a week written): one frame, and under Full or Reduced a mono line for two seconds. */
  if (o.still || !o.line) return;
  const moved = kind === "ledger-counter" ? null : onScreenMoved(p, f);
  const written = weekWritten(p, f);
  if (moved) showLine(o.line, fill(w.lineSwitch, { business: moved }));
  else if (written != null) showLine(o.line, fill(w.lineWeek, { n: String(written) }));
}
