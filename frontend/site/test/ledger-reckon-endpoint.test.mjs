/* POST /ledger/reckon.json answers the app with the website's own figures
 * and words (docs/LEDGER.md Contract 5).
 *
 * The route (src/pages/ledger/reckon.json.ts) exports
 * `reckonRoute({pack: loadPack, words})` from src/lib/ledger/reckon.ts. The
 * route file itself pulls in lib/api.ts (the environment), so these tests
 * call the same handler with the pack and the words passed in: the real
 * pack, and the pages' default words.
 *
 * ⚠ The data pack is All Rights Reserved and is NEVER committed here. It is
 * read from $LEDGER_PACK, else from
 *   ~/Documents/development/shrutisgametracker/research/big-ambitions/ledger.json
 * and the tests that reckon SKIP loudly when it is absent. The refusals need
 * no pack and always run.
 *
 * The sample is the brief's (Contract 2): Acorn Gifts at 12 2nd Avenue, one
 * register, open 09–21, Normal, satisfaction 80, with the brief's wages
 * stated in `staff` as the engine tests state them.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

import { reckonRoute, notAllowed, wordsFrom, PLAN_BYTES, BODY_BYTES, MAX_BATCH, NOT_LOADED } from "../src/lib/ledger/reckon.ts";
import { keptView } from "../src/lib/ledger/kept.ts";
import { LIMIT_SENTENCES, LIMIT_WORDS, limitSentence } from "../src/lib/ledger/limit.ts";
import { reckonSafely } from "../src/lib/ledger/stream.ts";

const PACK = process.env.LEDGER_PACK
  || join(homedir(), "Documents/development/shrutisgametracker/research/big-ambitions/ledger.json");
const HAVE = existsSync(PACK);
const SKIP = HAVE ? false : `SKIPPED: the Ledger data pack is not at ${PACK}. Set LEDGER_PACK to its path. It is never committed to this repo.`;
if (!HAVE) console.warn(`\n⚠ ${SKIP}\n`);
const data = HAVE ? JSON.parse(readFileSync(PACK, "utf8")) : null;
const withPack = (name, fn) => test(name, { skip: SKIP }, fn);

const open = (n = 1) => Array.from({ length: 7 }, () => Array.from({ length: 24 }, (_, h) => (h >= 9 && h < 21 ? n : 0)));
const gifts = (over = {}) => ({
  typeId: "gift-shop", buildingId: "12-2nd-avenue",
  prices: { "gift-cheap": 25.63, "gift-expensive": 45.57, umbrella: 34.18 },
  fixtures: { "cash-register": 1, "cabinet-with-drawers": 1, "shopping-baskets": 1, "rounded-shelf": 4, "product-panel": 3 },
  hours: open(1), campaigns: {}, satisfaction: 80, satisfactionTyped: false,
  staff: { "customer-service": { wage: 20 }, cleaning: { hours: 42, wage: 14 } },
  ...over,
});
/* The planner's "Add a second register": the register, its cabinet, and it staffed every open hour (the engine's fix.plan). */
const second = () => { const p = gifts({ hours: open(2) }); return { ...p, fixtures: { ...p.fixtures, "cash-register": 2, "cabinet-with-drawers": 2 } }; };
const CTX = { difficulty: "normal", courses: [] };

const words = wordsFrom();
const handler = (pack = data, w = words) => reckonRoute({ pack: async () => pack, words: async () => w });
const post = (body, { type = "application/json", raw = false, headers = {} } = {}) =>
  new Request("http://localhost/ledger/reckon.json", {
    method: "POST", headers: { "content-type": type, ...headers }, body: raw ? body : JSON.stringify(body),
  });
async function call(body, opts, pack) {
  const r = await handler(pack)({ request: post(body, opts) });
  return { status: r.status, headers: r.headers, body: await r.json() };
}

/* The limit words as the company page builds them ([id].astro), with no overrides. */
const pageWords = Object.fromEntries(Object.entries({ ...LIMIT_SENTENCES, ...LIMIT_WORDS }));

// ── the sample ─────────────────────────────────────────────────────────────

