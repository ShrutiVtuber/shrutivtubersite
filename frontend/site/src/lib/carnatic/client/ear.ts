/* The ear trainer (EAR_TRAINING.md; artboards P7-P12): eight families of
 * drills (SW, PD, PR, RR, GM, TL, MS, FM), each a ladder of levels, with
 * items made at load time from the same data the raga and tala pages use,
 * so the trainer never contradicts them.
 *
 * Rules kept here: a raga is never asked from its scale (scales appear only
 * in MS, labelled "a scale, not a raga"); synthesised audio says so; ragas
 * whose flag says synth isn't honest for them (carnatic_raga_flag, the
 * Studio's switch) are drilled only from approved recordings; pitch is
 * relative to the learner's Sa with the drone; no lives, no streaks, no red.
 * A wrong answer comes back after three other items and becomes a card.
 */
import { checkSargam, checkText, ragaKey, type SargamRule } from "../answers";
import { inline, ratio, semitones, tokenize, type Script, type TamilStyle, type Swara } from "../notation";
import { blip, ctx, playNote, talaSound } from "./audio";
import { genData, sargamPad, sargamResultHtml } from "./exercise";
import { loadPlayer } from "./embed";
import { attempts, dueCards, ensureCard, recordAttempt, review, wordFor } from "./learner";
import { playLine } from "./phrase";
import { attachPad } from "./tappad";
import { settings, startDrone, stopDrone, theDrone } from "./state";
import { pitchHz } from "../notation";

const esc = (s: string) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const pick = <T,>(a: T[]): T => a[Math.floor(Math.random() * a.length)];
const shuffle = <T,>(a: T[]): T[] => a.map((x) => [Math.random(), x] as const).sort((p, q) => p[0] - q[0]).map((x) => x[1]);
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// ── definitions from the API ───────────────────────────────────────────────

export interface Level { id: string; family: string; title: string; unlockedBy: string; answer: string; audio: { kind: string }; fluentMs: number; note: string | null; ladder: string[] }
export interface Drills {
  families: { id: string; title: string; answerBy: string; words: string; note?: string }[];
  levels: Level[];
  confusable: { set: string; ragas: string[]; mode: string; unlockedBy: string; differ: string }[];
  ragaFlags: Record<string, { synthOk: boolean }>;
}
export interface Rec {
  id: string; status: string; provider: string; url: string; title: string; raga: string; tala: string; form: string; instrument: string;
  composition: string; clips: { id: string; start: string; end: string; label: string }[]; sections: { t: string; label: string }[];
  beatMap: { clip?: string; samam: number[]; counts?: number[] } | null; annotations?: any;
}

// ── per-level progress, on the device (and as attempts on the account) ────

const KEY = "swara.ear";
interface LevelState { recent: boolean[]; sessions: { at: string; right: number; of: number }[] }
function readAll(): Record<string, LevelState> {
  try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch { return {}; }
}
function writeAll(s: Record<string, LevelState>) {
  try { localStorage.setItem(KEY, JSON.stringify(s)); } catch { /* storage blocked: this visit still works */ }
}
export function levelState(id: string): LevelState {
  const s = readAll()[id];
  return { recent: s?.recent ?? [], sessions: s?.sessions ?? [] };
}
function noteAnswer(id: string, right: boolean) {
  const all = readAll();
  const s = all[id] ?? { recent: [], sessions: [] };
  s.recent = [...s.recent, right].slice(-20);
  all[id] = s;
  writeAll(all);
}
function noteSession(id: string, right: number, of: number) {
  const all = readAll();
  const s = all[id] ?? { recent: [], sessions: [] };
  s.sessions = [...s.sessions, { at: new Date().toISOString(), right, of }].slice(-60);
  all[id] = s;
  writeAll(all);
}
/** 16 of the last 20 right: the trainer suggests the next level (it never moves anyone). */
export function comfortable(id: string): boolean {
  const r = levelState(id).recent;
  return r.length >= 20 && r.filter(Boolean).length >= 16;
}
/** The ladder step inside a level, from the recent answers: 0 to ladder.length - 1. */
export function rung(id: string, ladder: number): number {
  const right = levelState(id).recent.filter(Boolean).length;
  return Math.max(0, Math.min(ladder - 1, Math.floor(right / 5)));
}

// ── sound ──────────────────────────────────────────────────────────────────

const saHz = () => pitchHz(settings().sa || "C3");
const tuning = () => (settings().playbackTuning === "equal" ? "equal" : "just") as "just" | "equal";
function hz(tok: string, octave = 0): number {
  const t = tokenize(tok)[0];
  return saHz() * ratio(semitones(t.swara as Swara, t.variant ?? null) + 12 * ((t.octave ?? 0) + octave), tuning());
}
function droneOn(tuningName: "pa" | "ma" | "mute" | "ni" = "pa") {
  if (!theDrone().playing) startDrone(tuningName);
}

export const SYNTH = "Synthesised approximation";

// ── the question every family makes ────────────────────────────────────────

export interface Question {
  level: string; card: string; prompt: string; note?: string;
  kind: "choice" | "multi" | "sargam" | "number" | "text" | "tap" | "unavailable";
  options?: { id: string; label: string }[];
  answer?: string | string[] | number;
  accept?: string[];
  rule?: SargamRule;
  source: string;
  play?: (box: HTMLElement) => Promise<number | void>;
  /** Tap questions: the AudioContext time to tap, and the tolerance in seconds. */
  tapAt?: () => number | null; tolerance?: number;
  explain: string;
  lesson?: string;
}

type Data = Omit<Awaited<ReturnType<typeof genData>>, "melas" | "practical" | "suladi"> & {
  melas: any[]; practical: any[]; suladi: any[]; janyasFull: any[]; recs: Rec[]; drills: Drills;
};

const NAMES: Record<string, string> = {
  S: "Sa (shadjam)", P: "Pa (panchamam)", R1: "R₁ (suddha rishabham)", R2: "R₂ (chatusruti rishabham)", R3: "R₃ (shatsruti rishabham)",
  G1: "G₁ (suddha gandharam)", G2: "G₂ (sadharana gandharam)", G3: "G₃ (antara gandharam)", M1: "M₁ (suddha madhyamam)",
  M2: "M₂ (prati madhyamam)", D1: "D₁ (suddha dhaivatam)", D2: "D₂ (chatusruti dhaivatam)", D3: "D₃ (shatsruti dhaivatam)",
  N1: "N₁ (suddha nishadam)", N2: "N₂ (kaisiki nishadam)", N3: "N₃ (kakali nishadam)",
};
const SHORT = (t: string) => t.replace(/([SRGMPDN])([123])/g, (_, s, n) => s + "₀₁₂₃"[Number(n)]);
const TWELVE = ["S", "R1", "R2", "G2", "G3", "M1", "M2", "P", "D1", "D2", "N2", "N3"];
const ENH: Record<string, string> = { R2: "G1", R3: "G2", D2: "N1", D3: "N2", G1: "R2", G2: "R3", N1: "D2", N2: "D3" };
const MMG = ["S", "R1", "G3", "M1", "P", "D1", "N3"];
const OCT = ["mandra", "madhya", "tara"];

function synthOk(d: Data, raga: string): boolean {
  const flag = d.drills.ragaFlags[raga];
  return flag ? flag.synthOk : true;
}
function ragaName(d: Data, id: string): string {
  return d.janyasFull.find((r) => r.id === id)?.name ?? d.melas.find((m: any) => m.id === id)?.name ?? id;
}
function prayogas(d: Data, id: string): { sargam: string; note?: string }[] {
  return (d.janyasFull.find((r) => r.id === id)?.prayogas ?? []).filter((p: any) => p.sargam && tokenize(p.sargam).some((t) => t.kind === "note"));
}
function scaleOf(d: Data, id: string): string { return d.scales[id] ?? ""; }

