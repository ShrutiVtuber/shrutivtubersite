/* Dates, the way the design writes them.
 *
 * Two forms, and they are not interchangeable: cards and marks use the dotted
 * numeric form the designer's references show (25.08.2026), while an article's
 * byline spells the month out, because that is the one a reader actually reads.
 */
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const parts = (iso: string): [number, number, number] | null => {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso ?? "");
  return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : null;
};

/** 25.08.2026 — for cards, rows and marks. */
export function shortDate(iso: string): string {
  const p = parts(iso);
  if (!p) return iso ?? "";
  const [y, m, d] = p;
  return `${String(d).padStart(2, "0")}.${String(m).padStart(2, "0")}.${y}`;
}

/** 25 August 2026 — for a byline. */
export function longDate(iso: string): string {
  const p = parts(iso);
  if (!p) return iso ?? "";
  const [y, m, d] = p;
  return `${d} ${MONTHS[m - 1]} ${y}`;
}

/** 24.08 — the leader-line rows, which the design writes without a year. */
export function rowDate(iso: string): string {
  const p = parts(iso);
  if (!p) return iso ?? "";
  const [, m, d] = p;
  return `${String(d).padStart(2, "0")}.${String(m).padStart(2, "0")}`;
}

/** Group entries by month, newest first, for the all-content page. */
export function byMonth<T extends { date: string }>(items: T[]): [string, T[]][] {
  const groups = new Map<string, T[]>();
  for (const item of [...items].sort((a, b) => (b.date ?? "").localeCompare(a.date ?? ""))) {
    const p = parts(item.date);
    const key = p ? `${MONTHS[p[1] - 1]} ${p[0]}` : "Undated";
    (groups.get(key) ?? groups.set(key, []).get(key)!).push(item);
  }
  return [...groups.entries()];
}
