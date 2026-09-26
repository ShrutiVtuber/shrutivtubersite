/* What a learner keeps while working through the course, in the browser:
 * lesson state (opened, completed by their own hand, where they were
 * reading), attempts, and review cards. Signed out it stays on this device
 * and that is enough; signed in it is merged into the account
 * (docs/carnatic/API.md §11-§12), so the app and every browser agree.
 *
 * ⚠ No streaks, no missed days: nothing here records consecutive days.
 */
import { boot, csrf } from "./state";

const KEY = "swara.learner";

export interface LessonState { openedAt?: string | null; completedAt?: string | null; position?: { heading?: string; fraction?: number } | null; updatedAt?: string | null }
export interface Card { key: string; box: number; lastSeen: string | null; nextDue: string | null; recent: boolean[] }
export interface Attempt { id: string; itemId: string; kind: string; startedAt: string; seconds: number; result: Record<string, any> }

interface Store { lessons: Record<string, LessonState>; cards: Record<string, Card>; attempts: Attempt[]; unsent: string[]; newToday?: { day: string; n: number } }

function read(): Store {
  try {
    const s = JSON.parse(localStorage.getItem(KEY) || "{}");
    return { lessons: s.lessons ?? {}, cards: s.cards ?? {}, attempts: s.attempts ?? [], unsent: s.unsent ?? [], newToday: s.newToday };
  } catch {
    return { lessons: {}, cards: {}, attempts: [], unsent: [] };
  }
}

function write(s: Store) {
  try {
    // Keep the device's history bounded; the account keeps the rest.
    s.attempts = s.attempts.slice(-400);
    localStorage.setItem(KEY, JSON.stringify(s));
  } catch {
    /* Blocked storage: the page still works for this visit. */
  }
}

const now = () => new Date().toISOString();

