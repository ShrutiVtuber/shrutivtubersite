/* The visitor's settings and the one drone, in the browser.
 *
 * Settings live in localStorage (signed out: that is all there is, and it is
 * enough — nothing is a wall), mirrored into the `swara_prefs` cookie so the
 * server renders the next page in the right script and for the right Sa.
 * Signed in, every change is also saved to the account, so the app and other
 * browsers agree; a change made elsewhere in between is adopted, not
 * overwritten (409 from the API).
 */
import { Drone, type DroneTuning } from "./audio";
import { pitchHz } from "../notation";

export interface Boot {
  lang: string; signedIn: boolean; supporter: boolean; partsPerSong: number | null;
  settings: Record<string, any>; settingsUpdatedAt: string | null;
}

const KEY = "swara.settings";
const COOKIE_KEYS = ["lang", "swaraLetters", "tamilStyle", "subscripts", "otherScripts", "instrument", "sa", "flute",
  "hand", "droneTuning", "playbackTuning", "tempo", "fourthSpeed", "eighthAlankaram", "theme"];

let state: Boot | null = null;
let updatedAt: string | null = null;
const listeners = new Set<(s: Record<string, any>) => void>();

function readLocal(): Record<string, any> {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function writeLocal(s: Record<string, any>) {
  try {
    localStorage.setItem(KEY, JSON.stringify(s));
  } catch {
    /* Private window or blocked storage: the cookie still carries it. */
  }
  const small: Record<string, any> = {};
  for (const k of COOKIE_KEYS) if (k in s) small[k] = s[k];
  document.cookie = `swara_prefs=${encodeURIComponent(JSON.stringify(small))}; path=/carnatic; max-age=${60 * 60 * 24 * 365}; samesite=lax`;
}

export function boot(): Boot {
  if (state) return state;
  const el = document.getElementById("swara-boot");
  const b: Boot = el ? JSON.parse(el.textContent || "{}") : { lang: "en", signedIn: false, supporter: false, partsPerSong: 2, settings: {}, settingsUpdatedAt: null };
  /* Signed in, the account is the truth (it came with the page). Signed out,
     what this browser kept wins over the defaults the server assumed. */
  b.settings = b.signedIn ? { ...readLocal(), ...b.settings } : { ...b.settings, ...readLocal() };
  updatedAt = b.settingsUpdatedAt;
  state = b;
  writeLocal(b.settings);
  return b;
}

export function settings(): Record<string, any> {
  return boot().settings;
}

export function onSettings(fn: (s: Record<string, any>) => void) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

let saveTimer: number | null = null;

export function setSettings(patch: Record<string, any>) {
  const b = boot();
  b.settings = { ...b.settings, ...patch };
  writeLocal(b.settings);
  if ("theme" in patch) applyTheme(patch.theme);
  listeners.forEach((fn) => fn(b.settings));
  if (b.signedIn) {
    if (saveTimer) window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(save, 500);
  }
}

async function save() {
  const b = boot();
  try {
    const r = await fetch("/api/carnatic/me/settings", {
      method: "PUT",
      headers: { "content-type": "application/json", "x-csrf-token": csrf() },
      body: JSON.stringify({ settings: b.settings, baseUpdatedAt: updatedAt }),
    });
    const body = await r.json().catch(() => null);
    if (r.status === 409 && body?.settings) {
      /* Changed on another device in between: keep theirs, then lay this
         change over it and save again. */
      updatedAt = body.updatedAt;
      b.settings = { ...body.settings, ...b.settings };
      await save();
      return;
    }
    if (r.ok && body) updatedAt = body.updatedAt;
  } catch {
    /* Offline: this browser keeps it and the next change tries again. */
  }
}

export function csrf(): string {
  return document.cookie.split("; ").find((c) => c.startsWith("shruti_csrf="))?.split("=")[1] ?? "";
}

/* The site's own theme switch: dawn and dusk are its light and dark. */
export function applyTheme(theme: string) {
  const map: Record<string, string> = { dawn: "light", dusk: "dark", system: "system" };
  const t = map[theme] ?? "system";
  try {
    if (t === "system") localStorage.removeItem("shruti-theme");
    else localStorage.setItem("shruti-theme", t);
  } catch { /* ignore */ }
  if (t === "system") document.documentElement.removeAttribute("data-theme");
  else document.documentElement.setAttribute("data-theme", t);
}

/* ── the drone ───────────────────────────────────────────────────────────── */

let drone: Drone | null = null;
const droneListeners = new Set<(on: boolean, label: string) => void>();

export function theDrone(): Drone {
  if (!drone) drone = new Drone();
  return drone;
}

export function onDrone(fn: (on: boolean, label: string) => void) {
  droneListeners.add(fn);
}

function tell() {
  const d = theDrone();
  const s = settings();
  droneListeners.forEach((fn) => fn(d.playing, `Sa = ${s.sa} · ${d.saHz ? pitchHz(s.sa).toFixed(1) : ""} Hz`));
}

export function startDrone(tuning?: DroneTuning) {
  const s = settings();
  theDrone().start(pitchHz(s.sa || "C3"), tuning ?? s.droneTuning ?? "pa", s.droneVolume ?? 0.6);
  tell();
}

export function stopDrone() {
  theDrone().stop();
  tell();
}

export function toggleDrone(tuning?: DroneTuning): boolean {
  if (theDrone().playing) stopDrone();
  else startDrone(tuning);
  return theDrone().playing;
}

export const notifyDrone = tell;