function phrasePlayer(line: string, scale?: string, unit = 0.42): Question["play"] {
  return async () => { droneOn(); return playLine(line, { saHz: saHz(), tuning: tuning(), scale, unit }); };
}
function recPlayer(r: Rec, clip?: { start: string; end: string }): Question["play"] {
  const toS = (t?: string) => (t ? t.split(":").reduce((a, x) => a * 60 + Number(x), 0) : undefined);
  return async (box) => { if (theDrone().playing) stopDrone(); loadPlayer(box, r.provider, r.url, { start: toS(clip?.start), end: toS(clip?.end) }); };
}
const unavailable = (level: string, text: string): Question => ({ level, card: level, prompt: text, kind: "unavailable", source: "", explain: "" });

// ── the families ───────────────────────────────────────────────────────────

function sw(level: Level, d: Data, step: number): Question {
  const dur = [2, 1, 0.5, 0.5][step] ?? 1;
  const fade = step >= 3;
  const one = (tok: string, oct = 0): Question["play"] => async () => {
    droneOn();
    const at = ctx().currentTime + 0.1;
    playNote({ hz: hz(tok, oct), at, dur });
    if (fade) setTimeout(() => stopDrone(), 1000);
    return at + dur;
  };
  const base = { level: level.id, source: `${SYNTH} · drone on Sa`, lesson: level.unlockedBy };
  switch (level.id) {
    case "SW.01": {
      const tok = pick(["S", "P", "S", "P", pick(["R2", "G3", "M1", "D2", "N3"])]);
      const ans = tok === "S" ? "sa" : tok === "P" ? "pa" : "neither";
      return { ...base, card: `SW.01:${ans}`, prompt: "Sa, Pa, or neither?", kind: "choice", play: one(tok),
        options: [{ id: "sa", label: "Sa" }, { id: "pa", label: "Pa" }, { id: "neither", label: "Neither" }], answer: ans,
        explain: ans === "neither" ? `It was ${NAMES[tok]}: it doesn't sit still against the drone the way Sa and Pa do.` : `${ans === "sa" ? "Sa merges with the drone's lowest strings" : "Pa is the drone's other note, a pure fifth above Sa"}.` };
    }
    case "SW.02": {
      const tok = pick(["S", "P"]);
      const o = pick([-1, 0, 1]);
      return { ...base, card: `SW.02:${tok}${o}`, prompt: `Which octave is this ${tok === "S" ? "Sa" : "Pa"} in?`, kind: "choice", play: one(tok, o),
        options: OCT.map((x, i) => ({ id: String(i - 1), label: x })), answer: String(o),
        explain: `It was ${OCT[o + 1]} ${tok === "S" ? "Sa" : "Pa"}. Madhya is the middle octave, the one the drone's Sa sits in; mandra is below, tara above.` };
    }
    case "SW.03": {
      const count = [3, 5, 7, 7][step];
      const tok = pick(MMG);
      const opts = shuffle([tok, ...shuffle(MMG.filter((x) => x !== tok)).slice(0, count - 1)]).sort((a, b) => MMG.indexOf(a) - MMG.indexOf(b));
      return { ...base, card: `SW.03:${tok}`, prompt: "Which swara of Mayamalavagowla?", kind: "choice", play: one(tok),
        options: opts.map((x) => ({ id: x, label: SHORT(x) })), answer: tok, explain: `It was ${NAMES[tok]}.` };
    }
    case "SW.04": {
      const pairs: [string, string, string][] = [["R1", "R2", "S R"], ["G2", "G3", "R2 G"], ["M1", "M2", "G3 M"], ["D1", "D2", "P D"], ["N2", "N3", "D2 N"]];
      const [a, b, ctxLine] = pick(pairs);
      const tok = pick([a, b]);
      const withContext = step >= 1;
      return { ...base, card: `SW.04:${a}-${b}`, prompt: `Which ${tok[0] === "R" ? "Ri" : tok[0] === "G" ? "Ga" : tok[0] === "M" ? "Ma" : tok[0] === "D" ? "Dha" : "Ni"} did you hear?`,
        kind: "choice", options: [{ id: a, label: NAMES[a] }, { id: b, label: NAMES[b] }], answer: tok,
        play: withContext ? phrasePlayer(`${ctxLine.split(" ")[0]} ${tok}`, undefined, dur * 0.8) : one(tok),
        note: withContext ? `Played after ${SHORT(ctxLine.split(" ")[0])}, as in a phrase.` : undefined,
        explain: `It was ${NAMES[tok]}. ${SHORT(b)} sits a semitone above ${SHORT(a)}; listen for how much room there is between it and the note below.` };
    }
    case "SW.05": {
      const tok = pick(TWELVE);
      return { ...base, card: `SW.05:${tok}`, prompt: "Which of the twelve swarasthanas?", kind: "choice", play: one(tok),
        options: TWELVE.map((x) => ({ id: x, label: SHORT(x) })), answer: tok, accept: ENH[tok] ? [tok, ENH[tok]] : [tok],
        explain: `It was ${NAMES[tok]}${ENH[tok] ? `, which is the same pitch as ${NAMES[ENH[tok]]}` : ""}.` };
    }
    case "SW.06": {
      const tok = pick(MMG);
      const o = pick([-1, 0, 1]);
      const others = shuffle(MMG.flatMap((x) => [-1, 0, 1].map((oo) => `${x}|${oo}`)).filter((x) => x !== `${tok}|${o}`)).slice(0, 5);
      const opts = shuffle([`${tok}|${o}`, ...others]);
      return { ...base, card: `SW.06:${tok}`, prompt: "Which swara, in which octave?", kind: "choice", play: one(tok, o),
        options: opts.map((x) => { const [t, oo] = x.split("|"); return { id: x, label: `${SHORT(t)} ${OCT[Number(oo) + 1]}` }; }),
        answer: `${tok}|${o}`, explain: `It was ${NAMES[tok]}, ${OCT[o + 1]}. Both the swara and the octave have to match.` };
    }
    default: {
      const [x, y] = shuffle(MMG).slice(0, 2);
      const opts = shuffle([`${x} ${y}`, `${y} ${x}`, `${x} ${shuffle(MMG.filter((z) => z !== x && z !== y))[0]}`, `${shuffle(MMG.filter((z) => z !== x && z !== y))[0]} ${y}`]);
      return { ...base, card: `SW.07:${[x, y].sort().join("-")}`, prompt: "Two swaras: name both, in the order you heard them.", kind: "choice",
        play: async () => { droneOn(); const at = ctx().currentTime + 0.1; playNote({ hz: hz(x), at, dur }); playNote({ hz: hz(y), at: at + dur + 0.25, dur }); return at + 2 * dur + 0.25; },
        options: [...new Set(opts)].map((o) => ({ id: o, label: o.split(" ").map(SHORT).join(" then ") })), answer: `${x} ${y}`,
        explain: `${SHORT(x)} then ${SHORT(y)}: the second is ${MMG.indexOf(y) > MMG.indexOf(x) ? "higher" : "lower"}.` };
    }
  }
}

