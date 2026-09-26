/* The Ledger's reckoning must say what the game would say.
 *
 * The engine (src/lib/ledger/engine.ts) is TypeScript and this file is not:
 * Node strips the types itself (on by default since Node 23.6; this repo runs
 * Node 26), so `node --test test/` loads the .ts module directly, with no build
 * step, as headings-fit does with fit.ts. Only erasable TypeScript is allowed
 * in lib/ledger for that reason: no enums, no namespaces, no parameter properties.
 *
 * ⚠ The data pack is All Rights Reserved and is NEVER committed here. These
 * tests read it from $LEDGER_PACK, else from
 *   ~/Documents/development/shrutisgametracker/research/big-ambitions/ledger.json
 * and when it is absent every test SKIPS with the reason printed, rather than
 * passing on nothing.
 *
 * The calibration is the brief's sample (BRIEF §14, docs/LEDGER.md Contract 2):
 * a gift shop at 12 2nd Avenue, Hell's Kitchen, one register on its cabinet,
 * open 09:00–21:00 every day with one register staffed, Normal, satisfaction
 * 80, demand 80, no campaigns. The brief's week of $73,171 assumed wages of
 * $2,268: a cashier 12 h × 7 d at $20 an hour, and a cleaner 6 h × 7 d at $14.
 * Those wages are not the pack's (customer service is $16 base × Normal's 0.7
 * = $11.20; cleaning $12 × 0.7 = $8.40), so the sample plan states them
 * itself, through the plan's `staff` lines: customer service at $20 (its hours
 * come from the painted registers: 84) and cleaning at 42 h × $14. Goods are
 * bought at the cheapest wholesalers' index, 0.90. The displays are what the
 * brief takes for granted: enough for 30 customers an hour of each product
 * (two rounded shelves each for the gifts, three product panels for umbrellas),
 * and the stack of baskets a gift shop needs to open.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

import {
  reckon, priceStair, cheapestCampaigns, rentOrBuy, rankBuildings, fill,
} from "../src/lib/ledger/engine.ts";

const PACK = process.env.LEDGER_PACK
  || join(homedir(), "Documents/development/shrutisgametracker/research/big-ambitions/ledger.json");
const HAVE = existsSync(PACK);
const SKIP = HAVE ? false : `SKIPPED: the Ledger data pack is not at ${PACK}. Set LEDGER_PACK to its path. It is never committed to this repo.`;
if (!HAVE) console.warn(`\n⚠ ${SKIP}\n`);
const data = HAVE ? JSON.parse(readFileSync(PACK, "utf8")) : null;

const it = (name, fn) => test(name, { skip: SKIP }, fn);

const CTX = { difficulty: "normal", courses: [] };
const open = (n = 1, from = 9, to = 21) =>
  Array.from({ length: 7 }, () => Array.from({ length: 24 }, (_, h) => (h >= from && h < to ? n : 0)));

function sample(over = {}) {
  return {
    typeId: "gift-shop",
    buildingId: "12-2nd-avenue",
    prices: { "gift-cheap": 25.63, "gift-expensive": 45.57, umbrella: 34.18 },
    fixtures: {
      "cash-register": 1, "cabinet-with-drawers": 1, "shopping-baskets": 1,
      "rounded-shelf": 4, "product-panel": 3,
    },
    hours: open(1),
    campaigns: {},
    satisfaction: 80,
    satisfactionTyped: false,
    staff: { "customer-service": { wage: 20 }, cleaning: { hours: 42, wage: 14 } },
    ...over,
  };
}

/** The brief's table of customers expected at 09:00–20:00, before the register's ceiling. */
const BRIEF_WOULD = [
  [18, 18, 18, 27, 27, 27, 27, 27, 19, 19, 8, 8],
  [16, 16, 16, 25, 25, 25, 25, 25, 18, 18, 8, 8],
  [15, 15, 15, 23, 23, 23, 23, 23, 17, 17, 7, 7],
  [16, 16, 16, 25, 25, 25, 25, 25, 18, 18, 8, 8],
  [20, 20, 20, 30, 30, 30, 30, 30, 21, 21, 9, 9],
  [22, 22, 22, 30, 30, 30, 30, 30, 23, 23, 10, 10],
  [21, 21, 21, 30, 30, 30, 30, 30, 22, 22, 10, 10],
];

