/* The planner's *Plan on stream* switch (overlays handoff A4–A6; Contract 4).
 *
 * Where: wide (≥ 900) at the right end of the sticky stats bar; narrow, a
 * fixed bottom bar 52px tall plus the safe area. `role="switch"`. Never red.
 *
 *   off             Plan on stream · off · chat sees nothing
 *   on              On stream · chat sees this plan       (accent wash, the now disc)
 *   nothing-minted  Plan on stream · no overlay minted yet (tap: the note, inline)
 *   signed-out      Plan on stream · needs an account      (tap: the note, inline)
 *   no-ledger       Plan on stream · no ledger chosen      (tap: the note, inline)
 *   checking        Plan on stream · off · chat sees nothing, while the
 *                   overlays of the ledger are asked for; a tap waits for them
 *
 * On: the plan goes to `PUT /api/ledger/ledgers/{id}/live` a moment after each
 * `ledger:plan` change (debounced ~300 ms), with `change: {label, delta}` —
 * the A2 sentence from `changeLabel()` against the plan last SENT, and the
 * planner's own reckoning of what it did to the week. When the plan is a
 * different plan (another business, or a draft kept as a business), the
 * change is omitted: the overlay redraws with no change line. The *Chat sees*
 * strip under the stats bar repeats exactly that line.
 *
 * Off: `DELETE …/live` at once; the overlay draws its empty frame.
 *
 * Leaving: on `pagehide` (and `beforeunload`) the switch sends the DELETE with
 * `keepalive`, best effort, and is sent again (PUT) if the page comes back
 * from the back-forward cache still on. ⚠ Signing out is not observable from
 * here: a sign-out in another tab, or a session that expires, leaves the last
 * plan live until this page is left or the switch goes off, and the overlay
 * keeps showing it. A sign-out in this tab navigates away, which is a pagehide.
 *
 * Needs a ledger: `?ledger=ID`, or the business's own ledger. With neither the
 * switch explains and offers the reader's ledgers (the note has the shape of
 * the nothing-minted note).
 *
 * The pure half (tap, noteFor, face, liveBody, debounce, isMinted) is tested
 * with `node --test`; `mountStreamSwitch` wires it to the page.
 *
 * ⚠ Every word comes from StreamSwitch.astro's say() strings (data-words).
 */
import type { LedgerData, Plan, Reckoning } from "./types.ts";
import { changeLabel, changeLine, WORDS as STREAM_WORDS } from "./stream.ts";
import { escape, fill } from "./format.ts";
import { fetchPack, type Words } from "./client.ts";

export const DEBOUNCE_MS = 300;
export const PLAN_KINDS = ["ledger-plan-panel", "ledger-plan-card"] as const;

export type SwitchState = "checking" | "signed-out" | "no-ledger" | "nothing-minted" | "off" | "on";
export type NoteKind = "signed-out" | "nothing-minted" | "no-ledger" | null;
export type Effect = "put" | "delete" | null;

/** What a tap does: the next state, whether the note is open, and what to send. */
export function tap(state: SwitchState, asked: boolean): { state: SwitchState; asked: boolean; effect: Effect } {
  switch (state) {
    case "on": return { state: "off", asked: false, effect: "delete" };
    case "off": return { state: "on", asked: false, effect: "put" };
    case "checking": return { state, asked: true, effect: null };
    // the three that cannot stream: the tap opens (or closes) the note that says why
    default: return { state, asked: !asked, effect: null };
  }
}

/** The inline note under the stats bar: only after a tap, and only for a state that cannot stream. */
export function noteFor(state: SwitchState, asked: boolean): NoteKind {
  if (!asked) return null;
  return state === "signed-out" || state === "nothing-minted" || state === "no-ledger" ? state : null;
}

/** The switch's two lines, as word keys, and whether it reads as on. */
export function face(state: SwitchState): { on: boolean; label: string; sub: string } {
  switch (state) {
    case "on": return { on: true, label: "label.on", sub: "sub.on" };
    case "signed-out": return { on: false, label: "label.off", sub: "sub.signedOut" };
    case "no-ledger": return { on: false, label: "label.off", sub: "sub.noLedger" };
    case "nothing-minted": return { on: false, label: "label.off", sub: "sub.noMint" };
    default: return { on: false, label: "label.off", sub: "sub.off" };
  }
}

/** Whether the ledger has a plan-on-stream overlay minted, from `GET …/overlays`. */
export const isMinted = (overlays: unknown): boolean =>
  Array.isArray(overlays) && overlays.some((o) => o && (PLAN_KINDS as readonly string[]).includes((o as { kind?: string }).kind ?? ""));

/** Which plan this is: a kept business, or the unsaved draft. A different key is a different plan. */
export const planKey = (business: number | null | undefined): string => (business ? `business:${business}` : "draft");

export interface Sent { key: string; plan: Plan; week: number | null }
export interface Next { key: string; plan: Plan; week: number | null; reckoning?: Reckoning | null }
export interface LiveBody { plan: Plan; name: string; change?: { label: string; delta: number | null } }

const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);

