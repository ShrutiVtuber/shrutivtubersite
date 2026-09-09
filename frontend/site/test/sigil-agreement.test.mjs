/* The website and the phone must draw the same sigil.
 *
 * A practitioner types a statement here, then types it again into Shruti's
 * Tools, and gets two different figures — which one is theirs? The tool's whole
 * claim is that the geometry is deterministic and reproducible by hand. Two
 * engines that disagree make that claim false.
 *
 * The Dart port in shruti-tools holds the matching half of this
 * (`test/sigil_agrees_test.dart`). BOTH sides compare against the SAME fixture
 * file, copied into both repos, and that is the point of the arrangement: this
 * catches sigil.js drifting, the Dart one catches the port drifting, and
 * neither can be quietly satisfied by editing the fixture — it would then have
 * to be re-copied to the other repo, where it would fail.
 *
 * ⚠ If this fails because you MEANT to change the geometry: regenerate with
 *     node scripts/gen-sigil-fixture.mjs > test/fixtures/sigil_agreement.json
 * then copy that file to shruti-tools/test/fixtures/ and ship both. A sigil
 * drawn last year should still come out the same, so changing the geometry at
 * all is worth a moment's thought first.
 *
 * Lives here and not in the Python suite because the backend container has no
 * node and no copy of the frontend — the test would have skipped itself
 * forever, which is worse than not having written it.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { reduce, draw } from "../src/lib/sigil.js";

const fixture = JSON.parse(
  readFileSync(fileURLToPath(new URL("./fixtures/sigil_agreement.json", import.meta.url)), "utf8"),
);

test("the geometry still draws what the app expects", () => {
  for (const want of fixture) {
    const r = reduce(want.statement, { keepVowels: want.keepVowels });
    const where = `${JSON.stringify(want.statement)} as ${want.weight}/${want.enclosure}`;

    assert.deepEqual(r.lettersOnly, want.lettersOnly, `letters of ${where}`);
    assert.deepEqual(r.afterVowels, want.afterVowels, `vowel step of ${where}`);
    assert.deepEqual(r.unique, want.unique, `reduction of ${where}`);
    assert.equal(r.exhausted, want.exhausted);
    assert.equal(r.tooShort, want.tooShort);

    const svg = draw(r.unique, { weight: want.weight, enclosure: want.enclosure });
    assert.equal(svg, want.svg, `the figure for ${where} changed — the app draws the old one`);
  }
});

test("the fixture still covers the corners", () => {
  // Guards the guard: a fixture trimmed to two happy cases proves nothing.
  assert.ok(fixture.length >= 10, "the fixture shrank");
  assert.ok(fixture.some((c) => c.exhausted), "no all-vowels case");
  assert.ok(fixture.some((c) => c.tooShort), "no single-letter case");
  assert.ok(fixture.some((c) => c.keepVowels), "no vowels-kept case");
  assert.equal(new Set(fixture.map((c) => c.weight)).size, 3);
  assert.equal(new Set(fixture.map((c) => c.enclosure)).size, 3);
});

test("nothing is drawn from an empty reduction", () => {
  // A blank 512×512 frame would be a figure the reader could export and use.
  assert.equal(draw([], {}), null);
  assert.equal(reduce("AEIOU").unique.length, 0);
});

test("the statement never travels with the figure", () => {
  // Someone will send this SVG to a friend. The page promises the statement is
  // neither transmitted nor written into the file; nothing enforces that but a
  // test.
  for (const c of fixture) {
    if (c.svg === null) continue;
    for (const tag of ["<title", "<desc", "<metadata"]) {
      assert.ok(!c.svg.includes(tag), `${tag} in the figure for ${c.statement}`);
    }
    for (const word of c.statement.toUpperCase().split(/\s+/).filter((w) => w.length > 2)) {
      assert.ok(
        !c.svg.toUpperCase().includes(word),
        `"${word}" of the statement was written into the file`,
      );
    }
  }
});
