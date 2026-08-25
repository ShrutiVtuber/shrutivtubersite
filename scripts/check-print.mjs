/* Does any watermark sit on top of something a reader needs?
 *
 * She asked for watermarks "not over the chart or any useful information",
 * and that is a geometric claim, so it is checked geometrically. Reading the
 * stylesheet cannot answer it: the marks are positioned against the sheet, so
 * a padding change three rules away moves them into the type area without
 * changing a single line that mentions a watermark.
 *
 * Measured in PRINT media, because that is the layout that matters and it is
 * not the one you see on screen.
 */
import { chromium } from "playwright-core";

const BASE = process.env.BASE ?? "http://127.0.0.1:8200";
const TOKEN = process.env.TOKEN;
if (!TOKEN) {
  console.error("  TOKEN is required — the owner token of a chart to print");
  process.exit(2);
}

const browser = await chromium.launch({
  executablePath: "/ms-playwright/chromium-1148/chrome-linux/chrome",
});
const ctx = await browser.newContext({
  userAgent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
});
if (process.env.ADMIN_COOKIE) {
  await ctx.addCookies([{
    name: "shruti_session", value: process.env.ADMIN_COOKIE,
    domain: new URL(BASE).hostname, path: "/",
  }]);
}
const page = await ctx.newPage();
await page.goto(`${BASE}/chart/print/${TOKEN}`, { waitUntil: "networkidle" });
await page.emulateMedia({ media: "print" });
await page.waitForTimeout(300);

const { content, marks } = await page.evaluate(() => {
  const box = (e) => {
    const b = e.getBoundingClientRect();
    return { x: b.x, y: b.y, w: b.width, h: b.height,
             what: e.tagName.toLowerCase() + " «" + (e.textContent || "").trim().slice(0, 28) + "»" };
  };
  const content = [];
  const svg = document.querySelector("svg");
  if (svg) content.push({ ...box(svg), what: "the chart" });
  document.querySelectorAll(
    ".sheet h1, .sheet h2, .sheet p, .sheet td, .sheet th, .sheet-foot span",
  ).forEach((e) => {
    if (!e.closest(".edge") && (e.textContent || "").trim()) content.push(box(e));
  });
  return { content, marks: [...document.querySelectorAll(".edge")].map(box) };
});

const hits = (a, b) =>
  !(a.x + a.w <= b.x || b.x + b.w <= a.x || a.y + a.h <= b.y || b.y + b.h <= a.y);

const clashes = [];
for (const mark of marks) for (const c of content) if (hits(mark, c)) clashes.push(c.what);

if (!content.length || !marks.length) {
  console.error(`  NOTHING MEASURED — ${content.length} readable boxes, ${marks.length} marks.`);
  console.error("  That is a broken check, not a passing one.");
  await browser.close();
  process.exit(2);
}

if (clashes.length) {
  console.error(`  a watermark covers ${clashes.length} thing(s):`);
  for (const c of [...new Set(clashes)]) console.error(`    ${c}`);
  await browser.close();
  process.exit(1);
}
console.log(`  nothing is covered — ${marks.length} marks clear of ${content.length} readable boxes`);
await browser.close();
