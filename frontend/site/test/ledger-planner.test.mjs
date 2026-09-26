/* The Ledger's planner: its words, its drawings, and its place in the site.
 *
 * The planner (src/lib/ledger/planner.ts) draws with the page's say()
 * strings only, read by key from `data-words`. A key the script asks for that
 * the page does not give would show the reader a key, so every one is
 * checked against src/pages/ledger/plan.astro here.
 *
 * The drawings are pure (lib/ledger/limit, notes, stair, format, statsbar) and
 * are checked against the engine's own figures for the brief's sample. Those
 * tests need the data pack and SKIP without it, as the engine's tests do; the
 * source checks never skip.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { reckon, priceStair, money as engineMoney, fill as engineFill } from "../src/lib/ledger/engine.ts";
import { money, fill, lineValue, dataLine, factor } from "../src/lib/ledger/format.ts";
import { limitSentence, limitNote, fixLabel, missingRows, LIMIT_SENTENCES } from "../src/lib/ledger/limit.ts";
import { planChanges, compareRows, savedSentence } from "../src/lib/ledger/notes.ts";
import { drawStair } from "../src/lib/ledger/stair.ts";
import { intensity } from "../src/lib/ledger/grid.ts";
import { drawFigureBreakdown } from "../src/lib/statsbar.ts";

const SRC = fileURLToPath(new URL("../src/", import.meta.url));
const read = (p) => readFileSync(join(SRC, p), "utf8");

// ── the page gives every word the script asks for ────────────────────────

test("every word the planner script draws is a say() string on the page", () => {
  const script = read("lib/ledger/planner.ts");
  const page = read("pages/ledger/plan.astro");
  const asked = new Set([...script.matchAll(/\bt[f]?\("([^"]+)"/g)].map((m) => m[1]));
  // keys built at run time: one per section, building use and class
  for (const s of ["type", "building", "products", "fixtures", "hours", "campaigns", "assumptions", "review"]) asked.add(`section.${s}`);
  for (const u of ["shop", "office", "warehouse", "home", "cinema", "theatre", "special"]) asked.add(`use.${u}`);
  for (const c of ["working", "middle", "upper"]) asked.add(`class.${c}`);
  const given = new Set([
    ...[...page.matchAll(/"([^"]+)":\s*say\(/g)].map((m) => m[1]),
    ...[...page.matchAll(/^\s+([a-zA-Z]+):\s*say\(/gm)].map((m) => m[1]),
  ]);
  // section.* arrive through NAMES
  for (const s of ["type", "building", "products", "fixtures", "hours", "campaigns", "assumptions", "review"]) {
    if (page.includes(`say("section.${s}"`)) given.add(`section.${s}`);
  }
  const missing = [...asked].filter((k) => !given.has(k)).sort();
  assert.deepEqual(missing, [], `the planner asks for words the page does not give:\n  ${missing.join("\n  ")}`);
});

test("the planner, the notes and the staircase write no English of their own", () => {
  // Their defaults are for the page's say(); the script only reads keys.
  const script = read("lib/ledger/planner.ts");
  // a run of words between two tags: ">Every customer buys<"
  const html = [...script.matchAll(/>\s*([A-Za-z][a-z]+(?:[ ,][A-Za-z]+)+[.!]?)\s*</g)].map((m) => m[1]);
  assert.deepEqual(html, [], `English written into the planner's markup:\n  ${html.join("\n  ")}`);
});

test("the engine's sentences are all in What limits it's words", () => {
  const engine = read("lib/ledger/engine.ts");
  const component = read("components/ledger/WhatLimitsIt.astro");
  const keys = [...engine.matchAll(/say\("(limit\.[^"]+)"/g)].map((m) => m[1]);
  assert.ok(keys.length >= 10, "the engine's limit sentences were found");
  for (const k of new Set(keys)) {
    assert.ok(component.includes(`say("${k}"`), `WhatLimitsIt.astro has no say() for ${k}`);
    assert.ok(k in LIMIT_SENTENCES, `lib/ledger/limit.ts has no fallback for ${k}`);
  }
});

// ── the Ledger in the site's chrome ──────────────────────────────────────

test("the Ledger is the sixth tab of the lockup strip, before Create a guide", () => {
  const nav = read("components/chrome/GuidesNav.astro");
  const hrefs = [...nav.matchAll(/\["(\/[^"]*)",\s*say\(/g)].map((m) => m[1]);
  /* Play (the hub, 26 Sep 2026) is the first tab, ahead of the rooms. */
  assert.deepEqual(hrefs, ["/play", "/guides", "/builds", "/groups", "/guides/overlays", "/ledger", "/guides/write"]);
});