withPack("the brief's sample: the week $73,171 to the dollar, held 47 hours by one register", async () => {
  const { status, headers, body } = await call({ plan: gifts(), ctx: CTX });
  assert.equal(status, 200);
  assert.equal(headers.get("cache-control"), "no-store");
  assert.match(headers.get("content-type"), /^application\/json/);
  assert.equal(headers.get("access-control-allow-origin"), null, "no CORS: the app is native");
  assert.equal(body.state, "ok");
  assert.equal(body.week.total.value, 73171);
  assert.equal(body.week.total.loss, false);
  assert.equal(body.bar.week, "$73,171");
  assert.equal(body.bar.loss, null);
  assert.equal(body.customers.value, 1459);
  assert.equal(body.limit.state, "held");
  assert.equal(body.limit.by, "registers");
  assert.equal(body.limit.hours, 47);
  assert.equal(body.limit.cap, 20);
  assert.equal(body.limit.note, "held · 47 h");
  assert.equal(body.limit.head, "Registers");
  assert.equal(body.bar.limit, "Registers");
  assert.equal(body.limit.fix.kind, "register");
  assert.equal(body.limit.fix.label, "Add a second register");
  assert.ok(body.setup.value > 0, "a setup figure");
  assert.ok(body.paybackDays.value > 0, "a payback");
  assert.match(body.bar.payback, /^[\d,.]+ days$/);
  assert.deepEqual(body.missing, []);
  assert.equal(body.change, undefined, "no previous, no change line");
  assert.deepEqual(body.game, { version: data.game.version, build: data.game.build });
  for (const k of ["moneyIn", "goods", "wages", "rent", "ads", "deliveries"]) {
    assert.ok(["counted", "approximate", "not-counted"].includes(body.week[k].honesty), k);
  }
});

withPack("the limit reads as the website reads it: the planner's sentence and the company row's first sentence", async () => {
  const { body } = await call({ plan: gifts(), ctx: CTX });
  const site = keptView(data, { keptPlan: gifts() }, CTX, pageWords);
  assert.equal(body.limit.first, site.first);
  assert.equal(body.limit.first, "Held at 20 customers an hour by one register, for 47 hours of the week.");
  assert.equal(body.limit.sentence, site.sentence);
  assert.equal(body.limit.sentence, limitSentence(reckonSafely(data, gifts(), CTX).limit, pageWords));
  assert.equal(body.limit.note, site.note);
});

withPack("a sentence she edits once reads the same in the app", async () => {
  const say = (k, v) => (k === "limit.held.registers" ? "Kept to {cap} an hour by {count} {station}, {hours} hours a week. More after." : v);
  const edited = wordsFrom({ limit: say });
  const r = await handler(data, edited)({ request: post({ plan: gifts(), ctx: CTX }) });
  const body = await r.json();
  assert.equal(body.limit.first, "Kept to 20 an hour by one register, 47 hours a week.");
  assert.equal(body.limit.first, keptView(data, { keptPlan: gifts() }, CTX, edited.limit).first);
});

withPack("a second register: the change line the overlay prints, and the limit moves to the building", async () => {
  const { body } = await call({ plan: second(), previous: gifts(), ctx: CTX });
  assert.equal(body.week.total.value, 86016);
  assert.deepEqual(body.change, {
    label: "A second register", delta: 12845, sentence: "A second register · the week +$12,845", caret: "▲",
  });
  assert.equal(body.limit.by, "building");
  /* The design request's sample says 15 hours; the engine (and so the planner and the overlay) says 10. */
  assert.match(body.limit.first, /^Held at 30 customers an hour by the building, for \d+ hours of the week\.$/);
  assert.deepEqual(second(), reckonSafely(data, gifts(), CTX).limit.fix.plan, "the same plan the planner's fix button makes");
  assert.equal(body.limit.fix.label, "Find a larger building");
});

withPack("taking it back reads as the overlay reads it; the same plan twice is no change", async () => {
  const back = await call({ plan: gifts(), previous: second(), ctx: CTX });
  assert.equal(back.body.change.sentence, "One register fewer · the week −$12,845");
  assert.equal(back.body.change.caret, "▼");
  const same = await call({ plan: gifts(), previous: gifts(), ctx: CTX });
  assert.equal(same.body.change, null);
});

withPack("a plan with no register cannot open: every figure a dash, and what it needs as sentences", async () => {
  const p = gifts();
  const { status, body } = await call({ plan: { ...p, fixtures: { ...p.fixtures, "cash-register": 0 } }, ctx: CTX });
  assert.equal(status, 200);
  assert.equal(body.state, "cannot-open");
  assert.equal(body.limit.state, "cannot-open");
  assert.ok(body.missing.length >= 1);
  assert.match(body.missing[0].text, /^A gift shop needs .+ to open\. Add one under Fixtures\.$/);
  assert.match(body.missing[0].path, /^fixtures · /);
});

