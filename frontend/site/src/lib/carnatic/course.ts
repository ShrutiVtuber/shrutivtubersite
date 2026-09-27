/* The course, read from the backend (docs/carnatic/API.md §10).
 *
 * Visitors read published lessons only. The operator, signed in to the
 * admin, sees drafts too ("preview"), with a line saying so on the page.
 */
import { SITE_API } from "../api";
import { asAdmin } from "../admin";
import { asReader } from "../account";
import { ragas as loadRagas, talas as loadTalas } from "./data";
import type { ExerciseInfo, GlossaryTerm, LessonCtx, LessonSource, RecordingInfo } from "./lesson";

export interface UnitLesson {
  id: string; slug: string; order: number; title: string; minutes: number; level: string;
  available: boolean; status: string; hasListening: boolean; hasPractice: boolean; after: string[];
}
export interface Unit { n: number; title: string; level: string; levelLabel: string; intro: string; lessons: UnitLesson[]; checkpoint: string | null }
export interface Lesson {
  id: string; slug: string; lang: string; revision: number; status: string; unit: number; order: number;
  title: string; summary: string; level: string; minutes: number; goals: string[]; prerequisites: string[];
  tools: string[]; ragas: string[]; talas: string[];
  recordings: { id: string; why: string; available: boolean }[];
  sources: LessonSource[]; exercises: string[]; body: string; words: number;
  translation: null | { lang: string; status: string; outOfDate: boolean };
}
export interface Recording {
  id: string; status: string; provider: string; url: string; title: string; channel: string; artists: string[];
  instrument: string; composition: string; composer: string; form: string; raga: string; tala: string;
  listenFor: string; clips: { id: string; start: string; end: string; label: string }[];
  sections: { t: string; label: string }[]; beatMap: { clip?: string; samam: number[]; counts?: number[] } | null;
  analyses: number;
}

async function get<T>(path: string, astro?: any): Promise<T | null> {
  if (astro) {
    const r = await asAdmin(astro, path);
    return r.ok ? (r.body as T) : null;
  }
  try {
    const r = await fetch(`${SITE_API}${path}`);
    return r.ok ? ((await r.json()) as T) : null;
  } catch {
    return null;
  }
}

/** Is the visitor the operator (admin session)? Cheap: one call. */
export async function isOperator(astro: any): Promise<boolean> {
  const r = await asAdmin(astro, "/api/admin/me");
  return r.ok;
}

export async function units(astro?: any, preview = false): Promise<Unit[]> {
  const body = await get<{ items: Unit[] }>(`/api/carnatic/course/units${preview ? "?preview=true" : ""}`, preview ? astro : undefined);
  return body?.items ?? [];
}

export async function lesson(key: string, astro?: any, preview = false, lang = "en"): Promise<Lesson | null> {
  const q = new URLSearchParams({ lang, ...(preview ? { preview: "true" } : {}) });
  return get<Lesson>(`/api/carnatic/course/lessons/${encodeURIComponent(key)}?${q}`, preview ? astro : undefined);
}

export async function exercises(filter: { unit?: number; lesson?: string }, astro?: any, preview = false): Promise<ExerciseInfo[]> {
  const q = new URLSearchParams({
    ...(filter.unit ? { unit: String(filter.unit) } : {}), ...(filter.lesson ? { lesson: filter.lesson } : {}),
    ...(preview ? { preview: "true" } : {}),
  });
  const body = await get<{ items: ExerciseInfo[] }>(`/api/carnatic/course/exercises?${q}`, preview ? astro : undefined);
  return body?.items ?? [];
}

export async function exercise(id: string, astro?: any, preview = false): Promise<ExerciseInfo | null> {
  return get<ExerciseInfo>(`/api/carnatic/course/exercises/${encodeURIComponent(id)}${preview ? "?preview=true" : ""}`,
    preview ? astro : undefined);
}

export async function glossary(): Promise<GlossaryTerm[]> {
  return (await get<{ items: GlossaryTerm[] }>("/api/carnatic/course/glossary"))?.items ?? [];
}

export interface Drills {
  families: { id: string; title: string; answerBy: string; words: string; note?: string }[];
  levels: { id: string; family: string; title: string; unlockedBy: string; answer: string; audio: { kind: string }; fluentMs: number; note: string | null; ladder: string[] }[];
  confusable: { set: string; ragas: string[]; mode: string; unlockedBy: string; differ: string }[];
  ragaFlags: Record<string, { synthOk: boolean }>;
  talaKeeping: Record<string, any>[];
  topics: Record<string, number[]>;
}

export async function drills(): Promise<Drills | null> {
  return get<Drills>("/api/carnatic/course/drills");
}

export async function recordings(filter: { raga?: string; form?: string } = {}): Promise<Recording[]> {
  const q = new URLSearchParams(filter as Record<string, string>);
  return (await get<{ items: Recording[] }>(`/api/carnatic/listening/recordings?${q}`))?.items ?? [];
}

export async function recording(id: string): Promise<Recording | null> {
  return get<Recording>(`/api/carnatic/listening/recordings/${encodeURIComponent(id)}`);
}

/** A short name for a recording where the provider's own title is long. */
export function recordingLabel(r: Pick<Recording, "composition" | "title" | "form" | "id">): string {
  if (r.composition) return r.composition;
  const t = (r.title || "").split(/[|·\-–—]/)[0].trim();
  return t || r.id;
}

export interface LessonState { openedAt: string | null; completedAt: string | null; position: { heading?: string; fraction?: number } | null; updatedAt: string | null }