// ── The sample ───────────────────────────────────────────────────────────

it("the sample gift shop serves 1,459 customers a week, held 47 hours by its one register", () => {
  const r = reckon(data, sample(), CTX);
  assert.equal(r.state, "ok");
  assert.equal(r.customers.value, 1459);
  assert.equal(r.limit.state, "held");
  assert.equal(r.limit.by, "registers");
  assert.equal(r.limit.hours, 47);
  assert.equal(r.limit.cap, 20);
  assert.equal(r.limit.would, 30);
});

it("the customers who would come each hour are the brief's table, read from the start hour", () => {
  const r = reckon(data, sample(), CTX);
  assert.deepEqual(r.would.map((row) => row.slice(9, 21)), BRIEF_WOULD);
});

it("the sample's week is $73,171: money in, goods, wages, rent and deliveries as the brief", () => {
  const w = reckon(data, sample(), CTX).week;
  assert.equal(Math.round(w.moneyIn.value), 93561);
  assert.equal(Math.round(w.goods.value), 15363);
  assert.equal(w.wages.value, 2268);
  assert.equal(w.rent.value, 2359);
  assert.equal(w.deliveries.value, 400);
  assert.equal(w.ads.value, 0);
  assert.ok(Math.abs(w.total.value - 73171) < 1, `the week is ${w.total.value}`);
  assert.equal(w.loss, false);
});

it("the sample sells 1,290, 759 and 759 units at the all-buy edge", () => {
  const r = reckon(data, sample(), CTX);
  assert.deepEqual(r.products.map((p) => [p.id, Math.round(p.units)]),
    [["gift-cheap", 1290], ["gift-expensive", 759], ["umbrella", 759]]);
  for (const p of r.products) assert.equal(p.tread.step, 0);
});

it("a price left blank is the all-buy edge, to the cent: 25.63, 45.57 and 34.18 in Hell's Kitchen", () => {
  const r = reckon(data, sample({ prices: {} }), CTX);
  assert.deepEqual(r.products.map((p) => p.price), [25.63, 45.57, 34.18]);
  assert.ok(Math.abs(r.week.total.value - 73171) < 1);
});

it("a second register costs $1,370 with its cabinet, a cashier $1,680 a week, and is worth $12,844–12,845", () => {
  const { fix, say } = reckon(data, sample(), CTX).limit;
  assert.equal(fix.kind, "register");
  assert.deepEqual(fix.adds, { "cash-register": 1, "cabinet-with-drawers": 1 });
  assert.equal(fix.cost.value, 1370);
  assert.equal(fix.weeklyCost.value, 1680);
  assert.ok(fix.worth.value >= 12844 && fix.worth.value <= 12845.5, `worth ${fix.worth.value}`);
  assert.equal(fill(say.template, say.params),
    "Held at 20 customers an hour by one register, for 47 hours of the week. 30 would come. " +
    "A second register ($1,370 with its cabinet) and a cashier ($1,680 a week) are worth $12,845 a week.");
});

it("applying the fix frees the sample: every customer served, held only by the building", () => {
  const r0 = reckon(data, sample(), CTX);
  const r = reckon(data, r0.limit.fix.plan, CTX);
  assert.equal(r.customers.value, 1730);
  assert.equal(r.limit.by, "building");
  assert.equal(r.limit.fix.worth.value, null);
  assert.ok(Math.abs(r.week.total.value - r0.week.total.value - r0.limit.fix.worth.value) < 1e-6);
});

it("a wage the plan does not give is base × the salary multiplier, and marked approximate", () => {
  const r = reckon(data, sample({ staff: {} }), CTX);
  assert.ok(Math.abs(r.week.wages.value - 84 * 16 * 0.7) < 1e-9);
  assert.equal(r.week.wages.honesty, "approximate");
  assert.ok(r.week.wages.lines.some((l) => l.key === "wages.security-guard.unplanned" && l.value == null));
});

it("the week's lines add up to the week, and costs the Ledger cannot price are marked not counted", () => {
  const t = reckon(data, sample(), CTX).week.total;
  let v = 0;
  for (const l of t.lines) {
    if (l.op === "=" || l.value == null) continue;
    v += l.op === "−" ? -l.value : l.value;
  }
  assert.ok(Math.abs(v - t.value) < 1e-6);
  assert.equal(t.honesty, "approximate");
  const nc = t.lines.filter((l) => l.honesty === "not-counted").map((l) => l.key);
  assert.ok(nc.includes("week.theft") && nc.includes("week.tax"));
});

