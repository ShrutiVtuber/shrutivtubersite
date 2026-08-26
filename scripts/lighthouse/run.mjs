import fs from "node:fs";
import lighthouse from "lighthouse";
import * as chromeLauncher from "chrome-launcher";

const CHROME = process.env.CHROME_PATH;
const BASE = process.env.BASE ?? "http://127.0.0.1:8200";
const pages = process.argv.slice(2);

const chrome = await chromeLauncher.launch({
  chromePath: CHROME,
  chromeFlags: ["--headless=new", "--no-sandbox", "--disable-gpu",
                "--disable-dev-shm-usage"],
});

const results = [];
for (const path of pages) {
  try {
    const r = await lighthouse(`${BASE}${path}`, {
      port: chrome.port,
      output: "json",
      logLevel: "error",
      // Desktop-ish but with Lighthouse's default mobile throttling kept off,
      // so the numbers describe the site rather than a simulated 3G phone.
      formFactor: "desktop",
      screenEmulation: { mobile: false, width: 1350, height: 940,
                         deviceScaleFactor: 1, disabled: false },
      throttling: { rttMs: 40, throughputKbps: 10240, cpuSlowdownMultiplier: 1,
                    requestLatencyMs: 0, downloadThroughputKbps: 0,
                    uploadThroughputKbps: 0 },
    });
    const c = r.lhr.categories;
    const row = {
      path,
      perf: Math.round((c.performance?.score ?? 0) * 100),
      a11y: Math.round((c.accessibility?.score ?? 0) * 100),
      bp: Math.round((c["best-practices"]?.score ?? 0) * 100),
      seo: Math.round((c.seo?.score ?? 0) * 100),
      fails: {},
    };
    for (const [key, cat] of Object.entries(c)) {
      for (const ref of cat.auditRefs) {
        const a = r.lhr.audits[ref.id];
        if (!a || a.score === null || a.score >= 1) continue;
        if (a.scoreDisplayMode === "informative" ||
            a.scoreDisplayMode === "notApplicable") continue;
        (row.fails[key] ??= []).push({
          id: a.id, title: a.title,
          score: a.score,
          disp: a.displayValue ?? "",
          weight: ref.weight,
        });
      }
    }
    results.push(row);
    console.log(`  ${path.padEnd(26)} P${row.perf} A${row.a11y} B${row.bp} S${row.seo}`);
  } catch (e) {
    console.log(`  ${path.padEnd(26)} FAILED — ${e.message.slice(0, 70)}`);
    results.push({ path, error: e.message });
  }
}
await chrome.kill();
fs.writeFileSync(process.env.OUT ?? "lh-results.json", JSON.stringify(results, null, 2));