function stepwise(scale: string[], n: number, leaps = 1, octaves = false): string {
  let i = Math.floor(Math.random() * (scale.length - 2)) + 1;
  const out: string[] = [];
  for (let k = 0; k < n; k++) {
    const t = scale[Math.max(0, Math.min(scale.length - 1, i))];
    out.push(t);
    i += (Math.random() < 0.5 ? -1 : 1) * (1 + Math.floor(Math.random() * leaps));
    if (!octaves) i = Math.max(0, Math.min(scale.length - 1, i));
  }
  return out.join(" ");
}

function pd(level: Level, d: Data, step: number): Question {
  const len = [3, 5, 8, 12][step] ?? 5;
  const mm = ["S", "R1", "G3", "M1", "P", "D1", "N3", "S'"];
  const withOct = [".P", ".D1", ".N3", "S", "R1", "G3", "M1", "P", "D1", "N3", "S'", "R1'", "G3'"];
  const base = { level: level.id, source: SYNTH, kind: "sargam" as const, lesson: level.unlockedBy, rule: { scale: scaleOf(d, "mayamalavagowla") || "S R1 G3 M1 P D1 N3", checkOctaves: true } as SargamRule };
  let line = "", prompt = "Write what you hear.", raga = "mayamalavagowla", note: string | undefined;
  switch (level.id) {
    case "PD.01": line = stepwise(mm, 3); break;
    case "PD.02": {
      const notes = stepwise(mm, Math.min(6, len)).split(" ");
      line = notes.map((t) => (Math.random() < 0.35 ? `${t} ,` : t)).join(" ");
      base.rule.checkHolds = true; note = "Holds count: write , for each extra unit.";
      break;
    }
    case "PD.03": line = stepwise(mm, Math.ceil(len / 2)).split(" ").flatMap((t) => [t, t]).join(" "); break;
    case "PD.04": line = stepwise(mm, len, 4); break;
    case "PD.05": line = stepwise(withOct, len, 2); break;
    case "PD.06": line = stepwise(mm, 16); note = "Speed 2: two notes to a count."; break;
    case "PD.07": {
      raga = pick(["mohanam", "kalyani", "kharaharapriya"]);
      const sc = (scaleOf(d, raga).split(" ").filter((t) => t && !t.includes("'")));
      line = stepwise([...new Set(sc)], len);
      prompt = `Write what you hear. The raga is ${ragaName(d, raga)}, so the swara numbers aren't needed.`;
      base.rule = { raga, scale: scaleOf(d, raga), checkOctaves: true };
      break;
    }
    case "PD.08": {
      const pool = d.janyasFull.filter((r) => synthOk(d, r.id) && prayogas(d, r.id).length);
      const r = pick(pool);
      raga = r.id;
      line = pick(prayogas(d, r.id)).sargam;
      prompt = `A phrase of ${r.name}. Write it; gamaka signs aren't needed.`;
      base.rule = { raga, scale: scaleOf(d, raga), checkOctaves: true };
      note = (r.gamakaCharacter ?? []).length ? undefined : "Played plain: the research gives no gamaka curves for this raga.";
      break;
    }
    default: {
      const withTx = d.recs.filter((r) => (r.annotations?.transcriptions ?? []).length);
      if (!withTx.length) return unavailable(level.id, "No recording has a transcription yet. This drill opens when Shruti annotates one.");
      const r = pick(withTx);
      const tx = pick(r.annotations.transcriptions) as { start: string; end: string; sargam: string };
      return { ...base, source: "Recording", card: `PD.09:${r.id}`, prompt: `Transcribe the phrase in this clip (${r.raga ? ragaName(d, r.raga) : "raga given below"}).`,
        play: recPlayer(r, tx), answer: tx.sargam, rule: { raga: r.raga, scale: scaleOf(d, r.raga), checkOctaves: true },
        explain: "Compared with Shruti's transcription, swara by swara." };
    }
  }
  const unit = level.id === "PD.06" ? 0.3 : 0.5;
  return { ...base, card: `${level.id}:${raga}`, prompt, note, play: phrasePlayer(line, scaleOf(d, raga), unit), answer: line,
    explain: `It was ${line.split(" ").map(SHORT).join(" ")}.` };
}

let preferSet: string | null = null;

function pr(level: Level, d: Data, done: (lesson: string) => boolean): Question {
  const all = d.drills.confusable.filter((c) => c.mode.startsWith("synth") && c.ragas.every((r) => synthOk(d, r) && prayogas(d, r).length));
  const wanted = (preferSet ?? "").split(",").map((x) => x.trim()).filter(Boolean);
  const sets = wanted.length && all.some((c) => wanted.includes(c.set)) ? all.filter((c) => wanted.includes(c.set)) : all;
  const base = { level: level.id, source: SYNTH, lesson: level.unlockedBy };
  if (level.id === "PR.01") {
    const open = sets.filter((c) => done(c.unlockedBy));
    const c = pick(open.length ? open : sets);
    if (!c && preferSet) return unavailable(level.id, "This pair is drilled from recordings only, and none is approved with clips yet.");
    if (!c) return unavailable(level.id, "No confusable set can be played honestly by the synth yet.");
    const r = pick(c.ragas);
    const p = pick(prayogas(d, r));
    return { ...base, card: `PR.01:${c.set}`, kind: "choice", prompt: "Which raga does this phrase belong to?", play: phrasePlayer(p.sargam, scaleOf(d, r)),
      options: c.ragas.map((x) => ({ id: x, label: ragaName(d, x) })), answer: r,
      explain: `${ragaName(d, r)}: ${p.note ?? p.sargam}. The set differs in ${c.differ}.` };
  }
  if (level.id === "PR.02") {
    const c = pick(sets);
    if (!c) return unavailable(level.id, "No confusable set can be played honestly by the synth yet.");
    const x = pick(c.ragas);
    const from = pick(c.ragas);
    const p = pick(prayogas(d, from));
    const yes = from === x;
    return { ...base, card: `PR.02:${c.set}`, kind: "choice", prompt: `Is this phrase idiomatic in ${ragaName(d, x)}?`, play: phrasePlayer(p.sargam, scaleOf(d, from)),
      options: [{ id: "yes", label: "Yes" }, { id: "no", label: "No" }], answer: yes ? "yes" : "no",
      explain: yes ? `It's a sourced prayoga of ${ragaName(d, x)}: ${p.note ?? p.sargam}.` : `It's a sourced prayoga of ${ragaName(d, from)}, a sister of ${ragaName(d, x)} (${c.differ}).` };
  }
  const pool = d.janyasFull.filter((r) => synthOk(d, r.id) && prayogas(d, r.id).length);
  const r = pick(pool);
  const p = pick(prayogas(d, r.id));
  if (level.id === "PR.03") {
    const opts = shuffle([r, ...shuffle(pool.filter((x) => x.id !== r.id)).slice(0, 3)]);
    return { ...base, card: `PR.03:${r.id}`, kind: "choice", prompt: "Which raga does this phrase come from?", play: phrasePlayer(p.sargam, scaleOf(d, r.id)),
      options: opts.map((x) => ({ id: x.id, label: x.name })), answer: r.id, explain: `${r.name}: ${p.note ?? p.sargam}.` };
  }
  return { ...base, card: `PR.04:${r.id}`, kind: "text", prompt: "Name the raga.", play: phrasePlayer(p.sargam, scaleOf(d, r.id)),
    answer: r.name, accept: [r.name, ...(r.aliases ?? [])], explain: `${r.name}: ${p.note ?? p.sargam}. Spellings like Thodi or Dheerasankarabharanam are accepted.` };
}

