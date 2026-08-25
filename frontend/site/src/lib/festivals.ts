/* The festival corpora, attached to a calendar's months.
 *
 * Both calendar tools had the markup to show festivals and neither ever did:
 * `/hindu-year` and `/attic-year` return months, `/festivals` returns dated
 * observances, and nothing joined the two. So forty-five Attic entries and
 * seventy-two Hindu ones — the deepest work in the project — were unreachable
 * from the pages built to show them.
 *
 * The join is done here, once, because both calendars need exactly the same
 * thing and the rule that makes it correct is not obvious: a festival belongs
 * to the month whose span CONTAINS it, never to the Gregorian month it shares
 * a number with. A lunisolar month starts mid-Gregorian-month by definition.
 */
import { askAstro } from "./api";

export interface Festival {
  key: string;
  name: string;
  date: string;
  start: string;
  end: string;
  spanDays: number;
  summary: string;
  /** attested · reconstructed · disputed — shown, never flattened. */
  confidence: string;
  restriction: string;
  note: string;
  school: string | null;
  tags: string[];
  sources: { author?: string; work: string; locus: string | null }[];
}

/** An entry the corpus refuses to date rather than guessing a day for it. */
export interface Undated {
  key: string;
  name: string;
  summary: string;
  confidence: string;
  note: string;
  reason?: string;
}

export interface Corpus {
  tradition: string;
  verified: boolean;
  verificationNote: string;
  counts: { entries: number; dated: number; undated: number };
  festivals: Festival[];
  undated: Undated[];
}

interface Span { start: string; end: string }

/**
 * Fetch a tradition's year.
 *
 * A festival year and a calendar year are not the same window. The Attic year
 * opens after the summer solstice and runs into the next Gregorian year, so
 * asking for one Gregorian year would lose its second half — both are fetched
 * and merged, and the month join then discards whatever falls outside.
 */
/* A festival year is a pure function of tradition, year and observer, and it
 * does not change — so it is computed once per process and kept.
 *
 * This is not a micro-optimisation. Resolving the seventy-two Hindu entries
 * for one year takes about eleven seconds in the daemon, consistently, warm
 * or cold; two years of that is over the fetch timeout and the page renders
 * its cannot-compute state instead of a calendar. Cached, the first visitor
 * after a deploy waits and nobody else does.
 *
 * Unbounded on purpose: the key space is a handful of years times the places
 * people actually ask about, and an entry is a few hundred kilobytes. If that
 * ever stops being true it wants a real cache, not a bigger number here.
 */
const YEARS = new Map<string, Promise<Corpus | null>>();

async function fetchYear(
  tradition: string, year: number, lat: number, lon: number,
): Promise<Corpus | null> {
  const answer = await askAstro<Corpus>(
    `/festivals?tradition=${tradition}&year=${year}&lat=${lat}&lon=${lon}`,
    60_000,
  );
  if (!answer.ok) {
    console.warn(
      `[festivals] ${tradition} ${year} unavailable (status ${answer.status})`,
    );
  }
  return answer.ok ? answer.data : null;
}

function year(
  tradition: string, y: number, lat: number, lon: number,
): Promise<Corpus | null> {
  // Rounded, so two visitors a metre apart share the work.
  const key = `${tradition}:${y}:${lat.toFixed(3)}:${lon.toFixed(3)}`;
  let pending = YEARS.get(key);
  if (!pending) {
    pending = fetchYear(tradition, y, lat, lon);
    YEARS.set(key, pending);
    // A failed fetch must not be remembered as "no festivals" for the life of
    // the process — the next visitor should get another try.
    pending.then((got) => { if (!got) YEARS.delete(key); }).catch(() => YEARS.delete(key));
  }
  return pending;
}

