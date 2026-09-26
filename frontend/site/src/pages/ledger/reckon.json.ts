/* POST /ledger/reckon.json: the Ledger's figures for the Squirrel Guides app
 * (docs/LEDGER.md Contract 5). The handler is lib/ledger/reckon.ts; this
 * file only hands it the pack and the words.
 *
 * WHY AN ASTRO ROUTE, not FastAPI: the engine is TypeScript, and running it
 * here is how the app, the website and the overlays can never disagree.
 * Caddy sends /api/* to the Python backend, so the route lives under /ledger.
 *
 * WHY IT NEEDS NO SESSION AND NO CSRF TOKEN: it reads nothing about anybody
 * and writes nothing. The plan arrives in the body, the answer is arithmetic
 * on it and the game's public facts, and no cookie is read or honoured. A
 * forged cross-site POST could only make a browser compute something and
 * throw the answer away (and a browser cannot even send it: application/json
 * is not a simple content type, so a cross-origin page is stopped at the
 * preflight, which this route never answers). The app is native, so it needs
 * no CORS headers either, and none are sent.
 *
 * The middleware keeps it in the guides section: hidden with the section it
 * is a 404 (JSON), but the holding page does not swallow it, as it does not
 * swallow /api/*.
 */
import type { APIRoute } from "astro";
import { copy } from "../../lib/copy";
import { loadPack } from "../../lib/ledger/data";
import { notAllowed, reckonRoute, wordsFrom } from "../../lib/ledger/reckon";

export const prerender = false;

/* The words the pages say, read from the same scopes: What limits it
   (component:WhatLimitsIt), It cannot open yet (ledger/plan), the change
   labels (component:StreamSwitch) and the figures bar (component:LedgerStats). */
async function words() {
  const [limit, plan, stream, stats] = await Promise.all([
    copy("component:WhatLimitsIt"), copy("ledger/plan"), copy("component:StreamSwitch"), copy("component:LedgerStats"),
  ]);
  return wordsFrom({ limit, plan, stream, stats });
}

export const POST: APIRoute = reckonRoute({ pack: loadPack, words });
export const ALL: APIRoute = notAllowed;
