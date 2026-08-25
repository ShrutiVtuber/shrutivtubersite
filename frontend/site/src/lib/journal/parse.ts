/* Reading BeeRanked's synced pages into data.
 *
 * The designer's skeleton has nothing in common with what BeeRanked emits, so
 * their markup is not passed through — it is read for its DATA and the
 * components re-emit the designed structure. That is what the brief promised
 * them and what rebetichord's injector does on the sister project.
 *
 * A real parser, not regular expressions. Regex over HTML is what produced the
 * bug where a CSS comment containing the word `<main>` was rendered as an
 * article: the extractor matched the first thing that looked like a tag and had
 * no idea it was inside a stylesheet. A parser cannot make that mistake.
 *
 * BeeRanked is trusted — a partner's product, her content — so markup is
 * carried across without sanitising.
 */
import { readFile, readdir } from "node:fs/promises";
import { join, resolve, sep } from "node:path";
import { parse, type HTMLElement } from "node-html-parser";

import { moments } from "./sky";
import type {
  AzGroup, AzRow, ChangeGroup, Crumb, Entry, JournalPage, Kind, NavGroup,
  PageType, Release, TocItem,
} from "./types";

const ROOT = process.env.SHRUTI_JOURNAL_DIR ?? "/srv/journal";

/** Path segments to a file inside the synced tree, or null if it escapes. */
function fileFor(parts: string[]): string | null {
  if (parts.some((p) => !p || p === "." || p === ".." || p.includes("\0"))) return null;
  const candidate = resolve(join(ROOT, ...parts, "index.html"));
  return candidate.startsWith(resolve(ROOT) + sep) || candidate === resolve(ROOT)
    ? candidate
    : null;
}

const KIND_BY_PREFIX: Record<string, Kind> = {
  blog: "writing",
  docs: "documentation",
  wiki: "wiki",
  changelog: "changelog",
};

export function kindOf(parts: string[]): Kind {
  return KIND_BY_PREFIX[parts[0] ?? ""] ?? "writing";
}

/** Which of the designer's pages this path wants. */
export function typeOf(parts: string[]): PageType {
  const [first, second] = parts;
  if (parts.length === 0) return "hub";
  if (first === "all") return "all";
  if (first === "sitemap") return "sitemap";
  if (first === "changelog") return parts.length > 1 ? "changelog-entry" : "changelog";
  if (second === "category") return "category";
  if (parts.length === 1) return "index";
  if (first === "docs") return "docs";
  if (first === "wiki") return "wiki";
  return "article";
}

const text = (el: HTMLElement | null | undefined): string =>
  (el?.textContent ?? "").replace(/\s+/g, " ").trim();

const MONTH_ABBR = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

/** ISO date out of prose like "Aug 25, 2026", or "" when there is none. */
function isoFromProse(raw: string): string {
  const iso = /(\d{4})-(\d{2})-(\d{2})/.exec(raw)?.[0];
  if (iso) return iso;
  const m = /([A-Z][a-z]{2})[a-z]*\s+(\d{1,2}),\s*(\d{4})/.exec(raw);
  if (!m) return "";
  const mm = MONTH_ABBR.indexOf(m[1]) + 1;
  return mm > 0 ? `${m[3]}-${String(mm).padStart(2, "0")}-${m[2].padStart(2, "0")}` : "";
}

/** ISO date from a <time datetime> or from prose like "Aug 25, 2026". */
function dateFrom(root: HTMLElement): { iso: string; updated: boolean } {
  const t = root.querySelector("time[datetime]");
  if (t) {
    return {
      iso: t.getAttribute("datetime") ?? "",
      updated: /updated/i.test(text(t.parentNode as HTMLElement)),
    };
  }
  const raw = text(root.querySelector("header p, .docs-meta"));
  return { iso: isoFromProse(raw), updated: /updated/i.test(raw) };
}

/**
 * The body, re-classed for the design.
 *
 * BeeRanked's prose is close to what the design wants; the differences are
 * mechanical. Tables gain the scroll box the design requires — the page must
 * never move sideways — and get the designer's classes so a table looks like
 * the reference rather than like a browser default.
 */
