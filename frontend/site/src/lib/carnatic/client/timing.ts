/* Tap timing in the browser: the output's latency, the learner's calibrated
 * offset, the timing windows, and the Calibrate button every tap game shows
 * (the tala trainer, {{tap}} tasks, the self-tests' tap parts, settings).
 *
 * - A beat is HEARD at its scheduled AudioContext time plus the output's
 *   latency (outputLatency + baseLatency). The hand, the grid and scoring
 *   all use that.
 * - The offset: tap along to 14 clicks; the median of the taps' offsets,
 *   outliers dropped, kept per device and output (this browser's
 *   localStorage, and the account's `tapOffsets` so it survives a cleared
 *   browser). During play a slow, bounded correction follows the learner.
 * - Timing: relaxed (default) ±60/±120 ms, standard ±30/±80, strict ±20/±50,
 *   the setting `timing`.
 */
import { blip, ctx } from "./audio";
import { settings, setSettings } from "./state";
import { attachPad } from "./tappad";
import { CALIBRATION_CLICKS, calibrate, correct, rate, windows, type TimingMode } from "../beatclock";

/** Seconds between a sound's scheduled time and when it leaves the speaker. */
export function latency(): number {
  const a = ctx() as AudioContext & { outputLatency?: number; baseLatency?: number };
  const out = Number.isFinite(a.outputLatency) ? Number(a.outputLatency) : 0;
  const base = Number.isFinite(a.baseLatency) ? Number(a.baseLatency) : 0;
  return Math.max(0, Math.min(0.5, out + base));
}

/** The AudioContext time being heard now. */
export const heardNow = () => ctx().currentTime - latency();

export function timingMode(): TimingMode {
  const m = settings().timing;
  return m === "standard" || m === "strict" ? m : "relaxed";
}

export function setTimingMode(m: TimingMode) {
  setSettings({ timing: m });
}

/** The windows now, for targets `gapSeconds` apart. */
export const windowsNow = (gapSeconds = Infinity) => windows(timingMode(), gapSeconds);

/* ── the calibrated offset, per device and output ───────────────────────── */

const LOCAL = "swara.tapOffsets";

/** This device and output, coarsely: platform, browser and the output (sink). */
export function outputKey(): string {
  const ua = navigator.userAgent;
  const platform = /Android/.test(ua) ? "android" : /iPhone|iPad|iPod/.test(ua) ? "ios" : /Mac/.test(ua) ? "mac"
    : /Windows/.test(ua) ? "windows" : /Linux|X11/.test(ua) ? "linux" : "other";
  const browser = /Firefox\//.test(ua) ? "firefox" : /Edg\//.test(ua) ? "edge" : /Chrome\//.test(ua) ? "chrome" : /Safari\//.test(ua) ? "safari" : "other";
  const sink = (ctx() as any).sinkId;
  const out = typeof sink === "string" && sink ? sink.slice(0, 24) : sink && typeof sink === "object" ? "none" : "default";
  return `web:${platform}:${browser}:${out}`;
}

function readLocal(): Record<string, number> {
  try { return JSON.parse(localStorage.getItem(LOCAL) || "{}") ?? {}; } catch { return {}; }
}

/** The calibrated offset in ms for this device and output, or null if never calibrated. */
export function calibratedOffset(): number | null {
  const k = outputKey();
  const local = readLocal()[k];
  if (Number.isFinite(local)) return Number(local);
  const synced = settings().tapOffsets?.[k];
  return Number.isFinite(synced) ? Number(synced) : null;
}

export function setCalibratedOffset(ms: number | null) {
  const k = outputKey();
  const local = readLocal();
  const synced = { ...(settings().tapOffsets ?? {}) };
  if (ms === null) { delete local[k]; delete synced[k]; } else { local[k] = Math.round(ms); synced[k] = Math.round(ms); }
  try { localStorage.setItem(LOCAL, JSON.stringify(local)); } catch { /* storage blocked */ }
  setSettings({ tapOffsets: synced });
  listeners.forEach((fn) => fn());
}

const listeners = new Set<() => void>();
export function onCalibration(fn: () => void) { listeners.add(fn); return () => listeners.delete(fn); }

/**
 * Scores taps for one run: how far a tap is from the heard beat, less the
 * learner's offset; the offset follows them slowly (bounded) as they play.
 */
export class TapJudge {
  readonly base: number;
  offset: number;
  constructor() {
    this.base = calibratedOffset() ?? 0;
    this.offset = this.base;
  }
  /** ms from the heard target to the tap, corrected; negative = early. */
  delta(tapAt: number, targetAt: number, lat = latency()): number {
    const raw = (tapAt - (targetAt + lat)) * 1000;
    this.offset = correct(this.offset, this.base, raw);
    return raw - this.offset;
  }
  /** The same, without moving the running correction. */
  peek(tapAt: number, targetAt: number, lat = latency()): number {
    return (tapAt - (targetAt + lat)) * 1000 - this.offset;
  }
}

export { rate };

/* ── the Calibrate button ───────────────────────────────────────────────── */

