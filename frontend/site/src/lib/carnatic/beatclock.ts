/* Tala timing without gaps or drift, and tap timing a person can meet.
 * Pure (no DOM, no audio) so it runs under a fake clock in tests.
 *
 * - Beats are absolute: beat n sounds at start + n × beat. Nothing is added
 *   up count by count (which drifts) and no cycle is scheduled when the one
 *   before ends (which leaves a gap): a lookahead scheduler hands out every
 *   beat that falls in the next window (100-200 ms) on each short tick.
 * - What the ear hears is the scheduled time plus the output's latency, and
 *   a tap lands where the learner heard the beat plus their own habit: the
 *   calibration offset, measured on demand (median of 12-16 taps, outliers
 *   dropped) and nudged slowly, within bounds, while they play.
 * - Timing windows: relaxed (default) ±60 / ±120 ms, standard ±30 / ±80,
 *   strict ±20 / ±50; never wider than 40 % of the gap between targets.
 */

export interface Beat { n: number; at: number; index: number; cycle: number }

export class BeatScheduler {
  private nextN = 0;
  start: number;
  beat: number;
  perCycle: number;
  constructor(start: number, beat: number, perCycle: number) {
    this.start = start;
    this.beat = beat;
    this.perCycle = perCycle;
  }

  /** Beat n's time: absolute, so beat 800 is as exact as beat 1. */
  timeOf(n: number): number { return this.start + n * this.beat; }

  /** Every beat not yet handed out that sounds before `now + lookahead`. */
  due(now: number, lookahead = 0.15): Beat[] {
    const out: Beat[] = [];
    while (this.timeOf(this.nextN) < now + lookahead) {
      const n = this.nextN++;
      out.push({ n, at: this.timeOf(n), index: n % this.perCycle, cycle: Math.floor(n / this.perCycle) });
    }
    return out;
  }

  /** The beat sounding at `t` (the last one at or before it), or null before the first. */
  beatAt(t: number): Beat | null {
    if (t < this.start) return null;
    const n = Math.floor((t - this.start) / this.beat + 1e-9);
    return { n, at: this.timeOf(n), index: n % this.perCycle, cycle: Math.floor(n / this.perCycle) };
  }

  /** The beat nearest `t`, and how far `t` is from it (seconds; negative = early). */
  nearest(t: number): { beat: Beat; delta: number } | null {
    if (t < this.start - this.beat / 2) return null;
    const n = Math.max(0, Math.round((t - this.start) / this.beat));
    const at = this.timeOf(n);
    return { beat: { n, at, index: n % this.perCycle, cycle: Math.floor(n / this.perCycle) }, delta: t - at };
  }

  /** A new tempo from the next beat on, without a jump: the next beat keeps its time. */
  retempo(beat: number, now: number) {
    const n = Math.max(this.nextN, Math.ceil((now - this.start) / this.beat));
    const at = this.timeOf(n);
    this.start = at - n * beat;
    this.beat = beat;
  }

  /**
   * After the tab was hidden (timers throttled, beats possibly missed), skip
   * to the next beat still ahead of `now` rather than bursting the missed ones.
   */
  reanchor(now: number) {
    const n = Math.ceil((now - this.start) / this.beat);
    if (n > this.nextN) this.nextN = n;
  }
}

// ── timing windows ──────────────────────────────────────────────────────────

export type TimingMode = "relaxed" | "standard" | "strict";
export const WINDOWS: Record<TimingMode, { perfect: number; onTime: number }> = {
  relaxed: { perfect: 60, onTime: 120 },
  standard: { perfect: 30, onTime: 80 },
  strict: { perfect: 20, onTime: 50 },
};

/** The windows in ms for a mode, capped at 40 % of the gap between targets. */
export function windows(mode: TimingMode = "relaxed", gapSeconds = Infinity): { perfect: number; onTime: number } {
  const w = WINDOWS[mode] ?? WINDOWS.relaxed;
  const cap = gapSeconds * 1000 * 0.4;
  return { perfect: Math.min(w.perfect, cap), onTime: Math.min(w.onTime, cap) };
}

export function rate(deltaMs: number, w: { perfect: number; onTime: number }): "perfect" | "onTime" | "early" | "late" {
  const a = Math.abs(deltaMs);
  if (a <= w.perfect) return "perfect";
  if (a <= w.onTime) return "onTime";
  return deltaMs < 0 ? "early" : "late";
}

// ── calibration ─────────────────────────────────────────────────────────────

/** How many clicks calibration plays, and how many taps it needs to trust. */
export const CALIBRATION_CLICKS = 14;
export const CALIBRATION_MIN = 8;
/** The running correction moves at most this far (ms) from the calibrated offset. */
export const RUNNING_BOUND_MS = 40;

/**
 * The learner's offset (ms, positive = they tap after the sound): the median
 * of the taps' offsets once outliers are dropped (more than 2.5 median
 * absolute deviations, or 200 ms, from the median). Null with too few taps.
 */
export function calibrate(offsetsMs: number[]): { offsetMs: number; used: number } | null {
  const xs = offsetsMs.filter((x) => Number.isFinite(x) && Math.abs(x) < 400);
  if (xs.length < CALIBRATION_MIN) return null;
  const med = median(xs);
  const mad = median(xs.map((x) => Math.abs(x - med))) || 1;
  const kept = xs.filter((x) => Math.abs(x - med) <= Math.min(200, 2.5 * mad * 1.4826 + 10));
  if (kept.length < CALIBRATION_MIN) return null;
  return { offsetMs: Math.round(median(kept)), used: kept.length };
}

/**
 * The slow correction during play: each scored tap pulls the offset a
 * little (rate 5 %) towards what it showed, never further than the bound
 * from the calibrated value, and ignores taps that were far off anyway.
 */
export function correct(current: number, base: number, observedMs: number, rateK = 0.05, bound = RUNNING_BOUND_MS): number {
  if (!Number.isFinite(observedMs) || Math.abs(observedMs - current) > 150) return current;
  const next = current + (observedMs - current) * rateK;
  return Math.max(base - bound, Math.min(base + bound, next));
}

export function median(xs: number[]): number {
  if (!xs.length) return 0;
  const s = [...xs].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}
