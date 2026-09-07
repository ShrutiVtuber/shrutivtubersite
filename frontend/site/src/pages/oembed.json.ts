// SPDX-License-Identifier: AGPL-3.0-only
/* oEmbed, so a pasted link becomes the wheel.
 *
 * Discord, WordPress and most editors ask a site what to do with a URL before
 * they decide to show a bare link. Answering turns every shared tool link into
 * a picture of the sky, which is the difference between a link somebody
 * ignores and one they follow.
 *
 * `rich` rather than `photo`: the wheel is an iframe, and a photo response
 * would have to be a PNG that cannot be stepped or clicked through.
 *
 * The URL is checked against this site and against the two paths that have an
 * embed. An oEmbed endpoint that echoes back whatever it is handed is a way to
 * put arbitrary markup in somebody else's page under our domain's name.
 */
import type { APIRoute } from "astro";
import { SITE_URL } from "../lib/api";
import { ZODIAC } from "../lib/signs";

const MAX = 1000;
const MIN = 240;

/**
 * The middle of a period, as an instant — what to draw the sky for.
 *
 * The MIDDLE rather than the start: a monthly reading is about the month, and
 * the sky on the 1st is the sky of the handover, not of the thing described.
 * Noon UT for the same reason a daily reading is not about midnight.
 *
 * Weeks go through the ISO rule — week 1 is the one holding January 4th — so
 * this agrees with the ids the backend mints rather than counting sevens from
 * the 1st and drifting a week every few years.
 */
function instantFor(period: string, covers: string): string {
  const noon = (y: number, m: number, d: number) =>
    new Date(Date.UTC(y, m - 1, d, 12)).toISOString().slice(0, 19) + "Z";

  if (period === "daily") {
    const [y, m, d] = covers.split("-").map(Number);
    return noon(y, m, d);
  }
  if (period === "monthly") {
    const [y, m] = covers.split("-").map(Number);
    return noon(y, m, 15);
  }
  if (period === "yearly") return noon(Number(covers), 7, 2);

  /* weekly: YYYY-Www. January 4th is always in week 1, so step back to that
     week's Monday and forward by whole weeks. */
  const [ys, ws] = covers.split("-W");
  const jan4 = new Date(Date.UTC(Number(ys), 0, 4, 12));
  const dow = (jan4.getUTCDay() + 6) % 7;            // Monday = 0
  const monday = new Date(jan4.getTime() - dow * 864e5
                          + (Number(ws) - 1) * 7 * 864e5);
  const thursday = new Date(monday.getTime() + 3 * 864e5);
  return thursday.toISOString().slice(0, 19) + "Z";
}

export const GET: APIRoute = async ({ url }) => {
  const target = url.searchParams.get("url") ?? "";
  const format = (url.searchParams.get("format") ?? "json").toLowerCase();
  const width = Math.min(MAX, Math.max(MIN, Number(url.searchParams.get("maxwidth") ?? 520)));

  if (format !== "json") {
    /* The spec says 501 for a format we do not implement, not 400 — the
       request was well formed and we simply do not speak XML. */
    return new Response("only json\n", { status: 501 });
  }

  let asked: URL;
  try {
    asked = new URL(target);
  } catch {
    return new Response("url must be absolute\n", { status: 400 });
  }
  if (asked.origin !== new URL(SITE_URL).origin) {
    return new Response("not a link to this site\n", { status: 404 });
  }

  /* /tools/events and a dated reading are the two things worth embedding. */
  const events = asked.pathname === "/tools/events";
  const reading = asked.pathname.match(
    /^\/horoscopes\/([a-z]+)\/(daily|weekly|monthly|yearly)\/([\w-]+)$/);
  if (!events && !reading) {
    return new Response("nothing embeddable at that address\n", { status: 404 });
  }

  /* A reading's wheel is rotated to its sign and set to ITS period, not to
     now. Somebody pasting last month's reading should get last month's sky —
     a card showing today's would be a picture of a different chart than the
     words underneath it. */
  const rising = events
    ? (ZODIAC.includes(asked.searchParams.get("rising") as any)
        ? asked.searchParams.get("rising")! : "")
    : (reading![1].charAt(0).toUpperCase() + reading![1].slice(1));
  const at = events
    ? (asked.searchParams.get("at") ?? "")
    : instantFor(reading![2], reading![3]);

  const src = `${SITE_URL}/embed/wheel?rising=${encodeURIComponent(rising)}`
    + (at ? `&at=${encodeURIComponent(at)}` : "");
  const height = Math.round(width * 1.08);
  const title = events
    ? (rising ? `Transit wheel — ${rising} rising` : "Transit wheel")
    : `${rising} — ${reading![3]} — Shruti`;

  return new Response(JSON.stringify({
    version: "1.0",
    type: "rich",
    provider_name: "Shruti",
    provider_url: SITE_URL,
    title,
    width,
    height,
    html: `<iframe src="${src}" width="${width}" height="${height}" `
        + `style="border:0;max-width:100%" loading="lazy" `
        + `title="Transit wheel — shrutivtuber.com"></iframe>`,
  }, null, 2), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
};
