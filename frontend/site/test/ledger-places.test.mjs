/* The Ledger's Places and Calculators: the pure halves, the words, and their
 * place in the site.
 *
 *   lib/ledger/places.ts       virtualWindow · sortInForce · nextSort · placesRows · hoodTiles · mixClasses
 *   lib/ledger/drawer.ts       recordView · layoutArticle
 *   lib/ledger/calculators.ts  stepTarget · stepYears · campaignHref · defaultBuilding · unitsAtEdgeFor
 *
 * Tests that need the data pack SKIP without it, as the engine's do; the
 * source checks and the pure math never skip.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { virtualWindow, sortInForce, nextSort, placesRows, hoodTiles, mixClasses, mixWords, defaultFilters, canRank, OVERSCAN }
  from "../src/lib/ledger/places.ts";
import { recordView, layoutArticle, FINISHABLE_YEARS } from "../src/lib/ledger/drawer.ts";
import { stepTarget, stepYears, campaignHref, defaultBuilding, unitsAtEdgeFor, TARGET } from "../src/lib/ledger/calculators.ts";
import { cheapestCampaigns } from "../src/lib/ledger/engine.ts";

const PACK = process.env.LEDGER_PACK
  || join(homedir(), "Documents/development/shrutisgametracker/research/big-ambitions/ledger.json");
const HAVE = existsSync(PACK);
const SKIP = HAVE ? false : `SKIPPED: the Ledger data pack is not at ${PACK}.`;
const data = HAVE ? JSON.parse(readFileSync(PACK, "utf8")) : null;
const withPack = (name, fn) => test(name, { skip: SKIP }, fn);

const SRC = fileURLToPath(new URL("../src/", import.meta.url));
const read = (p) => readFileSync(join(SRC, p), "utf8");
const CTX = { difficulty: "normal", courses: [] };
const HOURS = () => Array.from({ length: 7 }, () => Array.from({ length: 24 }, (_, h) => (h >= 9 && h < 21 ? 1 : 0)));
const giftShop = () => ({
  typeId: "gift-shop", buildingId: "12-2nd-avenue", prices: {}, campaigns: {}, satisfaction: 80, satisfactionTyped: false,
  fixtures: { "cash-register": 1, "cabinet-with-drawers": 1, "shopping-baskets": 1, "rounded-shelf": 4, "product-panel": 3 },
  hours: HOURS(),
});

// ── the virtual window ─────────────────────────────────────────────────────

test("the virtual window draws the rows in view and six either side", () => {
  // 600px scroller, 56px rows, at the top: rows 0–10 are in view (0..600/56 → 11), plus six below
  assert.deepEqual(virtualWindow(0, 600, 56, 883), { start: 0, end: 11 + OVERSCAN, height: 883 * 56 });
  // scrolled to row 100 exactly: six above it, the ~11 in view and six below
  const w = virtualWindow(100 * 56, 600, 56, 883);
  assert.equal(w.start, 94);
  assert.equal(w.end, Math.ceil((100 * 56 + 600) / 56) + OVERSCAN);
  assert.ok(w.end - w.start <= 11 + 1 + 2 * OVERSCAN, "never more than the view and the overscan");
});

test("the virtual window stays inside the list", () => {
  assert.deepEqual(virtualWindow(0, 520, 88, 0), { start: 0, end: 0, height: 0 });
  const near = virtualWindow(1e6, 520, 88, 20); // scrolled past the end
  assert.ok(near.start <= near.end && near.end === 20);
  assert.equal(virtualWindow(-40, 520, 88, 20).start, 0, "a rubber-band scroll above the top");
  assert.equal(virtualWindow(0, 520, 88, 3).end, 3, "a short list is drawn whole");
  assert.equal(virtualWindow(0, 520, 88, 883).end, Math.ceil(520 / 88) + OVERSCAN, "88px rows on the phone");
});

// ── sort ───────────────────────────────────────────────────────────────────

test("the sort in force: chosen, else the planned week when ranking, else the address", () => {
  const f = defaultFilters();
  assert.deepEqual(sortInForce(f, true), { sort: "week", dir: -1 });
  assert.deepEqual(sortInForce(f, false), { sort: "address", dir: 1 });
  assert.deepEqual(sortInForce({ ...f, sort: "rent", dir: 1 }, false), { sort: "rent", dir: 1 });
  assert.deepEqual(sortInForce({ ...f, sort: "week", dir: 1 }, false), { sort: "address", dir: 1 }, "no week to sort by without a plan");
});

test("a sort head flips its own direction and starts a new one where it reads best", () => {
  assert.deepEqual(nextSort({ sort: "week", dir: -1 }, "week"), { sort: "week", dir: 1 });
  assert.deepEqual(nextSort({ sort: "week", dir: 1 }, "week"), { sort: "week", dir: -1 });
  assert.deepEqual(nextSort({ sort: "week", dir: -1 }, "address"), { sort: "address", dir: 1 });
  assert.deepEqual(nextSort({ sort: "address", dir: 1 }, "rent"), { sort: "rent", dir: -1 });
});

test("a plan without a type is not ranked for", () => {
  assert.equal(canRank(null), false);
  assert.equal(canRank({ typeId: null }), false);
  assert.equal(canRank({ typeId: "gift-shop" }), true);
});

test("the classes a neighbourhood mostly is, largest first", () => {
  assert.deepEqual(mixClasses({ working: 0.06, middle: 0.82, upper: 0.12 }), ["middle", "upper"]);
  assert.deepEqual(mixClasses({ working: 0, middle: 0.06, upper: 0.94 }), ["upper"]);
  const w = { class: { working: "working", middle: "middle", upper: "upper" }, and: "and", template: "{classes} class", none: "every class" };
  assert.equal(mixWords(["middle", "upper"], w), "middle and upper class");
  assert.equal(mixWords([], w), "every class");
});

withPack("filters: neighbourhood, use and capacity narrow the list; any use lists all 883", () => {
  const all = placesRows(data, null, CTX, { ...defaultFilters(), use: "any", rank: false });
  assert.equal(all.length, data.buildings.length);
  const shops = placesRows(data, null, CTX, { ...defaultFilters(), use: "shop", rank: false });
  assert.equal(shops.length, data.buildings.filter((b) => b.use === "shop").length);
  const hk30 = placesRows(data, null, CTX, { ...defaultFilters(), use: "shop", hood: "hells-kitchen", cap: 30, rank: false });
  assert.ok(hk30.length > 0);
  for (const r of hk30) {
    const b = data.buildings.find((x) => x.id === r.id);
    assert.equal(b.neighbourhood, "hells-kitchen"); assert.equal(b.use, "shop"); assert.equal(b.capacity, 30);
  }
  const addresses = shops.map((r) => data.buildings.find((x) => x.id === r.id).address);
  assert.deepEqual(addresses, [...addresses].sort((a, b) => a.localeCompare(b)), "unranked, by address");
});

withPack("ranked for a plan: the best planned week first, and a sort head reverses it", () => {
  const f = { ...defaultFilters(), use: "shop", hood: "hells-kitchen" };
  const rows = placesRows(data, giftShop(), CTX, f);
  const weeks = rows.map((r) => r.week).filter((w) => w != null);
  assert.ok(weeks.length > 0);
  assert.deepEqual(weeks, [...weeks].sort((a, b) => b - a));
  const up = placesRows(data, giftShop(), CTX, { ...f, sort: "week", dir: 1 }).map((r) => r.week).filter((w) => w != null);
  assert.deepEqual(up, [...up].sort((a, b) => a - b));
  const rent = placesRows(data, giftShop(), CTX, { ...f, sort: "rent", dir: -1 }).map((r) => data.buildings.find((x) => x.id === r.id).rentDay).filter((x) => x != null);
  assert.deepEqual(rent, [...rent].sort((a, b) => b - a));
});

withPack("the index strip: seven tiles, counts for the use, a rent level for each", () => {
  const tiles = hoodTiles(data, "shop");
  assert.equal(tiles.length, 7);
  assert.equal(tiles.reduce((a, t) => a + t.count, 0), data.buildings.filter((b) => b.use === "shop").length);
  const hk = tiles.find((t) => t.id === "hells-kitchen");
  assert.equal(hk.accepts, 1.424);
  assert.equal(hk.ads, 0.7);
  assert.deepEqual(hk.mix, ["middle", "upper"]);
  assert.equal(tiles.find((t) => t.id === "midtown").rent, "high", "Midtown's shops rent dearest a m²");
  assert.deepEqual(new Set(tiles.map((t) => t.rent)), new Set(["low", "middling", "high"]));
  assert.equal(hoodTiles(data, "any").reduce((a, t) => a + t.count, 0), data.buildings.length);
});

// ── the record drawer ──────────────────────────────────────────────────────

test("a layout code takes the article it is read with", () => {
  assert.equal(layoutArticle("C2"), "a");
  assert.equal(layoutArticle("F2"), "an");
  assert.equal(layoutArticle("E1"), "an");
  assert.equal(layoutArticle("D2"), "a");
});

withPack("the record of 12 2nd Avenue: its facts and its rent or buy", () => {
  const v = recordView(data, "12-2nd-avenue");
  assert.equal(v.address, "12 2nd Avenue");
  assert.equal(v.hood, "Hell's Kitchen");
  assert.equal(v.capacity, 30);
  assert.equal(v.rentDay, 337);
  assert.equal(v.rentYear, 337 * 60);
  assert.equal(v.price, 146520752);
  assert.ok(Math.abs(v.repayYears - 146520752 / (337 * 60)) < 1e-6);
  assert.equal(v.robKind, v.repayYears > FINISHABLE_YEARS ? "repays-rent-cheaper" : "repays");
  assert.equal(recordView(data, "no-such-building"), null);
  const notForRent = data.buildings.find((b) => b.rentDay == null);
  if (notForRent) assert.equal(recordView(data, notForRent.id).robKind, "not-for-rent");
});

// ── the calculators ────────────────────────────────────────────────────────

test("the promotion target steps by 5 between 5 and 120", () => {
  assert.equal(stepTarget(20, 1), 25);
  assert.equal(stepTarget(20, -1), 15);
  assert.equal(stepTarget(TARGET.min, -1), TARGET.min);
  assert.equal(stepTarget(TARGET.max, 1), TARGET.max);
});

test("the years step by one to 20 and by ten beyond, between 1 and 400", () => {
  assert.equal(stepYears(5, 1), 6);
  assert.equal(stepYears(19, 1), 20);
  assert.equal(stepYears(20, 1), 30);
  assert.equal(stepYears(30, -1), 20);
  assert.equal(stepYears(20, -1), 19);
  assert.equal(stepYears(1, -1), 1);
  assert.equal(stepYears(400, 1), 400);
});

test("Use this mix in the plan opens the planner on the building with the mix on", () => {
  const href = campaignHref("12-2nd-avenue", ["internet-small", "billboard-small"]);
  const u = new URL(href, "https://x.test");
  assert.equal(u.pathname, "/ledger/plan");
  assert.equal(u.searchParams.get("building"), "12-2nd-avenue");
  assert.equal(u.searchParams.get("campaigns"), "internet-small,billboard-small");
  assert.equal(u.searchParams.get("section"), "campaigns");
});

withPack("a console starts on the building asked for, else the neighbourhood's first shop", () => {
  assert.equal(defaultBuilding(data, "hells-kitchen", ["12-2nd-avenue"]).id, "12-2nd-avenue");
  const first = defaultBuilding(data, "midtown", ["12-2nd-avenue"]); // asked-for is in another neighbourhood
  assert.equal(first.neighbourhood, "midtown");
  assert.equal(first.use, "shop");
});

withPack("the campaigns are the game's own, and the cheapest mix reaching a target costs least", () => {
  assert.deepEqual(data.campaigns.map((c) => c.id),
    ["internet-small", "internet-medium", "internet-large", "billboard-small", "billboard-medium", "billboard-large"]);
  const a = cheapestCampaigns(data, "12-2nd-avenue", 20);
  assert.equal(a.tried, 63);
  assert.ok(a.reached && a.mix.gain >= 20);
  const out = cheapestCampaigns(data, "12-2nd-avenue", 120);
  assert.equal(out.reached, false, "past 100 no mix reaches");
  assert.ok(out.max.gain <= 100);
});

withPack("its week needs the plan in hand, of this type, in this neighbourhood", () => {
  const plan = giftShop();
  const units = unitsAtEdgeFor(data, plan, CTX, "gift-shop", "hells-kitchen", "gift-cheap");
  assert.ok(units > 0);
  assert.equal(unitsAtEdgeFor(data, plan, CTX, "gift-shop", "midtown", "gift-cheap"), null, "another neighbourhood");
  assert.equal(unitsAtEdgeFor(data, plan, CTX, "florist", "hells-kitchen", "gift-cheap"), null, "another type");
  assert.equal(unitsAtEdgeFor(data, null, CTX, "gift-shop", "hells-kitchen", "gift-cheap"), null, "no plan");
});

// ── the words and the site ─────────────────────────────────────────────────

const asked = (script) => new Set([...script.matchAll(/\bt[f]?\("([^"]+)"/g)].map((m) => m[1]));
const given = (page) => new Set([...page.matchAll(/"([\w.]+)":\s*say\(|^\s*(\w+):\s*say\(/gm)].map((m) => m[1] ?? m[2]));

test("every word the places script draws is a say() string on the page", () => {
  const want = asked(read("lib/ledger/places.ts"));
  for (const u of ["any", "shop", "office", "warehouse", "home", "cinema", "theatre", "special"]) { want.add(`use.${u}`); if (u !== "special") want.add(`things.${u}`); }
  for (const l of ["low", "middling", "high"]) want.add(`level.${l}`);
  for (const c of ["working", "middle", "upper"]) want.add(`class.${c}`);
  want.add("and"); want.add("mix.template"); want.add("mix.none");
  const page = read("pages/ledger/places.astro");
  const have = given(page);
  for (const k of ["use.any", "use.shop", "use.office", "use.warehouse", "use.home", "use.cinema", "use.theatre"]) have.add(k); // built from USE_NAMES
  const missing = [...want].filter((k) => !have.has(k));
  assert.deepEqual(missing, [], "keys the places script asks for that the page does not give");
});

test("every word the drawer draws is a say() string on RecordDrawer", () => {
  const want = asked(read("lib/ledger/drawer.ts"));
  for (const u of ["shop", "office", "warehouse", "home", "cinema", "theatre", "special"]) want.add(`noun.${u}`);
  for (const a of ["a", "an"]) want.add(`article.${a}`);
  const have = given(read("components/ledger/RecordDrawer.astro"));
  assert.deepEqual([...want].filter((k) => !have.has(k)), []);
});

test("every word the calculators draw is a say() string on the page", () => {
  const want = asked(read("lib/ledger/calculators.ts"));
  for (const u of ["shop", "office", "warehouse", "home", "cinema", "theatre", "special"]) want.add(`use.${u}`);
  const page = read("pages/ledger/calculators.astro");
  const have = given(page);
  // the staircase's own words arrive from STAIR_WORDS, each through say()
  for (const k of ["mark.market", "mark.allBuy", "mark.best", "mark.merged", "mark.competitor", "axis", "backorder", "aria"]) have.add(k);
  assert.match(page, /STAIR_WORDS\)\.map\(\(\[k, v\]\) => \[k, say\(/);
  assert.deepEqual([...want].filter((k) => !have.has(k)), []);
});

test("Places and Calculators are public: in the sitemap, not kept out of search, one h1 each", () => {
  const sitemap = read("pages/sitemap.xml.ts");
  for (const p of ["/ledger/places", "/ledger/calculators"]) {
    assert.ok(sitemap.includes(`["${p}",`), `${p} is in the sitemap`);
    const src = read(`pages${p}.astro`);
    assert.ok(!/\bnoindex\b/.test(src.replace(/\/\*[\s\S]*?\*\//g, "")), `${p} is not noindex`);
    assert.equal((src.match(/<h1[\s>]/g) || []).length + (src.match(/<Head\b/g) || []).length, 1);
  }
});

test("the calculators use the pack's campaign and course names, not the handoff's samples", () => {
  for (const p of ["lib/ledger/calculators.ts", "pages/ledger/calculators.astro", "lib/ledger/places.ts", "pages/ledger/places.astro"]) {
    const src = read(p);
    for (const sample of ["Internet · local", "Internet · city", "Billboard · street", "Gift shop, as planned"]) {
      assert.ok(!src.includes(sample), `${p} does not carry the sample "${sample}"`);
    }
  }
});

test("no style of Places, Calculators or the switch is red, green or a new hue", () => {
  for (const p of ["styles/ledger-places.css", "styles/ledger-stream-switch.css"]) {
    const css = read(p);
    assert.ok(!css.includes("--live"), `${p} never uses --live`);
    assert.ok(!/#(?:[0-9a-f]{3}){1,2}\b/i.test(css), `${p} carries no hex`);
    assert.ok(!/\b(?:rgb|hsl)a?\(/i.test(css), `${p} carries no colour function but color-mix`);
  }
});
