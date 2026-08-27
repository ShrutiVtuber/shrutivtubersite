/* Register every editable string with the admin.
 *
 * Reads the `t("key", "default")` calls back out of the page sources, so the
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

const ROOT = path.resolve(process.argv[2] ?? "frontend/site/src/pages");
const BASE = process.env.BASE ?? "http://127.0.0.1:8200";
const COOKIE = process.env.ADMIN_COOKIE ?? "";

/* `t("key", "text")` and `t("key", 'text')` and backticks, across newlines.
   Deliberately NOT a general expression parser: a default that is not a plain
   literal cannot be seeded, and should not be — a string assembled at runtime
   is not a string somebody can edit. */
const CALL = /\bt\(\s*(["'`])([^"'`]+?)\1\s*,\s*(["'`])([\s\S]*?)\3\s*(?:,\s*(["'`])([^"'`]*?)\5\s*)?\)/g;

function pageNameFor(file) {
  let rel = path.relative(ROOT, file).replace(/\.astro$/, "");
  if (rel.endsWith("/index")) rel = rel.slice(0, -"/index".length);
  if (rel === "index") rel = "home";
  return rel;
}

function walk(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (e.name === "admin") continue;
      out.push(...walk(p));
    } else if (e.name.endsWith(".astro")) out.push(p);
  }
  return out;
}

/* A key becomes a label by being read as English. "tiers.note" is not a thing
   to hand somebody writing marketing copy. */
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
      label: m[6] || labelFor(key),
      default: text,
      position: i++,
      multiline: text.length > 90 || text.includes("\n"),
    });
  }
  if (items.length === 0) continue;

  const page = pageNameFor(file);
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
