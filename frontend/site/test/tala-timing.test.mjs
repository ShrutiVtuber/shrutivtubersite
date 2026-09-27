/* Tala timing (src/lib/carnatic/beatclock.ts) under a fake clock: the lookahead
 * scheduler leaves no gap between avartanams and does not drift over 100 of
 * them, however unevenly its timer fires; a hidden tab is caught up without a
 * burst; the timing windows and the calibration behave as specified. */
import { test } from "node:test";
import assert from "node:assert/strict";
import { BeatScheduler, windows, rate, calibrate, correct, CALIBRATION_MIN, RUNNING_BOUND_MS } from "../src/lib/carnatic/beatclock.ts";

/* A small deterministic random source, so a failure can be replayed. */
function rng(seed) {
  let x = seed >>> 0;
  return () => ((x = (x * 1664525 + 1013904223) >>> 0) / 2 ** 32);
}

/** Run a scheduler on a fake audio clock: the refill timer fires every `tick` s, give or take `jitter`. */
function run({ bpm, counts, avartanams, tick = 0.025, jitter = 0.02, stallEvery = 0, stall = 0, lookahead = 0.15, seed = 1 }) {
  const r = rng(seed);
  const beat = 60 / bpm;
  const s = new BeatScheduler(0.15, beat, counts);
  const out = [];
  let now = 0, ticks = 0;
  const total = counts * avartanams;
  while (out.length < total) {
    for (const b of s.due(now, lookahead)) if (out.length < total) out.push({ ...b, handedAt: now });
    ticks++;
    now += Math.max(0.001, tick + (r() * 2 - 1) * jitter) + (stallEvery && ticks % stallEvery === 0 ? stall : 0);
  }
  return { out, beat, s };
}

test("no gap between avartanams and no drift over 100 avartanams, with an uneven timer", () => {
  for (const [bpm, counts] of [[60, 8], [70, 8], [47, 7], [133, 5], [40, 16]]) {
    const { out, beat } = run({ bpm, counts, avartanams: 100, stallEvery: 37, stall: 0.1, seed: bpm });
    assert.equal(out.length, counts * 100);
    out.forEach((b, n) => {
      assert.equal(b.n, n, "every count once, in order");
      assert.equal(b.index, n % counts);
      assert.equal(b.cycle, Math.floor(n / counts));
      // absolute: count n is at start + n × count, to the nanosecond, at count 1 and at count 800
      assert.ok(Math.abs(b.at - (0.15 + n * beat)) < 1e-9, `count ${n} drifted`);
      // handed to Web Audio before it is due to sound, never after
      assert.ok(b.at >= b.handedAt, `count ${n} was scheduled late`);
    });
    for (let n = 1; n < out.length; n++) {
      const gap = out[n].at - out[n - 1].at;
      assert.ok(Math.abs(gap - beat) < 1e-9, `gap before count ${n} (cycle ${out[n].cycle}) is ${gap}, not ${beat}`);
    }
    // the samam of avartanam 100 is exactly 99 cycles after the first
    const samams = out.filter((b) => b.index === 0);
    assert.ok(Math.abs(samams[99].at - samams[0].at - 99 * counts * beat) < 1e-9);
  }
});

test("the next cycle is scheduled ahead, not when the one before ends", () => {
  const { out } = run({ bpm: 60, counts: 8, avartanams: 10, tick: 0.025, jitter: 0.02 });
  for (const b of out.filter((x) => x.index === 0 && x.cycle > 0)) {
    // at least 150 ms of lookahead less one late timer (≤ 45 ms here) before samam sounds
    assert.ok(b.at - b.handedAt > 0.1, `samam of cycle ${b.cycle} handed over only ${(b.at - b.handedAt) * 1000} ms ahead`);
  }
});

test("a hidden tab: a longer lookahead keeps it gapless at one tick a second", () => {
  const { out, beat } = run({ bpm: 60, counts: 8, avartanams: 100, tick: 1.0, jitter: 0.1, lookahead: 1.5 });
  out.forEach((b, n) => {
    assert.ok(b.at >= b.handedAt);
    if (n) assert.ok(Math.abs(b.at - out[n - 1].at - beat) < 1e-9);
  });
});