export async function myLessons(astro: any): Promise<Record<string, LessonState>> {
  const r = await asReader(astro, "/api/carnatic/me/lessons");
  return r.ok ? r.body?.items ?? {} : {};
}

/** Everything the renderer needs to draw a lesson's embeds. */
export async function lessonContext(l: Lesson, base: Pick<LessonCtx, "script" | "tamil" | "href" | "saLabel">,
                                    extra: { exercises: ExerciseInfo[]; glossary: GlossaryTerm[]; drills: Drills | null;
                                             units: Unit[] }): Promise<LessonCtx> {
  const [ragaData, talaData, recs] = await Promise.all([loadRagas(), loadTalas(), recordings()]);
  const ragaMap: LessonCtx["ragas"] = {};
  for (const r of [...(ragaData?.janyas ?? []), ...(ragaData?.performed ?? [])]) {
    ragaMap![r.id] = { name: r.name, arohana: r.arohana, avarohana: r.avarohana, parent: `mela ${r.parent?.number}` };
  }
  const melas: LessonCtx["melas"] = {};
  for (const m of ragaData?.melakartas ?? []) {
    melas![m.number] = { name: m.name, arohana: m.arohana, avarohana: m.avarohana, chakra: m.chakra?.name };
    ragaMap![m.id] = ragaMap![m.id] ?? { name: m.name, arohana: m.arohana, avarohana: m.avarohana };
  }
  const talaNames: Record<string, string> = {};
  for (const t of talaData?.practical ?? []) talaNames[t.id] = t.name;
  for (const t of talaData?.suladi ?? []) talaNames[t.id] = t.name ?? t.id.replace(/_/g, " ");
  const byId = new Map(recs.map((r) => [r.id, r]));
  const recordingsMap: Record<string, RecordingInfo> = {};
  const wanted = new Set([...l.recordings.map((r) => r.id), ...[...l.body.matchAll(/\{\{\s*recording[^}]*id=([^\s}]+)/g)].map((m) => m[1])]);
  for (const id of wanted) {
    const r = byId.get(id);
    const why = l.recordings.find((x) => x.id === id)?.why;
    recordingsMap[id] = r && r.status === "approved"
      ? { id, available: true, label: recordingLabel(r), why, provider: r.provider, url: r.url, raga: r.raga, clips: r.clips }
      : { id, available: false, label: id, why };
  }
  const lessonTitles: LessonCtx["lessonTitles"] = {};
  for (const u of extra.units) for (const x of u.lessons) lessonTitles![x.id] = { title: x.title, slug: x.slug };
  return {
    ...base, sources: l.sources, glossary: extra.glossary,
    exercises: Object.fromEntries(extra.exercises.map((e) => [e.id, e])),
    recordings: recordingsMap, ragas: ragaMap, melas, talaNames,
    drillTitles: Object.fromEntries((extra.drills?.levels ?? []).map((d) => [d.id, d.title])),
    lessonTitles, slug: l.slug, lessonId: l.id,
    selftests: Object.fromEntries((extra.drills?.talaKeeping ?? []).map((k: any) => [k.id, { title: k.title, minutes: k.minutes }])),
    unitTitles: Object.fromEntries(extra.units.map((u) => [u.n, u.title])),
  };
}

/** "3 h 36 min", "about 15 min". */
export function duration(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m ? `${h} h ${m} min` : `${h} h`;
}

export interface WorkSummary {
  id: number; room: string; subject: string; title: string; author: string; authorId: number | null; mine: boolean;
  submittedAt: string | null; votes: number; comments: number; excerpt: string; hidden: boolean;
}

/** Community works in a room about one subject, as the viewer may see them (blocks and hidden ones left out). */
export async function works(astro: any, room: string, subject?: string, sort: "new" | "discussed" = "new"): Promise<WorkSummary[]> {
  const q = new URLSearchParams({ room, sort, ...(subject ? { subject } : {}) });
  const r = await asReader(astro, `/api/carnatic/community/works?${q}`);
  return r.ok ? r.body?.items ?? [] : [];
}

export async function lessonsAbout(filter: { raga?: string; tala?: string; recording?: string }): Promise<{ id: string; slug: string; title: string; unit: number; order: number; minutes: number }[]> {
  const q = new URLSearchParams(Object.entries(filter).filter(([, v]) => v) as [string, string][]);
  return (await get<{ items: any[] }>(`/api/carnatic/course/lessons?${q}`))?.items ?? [];
}

/** "2 days ago", "1 week ago": for lists. */
export function ago(iso: string | null): string {
  if (!iso) return "";
  const d = (Date.now() - new Date(iso).getTime()) / 86400000;
  if (d < 1) return "today";
  if (d < 2) return "yesterday";
  if (d < 7) return `${Math.floor(d)} days ago`;
  if (d < 14) return "1 week ago";
  if (d < 60) return `${Math.floor(d / 7)} weeks ago`;
  return new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

/** The Swara Studio admin is the operator's only: anyone else goes to the admin sign-in. */
export async function studioGate(astro: any): Promise<Response | null> {
  if (await isOperator(astro)) return null;
  return astro.redirect(`/admin/signin?next=${encodeURIComponent(astro.url.pathname + astro.url.search)}`, 303);
}

export async function studio<T = any>(astro: any, path: string): Promise<T | null> {
  const r = await asAdmin(astro, `/api/carnatic/studio${path}`);
  return r.ok ? (r.body as T) : null;
}
