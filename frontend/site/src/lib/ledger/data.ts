/* The Ledger's data pack, read on the server.
 *
 * `GET /api/ledger/data` serves the pack (Contract 1 of docs/LEDGER.md) and
 * answers 404 when it is not loaded. That is a working state, not a failure:
 * a page asks `loadPack()`, and on null it renders "the game's data is not
 * loaded yet" and nothing that would need a figure.
 *
 * The pack is about 385 KB. A page render only needs to know that it is there
 * and which game it describes (the foot's data line), so the answer is kept
 * for a minute in this process rather than fetched again on every request.
 * The browser fetches its own copy for the reckoning (see `client.ts`): the
 * server renders the shell, the script fills it.
 *
 * ⚠ Server only: this imports lib/api.ts, which reads the environment. A
 * client script imports `client.ts` and `format.ts`, never this file.
 */
import { site } from "../api";
import type { LedgerData } from "./types";

export const DATA_PATH = "/api/ledger/data";
const KEEP_MS = 60_000;

let kept: { at: number; pack: LedgerData | null } | null = null;

/** The pack, or null when it is not loaded (or the backend did not answer). */
export async function loadPack(): Promise<LedgerData | null> {
  const now = Date.now();
  if (kept && now - kept.at < KEEP_MS) return kept.pack;
  const read = await site<LedgerData>(DATA_PATH);
  const pack = read && typeof read === "object" && read.game && Array.isArray(read.businessTypes) ? read : null;
  /* A miss is kept for less time than a hit: the pack arriving should show
     within seconds of the sync, not a minute later. */
  kept = { at: pack ? now : now - KEEP_MS + 5_000, pack };
  return pack;
}

/** Only the `game` block, for the foot's data line. */
export async function loadGame(): Promise<LedgerData["game"] | null> {
  return (await loadPack())?.game ?? null;
}