it("setup is the fixtures plus the $20,220 deposit, and payback divides it by a day's takings", () => {
  const r = reckon(data, sample(), CTX);
  assert.equal(r.setup.fixtures.value, 900 + 470 + 200 + 4 * 1200 + 3 * 500);
  assert.equal(r.setup.deposit.value, 20220);
  assert.equal(r.setup.total.value, r.setup.fixtures.value + 20220);
  assert.ok(Math.abs(r.paybackDays.value - r.setup.total.value / (r.week.total.value / 7)) < 1e-9);
});

// ── Displays and other ceilings ──────────────────────────────────────────

it("one product panel for umbrellas holds them at 10 an hour, and a second panel is the fix", () => {
  const plan = sample({ fixtures: { ...sample().fixtures, "cash-register": 2, "cabinet-with-drawers": 2, "product-panel": 1 }, hours: open(2) });
  const r = reckon(data, plan, CTX);
  assert.equal(r.limit.by, "displays");
  assert.equal(r.limit.productId, "umbrella");
  assert.equal(r.limit.cap, 10);
  assert.equal(r.limit.fix.kind, "display");
  assert.deepEqual(r.limit.fix.adds, { "product-panel": 1 });
  assert.equal(r.limit.fix.cost.value, 500);
  assert.ok(r.limit.fix.worth.value > 0);
});

it("a register bought but not staffed is fixed by staffing it, at no cost", () => {
  const plan = sample({ fixtures: { ...sample().fixtures, "cash-register": 2, "cabinet-with-drawers": 2 } });
  const { fix } = reckon(data, plan, CTX).limit;
  assert.equal(fix.kind, "staff");
  assert.equal(fix.cost.value, 0);
  assert.equal(fix.weeklyCost.value, 1680);
});

// ── States ───────────────────────────────────────────────────────────────

it("a week where nobody buys is a loss, carries the sign, and never pays back", () => {
  const r = reckon(data, sample({ prices: { "gift-cheap": 999, "gift-expensive": 999, umbrella: 999 } }), CTX);
  assert.equal(r.state, "ok");
  assert.equal(r.week.moneyIn.value, 0);
  assert.ok(r.week.total.value < 0);
  assert.equal(r.week.loss, true);
  assert.equal(r.paybackDays.value, null);
  for (const p of r.products) assert.equal(p.tread, null);
});

it("a shop never open costs its rent and wages, and says there is nothing to limit", () => {
  const r = reckon(data, sample({ hours: open(0) }), CTX);
  assert.equal(r.state, "closed");
  assert.equal(r.customers.value, 0);
  assert.equal(r.week.total.value, -2359 - 588);
  assert.equal(r.week.loss, true);
  assert.equal(r.limit.state, "unknown");
  assert.equal(r.limit.reason, "closed");
});

it("a gift shop in an office is not a shop, and the week is not reckoned", () => {
  const office = data.buildings.find((b) => b.use === "office");
  const r = reckon(data, sample({ buildingId: office.id }), CTX);
  assert.equal(r.state, "not-a-shop");
  assert.equal(r.limit.state, "not-a-shop");
  assert.equal(r.week.total.value, null);
  assert.equal(fill(r.limit.say.template, r.limit.say.params),
    "This building is not a shop. A gift shop needs a shop unit; the finder lists them.");
});

it("a gift shop without a register cannot open, and says what it needs", () => {
  const f = { ...sample().fixtures };
  delete f["cash-register"];
  const r = reckon(data, sample({ fixtures: f }), CTX);
  assert.equal(r.state, "cannot-open");
  assert.equal(r.limit.state, "cannot-open");
  assert.ok(r.missing.some((m) => m.path === "fixtures" && m.requirement === "cash-register|checkout-counter"));
  assert.equal(r.week.total.value, null);
  assert.equal(r.served.flat().reduce((a, b) => a + b, 0), 0);
  assert.equal(fill(r.limit.say.template, r.limit.say.params), "Nothing to limit until it can open. It needs a cash register first.");
});

