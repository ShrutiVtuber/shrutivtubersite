/* Shruti's Guides on the site: the shape of a guide document, and words for
 * the parts of it that are not prose.
 *
 * The document is format 1 from the shrutisgametracker repository —
 * schema.json is the authority, and the backend validates against it before
 * anything is published, so a page may trust the SHAPE. What it may not trust
 * is the text: it is other people's writing and is rendered as text nodes,
 * never as HTML.
 *
 * ⚠ No English lives here. A gate is turned into words with a vocabulary the
 * page passes in from its own copy(), so "or later" is editable from the
 * admin like every other sentence a reader sees.
 */
export type Gate = Record<string, unknown>;

export interface Variant { id: string; name: string }
export interface Field {
  id: string; label: string; type: "number" | "ordered";
  min?: number; max?: number; options?: string[]; labels?: Record<string, string>;
  show_when?: Gate; applies_to?: string[];
}
export interface Link { label?: string; url: string; type?: string }
export interface Phase {
  id: string; name: string; band?: string; order: number; skip_group?: string; track?: string;
}
export interface Step {
  id: string; phase: string; kind: "milestone" | "optional" | "system"; order: number;
  title: string; oneliner?: string; do?: string; done_when?: string; why?: string;
  minutes?: number; ongoing?: boolean; gate?: Gate; auto_done?: Gate;
  applies_to?: string[]; codex?: string; links?: Link[];
}
export interface Routine {
  id: string; name: string; resets: "session" | "daily" | "weekly" | "manual";
  items: { id: string; text: string }[]; gate?: Gate; applies_to?: string[];
}
export interface CodexEntry {
  id: string; name: string; group?: string; show_when?: Gate; ignore_until?: string;
  what?: string; when?: string; how?: string; caveats?: string[]; links?: Link[];
}
export interface CodexNote { id: string; title: string; items: string[] }
export interface Track {
  id: string; name: string; applies_to?: string[]; day_one?: string[];
  ranks?: { n: number; capstone: string; when?: string }[];
  counters?: { id: string; label: string; max?: number; nudge_at?: number; nudge?: string }[];
  sections?: { id: string; title: string; body: string }[];
}
export interface GuideDoc {
  format: number;
  game: { id: string; name: string; variants?: Variant[] };
  guide: {
    id: string; title: string; authors?: string[]; version?: string; game_patch?: string;
    summary?: string; caveats?: string[];
  };
  checkin?: Field[]; phases?: Phase[]; steps?: Step[]; routines?: Routine[];
  codex?: CodexEntry[]; codex_notes?: CodexNote[]; tracks?: Track[];
}

/** The vocabulary a page hands in. Each is a template with {named} holes. */
export interface GateWords {
  min: string; max: string; atLeast: string; is: string; variant: string; after: string; once: string;
}

export const fill = (template: string, vars: Record<string, string>) =>
  template.replace(/\{(\w+)\}/g, (_, k: string) => vars[k] ?? "");

/** A check-in option's display name: the declared label, else the id tidied. */
export function optionLabel(field: Field | undefined, option: string): string {
  const named = field?.labels?.[option];
  if (named) return named;
  /* `act4` reads "Act 4", `base_done` reads "Base done". */
  const plain = option.replace(/_/g, " ").replace(/([a-z])(\d)/gi, "$1 $2");
  return plain.charAt(0).toUpperCase() + plain.slice(1);
}

/**
 * A gate as a list of short phrases, one per condition. All must hold, and
 * the page joins them however it likes. An absent or empty gate is no phrases.
 */
export function gateWords(gate: Gate | undefined, doc: GuideDoc, words: GateWords): string[] {
  if (!gate) return [];
  const fields = new Map((doc.checkin ?? []).map((f) => [f.id, f]));
  const variants = new Map((doc.game.variants ?? []).map((v) => [v.id, v.name]));
  const codex = new Map((doc.codex ?? []).map((c) => [c.id, c.name]));
  const out: string[] = [];
  for (const [key, value] of Object.entries(gate)) {
    if (key === "variant") {
      out.push(fill(words.variant, { name: variants.get(String(value)) ?? String(value) }));
      continue;
    }
    if (key === "steps_done") {
      out.push(fill(words.after, { ids: (Array.isArray(value) ? value : [value]).map(String).join(", ") }));
      continue;
    }
    if (key === "codex_active") {
      const names = (Array.isArray(value) ? value : [value]).map((id) => codex.get(String(id)) ?? String(id));
      out.push(fill(words.once, { names: names.join(", ") }));
      continue;
    }
    /* ⚠ Greedy on purpose: `season_rank_min` is the field `season_rank`. */
    const m = /^(.+)_(min|max|at_least|is)$/.exec(key);
    if (!m) {
      out.push(`${key} ${String(value)}`);
      continue;
    }
    const field = fields.get(m[1]);
    const what = field?.label ?? m[1];
    if (m[2] === "min") out.push(fill(words.min, { what, n: String(value) }));
    else if (m[2] === "max") out.push(fill(words.max, { what, n: String(value) }));
    else if (m[2] === "at_least") out.push(fill(words.atLeast, { what, value: optionLabel(field, String(value)) }));
    else out.push(fill(words.is, { what, value: optionLabel(field, String(value)) }));
  }
  return out;
}

export const phasesOf = (doc: GuideDoc): Phase[] =>
  [...(doc.phases ?? [])].sort((a, b) => a.order - b.order);

export const stepsOf = (doc: GuideDoc, phase: Phase): Step[] =>
  (doc.steps ?? []).filter((s) => s.phase === phase.id).sort((a, b) => a.order - b.order);

/** Variant names for an applies_to list; empty when it applies to all. */
export function variantNames(ids: string[] | undefined, doc: GuideDoc): string[] {
  if (!ids || ids.length === 0) return [];
  const all = doc.game.variants ?? [];
  if (ids.length >= all.length && all.every((v) => ids.includes(v.id))) return [];
  return ids.map((id) => all.find((v) => v.id === id)?.name ?? id);
}

/** Codex entries grouped by their `group`, in order of first appearance. */
export function codexGroups(doc: GuideDoc): [string, CodexEntry[]][] {
  const groups = new Map<string, CodexEntry[]>();
  for (const entry of doc.codex ?? []) {
    const key = entry.group ?? "";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(entry);
  }
  return [...groups.entries()];
}

/**
 * ⚠ A link in a guide is somebody else's URL. Only http(s) is drawn as an
 * anchor; anything else — javascript:, data:, a bare word — is shown as text.
 */
export const safeUrl = (url: unknown): string =>
  typeof url === "string" && /^https?:\/\/\S+$/i.test(url) ? url : "";

export const titled = (s: string) =>
  s ? s.charAt(0).toUpperCase() + s.slice(1).replace(/[_-]/g, " ") : "";
