# Lighthouse

Three scripts, because "the score is 99" and "which element is costing the
point" are different questions and only the second one is actionable.

| | |
|---|---|
| `run.mjs` | every category, one line per page — the sweep |
| `metrics.mjs` | the performance score broken into what each metric LOST |
| `detail.mjs` | the failing ELEMENTS, with selectors and axe's explanation |

## Running it

Chrome is not in the repo and not a dependency of the site. Fetch one:

```sh
cd scripts/lighthouse
npm install lighthouse chrome-launcher
npx @puppeteer/browsers install chrome@stable
export CHROME_PATH=$PWD/chrome/linux-*/chrome-linux64/chrome
```

Then, with the stack up and **the holding page off** (otherwise every page is
audited as the holding page):

```sh
node run.mjs / /about /tools /tools/planetary-hours
AUDITS=color-contrast,heading-order node detail.mjs /about
node metrics.mjs /
```

`BASE` overrides the origin; it defaults to `http://127.0.0.1:8200`.

## What the numbers mean, and what they do not

Measured on a **desktop** form factor with throttling effectively off, so they
describe the site rather than a simulated phone on 3G. Run them the same way
every time or the numbers are not comparable to each other.

They are also measured against a development machine running the whole stack
plus a headless Chrome. Production has a box to itself. **Treat a local number
as a floor, not as the answer** — and re-run against the live origin once the
holding page is down, because that is the number that describes what a reader
gets.

## Two results that are correct and will never be 100

- **`/signup` scores SEO 66.** It carries `noindex, nofollow` on purpose: it is
  a conversion endpoint, not something anybody should reach from a search. The
  audit that fails is `is-crawlable`, and it is failing on a decision rather
  than a defect. Making it 100 would mean publishing the page to search.
- **The two calendar pages flip between 99 and 100.** Both render a whole
  calendar server-side, and their LCP lands at 0.8–0.9s, right on the boundary
  of the scoring curve. What moves is machine load, not the page.
