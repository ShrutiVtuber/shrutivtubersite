/* The school's data, read on the server.
 *
 * The files are built from the private research by
 * scripts/sync-carnatic-data.sh and served by the backend
 * (/api/carnatic/data/*). They are fetched once per digest and kept in
 * memory: the manifest is asked again every minute, and a file is fetched
 * again only when its digest changes.
 *
 * Absent is a working state. Until the data is synced every page renders its
 * designed absent state, and the drone, the tuner and the tala trainer, which
 * need none of it, still work.
 */
import { SITE_API } from "../api";

export interface Manifest {
  digest: string;
  built_at: string;
  files: { name: string; digest: string; bytes: number }[];
  counts?: { melakartas: number; janyas: number; performed: number };
}

const TTL = 60_000;
let manifestCache: { at: number; value: Manifest | null } | null = null;
const files = new Map<string, { digest: string; value: any }>();

async function fetchJson(path: string, timeoutMs = 8000): Promise<any | null> {
  const control = new AbortController();
  const timer = setTimeout(() => control.abort(), timeoutMs);
  try {
    const r = await fetch(`${SITE_API}${path}`, { signal: control.signal });
    return r.ok ? await r.json() : null;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

export async function manifest(): Promise<Manifest | null> {
  const now = Date.now();
  if (manifestCache && now - manifestCache.at < TTL) return manifestCache.value;
  const value = (await fetchJson("/api/carnatic/data/manifest")) as Manifest | null;
  /* A blip keeps the last good answer rather than blanking every page. */
  manifestCache = { at: now, value: value ?? manifestCache?.value ?? null };
  return manifestCache.value;
}

async function file<T = any>(name: string): Promise<T | null> {
  const m = await manifest();
  const entry = m?.files.find((f) => f.name === name);
  if (!entry) return null;
  const hit = files.get(name);
  if (hit && hit.digest === entry.digest) return hit.value as T;
  const value = await fetchJson(`/api/carnatic/data/${name}`, 15000);
  if (value) files.set(name, { digest: entry.digest, value });
  return (value ?? hit?.value ?? null) as T | null;
}

/* Shapes, loosely: the build script is the authority (scripts/carnatic/build_data.py). */
export type Scripts = { ta: { grantha: string | null; pure: string | null } | null; te: string | null; kn: string | null };
export interface Mela {
  number: number; id: string; name: string; iso: string | null; aliases: string[];
  chakra: { number: number; name: string; iso?: string; mnemonic?: string; position: number };
  madhyama: string; swaras: string[]; swarasthanaNames: Record<string, string>; semitones: number[];
  arohana: string; avarohana: string; vivadi: string[];
  katapayadi: { aksharas: string[]; used: string[]; digits: number[]; rule: string; note: string | null };
  dikshitar: string | null; scripts: Scripts; confidence: Record<string, string>;
  janyas: string[]; performed: string | null; notes: string | null;
}
export interface Raga {
  id: string; kind: "janya" | "melakarta"; name: string; iso: string | null; aliases: string[];
  number?: number;
  parent: { number: number; name: string }; parentAlternatives: { number?: number; name: string; who?: string }[];
  arohana: string; avarohana: string; variants: { arohana?: string; avarohana?: string; who?: string }[];
  anya: any[];
  classification: { aro: number; ava: number; jati: string; vakra: boolean; bhashanga: boolean; varja: boolean };
  jiva: { value: string[]; agreement: string; sources: string[] } | null;
  nyasa: { value: string[]; agreement: string; sources: string[] } | null;
  graha: { value: string[]; agreement: string; sources: string[] } | null;
  prayogas: { sargam: string; note?: string; source?: string }[];
  gamakaCharacter: { text: string; attribution?: string; source_url?: string; confidence?: string; kind?: string }[];
  timeRasa: { value: string; attribution?: string; status?: string } | null;
  compositions: { title: string; form: string; composer: string; tala: string; language?: string; learner_note?: string; verified: boolean }[];
  disagreements: string[]; hindustaniComparison?: any; pedagogy?: string;
  confidence: string; confidenceReason?: string; sources: string[];
  tier: number | null; order?: number; hindustani: boolean; scripts: Scripts;
}
export interface Ragas { melakartas: Mela[]; janyas: Raga[]; performed: Raga[]; aliases: Record<string, string>; meta: any }

export const ragas = () => file<Ragas>("ragas.json");
export const talas = () => file<any>("talas.json");
export const lessons = () => file<any>("lessons.json");
export const instruments = () => file<any>("instruments.json");
export const featured = () => file<any>("featured.json");
export const gamakas = () => file<any>("gamakas.json");

/** Every raga with a page: the janyas and the melakartas performed as ragas. */
export async function ragaById(id: string): Promise<Raga | null> {
  const r = await ragas();
  return r ? [...r.janyas, ...r.performed].find((x) => x.id === id) ?? null : null;
}

export interface Review { status: "confirmed" | "corrected"; text: string | null }
let reviewCache: { at: number; value: Record<string, Review> } | null = null;

/** Which names and facts a reviewer has cleared. Absent means unverified. */
export async function reviews(): Promise<Record<string, Review>> {
  const now = Date.now();
  if (reviewCache && now - reviewCache.at < 15_000) return reviewCache.value;
  const body = await fetchJson("/api/carnatic/reviews");
  reviewCache = { at: now, value: body?.items ?? reviewCache?.value ?? {} };
  return reviewCache.value;
}
