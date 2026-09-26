/* Raga names in the three Indian scripts, with their review state.
 *
 * Every Tamil, Telugu and Kannada name is an unverified candidate until a
 * native reader clears it in the review queue (/carnatic/admin). A cleared
 * name loses the marker; a corrected one shows the correction.
 *
 * Keys match the backend's queue (routes/carnatic.py `queue_items`):
 * `script:janya:<id>:<lang>`, `script:mela:<n>:<lang>`, and `:ta:pure` for the
 * pure-Tamil spelling. A melakarta sung as a raga (Todi, Kalyani) shows its
 * mela's names, under the mela's keys.
 */
import type { Review, Scripts } from "./data";
import type { TamilStyle } from "./notation";

export type IndicLang = "ta" | "te" | "kn";
export interface ScriptName { lang: IndicLang; text: string; verified: boolean; key: string }

export function scriptName(
  scripts: Scripts | null | undefined, lang: IndicLang, tamil: TamilStyle,
  reviews: Record<string, Review>, base: string,
): ScriptName | null {
  if (!scripts) return null;
  let text: string | null = null;
  let key = `${base}:${lang}`;
  if (lang === "ta") {
    const ta = scripts.ta;
    if (tamil === "pure" && ta?.pure) {
      text = ta.pure;
      key = `${base}:ta:pure`;
    } else {
      text = ta?.grantha ?? ta?.pure ?? null;
      if (!ta?.grantha && ta?.pure) key = `${base}:ta:pure`;
    }
  } else {
    text = scripts[lang];
  }
  if (!text) return null;
  const r = reviews[key];
  if (r?.status === "corrected" && r.text) return { lang, text: r.text, verified: true, key };
  return { lang, text, verified: r?.status === "confirmed", key };
}

export function allScriptNames(
  scripts: Scripts | null | undefined, tamil: TamilStyle, reviews: Record<string, Review>, base: string,
): ScriptName[] {
  return (["ta", "te", "kn"] as IndicLang[])
    .map((l) => scriptName(scripts, l, tamil, reviews, base))
    .filter((x): x is ScriptName => Boolean(x));
}

export const ragaKey = (r: { id: string; kind: string; number?: number; parent: { number: number } }) =>
  r.kind === "melakarta" ? `script:mela:${r.number ?? r.parent.number}` : `script:janya:${r.id}`;

/* ── search ──────────────────────────────────────────────────────────────── */

/**
 * The spelling normaliser (research response Q16): th/t, sh/s, dh/d, aa/a,
 * ee/i, oo/u, doubled consonants, v/w, ow/au, a final -m or -am, "dheera-"
 * and "dhira-", and no spaces or hyphens. "Sankarabharanam" finds 29
 * Dheerasankarabharanam because the mela prefix is optional.
 */
export function normalise(s: string): string {
  let t = s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();
  t = t.replace(/[\s\-_.'’]/g, "");
  t = t.replace(/^(dheera|dhira)/, "");
  t = t.replace(/ow/g, "au").replace(/w/g, "v");
  t = t.replace(/([kgcjtdpbs])h/g, "$1");
  t = t.replace(/aa/g, "a").replace(/ee/g, "i").replace(/oo/g, "u");
  t = t.replace(/(.)\1+/g, "$1");
  t = t.replace(/m$/, "").replace(/a$/, "");
  return t;
}