export function calibrationLabel(): string {
  const o = calibratedOffset();
  return o === null ? "Not calibrated" : `Calibrated · offset ${o > 0 ? "+" : ""}${o} ms`;
}

/** "Calibrate" with its status and Reset, for any tap game or the settings page. */
export function calibrateButton(): HTMLElement {
  const box = document.createElement("div");
  box.className = "cal";
  box.innerHTML = `<button type="button" class="cal-go" data-cal>Calibrate</button><span class="cal-state" data-cal-state></span><button type="button" class="cal-reset" data-cal-reset>Reset</button>`;
  const paint = () => {
    box.querySelector<HTMLElement>("[data-cal-state]")!.textContent = calibrationLabel();
    box.querySelector<HTMLElement>("[data-cal-reset]")!.hidden = calibratedOffset() === null;
  };
  box.querySelector("[data-cal]")!.addEventListener("click", () => void runCalibration());
  box.querySelector("[data-cal-reset]")!.addEventListener("click", () => setCalibratedOffset(null));
  const off = onCalibration(paint);
  new MutationObserver((_, obs) => { if (!box.isConnected) { off(); obs.disconnect(); } }).observe(document.body, { childList: true, subtree: true });
  paint();
  return box;
}

let running: Promise<number | null> | null = null;

/** Tap along to 14 clicks; stores and returns the offset, or null if too few taps were steady. */
export function runCalibration(): Promise<number | null> {
  if (running) return running;
  running = new Promise<number | null>((resolve) => {
    const dlg = document.createElement("dialog");
    dlg.className = "cal-dialog";
    dlg.innerHTML = `<p class="cal-h">Calibrate your taps</p>
      <p class="cal-p">Tap with each click, as you would with the tala. ${CALIBRATION_CLICKS} clicks; the odd stray tap is left out. This sets the offset for this device and its speakers or headphones.</p>
      <button type="button" class="cal-pad" data-cal-pad>Tap here, or press the space bar</button>
      <p class="cal-p" data-cal-msg aria-live="polite"></p>
      <div class="cal-row"><button type="button" class="cal-go" data-cal-start>Start</button><button type="button" class="cal-reset" data-cal-close>Close</button></div>`;
    document.body.appendChild(dlg);
    const msg = dlg.querySelector<HTMLElement>("[data-cal-msg]")!;
    const pad = dlg.querySelector<HTMLElement>("[data-cal-pad]")!;
    let clicks: number[] = [];
    let offsets: number[] = [];
    let timer = 0;
    const gap = 0.6;
    const lat = () => latency();
    const detach = attachPad(pad, {
      exclusive: true,
      onTap: (_k, at) => {
        if (!clicks.length) { start(); return; }
        const heard = clicks.map((c) => c + lat());
        let best = heard[0];
        for (const h of heard) if (Math.abs(at - h) < Math.abs(at - best)) best = h;
        if (Math.abs(at - best) < gap / 2) offsets.push((at - best) * 1000);
        msg.textContent = `${offsets.length} tap${offsets.length === 1 ? "" : "s"}`;
      },
    });
    const close = (v: number | null) => {
      window.clearTimeout(timer);
      detach();
      dlg.close();
      dlg.remove();
      running = null;
      resolve(v);
    };
    const start = () => {
      const ac = ctx();
      void ac.resume?.();
      const t0 = ac.currentTime + 0.8;
      clicks = Array.from({ length: CALIBRATION_CLICKS }, (_, i) => t0 + i * gap);
      offsets = [];
      clicks.forEach((c, i) => blip(i === 0 ? 1320 : 990, c, 0.04, 0.18));
      msg.textContent = "Listen, then tap with the clicks…";
      window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        const r = calibrate(offsets);
        if (!r) { msg.textContent = `Only ${offsets.length} steady taps. Press Start and try again.`; clicks = []; return; }
        setCalibratedOffset(r.offsetMs);
        msg.textContent = `${calibrationLabel()} (${r.used} taps).`;
        clicks = [];
        window.setTimeout(() => close(r.offsetMs), 1400);
      }, (t0 - ac.currentTime + CALIBRATION_CLICKS * gap + 0.4) * 1000);
    };
    dlg.querySelector("[data-cal-start]")!.addEventListener("click", start);
    dlg.querySelector("[data-cal-close]")!.addEventListener("click", () => close(null));
    dlg.addEventListener("cancel", () => close(null));
    dlg.showModal();
  });
  return running;
}

/** The timing setting as a small select, for tap games (the settings page has chips). */
export function timingSelect(onChange?: () => void): HTMLLabelElement {
  const l = document.createElement("label");
  l.className = "tap-timing";
  l.innerHTML = `Timing <select><option value="relaxed">relaxed</option><option value="standard">standard (±30/±80 ms)</option><option value="strict">strict</option></select>`;
  const sel = l.querySelector("select")!;
  sel.value = timingMode();
  sel.addEventListener("change", () => { setTimingMode(sel.value as TimingMode); onChange?.(); });
  return l;
}