it("a register without its cabinet cannot open either", () => {
  const f = { ...sample().fixtures, "cabinet-with-drawers": 0 };
  const r = reckon(data, sample({ fixtures: f }), CTX);
  assert.equal(r.state, "cannot-open");
  assert.ok(r.missing.some((m) => m.requirement === "cabinet-with-drawers" && m.neededBy === "cash-register"));
});

it("a type whose course is not finished cannot open until it is", () => {
  const plan = sample({ typeId: "liquor-store", products: ["beer"], fixtures: { "cash-register": 1, "cabinet-with-drawers": 1, "shopping-baskets": 1 } });
  const r = reckon(data, plan, CTX);
  assert.ok(r.missing.some((m) => m.path === "type" && m.requirement === "headquarters"));
  const r2 = reckon(data, plan, { ...CTX, courses: ["headquarters"] });
  assert.ok(!r2.missing.some((m) => m.path === "type"));
});

it("with no type or no building nothing is known yet, and every figure is a dash", () => {
  for (const over of [{ typeId: null }, { buildingId: null }]) {
    const r = reckon(data, sample(over), CTX);
    assert.equal(r.limit.state, "unknown");
    assert.equal(r.week.total.value, null);
    assert.equal(r.customers.value, null);
  }
});

it("the same plan reckons the same, every time", () => {
  const a = reckon(data, sample(), CTX);
  const b = reckon(data, JSON.parse(JSON.stringify(sample())), CTX);
  assert.deepEqual(a, b);
  assert.equal(JSON.stringify(a), JSON.stringify(reckon(data, sample(), CTX)));
});

// ── The staircase ────────────────────────────────────────────────────────

it("the staircase has a tread for each class ceiling, shared by the neighbourhood's class mix", () => {
  const s = priceStair(data, "gift-cheap", "garment-district");
  assert.equal(s.steps.length, 3);
  assert.deepEqual(s.steps.map((t) => t.share), [1, 0.3, 0.08]);
  assert.deepEqual(s.steps.map((t) => t.to), [23.11, 25.2, 30.6]); // 18 × 1.284, × 1.40, × 1.70
  assert.deepEqual(s.steps.map((t) => t.buyers), [["working", "middle", "upper"], ["middle", "upper"], ["upper"]]);
  // Hell's Kitchen's index (1.424) is above the middle ceiling, so two treads merge.
  const hk = priceStair(data, "gift-cheap", "hells-kitchen");
  assert.deepEqual(hk.steps.map((t) => [t.to, t.share]), [[25.63, 1], [30.6, 0.12]]);
  assert.equal(hk.markers.allBuy, 25.63);
  assert.equal(hk.best.price, 25.63);
});

it("pricing below the all-buy edge sells no more and earns less", () => {
  const at = reckon(data, sample(), CTX);
  const below = reckon(data, sample({ prices: { ...sample().prices, "gift-cheap": 22 } }), CTX);
  const a = at.products.find((p) => p.id === "gift-cheap"), b = below.products.find((p) => p.id === "gift-cheap");
  assert.equal(b.units, a.units);
  assert.ok(b.moneyIn.value < a.moneyIn.value);
  assert.ok(below.week.total.value < at.week.total.value);
});

it("a monopoly lifts every edge by 0.30, a competitor lowers the reference, a backorder leaves nothing to sell", () => {
  const m = priceStair(data, "gift-cheap", "hells-kitchen", { monopoly: true });
  assert.equal(m.markers.allBuy, 31.03); // 18 × 1.724
  const c = priceStair(data, "gift-cheap", "hells-kitchen", {}, { competitorPrice: 15 });
  assert.equal(c.reference, 15);
  assert.equal(c.markers.competitor, 15);
  assert.equal(c.markers.allBuy, 21.36);
  const bo = priceStair(data, "gift-cheap", "hells-kitchen", { backorder: true }, { unitsAtEdge: 1000 });
  assert.equal(bo.nothingToSell, true);
  assert.equal(bo.best.moneyWeek, 0);
});

// ── Campaigns ────────────────────────────────────────────────────────────

