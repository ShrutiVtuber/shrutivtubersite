/* How the Ledger writes a figure, shared by the server and the scripts.
 *
 * Pure: no DOM, no fetch, so `node --test` loads it as it loads the engine.
 * Every WORD here is a template the page passes in (from say()); this file
 * only writes numbers and puts them into the words.
 *
 *   —      no figure
 *   0      a real fact, shown as $0 / 0
 *   ≈      approximate: it rests on something assumed
 *   †      not counted: the game charges it, the Ledger cannot price it
 *   −$1,820 a loss is the sign, never a colour
 */
import type { BreakdownLine, Figure, Honesty, LedgerData, LineUnit } from "./types.ts";

/* ⚠ `money` and `fill` are the engine's own two formatters, repeated here so
   that the site's stats bar (lib/statsbar.ts, used by /builds and the
   overlays) can write a Ledger figure without loading the whole engine.
   test/ledger-format.test.mjs holds them to the engine's output. */

/** $1,370 · −$1,820. Rounded to the dollar, as every headline figure is. */
export function money(n: number | null): string {
  if (n == null || !Number.isFinite(n)) return "—";
  const r = Math.round(n);
  return (r < 0 ? "−" : "") + "$" + Math.abs(r).toLocaleString("en-US");
}

/** Fill a say() template: "Held at {cap}" + {cap: "20"}. Unknown names stay as written. */
export function fill(template: string, params: Record<string, string>): string {
  return template.replace(/\{(\w+)\}/g, (m, k: string) => (k in params ? params[k] : m));
}

export const DASH = "—";
export const MARK: Record<Honesty, string> = { counted: "", approximate: "≈", "not-counted": "†" };

export const escape = (t: unknown): string =>
  String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c] as string));

/** 1,459 · rounded to a whole. */
export const count = (n: number | null | undefined): string =>
  n == null || !Number.isFinite(n) ? DASH : Math.round(n).toLocaleString("en-US");

/** $25.63 — a shelf price, to the cent. */
export const price = (n: number | null | undefined): string =>
  n == null || !Number.isFinite(n) ? DASH : `${n < 0 ? "−" : ""}$${Math.abs(n).toFixed(2)}`;

/** ×0.85 — a multiplier. Two places, three when the third says something. */
export const factor = (n: number | null | undefined): string => {
  if (n == null || !Number.isFinite(n)) return DASH;
  const two = n.toFixed(2);
  const three = n.toFixed(3);
  return `×${Number(three) === Number(two) ? two : three.replace(/0$/, "")}`;
};

/** 12.3 days · a payback. */
export const days = (n: number | null | undefined, unit = "days"): string =>
  n == null || !Number.isFinite(n) ? DASH : `${(Math.round(n * 10) / 10).toLocaleString("en-US")} ${unit}`;

/** A figure by its unit, with no sign. */
export function byUnit(value: number | null, unit: LineUnit, units: Partial<Record<LineUnit, string>> = {}): string {
  if (value == null || !Number.isFinite(value)) return DASH;
  switch (unit) {
    case "money": return money(Math.abs(value));
    case "price": return price(Math.abs(value));
    case "factor": return factor(value);
    case "count": return count(Math.abs(value));
    case "hours": return `${count(Math.abs(value))} ${units.hours ?? "h"}`;
    case "days": return days(Math.abs(value), units.days ?? "days");
    case "years": return days(Math.abs(value), units.years ?? "years");
    case "percent": return `${count(Math.abs(value))} %`;
    default: return count(value);
  }
}

/** A breakdown line's value as the popover writes it: +$1,234 · −$2,359 · ×0.85 · † */
export function lineValue(l: BreakdownLine, units: Partial<Record<LineUnit, string>> = {}): string {
  if (l.value == null) return MARK["not-counted"];
  const body = byUnit(l.value, l.unit, units);
  if (l.value === 0 && (l.unit === "money" || l.unit === "price")) return body; // $0 is a fact, with no sign
  if (l.op === "×" || l.unit === "factor") return l.unit === "factor" ? body : `×${body}`;
  if (l.op === "÷") return `÷${body}`;
  if (l.op === "=") return l.value < 0 && (l.unit === "money" || l.unit === "price") ? `−${body}` : body;
  if (l.op === "−") return `−${body}`;
  return l.value < 0 && (l.unit === "money" || l.unit === "price") ? `−${body}` : `+${body}`;
}

/** A headline: its value, and its honesty mark as a superscript. HTML. */
export function withMark(text: string, honesty: Honesty | undefined): string {
  const m = honesty ? MARK[honesty] : "";
  return `${escape(text)}${m ? `<sup class="lg-mark">${m}</sup>` : ""}`;
}

/** A money Figure's headline text: $73,171 · −$1,820 · —. */
export const figureMoney = (f: Figure | null | undefined): string => money(f?.value ?? null);

/** "Big Ambitions · 1.0 · build 3682 · gathered 25 Sep 2026" — on every Ledger page. */
export function dataLine(game: LedgerData["game"] | null | undefined,
  words: { build?: string; gathered?: string } = {}): string {
  if (!game) return "";
  const parts = [game.name, game.version];
  if (game.build) parts.push(fill(words.build ?? "build {build}", { build: game.build }));
  if (game.gathered) parts.push(fill(words.gathered ?? "gathered {date}", { date: shortDate(game.gathered) }));
  return parts.filter(Boolean).join(" · ");
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
/** 2026-09-25 → 25 Sep 2026 */
export function shortDate(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || "");
  if (!m) return iso;
  return `${Number(m[3])} ${MONTHS[Number(m[2]) - 1] ?? m[2]} ${m[1]}`;
}

/** 9 → "09" */
export const pad2 = (h: number): string => String(h).padStart(2, "0");

/** "a gift shop" from "Gift shop" (the article the sentences need). */
export const articled = (name: string): string => `${/^[aeiou]/i.test(name) ? "an" : "a"} ${name.toLowerCase()}`;
export const capital = (s: string): string => s.charAt(0).toUpperCase() + s.slice(1);

/** "a, b and c" */
export function listed(items: string[], and = "and"): string {
  if (items.length <= 1) return items[0] ?? "";
  return `${items.slice(0, -1).join(", ")} ${and} ${items[items.length - 1]}`;
}
