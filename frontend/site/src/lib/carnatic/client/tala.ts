/* The tala clock: schedules each count on the audio clock (so the beat never
 * drifts with the page's frame rate) and tells the page which count is
 * sounding, for the grid's playhead and the hand.
 *
 * Speed 1 is 60 counts a minute by default (DECISIONS tala §6). The tala never
 * speeds up for the faster speeds; only the melody doubles.
 */
import { ctx, talaSound } from "./audio";

export interface ClockCount { n: number; action: "clap" | "finger" | "wave" | "silent"; finger?: string; samam?: boolean }

export class TalaClock {
  counts: ClockCount[];
  bpm: number;
  nadai = 4;
  sound = true;
  /** When each count of the current run was scheduled (AudioContext time). */
  times: { at: number; index: number; cycle: number }[] = [];
  private timer: number | null = null;
  private raf = 0;
  private next = 0;
  private index = 0;
  private cycle = 0;
  onCount: (index: number, cycle: number) => void = () => {};
  onMatra: (index: number, matra: number) => void = () => {};
  onStop: () => void = () => {};
  onFrame: () => void = () => {};
  /** Extra things to schedule with each count (a melody's notes). */
  onSchedule: (index: number, cycle: number, at: number, countSeconds: number) => void = () => {};

  constructor(counts: ClockCount[], bpm = 60) {
    this.counts = counts;
    this.bpm = bpm;
  }

  get playing() { return this.timer !== null; }
  get countSeconds() { return 60 / this.bpm; }

  start(delay = 0.15) {
    this.stop();
    const ac = ctx();
    this.next = ac.currentTime + delay;
    this.index = 0;
    this.cycle = 0;
    this.times = [];
    const tick = () => {
      const now = ctx().currentTime;
      while (this.next < now + 0.25) {
        const c = this.counts[this.index];
        if (this.sound) talaSound(c.action, this.next, { samam: c.samam, finger: c.finger });
        this.onSchedule(this.index, this.cycle, this.next, this.countSeconds);
        this.times.push({ at: this.next, index: this.index, cycle: this.cycle });
        if (this.times.length > 64) this.times.shift();
        this.next += this.countSeconds;
        this.index += 1;
        if (this.index >= this.counts.length) { this.index = 0; this.cycle += 1; }
      }
    };
    tick();
    this.timer = window.setInterval(tick, 40);
    let shown = -1, shownMatra = -1;
    const frame = () => {
      const now = ctx().currentTime;
      const past = this.times.filter((t) => t.at <= now);
      const cur = past[past.length - 1];
      if (cur) {
        const key = cur.cycle * 1000 + cur.index;
        if (key !== shown) { shown = key; this.onCount(cur.index, cur.cycle); }
        const matra = Math.min(this.nadai - 1, Math.floor(((now - cur.at) / this.countSeconds) * this.nadai));
        if (matra !== shownMatra) { shownMatra = matra; this.onMatra(cur.index, matra); }
      }
      this.onFrame();
      this.raf = requestAnimationFrame(frame);
    };
    this.raf = requestAnimationFrame(frame);
  }

  stop() {
    if (this.timer !== null) window.clearInterval(this.timer);
    this.timer = null;
    cancelAnimationFrame(this.raf);
    this.onStop();
  }

  /** The scheduled count nearest a moment, for tap scoring. */
  nearest(at: number): { at: number; index: number; delta: number } | null {
    let best: { at: number; index: number; delta: number } | null = null;
    for (const t of this.times) {
      const delta = at - t.at;
      if (!best || Math.abs(delta) < Math.abs(best.delta)) best = { at: t.at, index: t.index, delta };
    }
    return best;
  }
}

/** Tap rating (Foundations v2 §04b): perfect ±30 ms, on time ±80 ms, otherwise early or late. Never red. */
export function rate(deltaMs: number): "perfect" | "ontime" | "early" | "late" {
  const a = Math.abs(deltaMs);
  if (a <= 30) return "perfect";
  if (a <= 80) return "ontime";
  return deltaMs < 0 ? "early" : "late";
}