function rr(level: Level, d: Data): Question {
  const flute = level.id === "RR.05";
  const recs = d.recs.filter((r) => r.raga && r.clips.length && (!flute || r.instrument === "venu"));
  if (!recs.length) return unavailable(level.id, flute ? "Shruti's flute recordings aren't in the room yet. This drill opens when they are." : "No approved recording has clips marked yet. This drill opens as the Listening room fills.");
  const r = pick(recs);
  const clip = pick(r.clips);
  const ragas = [...new Set(d.recs.map((x) => x.raga).filter(Boolean))];
  const base = { level: level.id, source: "Recording · clip chosen by Shruti", lesson: level.unlockedBy, play: recPlayer(r, clip), card: `${level.id}:${r.raga}` };
  const n = level.id === "RR.01" ? 2 : 4;
  const opts = shuffle([r.raga, ...shuffle(ragas.filter((x) => x !== r.raga)).slice(0, n - 1)]);
  const reveal = `It was ${ragaName(d, r.raga)}${r.composition ? `: ${r.composition}` : ""}.`;
  if (level.id === "RR.03") return { ...base, kind: "text", prompt: "Name the raga of this clip.", answer: ragaName(d, r.raga), accept: [ragaName(d, r.raga), r.raga], explain: reveal };
  if (level.id === "RR.04") {
    const forms = [...new Set(d.recs.map((x) => x.form).filter(Boolean))];
    const talas = [...new Set(d.recs.map((x) => x.tala).filter(Boolean))];
    return { ...base, kind: "multi", prompt: "Raga, form and tala: pick one of each.",
      options: [...shuffle([r.raga, ...shuffle(ragas.filter((x) => x !== r.raga)).slice(0, 2)]).map((x) => ({ id: `raga:${x}`, label: `Raga: ${ragaName(d, x)}` })),
                ...shuffle([r.form, ...shuffle(forms.filter((x) => x !== r.form)).slice(0, 2)]).filter(Boolean).map((x) => ({ id: `form:${x}`, label: `Form: ${x}` })),
                ...shuffle([r.tala, ...shuffle(talas.filter((x) => x !== r.tala)).slice(0, 2)]).filter(Boolean).map((x) => ({ id: `tala:${x}`, label: `Tala: ${x.replace(/_/g, " ")}` }))],
      answer: [`raga:${r.raga}`, ...(r.form ? [`form:${r.form}`] : []), ...(r.tala ? [`tala:${r.tala}`] : [])], explain: `${reveal} Form: ${r.form || "not marked"}; tala: ${(r.tala || "not marked").replace(/_/g, " ")}.` };
  }
  return { ...base, kind: "choice", prompt: "Which raga is this clip in?", options: opts.map((x) => ({ id: x, label: ragaName(d, x) })), answer: r.raga, explain: reveal };
}

const GAMAKA_LABEL: Record<string, string> = {
  plain: "A plain note", kampita: "Kampita", "jaru-up": "Jaru up (etra jaru)", "jaru-down": "Jaru down (irakka jaru)", step: "A plain step",
  nokku: "Nokku", odukkal: "Odukkal", orikkai: "Orikkai", sphurita: "Sphurita", pratyahata: "Pratyahata", ravai: "Ravai", khandippu: "Khandippu",
};
const GAMAKA_EXPLAIN: Record<string, string> = {
  plain: "the pitch stays put", kampita: "the note oscillates towards the one above and settles back", "jaru-up": "a slide up into the note", "jaru-down": "a slide down into the note",
  step: "two notes, no slide between them", nokku: "the note is stressed from the one above", odukkal: "the note is stressed from the one below", orikkai: "a flick up at the end of the note",
  sphurita: "on a repeated note, the second is struck from the note below", pratyahata: "on a repeated note, the second is struck from the note above (the textbook list uses the name differently: GAMAKA.md)",
  ravai: "a quick hit on the note above and back", khandippu: "a quick hit on the previous, lower note and back",
};

function gm(level: Level, d: Data, step: number): Question {
  const dur = [1.4, 1, 0.7, 0.5][step] ?? 1;
  const base = { level: level.id, source: SYNTH, lesson: level.unlockedBy };
  const note = pick(["G3", "M1", "P", "D2", "R2"]);
  const choices: Record<string, string[]> = {
    "GM.01": ["plain", "kampita"], "GM.02": ["jaru-up", "jaru-down", "step"], "GM.03": ["nokku", "odukkal", "orikkai"],
    "GM.04": ["plain", "sphurita", "pratyahata"], "GM.05": ["ravai", "khandippu"],
    "GM.06": ["kampita", "jaru-up", "jaru-down", "nokku", "odukkal", "orikkai", "sphurita", "pratyahata", "ravai", "khandippu"],
  };
  if (level.id === "GM.07") {
    const recs = d.recs.filter((r) => (r.annotations?.gamakas ?? []).length);
    if (!recs.length) return unavailable(level.id, "No recording has gamakas marked yet. This drill opens when Shruti annotates one.");
    const r = pick(recs);
    const mark = pick(r.annotations.gamakas) as { t: string; gamakas: string[] };
    return { ...base, source: "Recording · Shruti's annotation", card: `GM.07:${r.id}`, kind: "multi", prompt: `Which of these do you hear at ${mark.t}?`,
      play: recPlayer(r, { start: mark.t, end: "" }), options: choices["GM.06"].map((g) => ({ id: g, label: GAMAKA_LABEL[g] })), answer: mark.gamakas,
      explain: `Shruti marked ${mark.gamakas.map((g) => GAMAKA_LABEL[g]).join(", ")} here.` };
  }
  const opts = choices[level.id] ?? choices["GM.06"];
  const g = pick(opts);
  const play: Question["play"] = async () => {
    droneOn();
    const at = ctx().currentTime + 0.1;
    const h = hz(note);
    const up = h * Math.pow(2, 2 / 12), down = h * Math.pow(2, -2 / 12);
    if (level.id === "GM.02") {
      const from = g === "jaru-down" ? up * Math.pow(2, 2 / 12) : down * Math.pow(2, -1 / 12);
      playNote({ hz: from, at, dur: dur * 0.7 });
      playNote({ hz: h, at: at + dur * 0.7, dur, gamaka: g === "step" ? null : g, fromHz: from });
      return at + dur * 1.7;
    }
    if (level.id === "GM.04") {
      playNote({ hz: h, at, dur: dur * 0.8 });
      playNote({ hz: h, at: at + dur * 0.8, dur: dur * 0.8, gamaka: g === "plain" ? null : g === "sphurita" ? "odukkal" : "nokku", upperHz: up, lowerHz: down });
      return at + dur * 1.6;
    }
    // GM.06 and later rungs: the gamaka inside a short phrase, on the marked (third) note.
    if (level.id === "GM.06" || step >= 3) {
      const line = ["S", "R2", note, "P"];
      line.forEach((t, i) => playNote({ hz: hz(t), at: at + i * dur * 0.6, dur: dur * 0.6, gamaka: i === 2 ? g : null, fromHz: i ? hz(line[i - 1]) : null }));
      return at + 4 * dur * 0.6;
    }
    playNote({ hz: h, at, dur, gamaka: g === "plain" ? null : g, upperHz: up, lowerHz: down, fromHz: g === "jaru-up" ? down : g === "jaru-down" ? up : null });
    return at + dur;
  };
  return { ...base, card: `${level.id}:${g}`, kind: "choice", prompt: level.id === "GM.06" ? `Which gamaka is on the third note (${SHORT(note)})?` : `${level.title}`,
    play, options: opts.map((x) => ({ id: x, label: GAMAKA_LABEL[x] })), answer: g, explain: `${GAMAKA_LABEL[g]}: ${GAMAKA_EXPLAIN[g]}.` };
}

