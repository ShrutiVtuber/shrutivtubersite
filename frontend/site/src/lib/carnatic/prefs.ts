/* What this visitor has chosen: script, instrument, Sa, drone — read on the
 * server so a page renders in their script and for their Sa from the first
 * paint, not after a script has run.
 *
 * Signed out, the choices live in the browser (localStorage, mirrored into
 * the `swara_prefs` cookie so the server can read them). Signed in, the
 * account's settings win, so a phone and a laptop agree.
 */
import { asReader } from "../account";
import type { Lang } from "./i18n";
import type { Script, TamilStyle } from "./notation";
import { pitchHz } from "./notation";

export interface Settings {
  lang: Lang; swaraLetters: "latin" | "interface"; tamilStyle: TamilStyle; theme: "dawn" | "dusk" | "system";
  instrument: "voice" | "venu" | "veena" | "violin" | "mridangam"; hand: "right" | "left";
  sa: string; flute: string; droneTuning: "pa" | "ma" | "ni" | "mute"; playbackTuning: "just" | "equal";
  subscripts: "info" | "always"; otherScripts: "show" | "hide"; tempo: number;
  fourthSpeed: boolean; eighthAlankaram: boolean;
}

/* DECISIONS.md, 26 Sep 2026: voice C, flute the learner's (E5 suggested),
   veena E3, violin E. Kept in step with backend core/carnatic.py. */
export const DEFAULT_SA: Record<Settings["instrument"], string> = {
  voice: "C3", venu: "E5", veena: "E3", violin: "E4", mridangam: "C3",
};

export const DEFAULTS: Settings = {
  lang: "en", swaraLetters: "latin", tamilStyle: "grantha", theme: "system", instrument: "voice",
  hand: "right", sa: DEFAULT_SA.voice, flute: "E", droneTuning: "pa", playbackTuning: "just",
  subscripts: "info", otherScripts: "show", tempo: 60, fourthSpeed: false, eighthAlankaram: false,
};

export const PREFS_COOKIE = "swara_prefs";

export interface Me {
  signedIn: boolean; displayName?: string; supporter?: boolean;
  limits: { partsPerSong: number | null }; settings: Settings | null; settingsUpdatedAt?: string | null;
}

function fromCookie(astro: any): Partial<Settings> {
  try {
    const raw = astro.cookies?.get(PREFS_COOKIE)?.value;
    if (!raw) return {};
    const parsed = JSON.parse(decodeURIComponent(raw));
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

export async function visitor(astro: any): Promise<{ me: Me; settings: Settings }> {
  const signedIn = Boolean(astro.locals?.signedIn);
  let me: Me = { signedIn: false, limits: { partsPerSong: 2 }, settings: null };
  if (signedIn) {
    const r = await asReader(astro, "/api/carnatic/me");
    if (r.ok && r.body) me = r.body as Me;
  }
  const settings = { ...DEFAULTS, ...fromCookie(astro), ...(me.settings ?? {}) } as Settings;
  return { me, settings };
}

/** The script swaras are drawn in: Latin, or the interface language's letters. */
export function swaraScript(settings: Settings, lang: Lang): Script {
  if (settings.swaraLetters !== "interface" || lang === "en") return "lat";
  return lang;
}

export function saHz(settings: Settings): number {
  return pitchHz(settings.sa || DEFAULTS.sa);
}

/** "E flute (medium)" etc. for the instrument's Sa line. */
export function saLabel(settings: Settings): string {
  return `${settings.sa.replace(/(\d)$/, "$1")}`;
}