function bodyFrom(prose: HTMLElement | null): string {
  if (!prose) return "";

  prose.querySelectorAll("table").forEach((table) => {
    table.setAttribute("class", `j-table ${table.getAttribute("class") ?? ""}`.trim());
    // Figures in a table are aligned columns; give them the mono treatment.
    table.querySelectorAll("td").forEach((td) => {
      if (/^[\d.,:°′″×+\-\s/%]+$/.test(text(td)) && text(td).length > 0) {
        td.setAttribute("class", `j-mono ${td.getAttribute("class") ?? ""}`.trim());
      }
    });
    const wrap = parse('<div class="j-scroll"></div>').firstChild as HTMLElement;
    table.replaceWith(wrap);
    wrap.appendChild(table);
  });

  prose.querySelectorAll("pre").forEach((pre) => {
    pre.setAttribute("class", `j-pre ${pre.getAttribute("class") ?? ""}`.trim());
  });

  return prose.innerHTML;
}

function tocFrom(prose: HTMLElement | null): TocItem[] {
  if (!prose) return [];
  return prose
    .querySelectorAll("h2[id], h3[id], h4[id]")
    .map((h) => ({
      id: h.getAttribute("id") ?? "",
      text: text(h),
      level: h.rawTagName === "h2" ? 2 : 3,
    }))
    .filter((i) => i.id && i.text);
}

function crumbsFrom(root: HTMLElement): Crumb[] {
  const nav = root.querySelector("nav");
  if (!nav) return [];
  return nav
    .querySelectorAll("a")
    .map((a) => ({ href: a.getAttribute("href") ?? "", label: text(a) }))
    .filter((c) => c.href && c.label);
}

