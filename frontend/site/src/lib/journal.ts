/* Reading what the BeeRanked agent syncs.
 *
 * The agent writes complete HTML pages into a directory. This pulls out the
 * parts a page of ours needs — the title, the description, and the content —
 * so the section can be rendered inside the site's OWN layout.
 *
 * That is the whole point. Every other approach ends in a copy of the header
 * that drifts the moment the real nav changes, which is the problem this
 * replaces. Rebetichord solves it by booting their React bundle inside an
 * injector; Astro already renders on the server, so there is nothing to boot
 * and no sidecar to run — the real SiteHeader and SiteFooter components render
 * here exactly as they do on every other page, live badge and session state
 * included.
 *
 * BeeRanked is trusted — it is a partner's product and the content is hers —
 * so the extracted markup is rendered as-is rather than put through a
 * sanitiser.
 */
import { readFile, readdir } from "node:fs/promises";
import { join, normalize, resolve, sep } from "node:path";

const ROOT = process.env.SHRUTI_JOURNAL_DIR ?? "/srv/journal";

export interface Page {
  /** The article markup, without BeeRanked's own chrome. */
  html: string;
  title: string;
  description: string;
}

/**
 * Resolve a request path to a file inside the synced tree.
 *
 * Every segment is checked after normalising, and the result must still be
 * inside ROOT. A path is user input even when it looks like a route.
 */
function fileFor(slugParts: string[]): string | null {
  const cleaned = slugParts.filter((p) => p.length > 0 && p !== "." && p !== "..");
  if (cleaned.length !== slugParts.filter((p) => p.length > 0).length) return null;
  const candidate = resolve(join(ROOT, ...cleaned, "index.html"));
  if (candidate !== normalize(candidate)) return null;
  if (!candidate.startsWith(resolve(ROOT) + sep)) return null;
  return candidate;
}

const between = (html: string, open: RegExp, close: string): string => {
  const start = html.search(open);
  if (start < 0) return "";
  const from = html.indexOf(">", start) + 1;
  const end = html.lastIndexOf(close);
  return end > from ? html.slice(from, end) : "";
};

const meta = (html: string, name: string): string => {
  const m = new RegExp(
    `<meta[^>]+(?:name|property)=["']${name}["'][^>]*content=["']([^"']*)["']`,
    "i",
  ).exec(html);
  return m ? m[1] : "";
};

export async function page(slugParts: string[]): Promise<Page | null> {
  const file = fileFor(slugParts);
  if (!file) return null;

  let html: string;
  try {
    html = await readFile(file, "utf8");
  } catch {
    return null;
  }

  /* `<main>` is the article and its listings; everything outside it is chrome
     we are replacing. If a template ever omits <main>, fall back to the body
     rather than rendering nothing. */
  let content = between(html, /<main[^>]*>/i, "</main>");
  if (!content.trim()) content = between(html, /<body[^>]*>/i, "</body>");
  if (!content.trim()) return null;

  /* Their stylesheets are deliberately NOT carried across.
   *
   * They ship three `:root` blocks of their own, and `--accent` is a name both
   * systems use — injecting them turned the site's own header links rose on
   * journal pages and would have kept doing that for every token the two
   * happen to share. The content is styled below in the site's tokens
   * instead, which is where this was always going. */

  const titleTag = /<title[^>]*>([\s\S]*?)<\/title>/i.exec(html);
  const title = (titleTag ? titleTag[1] : "").replace(/\s*[,·|]\s*Shruti.*$/i, "").trim();

  return {
    html: content,
    title: title || "Journal",
    description: meta(html, "description") || meta(html, "og:description"),
  };
}

/** Every path the agent has written, for the sitemap and for link checking. */
export async function paths(): Promise<string[]> {
  const found: string[] = [];
  async function walk(dir: string, prefix: string[]): Promise<void> {
    let entries;
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      if (e.isDirectory()) await walk(join(dir, e.name), [...prefix, e.name]);
      else if (e.name === "index.html") found.push("/journal/" + prefix.join("/"));
    }
  }
  await walk(ROOT, []);
  return found.sort();
}