test("back from a frozen tab: re-anchored to the next count ahead, no burst, still on the grid", () => {
  const s = new BeatScheduler(0, 0.5, 8);
  s.due(0, 0.15);
  s.due(1.0, 0.15);
  const now = 61.23;                      // the timer was frozen for a minute
  s.reanchor(now);
  const due = s.due(now, 0.15);
  assert.ok(due.length <= 1, "no burst of missed counts");
  for (const b of due) {
    assert.ok(b.at >= now);
    assert.ok(Math.abs(b.at - b.n * 0.5) < 1e-9, "still start + n × count");
  }
  assert.equal(s.beatAt(now).n, 122);
});

test("a new tempo takes over without a jump", () => {
  const s = new BeatScheduler(0, 1, 8);
  const first = s.due(0, 0.15).concat(s.due(0.9, 0.15));
  const lastAt = first[first.length - 1].at;  // count 1 at 1.0
  s.retempo(0.5, 0.95);
  const next = s.due(3.0, 0.15);
  assert.ok(Math.abs(next[0].at - (lastAt + 1)) < 1e-9, "the next unscheduled count keeps its time");
  for (let i = 1; i < next.length; i++) assert.ok(Math.abs(next[i].at - next[i - 1].at - 0.5) < 1e-9);
});

test("nearest and beatAt, at count 800 as at count 1", () => {
  const s = new BeatScheduler(0.15, 60 / 70, 8);
  const t = 0.15 + 800 * (60 / 70);
  assert.equal(s.beatAt(t + 0.001).n, 800);
  const h = s.nearest(t - 0.04);
  assert.equal(h.beat.n, 800);
  assert.ok(Math.abs(h.delta + 0.04) < 1e-9);
  assert.equal(s.nearest(0).beat.n, 0);
  assert.equal(s.nearest(-1), null, "long before the first count: nothing to score against");
});

test("timing windows: relaxed by default, standard and strict, never over 40 % of the gap", () => {
  assert.deepEqual(windows(), { perfect: 60, onTime: 120 });
  assert.deepEqual(windows("standard"), { perfect: 30, onTime: 80 });
  assert.deepEqual(windows("strict"), { perfect: 20, onTime: 50 });
  assert.deepEqual(windows("relaxed", 1), { perfect: 60, onTime: 120 });
  const dense = windows("relaxed", 0.2);   // targets 200 ms apart: at most 80 ms
  assert.ok(Math.abs(dense.onTime - 80) < 1e-9 && dense.perfect === 60);
  const w = windows();
  assert.equal(rate(-59, w), "perfect");
  assert.equal(rate(110, w), "onTime");
  assert.equal(rate(-121, w), "early");
  assert.equal(rate(130, w), "late");
});

test("calibration: the median offset with outliers left out", () => {
  const r = rng(7);
  const taps = Array.from({ length: 14 }, () => 45 + (r() * 2 - 1) * 12);
  taps[3] = 310; taps[9] = -180;           // a stray tap and a double-tap
  const c = calibrate(taps);
  assert.ok(c && Math.abs(c.offsetMs - 45) <= 6, `offset ${c?.offsetMs}`);
  assert.equal(c.used, 12);
  assert.equal(calibrate(taps.slice(0, CALIBRATION_MIN - 1)), null, "too few taps");
});

test("the running correction is slow and bounded", () => {
  let o = 20;
  o = correct(o, 20, 60);
  assert.ok(o > 20 && o < 23, "one tap moves it only a little");
  for (let i = 0; i < 500; i++) o = correct(o, 20, 200 - 100);
  assert.ok(o <= 20 + RUNNING_BOUND_MS + 1e-9, "never further than the bound from the calibration");
  assert.equal(correct(10, 10, 400), 10, "a tap far off is ignored");
});
