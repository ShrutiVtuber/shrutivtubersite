/* The sargam line, drawn as HTML strings — isomorphic, so the server renders
 * every line on the page and the player, trainer and composer redraw theirs
 * in the browser with exactly the same markup.
 *
 * Anatomy of one note, top to bottom (Foundations v2 §03): gamaka mark (rose,
 * 16px) · speed lines (1px ink, one per speed above the first, in the count's
 * header) · tara dot · the swara with its variant subscript at 0.5em · mandra
 * dot · sahitya (italic serif, under a dotted rule).
 *
 * ⚠ Octave dots are drawn; the data's S' and .P never reach the page. Dots
 * and marks are never the only carrier of meaning: every note carries an
 * aria-label ("tara Sa", "Ri two", "hold").
 */
import {
  type Script, type TamilStyle, type Token, GAMAKA_SIGN, gamakaName, letter, numeral, signBefore, spoken, tokenize,
} from "./notation";

export interface DrawOptions {
  script: Script;
  tamil?: TamilStyle;
  /** Variant subscripts: always, or only where they add information. */
  subs?: boolean | string[];
  /** Mark notes outside the raga with a dotted underline (the composer's flag). */
  outside?: Set<string>;
}

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export function noteHtml(t: Token, o: DrawOptions, extraClass = ""): string {
  if (t.kind === "hold") {
    return `<span class="sn sn-hold ${extraClass}" aria-label="${spoken(t)}"><span class="sn-g"></span><span class="sn-up"></span><span class="sn-l">${t.units === 2 ? ";" : ","}</span><span class="sn-dn"></span></span>`;
  }
  if (t.kind !== "note" || !t.swara) {
    return `<span class="sn sn-text ${extraClass}"><span class="sn-g"></span><span class="sn-up"></span><span class="sn-l">${esc(t.raw)}</span><span class="sn-dn"></span></span>`;
  }
  const up = (t.octave ?? 0) > 0 ? `<i></i>`.repeat(Math.min(2, t.octave ?? 0)) : "";
  const dn = (t.octave ?? 0) < 0 ? `<i></i>`.repeat(Math.min(2, -(t.octave ?? 0))) : "";
  const wantSub = Array.isArray(o.subs) ? o.subs.includes(t.swara) : o.subs;
  const sub = wantSub && t.variant ? `<sub>${numeral(t.variant, o.script)}</sub>` : "";
  const sign = t.gamaka ? GAMAKA_SIGN[t.gamaka] ?? "" : "";
  const g = sign && !signBefore(t.gamaka)
    ? `<span class="sn-g" title="${esc(gamakaName(t.gamaka!))}">${esc(sign)}</span>` : `<span class="sn-g"></span>`;
  const before = sign && signBefore(t.gamaka) ? `<span class="sn-pre" title="${esc(gamakaName(t.gamaka!))}">${esc(sign)}</span>` : "";
  const name = t.swara + (t.variant ?? "");
  const cls = ["sn", extraClass, t.anya ? "sn-anya" : "", t.vakra ? "sn-vakra" : "", t.hint ? "sn-hint" : "",
    o.outside?.has(name) ? "sn-outside" : ""].filter(Boolean).join(" ");
  const glyph = letter(t.swara, o.script, o.tamil);
  const label = spoken(t) + (t.anya ? ", anya swara" : "") + (t.hint ? ", a faint hint" : "");
  return `<span class="${cls}" role="img" aria-label="${esc(label)}">${g}<span class="sn-up">${up}</span>`
    + `<span class="sn-l">${before}${t.hint ? "(" : ""}${glyph}${sub}${t.hint ? ")" : ""}</span><span class="sn-dn">${dn}</span></span>`;
}

/** A phrase or a scale: a row of notes. `·` in the data is a quiet separator. */
export function phraseHtml(line: string, o: DrawOptions): string {
  const cells = tokenize(line).map((t) =>
    t.kind === "text" && t.raw === "·" ? `<span class="sn-sep" aria-hidden="true">·</span>` : noteHtml(t, o));
  return `<span class="sn-row">${cells.join("")}</span>`;
}

/** Plain text of a line in a script, for places a glyph row does not fit (select options, titles). */
export function phraseText(line: string, o: DrawOptions): string {
  const sub = "₀₁₂₃";
  return tokenize(line).map((t) => {
    if (t.kind !== "note" || !t.swara) return t.raw;
    const v = (Array.isArray(o.subs) ? o.subs.includes(t.swara) : o.subs) && t.variant ? (o.script === "kn" ? numeral(t.variant, "kn") : sub[t.variant]) : "";
    const dot = (t.octave ?? 0) > 0 ? "̇" : (t.octave ?? 0) < 0 ? "̣" : "";
    return letter(t.swara, o.script, o.tamil) + dot + v;
  }).join(" ");
}

export interface Avartanam {
  /** Notes per count, count by count ([["S"],["R"]…] or [["S","R"],…]). */
  counts: string[][];
  /** Anga sizes in counts ([4,2,2] for Adi); a bar after each, a double bar at the end. */
  angas: number[];
  sahitya?: (string | null | undefined)[];
  /** 1 = one note a count; 2 = two; 3 = four (a speed line per speed above the first). */
  speed?: number;
  /** Extra rows per count (mridangam strokes), faint. */
  strokes?: (string[] | null | undefined)[];
}

/**
 * One avartanam on the tala grid. Each count is a fixed column: faster speeds
 * put more notes into the column instead of widening it, so lines at every
 * speed stay aligned to the beat. `data-count` lets a playhead find it.
 */
export function avartanamHtml(a: Avartanam, o: DrawOptions, lineIndex = 0): string {
  const speed = a.speed ?? 1;
  const lines = speed > 1 ? `<span class="sl-speed">${`<i></i>`.repeat(speed - 1)}</span>` : `<span class="sl-speed"></span>`;
  const bars = new Set<number>();
  let at = 0;
  for (const size of a.angas) {
    at += size;
    bars.add(at - 1);
  }
  const cells = a.counts.map((notes, i) => {
    const toks = notes.flatMap((n) => tokenize(n));
    const body = toks.map((t) => noteHtml(t, o)).join("");
    const sa = a.sahitya?.[i];
    const st = a.strokes?.[i];
    const bar = i === a.counts.length - 1 ? " sl-end" : bars.has(i) ? " sl-bar" : "";
    return `<span class="sl-count${bar}" data-count="${i}" data-line="${lineIndex}">${lines}`
      + `<span class="sl-notes" data-n="${toks.length}">${body}</span>`
      + (a.sahitya ? `<span class="sl-sahitya">${sa ? esc(sa) : "&nbsp;"}</span>` : "")
      + (a.strokes ? `<span class="sl-strokes">${st?.length ? st.map((s) => `<b>${esc(s)}</b>`).join("") : ""}</span>` : "")
      + `</span>`;
  });
  return `<div class="sl" role="group" style="--sl-counts:${a.counts.length}">${cells.join("")}</div>`;
}

/** Split an exercise's segment list into avartanams of counts at a speed (1, 2 or 4 notes a count). */
export function toCounts(segments: string[][], perCount: number): string[][] {
  const flat = segments.flat();
  const out: string[][] = [];
  for (let i = 0; i < flat.length; i += perCount) out.push(flat.slice(i, i + perCount));
  return out;
}