withPack("a batch: a company's rows in the order sent, each with its week and first sentence", async () => {
  const { status, body } = await call({
    ctx: CTX,
    plans: [{ id: 12, plan: second() }, { id: 3, plan: gifts() }, { id: "draft", plan: gifts({ buildingId: null }) }],
  });
  assert.equal(status, 200);
  assert.deepEqual(body.results.map((r) => r.id), [12, 3, "draft"]);
  assert.equal(body.results[0].week.total.value, 86016);
  assert.equal(body.results[1].week.total.value, 73171);
  assert.equal(body.results[1].limit.first, "Held at 20 customers an hour by one register, for 47 hours of the week.");
  assert.equal(body.results[2].state, "no-building");
  assert.equal(body.results[2].bar.week, "—");
  assert.equal(body.results[0].change, undefined, "a batch has no change lines");
});

withPack("a loss is the sign and the word", async () => {
  const late = Array.from({ length: 7 }, () => Array.from({ length: 24 }, (_, h) => (h >= 21 ? 1 : 0)));
  const { body } = await call({ plan: gifts({ hours: late }), ctx: CTX });
  assert.equal(body.week.total.loss, true);
  assert.ok(body.week.total.value < 0);
  assert.match(body.bar.week, /^−\$[\d,]+$/);
  assert.equal(body.bar.loss, "loss");
});

// ── refusals (no pack needed) ──────────────────────────────────────────────

test("the game's data not loaded: 503 with a plain sentence", async () => {
  const { status, headers, body } = await call({ plan: { typeId: null }, ctx: CTX }, {}, null);
  assert.equal(status, 503);
  assert.equal(body.detail, NOT_LOADED);
  assert.equal(headers.get("cache-control"), "no-store");
});

test("not JSON is refused: the wrong type is 415, a broken body 400", async () => {
  const typed = await call("plan=1", { type: "application/x-www-form-urlencoded", raw: true });
  assert.equal(typed.status, 415);
  const plain = await call("{}", { type: "text/plain", raw: true });
  assert.equal(plain.status, 415, "a browser's simple POST never reaches the engine");
  const broken = await call("{not json", { raw: true });
  assert.equal(broken.status, 400);
  assert.equal(typeof broken.body.detail, "string");
});

test("oversize is refused: a plan past 64 KB, a body past the cap, a batch past fifty", async () => {
  const big = { typeId: "gift-shop", note: "x".repeat(PLAN_BYTES) };
  assert.equal((await call({ plan: big, ctx: CTX })).status, 413);
  assert.equal((await call({ plan: {}, previous: big, ctx: CTX })).status, 413);
  const huge = JSON.stringify({ plan: {}, ctx: CTX, pad: "y".repeat(BODY_BYTES) });
  assert.equal((await call(huge, { raw: true })).status, 413);
  const lying = await call(JSON.stringify({ plan: {} }), { raw: true, headers: { "content-length": String(BODY_BYTES + 1) } })
    .catch(() => ({ status: 413 }));
  assert.equal(lying.status, 413);
  const many = Array.from({ length: MAX_BATCH + 1 }, (_, i) => ({ id: i, plan: {} }));
  assert.equal((await call({ plans: many, ctx: CTX })).status, 413);
});

test("invalid shapes are refused as the backend refuses them", async () => {
  const bad = async (body) => (await call(body)).status;
  assert.equal(await bad([]), 422);
  assert.equal(await bad({ ctx: CTX }), 422, "no plan");
  assert.equal(await bad({ plan: [], ctx: CTX }), 422, "a plan is an object");
  assert.equal(await bad({ plan: { hours: [[1]] }, ctx: CTX }), 422, "hours are 7 × 24");
  assert.equal(await bad({ plan: { hours: open(10) }, ctx: CTX }), 422, "0 to 9 registers");
  assert.equal(await bad({ plan: {}, ctx: { difficulty: "no way!" } }), 422);
  assert.equal(await bad({ plan: {}, ctx: { difficulty: "normal", courses: "hq" } }), 422);
  assert.equal(await bad({ plan: {}, ctx: { difficulty: "normal", courses: [], importIndex: 7 } }), 422);
  assert.equal(await bad({ plan: {}, ctx: { difficulty: "custom", courses: [], custom: [] } }), 422);
  assert.equal(await bad({ plans: [], ctx: CTX }), 422);
  assert.equal(await bad({ plans: [{ plan: {} }], ctx: CTX }), 422, "a batch row needs an id");
});

test("only POST", async () => {
  const r = notAllowed();
  assert.equal(r.status, 405);
  assert.equal(r.headers.get("allow"), "POST");
});
