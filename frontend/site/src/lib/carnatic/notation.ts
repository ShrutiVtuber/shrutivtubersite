/* Swara notation: reading the data's tokens and drawing them for people.
 *
 * Isomorphic — the pages render lines on the server and the player, trainer
 * and composer redraw them in the browser from the same functions.
 *
 * ⚠ The data writes octaves in ASCII (S' tara, .P mandra, N2. mandra in the
 * janya file). People never see that: a token becomes a glyph with dots above
 * or below it, and a screen reader hears "tara Sa".
 */

export type Script = "lat" | "ta" | "te" | "kn";
export type TamilStyle = "grantha" | "pure";
export type Swara = "S" | "R" | "G" | "M" | "P" | "D" | "N";

export interface Token {
  kind: "note" | "hold" | "text";
  raw: string;
  swara?: Swara;
  variant?: number | null;
  /** -2 anumandra, -1 mandra, 0 madhya, 1 tara, 2 ati-tara. */
  octave?: number;
  gamaka?: string | null;
  /** An anya swara (from outside the parent mela) in this phrase. */
  anya?: boolean;
  /** Part of a vakra (zigzag) movement. */
  vakra?: boolean;
  /** Written in brackets: a faint hint of a note, not a note sung. */
  hint?: boolean;
  /** "," one unit, ";" two. */
  units?: number;
}