function talaCues(counts: any[], at: number, beat: number, avs: number, clapsOnly = false, kalai = 1) {
  for (let a = 0; a < avs; a++) counts.forEach((c, i) => {
    for (let k = 0; k < kalai; k++) {
      const t = at + ((a * counts.length + i) * kalai + k) * beat;
      if (clapsOnly && c.action !== "clap") continue;
      talaSound(c.action, t, { samam: c.samam && k === 0, finger: c.finger });
    }
  });
  return at + avs * counts.length * kalai * beat;
}

function tl(level: Level, d: Data, step: number): Question {
  const tempo = [[50, 70], [40, 100], [40, 140], [40, 140]][step] ?? [50, 70];
  const bpm = tempo[0] + Math.round(Math.random() * (tempo[1] - tempo[0]));
  const beat = 60 / bpm;
  const base = { level: level.id, source: "Kriya cues: clap, finger and wave sounds", lesson: level.unlockedBy };
  const T = (id: string): any => d.practical.find((t: any) => t.id === id);
  const four = ["adi", "rupaka_3count", "misra_chapu", "khanda_chapu"];
  switch (level.id) {
    case "TL.01":
    case "TL.02": {
      const id = pick(four);
      const t = T(id);
      return { ...base, card: `${level.id}:${id}`, kind: "choice", prompt: level.id === "TL.02" ? "Which tala? Claps only." : "Which tala?",
        play: async () => talaCues(t.counts, ctx().currentTime + 0.2, beat, 2, level.id === "TL.02"),
        options: four.map((x) => ({ id: x, label: T(x)?.name ?? x })), answer: id,
        explain: `${t.name}: ${t.speech ?? t.counts.map((c: any) => c.action).join(" ")}.` };
    }
    case "TL.03": {
      const speed = pick([1, 2, 3]);
      const line = "S R G M P D N S' S' N D P M G R S";
      return { ...base, source: `${SYNTH} · Adi cues`, card: `TL.03:${speed}`, kind: "choice", prompt: "Which speed is the line in?",
        play: async () => {
          const at = ctx().currentTime + 0.2;
          const b = 60 / 60;
          talaCues(T("adi").counts, at, b, 1);
          const perCount = [1, 2, 4][speed - 1];
          const toks = line.split(" ").slice(0, 8 * perCount > 16 ? 16 : 8 * perCount);
          playLine(toks.join(" "), { saHz: saHz(), tuning: tuning(), scale: scaleOf(d, "mayamalavagowla"), unit: b / perCount, at });
          return at + 8 * b;
        },
        options: [1, 2, 3].map((x) => ({ id: String(x), label: `Speed ${x}` })), answer: String(speed),
        explain: `Speed ${speed}: ${[1, 2, 4][speed - 1]} note${speed > 1 ? "s" : ""} to each count of the tala.` };
    }
    case "TL.04": {
      const t = pick(d.suladi.filter((x: any) => (x.counts ?? []).length && x.counts.length <= 17));
      return { ...base, card: `TL.04:${t.id}`, kind: "number", prompt: "How many aksharas in this tala? Count them.",
        play: async () => talaCues(t.counts, ctx().currentTime + 0.2, 60 / 70, 1), answer: t.counts.length,
        explain: `${(t.name ?? t.id).replace(/_/g, " ")}: ${t.counts.length} aksharas.` };
    }
    case "TL.05": {
      const types: [string, number][] = [["tisra", 3], ["chaturasra", 4], ["khanda", 5], ["misra", 7], ["sankeerna", 9]];
      const [id, n] = pick(types);
      return { ...base, source: "Konnakol cues over a steady count", card: `TL.05:${id}`, kind: "choice", prompt: "Which nadai?",
        play: async () => {
          const at = ctx().currentTime + 0.2, b = 60 / 50;
          for (let c = 0; c < 4; c++) { talaSound("clap", at + c * b, { samam: c === 0 }); for (let k = 0; k < n; k++) blip(k === 0 ? 1320 : 990, at + c * b + (k * b) / n, 0.04, 0.06); }
          return at + 4 * b;
        },
        options: types.map(([x]) => ({ id: x, label: x[0].toUpperCase() + x.slice(1) })), answer: id, explain: `${id[0].toUpperCase() + id.slice(1)} nadai: ${n} to each count.` };
    }
    case "TL.06": {
      const k = pick([1, 2]);
      return { ...base, source: `${SYNTH} · Adi cues`, card: `TL.06:${k}`, kind: "choice", prompt: "1 kalai or 2 kalai?",
        play: async () => {
          const at = ctx().currentTime + 0.2, b = 60 / 70;
          const end = talaCues(T("adi").counts, at, b, 1, false, k);
          playLine("S , R , G , M , P , D , N , S' ,", { saHz: saHz(), tuning: tuning(), scale: scaleOf(d, "mayamalavagowla"), unit: b / 2 * k, at });
          return end;
        },
        options: [{ id: "1", label: "1 kalai" }, { id: "2", label: "2 kalai" }], answer: String(k),
        explain: k === 2 ? "2 kalai: every action of the tala is done twice, so an avartanam takes twice as long." : "1 kalai: one action to each count." };
    }
    case "TL.07": {
      const off = pick([0, 0.5, 1.5]);
      const label: Record<string, string> = { "0": "On samam", "0.5": "Half a count after samam", "1.5": "One and a half counts after samam" };
      return { ...base, source: `${SYNTH} · Adi cues`, card: `TL.07:${off}`, kind: "choice", prompt: "Where does the line start?",
        play: async () => {
          const at = ctx().currentTime + 0.2, b = 60 / 60;
          talaCues(T("adi").counts, at, b, 1);
          playLine("S R G M P D", { saHz: saHz(), tuning: tuning(), scale: scaleOf(d, "mayamalavagowla"), unit: b / 2, at: at + off * b });
          return at + 8 * b;
        },
        options: ["0", "0.5", "1.5"].map((x) => ({ id: x, label: label[x] })), answer: String(off), explain: `${label[String(off)]}: that is the eduppu.` };
    }
    case "TL.08": {
      const recs = d.recs.filter((r) => r.beatMap && r.tala);
      if (!recs.length) return unavailable(level.id, "No recording has a beat map yet. This drill opens when Shruti taps one in the Studio.");
      const r = pick(recs);
      const talas = [...new Set(recs.map((x) => x.tala))];
      const opts = shuffle([r.tala, ...shuffle(four.filter((x) => x !== r.tala)).slice(0, 3), ...talas.filter((x) => x !== r.tala)].filter((x, i, a) => a.indexOf(x) === i)).slice(0, 4);
      if (!opts.includes(r.tala)) opts[0] = r.tala;
      return { ...base, source: "Recording with Shruti's beat map", card: `TL.08:${r.tala}`, kind: "choice", prompt: "Which tala is this clip in?",
        play: recPlayer(r, r.clips[0]), options: opts.map((x) => ({ id: x, label: T(x)?.name ?? x.replace(/_/g, " ") })), answer: r.tala, explain: `It's in ${T(r.tala)?.name ?? r.tala}.` };
    }
    case "TL.09": {
      // A mora: a 5-syllable phrase three times with gaps of 2, placed to land on samam; the final samam is silent.
      let landing: number | null = null;
      return { ...base, source: "Konnakol cues", card: "TL.09:mora", kind: "tap", tolerance: 0.08, prompt: "Where does this mora land? Tap when it lands.",
        note: "Adi, one avartanam of count-in. The final samam is muted.",
        play: async () => {
          const at = ctx().currentTime + 0.2, b = 60 / 60, m = b / 4; // chatusra: 4 matras a count
          const total = 5 * 3 + 2 * 2; // 19 matras
          const start = 32 * 2 - total; // lands on the samam after 2 avartanams
          talaCues(T("adi").counts, at, b, 2);
          for (let r = 0; r < 3; r++) for (let k = 0; k < 5; k++) blip(k === 0 ? 1320 : 990, at + (start + r * 7 + k) * m, 0.05, 0.07);
          landing = at + 32 * 2 * m;
          return landing + b;
        },
        tapAt: () => landing, explain: "Three times five, with two gaps of two, is 19 matras: started 19 before samam, it lands on samam." };
    }
    case "TL.10": {
      let change: number | null = null;
      const from = pick([4, 3]), to = pick([5, 3, 4].filter((x) => x !== from));
      return { ...base, source: "Konnakol cues", card: `TL.10:${from}-${to}`, kind: "tap", tolerance: 0.5 * (60 / 60), prompt: "Tap when the nadai changes.",
        play: async () => {
          const at = ctx().currentTime + 0.2, b = 60 / 60;
          const n = 4 + Math.floor(Math.random() * 4);
          for (let c = 0; c < 12; c++) { talaSound(c % 8 === 0 ? "clap" : "finger", at + c * b, { samam: c % 8 === 0 }); const sub = c < n ? from : to; for (let k = 0; k < sub; k++) blip(k === 0 ? 1320 : 990, at + c * b + (k * b) / sub, 0.04, 0.06); }
          change = at + n * b;
          return at + 12 * b;
        },
        tapAt: () => change, explain: `It changed from ${from} to ${to} to a count. Within half a count is right.` };
    }
    default: {
      const recs = d.recs.filter((r) => (r.annotations?.korvais ?? []).length);
      if (!recs.length) return unavailable(level.id, "No recording has a korvai landing marked yet. This drill opens when Shruti annotates one.");
      const r = pick(recs);
      const k = pick(r.annotations.korvais) as { start: string; landing: number };
      let t0 = 0;
      return { ...base, source: "Recording · Shruti's annotation", card: `TL.11:${r.id}`, kind: "tap", tolerance: 0.15, prompt: "Tap where the korvai lands.",
        play: async (box) => { t0 = ctx().currentTime; await recPlayer(r, { start: k.start, end: "" })!(box); },
        tapAt: () => t0 + (k.landing - (k.start ? k.start.split(":").reduce((a, x) => a * 60 + Number(x), 0) : 0)), explain: "Within 150 ms of Shruti's mark is right." };
    }
  }
}