export async function corpus(
  tradition: "attic" | "hindu",
  years: number[],
  lat: number,
  lon: number,
): Promise<Corpus | null> {
  const answers = (await Promise.all(
    years.map((y) => year(tradition, y, lat, lon)),
  )).map((data) => ({ ok: Boolean(data), data }));
  const good = answers.filter((a) => a.ok && a.data).map((a) => a.data!);
  if (good.length === 0) return null;

  const seen = new Set<string>();
  const festivals: Festival[] = [];
  for (const one of good) {
    for (const f of one.festivals ?? []) {
      // Two overlapping year windows return the same occurrence twice.
      const id = `${f.key}@${f.date}`;
      if (seen.has(id)) continue;
      seen.add(id);
      festivals.push(f);
    }
  }
  festivals.sort((a, b) => a.date.localeCompare(b.date));

  /* UNDATED means the corpus will not name a day. It does not mean "the
   * daemon's window happened to end first".
   *
   * The API reports both under one key, and merging years naively produced a
   * list that said Haloa had no attested day when Haloa has one — it simply
   * fell in the next Gregorian year, and the very next fetch dates it. Left
   * alone, the page would claim a gap in the scholarship that is really a gap
   * in the question asked, which is the exact opposite of what this section
   * is for.
   *
   * So: merge, drop anything the merged list actually dates, and dedupe. What
   * survives is genuinely undatable. */
  const dated = new Set(festivals.map((f) => f.key));
  const undated: Undated[] = [];
  const held = new Set<string>();
  for (const one of good) {
    for (const u of one.undated ?? []) {
      if (dated.has(u.key) || held.has(u.key)) continue;
      held.add(u.key);
      undated.push(u);
    }
  }

  return {
    ...good[0],
    festivals,
    undated,
    counts: {
      entries: good[0].counts?.entries ?? 0,
      dated: festivals.length,
      undated: undated.length,
    },
  };
}

/**
 * Bucket festivals into months by span containment.
 *
 * `start`/`end` rather than `date`, so a festival running across a month
 * boundary — the Greater Mysteries run for days — is filed by when it begins
 * rather than being dropped for ending elsewhere.
 */
export function byMonth<M extends Span>(months: M[], festivals: Festival[]): Festival[][] {
  return months.map((m) =>
    festivals.filter((f) => {
      const begins = (f.start || f.date).slice(0, 10);
      return begins >= m.start.slice(0, 10) && begins <= m.end.slice(0, 10);
    }),
  );
}

/** How sure the corpus is. Shown as a word, because grading is the honesty. */
export const CONFIDENCE_NOTE: Record<string, string> = {
  attested: "the day is given by an ancient source",
  reconstructed: "the day is inferred, and scholars broadly agree",
  disputed: "the day is argued over; this is one defensible reading",
};


/* Warm the two default years in the background at startup.
 *
 * The first render of the Hindu calendar takes about twenty-two seconds cold,
 * because the daemon resolves seventy-two entries across two years. Cached it
 * is a third of a second. Without this the person who pays that cost is the
 * first visitor after a deploy, which is precisely the visitor least owed a
 * blank-looking page — so the server pays it instead, before anyone asks.
 *
 * Deliberately not awaited and deliberately silent. A failed warm leaves the
 * cache empty and the next real request tries again; a warm that threw and
 * took the server down at boot would be a far worse trade than a slow page.
 */
const UJJAIN = { lat: 23.1765, lon: 75.7885 };
const ATHENS = { lat: 37.9838, lon: 23.7275 };

async function warm(): Promise<void> {
  const started = Date.now();
  const now = new Date();
  const gregorian = now.getUTCFullYear();
  const atticStart = now.getUTCMonth() >= 6 ? gregorian : gregorian - 1;

  /* ONE AT A TIME, and the order is deliberate.
   *
   * Firing all four at once starved them: the daemon runs two workers, a
   * Hindu year costs twelve to fifteen seconds of solid computation, and four
   * parallel requests contending for two workers all exceeded the timeout —
   * a warm that reported 0/4 and left every page as slow as before.
   *
   * Attic first because it is nearly free, so that page is fast within a
   * second or two of boot rather than waiting behind half a minute of
   * pañcāṅga. */
  const jobs: [string, number, number, number][] = [
    ["attic", atticStart, ATHENS.lat, ATHENS.lon],
    ["attic", atticStart + 1, ATHENS.lat, ATHENS.lon],
    ["hindu", gregorian - 1, UJJAIN.lat, UJJAIN.lon],
    ["hindu", gregorian, UJJAIN.lat, UJJAIN.lon],
  ];

  let got = 0;
  for (const [tradition, y, lat, lon] of jobs) {
    try {
      if (await year(tradition, y, lat, lon)) got += 1;
    } catch {
      // Left for the next real request to retry.
    }
  }
  // One line, at boot, so a slow or failing warm is visible in the logs
  // rather than being inferred from a slow page weeks later.
  console.log(
    `[festivals] warmed ${got}/${jobs.length} years in ${Math.round((Date.now() - started) / 1000)}s`,
  );
}

/* Called unconditionally. `import.meta.env.SSR` looked like the right guard
   and was worse than none: Vite resolves it at build time and tree-shook the
   call away, so the warm silently never ran and the first visitor still paid
   the full twenty-four seconds. This module only ever runs on the server —
   every path in it fetches the daemon over the internal network — so there is
   nothing to guard against. */
void warm();