/** Every listing row on an index or hub page. */
function entriesFrom(root: HTMLElement): Entry[] {
  const seen = new Set<string>();
  const out: Entry[] = [];

  for (const a of root.querySelectorAll("a[href]")) {
    const href = a.getAttribute("href") ?? "";
    // A content link is /journal/<type>/<slug>/ — three segments or more.
    const m = /^\/journal\/(blog|docs|wiki|changelog)\/([^/?#]+)\/?$/.exec(href);
    if (!m || m[2] === "category" || seen.has(href)) continue;

    const title =
      text(a.querySelector(".tt-title, .cover-title, .docs-index-link")) || text(a);
    if (!title) continue;

    seen.add(href);
    const dateText = text(a.querySelector(".tt-date, .cover-date"));
    const iso = /(\d{4})-(\d{2})-(\d{2})/.exec(dateText)?.[0] ?? "";
    const img = a.querySelector("img");

    out.push({
      href,
      title,
      kind: KIND_BY_PREFIX[m[1]] ?? "writing",
      date: iso || dateText,
      dek: text(a.querySelector(".tt-dek, .cover-dek")),
      cover: img?.getAttribute("src") ?? null,
      updated: /updated/i.test(dateText),
    });
  }
  return out;
}

const KIND_OF_HREF = (href: string): Kind | null =>
  KIND_BY_PREFIX[/^\/journal\/([^/?#]+)/.exec(href)?.[1] ?? ""] ?? null;

/**
 * The sitemap's columns.
 *
 * Every row is kept. The designer's reference truncates each group to three
 * and offers "+ 18 more", but their page was drawn against invented content —
 * a sitemap that hides pages is not a sitemap, and this one is the human-
 * readable companion to sitemap.xml. If it ever grows long enough to be a
 * problem, that is a real problem to solve rather than one to pre-empt by
 * dropping rows.
 */
function sitemapGroups(main: HTMLElement): AzGroup[] {
  const out: AzGroup[] = [];

  for (const block of main.querySelectorAll(".sm-block")) {
    const h = block.querySelector("h2");
    if (!h) continue;

    // The heading carries its count in an <em>; the label is what remains.
    const em = h.querySelector("em");
    const label = text(h.querySelector("a")) || text(h).replace(text(em), "").trim();

    const rows: AzRow[] = [];
    for (const li of block.querySelectorAll("li")) {
      const a = li.querySelector("a");
      const href = a?.getAttribute("href") ?? "";
      const title = text(a);
      if (!href || !title) continue;
      rows.push({ href, title, date: isoFromProse(text(li.querySelector("time"))) });
    }
    if (!rows.length || !label) continue;

    out.push({
      kind: KIND_OF_HREF(rows[0].href),
      label,
      count: Number(text(em)) || rows.length,
      more: null,
      rows,
    });
  }
  return out;
}

/** The wiki index, filed A–Z by title. */
function azGroups(entries: Entry[]): AzGroup[] {
  const groups = new Map<string, AzRow[]>();
  for (const e of [...entries].sort((a, b) => a.title.localeCompare(b.title))) {
    /* Fold accents before taking the letter, so Ἑκατομβαιών and Ayanāṁśa file
       where a reader would look for them rather than under a letter of their
       own. */
    const folded = e.title.normalize("NFD").replace(/\p{Diacritic}/gu, "");
    const letter = /^\p{L}/u.test(folded) ? folded[0].toUpperCase() : "#";
    (groups.get(letter) ?? groups.set(letter, []).get(letter)!).push({
      href: e.href,
      title: e.title,
      date: e.date,
    });
  }
  return [...groups.entries()].map(([label, rows]) => ({
    kind: null,
    label,
    count: rows.length,
    more: null,
    rows,
  }));
}

/* The six groups a changelog entry may carry, in the order the design fixes
   them — never in whatever order the source happened to write them. */
const CHANGE_KEYS = ["added", "changed", "fixed", "deprecated", "removed", "security"];

function changeGroups(prose: HTMLElement | null): ChangeGroup[] {
  if (!prose) return [];
  const found = new Map<string, string[]>();

  for (const h of prose.querySelectorAll("h2, h3, h4, p > strong, .j-eyebrow")) {
    const key = text(h).toLowerCase().replace(/[^a-z]/g, "");
    if (!CHANGE_KEYS.includes(key)) continue;

    // The list belongs to the heading it follows.
    let node = h.nextElementSibling;
    while (node && node.rawTagName !== "ul" && node.rawTagName !== "ol") {
      if (/^h[1-6]$/.test(node.rawTagName ?? "")) { node = null; break; }
      node = node.nextElementSibling;
    }
    const notes = node ? node.querySelectorAll("li").map((li) => li.innerHTML.trim()) : [];
    if (notes.length) found.set(key, [...(found.get(key) ?? []), ...notes]);
  }

  return CHANGE_KEYS.filter((k) => found.has(k)).map((k) => ({ key: k, notes: found.get(k)! }));
}

/** The documentation sidebar, rebuilt from the synced index. */
async function navFrom(currentHref: string): Promise<NavGroup[]> {
  const file = fileFor(["docs"]);
  if (!file) return [];
  let html: string;
  try {
    html = await readFile(file, "utf8");
  } catch {
    return [];
  }
  const root = parse(html);
  const main = root.querySelector("main");
  if (!main) return [];

  const links = entriesFrom(main).map((e) => ({
    href: e.href,
    label: e.title,
    current: e.href.replace(/\/$/, "") === currentHref.replace(/\/$/, ""),
    sub: [] as TocItem[],
  }));
  return links.length ? [{ label: "Documentation", links }] : [];
}

/**
 * The releases on a changelog index.
 *
 * Written against BeeRanked's general shape rather than a specific one: no
 * changelog is synced yet — the source is GitHub and she has still to wire it
 * in Studio — so this reads what any sane rendering of a release list gives
 * (a link, a version, a date, a summary) and leans on nothing more. Check it
 * against the real markup once the first release lands.
 */
function releasesFrom(root: HTMLElement): Release[] {
  const seen = new Set<string>();
  const out: Release[] = [];

  for (const a of root.querySelectorAll("a[href]")) {
    const href = a.getAttribute("href") ?? "";
    if (!/^\/journal\/changelog\/[^/?#]+\/?$/.test(href) || seen.has(href)) continue;
    seen.add(href);

    const version =
      text(a.querySelector(".log-v, .j-log-v, .tt-title")) ||
      /v?\d+\.\d+(\.\d+)?/.exec(text(a))?.[0] ||
      text(a).split(" ")[0];
    const date = isoFromProse(text(a.querySelector("time")) || text(a));

    out.push({
      href,
      version,
      title: text(a.querySelector(".log-title")),
      date,
      summary: text(a.querySelector(".log-body, .log-sum, .tt-dek")),
      counts: {},
      groups: [],
    });
  }
  return out;
}

export async function read(parts: string[]): Promise<JournalPage | null> {
  const file = fileFor(parts);
  if (!file) return null;

  let html: string;
  try {
    html = await readFile(file, "utf8");
  } catch {
    return null;
  }

  const root = parse(html);
  const main = root.querySelector("main");
  if (!main) return null;

  /* Carried through untouched. It already names her domain, her Organization
     and her real profiles, so rewriting any of it would only be a chance to
     get it wrong. Parsed first though — a malformed block is dropped rather
     than emitted, because invalid JSON-LD is worse than none: a search engine
     that chokes on one block may ignore the rest of the page's markup. */
  const structuredData: string[] = [];
  for (const node of root.querySelectorAll('script[type="application/ld+json"]')) {
    const raw = node.textContent?.trim() ?? "";
    if (!raw) continue;
    try {
      structuredData.push(JSON.stringify(JSON.parse(raw)));
    } catch {
      /* Not ours to fix, and not worth failing a page over. */
    }
  }

  const type = typeOf(parts);
  const kind = kindOf(parts);
  const prose = main.querySelector(".prose, .docs-body, .wiki-body");
  const { iso, updated } = dateFrom(main);

  const rawTitle = text(root.querySelector("title"));
  const h1 = text(main.querySelector("h1, .docs-title"));
  const title = h1 || rawTitle.replace(/\s*[,·|]\s*Shruti.*$/i, "").trim();

  const meta = (name: string) =>
    root
      .querySelectorAll("meta")
      .find(
        (m) =>
          m.getAttribute("name") === name || m.getAttribute("property") === name,
      )
      ?.getAttribute("content") ?? "";

  const currentHref = `/journal/${parts.join("/")}${parts.length ? "/" : ""}`;
  const cover = main.querySelector("article img, .cover-media img")?.getAttribute("src") ?? null;
  const entries = entriesFrom(main);

  /* The wiki index files A–Z; the sitemap keeps the source's own sections. No
     other page type uses columns, and building them costs a pass over the
     document, so only the two that need them pay for it. */
  const groups =
    type === "sitemap"
      ? sitemapGroups(main)
      : type === "index" && kind === "wiki"
        ? azGroups(entries)
        : [];

  const release: Release | null =
    type !== "changelog-entry"
      ? null
      : {
          href: currentHref,
          version: title,
          title: text(main.querySelector(".log-project, .j-log-project")),
          date: iso,
          summary: meta("description"),
          counts: {},
          groups: changeGroups(prose),
        };

  return {
    type,
    kind,
    title,
    description: meta("description") || meta("og:description"),
    lede: text(main.querySelector(".hub-lede, .index-lede, header p:not(:has(time))")),
    crumbs: crumbsFrom(main),
    body: bodyFrom(prose),
    deck: meta("description"),
    date: iso,
    updated,
    cover,
    toc: tocFrom(prose),
    entries,
    count: entries.length,
    pagination: null,
    tags: [],
    nav: type === "docs" ? await navFrom(currentHref) : [],
    groups,
    releases: type === "changelog" ? releasesFrom(main) : [],
    release,
    structuredData,
    /* Only a written piece has a moment, and in the design only an article
       shows one. Documentation carries a provenance block instead — which
       ephemeris, which flags — because a page that is revised has no single
       instant to record, and the wiki carries neither. An index has none
       either, and asking would be a request per listing. */
    sky:
      type === "article"
        ? await moments(parts[parts.length - 1] ?? "")
        : { published: null, written: null },
  };
}

/** Every path the agent has written. */
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