const RG = ["R1 G1", "R1 G2", "R1 G3", "R2 G2", "R2 G3", "R3 G3"];
const DN = ["D1 N1", "D1 N2", "D1 N3", "D2 N2", "D2 N3", "D3 N3"];

function ms(level: Level, d: Data): Question {
  const m = pick(d.melas);
  const n = Number(m.number);
  const half = n > 36 ? n - 36 : n;
  const rg = Math.floor((half - 1) / 6), dn = (half - 1) % 6;
  const base = { level: level.id, source: `${SYNTH} · a scale, not a raga`, lesson: level.unlockedBy, note: "A scale, not a raga: played plain, up and down.",
    play: phrasePlayer(`${m.arohana} ${m.avarohana}`, undefined, 0.45) };
  const pairLabel = (p: string) => p.split(" ").map(SHORT).join(" ");
  switch (level.id) {
    case "MS.01": return { ...base, card: `MS.01:${rg}`, kind: "choice", prompt: "Which Ri and Ga?", options: RG.map((p, i) => ({ id: String(i), label: pairLabel(p) })), answer: String(rg),
      explain: `${pairLabel(RG[rg])}: mela ${n}, ${m.name}, is in chakra ${m.chakra?.number} (${m.chakra?.name}).` };
    case "MS.02": return { ...base, card: `MS.02:${dn}`, kind: "choice", prompt: "Which Dha and Ni?", options: DN.map((p, i) => ({ id: String(i), label: pairLabel(p) })), answer: String(dn),
      explain: `${pairLabel(DN[dn])}: position ${dn + 1} in its chakra. Mela ${n}, ${m.name}.` };
    case "MS.03": return { ...base, card: `MS.03:${m.madhyama}`, kind: "choice", prompt: "M₁ or M₂?", options: [{ id: "M1", label: "M₁ (suddha)" }, { id: "M2", label: "M₂ (prati)" }], answer: m.madhyama,
      explain: `${SHORT(m.madhyama)}: melas 1-36 take M₁ and 37-72 take M₂. This was ${n}, ${m.name}.` };
    default: return { ...base, card: "MS.04", kind: "number", prompt: "Which mela number? (Ri-Ga, Dha-Ni and Ma together.)", answer: n,
      explain: `${n > 36 ? "36 (M₂) + " : ""}6 × ${rg} (the Ri-Ga pair, ${pairLabel(RG[rg])}) + ${dn + 1} (the Dha-Ni pair, ${pairLabel(DN[dn])}) = ${n}: ${m.name}.` };
  }
}

function fm(level: Level, d: Data): Question {
  const want: Record<string, string[]> = {
    "FM.01": ["pallavi", "anupallavi", "charanam"],
    "FM.02": ["kalpita", "manodharma"],
    "FM.03": ["alapana", "tanam", "kriti", "niraval", "kalpanaswaram", "tani"],
  };
  const improv = new Set(["alapana", "tanam", "niraval", "kalpanaswaram", "tani", "viruttam"]);
  const cands: { r: Rec; start: string; end: string; label: string }[] = [];
  for (const r of d.recs) {
    const secs = [...r.sections].sort((a, b) => a.t.localeCompare(b.t));
    secs.forEach((s, i) => {
      const lab = s.label.toLowerCase().trim().split(/\s+/)[0];
      const key = level.id === "FM.02" ? (improv.has(lab) ? "manodharma" : want["FM.01"].includes(lab) || lab === "kriti" ? "kalpita" : "") : lab;
      if (want[level.id].includes(key)) cands.push({ r, start: s.t, end: secs[i + 1]?.t ?? "", label: key });
    });
  }
  if (!cands.length) return unavailable(level.id, "No recording has its sections marked yet. This drill opens when Shruti annotates one.");
  const c = pick(cands);
  return { level: level.id, card: `${level.id}:${c.label}`, source: "Recording · Shruti's section marks", lesson: level.unlockedBy, kind: "choice",
    prompt: level.id === "FM.02" ? "Composed (kalpita) or improvised (manodharma)?" : level.id === "FM.01" ? "Which section is this clip?" : "Which item of a main piece is this?",
    play: recPlayer(c.r, c), options: want[level.id].map((x) => ({ id: x, label: x[0].toUpperCase() + x.slice(1) })), answer: c.label,
    explain: `Shruti marked this as ${c.label}${c.r.composition ? `, in ${c.r.composition}` : ""}.` };
}

export function makeQuestion(level: Level, d: Data, done: (lesson: string) => boolean): Question {
  const step = rung(level.id, Math.max(1, level.ladder?.length || 4));
  switch (level.family) {
    case "SW": return sw(level, d, step);
    case "PD": return pd(level, d, step);
    case "PR": return pr(level, d, done);
    case "RR": return rr(level, d);
    case "GM": return gm(level, d, step);
    case "TL": return tl(level, d, step);
    case "MS": return ms(level, d);
    default: return fm(level, d);
  }
}

