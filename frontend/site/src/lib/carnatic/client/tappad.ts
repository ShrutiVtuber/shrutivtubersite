/* The tap pad every tap game shares (the tala trainer, {{tap}} tasks, the
 * K self-tests and tapping along with a recording).
 *
 * - Timed on pointerdown, never click, and on the AUDIO clock: the moment
 *   is the event's own timestamp carried over to AudioContext time, so a
 *   busy page or a scroll doesn't make taps late.
 * - `touch-action: none` on the pad, so a tap inside a scrolling page is a
 *   tap, not the start of a scroll.
 * - On touch screens, whole-hand gestures (gestures.ts): two fingers = clap,
 *   one finger = finger count, a sideways swipe = wave. A mouse click is a
 *   clap. Keys: Space = clap, F = finger, W = wave.
 * - "Claps only" (a setting, kept on this device): every tap is a clap, for
 *   anyone who'd rather just keep the claps.
 */
import { GestureReader, KEYS, type Gesture } from "../gestures";
import { ctx } from "./audio";

const KEY = "swara.tap.clapsOnly";

export function clapsOnly(): boolean {
  try {
    const v = localStorage.getItem(KEY);
    if (v !== null) return v === "1";
  } catch { /* storage blocked */ }
  // Default: whole-hand gestures on touch screens, claps only with a mouse.
  return !window.matchMedia?.("(pointer: coarse)").matches;
}

export function setClapsOnly(on: boolean) {
  try { localStorage.setItem(KEY, on ? "1" : "0"); } catch { /* storage blocked */ }
}

export const HINT_GESTURES = "Two fingers: clap · one finger: finger count · swipe sideways: wave. Keys: Space clap, F finger, W wave.";
export const HINT_CLAPS = "Tap for each clap, anywhere on the pad. Space works too.";

/** The AudioContext time an input event happened at (its own timestamp, not when the handler ran). */
export function audioTimeOf(e: Event): number {
  const lag = Math.max(0, performance.now() - e.timeStamp) / 1000;
  return ctx().currentTime - (lag < 1 ? lag : 0);
}

export interface PadOpts {
  onTap: (kind: Gesture, at: number) => void;
  /** Keys work while the pad is on the page; a page with several pads can turn them off. */
  keys?: boolean;
  hint?: HTMLElement | null;
  /** While attached, this pad alone gets the keys (the calibration dialog). */
  exclusive?: boolean;
}

/** The pad that has the keys to itself, if any. */
let keyOwner: HTMLElement | null = null;

/** Attach the pad behaviour to an element. Returns a function that detaches it. */
export function attachPad(el: HTMLElement, o: PadOpts): () => void {
  el.classList.add("tap-pad");
  el.style.touchAction = "none";
  const reader = new GestureReader();
  const starts = new Map<number, number>();   // pointer id -> audio time at its down
  let first = 0;
  const emit = (kind: Gesture, atMs: number) => {
    void atMs;
    o.onTap(clapsOnly() ? "clap" : kind, first);
  };
  const down = (e: PointerEvent) => {
    e.preventDefault();
    const at = audioTimeOf(e);
    if (starts.size === 0) first = at;
    starts.set(e.pointerId, at);
    try { el.setPointerCapture(e.pointerId); } catch { /* not supported */ }
    if (clapsOnly() || e.pointerType !== "touch") { o.onTap("clap", at); reader.reset(); return; }
    const r = reader.pointerDown(e.pointerId, e.clientX, e.clientY, at * 1000, e.pointerType);
    if (r) emit(r.kind, r.at);
  };
  const move = (e: PointerEvent) => {
    if (!starts.has(e.pointerId) || clapsOnly() || e.pointerType !== "touch") return;
    const r = reader.pointerMove(e.pointerId, e.clientX, e.clientY);
    if (r) emit(r.kind, r.at);
  };
  const up = (e: PointerEvent) => {
    if (!starts.has(e.pointerId)) return;
    starts.delete(e.pointerId);
    if (clapsOnly() || e.pointerType !== "touch") return;
    const r = reader.pointerUp(e.pointerId, e.clientX, e.clientY, audioTimeOf(e) * 1000);
    if (r) emit(r.kind, r.at);
  };
  const cancel = (e: PointerEvent) => { starts.delete(e.pointerId); reader.cancel(e.pointerId); };
  const key = (e: KeyboardEvent) => {
    if (o.keys === false || !el.isConnected || (keyOwner && keyOwner !== el)) return;
    const kind = KEYS[e.code];
    if (!kind || e.repeat || (e.target as HTMLElement)?.closest?.("input, textarea, select, [contenteditable]")) return;
    e.preventDefault();
    o.onTap(clapsOnly() ? "clap" : kind, audioTimeOf(e));
  };
  el.addEventListener("pointerdown", down);
  el.addEventListener("pointermove", move);
  el.addEventListener("pointerup", up);
  el.addEventListener("pointercancel", cancel);
  el.addEventListener("contextmenu", (e) => e.preventDefault());
  document.addEventListener("keydown", key);
  if (o.exclusive) keyOwner = el;
  if (o.hint) o.hint.textContent = clapsOnly() ? HINT_CLAPS : HINT_GESTURES;
  return () => {
    el.removeEventListener("pointerdown", down);
    el.removeEventListener("pointermove", move);
    el.removeEventListener("pointerup", up);
    el.removeEventListener("pointercancel", cancel);
    document.removeEventListener("keydown", key);
    if (keyOwner === el) keyOwner = null;
  };
}

/** The "claps only" switch, as a small checkbox label. */
export function clapsOnlyToggle(onChange?: () => void): HTMLLabelElement {
  const l = document.createElement("label");
  l.className = "tap-claps";
  l.innerHTML = `<input type="checkbox"> Claps only`;
  const box = l.querySelector("input")!;
  box.checked = clapsOnly();
  box.addEventListener("change", () => { setClapsOnly(box.checked); onChange?.(); });
  return l;
}
