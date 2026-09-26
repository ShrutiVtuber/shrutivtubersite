/* Checking answers (FORMAT.md §4c). Pure and isomorphic: the reader, Test
 * yourself, the ear trainer and the Studio admin's preview all check the same
 * way, and the app follows the same rules.
 *
 * Nothing here decides anything about the learner. A wrong answer is "not
 * quite", explained, and comes back later; partial credit is a sentence
 * ("13 of 14 swaras. The eighth was Pa, not Ni."), never a percentage.
 */
import { parseToken, spoken, variantsOf } from "./notation";

const ORDINAL = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
  "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth"];
const NAME: Record<string, string> = { S: "Sa", R: "Ri", G: "Ga", M: "Ma", P: "Pa", D: "Dha", N: "Ni" };
const ENHARMONIC: Record<string, string> = { R2: "G1", R3: "G2", D2: "N1", D3: "N2" };

export interface SargamRule {
  raga?: string;
  /** Scale that resolves unnumbered swaras (the raga's arohana + avarohana). */
  scale?: string;
  checkHolds?: boolean;
  checkOctaves?: boolean;
  checkBars?: boolean;
  enharmonic?: "accept" | "reject";
  /** Variant numbers required (a scale question with no raga). */
  variantsRequired?: boolean;
}

export interface NoteKey { key: string; label: string; hold: boolean }

/** A token in comparable form, or null for something that isn't notation. */
export function normaliseToken(raw: string, r: SargamRule, vars: Record<string, number>): NoteKey | null {
  let t = raw.trim();
  if (!t) return null;
  if (t === "|" || t === "||") return r.checkBars ? { key: t, label: t === "|" ? "a bar" : "a double bar", hold: false } : null;
  if (t === "," || t === ";") return r.checkHolds ? { key: t, label: t === ";" ? "a two-unit hold" : "a hold", hold: true } : null;
  t = t.replace(/^[a-z-]+:/i, "");          // gamaka prefixes aren't asked for unless a check says so
  t = t.replace(/^([.]*)([srgmpdn])/, (_m, dots, s) => dots + s.toUpperCase());
  const tok = parseToken(t);
  if (tok.kind !== "note" || !tok.swara) return { key: `?${raw}`, label: `“${raw}”`, hold: false };
  let v = tok.variant ?? null;
  if (tok.swara === "S" || tok.swara === "P") v = null;
  if (v === null && tok.swara !== "S" && tok.swara !== "P" && !r.variantsRequired) v = vars[tok.swara] ?? null;
  let name = `${tok.swara}${v ?? ""}`;
  if (r.enharmonic === "accept" && ENHARMONIC[name]) name = ENHARMONIC[name];
  const oct = r.checkOctaves === false ? 0 : tok.octave ?? 0;
  const label = spoken({ ...tok, variant: v, octave: oct } as any);
  return { key: `${name}@${oct}`, label, hold: false };
}

export function sargamKeys(line: string, r: SargamRule): NoteKey[] {
  const vars = r.scale ? variantsOf(r.scale) : {};
  const out: NoteKey[] = [];
  for (const raw of (line ?? "").split(/\s+/)) {
    if (!raw) continue;
    // "S," is Sa then a hold, as in the composer.
    const m = /^(.+?)(,+)$/.exec(raw);
    const parts = m && m[1] !== "," ? [m[1], ...m[2].split("")] : [raw];
    for (const p of parts) {
      const k = normaliseToken(p, r, vars);
      if (k) out.push(k);
    }
  }
  return out;
}

export interface SargamResult {
  right: boolean;
  matched: number;
  of: number;
  /** Per answer token: ok, or the key's token to draw above it. */
  cells: { given: string; ok: boolean; want?: string; missing?: boolean; extra?: boolean }[];
  sentence: string;
  wrongNumbers: string[];
}