// ── data ───────────────────────────────────────────────────────────────────

let dataP: Promise<Data> | null = null;
export function earData(drills: Drills): Promise<Data> {
  if (!dataP) {
    dataP = Promise.all([
      genData(),
      fetch("/api/carnatic/data/ragas.json").then((r) => (r.ok ? r.json() : null)).catch(() => null),
      fetch("/api/carnatic/listening/recordings").then((r) => (r.ok ? r.json() : { items: [] })).catch(() => ({ items: [] })),
    ]).then(([g, ragas, recs]): Data => ({
      ...g, drills,
      janyasFull: [...(ragas?.janyas ?? []), ...(ragas?.performed ?? [])],
      recs: (recs.items ?? []).filter((r: Rec) => r.status === "approved"),
    }));
  }
  return dataP;
}

// ── a session ──────────────────────────────────────────────────────────────

export interface SessionOpts {
  script: Script; tamil?: TamilStyle; size?: number;
  lessonHref: (id: string) => { title: string; href: string } | null;
  done: (lesson: string) => boolean;
  backHref: string;
  /** Review: due cards across levels instead of one level. */
  review?: boolean;
  /** PR drills: keep to these confusable sets ("C4,C5"). */
  set?: string | null;
  /** Inside a checkpoint: no page chrome, and the result goes here. */
  embedded?: (right: number, of: number) => void;
}

