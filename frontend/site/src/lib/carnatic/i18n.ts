/* Swara Studio's languages: English, Tamil, Telugu and Kannada.
 *
 * The site header stays English (the site's languages are its own); the
 * school below it speaks the visitor's choice. The language travels in the
 * address (?lang=ta) so every page in every language has its own URL, for
 * search engines and for sharing, and is remembered in a cookie so a visitor
 * who chose Tamil once is not sent back to English by a bare link.
 *
 * ⚠ Every Tamil, Telugu and Kannada string is a draft awaiting a native
 * reader (DECISIONS ragas §10; the design's translations are marked as drafts
 * too). Pages in those languages carry the "unverified" marker beside the
 * language switcher until the review queue clears the language.
 *
 * English strings are editable from the admin like every other word on the
 * site (copy page "carnatic"); the other languages are editable per language
 * (copy pages "carnatic.ta" and so on), falling back to the drafts here.
 */
import { copy } from "../copy";
import { STRINGS, type Key } from "./strings";

export type Lang = "en" | "ta" | "te" | "kn";
export const LANGS: Lang[] = ["en", "ta", "te", "kn"];
export const LANG_LABEL: Record<Lang, string> = { en: "EN", ta: "தமிழ்", te: "తెలుగు", kn: "ಕನ್ನಡ" };
export const LANG_NAME: Record<Lang, string> = { en: "English", ta: "Tamil", te: "Telugu", kn: "Kannada" };
export const LANG_COOKIE = "swara_lang";

const isLang = (v: unknown): v is Lang => typeof v === "string" && (LANGS as string[]).includes(v);

/** The page's language: the address first, then the remembered choice, then English. */
export function langOf(astro: { url: URL; cookies?: any }): Lang {
  const asked = astro.url.searchParams.get("lang");
  if (isLang(asked)) return asked;
  const kept = astro.cookies?.get?.(LANG_COOKIE)?.value;
  return isLang(kept) ? kept : "en";
}

/** A link inside the school, in the page's language. */
export function hrefIn(lang: Lang, path: string): string {
  if (lang === "en") return path;
  const [base, hash] = path.split("#");
  const sep = base.includes("?") ? "&" : "?";
  return `${base}${sep}lang=${lang}${hash ? "#" + hash : ""}`;
}

export type T = ((key: Key, vars?: Record<string, string | number>) => string) & { lang: Lang; has: (key: Key) => boolean };

/**
 * The words for one page render. `t("landing.h1")` gives the page's language
 * where a draft exists and English otherwise; `{n}` placeholders are filled.
 */
export async function words(lang: Lang): Promise<T> {
  const say = await copy(lang === "en" ? "carnatic" : `carnatic.${lang}`);
  const fill = (s: string, vars?: Record<string, string | number>) =>
    vars ? s.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? String(vars[k]) : m)) : s;
  const t = ((key: Key, vars?: Record<string, string | number>) => {
    const row = STRINGS[key];
    if (!row) return key;
    const draft = lang === "en" ? row[0] : (row[LANGS.indexOf(lang)] || row[0]);
    return fill(say(key, draft), vars);
  }) as T;
  t.lang = lang;
  t.has = (key: Key) => lang === "en" || Boolean(STRINGS[key]?.[LANGS.indexOf(lang)]);
  return t;
}

/** Leading and tracking per script (tokens --leading-indic, --tracking-eyebrow-indic). */
export const isIndic = (lang: Lang) => lang !== "en";