/**
 * The body of the next PUT, or null when there is nothing new to send.
 * The change is against the plan last sent (a burst of taps inside the
 * debounce reads as one change); it is left out for a first send and when
 * the plan is a different plan.
 */
export function liveBody(data: LedgerData, sent: Sent | null, next: Next, name: string, force = false,
  w: typeof STREAM_WORDS = STREAM_WORDS): LiveBody | null {
  const samePlan = !!sent && sent.key === next.key;
  if (samePlan && !force && same(sent!.plan, next.plan)) return null;
  const body: LiveBody = { plan: next.plan, name };
  if (samePlan && !same(sent!.plan, next.plan)) {
    const delta = sent!.week != null && next.week != null ? Math.round(next.week - sent!.week) : null;
    body.change = { label: changeLabel(data, sent!.plan, next.plan, next.reckoning ?? null, w), delta };
  }
  return body;
}

/** A debounce with its timers passed in, so a test can drive the clock. */
export function debounce(fn: () => void, ms = DEBOUNCE_MS,
  timers: { set: (f: () => void, ms: number) => unknown; clear: (h: unknown) => void } = { set: (f, m) => setTimeout(f, m), clear: (h) => clearTimeout(h as number) }) {
  let handle: unknown = null;
  return {
    call() { if (handle != null) timers.clear(handle); handle = timers.set(() => { handle = null; fn(); }, ms); },
    flush() { if (handle != null) { timers.clear(handle); handle = null; fn(); } },
    cancel() { if (handle != null) { timers.clear(handle); handle = null; } },
    get pending() { return handle != null; },
  };
}

// ── the page ───────────────────────────────────────────────────────────────

interface SwitchInit {
  signedIn: boolean;
  ledgerId: number | null;
  ledgerName: string;
  ledgers: { id: number; name: string }[];
  signInHref: string;
}

