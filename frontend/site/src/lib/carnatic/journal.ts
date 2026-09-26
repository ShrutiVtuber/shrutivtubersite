/* The school's journal: the articles in /journal (BeeRanked's synced pages)
 * that are about Carnatic music, for the landing page and for the app
 * (docs/carnatic/API.md §7, /carnatic/journal.json).
 *
 * "About Carnatic music" is decided by the same topic words everywhere, so the
 * landing, the web and the app list the same posts. Read from the synced files
 * and kept for ten minutes: the journal changes when the agent writes, not
 * per request.
 *
 * ⚠ The journal's HTML parser is a CommonJS module the production build
 * bundles and the dev server cannot load (the journal's own pages have the
 * same limit), so in dev this reads nothing and callers show their empty
 * state. Imported only when asked for, so pages that never list the journal
 * never load it.
 */

export const TOPICS = /\b(carnatic|raga|ragam|tala|talam|swara|sruti|shruti box|tanpura|drone|gamaka|varisai|alankaram|geetham|varnam|kriti|venu|veena|mridangam|konnakol|melakarta|mohanam|bhairavi|begada|just intonation)\b/i;

export interface SchoolArticle {
  slug: string;
  href: string;
  title: string;
  deck: string;
  date: string;
  updated: boolean;
  cover: string | null;
}

export interface SchoolArticleFull extends SchoolArticle {
  body: string;
  toc: { id: string; text: string; level: number }[];
}

const TTL = 10 * 60 * 1000;
let cache: { at: number; list: SchoolArticleFull[] } | null = null;

const slugOk = (s: string) => /^[a-z0-9][a-z0-9-]{0,200}$/.test(s);

async function load(): Promise<SchoolArticleFull[]> {
  if (import.meta.env.DEV) return [];
  if (cache && Date.now() - cache.at < TTL) return cache.list;
  const { paths, read } = await import("../journal/parse");
  const out: SchoolArticleFull[] = [];
  for (const path of await paths()) {
    const m = /^\/journal\/blog\/([^/]+)$/.exec(path);
    if (!m || m[1] === "category" || m[1] === "page" || !slugOk(m[1])) continue;
    const page = await read(["blog", m[1]]).catch(() => null);
    if (!page || page.type !== "article") continue;
    if (!TOPICS.test(`${page.title} ${page.description} ${page.deck}`)) continue;
    out.push({
      slug: m[1], href: `/journal/blog/${m[1]}/`, title: page.title, deck: page.deck || page.description,
      date: page.date, updated: page.updated, cover: page.cover, body: page.body, toc: page.toc,
    });
  }
  out.sort((a, b) => (b.date || "").localeCompare(a.date || ""));
  cache = { at: Date.now(), list: out };
  return out;
}

/** The school's articles, newest first, without their bodies. */
export async function schoolArticles(): Promise<SchoolArticle[]> {
  try {
    return (await load()).map(({ body: _b, toc: _t, ...rest }) => rest);
  } catch {
    return [];
  }
}

/** One article of the school's, with its body, or null. */
export async function schoolArticle(slug: string): Promise<SchoolArticleFull | null> {
  if (!slugOk(slug)) return null;
  try {
    return (await load()).find((a) => a.slug === slug) ?? null;
  } catch {
    return null;
  }
}