test("the Ledger is in the Play menu, the wing's pages and the sitemap", () => {
  const header = read("components/chrome/SiteHeader.astro");
  assert.match(header, /\["\/ledger",\s*"Ledger"\]/, "NAV has the Ledger as a tuple");
  assert.match(header, /group\.play[^\]]*"\/ledger"/, "the Play group lists /ledger");
  assert.match(read("layouts/BaseLayout.astro"), /\(guides\|builds\|groups\|tracker\|ledger\|play\)/);
  const sitemap = read("pages/sitemap.xml.ts");
  for (const p of ["/ledger", "/ledger/plan"]) assert.ok(sitemap.includes(`["${p}",`), `${p} is in the sitemap`);
  assert.ok(read("pages/guides/index.astro").includes('href: "/ledger"'), "Also in this wing lists the Ledger");
});

test("the Ledger's pages carry the sub-bar, the foot and one h1", () => {
  for (const p of ["pages/ledger/plan.astro", "pages/ledger/index.astro", "pages/ledger/places.astro", "pages/ledger/calculators.astro"]) {
    const src = read(p);
    assert.ok(src.includes("<LedgerBar"), `${p} has the sub-bar`);
    assert.ok(src.includes("<LedgerFoot"), `${p} has the foot`);
    const h1 = (src.match(/<h1[\s>]/g) || []).length + (src.match(/<Head\b/g) || []).length;
    assert.equal(h1, 1, `${p} has exactly one h1`);
  }
  // Places and Calculators are built and public now: test/ledger-places.test.mjs checks they are in the sitemap.
});

test("no Ledger style is red or green", () => {
  const css = read("styles/ledger.css");
  assert.ok(!css.includes("--live"), "ledger.css never uses --live");
  assert.ok(!/#(?:[0-9a-f]{3}){1,2}\b/i.test(css.replace(/--ink-faint:\s*#[0-9A-F]+|--rose:\s*#[0-9A-F]+/gi, "")),
    "ledger.css carries no hex but the two section values");
});

// ── the formatters agree with the engine ────────────────────────────────

test("money and fill are the engine's, to the character", () => {
  for (const n of [0, 1, 73171.4, -1820, 1234567.5, null, NaN]) assert.equal(money(n), engineMoney(n));
  const t = "Held at {cap} by {who}, {unknown}";
  assert.equal(fill(t, { cap: "20", who: "one register" }), engineFill(t, { cap: "20", who: "one register" }));
});

test("a breakdown line carries its sign, and a not-counted line is a dagger", () => {
  assert.equal(lineValue({ op: "+", value: 93561.2, unit: "money", honesty: "approximate" }), "+$93,561");
  assert.equal(lineValue({ op: "−", value: 2359, unit: "money", honesty: "counted" }), "−$2,359");
  assert.equal(lineValue({ op: "×", value: 0.85, unit: "factor", honesty: "counted" }), "×0.85");
  assert.equal(lineValue({ op: "−", value: null, unit: "money", honesty: "not-counted" }), "†");
  assert.equal(factor(1.424), "×1.424");
  assert.equal(dataLine({ name: "Big Ambitions", version: "1.0", build: "3682", gathered: "2026-09-25" }),
    "Big Ambitions · 1.0 · build 3682 · gathered 25 Sep 2026");
});

test("the grid-intensity rule runs from 6 to 32", () => {
  assert.equal(intensity(0), 6);
  assert.equal(intensity(15), 19);
  assert.equal(intensity(30), 32);
  assert.equal(intensity(90), 32);
});

// ── with the pack: the sample, drawn ────────────────────────────────────

const PACK = process.env.LEDGER_PACK
  || join(homedir(), "Documents/development/shrutisgametracker/research/big-ambitions/ledger.json");
const HAVE = existsSync(PACK);
const SKIP = HAVE ? false : `SKIPPED: the Ledger data pack is not at ${PACK}.`;
const data = HAVE ? JSON.parse(readFileSync(PACK, "utf8")) : null;
const it = (name, fn) => test(name, { skip: SKIP }, fn);
const CTX = { difficulty: "normal", courses: [] };
const open = (n = 1) => Array.from({ length: 7 }, () => Array.from({ length: 24 }, (_, h) => (h >= 9 && h < 21 ? n : 0)));
const sample = (over = {}) => ({
  typeId: "gift-shop", buildingId: "12-2nd-avenue", prices: {},
  fixtures: { "cash-register": 1, "cabinet-with-drawers": 1, "shopping-baskets": 1, "rounded-shelf": 4, "product-panel": 3 },
  hours: open(1), campaigns: {}, satisfaction: 80, satisfactionTyped: false,
  staff: { "customer-service": { wage: 20 }, cleaning: { hours: 42, wage: 14 } }, ...over,
});

