/* The planner's Plan on stream switch (overlays handoff A4–A5): its states,
 * its notes, the debounce and the body of each PUT (lib/ledger/stream-switch.ts).
 * The change sentences themselves are stream.ts's (test/ledger-stream.test.mjs).
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { tap, noteFor, face, isMinted, planKey, liveBody, debounce, DEBOUNCE_MS } from "../src/lib/ledger/stream-switch.ts";
import { reckon } from "../src/lib/ledger/engine.ts";

const PACK = process.env.LEDGER_PACK
  || join(homedir(), "Documents/development/shrutisgametracker/research/big-ambitions/ledger.json");
const HAVE = existsSync(PACK);
const SKIP = HAVE ? false : `SKIPPED: the Ledger data pack is not at ${PACK}.`;
const data = HAVE ? JSON.parse(readFileSync(PACK, "utf8")) : null;
const withPack = (name, fn) => test(name, { skip: SKIP }, fn);
const SRC = fileURLToPath(new URL("../src/", import.meta.url));
const read = (p) => readFileSync(join(SRC, p), "utf8");

// ── states and notes ──────────────────────────────────────────────────────

test("a tap: off goes on and puts, on goes off and deletes", () => {
  assert.deepEqual(tap("off", false), { state: "on", asked: false, effect: "put" });
  assert.deepEqual(tap("on", false), { state: "off", asked: false, effect: "delete" });
});

test("a tap on a switch that cannot stream opens its note, and a second closes it; it never streams", () => {
  for (const s of ["signed-out", "nothing-minted", "no-ledger"]) {
    const once = tap(s, false);
    assert.deepEqual(once, { state: s, asked: true, effect: null });
    assert.deepEqual(tap(s, true), { state: s, asked: false, effect: null });
  }
  assert.deepEqual(tap("checking", false), { state: "checking", asked: true, effect: null }, "a tap while the overlays are asked for waits");
});

test("which note the switch shows, per state", () => {
  assert.equal(noteFor("signed-out", true), "signed-out");
  assert.equal(noteFor("nothing-minted", true), "nothing-minted");
  assert.equal(noteFor("no-ledger", true), "no-ledger");
  for (const s of ["signed-out", "nothing-minted", "no-ledger"]) assert.equal(noteFor(s, false), null, "only after a tap");
  for (const s of ["off", "on", "checking"]) assert.equal(noteFor(s, true), null, `${s} has no note`);
});

test("what the switch reads: A5's two lines for every state", () => {
  assert.deepEqual(face("off"), { on: false, label: "label.off", sub: "sub.off" });
  assert.deepEqual(face("checking"), { on: false, label: "label.off", sub: "sub.off" });
  assert.deepEqual(face("on"), { on: true, label: "label.on", sub: "sub.on" });
  assert.deepEqual(face("nothing-minted"), { on: false, label: "label.off", sub: "sub.noMint" });
  assert.deepEqual(face("signed-out"), { on: false, label: "label.off", sub: "sub.signedOut" });
  assert.deepEqual(face("no-ledger"), { on: false, label: "label.off", sub: "sub.noLedger" });
});

test("minted means a plan-on-stream overlay: the plate's kinds do not count", () => {
  assert.equal(isMinted([]), false);
  assert.equal(isMinted([{ kind: "ledger-plate" }, { kind: "ledger-strip" }]), false);
  assert.equal(isMinted([{ kind: "ledger-plate" }, { kind: "ledger-plan-card" }]), true);
  assert.equal(isMinted([{ kind: "ledger-plan-panel" }]), true);
  assert.equal(isMinted({ detail: "no such ledger" }), false);
});

test("the switch's words are A5's, each through say()", () => {
  const src = read("components/ledger/StreamSwitch.astro");
  for (const [k, v] of [
    ["label.off", "Plan on stream"], ["label.on", "On stream"], ["sub.off", "off · chat sees nothing"], ["sub.on", "chat sees this plan"],
    ["sub.noMint", "no overlay minted yet"], ["sub.signedOut", "needs an account"], ["chat.eyebrow", "Chat sees"],
    ["chat.none", "Chat sees the figures above as they are now."], ["note.mint", "This ledger on stream"], ["note.notNow", "Not now"],
    ["note.signIn", "Sign in"],
  ]) assert.ok(src.includes(`say("${k}", "${v}")`), `${k} reads "${v}"`);
  assert.ok(src.includes('"No plan-on-stream overlay is minted for {ledger} yet, so chat has nothing to see this plan on."'));
  assert.ok(src.includes('"Streaming a plan needs an account: an overlay belongs to one, and this plan is not kept anywhere yet."'));
  assert.match(src, /role="switch"/);
  const script = read("lib/ledger/stream-switch.ts");
  const asked = new Set([...script.matchAll(/\bt\("([^"]+)"/g)].map((m) => m[1]));
  for (const s of ["off", "on", "checking", "signed-out", "no-ledger", "nothing-minted"]) { asked.add(face(s).label); asked.add(face(s).sub); }
  const given = new Set([...src.matchAll(/"([\w.]+)":\s*say\(/g)].map((m) => m[1]));
  assert.deepEqual([...asked].filter((k) => !given.has(k)), [], "keys the switch asks for that the component does not give");
});

test("the planner mounts the switch before its first ledger:plan, and never red", () => {
  const page = read("pages/ledger/plan.astro");
  assert.ok(page.indexOf("mountStreamSwitch(box, root)") < page.indexOf("mountPlanner(root)"));
  assert.match(page, /<StreamSwitch /);
  const css = read("styles/ledger-stream-switch.css");
  assert.ok(!css.includes("--live") && !css.includes("--rose"), "the switch is accent, never red");
  assert.match(css, /min-height: calc\(52px \+ env\(safe-area-inset-bottom\)\)/, "the bottom bar is 52px plus the safe area");
  assert.match(css, /@media \(max-width: 899px\)/, "narrow below 900");
});

// ── the debounce ──────────────────────────────────────────────────────────

function clock() {
  let now = 0, id = 0;
  const due = new Map();
  return {
    timers: { set: (f, ms) => { due.set(++id, { at: now + ms, f }); return id; }, clear: (h) => { due.delete(h); } },
    advance(ms) {
      now += ms;
      for (const [h, t] of [...due].sort((a, b) => a[1].at - b[1].at)) if (t.at <= now) { due.delete(h); t.f(); }
    },
  };
}

test("a burst of changes sends once, a moment after the last", () => {
  const c = clock();
  let sent = 0;
  const d = debounce(() => { sent++; }, DEBOUNCE_MS, c.timers);
  d.call(); c.advance(100); d.call(); c.advance(100); d.call();
  assert.equal(sent, 0);
  c.advance(DEBOUNCE_MS - 1);
  assert.equal(sent, 0, "not before the moment has passed");
  c.advance(1);
  assert.equal(sent, 1);
  c.advance(10_000);
  assert.equal(sent, 1, "and only once");
  assert.ok(DEBOUNCE_MS >= 200 && DEBOUNCE_MS <= 500, "about 300 ms");
});

test("cancel drops a pending send (the switch went off); flush sends it now", () => {
  const c = clock();
  let sent = 0;
  const d = debounce(() => { sent++; }, DEBOUNCE_MS, c.timers);
  d.call(); d.cancel(); c.advance(1000);
  assert.equal(sent, 0);
  d.call(); assert.equal(d.pending, true); d.flush();
  assert.equal(sent, 1); assert.equal(d.pending, false);
});

// ── the body of each PUT ──────────────────────────────────────────────────

const HOURS = () => Array.from({ length: 7 }, () => Array.from({ length: 24 }, (_, h) => (h >= 9 && h < 21 ? 1 : 0)));
const sample = () => ({
  typeId: "gift-shop", buildingId: "12-2nd-avenue", prices: {}, campaigns: {}, satisfaction: 80, satisfactionTyped: false,
  fixtures: { "cash-register": 1, "cabinet-with-drawers": 1, "shopping-baskets": 1, "rounded-shelf": 4, "product-panel": 3 },
  hours: HOURS(), staff: { "customer-service": { wage: 20 }, cleaning: { hours: 42, wage: 14 } },
});
const CTX = { difficulty: "normal", courses: [] };
const next = (key, plan) => { const r = reckon(data, plan, CTX); return { key, plan, week: r.week.total.value, reckoning: r }; };

test("the plan's key: a kept business, or the draft", () => {
  assert.equal(planKey(null), "draft");
  assert.equal(planKey(12), "business:12");
});

withPack("the first send carries the plan and no change line", () => {
  const body = liveBody(data, null, next("draft", sample()), "");
  assert.deepEqual(Object.keys(body).sort(), ["name", "plan"]);
});

withPack("a change carries the A2 sentence and the week's delta against the plan last sent", () => {
  const a = next("business:7", sample());
  const sent = { key: a.key, plan: a.plan, week: a.week };
  const plan = sample();
  plan.fixtures["cash-register"] = 2; plan.fixtures["cabinet-with-drawers"] = 2;
  plan.hours = plan.hours.map((row) => row.map((v) => (v ? 2 : 0)));
  const b = next("business:7", plan);
  const body = liveBody(data, sent, b, "Acorn Gifts");
  assert.equal(body.name, "Acorn Gifts");
  assert.equal(body.change.label, "A second register");
  assert.equal(body.change.delta, Math.round(b.week - a.week));
  assert.ok(body.change.delta !== 0);
});

withPack("the same plan again sends nothing; a different plan sends without a change", () => {
  const a = next("draft", sample());
  const sent = { key: a.key, plan: a.plan, week: a.week };
  assert.equal(liveBody(data, sent, next("draft", sample()), ""), null);
  assert.ok(liveBody(data, sent, next("draft", sample()), "", true), "forced (turning on again) it sends");
  const other = liveBody(data, sent, next("business:3", { ...sample(), satisfaction: 60 }), "Acorn Gifts");
  assert.ok(other && !("change" in other), "another plan: the overlay redraws with no change line");
});

withPack("a delta is null when either week is a dash", () => {
  const noBuilding = { ...sample(), buildingId: null };
  const a = next("draft", noBuilding);
  const body = liveBody(data, { key: "draft", plan: a.plan, week: null }, next("draft", sample()), "");
  assert.equal(body.change.label, "Building 12 2nd Avenue");
  assert.equal(body.change.delta, null);
});
