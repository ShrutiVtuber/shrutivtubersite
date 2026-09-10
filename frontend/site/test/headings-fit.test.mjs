/* A heading drawn by the server has to fit the box it is drawn into.
 *
 * ⚠ **Both failures are invisible in the finished image**, which is why this
 * is a test and not a look. SVG text does not wrap and does not complain: a
 * title too long for its column simply runs past the edge and the PNG is
 * cropped at the width it was asked for, so the card renders, uploads, and
 * posts to Discord reading "TEST — bridge chec". And the first fix for that
 * was worse — it stopped wrapping once it had two lines and returned them,
 * so a long title came back as its opening words with the rest silently gone
 * and no ellipsis to show anything was missing. A well-composed card that is
 * quietly wrong outlives one that looks broken.
 *
 * The horoscope share card never needed this: it only ever sets one of twelve
 * sign names. The practice room puts a writer's own title in the same slot.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { fitLines } from "../src/lib/fit.ts";

/** The column the practice cards draw into. */
const WIDTH = 520;
/** Matches PER_EM in the module: what it believes a character costs. */
const PER_EM = 0.5;

const fits = ({ lines, size }, width = WIDTH) =>
  lines.every((line) => line.length * size * PER_EM <= width);

test("a short heading is drawn at the largest size", () => {
  const got = fitLines("Leo", WIDTH);
  assert.deepEqual(got.lines, ["Leo"]);
  assert.equal(got.size, 72);
});

test("every sign name fits on one line at full size", () => {
  for (const name of ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                      "Libra", "Scorpio", "Sagittarius", "Capricorn",
                      "Aquarius", "Pisces"]) {
    const got = fitLines(name, WIDTH);
    assert.equal(got.lines.length, 1, `${name} wrapped`);
    assert.equal(got.size, 72, `${name} was shrunk`);
  }
});

test("a heading too wide for one line uses two", () => {
  const got = fitLines("TEST — bridge check", WIDTH);
  assert.equal(got.lines.length, 2);
  assert.ok(fits(got), "still too wide after wrapping");
  assert.equal(got.lines.join(" "), "TEST — bridge check",
               "wrapping changed the words");
});

test("a long heading shrinks before it gives up", () => {
  const got = fitLines("A whole month of readings for every sign", WIDTH);
  assert.ok(got.size < 72, "never tried a smaller size");
  assert.ok(fits(got), "does not fit even after shrinking");
});

test("a heading that cannot fit says so, rather than losing its end", () => {
  const long = "An extremely long title about the whole of September and " +
               "everything the sky did in it";
  const got = fitLines(long, WIDTH);
  assert.ok(got.lines.length <= 2, "spilled past two lines");
  assert.ok(fits(got), "overflows the column");
  assert.ok(got.lines.at(-1).endsWith("…"),
            "text was dropped with no ellipsis — the card looks complete and " +
            "is missing half the title");
});

test("one unbreakable word is cut, not left to overflow", () => {
  const got = fitLines("Supercalifragilisticexpialidociousandthensomemore", WIDTH);
  assert.ok(fits(got), "a single long word ran past the edge");
  assert.ok(got.lines.at(-1).endsWith("…"));
});

test("nothing to draw is not a crash", () => {
  for (const empty of ["", "   ", "\n"]) {
    const got = fitLines(empty, WIDTH);
    assert.equal(got.lines.length, 1);
    assert.equal(got.lines[0], "");
  }
});

test("a narrow column still returns something drawable", () => {
  const got = fitLines("A whole month of readings", 60);
  assert.ok(got.lines.length >= 1);
  assert.ok(got.lines.every((l) => typeof l === "string"));
});