it("the campaign search tries all 63 mixes and picks the cheapest that reaches the target", () => {
  const b = data.buildings.find((x) => x.id === "12-2nd-avenue");
  const hood = data.neighbourhoods.find((n) => n.id === b.neighbourhood);
  const gainOf = (reach) => Math.round(Math.round(Math.min(reach / b.sqm, 1) * 100) * hood.marketingStrength);
  for (const target of [5, 10, 20, 35, 50, 70]) {
    const a = cheapestCampaigns(data, b.id, target);
    assert.equal(a.tried, 63);
    assert.equal(a.reached, true, `target ${target}`);
    assert.ok(a.mix.gain >= target);
    // No cheaper mix reaches it.
    for (let mask = 1; mask < 64; mask++) {
      const cs = data.campaigns.filter((_, i) => mask & (1 << i));
      const cost = cs.reduce((s, c) => s + c.costDay, 0);
      if (gainOf(cs.reduce((s, c) => s + c.reach, 0)) >= target) assert.ok(cost >= a.mix.costDay, `target ${target}: mask ${mask} is cheaper`);
    }
  }
  assert.deepEqual(cheapestCampaigns(data, b.id, 5).mix.campaigns, ["internet-small"]);
});

it("a target no mix reaches reports the most that can be reached, and its cost", () => {
  const a = cheapestCampaigns(data, "12-2nd-avenue", 120);
  assert.equal(a.reached, false);
  assert.equal(a.mix, null);
  assert.equal(a.max.gain, 70); // 100 % reach × Hell's Kitchen's strength 0.7
  assert.equal(a.max.costDay, 2500); // the medium billboard alone covers 225 m²
  assert.deepEqual(a.max.campaigns, ["billboard-medium"]);
});

// ── Rent or buy ──────────────────────────────────────────────────────────

it("rent or buy counts game years of rent against the whole building's price", () => {
  const r = rentOrBuy(data, "12-2nd-avenue", 5);
  assert.equal(r.rentYear.value, 337 * 60);
  assert.equal(r.rentOver.value, 337 * 60 * 5);
  assert.equal(r.price.value, 146520752);
  assert.ok(Math.abs(r.yearsToRepay.value - 146520752 / 20220) < 1e-9);
  assert.equal(r.verdict, "rent");
  assert.equal(r.difference, 146520752 - 101100);
  assert.ok(r.price.lines.some((l) => l.honesty === "not-counted"));
  const buy = rentOrBuy(data, "12-2nd-avenue", 8000);
  assert.equal(buy.verdict, "buy");
  const special = data.buildings.find((b) => b.use === "special");
  assert.equal(rentOrBuy(data, special.id, 5).state, "not-for-rent");
});

// ── Ranking ──────────────────────────────────────────────────────────────

it("ranking reckons all 883 buildings in well under a second and a half, best week first", () => {
  const plan = sample({ satisfaction: 75 }); // a plan nothing has ranked yet: no memo
  const t0 = performance.now();
  const rows = rankBuildings(data, plan, CTX, {});
  const ms = performance.now() - t0;
  assert.equal(rows.length, 883);
  assert.ok(ms < 1500, `a full rank took ${ms.toFixed(0)} ms`);
  const weeks = rows.map((r) => r.week);
  const firstNull = weeks.indexOf(null);
  const ranked = firstNull < 0 ? weeks : weeks.slice(0, firstNull);
  assert.ok(ranked.length === 306, "every shop is ranked and nothing else is");
  for (let i = 1; i < ranked.length; i++) assert.ok(ranked[i - 1] >= ranked[i]);
  assert.ok(weeks.slice(ranked.length).every((w) => w === null));
  assert.equal(rankBuildings(data, plan, CTX, {}), rows, "the second call is the memo");
});

it("ranking filters and sorts by the building's own facts", () => {
  const rows = rankBuildings(data, sample(), CTX, { neighbourhood: "hells-kitchen", use: "shop", capacity: 30, sort: "rent", dir: 1 });
  const byId = new Map(data.buildings.map((b) => [b.id, b]));
  assert.ok(rows.length > 0);
  for (const r of rows) {
    const b = byId.get(r.id);
    assert.equal(b.neighbourhood, "hells-kitchen");
    assert.equal(b.capacity, 30);
  }
  for (let i = 1; i < rows.length; i++) assert.ok(byId.get(rows[i - 1].id).rentDay <= byId.get(rows[i].id).rentDay);
  assert.ok(rows.some((r) => r.id === "12-2nd-avenue"));
});
