/* The exercise player: an exercise over the drone and the tala, at speeds 1,
 * 2 and 3 (one, two and four notes a count; the tala never speeds up), or
 * "up and down" (1 → 2 → 3 → 2 → 1). At each speed an exercise is sung the
 * fewest times that end it on samam (the validator's rule; the ×N badge).
 */
import { TalaClock, type ClockCount } from "./tala";
import { playNote, ctx } from "./audio";
import { ratio, semitones, tokenize, variantsOf } from "../notation";

export interface Exercise {
  id: string; title: string; counts: ClockCount[]; angas: number[];
  notes: string[]; repeats: Record<string, number>; scale: string;
}

export interface Run { speed: number; perCount: number; notes: string[] }

const PER: Record<number, number> = { 1: 1, 2: 2, 3: 4, 4: 8 };

export function runsFor(ex: Exercise, speeds: number[]): Run[] {
  return speeds.map((s) => {
    const times = ex.repeats[String(s)] ?? 1;
    const notes: string[] = [];
    for (let i = 0; i < times; i++) notes.push(...ex.notes);
    return { speed: s, perCount: PER[s], notes };
  });
}

export class Player {
  clock: TalaClock;
  runs: Run[] = [];
  private g = 0;                       // global count since start
  onView: (run: Run, runIndex: number, avartanam: string[][], countInAv: number) => void = () => {};
  onDone: (speeds: number[]) => void = () => {};
  loop = false;
  saHz = 261.63;
  tuning: "just" | "equal" = "just";
  private vars: Record<string, number> = {};
  private ended = false;

  constructor(public ex: Exercise, bpm = 60) {
    this.clock = new TalaClock(ex.counts, bpm);
    this.vars = variantsOf(ex.scale);
    this.clock.onSchedule = (_i, _c, at, cs) => this.schedule(at, cs);
  }

  private locate(g: number): { runIndex: number; start: number } | null {
    let acc = 0;
    for (let r = 0; r < this.runs.length; r++) {
      const counts = Math.ceil(this.runs[r].notes.length / this.runs[r].perCount);
      if (g < acc + counts) return { runIndex: r, start: acc };
      acc += counts;
    }
    return null;
  }

  private hz(tok: string): number | null {
    const t = tokenize(tok)[0];
    if (!t || t.kind !== "note" || !t.swara) return null;
    const v = t.variant ?? this.vars[t.swara] ?? null;
    return this.saHz * ratio(semitones(t.swara, v) + 12 * (t.octave ?? 0), this.tuning);
  }

  private schedule(at: number, countSeconds: number) {
    if (this.ended) return;
    const g = this.g++;
    const where = this.locate(g);
    if (!where) {
      /* Past the end: let the last count ring, then finish (or go round). */
      if (this.loop) {
        this.g = 0;
        return this.schedule(at, countSeconds);
      }
      const done = this.runs.map((r) => r.speed);
      this.ended = true;
      window.setTimeout(() => { this.stop(); this.onDone(done); }, Math.max(0, (at - ctx().currentTime) * 1000));
      return;
    }
    const run = this.runs[where.runIndex];
    const k = g - where.start;
    const slice = run.notes.slice(k * run.perCount, (k + 1) * run.perCount);
    const unit = countSeconds / run.perCount;
    slice.forEach((tok, j) => {
      if (tok === "," || tok === ";") return;
      let dur = unit;
      /* A karvai lengthens the note before it, across the count if need be. */
      for (let x = k * run.perCount + j + 1; x < run.notes.length && run.notes[x] === ","; x++) dur += unit;
      const hz = this.hz(tok);
      if (hz) playNote({ hz, at: at + j * unit, dur: dur * 0.92, gain: 0.2 });
    });
    const counts = this.ex.counts.length;
    const avIndex = Math.floor(k / counts);
    const avStart = avIndex * counts * run.perCount;
    const av: string[][] = [];
    for (let c = 0; c < counts; c++) av.push(run.notes.slice(avStart + c * run.perCount, avStart + (c + 1) * run.perCount));
    const delay = Math.max(0, (at - ctx().currentTime) * 1000);
    window.setTimeout(() => this.onView(run, where.runIndex, av, k % counts), delay);
  }

  start(speeds: number[]) {
    this.runs = runsFor(this.ex, speeds);
    this.g = 0;
    this.ended = false;
    this.clock.start();
  }

  stop() { this.clock.stop(); }
  get playing() { return this.clock.playing; }
}

/* A venu fingering for a note of the exercise (primary, else the
   cross-fingering), for the faint instrument view under each count. */
export function fingeringFor(fingerings: any[], tok: string, vars: Record<string, number>): string | null {
  const t = tokenize(tok)[0];
  if (!t || t.kind !== "note" || !t.swara) return null;
  const v = t.variant ?? vars[t.swara];
  const name = t.swara + (v && !"SP".includes(t.swara) ? v : "");
  const sthayi = (t.octave ?? 0) > 0 ? "tara" : (t.octave ?? 0) < 0 ? "mandra" : "madhya";
  const rows = fingerings.filter((f) => f.swara === name && f.sthayi === sthayi && f.holes);
  const row = rows.find((f) => f.kind === "primary") ?? rows.find((f) => f.kind === "cross-fingering") ?? rows[0];
  return row?.holes ?? null;
}
