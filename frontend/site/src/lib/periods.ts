// SPDX-License-Identifier: AGPL-3.0-only
/**
 * What a period id means: which days it covers, and what to call it.
 *
 * Extracted because there are now TWO writing desks — hers in the admin, and
 * the public one people practise on — and they must agree about what "this
 * week" is. Two copies of ISO week arithmetic is two chances to disagree, and
 * the disagreement would be silent: both would render a perfectly plausible
 * week, one of them the wrong one.
 *
 * ISO weeks throughout. Monday starts a week, week one holds the first
 * Thursday, and **Thursday decides the year** — which is why a week in early
 * January can belong to the year before, and why counting sevens from the 1st
 * drifts by a week every few years.
 */
export const PERIODS = ["daily", "weekly", "monthly", "yearly"] as const;
export type Period = (typeof PERIODS)[number];

/** Narrow an untrusted query parameter to a period, or fall back.
 *
 * A predicate on `string | null` cannot narrow the ARGUMENT at the call site
 * when the argument is itself `string | null` — TypeScript keeps the null. So
 * this returns the period instead of a boolean, which is what every caller
 * actually wanted. */
export function asPeriod(value: string | null | undefined, fallback: Period = "weekly"): Period {
  return (PERIODS as readonly string[]).includes(value ?? "")
    ? (value as Period)
    : fallback;
}

const pad = (n: number) => String(n).padStart(2, "0");

/** The ISO week id — `2026-W38` — for a date. */
export function isoWeek(d: Date): string {
  const t = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7));
  const start = new Date(Date.UTC(t.getUTCFullYear(), 0, 1));
  return `${t.getUTCFullYear()}-W${pad(
    Math.ceil(((t.getTime() - start.getTime()) / 86400000 + 1) / 7),
  )}`;
}

/** The Monday and Sunday of an ISO week id. */
export function weekDays(id: string): [string, string] {
  const [y, w] = id.split("-W").map(Number);
  const jan4 = new Date(Date.UTC(y, 0, 4));
  const monday = new Date(jan4);
  monday.setUTCDate(jan4.getUTCDate() - ((jan4.getUTCDay() || 7) - 1) + (w - 1) * 7);
  const sunday = new Date(monday);
  sunday.setUTCDate(monday.getUTCDate() + 6);
  return [monday.toISOString().slice(0, 10), sunday.toISOString().slice(0, 10)];
}

/** The id of the period containing [at], which defaults to now. */
export function currentCovers(period: Period, at: Date = new Date()): string {
  switch (period) {
    case "daily":
      return at.toISOString().slice(0, 10);
    case "weekly":
      return isoWeek(at);
    case "yearly":
      return String(at.getUTCFullYear());
    case "monthly":
      return `${at.getUTCFullYear()}-${pad(at.getUTCMonth() + 1)}`;
  }
}

/** The first and last day a period covers, as ISO dates. */
export function range(period: Period, covers: string): [string, string] {
  if (period === "weekly") return weekDays(covers);
  if (period === "monthly") {
    const [y, m] = covers.split("-").map(Number);
    const last = new Date(Date.UTC(y, m, 0)).getUTCDate();
    return [`${covers}-01`, `${covers}-${pad(last)}`];
  }
  if (period === "yearly") return [`${covers}-01-01`, `${covers}-12-31`];
  return [covers, covers];
}

/** What a person would call it out loud. */
export function label(period: Period, covers: string): string {
  const day = { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" } as const;
  if (period === "yearly") return covers;
  if (period === "monthly") {
    const [y, m] = covers.split("-").map(Number);
    return new Date(Date.UTC(y, m - 1, 1)).toLocaleDateString("en-GB", {
      month: "long", year: "numeric", timeZone: "UTC",
    });
  }
  if (period === "weekly") {
    const [monday] = weekDays(covers);
    return `Week of ${new Date(`${monday}T00:00:00Z`).toLocaleDateString("en-GB", day)}`;
  }
  return new Date(`${covers}T00:00:00Z`).toLocaleDateString("en-GB", {
    weekday: "long", ...day,
  });
}

/** The shape a period's id must have, so a bad one is a 404 rather than a
 *  page that says "not written yet" for every string anybody types. */
export const SHAPE: Record<Period, RegExp> = {
  daily: /^\d{4}-\d{2}-\d{2}$/,
  weekly: /^\d{4}-W\d{2}$/,
  monthly: /^\d{4}-\d{2}$/,
  yearly: /^\d{4}$/,
};