export function mountStreamSwitch(box: HTMLElement, planner: HTMLElement): void {
  let words: Words = {};
  let init: SwitchInit;
  try { words = JSON.parse(box.dataset.words || "{}"); } catch { words = {}; }
  try { init = JSON.parse(box.dataset.init || "{}"); } catch { return; }
  const t = (k: string): string => (k in words ? words[k] : k);
  const $ = <T extends HTMLElement = HTMLElement>(sel: string) => box.querySelector<T>(sel);
  /* The change sentences (A2) are the planner's say() strings: the overlay
     prints the label it is sent. The line around it ("{change} · the week
     +$n") is the overlay's own (stream.ts WORDS), so the strip uses that one
     unchanged and reads exactly as the overlay does. */
  const streamWords: typeof STREAM_WORDS = { ...STREAM_WORDS,
    ...Object.fromEntries(Object.keys(STREAM_WORDS).filter((k) => k.startsWith("ch") && `stream.${k}` in words).map((k) => [k, words[`stream.${k}`]])) };

  // Into the stats bar: the wide switch at the right end of its row, the strip and the note under it.
  const bar = planner.querySelector<HTMLElement>("[data-ledger-stats]");
  const wide = $("[data-switch-wide]");
  const under = $("[data-switch-under]");
  const row = bar?.querySelector(".sb-line-row");
  if (row && wide) row.appendChild(wide);
  if (bar && under) bar.appendChild(under);
  box.hidden = false;
  planner.classList.add("lg-has-switch");

  let ledgerId = init.ledgerId;
  let state: SwitchState = !init.signedIn ? "signed-out" : ledgerId ? "checking" : "no-ledger";
  let asked = false;
  let data: LedgerData | null = null;
  let latest: Next | null = null;
  let sent: Sent | null = null;
  let line: { text: string; caret: string } | null = null;
  let name = "";
  let away = false;

  const send = debounce(() => { void push(false); });

  async function call(method: "PUT" | "DELETE", body?: unknown, keepalive = false): Promise<number> {
    if (!ledgerId) return 0;
    try {
      const r = await fetch(`/api/ledger/ledgers/${ledgerId}/live`, {
        method, credentials: "same-origin", keepalive,
        headers: { "content-type": "application/json", accept: "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      return r.status;
    } catch { return 0; }
  }

  async function push(force: boolean) {
    if (state !== "on" || !latest || !data) return;
    const body = liveBody(data, sent, latest, name, force, streamWords);
    if (!body) return;
    const was = latest;
    const status = await call("PUT", body);
    if (status >= 200 && status < 300) {
      sent = { key: was.key, plan: was.plan, week: was.week };
      line = body.change ? changeLine(body.change, STREAM_WORDS) : null;
      draw();
    } else if (status === 401 || status === 403 || status === 404) {
      // the ledger or the session is gone: the switch goes off, quietly
      state = "off"; sent = null; line = null; draw();
    }
  }

  async function checkMinted() {
    if (!init.signedIn || !ledgerId) return;
    try {
      const r = await fetch(`/api/ledger/ledgers/${ledgerId}/overlays`, { credentials: "same-origin", headers: { accept: "application/json" } });
      const minted = r.ok ? isMinted(await r.json()) : false;
      if (state === "on") return;
      state = minted ? "off" : "nothing-minted";
      // A4: minting from the note turns the switch on (and a tap made while
      // the overlays were being asked for is honoured once they answer)
      if (minted && asked) { asked = false; turnOn(); return; }
    } catch { state = "nothing-minted"; }
    draw();
  }

  function turnOn() {
    state = "on";
    sent = null;
    line = null;
    draw();
    void push(true);
  }

  function turnOff() {
    send.cancel();
    state = "off";
    sent = null;
    line = null;
    draw();
    void call("DELETE");
  }

  function draw() {
    const f = face(state);
    for (const sw of box.ownerDocument.querySelectorAll<HTMLElement>("[data-switch]")) {
      sw.setAttribute("aria-checked", String(f.on));
      sw.dataset.state = state;
      const label = sw.querySelector("[data-switch-label]");
      const sub = sw.querySelector("[data-switch-sub]");
      if (label) label.textContent = t(f.label);
      if (sub) sub.textContent = t(f.sub);
    }
    const strip = under?.querySelector<HTMLElement>("[data-chat-sees]");
    if (strip) {
      strip.hidden = state !== "on";
      const text = strip.querySelector("[data-chat-line]");
      const caret = strip.querySelector("[data-chat-caret]");
      const eyebrow = strip.querySelector<HTMLElement>("[data-chat-eyebrow]");
      if (eyebrow) eyebrow.hidden = !line;
      if (text) text.textContent = line ? line.text : t("chat.none");
      if (caret) caret.textContent = line?.caret ?? "";
    }
    const which = noteFor(state, asked);
    const note = under?.querySelector<HTMLElement>("[data-switch-note]");
    if (note) {
      note.hidden = !which;
      for (const part of note.querySelectorAll<HTMLElement>("[data-note-for]")) part.hidden = part.dataset.noteFor !== which;
      const noMint = note.querySelector("[data-note-nomint-text]");
      if (noMint) noMint.textContent = fill(t("note.noMint"), { ledger: init.ledgerName });
      const mint = note.querySelector<HTMLAnchorElement>("[data-note-mint]");
      if (mint && ledgerId) mint.href = `/ledger/${ledgerId}#stream`;
      const list = note.querySelector<HTMLElement>("[data-note-ledgers]");
      if (list && which === "no-ledger") {
        const here = new URL(window.location.href);
        list.innerHTML = init.ledgers.map((l) => {
          const u = new URL(here);
          u.searchParams.set("ledger", String(l.id));
          if (!u.searchParams.get("business")) u.searchParams.set("draft", "1");
          return `<a class="lg-btn" data-variant="secondary" data-size="sm" href="${escape(u.pathname + u.search)}">${escape(l.name)}</a>`;
        }).join("");
        note.querySelectorAll<HTMLElement>("[data-note-start]").forEach((x) => { x.hidden = init.ledgers.length > 0; });
        const choose = note.querySelector<HTMLElement>("[data-note-choose]");
        if (choose) choose.hidden = init.ledgers.length === 0;
      }
    }
  }

  box.ownerDocument.addEventListener("click", (e) => {
    const target = e.target as HTMLElement;
    if (target.closest("[data-switch]")) {
      const next = tap(state, asked);
      state = next.state;
      asked = next.asked;
      if (next.effect === "put") turnOn();
      else if (next.effect === "delete") turnOff();
      else draw();
      return;
    }
    if (target.closest("[data-note-close]")) { asked = false; draw(); }
  });

  planner.addEventListener("ledger:plan", (e) => {
    const d = (e as CustomEvent).detail as { plan: Plan; reckoning: Reckoning; business: number | null; ledgerId: number | null };
    if (!d?.plan) return;
    // a draft kept as a business in a ledger: stream through that ledger if none was chosen
    if (!ledgerId && d.business && d.ledgerId && init.signedIn) {
      ledgerId = d.ledgerId;
      init.ledgerName = init.ledgers.find((l) => l.id === ledgerId)?.name ?? init.ledgerName;
      state = "checking";
      void checkMinted();
    }
    const total = d.reckoning?.week?.total?.value;
    latest = { key: planKey(d.business), plan: d.plan, week: total == null || !Number.isFinite(total) ? null : total, reckoning: d.reckoning };
    name = (planner.querySelector("[data-plan-title]")?.textContent ?? "").trim();
    if (!d.business) name = "";
    if (state === "on") send.call();
  });

  // Leaving the page takes the plan off stream, best effort; coming back from the bfcache puts it on again.
  const leave = () => {
    if (state !== "on" || away) return;
    away = true;
    send.cancel();
    void call("DELETE", undefined, true);
  };
  window.addEventListener("pagehide", leave);
  window.addEventListener("beforeunload", leave);
  window.addEventListener("pageshow", (e) => {
    if (!(e as PageTransitionEvent).persisted) return;
    if (away && state === "on") { away = false; sent = null; line = null; draw(); void push(true); }
    else if (state === "nothing-minted") void checkMinted();
  });
  // back from minting in another tab
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && state === "nothing-minted") void checkMinted();
  });

  fetchPack().then((d) => { data = d; });
  draw();
  void checkMinted();
}
