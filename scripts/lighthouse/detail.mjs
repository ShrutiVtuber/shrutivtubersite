import fs from "node:fs";
import lighthouse from "lighthouse";
import * as chromeLauncher from "chrome-launcher";

const chrome = await chromeLauncher.launch({
  chromePath: process.env.CHROME_PATH,
  chromeFlags: ["--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
});
const WANT = (process.env.AUDITS ?? "").split(",").filter(Boolean);

for (const path of process.argv.slice(2)) {
  const r = await lighthouse(`${process.env.BASE ?? "http://127.0.0.1:8200"}${path}`, {
    port: chrome.port, output: "json", logLevel: "error",
    formFactor: "desktop",
    screenEmulation: { mobile: false, width: 1350, height: 940, deviceScaleFactor: 1, disabled: false },
    throttling: { rttMs: 40, throughputKbps: 10240, cpuSlowdownMultiplier: 1,
                  requestLatencyMs: 0, downloadThroughputKbps: 0, uploadThroughputKbps: 0 },
  });
  console.log(`\n═══ ${path} ═══`);
  for (const id of WANT) {
    const a = r.lhr.audits[id];
    if (!a || a.score === null || a.score >= 1) continue;
    console.log(` ▸ ${id}: ${a.displayValue ?? ""}`);
    const items = a.details?.items ?? [];
    for (const it of items.slice(0, 8)) {
      const node = it.node ?? it.subItems?.items?.[0]?.node;
      if (node) {
        console.log(`    ${(node.snippet ?? "").replace(/\s+/g, " ").slice(0, 130)}`);
        if (node.explanation) console.log(`      → ${node.explanation.replace(/\s+/g," ").slice(0,150)}`);
        if (node.selector) console.log(`      @ ${node.selector.slice(0, 110)}`);
      } else {
        const brief = { url: it.url, source: it.source?.url ?? it.source,
                        wasted: it.wastedBytes ?? it.wastedMs, score: it.score };
        console.log(`    ${JSON.stringify(brief).slice(0, 180)}`);
      }
    }
  }
}
await chrome.kill();
