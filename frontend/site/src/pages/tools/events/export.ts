// SPDX-License-Identifier: AGPL-3.0-only
/* The event table, taken away.
 *
 * A tool somebody writes from has to let them leave with the work. Three
 * shapes, because three different things are done with it: **CSV** for a
 * spreadsheet, **JSON** for whatever they are building, **Markdown** for
 * pasting straight into a draft.
 *
 * The whole-sign house is included when a rising sign is asked for, because
 * that is the column the export exists for — a list of events without the
 * rotation is the same list anyone can compute, and the rotation is the work.
 *
 * Times stay in Universal Time and say so. An export is read later, elsewhere,
 * possibly by someone in another country; a local time with no zone on it is
 * the failure this whole toolset is built around avoiding, and a file is
 * exactly where it would go unnoticed.
 */
import type { APIRoute } from "astro";
import { askAstro } from "../../../lib/api";
import { ZODIAC } from "../../../lib/signs";

const AVERSE = new Set([2, 6, 8, 12]);
const KINDS = "ingress,station,lunation,eclipse,aspect,void";

interface EventRow {
  kind: string; at: string; bodies: string[]; sign: string;
  degree: number; detail?: Record<string, any>;
}

const dm = (d: number) => {
  const deg = Math.floor(d);
  const min = Math.round((d - deg) * 60);
  return `${min === 60 ? deg + 1 : deg}°${String(min === 60 ? 0 : min).padStart(2, "0")}′`;
};

function describe(e: EventRow): string {
  const who = e.bodies.join(" · ");
  if (e.kind === "ingress") return `${who} enters ${e.sign}${e.detail?.retrograde ? " (retrograde)" : ""}`;
  if (e.kind === "station") return `${who} stations ${e.detail?.direction}`;
  if (e.kind === "lunation") return `${e.detail?.phase} moon`;
  if (e.kind === "eclipse") return `${e.detail?.type} ${e.detail?.of} eclipse`;
  if (e.kind === "aspect") return `${e.bodies[0]} ${e.detail?.aspect} ${e.bodies[1]}`;
  if (e.kind === "void") return `Moon void of course, ${e.detail?.minutes} minutes`;
  return e.kind;
}

/* RFC 4180: quote everything, and double an embedded quote. A planet name will
   never contain a comma, but "Moon void of course, 84 minutes" does — and a
   description that splits a row in half is a file somebody has to repair by
   hand before they can use it. */
const cell = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;

export const GET: APIRoute = async ({ url }) => {
  const format = (url.searchParams.get("format") ?? "csv").toLowerCase();
  const start = url.searchParams.get("start") ?? "";
  const end = url.searchParams.get("end") ?? "";
  const rising = ZODIAC.includes(url.searchParams.get("rising") as any)
    ? url.searchParams.get("rising")! : "";

  if (!/^\d{4}-\d{2}-\d{2}$/.test(start) || !/^\d{4}-\d{2}-\d{2}$/.test(end)) {
    return new Response("start and end must be YYYY-MM-DD\n", { status: 400 });
  }

  const answer = await askAstro<{ events: EventRow[] }>(
    `/events?start=${start}&end=${end}&kinds=${KINDS}&true_node=true`, 25000);
  if (!answer?.data) {
    return new Response("the ephemeris could not be reached\n", { status: 503 });
  }
  const events = answer.data.events;
  const houseOf = (s: string) =>
    rising ? ((ZODIAC.indexOf(s as any) - ZODIAC.indexOf(rising as any) + 12) % 12) + 1 : 0;

  const stem = `transits-${start}-to-${end}${rising ? `-${rising.toLowerCase()}` : ""}`;
  const attach = (type: string, ext: string, body: string) =>
    new Response(body, {
      headers: {
        "Content-Type": `${type}; charset=utf-8`,
        "Content-Disposition": `attachment; filename="${stem}.${ext}"`,
      },
    });

  if (format === "json") {
    return attach("application/json", "json", JSON.stringify({
      start, end, rising: rising || null,
      note: "All times are Universal Time, to the second.",
      count: events.length,
      events: events.map((e) => ({
        ...e,
        ...(rising ? { house: houseOf(e.sign), averse: AVERSE.has(houseOf(e.sign)) } : {}),
      })),
    }, null, 2));
  }

  if (format === "md" || format === "markdown") {
    const head = rising
      ? "| UT | What | Where | House |\n|---|---|---|---|"
      : "| UT | What | Where |\n|---|---|---|";
    const rows = events.map((e) => {
      const house = houseOf(e.sign);
      const where = e.kind === "void" ? "" : `${dm(e.degree)} ${e.sign}`;
      const base = `| ${e.at.slice(0, 16).replace("T", " ")} | ${describe(e)} | ${where} |`;
      return rising ? `${base} ${house}${AVERSE.has(house) ? " (averse)" : ""} |` : base;
    });
    return attach("text/markdown", "md", [
      `# Transits, ${start} to ${end}`,
      rising ? `\nRead from **${rising} rising**. Houses are whole-sign.` : "",
      "\nAll times Universal Time.\n",
      head, ...rows, "",
    ].join("\n"));
  }

  const header = ["utc", "kind", "bodies", "sign", "degree", "detail"];
  if (rising) header.push("house", "averse");
  const lines = [header.map(cell).join(",")];
  for (const e of events) {
    const house = houseOf(e.sign);
    const row: unknown[] = [
      e.at, e.kind, e.bodies.join(" "), e.sign, e.degree.toFixed(4), describe(e),
    ];
    if (rising) row.push(house, AVERSE.has(house) ? "yes" : "no");
    lines.push(row.map(cell).join(","));
  }
  return attach("text/csv", "csv", lines.join("\r\n") + "\r\n");
};
