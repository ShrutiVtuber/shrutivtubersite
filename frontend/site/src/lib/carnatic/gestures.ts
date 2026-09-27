/* Sophia's whole-hand gestures on a touch screen, read from pointer events
 * (no DOM, no audio: pure, so it can be tested).
 *
 *   two fingers down together  = a clap
 *   one finger, down and up    = a finger count
 *   one finger swiped sideways = a wave
 *
 * A gesture's time is always the moment the FIRST finger touched: that is
 * when the hand struck, whatever it turns out to be. A mouse or pen can't do
 * two fingers, so its press is a clap straight away; keys are Space = clap,
 * F = finger, W = wave.
 */

export type Gesture = "clap" | "finger" | "wave";
export interface Read { kind: Gesture; at: number }

/** Two fingers count as one clap when the second lands within this many ms of the first. */
export const CLAP_WINDOW_MS = 120;
/** A sideways move this far (px), more across than down, is a wave. */
export const WAVE_PX = 36;

export const KEYS: Record<string, Gesture> = { Space: "clap", KeyF: "finger", KeyW: "wave" };

interface Touch { x: number; y: number }

export class GestureReader {
  private down = new Map<number, Touch>();
  private t0 = 0;
  private start: Touch = { x: 0, y: 0 };
  private done = false;
  private fingers = 0;

  /** A pointer went down at time `t` (any clock, in ms). Returns a gesture when it is already certain. */
  pointerDown(id: number, x: number, y: number, t: number, pointerType = "touch"): Read | null {
    if (pointerType !== "touch") {
      this.reset();
      return { kind: "clap", at: t };
    }
    if (this.down.size === 0 && (this.done || this.fingers === 0 || t - this.t0 > CLAP_WINDOW_MS)) {
      this.reset();
      this.t0 = t;
      this.start = { x, y };
    }
    this.down.set(id, { x, y });
    this.fingers += 1;
    if (!this.done && this.fingers >= 2 && t - this.t0 <= CLAP_WINDOW_MS) {
      this.done = true;
      return { kind: "clap", at: this.t0 };
    }
    return null;
  }

  pointerMove(id: number, x: number, y: number): Read | null {
    if (this.done || !this.down.has(id) || this.fingers !== 1) return null;
    const dx = x - this.start.x;
    const dy = y - this.start.y;
    if (Math.abs(dx) >= WAVE_PX && Math.abs(dx) > Math.abs(dy)) {
      this.done = true;
      return { kind: "wave", at: this.t0 };
    }
    return null;
  }

  pointerUp(id: number, x: number, y: number, t: number): Read | null {
    const move = this.pointerMove(id, x, y);
    this.down.delete(id);
    if (move) return move;
    if (this.done || this.down.size > 0) return null;
    // One finger, up without a swipe. If it lifted inside the clap window a second
    // finger could still land; a real finger count lifts after it has struck, so we
    // decide now: the second finger of a clap lands within the window of the first
    // and is handled in pointerDown before this.
    if (this.fingers === 1) {
      this.done = true;
      return { kind: "finger", at: this.t0 };
    }
    void t;
    return null;
  }

  cancel(id: number) { this.down.delete(id); }

  reset() {
    this.down.clear();
    this.done = false;
    this.fingers = 0;
  }
}

/** The five counts' window: perfect ±30 ms, on time ±80 ms, otherwise early or late. */
export function rateMs(deltaMs: number, perfect = 30, onTime = 80): "perfect" | "onTime" | "early" | "late" {
  const a = Math.abs(deltaMs);
  if (a <= perfect) return "perfect";
  if (a <= onTime) return "onTime";
  return deltaMs < 0 ? "early" : "late";
}

const ACTION_WORD: Record<string, string> = { clap: "a clap", finger: "a finger count", wave: "a wave", silent: "silent" };

/**
 * Scoring one gesture against the count it lands nearest: right kind and in
 * time, or named neutrally when it's the wrong kind ("That count is a wave.").
 * A silent count is shown, never scored. With `clapsOnly` every tap is a clap.
 */
export function judge(g: Gesture, target: { kind: string } | null, clapsOnly: boolean):
  { ok: boolean; note: string } {
  if (!target) return { ok: false, note: "" };
  if (target.kind === "silent") return { ok: false, note: "That count is silent: shown, not scored." };
  if (clapsOnly || target.kind === "any" || target.kind === g) return { ok: true, note: "" };
  return { ok: false, note: `That count is ${ACTION_WORD[target.kind] ?? target.kind}.` };
}
