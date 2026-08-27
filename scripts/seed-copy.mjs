/* Register every editable string with the admin.
 *
 * Reads the `say("key", "default")` calls back out of the page sources, so the
 * template stays the single place a string is declared. Nothing here decides
 * what a string SAYS — it only tells the admin which strings exist, what to
 * call them, and what the page was written with.
 *
 * Run after any deploy that adds, renames or moves one:
 *   node scripts/seed-copy.mjs            (against localhost)
 *   BASE=https://shrutivtuber.com node scripts/seed-copy.mjs
 *
 * Values she has written are never touched — the route it posts to updates
 * labels, defaults and order, and nothing else.
 */
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(process.argv[2] ?? "frontend/site/src");
const BASE = process.env.BASE ?? "http://127.0.0.1:8200";
const COOKIE = process.env.ADMIN_COOKIE ?? "";

/* `t("key", "text")` and `t("key", 'text')` and backticks, across newlines.
   Deliberately NOT a general expression parser: a default that is not a plain
   literal cannot be seeded, and should not be — a string assembled at runtime
   is not a string somebody can edit. */
const CALL = /\bsay\(\s*(["'`])([^"'`]+?)\1\s*,\s*(["'`])([\s\S]*?)\3\s*(?:,\s*(["'`])([^"'`]*?)\5\s*)?\)/g;

/* The file DECLARES its own namespace — `copy("support")`, or
   `copy("component:SubscribeBlock")` for something shared across pages. Read
   it back rather than deriving it from the path: the path can be moved and the
   declaration cannot drift from what the page actually asks for at runtime. */
function pageNameFor(src) {
  const m = src.match(/copy\(\s*["'`]([^"'`]+)["'`]\s*\)/);
  return m ? m[1] : null;
}

function walk(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) {
      /* The admin edits copy; it does not have copy of its own to edit.
         Overlays render beside the encoder and must not wait on a fetch. */
      if (e.name === "admin" || e.name === "overlay" || e.name === "styles") continue;
      out.push(...walk(p));
    } else if (e.name.endsWith(".astro")) out.push(p);
  }
  return out;
}

/* A key becomes a label by being read as English. "tiers.note" is not a thing
   to hand somebody writing marketing copy. */
/* The first few words, as a name. Long enough to recognise, short enough to
   scan a column of them. */
function preview(text) {
  const flat = text.replace(/\s+/g, " ").trim();
  if (flat.length <= 42) return flat;
  return flat.slice(0, 42).replace(/\s+\S*$/, "") + "…";
}

const SAY = {
  cta: "button", btn: "button", lede: "lead paragraph", sub: "subheading",
  eyebrow: "eyebrow", body: "body text", note: "note", head: "heading",
  heading: "heading", title: "heading", intro: "introduction",
  empty: "empty state", err: "error", placeholder: "placeholder",
  oneoff: "one-off", footnote: "footnote", testmode: "test mode",
};

/* A key read as English. "oneoff.cta" is not a thing to hand somebody who is
   writing marketing copy — but "One-off · button" tells them where to look. */
function labelFor(key) {
  const parts = key.split(/[.\-_]/).filter(Boolean).map((p) => SAY[p] ?? p);
  const said = parts.join(" · ").replace(/(\d+)$/, " $1");
  return said.charAt(0).toUpperCase() + said.slice(1);
}

let pages = 0, strings = 0, added = 0;
for (const file of walk(ROOT)) {
  const src = fs.readFileSync(file, "utf8");
  const items = [];
  const seen = new Set();
  let m, i = 0;
  while ((m = CALL.exec(src))) {
    const key = m[2];
    if (seen.has(key)) continue;      // first occurrence wins its position
    seen.add(key);
    const text = m[4];
    items.push({
      key,
      /* A key like "text.9" tells her nothing, and those are exactly the
         strings that sit outside any heading — the ones hardest to place. When
         the key is that generic, the label becomes the words themselves, which
         is what she is actually looking for in the panel. */
      label: m[6] || (/^text\.?\d*$/.test(key) ? preview(text) : labelFor(key)),
      default: text,
      position: i++,
      multiline: text.length > 90 || text.includes("\n"),
    });
  }
  if (items.length === 0) continue;

  const page = pageNameFor(src);
  if (!page) {
    console.error(`  ${path.relative(ROOT, file)}: uses t() but never calls copy() — skipped`);
    process.exitCode = 1;
    continue;
  }
  const r = await fetch(`${BASE}/api/admin/copy/seed`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(COOKIE ? { Cookie: COOKIE } : {}) },
    body: JSON.stringify({ page, items }),
  });
  if (!r.ok) {
    console.error(`  ${page}: ${r.status} ${await r.text()}`);
    process.exitCode = 1;
    continue;
  }
  const got = await r.json();
  pages++; strings += got.seen; added += got.added;
  console.log(`  ${page.padEnd(28)} ${String(got.seen).padStart(3)} strings, ${got.added} new`);
}
console.log(`\n  ${pages} pages, ${strings} strings, ${added} newly registered`);
