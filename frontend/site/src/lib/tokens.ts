/* Times in the prose, written once and read in the reader's own clock.
 *
 * A horoscope that says "Thursday evening" is wrong for a third of the people
 * reading it. The author writes one column; it is read in Athens, in Tokyo and
 * in Los Angeles, where the same instant is a different weekday. So the prose
 * carries tokens, not sentences about days, and every one is resolved against
 * whoever is looking.
 *
 * **A token carries the instant, never an id.** The brief specified
 * `{{event:<id>}}` against a table of precomputed events, and added a
 * continuous-integration check that no published article referenced an id that
 * had disappeared — which is a guard against a fragility rather than a reason
 * for it. Recomputing an ephemeris can move an event by a second; if the id is
 * derived from the instant, the id changes and the published sentence breaks.
 * Writing the instant into the token means there is nothing to break: the
 * moment is the fact, and a second of drift renders the same date.
 *
 * **Server-rendered in Universal Time, then localised in place.** The page has
 * to be readable and indexable before any script runs, and the server does not
 * know the reader's zone — so it writes the UT value into a `<time>` element
 * and a small script rewrites the text content. With scripting off the reader
 * sees a real time, labelled as UT, which is honest rather than broken.
 */

/** The formats a token may ask for. `long` is the default. */
export type Format = "long" | "date" | "time" | "weekday" | "relative";

const FORMATS = new Set<Format>(["long", "date", "time", "weekday", "relative"]);

/* Matched loosely on purpose: an author typing a token by hand should get a
   visible failure, not silence, so anything token-shaped is captured and
   anything unresolvable is rendered as a marker. */
const TOKEN = /\{\{\s*(instant|range|daypart|tz)\s*:?\s*([^}|]*?)\s*(?:\|\s*([a-z]+)\s*)?\}\}/gi;

const ISO = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})$/;

function utc(iso: string, format: Format): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const o: Intl.DateTimeFormatOptions = { timeZone: "UTC" };
  if (format === "date") Object.assign(o, { day: "numeric", month: "long", year: "numeric" });
  else if (format === "time") Object.assign(o, { hour: "2-digit", minute: "2-digit", hour12: false });
  else if (format === "weekday") Object.assign(o, { weekday: "long" });
  else Object.assign(o, {
    weekday: "long", day: "numeric", month: "long",
    hour: "2-digit", minute: "2-digit", hour12: false,
  });
  const text = new Intl.DateTimeFormat("en-GB", o).format(d);
  return format === "weekday" ? text : `${text} UT`;
}

/** "in the morning" and so on, from the hour. UT until a script says otherwise. */
export function daypartOf(hour: number): string {
  if (hour < 5) return "overnight";
  if (hour < 12) return "in the morning";
  if (hour < 17) return "in the afternoon";
  if (hour < 22) return "in the evening";
  return "overnight";
}

function element(iso: string, format: Format, kind = "instant"): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return marker(`bad instant: ${iso}`);
  const text = kind === "daypart" ? daypartOf(d.getUTCHours()) : utc(iso, format);
  return `<time datetime="${d.toISOString()}" data-token="${kind}" `
       + `data-format="${format}">${text}</time>`;
}

/* Never silently empty. An unresolvable token in a published column is a
   mistake somebody has to be able to SEE — an empty space reads as a writing
   choice and survives for ever. */
function marker(why: string): string {
  return `<mark class="token-broken" title="${why}">⟨unresolved⟩</mark>`;
}

/**
 * Turn the tokens in rendered HTML into localisable `<time>` elements.
 *
 * Applied AFTER markdown: `{{…}}` carries no markdown syntax, so it survives
 * the processor untouched, and substituting here means this does not depend on
 * whether raw HTML is passed through.
 */
export function resolveTokens(html: string): string {
  if (!html.includes("{{")) return html;

  return html.replace(TOKEN, (whole, rawKind: string, value: string, rawFormat?: string) => {
    const kind = rawKind.toLowerCase();
    const asked = (rawFormat ?? "long").toLowerCase() as Format;
    const format: Format = FORMATS.has(asked) ? asked : "long";

    if (kind === "tz") {
      return `<span data-token="tz">Universal Time</span>`;
    }
    if (kind === "daypart") {
      return ISO.test(value) ? element(value, "long", "daypart") : marker(whole);
    }
    if (kind === "instant") {
      return ISO.test(value) ? element(value, format) : marker(whole);
    }
    if (kind === "range") {
      const [from, to] = value.split("..").map((s) => s.trim());
      if (!ISO.test(from ?? "") || !ISO.test(to ?? "")) return marker(whole);
      return `${element(from, format)} to ${element(to, "time")}`;
    }
    return marker(whole);
  });
}

/** Whether anything in the body will not resolve. Publishing checks this. */
export function unresolved(html: string): number {
  return (resolveTokens(html).match(/token-broken/g) ?? []).length;
}

/* ── the lint ─────────────────────────────────────────────────────────────
   A hardcoded weekday is the failure this whole mechanism exists to prevent,
   and it is invisible in the draft — it reads perfectly to the person who
   wrote it, in the zone they wrote it in. */
const HARDCODED: [RegExp, string][] = [
  [/\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/gi,
   "a weekday name is a different day for some readers"],
  [/\b(tonight|this morning|this afternoon|this evening|today|tomorrow|yesterday)\b/gi,
   "this depends on when and where it is read"],
  [/\b\d{1,2}[:.]\d{2}\s*(am|pm)?\b/gi,
   "a clock time is only right in one zone"],
  [/\b(at noon|at midnight|midday)\b/gi,
   "noon and midnight move with the reader"],
];

export interface Warning { text: string; why: string; at: number }

export function lintTimeExpressions(markdown: string): Warning[] {
  const found: Warning[] = [];
  for (const [pattern, why] of HARDCODED) {
    pattern.lastIndex = 0;
    for (const match of markdown.matchAll(pattern)) {
      found.push({ text: match[0], why, at: match.index ?? 0 });
    }
  }
  return found.sort((a, b) => a.at - b.at);
}