const NOTE = /^(?:([a-z-]+):)?(\(?)(\.{0,2})([SRGMPDN])([123])?('{0,2})(\.?)(\)?)((?:![av])*)$/;

/** Split a line of notation into tokens; a trailing hold comma is its own token. */
export function tokenize(line: string): Token[] {
  const out: Token[] = [];
  for (let raw of (line ?? "").trim().split(/\s+/)) {
    if (!raw) continue;
    let trailing = 0;
    while (raw.length > 1 && raw.endsWith(",")) {
      raw = raw.slice(0, -1);
      trailing += 1;
    }
    out.push(parseToken(raw));
    for (let i = 0; i < trailing; i++) out.push({ kind: "hold", raw: ",", units: 1 });
  }
  return out;
}

export function parseToken(raw: string): Token {
  if (raw === ",") return { kind: "hold", raw, units: 1 };
  if (raw === ";") return { kind: "hold", raw, units: 2 };
  const m = NOTE.exec(raw);
  if (!m) return { kind: "text", raw };
  const [, gamaka, open, low, s, v, high, lowSuffix, , flags] = m;
  return {
    kind: "note",
    raw,
    swara: s as Swara,
    variant: v ? Number(v) : null,
    octave: high.length - low.length - (lowSuffix ? 1 : 0),
    gamaka: gamaka || null,
    anya: flags.includes("!a"),
    vakra: flags.includes("!v"),
    hint: open === "(",
  };
}

/* ── letters ─────────────────────────────────────────────────────────────── */

const LATIN: Record<Swara, string> = { S: "S", R: "R", G: "G", M: "M", P: "P", D: "D", N: "N" };
/* GAPS_PASS_3 §7: the letters native notation prints. Tamil has two styles,
   grantha (ஸ, the default by the owner's decision of 26 Sep 2026) and pure
   Tamil (ச), a setting. */
const TAMIL_GRANTHA: Record<Swara, string> = { S: "ஸ", R: "ரி", G: "க", M: "ம", P: "ப", D: "த", N: "நி" };
const TAMIL_PURE: Record<Swara, string> = { ...TAMIL_GRANTHA, S: "ச" };
const TELUGU: Record<Swara, string> = { S: "స", R: "రి", G: "గ", M: "మ", P: "ప", D: "ద", N: "ని" };
const KANNADA: Record<Swara, string> = { S: "ಸ", R: "ರಿ", G: "ಗ", M: "ಮ", P: "ಪ", D: "ದ", N: "ನಿ" };

export function letter(s: Swara, script: Script, tamil: TamilStyle = "grantha"): string {
  if (script === "ta") return (tamil === "pure" ? TAMIL_PURE : TAMIL_GRANTHA)[s];
  if (script === "te") return TELUGU[s];
  if (script === "kn") return KANNADA[s];
  return LATIN[s];
}

/** Variant numerals: Kannada pages use Kannada numerals (GAPS_PASS_3 §7). */
export function numeral(n: number, script: Script): string {
  return script === "kn" ? "೦೧೨೩"[n] : String(n);
}

const SUBSCRIPT = "₀₁₂₃";
/** For running text and badges ("anya swara D₂"), where a real subscript is wanted. */
export function inline(tok: string, script: Script = "lat", tamil: TamilStyle = "grantha"): string {
  const t = parseToken(tok);
  if (t.kind !== "note" || !t.swara) return tok;
  const v = t.variant ? (script === "kn" ? numeral(t.variant, "kn") : SUBSCRIPT[t.variant]) : "";
  const dot = t.octave && t.octave > 0 ? "̇" : t.octave && t.octave < 0 ? "̣" : "";
  return letter(t.swara, script, tamil) + dot + v;
}

export const GLYPH_SIZE: Record<Script, string> = {
  lat: "var(--notation-size-lat)", ta: "var(--notation-size-ta)",
  te: "var(--notation-size-te)", kn: "var(--notation-size-kn)",
};

/* ── what a screen reader hears ──────────────────────────────────────────── */

const NAMES: Record<Swara, string> = { S: "Sa", R: "Ri", G: "Ga", M: "Ma", P: "Pa", D: "Dha", N: "Ni" };
const OCTAVE_WORD: Record<string, string> = { "-2": "anumandra", "-1": "mandra", "1": "tara", "2": "ati-tara" };
const NUMBER_WORD = ["", "one", "two", "three"];

export function spoken(t: Token): string {
  if (t.kind === "hold") return t.units === 2 ? "hold two" : "hold";
  if (t.kind !== "note" || !t.swara) return t.raw;
  const parts = [];
  if (t.octave) parts.push(OCTAVE_WORD[String(t.octave)]);
  parts.push(NAMES[t.swara]);
  if (t.variant) parts.push(NUMBER_WORD[t.variant]);
  if (t.gamaka) parts.push(`with ${gamakaName(t.gamaka)}`);
  return parts.join(" ");
}

/* ── gamaka signs (after Subbarama Dikshitar's SSP, 1904) ────────────────── */

export const GAMAKA_SIGN: Record<string, string> = {
  kampita: "∿", "jaru-up": "/", "jaru-down": "\\", nokku: "w", sphurita: "∴", pratyahata: "∵",
  ravai: "∧", khandippu: "✓", odukkal: "×", orikkai: "⋎",
};
const GAMAKA_NAME: Record<string, string> = {
  kampita: "kampita", "jaru-up": "etra jaru, a slide up", "jaru-down": "irakka jaru, a slide down",
  nokku: "nokku, stressed from above", sphurita: "sphurita", pratyahata: "pratyahata", ravai: "ravai",
  khandippu: "khandippu", odukkal: "odukkal, stressed from below", orikkai: "orikkai, a flick up at the end",
};
export const gamakaName = (g: string) => GAMAKA_NAME[g] ?? g;
/** Jaru is written BEFORE the note it slides to; every other sign sits above. */
export const signBefore = (g: string | null | undefined) => g === "jaru-up" || g === "jaru-down";

/* ── pitch ───────────────────────────────────────────────────────────────── */

/** Semitones above Sa for a swara and its variant (enharmonics as the melakarta scheme). */
export function semitones(s: Swara, v?: number | null): number {
  switch (s) {
    case "S": return 0;
    case "R": return v === 1 ? 1 : v === 3 ? 3 : 2;
    case "G": return v === 1 ? 2 : v === 2 ? 3 : 4;
    case "M": return v === 2 ? 6 : 5;
    case "P": return 7;
    case "D": return v === 1 ? 8 : v === 3 ? 10 : 9;
    case "N": return v === 1 ? 9 : v === 2 ? 10 : 11;
  }
}

/* The 5-limit table (GAPS_PASS_3 §8; DECISIONS ragas §9): "textbook
   just-intonation values; performers vary". Indexed by semitone. */
export const JI: number[] = [1, 16 / 15, 9 / 8, 6 / 5, 5 / 4, 4 / 3, 45 / 32, 3 / 2, 8 / 5, 5 / 3, 9 / 5, 15 / 8];

export function ratio(semis: number, tuning: "just" | "equal" = "just"): number {
  const octave = Math.floor(semis / 12);
  const within = ((semis % 12) + 12) % 12;
  const r = tuning === "just" ? JI[within] : Math.pow(2, within / 12);
  return r * Math.pow(2, octave);
}

const PC: Record<string, number> = { C: 0, "C#": 1, D: 2, "D#": 3, E: 4, F: 5, "F#": 6, G: 7, "G#": 8, A: 9, "A#": 10, B: 11 };
export const PITCH_CLASSES = Object.keys(PC);

/** "E5" → Hz at A4 = 440. */
export function pitchHz(name: string): number {
  const m = /^([A-G]#?)(-?\d)$/.exec(name);
  if (!m) return 261.63;
  const midi = PC[m[1]] + (Number(m[2]) + 1) * 12;
  return 440 * Math.pow(2, (midi - 69) / 12);
}

export function tokenHz(t: Token, saHz: number, tuning: "just" | "equal" = "just", ragaVariants?: Record<string, number>): number | null {
  if (t.kind !== "note" || !t.swara) return null;
  const v = t.variant ?? ragaVariants?.[t.swara] ?? null;
  return saHz * ratio(semitones(t.swara, v) + 12 * (t.octave ?? 0), tuning);
}

/** The variant each letter takes in a raga, from its scale ("R2", "G3" …). */
export function variantsOf(scale: string): Record<string, number> {
  const out: Record<string, number> = {};
  for (const t of tokenize(scale)) if (t.kind === "note" && t.swara && t.variant) out[t.swara] ??= t.variant;
  return out;
}

/** "E5 · 659.3 Hz" */
export const hzLabel = (hz: number) => `${hz.toFixed(1)} Hz`;
