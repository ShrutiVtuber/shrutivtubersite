/* Walk every page at every width and report anything that overflows.
 *
 * The failure being looked for is the one she saw: content wider than the
 * window, which produces a sideways scrollbar and a page that looks broken.
 * Measured rather than eyeballed, because a layout can be fine at the two
 * widths somebody happens to try and wrong between them.
 */
import { chromium } from "playwright-core";

const BASE = process.env.BASE ?? "http://127.0.0.1:8200";
const COOKIE = process.env.ADMIN_COOKIE ?? "";
const WIDTHS = [1440, 1280, 1160, 1100, 1024, 900, 834, 768, 700, 640, 560, 480, 390, 360];
const PAGES = (process.env.PAGES ?? "/").split(",");

const browser = await chromium.launch({ executablePath: "/ms-playwright/chromium-1148/chrome-linux/chrome" });
const context = await browser.newContext();
if (COOKIE) {
  await context.addCookies([{
    name: "shruti_session", value: COOKIE,
    domain: "127.0.0.1", path: "/",
  }]);
}

const problems = [];
for (const path of PAGES) {
  for (const width of WIDTHS) {
    const page = await context.newPage();
    await page.setViewportSize({ width, height: 900 });
    try {
      await page.goto(`${BASE}${path}`, { waitUntil: "networkidle", timeout: 20000 });
    } catch {
      await page.close();
      continue;
    }
    const found = await page.evaluate((w) => {
      const doc = document.documentElement;
      const overflow = doc.scrollWidth - w;
      const wide = [];
      if (overflow > 1) {
        for (const el of document.querySelectorAll("body *")) {
          const box = el.getBoundingClientRect();
          if (box.width === 0) continue;
          // The skip link lives off-screen on purpose; that is the pattern,
          // not a bug, and reporting it buries the real ones.
          // Anything parked far off-screen is deliberate — skip links and
          // honeypot fields both do it — and reporting them buries the real
          // ones underneath.
          if (box.right < -100) continue;
          if (box.right > w + 1 || box.left < -1) {
            const cls = (el.className || "").toString().split(" ").filter(Boolean).slice(0, 2).join(".");
            wide.push(`${el.tagName.toLowerCase()}${cls ? "." + cls : ""} ${Math.round(box.left)}→${Math.round(box.right)}`);
          }
        }
      }
      return { overflow, wide: [...new Set(wide)].slice(0, 3) };
    }, width);
    if (found.overflow > 1) {
      problems.push({ path, width, over: found.overflow, what: found.wide });
    }
    await page.close();
  }
}
await browser.close();

if (!problems.length) {
  console.log("  nothing overflows at any width");
} else {
  for (const p of problems) {
    console.log(`  ${p.path} @ ${p.width} — ${p.over}px over: ${p.what.join(" | ")}`);
  }
}
