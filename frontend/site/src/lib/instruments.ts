/* The nine instruments, from the database.
 *
 * Their names, subtitles, one-line descriptions and the whole "how it is
 * reckoned" passage used to be literals inside each tool's .astro file. Two
 * things followed from that, and both were wrong:
 *
 *   - a typo in the copy for an instrument needed an engineer and a deploy,
 *     which is an absurd amount of ceremony for a comma;
 *   - the admin panel had a Tools screen that edited a table no page read, so
 *     editing it appeared to work and changed nothing.
 *
 * Now there is one row per instrument and it is the source for all of it: the
 * tool's own page, its meta description, and its card on /tools. The order and
 * the grouping come from the row too, so adding a tenth instrument is a row
 * plus a page and nothing else.
 */
import { site, PATHS } from "./api";

export interface Instrument {
  slug: string;
  name: string;
  /** Native-script subtitle where one exists — पञ्चाङ्ग, Ἀττικός. */
  native: string;
  /** The mark beside the name. Type, not an icon. */
  glyph: string;
  /** Which group it sits in on /tools. */
  category: string;
  /** The one line: page subtitle, meta description, and card blurb. */
  summary: string;
  /** The rule it follows, for the aside. May be empty. */
  reckoned: string;
  /** The landing page's shorter line. Falls back to `summary` when unset. */
  landingBlurb: string;
  href: string;
}

/**
 * Visible instruments, in her order.
 *
 * An empty list is a real answer — the backend being unreachable, or every row
 * hidden — and callers render their absent state rather than a hard-coded
 * fallback. A fallback here would be the second copy this module exists to
 * remove, and it would go stale in exactly the way that is hardest to notice:
 * silently, and only when something is already wrong.
 */
export async function instruments(): Promise<Instrument[]> {
  return (await site<Instrument[]>(PATHS.tools)) ?? [];
}

/** One instrument by slug, or null. */
export async function instrument(slug: string): Promise<Instrument | null> {
  return (await instruments()).find((i) => i.slug === slug) ?? null;
}

/**
 * The categories present, in the order the rows give them.
 *
 * Derived rather than declared: a new category is created by typing it into a
 * row, and a list of category names kept beside this one would be a third
 * place to maintain.
 */
export function categories(all: Instrument[]): string[] {
  const seen: string[] = [];
  for (const i of all) if (i.category && !seen.includes(i.category)) seen.push(i.category);
  return seen;
}
