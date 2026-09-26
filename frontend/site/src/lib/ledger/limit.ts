/* What limits it: the Ledger's one sentence (handoff README §3).
 *
 * The engine returns the sentence as `{key, template, params}`. The page
 * passes every template through say() (WhatLimitsIt.astro puts them in its
 * `data-words`), and this fills the person's words with the engine's params,
 * so an edited sentence still carries the right figures. The engine's own
 * English is the last resort, never a blank.
 *
 * States: held (with the fix button) · free · not known yet · cannot open ·
 * not a shop. Never red, never an icon; the sentence is aria-live.
 */
import type { LedgerData, Limit, Missing, Plan } from "./types.ts";
import { fill } from "./engine.ts";
import { articled, capital, listed } from "./format.ts";
import type { Words } from "./client.ts";

/** The engine's sentences, keyed as it keys them. Defaults for say(). */
export const LIMIT_SENTENCES: Record<string, string> = {
  "limit.noType": "Nothing to limit yet. Choose a business type and a building, and the Ledger works out what holds it back.",
  "limit.unknown": "Nothing to limit yet. Choose a building and the Ledger works out what holds this business back.",
  "limit.notAShop": "This building is not a shop. {typeA} needs a shop unit; the finder lists them.",
  "limit.notItsUse": "This building is not {useNoun}. {typeA} needs {useA}; the finder lists them.",
  "limit.noCustomers": "{typeA} serves no customers, so nothing holds its customers back.",
  "limit.cannotOpen": "Nothing to limit until it can open. It needs {need} first.",
  "limit.closed": "Nothing to limit while it never opens. Paint the hours it opens under Hours and staff.",
  "limit.free": "Nothing binds. Every customer who would come is served, every open hour.",
  "limit.held.building": "Held at {cap} customers an hour by the building, for {hours} hours of the week. How many more would come is not known: the game stops counting at the building's capacity. A building with a larger capacity is the change that lifts it.",
  "limit.held.registers": "Held at {cap} customers an hour by {count} {station}, for {hours} hours of the week. {would} would come. A {ordinal} {stationOne} ({cost}{withNeeds}) and {staffA} ({weeklyCost} a week) are worth {worth} a week.",
  "limit.held.staff": "Held at {cap} customers an hour by {count} staffed {station}, for {hours} hours of the week. {would} would come. Staffing the {ordinal} {stationOne} every open hour ({weeklyCost} a week) is worth {worth} a week.",
  "limit.held.displays": "Held at {cap} customers an hour for {product} by its displays, for {hours} hours of the week. {would} would come. {fixtureA} ({cost}) is worth {worth} a week.",
  "limit.held.displays.none": "Held for {product} by its displays, for {hours} hours of the week. Nothing in the game's catalogue displays it.",
  "limit.held.fixtures": "Held at {cap} customers an hour by the {fixture}, for {hours} hours of the week. {would} would come. Another ({cost}) is worth {worth} a week.",
};

/** The console's note, the fix buttons and the words around them. Defaults for say(). */
export const LIMIT_WORDS: Record<string, string> = {
  "limit.notLoaded": "Nothing to limit yet: the game's data is not loaded, so there is nothing honest to reckon with.",
  "note.held": "held · {hours} h",
  "note.free": "free",
  "note.unknown": "not known yet",
  "note.cannotOpen": "cannot open yet",
  "note.notAShop": "not this building",
  "fix.register": "Add a {ordinal} {stationOne}",
  "fix.staff": "Staff the {ordinal} {stationOne}",
  "fix.display": "Add {fixture}",
  "fix.fixture": "Add another {fixture}",
  "fix.building": "Find a larger building",
  "fix.note": "You can undo it, and Review shows before against after.",
  "fix.note.building": "The Building section ranks every building for this plan.",
  // the stats bar's value for "What limits it"
  "head.registers": "Registers",
  "head.staff": "Staff",
  "head.displays": "Displays",
  "head.fixtures": "Fixtures",
  "head.building": "The building",
  "head.free": "Nothing",
  "head.unknown": "—",
};

const w = (words: Words, key: string, fallback?: string) =>
  key in words ? words[key] : fallback ?? LIMIT_SENTENCES[key] ?? LIMIT_WORDS[key] ?? "";

/** The sentence, in the person's words with the engine's figures. */
export function limitSentence(limit: Limit | null, words: Words): string {
  if (!limit) return w(words, "limit.notLoaded");
  const s = limit.say;
  return fill(w(words, s.key, s.template), s.params);
}

/** The note at the console's right: `held · 47 h` / `free` / `not known yet`. */
export function limitNote(limit: Limit | null, words: Words): string {
  if (!limit) return w(words, "note.unknown");
  switch (limit.state) {
    case "held": return fill(w(words, "note.held"), { hours: String(limit.hours ?? 0) });
    case "free": return w(words, "note.free");
    case "cannot-open": return w(words, "note.cannotOpen");
    case "not-a-shop": return w(words, "note.notAShop");
    default: return w(words, "note.unknown");
  }
}