it("the planner's sample is the brief's: What limits it reads the handoff's sentence", async () => {
  const { samplePlan } = await import("../src/lib/ledger/planner.ts");
  const r = reckon(data, samplePlan(), CTX);
  assert.equal(r.customers.value, 1459);
  assert.equal(limitNote(r.limit, {}), "held · 47 h");
  assert.match(limitSentence(r.limit, {}), /^Held at 20 customers an hour by one register, for 47 hours of the week\. 30 would come\. A second register \(\$1,370 with its cabinet\)/);
  assert.equal(fixLabel(r.limit, {}), "Add a second register");
});

it("a person's own words carry the engine's figures", () => {
  const r = reckon(data, sample(), CTX);
  const words = { "limit.held.registers": "{hours} hours held; {would} would come." };
  assert.equal(limitSentence(r.limit, words), "47 hours held; 30 would come.");
});

it("with no building, the limit is not known yet and the note says so", () => {
  const r = reckon(data, sample({ buildingId: null }), CTX);
  assert.equal(limitNote(r.limit, {}), "not known yet");
  assert.equal(fixLabel(r.limit, {}), null);
  assert.equal(limitSentence(null, {}).startsWith("Nothing to limit yet"), true);
});

it("a register missing reads as It cannot open yet, with a path and a sentence", () => {
  const r = reckon(data, sample({ fixtures: { "shopping-baskets": 1 } }), CTX);
  assert.equal(r.limit.state, "cannot-open");
  const rows = missingRows(r.missing, data, sample(), {});
  assert.ok(rows.length >= 1);
  assert.equal(rows[0].path, "fixtures · cash register");
  assert.match(rows[0].text, /^A gift shop needs a cash register or a checkout counter to open\./);
});

it("Before it saves lists each change, and the comparison moves with it", () => {
  const kept = sample();
  const r0 = reckon(data, kept, CTX);
  const next = r0.limit.fix.plan;
  const rows = planChanges(data, kept, next, {});
  assert.deepEqual(rows.map((x) => x.path), ["fixtures · cabinet with drawers", "fixtures · cash register", "hours · registers"]);
  assert.match(rows[1].text, /^1 → 2\. Buy the difference in the game before it opens tomorrow\.$/);
  const cmp = compareRows(r0, reckon(data, next, CTX), {});
  assert.equal(cmp[0].label, "The week");
  assert.equal(cmp[0].caret, "▲");
  assert.match(cmp[0].change, /^\+\$12,84[45]$/);
  assert.match(savedSentence(rows, {}), /^Saved\. fixtures · cabinet with drawers: 1 → 2; fixtures · cash register: 1 → 2; hours · registers: 84 h → 168 h\.$/);
  assert.deepEqual(planChanges(data, kept, sample(), {}), []);
});

it("the staircase draws its markers, merged when the best is the edge", () => {
  const s = priceStair(data, "gift-cheap", "hells-kitchen", {}, { unitsAtEdge: 1290 });
  const html = drawStair(s, { product: "Gift (cheap)", unitsAtEdge: 1290 });
  assert.match(html, /market \$18\.00/);
  assert.ok(html.includes("<path d=\"M"), "a stepped path");
  const labels = [...html.matchAll(/lg-stair-label[^>]*>([^<]+)</g)].map((m) => m[1]);
  assert.ok(labels.some((l) => l.includes("every customer buys")), labels.join(" | "));
  const back = drawStair(priceStair(data, "gift-cheap", "hells-kitchen", { backorder: true }), { product: "Gift (cheap)" });
  assert.match(back, /Backordered: there is nothing to sell this week/);
});

it("the week's breakdown groups money in and out, strikes what is not counted, and keeps the key", () => {
  const r = reckon(data, sample(), CTX);
  const out = r.week.total.lines.filter((l) => l.op === "−");
  const html = drawFigureBreakdown({
    title: "The week", value: money(r.week.total.value), honesty: r.week.total.honesty,
    groups: [{ label: "Money in", lines: r.week.moneyIn.lines }, { label: "Money out", lines: out }],
    total: { label: "The week", value: money(r.week.total.value) },
    words: { foot: "Every line names something you can go and change.", key: "≈ approximate · † not counted" },
  });
  assert.match(html, /\$73,171<sup class="lg-mark">≈<\/sup>/);
  assert.match(html, /data-state="not-counted"[\s\S]*?Tax, taken at the year(?:&#39;|')s end[\s\S]*?†/);
  assert.ok(html.includes("Every line names something you can go and change."));
});