export async function runSession(root: HTMLElement, levels: Level[], drills: Drills, o: SessionOpts) {
  const d = await earData(drills);
  preferSet = o.set ?? null;
  const size = o.size ?? 12;
  const byId = new Map(drills.levels.map((l) => [l.id, l]));
  let queue: Level[] = o.review
    ? dueCards().map((c) => byId.get(c.key.split(":")[0])).filter((x): x is Level => !!x).slice(0, 20)
    : Array.from({ length: size }, () => levels[0]);
  if (!queue.length) {
    root.innerHTML = `<p class="lr-eyebrow-top">Ear training · review</p><h1 class="lr-title">Nothing to review</h1><p class="ch-empty">No ear-training cards are due. They come back on their own schedule.</p><div class="st-actions"><a class="lr-link" href="${esc(o.backHref)}">Back to Ear training</a></div>`;
    return;
  }
  const total = queue.length;
  const results: { q: Question; right: boolean }[] = [];
  let retry: { q: Question; after: number }[] = [];
  let shown = 0;
  const started = new Date().toISOString(), t0 = Date.now();
  const lvl = levels[0];

  const next = () => {
    const due = retry.find((r) => r.after <= shown);
    if (due) { retry = retry.filter((r) => r !== due); return due.q; }
    const l = queue.shift();
    return l ? makeQuestion(l, d, o.done) : null;
  };

  const show = () => {
    const q = next();
    if (!q) return finish();
    if (q.kind === "unavailable") {
      if (o.embedded) { root.innerHTML = `<p class="ex-partial">${esc(q.prompt)}</p>`; o.embedded(0, 0); return; }
      root.innerHTML = `<p class="lr-eyebrow-top">Ear training · ${esc(q.level)}</p><h1 class="lr-title">${esc(byId.get(q.level)?.title ?? q.level)}</h1><p class="ch-empty">${esc(q.prompt)}</p><div class="st-actions"><a class="lr-link" href="${esc(o.backHref)}">Back to Ear training</a></div>`;
      return;
    }
    shown++;
    const level = byId.get(q.level)!;
    const bar = Array.from({ length: total }, (_, i) => `<i class="${i < results.length ? "done" : i === results.length ? "now" : ""}"></i>`).join("");
    root.innerHTML = (o.embedded ? `<div class="et-top"><span></span>` : `<div class="et-top"><a class="lr-link" href="${esc(o.backHref)}">‹ End session</a>`) + `<span>${esc(level.id)} · ${esc(level.title.toLowerCase())}</span><span class="mono">${Math.min(results.length + 1, total)} / ${total}</span></div>`
      + `<div class="et-bar">${bar}</div>`
      + `<div class="ex-card et-card"><div class="ex-head"><span class="ex-eyebrow">Ear training · ${esc(level.id)} · ${esc(level.title)}</span><span class="ex-id">${esc(q.card)}</span></div>`
      + `<div class="ex-body"><p class="ex-prompt">${esc(q.prompt)}</p>`
      + `<div class="et-play"><button type="button" class="lr-play lr-play-lg" data-play aria-label="Play"><svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M5 3l8 5-8 5z" fill="currentColor"/></svg></button>`
      + `<span><b>Play again as often as you like</b><small>${esc(q.source)}</small></span></div>`
      + `<div class="et-rec" data-rec></div>`
      + (q.note ? `<p class="ex-note">${esc(q.note)}</p>` : "")
      + `<div data-answer></div></div></div>`;
    const recBox = root.querySelector<HTMLElement>("[data-rec]")!;
    const playBtn = root.querySelector<HTMLButtonElement>("[data-play]")!;
    let playedAt = 0;
    playBtn.addEventListener("click", () => { playedAt = Date.now(); void q.play?.(recBox); });
    if (q.play && q.source.startsWith("Synth")) setTimeout(() => { playedAt = Date.now(); void q.play?.(recBox); }, 300);
    const box = root.querySelector<HTMLElement>("[data-answer]")!;
    const answered = (right: boolean, extra = "") => {
      const fast = playedAt ? Date.now() - playedAt < level.fluentMs : false;
      results.push({ q, right });
      if (!o.review) noteAnswer(q.level, right);
      ensureCard(q.card);
      review(q.card, right, right && fast);
      if (!right) retry.push({ q: makeQuestion(level, d, o.done), after: shown + 3 });
      const from = q.lesson ? o.lessonHref(q.lesson) : null;
      box.querySelectorAll<HTMLButtonElement>("button, input").forEach((b) => { b.disabled = true; });
      box.insertAdjacentHTML("beforeend", `<div class="ex-explain"><p class="ex-verdict">${right ? "Yes." : "Not quite. We'll come back to this one."}</p>${extra}<p>${esc(q.explain)}</p>${from ? `<a class="ex-from" href="${esc(from.href)}">From “${esc(from.title)}” ›</a>` : ""}</div>`
        + `<div class="ex-actions"><button type="button" class="ex-btn" data-next>${results.length >= total && !retry.length ? "Finish" : "Next"}</button></div>`);
      box.querySelector<HTMLButtonElement>("[data-next]")!.disabled = false;
      box.querySelector("[data-next]")!.addEventListener("click", show);
    };
    if (q.kind === "choice" || q.kind === "multi") {
      const many = q.kind === "multi";
      box.innerHTML = `<div class="ex-opts${many ? " ex-multi" : ""}">${q.options!.map((op) => `<button type="button" class="ex-opt" data-opt="${esc(op.id)}" aria-pressed="false"><span class="ex-mark"></span><span class="ex-opt-t">${esc(op.label)}</span><span class="ex-tag"></span></button>`).join("")}</div>`
        + (many ? `<div class="ex-actions"><button type="button" class="ex-btn" data-check>Check</button></div>` : "");
      const accept = new Set(Array.isArray(q.answer) ? q.answer : q.accept ?? [String(q.answer)]);
      const mark = (picked: Set<string>) => {
        box.querySelectorAll<HTMLElement>("[data-opt]").forEach((b) => {
          const id = b.dataset.opt!;
          const ok = accept.has(id);
          if (picked.has(id)) { b.classList.add(ok ? "is-right" : "is-wrong"); b.querySelector(".ex-tag")!.textContent = "your answer"; }
          else if (ok) { b.classList.add("is-missed"); b.querySelector(".ex-tag")!.textContent = "answer"; }
        });
        box.querySelector("[data-check]")?.closest(".ex-actions")?.remove();
        const right = many ? [...accept].every((x) => picked.has(x)) && [...picked].every((x) => accept.has(x)) : [...picked].some((x) => accept.has(x));
        answered(right);
      };
      const picked = new Set<string>();
      box.querySelectorAll<HTMLElement>("[data-opt]").forEach((b) => b.addEventListener("click", () => {
        const id = b.dataset.opt!;
        if (!many) { picked.add(id); b.setAttribute("aria-pressed", "true"); mark(picked); return; }
        if (picked.has(id)) picked.delete(id); else picked.add(id);
        b.setAttribute("aria-pressed", String(picked.has(id)));
      }));
      box.querySelector("[data-check]")?.addEventListener("click", () => mark(picked));
    } else if (q.kind === "sargam") {
      box.innerHTML = `<div data-pad-host></div><div class="ex-actions"><button type="button" class="ex-btn" data-check>Check</button></div>`;
      const pad = sargamPad(box.querySelector<HTMLElement>("[data-pad-host]")!, { script: o.script, tamil: o.tamil });
      box.querySelector("[data-check]")!.addEventListener("click", () => {
        const res = checkSargam(pad.value(), String(q.answer), q.rule ?? {});
        box.querySelector("[data-check]")!.closest(".ex-actions")!.remove();
        box.querySelector<HTMLElement>("[data-pad-host]")!.innerHTML = sargamResultHtml(res, { script: o.script, tamil: o.tamil } as any);
        answered(res.right, `<p class="ex-partial">${esc(res.sentence)}</p>`);
      });
    } else if (q.kind === "number" || q.kind === "text") {
      box.innerHTML = q.kind === "number"
        ? `<label class="ex-num"><input inputmode="numeric" data-in aria-label="Your answer"></label><div class="ex-actions"><button type="button" class="ex-btn" data-check>Check</button></div>`
        : `<div class="ex-text"><input data-in aria-label="Your answer" autocomplete="off"></div><div class="ex-actions"><button type="button" class="ex-btn" data-check>Check</button></div>`;
      const input = box.querySelector<HTMLInputElement>("[data-in]")!;
      const go = () => {
        const v = input.value.trim();
        if (!v) return;
        const right = q.kind === "number" ? Number(v) === Number(q.answer) : checkText(v, q.accept ?? [String(q.answer)]) || ragaKey(v) === ragaKey(String(q.answer));
        box.querySelector("[data-check]")!.closest(".ex-actions")!.remove();
        answered(right, right ? "" : `<p class="ex-partial">The answer: ${esc(String(q.answer))}.</p>`);
      };
      box.querySelector("[data-check]")!.addEventListener("click", go);
      input.addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
      input.focus();
    } else if (q.kind === "tap") {
      box.innerHTML = `<button type="button" class="tt-pad" data-tap>Tap here (or press space)</button><p class="tt-note" data-tap-note>Press play, then tap once at the moment.</p>`;
      const pad = box.querySelector<HTMLButtonElement>("[data-tap]")!;
      let off = () => {};
      const tap = (_kind: string, at: number) => {
        const target = q.tapAt?.();
        if (target == null) { box.querySelector("[data-tap-note]")!.textContent = "Press play first."; return; }
        const d = at - target;
        const right = Math.abs(d) <= (q.tolerance ?? 0.08);
        off();
        pad.remove();
        answered(right, `<p class="ex-partial">${Math.abs(d) < 0.01 ? "Right on it." : `${Math.round(Math.abs(d) * 1000)} ms ${d < 0 ? "early" : "late"}.`}</p>`);
      };
      off = attachPad(pad, { onTap: tap });
    }
  };

  const finish = () => {
    const right = results.filter((r) => r.right).length;
    if (o.embedded) {
      if (!o.review) noteSession(lvl.id, right, results.length);
      root.innerHTML = `<p class="ex-partial">${right} of ${results.length} right the first time.</p>`;
      o.embedded(right, results.length);
      return;
    }
    const back = new Set(results.filter((r) => !r.right).map((r) => r.q.card)).size;
    const itemId = o.review ? "ear-review" : lvl.id;
    if (!o.review) noteSession(lvl.id, right, results.length);
    recordAttempt({ itemId, kind: "drill", startedAt: started, seconds: Math.round((Date.now() - t0) / 1000), result: { right, of: results.length } });
    const words = ["No", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty"];
    const W = (n: number) => words[n] ?? String(n);
    const title = back ? `${W(right)} you heard, ${W(back).toLowerCase()} coming back` : `${W(right)} of ${W(results.length).toLowerCase()} the first time`;
    const missed = [...new Set(results.filter((r) => !r.right).map((r) => r.q.card.split(":")[1]).filter(Boolean))];
    const lede = back ? `The ones you missed${missed.length ? ` (${missed.slice(0, 3).map((m) => m.replace(/-/g, " against ")).join(", ")})` : ""} come back in review.` : "Nothing is coming back from this session.";
    const st = o.review ? null : levelState(lvl.id);
    const best = st?.sessions.slice(0, -1).reduce<{ right: number; of: number; at: string } | null>((b, s) => (!b || s.right / s.of > b.right / b.of ? s : b), null);
    const word = st ? wordFor(st.recent.filter(Boolean).length, st.recent.length) : "";
    const suggest = !o.review && comfortable(lvl.id) ? drills.levels.find((l) => l.family === lvl.family && l.id > lvl.id) : null;
    root.innerHTML = `<p class="lr-eyebrow-top">${esc(o.review ? "Review" : lvl.id)} · session done · ${results.length} items</p><h1 class="lr-title">${esc(title)}</h1><p class="st-lede">${esc(lede)}</p>`
      + (st ? `<div class="st-next"><b>${esc(lvl.title)} · ${esc(word)}</b><p>${best ? `Best session so far: ${best.right} of ${best.of}, ${new Date(best.at).toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" })}.` : "Your first session at this level."}${suggest ? ` 16 of your last 20 were right: <a href="?level=${esc(suggest.id)}">${esc(suggest.id)}, ${esc(suggest.title.toLowerCase())}</a> is ready when you are.` : ""}</p></div>` : "")
      + `<div class="st-actions"><button type="button" class="lr-btn" data-again>Another session</button><a class="lr-link" href="${esc(o.backHref)}">Back to Ear training</a></div>`;
    root.querySelector("[data-again]")!.addEventListener("click", () => { void runSession(root, levels, drills, o); });
  };
  show();
}

/** The family's history as words over time, for the skill map chart. */
export function familyHistory(levels: Level[]): { word: "new" | "getting there" | "comfortable"; highest: string | null; points: number[] } {
  const ids = levels.map((l) => l.id);
  const comfy = ids.filter((id) => comfortable(id));
  const highest = comfy.length ? comfy[comfy.length - 1] : null;
  const sessions = ids.flatMap((id) => levelState(id).sessions.map((s) => ({ ...s, id }))).sort((a, b) => a.at.localeCompare(b.at));
  const recent = ids.flatMap((id) => levelState(id).recent);
  const word = highest ? "comfortable" : recent.length ? wordFor(recent.filter(Boolean).length, recent.length) : "new";
  const points = sessions.slice(-8).map((s) => s.right / Math.max(1, s.of));
  return { word, highest, points };
}

export { attempts };
