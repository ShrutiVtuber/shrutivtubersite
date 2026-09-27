/* The tap pad's whole-hand gestures (src/lib/carnatic/gestures.ts): two fingers
 * together are a clap, one finger a finger count, a sideways swipe a wave; the
 * time is always when the first finger touched; a wrong gesture is named
 * neutrally; silent counts are never scored; claps only takes any tap. */
import { test } from "node:test";
import assert from "node:assert/strict";
import { GestureReader, judge, rateMs, KEYS, CLAP_WINDOW_MS } from "../src/lib/carnatic/gestures.ts";

test("two fingers landing together are one clap, timed at the first", () => {
  const g = new GestureReader();
  assert.equal(g.pointerDown(1, 100, 100, 1000), null);
  assert.deepEqual(g.pointerDown(2, 160, 100, 1000 + CLAP_WINDOW_MS - 20), { kind: "clap", at: 1000 });
  assert.equal(g.pointerUp(1, 100, 100, 1100), null);
  assert.equal(g.pointerUp(2, 160, 100, 1110), null);
});

test("one finger down and up is a finger count", () => {
  const g = new GestureReader();
  g.pointerDown(1, 100, 100, 2000);
  assert.deepEqual(g.pointerUp(1, 102, 101, 2060), { kind: "finger", at: 2000 });
});

test("a sideways swipe is a wave; a downward drag is not", () => {
  const g = new GestureReader();
  g.pointerDown(1, 100, 100, 3000);
  assert.deepEqual(g.pointerMove(1, 150, 104), { kind: "wave", at: 3000 });
  const h = new GestureReader();
  h.pointerDown(1, 100, 100, 4000);
  assert.equal(h.pointerMove(1, 104, 160), null);
  assert.deepEqual(h.pointerUp(1, 104, 160, 4080), { kind: "finger", at: 4000 });
});

test("a second finger long after the first starts a new gesture", () => {
  const g = new GestureReader();
  g.pointerDown(1, 100, 100, 5000);
  assert.deepEqual(g.pointerUp(1, 100, 100, 5050), { kind: "finger", at: 5000 });
  assert.equal(g.pointerDown(2, 100, 100, 5600), null);
  assert.deepEqual(g.pointerUp(2, 100, 100, 5650), { kind: "finger", at: 5600 });
});

test("a mouse press is a clap straight away", () => {
  assert.deepEqual(new GestureReader().pointerDown(1, 0, 0, 7000, "mouse"), { kind: "clap", at: 7000 });
});

test("keys: Space clap, F finger, W wave", () => {
  assert.equal(KEYS.Space, "clap");
  assert.equal(KEYS.KeyF, "finger");
  assert.equal(KEYS.KeyW, "wave");
});

test("scored by type and time", () => {
  assert.equal(rateMs(29), "perfect");
  assert.equal(rateMs(-79), "onTime");
  assert.equal(rateMs(-81), "early");
  assert.equal(rateMs(120), "late");
  assert.deepEqual(judge("wave", { kind: "wave" }, false), { ok: true, note: "" });
  assert.deepEqual(judge("clap", { kind: "wave" }, false), { ok: false, note: "That count is a wave." });
  assert.deepEqual(judge("finger", { kind: "clap" }, false), { ok: false, note: "That count is a clap." });
  assert.equal(judge("clap", { kind: "silent" }, false).ok, false);
  assert.match(judge("clap", { kind: "silent" }, true).note, /silent: shown, not scored/);
  assert.equal(judge("clap", { kind: "wave" }, true).ok, true, "claps only: every tap counts");
  assert.equal(judge("wave", { kind: "any" }, false).ok, true);
});
