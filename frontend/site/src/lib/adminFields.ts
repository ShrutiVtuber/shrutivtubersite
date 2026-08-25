/* What each field in the block editor actually is.
 *
 * The editor was generic: it listed a row's columns and made every one a text
 * box labelled with its column name. That is readable if you wrote the schema
 * and baffling otherwise — `body_md`, `media_id`, `repo_url` — and it gave no
 * hint of where anything ends up. An image field in particular said nothing
 * about which picture on which page it was going to become, so filling it in
 * was a guess you had to go and check.
 *
 * So the shape of each kind is described here instead of inferred. Where a
 * field is not described the old behaviour still applies, which keeps a column
 * added later visible rather than silently dropped from the form.
 */

export type FieldType =
  | "text" | "textarea" | "url" | "slug" | "select" | "checkbox" | "media" | "number";

export interface FieldSpec {
  label: string;
  /** One line under the input, saying what it is for. */
  help?: string;
  type?: FieldType;
  options?: { value: string; label: string }[];
  /** Fields with the same group are shown together, in first-seen order. */
  group?: string;
  placeholder?: string;
}

/**
 * Where a kind's image actually appears — and, where it does not, that it
 * does not.
 *
 * A picker is only offered where a template actually draws the picture.
 * Offering one that stores a row and changes no page is the exact confusion
 * this whole change is about, so a kind with nowhere to show an image says so
 * instead of pretending.
 */
export const MEDIA_USE: Record<string, { label: string; where: string } | { unused: true }> = {
  projects: {
    label: "Screenshot",
    where: "Appears on the Work page, inside this project's card. Without one, the card shows the designed “screenshot pending” plate.",
  },
  "fan-art": {
    label: "The artwork",
    where: "Appears in the fan works gallery. This is the piece itself, not a thumbnail.",
  },
  sections: {
    label: "Image",
    where: "Appears at the top of this block, above its words, across the width of the text.",
  },
  // Tools list themselves by name and summary; no template draws a picture for
  // one. The column exists, so the day a tool page wants an illustration this
  // is one line — but until then, saying so beats a control that does nothing.
  tools: { unused: true },
};

const STATUS = [
  { value: "active", label: "Active — worked on now" },
  { value: "maintained", label: "Maintained — stable, still cared for" },
  { value: "archived", label: "Archived — finished or set down" },
];

/* Visibility and order are not described here on purpose: the editor never
   renders them. Both are handled in the list view — a toggle and a reorder on
   each row — which is the right place for them, because you change them while
   looking at the list rather than while writing one item. */
const COMMON: Record<string, FieldSpec> = {
  slug: {
    label: "Slug",
    type: "slug",
    help: "The last part of its address. Changing it breaks any link already shared.",
    group: "Publishing",
  },
  body_md: {
    label: "Body",
    type: "textarea",
    help: "Markdown. Headings, links and lists all work.",
    group: "Content",
  },
};

export const FIELDS: Record<string, Record<string, FieldSpec>> = {
  projects: {
    name: { label: "Name", group: "Content", placeholder: "Theourgia" },
    tagline: {
      label: "Tagline", group: "Content",
      help: "One line, shown under the name on the card.",
    },
    body_md: { ...COMMON.body_md, help: "Markdown. The longer description on the Work page." },
    media_id: { label: "Screenshot", type: "media", group: "Image" },
    repo_url: {
      label: "Repository", type: "url", group: "Links",
      placeholder: "https://github.com/…",
      help: "Shown as the “source” link. Leave blank if it is not public.",
    },
    site_url: {
      label: "Live site", type: "url", group: "Links",
      placeholder: "https://…",
      help: "Shown as the “visit” link.",
    },
    featured: {
      label: "Lead the home page with this",
      type: "checkbox",
      group: "Publishing",
      help: "The home page shows two projects. Tick the two you want a stranger to meet first — tick more and the first two in portfolio order win. With none ticked it falls back to the first two, so the section is never empty. A hidden project is never shown, featured or not.",
    },
    status: { label: "Status", type: "select", options: STATUS, group: "Details" },
    role: {
      label: "Your role", group: "Details",
      placeholder: "Author and maintainer",
      help: "Shown in the credits table. Blank reads as “not recorded yet”.",
    },
    stack: {
      label: "Stack", group: "Details",
      placeholder: "Python · FastAPI · Postgres",
      help: "Shown in the credits table, and beside the card as its meta line.",
    },
    licence: { label: "Licence", group: "Details", placeholder: "AGPL-3.0-only" },
    contributors: {
      label: "Contributors", group: "Details",
      help: "Names besides yours, if any.",
    },
    slug: COMMON.slug,
  },

  sections: {
    page: {
      label: "Page", group: "Where",
      help: "The route this block belongs to — home, about, work.",
    },
    key: {
      label: "Key", group: "Where",
      help: "How the template addresses this block. Changing it can make the block stop appearing.",
    },
    kind: { label: "Kind", group: "Where", help: "Which component draws it." },
    eyebrow: { label: "Eyebrow", group: "Content", help: "The small line above the title." },
    title: { label: "Title", group: "Content" },
    body_md: COMMON.body_md,
    link_label: { label: "Link text", group: "Links", placeholder: "Read the notes" },
    link_url: { label: "Link address", type: "url", group: "Links" },
    media_id: { label: "Image", type: "media", group: "Image" },
  },

  tools: {
    name: { label: "Name", group: "Content" },
    summary: { label: "Summary", group: "Content", help: "One line, shown in the tools list." },
    body_md: COMMON.body_md,
    media_id: { label: "Image", type: "media", group: "Image" },
    locale: { label: "Language", group: "Details", help: "Leave blank unless it is language-specific." },
    slug: COMMON.slug,
  },

  "fan-art": {
    artist: { label: "Artist", group: "Content" },
    title: { label: "Title of the piece", group: "Content" },
    media_id: { label: "The artwork", type: "media", group: "Image" },
    url: { label: "Where to find them", type: "url", group: "Links" },
  },

  links: {
    platform: { label: "Platform", group: "Content", placeholder: "Twitch" },
    label: { label: "Label", group: "Content", help: "What the link says." },
    url: { label: "Address", type: "url", group: "Content" },
    category: { label: "Category", group: "Details", help: "Groups links together." },
  },

  credits: {
    name: { label: "Name", group: "Content" },
    role: { label: "What they did", group: "Content", placeholder: "Rigging" },
    url: { label: "Their site", type: "url", group: "Content" },
  },

  "profile-fields": {
    label: { label: "Label", group: "Content", placeholder: "Pronouns" },
    value: { label: "Value", group: "Content", placeholder: "she/her" },
  },
};

/** The order groups are shown in. Anything unlisted follows, in first-seen order. */
export const GROUP_ORDER = ["Content", "Image", "Links", "Details", "Where", "Publishing"];

/** A readable label for a column nothing describes yet. */
export function humanLabel(key: string): string {
  return key
    .replace(/_(md|url|id)$/, "")
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/^./, (c) => c.toUpperCase());
}

/** The spec for one field, falling back to a guess from its name. */
export function specFor(kind: string, key: string): FieldSpec {
  const known = FIELDS[kind]?.[key];
  if (known) return known;
  return {
    label: humanLabel(key),
    type: key.endsWith("_md") ? "textarea"
      : key.endsWith("_url") || key === "url" ? "url"
      : key === "media_id" ? "media"
      : "text",
  };
}
