/* Every word a reader sees must be one she can change.
 *
 * The copy system makes that possible; nothing made it TRUE. Strings kept
 * drifting back into templates, and she found them the slow way — writing the
 * final copy and hitting sentence after sentence with no box beside it: "I need
 * to stop finding areas that are not editable."
 *
 * So this walks every template, strips what never renders as prose, and fails
 * on any human-facing text that does not go through say(). A new hardcoded
 * label fails here rather than in her hands three weeks later.
 *
 * ⚠ To add a genuine exception, put it in ALLOWED with the reason. Do not widen
 * the stripping — that is how a guard quietly stops guarding.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join, relative, extname, basename } from "node:path";

const SRC = fileURLToPath(new URL("../src", import.meta.url));

/* Her own screens, and OBS sources nobody reads. The admin's labels are the
   tool she edits WITH; the overlays render into a stream at 1920×1080 where a
   <title> is never seen. */
const SKIP_DIRS = ["pages/admin", "pages/overlay"];

/* Attributes a person reads or hears. NOT data-* state flags: data-empty="true"
   is a switch the CSS reads, and an early version of this reported it. */
const SPOKEN = ["placeholder", "aria-label", "alt", "title", "aria-description", "label", "summary"];

/* Deliberate exceptions, each with its reason. */
const ALLOWED = [
  // An HTML entity cannot travel through say(): "♪&#xFE0E;" in a JS string
  // renders the characters &#xFE0E; to the reader. These are decorative marks
  // with no words in them.
  { file: "components/blocks/SupportBand.astro", text: "♪&#xFE0E;" },
  { file: "components/journal/SkyRecord.astro", text: "☉︎&#xFE0E; ☾︎&#xFE0E;" },
  { file: "pages/shop/thank-you.astro", text: "✶&#xFE0E;" },
  // "3 of 8" — the word between two numbers, assembled in the template.
  { file: "components/counters/CounterCard.astro", text: "of" },
];

function walk(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (extname(full) === ".astro") out.push(full);
  }
  return out;
}

/** Remove what never renders as prose, keeping newline count so lines line up. */
function strip(src) {
  const blank = (m) => "\n".repeat((m.match(/\n/g) || []).length);
  if (src.startsWith("---")) {
    const end = src.indexOf("\n---", 3);
    if (end !== -1) src = blank(src.slice(0, end + 4)) + src.slice(end + 4);
  }
  src = src.replace(/<style[^>]*>[\s\S]*?<\/style>/g, blank);
  src = src.replace(/<script[^>]*>[\s\S]*?<\/script>/g, blank);
  src = src.replace(/<!--[\s\S]*?-->/g, blank);
  return src;
}

/** Spans of {...}, so an expression's insides are not read as prose. */
function expressions(src) {
  const spans = [];
  let depth = 0, start = 0;
  for (let i = 0; i < src.length; i++) {
    if (src[i] === "{") { if (depth === 0) start = i; depth++; }
    else if (src[i] === "}" && depth) { depth--; if (depth === 0) spans.push([start, i + 1]); }
  }
  return spans;
}

const NOT_PROSE = /^[\s\d\W_]*$/;

test("no reader-facing string is stranded in a template", () => {
  const stranded = [];
  for (const path of walk(SRC)) {
    const rel = relative(SRC, path).split("\\").join("/");
    if (SKIP_DIRS.some((d) => rel.startsWith(d))) continue;

    const src = strip(readFileSync(path, "utf8"));
    const spans = expressions(src);
    const inExpr = (i) => spans.some(([a, b]) => i >= a && i < b);

    const note = (text) => {
      if (!text || NOT_PROSE.test(text)) return;
      if (text.includes("say(") || text.includes("{") || text.includes("}")) return;
      if (ALLOWED.some((a) => a.file === rel && a.text === text)) return;
      stranded.push(`${rel}: ${JSON.stringify(text)}`);
    };

    for (const m of src.matchAll(/>([^<>]+)</g)) {
      const at = m.index + 1;
      if (inExpr(at)) continue;
      note([...m[1]].filter((_c, k) => !inExpr(at + k)).join("").trim());
    }
    for (const m of src.matchAll(new RegExp(`\\b(${SPOKEN.join("|")})="([^"]+)"`, "g"))) {
      note(m[2].trim());
    }
  }

  assert.deepEqual(stranded, [],
    `${stranded.length} string(s) a reader sees but she cannot edit:\n  ` +
    stranded.join("\n  ") +
    "\n\nWrap each in say(\"key\", \"the words\") and run scripts/seed-copy.mjs.");
});

test("the exceptions are still real", () => {
  // An exception that no longer matches anything is a rule nobody removed.
  for (const a of ALLOWED) {
    const src = readFileSync(join(SRC, a.file), "utf8");
    assert.ok(src.includes(a.text),
      `${a.file} no longer contains ${JSON.stringify(a.text)} — drop the exception`);
  }
});