async function api(method: string, path: string, body?: unknown): Promise<any> {
  if (!boot().signedIn) return null;
  try {
    const r = await fetch(path, {
      method, headers: { "content-type": "application/json", "x-csrf-token": csrf() },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    return r.ok ? await r.json() : null;
  } catch {
    return null;
  }
}

// ── lessons ─────────────────────────────────────────────────────────────

export function lessonState(id: string): LessonState {
  return read().lessons[id] ?? {};
}

export function allLessons(): Record<string, LessonState> {
  return read().lessons;
}

export function updateLesson(id: string, change: LessonState) {
  const s = read();
  const cur = s.lessons[id] ?? {};
  const merged: LessonState = { ...cur, ...change, updatedAt: now() };
  if (cur.openedAt && change.openedAt && cur.openedAt < change.openedAt) merged.openedAt = cur.openedAt;
  s.lessons[id] = merged;
  write(s);
  const payload: Record<string, unknown> = { updatedAt: merged.updatedAt };
  if ("openedAt" in change) payload.openedAt = merged.openedAt;
  if ("completedAt" in change) payload.completedAt = change.completedAt ?? null;
  if ("position" in change) payload.position = change.position;
  void api("PUT", `/api/carnatic/me/lessons/${encodeURIComponent(id)}`, payload);
}

/** On sign-in pages: fold the account's state into the device's and send what the account lacks. */
export async function syncLessons(): Promise<Record<string, LessonState>> {
  const remote = await api("GET", "/api/carnatic/me/lessons");
  const s = read();
  if (remote?.items) {
    for (const [id, r] of Object.entries<LessonState>(remote.items)) {
      const l = s.lessons[id];
      if (!l || (r.updatedAt ?? "") > (l.updatedAt ?? "")) s.lessons[id] = { ...l, ...r, openedAt: [l?.openedAt, r.openedAt].filter(Boolean).sort()[0] ?? null };
    }
    for (const [id, l] of Object.entries(s.lessons)) {
      const r = remote.items[id];
      if (!r || (l.updatedAt ?? "") > (r.updatedAt ?? "")) void api("PUT", `/api/carnatic/me/lessons/${encodeURIComponent(id)}`, l);
    }
    write(s);
  }
  return s.lessons;
}

// ── attempts and bests ──────────────────────────────────────────────────

export function uid(): string {
  return (crypto as any).randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function recordAttempt(a: Omit<Attempt, "id"> & { id?: string }): Attempt {
  const full: Attempt = { ...a, id: a.id ?? uid() };
  const s = read();
  s.attempts.push(full);
  s.unsent.push(full.id);
  write(s);
  void flushAttempts();
  return full;
}

export function attempts(filter: { itemId?: string; kind?: string } = {}): Attempt[] {
  return read().attempts.filter((a) => (!filter.itemId || a.itemId === filter.itemId) && (!filter.kind || a.kind === filter.kind));
}

export async function flushAttempts() {
  if (!boot().signedIn) return;
  const s = read();
  const unsent = s.attempts.filter((a) => s.unsent.includes(a.id));
  if (!unsent.length) return;
  const r = await api("POST", "/api/carnatic/me/attempts", { attempts: unsent.slice(0, 200) });
  if (r) {
    const done = new Set(unsent.slice(0, 200).map((a) => a.id));
    const t = read();
    t.unsent = t.unsent.filter((id) => !done.has(id));
    write(t);
  }
}

// ── review cards (EAR_TRAINING.md §6) ───────────────────────────────────

export const BOX_DAYS = [0, 1, 3, 7, 16, 35, 75];

export function cards(): Card[] {
  return Object.values(read().cards);
}

export function dueCards(at = new Date()): Card[] {
  return cards().filter((c) => c.nextDue && new Date(c.nextDue) <= at)
    .sort((a, b) => (a.lastSeen ?? "").localeCompare(b.lastSeen ?? ""));
}

/** Add a card if new (at most `perDay` new cards a day). */
export function ensureCard(key: string, perDay = 10): boolean {
  const s = read();
  if (s.cards[key]) return false;
  const day = now().slice(0, 10);
  if (s.newToday?.day !== day) s.newToday = { day, n: 0 };
  if (s.newToday.n >= perDay) return false;
  s.newToday.n += 1;
  s.cards[key] = { key, box: 0, lastSeen: null, nextDue: now(), recent: [] };
  write(s);
  return true;
}

/** A review: right moves up one box (two if fluent); wrong goes to box 1. */
export function review(key: string, right: boolean, fluent = false): Card {
  const s = read();
  const c = s.cards[key] ?? { key, box: 0, lastSeen: null, nextDue: null, recent: [] };
  c.box = right ? Math.min(6, c.box + (fluent ? 2 : 1)) : 1;
  c.lastSeen = now();
  c.nextDue = new Date(Date.now() + BOX_DAYS[c.box] * 86400000).toISOString();
  c.recent = [...c.recent, right].slice(-5);
  s.cards[key] = c;
  write(s);
  void api("PUT", "/api/carnatic/me/cards", { cards: [c] });
  return c;
}

export async function syncCards(): Promise<Card[]> {
  const s = read();
  const r = await api("PUT", "/api/carnatic/me/cards", { cards: Object.values(s.cards) });
  if (r?.items) {
    const remote = await api("GET", "/api/carnatic/me/cards");
    for (const c of (remote?.items ?? []) as Card[]) {
      const l = s.cards[c.key];
      if (!l || (c.lastSeen ?? "") > (l.lastSeen ?? "")) s.cards[c.key] = c;
    }
    write(s);
  }
  return Object.values(s.cards);
}

// ── words (SELF_TEST.md §4) ─────────────────────────────────────────────

export function wordFor(right: number, of: number): "new" | "getting there" | "comfortable" {
  const share = of ? right / of : 0;
  return share >= 0.8 ? "comfortable" : share >= 0.5 ? "getting there" : "new";
}