/** Align the learner's tokens with the key (edit distance) and say what differs. */
export function checkSargam(given: string, key: string, r: SargamRule): SargamResult {
  const a = sargamKeys(given, r);
  const b = sargamKeys(key, r);
  const n = a.length, m = b.length;
  const d: number[][] = Array.from({ length: n + 1 }, (_, i) => Array.from({ length: m + 1 }, (_, j) => (i === 0 ? j : j === 0 ? i : 0)));
  for (let i = 1; i <= n; i++) for (let j = 1; j <= m; j++) {
    d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1].key === b[j - 1].key ? 0 : 1));
  }
  const cells: SargamResult["cells"] = [];
  let i = n, j = m, matched = 0;
  const firstWrong: { pos: number; want: NoteKey; got?: NoteKey }[] = [];
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && a[i - 1].key === b[j - 1].key && d[i][j] === d[i - 1][j - 1]) {
      cells.unshift({ given: a[i - 1].key, ok: true }); matched++; i--; j--;
    } else if (i > 0 && j > 0 && d[i][j] === d[i - 1][j - 1] + 1) {
      cells.unshift({ given: a[i - 1].key, ok: false, want: b[j - 1].key });
      firstWrong.unshift({ pos: j - 1, want: b[j - 1], got: a[i - 1] }); i--; j--;
    } else if (j > 0 && d[i][j] === d[i][j - 1] + 1) {
      cells.unshift({ given: "", ok: false, want: b[j - 1].key, missing: true });
      firstWrong.unshift({ pos: j - 1, want: b[j - 1] }); j--;
    } else {
      cells.unshift({ given: a[i - 1].key, ok: false, extra: true }); i--;
    }
  }
  const right = n === m && matched === m;
  const noteCount = b.filter((k) => !k.hold).length;
  const noteMatched = cells.filter((c) => c.ok && !c.given.startsWith(",") && !c.given.startsWith(";")).length;
  let sentence = `${noteMatched} of ${noteCount} swaras.`;
  const w = firstWrong[0];
  if (!right && w) {
    const ord = ORDINAL[w.pos] ?? `number ${w.pos + 1}`;
    sentence += w.got ? ` The ${ord} was ${w.want.label}, not ${w.got.label}.` : ` The ${ord}, ${w.want.label}, is missing.`;
  }
  if (!right && n > m && firstWrong.length === 0) sentence += " There are extra notes at the end.";
  const wrongNumbers = (given.match(/\b[sSpP][123]\b/g) ?? []);
  if (wrongNumbers.length) sentence += " Sa and Pa never take a number.";
  return { right, matched, of: m, cells, sentence, wrongNumbers };
}

// ── text ──────────────────────────────────────────────────────────────────

/** The raga-name normaliser (design-response Q16): Sankarabharanam = Dheerasankarabharanam, Thodi = Todi. */
export function ragaKey(text: string): string {
  let t = text.toLowerCase().trim().replace(/[\s\-_'’.]/g, "");
  t = t.replace(/^(dheera|dhira)/, "");
  for (const [a, b] of [["th", "t"], ["sh", "s"], ["dh", "d"], ["bh", "b"], ["kh", "k"], ["gh", "g"], ["ch", "c"],
    ["w", "v"], ["ow", "au"], ["ou", "au"]] as const) t = t.split(a).join(b);
  t = t.replace(/([aeiou])\1+/g, "$1");
  t = t.replace(/m$/, "").replace(/a$/, "");
  return t;
}

/** Text answers: lower-cased, spaces and hyphens removed, and the raga normaliser applied. */
export function textKey(text: string): string {
  const plain = text.toLowerCase().replace(/♯/g, "#").replace(/[\s\-_]/g, "");
  return plain;
}

export function checkText(given: string, accept: string[]): boolean {
  const g = textKey(given);
  const gr = ragaKey(given);
  return accept.some((a) => textKey(a) === g || (ragaKey(a) === gr && gr.length > 2));
}

// ── numbers ───────────────────────────────────────────────────────────────

export function parseNumber(text: string): number | null {
  const t = text.trim().replace(/\s+/g, "");
  if (!t) return null;
  const frac = /^(-?\d+)\/(\d+)$/.exec(t);
  if (frac) return Number(frac[2]) === 0 ? null : Number(frac[1]) / Number(frac[2]);
  const mixed = /^(\d+)(½|¼|¾)$/.exec(t);
  if (mixed) return Number(mixed[1]) + ({ "½": 0.5, "¼": 0.25, "¾": 0.75 } as Record<string, number>)[mixed[2]];
  const n = Number(t.replace(",", "."));
  return Number.isFinite(n) ? n : null;
}

export function checkNumber(given: string, answer: number, tolerance = 0, close?: number): "right" | "close" | "wrong" {
  const n = parseNumber(given);
  if (n === null) return "wrong";
  if (Math.abs(n - answer) <= tolerance + 1e-9) return "right";
  if (close !== undefined && Math.abs(n - answer) <= close + 1e-9) return "close";
  return "wrong";
}

// ── time ──────────────────────────────────────────────────────────────────

export function seconds(text: string | null | undefined): number | null {
  const t = (text ?? "").trim();
  if (!t) return null;
  const parts = t.split(":").map(Number);
  if (parts.some((p) => !Number.isFinite(p))) return null;
  return parts.reduce((acc, p) => acc * 60 + p, 0);
}

export function clock(s: number): string {
  const m = Math.floor(s / 60);
  const r = Math.round(s - m * 60);
  return `${m}:${String(r).padStart(2, "0")}`;
}

export { NAME as SWARA_NAMES };
