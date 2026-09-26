/* One of the school's journal posts for the app:
   GET /carnatic/journal/{slug}.json (docs/carnatic/API.md §7). The body is
   the journal's own article HTML, as /journal/blog/{slug}/ shows it. */
import type { APIRoute } from "astro";
import { schoolArticle } from "../../../lib/carnatic/journal";
import { cachedJson } from "../../../lib/carnatic/jsonResponse";
import { SITE_URL } from "../../../lib/api";

export const GET: APIRoute = async ({ params, request }) => {
  const a = await schoolArticle(params.slug ?? "");
  if (!a) return cachedJson(request, { code: "NOT_FOUND", detail: "No such journal post." }, 404);
  return cachedJson(request, { ...a, url: SITE_URL + a.href });
};