/** The one word the stats bar shows for the limit. */
export function limitHead(limit: Limit | null, words: Words): string {
  if (!limit) return w(words, "head.unknown");
  if (limit.state === "free") return w(words, "head.free");
  if (limit.state !== "held" || !limit.by) return w(words, "head.unknown");
  if (limit.by === "registers" && limit.fix?.kind === "staff") return w(words, "head.staff");
  return w(words, `head.${limit.by}`);
}

/** The fix button's label, or null when the limit has none to offer. */
export function fixLabel(limit: Limit | null, words: Words): string | null {
  const fix = limit?.fix;
  if (!limit || limit.state !== "held" || !fix) return null;
  const p = limit.say.params;
  if (fix.kind === "building") return w(words, "fix.building");
  if (!fix.plan) return null;
  if (fix.kind === "register") return fill(w(words, "fix.register"), p);
  if (fix.kind === "staff") return fill(w(words, "fix.staff"), p);
  const fixture = (p.fixtureA ?? p.fixture ?? "").replace(/^./, (c) => c.toLowerCase());
  return fill(w(words, fix.kind === "display" ? "fix.display" : "fix.fixture"), { ...p, fixture });
}

export function fixNote(limit: Limit | null, words: Words): string {
  return limit?.fix?.kind === "building" ? w(words, "fix.note.building") : w(words, "fix.note");
}

// ── It cannot open yet ───────────────────────────────────────────────────

/** Defaults for say(): the rows of "It cannot open yet". */
export const MISSING_WORDS: Record<string, string> = {
  "missing.path.fixtures": "fixtures · {short}",
  "missing.path.type": "type · course",
  "missing.path.products": "products",
  "missing.fixtures": "{typeA} needs {names} to open. Add one under Fixtures.",
  "missing.needs": "Each {neededBy} stands on {names}. Add one under Fixtures.",
  "missing.course": "{typeA} needs the {course} course finished first. A ledger's courses decide which types it can open.",
  "missing.products": "{typeA} needs one of {names} in stock. Choose it under Products.",
  "missing.or": "or",
};

/** One row per requirement a plan lacks: `{path, text}` for the note grid. */
export function missingRows(missing: Missing[], data: LedgerData, plan: Plan, words: Words): { path: string; text: string }[] {
  const mw = (k: string) => (k in words ? words[k] : MISSING_WORDS[k]);
  const type = data.businessTypes.find((t) => t.id === plan.typeId);
  const typeA = type ? capital(articled(type.name)) : "";
  const fx = (id: string) => data.fixtures.find((f) => f.id === id);
  return missing.map((m) => {
    if (m.path === "type") {
      return { path: mw("missing.path.type"), text: fill(mw("missing.course"), { typeA, course: m.names[0] ?? m.requirement }) };
    }
    if (m.path === "products") {
      return { path: mw("missing.path.products"), text: fill(mw("missing.products"), { typeA, names: listed(m.names, mw("missing.or")).toLowerCase() }) };
    }
    const ids = m.requirement.split("|");
    const short = (fx(ids[0])?.name ?? ids[0]).replace(/\s*\(.*\)$/, "").toLowerCase();
    const names = listed(m.names.map((n) => articled(n.replace(/\s*\(.*\)$/, ""))), mw("missing.or"));
    if (m.neededBy) {
      const by = (fx(m.neededBy)?.name ?? m.neededBy).toLowerCase();
      return { path: fill(mw("missing.path.fixtures"), { short }), text: fill(mw("missing.needs"), { neededBy: by, names }) };
    }
    return { path: fill(mw("missing.path.fixtures"), { short }), text: fill(mw("missing.fixtures"), { typeA, names }) };
  });
}

// ── mounting the console ─────────────────────────────────────────────────

export interface LimitView {
  /** Draw a limit; null draws the not-loaded sentence. */
  update(limit: Limit | null): void;
}

/**
 * Mount a WhatLimitsIt console. `onFix` runs when the fix button is pressed,
 * with the limit it was drawn for: apply `limit.fix.plan`, or for a building
 * limit, go to the Building section with ranking on.
 */
export function mountLimit(root: HTMLElement, onFix: (limit: Limit) => void, words?: Words): LimitView {
  const wd: Words = words ?? (() => { try { return JSON.parse(root.dataset.words || "{}"); } catch { return {}; } })();
  const text = root.querySelector<HTMLElement>("[data-limit-text]");
  const note = root.querySelector<HTMLElement>("[data-limit-note]");
  const fixRow = root.querySelector<HTMLElement>("[data-limit-fix]");
  const apply = root.querySelector<HTMLButtonElement>("[data-limit-apply]");
  const applyNote = root.querySelector<HTMLElement>("[data-limit-fix-note]");
  let current: Limit | null = null;
  apply?.addEventListener("click", () => { if (current) onFix(current); });
  return {
    update(limit) {
      current = limit;
      root.dataset.state = limit?.state ?? "unknown";
      const sentence = limitSentence(limit, wd);
      if (text && text.textContent !== sentence) text.textContent = sentence;
      if (note) note.textContent = limitNote(limit, wd);
      const label = fixLabel(limit, wd);
      if (fixRow) fixRow.hidden = !label;
      if (apply && label) apply.textContent = label;
      if (applyNote) applyNote.textContent = label ? fixNote(limit, wd) : "";
    },
  };
}
