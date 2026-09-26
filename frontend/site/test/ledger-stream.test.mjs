/* The Ledger on stream says what the design says, from the ledger's own facts.
 *
 * src/lib/ledger/stream.ts is the overlays' words and choices without a DOM
 * (design_handoff_ledger_overlays README §2–§4, A1–A3). The helpers that need
 * no game data always run; those that reckon a plan read the data pack as
 * ledger-engine.test.mjs does, and SKIP with the reason when it is absent.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

import {
  plateRows, plateMeasure, weekLabel, weekWritten, onScreenMoved, changeLine, changeLabel, streamLimit,
  planView, dataLine, reckonSafely,
} from "../src/lib/ledger/stream.ts";

const PACK = process.env.LEDGER_PACK
  || join(homedir(), "Documents/development/shrutisgametracker/research/big-ambitions/ledger.json");
const HAVE = existsSync(PACK);
const SKIP = HAVE ? false : `SKIPPED: the Ledger data pack is not at ${PACK}. Set LEDGER_PACK to its path.`;
const data = HAVE ? JSON.parse(readFileSync(PACK, "utf8")) : null;
const withPack = (name, fn) => test(name, { skip: SKIP }, fn);

// The brief's sample (§11): four open, then eight more for the crowded plate.
const NAMES = ["Acorn Gifts", "Acorn Coffee", "Acorn Flowers", "Acorn Burgers", "Acorn Books", "Acorn Liquor",
  "Acorn Jewels", "Acorn Electronics", "Acorn Gym", "Acorn Cuts", "Acorn Night", "Acorn Office"];
const TOTALS = [72880, 21040, 9480, -1820, 6120, 11300, 18450, 24900, 3880, 2410, 15760, 4200];
const twelve = NAMES.map((name, i) => ({ id: i + 1, name, neighbourhood: "", week: 6, total: TOTALS[i] }));

test("with twelve open, the plate shows the first four in the ledger's order and the one on screen", () => {
  const night = twelve.find((b) => b.name === "Acorn Night");
  const { shown, more } = plateRows(twelve, night.id);
  assert.deepEqual(shown.map((b) => b.name), ["Acorn Gifts", "Acorn Coffee", "Acorn Flowers", "Acorn Burgers", "Acorn Night"]);
  assert.equal(more, 7, "and 7 more open, in the ledger's order");
});

test("when the one on screen is already among the first four, the fifth in order fills the last row", () => {
  const { shown, more } = plateRows(twelve, 2);
  assert.deepEqual(shown.map((b) => b.name), ["Acorn Gifts", "Acorn Coffee", "Acorn Flowers", "Acorn Burgers", "Acorn Books"]);
  assert.equal(more, 7);
});

test("the plate never chooses by money: the biggest week off the first four stays off", () => {
  const { shown } = plateRows(twelve, 1);
  assert.ok(!shown.some((b) => b.name === "Acorn Electronics"), "a $24,900 week jumped the ledger's order");
});

test("five or fewer are all shown, with nothing said about the rest", () => {
  assert.deepEqual(plateRows(twelve.slice(0, 5), 5), { shown: twelve.slice(0, 5), more: 0 });
});

test("a crowded plate and a long company name tighten the rows and the limit", () => {
  assert.deepEqual(plateMeasure("Acorn Holdings", 4), { long: false, crowded: false, rowH: 92, clamp: 3, nameSize: 64 });
  assert.equal(plateMeasure("Acorn Holdings and the Northeast Retail Trust", 4).rowH, 80);
  assert.equal(plateMeasure("Acorn Holdings and the Northeast Retail Trust", 4).nameSize, 48);
  assert.deepEqual(plateMeasure("Acorn Holdings", 12).rowH, 72);
  assert.equal(plateMeasure("Acorn Holdings", 12).clamp, 2);
});

test("the week label says a loss in words, and no week is a dash, never $0", () => {
  assert.equal(weekLabel({ n: 6, total: 101580 }), "Week 6 · the company");
  assert.equal(weekLabel({ n: 2, total: -1620 }), "Week 2 · the company, a loss");
  assert.equal(weekLabel(null), "No week written yet · the company");
});

test("the data line is the version and build, written for chat", () => {
  assert.equal(dataLine({ version: "1.0", build: "3682" }), "1.0 · build 3682 · written for chat");
  assert.equal(dataLine({ version: "1.0", build: "3682" }, true), "1.0 · build 3682 · a plan, not yet open");
  assert.equal(dataLine(null), "");
});

test("a week written is said once, with its number; a first paint says nothing", () => {
  const before = { businesses: [{ id: 1, week: 6, total: 72880 }, { id: 2, week: 6, total: 21040 }] };
  const after = { businesses: [{ id: 1, week: 7, total: 74310 }, { id: 2, week: 6, total: 21040 }] };
  assert.equal(weekWritten(before, after), 7);
  assert.equal(weekWritten(after, after), null);
  assert.equal(weekWritten(null, after), null);
  const rewritten = { businesses: [{ id: 1, week: 7, total: 74000 }, { id: 2, week: 6, total: 21040 }] };
  assert.equal(weekWritten(after, rewritten), 7);
});

test("the business on screen moving names the new one; staying put says nothing", () => {
  const a = { onScreen: 1, businesses: [{ id: 1, name: "Acorn Gifts" }, { id: 2, name: "Acorn Coffee" }] };
  assert.equal(onScreenMoved(a, { ...a, onScreen: 2 }), "Acorn Coffee");
  assert.equal(onScreenMoved(a, a), null);
  assert.equal(onScreenMoved(null, a), null);
});

test("the change line reads better and worse the same way, with a caret in type", () => {
  assert.deepEqual(changeLine({ label: "A second register", delta: 12845 }),
    { text: "A second register · the week +$12,845", caret: "▲" });
  assert.deepEqual(changeLine({ label: "Price of gift (cheap) $30.00", delta: -4210 }),
    { text: "Price of gift (cheap) $30.00 · the week −$4,210", caret: "▼" });
  assert.deepEqual(changeLine({ label: "Hours repainted", delta: 0.3 }), { text: "Hours repainted · the week unchanged", caret: "" });
  assert.equal(changeLine(null), null);
});

// ── with the pack: A2's sentences from the pack's own names ────────────────

const open = (n = 1) => Array.from({ length: 7 }, () => Array.from({ length: 24 }, (_, h) => (h >= 9 && h < 21 ? n : 0)));
const gifts = (over = {}) => ({
  typeId: "gift-shop", buildingId: "12-2nd-avenue",
  prices: { "gift-cheap": 25.63, "gift-expensive": 45.57, umbrella: 34.18 },
  fixtures: { "cash-register": 1, "cabinet-with-drawers": 1, "shopping-baskets": 1, "rounded-shelf": 4, "product-panel": 3 },
  hours: open(1), campaigns: {}, satisfaction: 80, satisfactionTyped: false,
  staff: { "customer-service": { wage: 20 }, cleaning: { hours: 42, wage: 14 } },
  ...over,
});
const CTX = { difficulty: "normal", courses: [], custom: null };

withPack("A2's change sentences come from the diff, in the pack's own names", () => {
  const b = gifts();
  const add = (id, n = 1) => ({ ...b, fixtures: { ...b.fixtures, [id]: (b.fixtures[id] ?? 0) + n } });
  assert.equal(changeLabel(data, b, add("cash-register")), "A second register");
  assert.equal(changeLabel(data, add("cash-register"), b), "One register fewer");
  assert.equal(changeLabel(data, b, add("rounded-shelf")), "One more rounded shelf");
  assert.equal(changeLabel(data, b, add("rounded-shelf", -1)), "One rounded shelf fewer");
  assert.equal(changeLabel(data, b, add("classic-loudspeaker-small")), "A speaker");
  assert.equal(changeLabel(data, add("classic-loudspeaker-small"), b), "No speaker");
  assert.equal(changeLabel(data, b, { ...b, prices: { ...b.prices, "gift-cheap": 30 } }), "Price of gift (cheap) $30.00");
  assert.equal(changeLabel(data, b, { ...b, campaigns: { "internet-small": true } }), "Small internet campaign on");
  assert.equal(changeLabel(data, { ...b, campaigns: { "internet-small": true } }, b), "Small internet campaign off");
  assert.equal(changeLabel(data, b, { ...b, satisfaction: 85 }), "Satisfaction 85 %");
  assert.equal(changeLabel(data, b, { ...b, buildingId: null }), "No building");
  assert.equal(changeLabel(data, { ...b, buildingId: null }, b), "Building 12 2nd Avenue");
  assert.equal(changeLabel(data, b, { ...b, typeId: "coffee-shop" }), "Type coffee shop");
  assert.equal(changeLabel(data, b, { ...b, hours: open(2) }), "Hours repainted");
});

withPack("the sample plan on stream is the planner's: $73,171, held by one register for 47 hours", () => {
  const v = planView(data, gifts(), "Acorn Gifts", CTX);
  assert.equal(v.title, "Gift shop · Acorn Gifts");
  assert.equal(v.where, "12 2nd Avenue · Hell's Kitchen · 30 an hour");
  assert.equal(v.week, "$73,171");
  assert.equal(v.loss, false);
  assert.match(v.limit, /^Held at 20 customers an hour by one register, for 47 hours of the week\./);
  assert.equal(v.grid.length, 7);
  assert.equal(v.grid[0].length, 24);
  assert.equal(v.grid[0][3].open, false, "03:00 is closed");
  assert.ok(v.grid.flat().some((c) => c.held), "no hour is marked held");
});

withPack("with no building every figure is a dash and the limit is not known yet", () => {
  const v = planView(data, gifts({ buildingId: null }), "", CTX);
  assert.equal(v.where, "No building chosen yet");
  assert.equal(v.week, "—");
  assert.equal(v.setup, "—");
  assert.equal(v.payback, "—");
  assert.equal(v.grid, null);
  assert.equal(v.limit, "Not known yet. Choose a building and the Ledger works out what holds this business back.");
});

withPack("a plan without a register cannot open yet, and says what it needs", () => {
  const b = gifts();
  const v = planView(data, { ...b, fixtures: { ...b.fixtures, "cash-register": 0 } }, "", CTX);
  assert.equal(v.week, "—");
  assert.match(v.limit, /^It cannot open yet\. It needs a .+ first\.$/);
});

withPack("a shop open only at night is free and in loss: the sign and the word, and no payback", () => {
  const late = Array.from({ length: 7 }, () => Array.from({ length: 24 }, (_, h) => (h >= 21 ? 1 : 0)));
  const r = reckonSafely(data, gifts({ hours: late }), CTX);
  assert.equal(r.limit.state, "free");
  assert.equal(streamLimit(r.limit), "Nothing binds. Every customer who would come is served, every open hour.");
  const v = planView(data, gifts({ hours: late }), "a second try", CTX);
  assert.equal(v.loss, true);
  assert.match(v.week, /^−\$[\d,]+$/);
  assert.equal(v.payback, "—");
});
