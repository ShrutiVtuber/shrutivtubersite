/* Playing a line of notation over the drone, in just intonation relative to
 * the visitor's Sa (or equal temperament, if they chose it). Holds lengthen
 * the note before them; gamaka marks shape the pitch (audio.ts playNote). */
import { ctx, playNote } from "./audio";
import { pitchHz, semitones, ratio, tokenize, variantsOf, type Token } from "../notation";

export interface PlayOptions {
  saHz: number; tuning?: "just" | "equal"; unit?: number; scale?: string; at?: number;
  onNote?: (index: number, at: number) => void;
}

function hzOf(t: Token, o: PlayOptions, vars: Record<string, number>): number | null {
  if (t.kind !== "note" || !t.swara) return null;
  const v = t.variant ?? vars[t.swara] ?? null;
  return o.saHz * ratio(semitones(t.swara, v) + 12 * (t.octave ?? 0), o.tuning ?? "just");
}

/** Schedules the line and returns when it ends (AudioContext time). */
export function playLine(line: string | Token[], o: PlayOptions): number {
  const toks = (typeof line === "string" ? tokenize(line) : line).filter((t) => !(t.kind === "text" && t.raw === "·"));
  const vars = o.scale ? variantsOf(o.scale) : {};
  const unit = o.unit ?? 0.42;
  let at = o.at ?? ctx().currentTime + 0.08;
  let prevHz: number | null = null;
  toks.forEach((t, i) => {
    if (t.kind !== "note") { at += unit * (t.units ?? 1); return; }
    let dur = unit;
    for (let j = i + 1; j < toks.length && toks[j].kind === "hold"; j++) dur += unit * (toks[j].units ?? 1);
    const hz = hzOf(t, o, vars);
    if (hz && !t.hint) {
      const up = hz * Math.pow(2, 2 / 12), down = hz * Math.pow(2, -2 / 12);
      playNote({ hz, at, dur: dur * 0.95, gamaka: t.gamaka, fromHz: prevHz, upperHz: up, lowerHz: down });
      o.onNote?.(i, at);
      prevHz = hz;
    }
    at += unit;
  });
  return at;
}

export { pitchHz };
