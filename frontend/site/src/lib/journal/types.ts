/* What a journal page is, once BeeRanked's HTML has been read.
 *
 * The designer replaced the section's markup entirely — their skeleton is
 * `.j-page` / `.j-shell` / `.j-col` / `.j-rail`, nothing like what BeeRanked
 * emits. So the implementer's job is to pull the DATA out of the synced pages
 * and hand it to components that render their structure. These are the shapes
 * that pass between the two halves.
 */

/** The four content types, and the glyph each is marked with. */
export type Kind = "writing" | "documentation" | "wiki" | "changelog";

export const GLYPH: Record<Kind, string> = {
  writing: "☾",
  documentation: "♄",
  wiki: "☿",
  changelog: "♃",
};

export const KIND_LABEL: Record<Kind, string> = {
  writing: "Writing",
  documentation: "Documentation",
  wiki: "Wiki",
  changelog: "Changelog",
};

/** Which of the designer's pages to render. */
export type PageType =
  | "hub"
  | "all"
  | "index"        // blog / docs / wiki listing
  | "category"
  | "article"
  | "docs"
  | "wiki"
  | "changelog"
  | "changelog-entry"
  | "sitemap";

export interface Entry {
  href: string;
  title: string;
  kind: Kind;
  /** ISO date, or empty when the source gave none. */
  date: string;
  dek: string;
  cover: string | null;
  /** Documentation shows "updated" rather than a publication date. */
  updated: boolean;
}

/** A leader-line row — the sitemap's columns and the wiki's A–Z. */
export interface AzRow {
  href: string;
  title: string;
  /** dd.MM. These rows carry no year; the design gives them none. */
  date: string;
}

/** One heading in a leader-line column, with its rows beneath it. */
export interface AzGroup {
  /** Set when the group is a content type, so it can carry the type mark. */
  kind: Kind | null;
  label: string;
  count: number;
  /** Where the rest lives, when a group is shown in part. */
  more: string | null;
  rows: AzRow[];
}

export interface TocItem {
  id: string;
  text: string;
  /** h2 = 2, h3 = 3. Deeper levels are folded into 3. */
  level: number;
}

export interface Crumb {
  href: string;
  label: string;
}

export interface NavLink {
  href: string;
  label: string;
  current: boolean;
  /** In-page anchors under the current document. */
  sub: TocItem[];
}

export interface NavGroup {
  label: string;
  links: NavLink[];
}

export interface ChangeGroup {
  /** added · changed · fixed · deprecated · removed · security */
  key: string;
  notes: string[];
}

export interface Release {
  href: string;
  version: string;
  title: string;
  date: string;
  summary: string;
  counts: Record<string, number>;
  groups: ChangeGroup[];
}

/** The sky at one moment in an entry's life — stored, never recomputed. */
export interface SkyRecord {
  sunTropical: string;
  sunSidereal: string;
  moonTropical: string;
  moonSidereal: string;
  tithi: string;
  nakshatra: string;
  attic: string;
  thelemic: string;
  rule: string;
}

export interface JournalPage {
  type: PageType;
  kind: Kind;
  title: string;
  description: string;
  /** The section masthead's lede, where the page has one. */
  lede: string;
  crumbs: Crumb[];
  /** Article and docs body, as HTML, already re-classed for the design. */
  body: string;
  deck: string;
  date: string;
  updated: boolean;
  cover: string | null;
  toc: TocItem[];
  entries: Entry[];
  /** Blog index and category archives. */
  count: number;
  pagination: { prev: string | null; next: string | null; page: number } | null;
  tags: { href: string; label: string; count: number | null; current: boolean }[];
  nav: NavGroup[];
  /** Sitemap columns and the wiki's A–Z. */
  groups: AzGroup[];
  releases: Release[];
  release: Release | null;
  sky: import("./sky").Moments;
}
