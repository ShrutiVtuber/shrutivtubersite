/* The school's journal posts for the app: GET /carnatic/journal.json
   (docs/carnatic/API.md §7). Newest first, without bodies. */
import type { APIRoute } from "astro";
import { schoolArticles } from "../../lib/carnatic/journal";
import { cachedJson } from "../../lib/carnatic/jsonResponse";
import { SITE_URL } from "../../lib/api";

export const GET: APIRoute = async ({ request }) => {
  const items = (await schoolArticles()).map((a) => ({ ...a, url: SITE_URL + a.href }));
  return cachedJson(request, { items });
};
