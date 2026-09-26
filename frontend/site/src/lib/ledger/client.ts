/* The Ledger's data pack, read in the browser.
 *
 * The reckoning runs here (docs/LEDGER.md: "every change re-reckons at
 * once"), so the page needs the whole pack. It is about 385 KB, too much to
 * inline into every render, so the server draws the shell and the script
 * fetches the pack once, on its own origin (no third party), and shares the
 * one promise with anything else on the page that asks.
 *
 * Also here: reading a component's `data-words`, the say() strings a script
 * draws with. Every word a script writes comes from one of these maps.
 */
import type { LedgerData } from "./types.ts";

export const DATA_PATH = "/api/ledger/data";

let asked: Promise<LedgerData | null> | null = null;

/** The pack, or null when it is not loaded. Fetched once per page. */
export function fetchPack(): Promise<LedgerData | null> {
  if (!asked) {
    asked = fetch(DATA_PATH, { headers: { accept: "application/json" }, credentials: "same-origin" })
      .then(async (r) => {
        if (!r.ok) return null;
        const body = (await r.json()) as LedgerData;
        return body && Array.isArray(body.businessTypes) ? body : null;
      })
      .catch(() => null);
  }
  return asked;
}

export type Words = Record<string, string>;

/** The say() strings a component handed its script, as JSON in `data-words`. */
export function wordsOf(el: HTMLElement | null | undefined): Words {
  try {
    return el?.dataset.words ? (JSON.parse(el.dataset.words) as Words) : {};
  } catch {
    return {};
  }
}

/** A word by key, with the engine's own English as the last resort. */
export const word = (w: Words, key: string, fallback = ""): string => (key in w ? w[key] : fallback);
