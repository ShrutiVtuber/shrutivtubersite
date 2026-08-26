import lighthouse from "lighthouse";
import * as chromeLauncher from "chrome-launcher";
const chrome = await chromeLauncher.launch({
  chromePath: process.env.CHROME_PATH,
  chromeFlags: ["--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage"],
});
for (const path of process.argv.slice(2)) {
  const r = await lighthouse(`http://127.0.0.1:8200${path}`, {
    port: chrome.port, output: "json", logLevel: "error", formFactor: "desktop",
    screenEmulation:{mobile:false,width:1350,height:940,deviceScaleFactor:1,disabled:false},
    throttling:{rttMs:40,throughputKbps:10240,cpuSlowdownMultiplier:1,requestLatencyMs:0,
                downloadThroughputKbps:0,uploadThroughputKbps:0},
  });
  console.log(`\n═══ ${path}  perf ${Math.round(r.lhr.categories.performance.score*100)} ═══`);
  for (const ref of r.lhr.categories.performance.auditRefs) {
    if (!ref.weight) continue;
    const a = r.lhr.audits[ref.id];
    const contribution = ref.weight * (1 - (a.score ?? 1));
    console.log(`  w${String(ref.weight).padStart(2)}  score ${(a.score ?? 1).toFixed(3)}  ` +
                `lost ${contribution.toFixed(2)}  ${ref.id.padEnd(28)} ${a.displayValue ?? ""}`);
  }
}
await chrome.kill();
