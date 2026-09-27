/* The tala clock: schedules each count on the audio clock and tells the page
 * which count is being heard, for the grid's playhead, the hand and scoring.
 *
 * - No gap between avartanams and no drift: count n sounds at
 *   start + n × count (beatclock.ts), handed to Web Audio 150 ms ahead by a
 *   25 ms refill timer; a cycle is never scheduled when the one before ends.
 *   With the tab hidden (timers slowed to about once a second) it schedules
 *   further ahead; back in view it re-anchors to the next count ahead.
 * - One source of truth: the hand, the grid and the scoring read the same
 *   AudioContext clock, less the output's latency (what is heard now).
 *
 * Speed 1 is 60 counts a minute by default (DECISIONS tala §6). The tala never
 * speeds up for the faster speeds; only the melody doubles.
 */
import { ctx, talaSound } from "./audio";
import { BeatScheduler, type Beat } from "../beatclock";
import { latency } from "./timing";

export interface ClockCount { n: number; action: "clap" | "finger" | "wave" | "silent"; finger?: string; samam?: boolean }

export const LOOKAHEAD = 0.15;
export const LOOKAHEAD_HIDDEN = 1.5;
export const REFILL_MS = 25;

export class TalaClock {
  counts: ClockCount[];
  private _bpm: number;
  nadai = 4;
  sound = true;
  sched: BeatScheduler | null = null;
  private timer: number | null = null;
  private raf = 0;
  private onVisible = () => {};
  onCount: (index: number, cycle: number) => void = () => {};
  onMatra: (index: number, matra: number) => void = () => {};
  onStop: () => void = () => {};
  onFrame: () => void = () => {};
  /** Extra things to schedule with each count (a melody's notes). */
  onSchedule: (index: number, cycle: number, at: number, countSeconds: number) => void = () => {};

  constructor(counts: ClockCount[], bpm = 60) {
    this.counts = counts;
    this._bpm = bpm;
  }

  get playing() { return this.timer !== null; }
  get countSeconds() { return 60 / this._bpm; }
  get bpm() { return this._bpm; }
  /** A new tempo while playing takes over from the next unscheduled count, without a jump. */
  set bpm(v: number) {
    this._bpm = v;
    if (this.sched) this.sched.retempo(60 / v, ctx().currentTime);
  }

  /** The count being heard now (AudioContext time less the output latency). */
  heard(): Beat | null {
    return this.sched?.beatAt(ctx().currentTime - latency()) ?? null;
  }

  start(delay = 0.15) {
    this.stop();
    const ac = ctx();
    void ac.resume?.();
    const sched = (this.sched = new BeatScheduler(ac.currentTime + delay, this.countSeconds, this.counts.length));
    const tick = () => {
      const ahead = document.hidden ? LOOKAHEAD_HIDDEN : LOOKAHEAD;
      for (const b of sched.due(ctx().currentTime, ahead)) {
        const c = this.counts[b.index];
        if (this.sound) talaSound(c.action, b.at, { samam: c.samam, finger: c.finger });
        this.onSchedule(b.index, b.cycle, b.at, sched.beat);
      }
    };
    tick();
    this.timer = window.setInterval(tick, REFILL_MS);
    this.onVisible = () => {
      if (document.hidden) return;
      void ctx().resume?.();
      sched.reanchor(ctx().currentTime);
      tick();
    };
    document.addEventListener("visibilitychange", this.onVisible);
    let shown = -1, shownMatra = -1;
    const frame = () => {
      const t = ctx().currentTime - latency();
      const cur = sched.beatAt(t);
      if (cur) {
        if (cur.n !== shown) { shown = cur.n; shownMatra = -1; this.onCount(cur.index, cur.cycle); }
        const matra = Math.min(this.nadai - 1, Math.floor(((t - cur.at) / sched.beat) * this.nadai));
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
    document.removeEventListener("visibilitychange", this.onVisible);
    cancelAnimationFrame(this.raf);
    this.onStop();
  }

  /** The count nearest a tap (AudioContext time); `at` is the count's scheduled time. */
  nearest(tapAt: number): { at: number; index: number; cycle: number } | null {
    const hit = this.sched?.nearest(tapAt - latency());
    return hit ? { at: hit.beat.at, index: hit.beat.index, cycle: hit.beat.cycle } : null;
  }
}

/** Tap rating (Foundations v2 §04b, windows from the Timing setting): perfect, on time, early or late. Never red. */
export { rate } from "../beatclock";
