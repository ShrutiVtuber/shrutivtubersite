# The Ledger — how it is built

A business planner and account book for Big Ambitions, inside Squirrel Guides at `/ledger`. Design: `shrutisgametracker/design/design_handoff_ledger/` (README.md and SPEC.md are the spec; `prototype/` is the reference, not code to copy). Game research: `~/Documents/development/bigambitions/research/`.

This page holds the three contracts the parts are built against. Change a contract here first, then in the code.

## Decisions

- **The reckoning runs in the browser.** Every change re-reckons at once (handoff: "no debounce is needed"), and planning works signed out. `frontend/site/src/lib/ledger/engine.ts` is a pure module: no DOM, no fetch. It is tested with `node --test` against figures worked out from the research. The server stores plans and weeks; it does not compute them. The one exception is Contract 5: the app is native, so the Astro server runs the same engine for it.
- **The data is served, never committed here.** The compiled facts are `LicenseRef-All-Rights-Reserved`, like every research pack. They live in `shrutisgametracker/research/big-ambitions/ledger.json` with `sources-ledger.md` and `coverage-ledger.md`. `scripts/sync-gamedata.sh` copies them into the `gamedata` volume as `ledger-big-ambitions.json`, and `GET /api/ledger/data` serves the file. When it is missing, the Ledger says the game's data is not loaded, which is a working state.
- **Stack:** Astro 5 SSR with plain TypeScript module scripts that mount onto server-rendered markup, as `/builds/plan` does. No UI framework. Every visible string goes through `copy()` / `say()`. (The handoff says "Astro 6, islands", but the site is not built that way.)
- **Section:** `/ledger` belongs to the `guides` section, so it is hidden with it. Both `SECTION_PATHS` maps must be updated together.
- **Privacy:** a ledger is private. All three tables cascade with the account and appear in the export. Nothing in a ledger is public, so nothing here needs the publishing agreement.

## Contract 1 — the data pack (`ledger.json`)

Figures are numbers, ids are lower-case slugs, and anything unknown is `null`. Every section that carries values not read from the game's code includes `"confidence": "datamined" | "community" | "estimated"`.

```jsonc
{
  "game": { "id": "big-ambitions", "name": "Big Ambitions", "version": "1.0", "build": "3682", "gathered": "2026-09-25" },
  "rules": {
    "classCeilings": { "working": 1.20, "middle": 1.40, "upper": 1.70 },
    "monopolyBonus": 0.30,
    "satisfaction": { "at0": 0.5, "at100": 1.5 },          // multiplier = 0.5 + s/100
    "promotion": { "gainPerMultiplier": 0.75 },            // promoMult = base(difficulty) + 0.75 × promo/100
    "wholesaleDeliveryFee": 400,
    "maxAmountPerProduct": { "coffee-shop": 5 }            // defaults to 1 when absent
  },
  "difficulties": [ { "id": "normal", "name": "Normal", "startMoney": 10000, "taxPct": 5,
      "marketPriceMultiplier": 0.7, "salaryMultiplier": 0.7, "baseCustomerPromotionMultiplier": 0.55,
      "wholesaleUrgentFee": 0.20, "importerUrgentFee": 0.75, "exportMultiplier": 0.65, "sellingMultiplier": 0.75 } ],
  "neighbourhoods": [ { "id": "hells-kitchen", "name": "Hell's Kitchen",
      "mix": { "working": 0.06, "middle": 0.82, "upper": 0.12 }, "priceIndex": 1.424,
      "marketingStrength": 0.7, "demandsWeight": 0.7, "minInterior": 0, "rival": "Jessica Johnson" } ],
  "buildings": [ { "id": "12-2nd-avenue", "address": "12 2nd Avenue", "neighbourhood": "hells-kitchen",
      "use": "shop", "layout": "C2", "sqm": 225, "capacity": 30, "traffic": 72, "vehicleSlots": 0,
      "rentDay": 337, "deposit": 20220, "price": 146520752 } ],
      // use ∈ shop | office | warehouse | home | cinema | theatre | special
  "businessTypes": [ { "id": "gift-shop", "name": "Gift shop", "category": "retail", "simulator": "self-service",
      "course": null, "uses": ["shop"], "staff": ["customer-service", "security-guard"],
      "stock": ["wholesaler", "importer"], "theft": true, "maxAmountPerProduct": 1,
      "dayMult": [0.8, 0.75, 0.7, 0.75, 0.9, 1.0, 0.95],     // Monday first
      "hourMult": [/* 24 values, hour 0 first */],
      "products": [ { "product": "gift-cheap", "impact": 1.0 }, { "product": "soda-can", "impact": 0.9 } ],
      "requires": [ "cash-register|checkout-counter", "shopping-baskets" ],   // "a|b" = either
      "demands": { "music": 1, "uniforms": 1, "interior": 1, "toilet": 1, "privacy": 1, "sink": 1 },
      "entranceFee": null } ],
  "products": [ { "id": "gift-cheap", "name": "Gift (cheap)", "marketPrice": 18, "wholesale": 5, "box": 300,
      "salesRatio": 0.85, "optimalProviders": null, "sources": ["wholesaler", "importer"],
      "weeklyLimit": 3000, "displays": [ { "fixture": "rounded-shelf", "units": 200 } ] } ],
  "fixtures": [ { "id": "cash-register", "name": "Cash register", "price": 900, "store": "Square Appliances",
      "customersPerHour": 20, "kind": "pos", "needs": "cabinet-with-drawers", "displays": [] } ],
      // kind ∈ pos | display | required | comfort | security | storage
  "staffRoles": [ { "id": "customer-service", "name": "Customer service", "baseWage": 16, "station": "cash-register" } ],
  "campaigns": [ { "id": "internet-small", "name": "Small internet campaign", "kind": "internet", "costDay": 100, "reach": 20 } ],
  "courses": [ { "id": "headquarters", "name": "Headquarters" } ]
}
```

## Contract 2 — the engine (`frontend/site/src/lib/ledger/engine.ts`)

```ts
type Plan = {
  typeId: string | null; buildingId: string | null;
  prices: Record<string, number>;            // productId → shelf price; absent = the all-buy edge
  fixtures: Record<string, number>;          // fixtureId → count
  hours: number[][];                         // [7][24]: 0 closed, n = n registers staffed (Monday first)
  campaigns: Record<string, boolean>;
  satisfaction: number;                      // 0–100, default 80
  satisfactionTyped: boolean;
  demand?: Record<string, number>;           // productId → 0–100, default 80
  competitorPrice?: Record<string, number>;
};
type Ctx = { difficulty: string; courses: string[] };

reckon(data, plan, ctx): Reckoning
  // would[7][24], served[7][24], heldBy[7][24]: "building" | "registers" | "displays" | null
  // products: [{ id, price, tread, units, moneyIn, goods }]
  // week: { moneyIn, goods, wages, rent, ads, deliveries, total }  — every line a Figure
  // setup: { fixtures, deposit, total }, paybackDays
  // limit: { state: "held" | "free" | "unknown" | "cannot-open" | "not-a-shop", by?, cap?, hours?, would?,
  //          fix?: { kind, cost, weeklyCost, worth } }
  // missing: [{ path, requirement }]
type Figure = { value: number | null; honesty: "counted" | "approximate" | "not-counted"; lines: BreakdownLine[] };

priceStair(data, productId, neighbourhoodId, events)   // steps, markers: market / all-buy / best / competitor
cheapestCampaigns(data, buildingId, target)             // all 63 mixes; cheapest reaching target, or the best reachable
rentOrBuy(data, buildingId, years)
rankBuildings(data, plan, ctx, filters)                 // memoised by plan + filters
```

Additions, as built (types in `lib/ledger/types.ts`):

- `Plan.products?: string[]`: the products stocked; absent = the type's primary products.
- `Plan.displays?: {productId: {fixtureId: n}}`: which displays hold which product. When it is absent the engine shares the display fixtures out, and each goes to the product with the least display so far.
- `Plan.staff?: {roleId: {hours?, wage?}}`: the hours a week for staff beyond the registers (cleaning, guards), and the wage an hour when the person knows it. The default wage is base × the difficulty's salary multiplier, marked approximate. The role that staffs the registers works every staffed register-hour.
- `Ctx.custom?` (a Custom difficulty's values) and `Ctx.importIndex?` (default 0.9).
- `heldBy` can also be `"fixtures"`: a store-wide required fixture, such as the baskets or a changing room. `limit.reason` names the unknown state (no-type · no-building · closed · no-customers). `limit.say` and `rentOrBuy().say` are `{key, template, params}` for `say()` + `fill()`. Figures carry `lines: {key, label, op: + − × ÷ =, value, unit, honesty}`, and a null value means not counted.
- Goods are bought at the cheapest wholesalers' index (0.90). An imported-only good uses `Ctx.importIndex`. Deliveries are $400 for each wholesale contract. Prices are compared to the cent.

The formulas come from the research (`01-businesses-and-products.md` §1 and §5, `03-real-estate-investments.md` §2, `04-employees-operations-demand.md` §4–5). **Not** from the prototype's stand-in. The sample check comes from the brief: Acorn Gifts at 12 2nd Avenue, one register, open 09–21, Normal, satisfaction 80, demand 80, gives **1,459** customers a week, **47** hours held, and a week of **$73,171**. The brief's wages ($20 cashier, $14 cleaner 42 h) are not the pack's, so the test plan states them in `staff`.

## Contract 3 — the API (`backend/shruti/api/routes/ledger.py`)

| Method | Path | What |
|---|---|---|
| GET | `/api/ledger/data` | the pack, read from the volume; 404 "not loaded" when absent. No session read. |
| GET · POST | `/api/ledger/ledgers` | the reader's ledgers · start one `{name, difficulty, custom?, inGameDay?, courses[]}` |
| GET · PUT · DELETE | `/api/ledger/ledgers/{id}` | one ledger, with its businesses and their weeks · rename, difficulty, courses · delete |
| POST | `/api/ledger/ledgers/{id}/businesses` | keep a plan: `{name, plan}` |
| GET · PUT · DELETE | `/api/ledger/businesses/{id}` | `{name, plan, keptPlan, opened, position}` |
| PUT · DELETE | `/api/ledger/businesses/{id}/weeks/{n}` | write or remove one week `{moneyIn, goods?, wages?, rent?, ads?, deliveries?, units?, customers?, note?}` |
| POST | `/api/ledger/ledgers/{id}/weeks/{n}` | the entry grid: `{rows: [{businessId, …lines}]}`; rows without money in are skipped |

A route answers only for the reader's own ledger, and anyone else's is 404. Plans are JSON, checked for shape and size (64 KB at most), not recomputed. A null line means not written, never zero. All routes are free and ungated.

## Contract 4 — the Ledger on stream (`backend/shruti/api/routes/ledger_stream.py`)

Design: `shrutisgametracker/design/design_handoff_ledger_overlays/` (README §1–§8 and A1–A6). Seven overlay kinds, all drawn by `/overlay/ledger?t=` and inside a layout (`/overlay/guide-layout`): `ledger-plate`, `ledger-card`, `ledger-strip`, `ledger-limit`, `ledger-counter`, `ledger-plan-panel` and `ledger-plan-card`. The design's `streamingPlanId` is **not** used. The planner may stream a plan that was never kept, so the ledger stores the live plan itself.

| Method | Path | What |
|---|---|---|
| GET · POST | `/api/ledger/ledgers/{id}/overlays` | this ledger's overlays by kind, theme and motion, never their address · mint `{kind, theme?, motion?, label?, shows?: "" \| "top"}` → `{id, token, path, kind, theme, motion, shows, createdAt, lastSeen}` (the token once) |
| DELETE | `/api/ledger/ledgers/{id}/overlays/{tokenId}` | revoke (a delete) |
| PUT | `/api/ledger/ledgers/{id}/on-screen` | `{businessId \| null}`: only an open business of this ledger (404 otherwise; 422 if it was never opened) |
| PUT · DELETE | `/api/ledger/ledgers/{id}/live` | the *Plan on stream* switch: `{plan, name?, change?: {label, delta}}` overwrites the one live plan · off: cleared at once |

Minting uses the same fair use as every overlay and never charges. The theme defaults to the game's own (`GAME_THEMES`: Big Ambitions → `ledger`). A ledger's overlays are `overlay_token.ledger_id` (ON DELETE CASCADE), so they go with the ledger, and the ledger goes with the account. `GET /ledgers/{id}` now also carries `onScreenBusinessId` and `live` (a bool, never the plan).

**The frame** (`/api/overlay/guide?t=`, polled every second; the unchanged answer reads one row):

```jsonc
{ "kind", "theme", "motion", "version", "shows",
  "element": {
    "company": "Acorn Holdings", "game": {"version": "1.0", "build": "3682"},
    "ctx": {"difficulty", "courses", "custom"},                  // so the browser reckons with the engine
    // the five business kinds:
    "businesses": [{"id", "name", "neighbourhood", "week": 6, "total": 72880}],   // open only, ledger order
    "week": {"n": 6, "total": 101580} | null,                   // the latest week any open business wrote
    "onScreen": id | null, "onScreenPlan": {engine keys only} | null,
    // the two plan kinds, instead of all of the above but company:
    "live": {"plan": {engine keys only}, "name", "change": {"label", "delta"} | null, "updatedAt"} | null } }
```

A week's total is money in minus the lines written. It is never cash, a note, an unopened plan, another ledger, or where a week came from. Plans are cut to the engine's keys (`PLAN_KEYS`). The words and the change sentences (A2) are in `frontend/site/src/lib/ledger/stream.ts`. The planner builds `{label, delta}` with `changeLabel()` and its own reckoning.

## Contract 5 — the Ledger reckoned for the app (`POST /ledger/reckon.json`)

The Squirrel Guides app is native and cannot run the engine, and the figures must never differ between the phone, the website and the stream. So the Astro server runs the same engine for it. It is an Astro route because the engine is TypeScript and Caddy sends `/api/*` to Python: `frontend/site/src/pages/ledger/reckon.json.ts`, with the handler in `lib/ledger/reckon.ts` (`reckonRoute`). Tests: `frontend/site/test/ledger-reckon-endpoint.test.mjs`.

**Request** (`content-type: application/json`, anything else is 415; 1 MB at most):

```jsonc
// one plan: the lighter planner after each change, a business's week against its plan
{ "plan": {engine keys},                        // 64 KB at most, hours 7 × 24 of 0–9, as the backend checks a plan
  "ctx": { "difficulty": "normal", "courses": [], "custom": {…}?, "importIndex": 0.9? },   // the ledger's
  "previous": {engine keys}? }                   // the plan before the change: adds `change`
// a company's rows: up to 50, answered in the order sent (the ledger's order; never sorted)
{ "plans": [{ "id": 12, "plan": {…} }, …], "ctx": {…} }
```

**Answer** (200; `Cache-Control: no-store`). Money is rounded to the dollar and payback to a tenth of a day, as the headlines are. `honesty` is `counted | approximate | not-counted`. A null value is a dash, never $0.

```jsonc
{ "game": { "version": "1.0", "build": "3682" },
  "state": "ok",                         // the engine's: ok · no-type · no-building · not-a-shop · cannot-open · closed · no-customers
  "week": { "moneyIn": {"value": 93561, "honesty": "approximate"}, "goods": {…}, "wages": {…}, "rent": {…},
            "ads": {…}, "deliveries": {…}, "total": {"value": 73171, "honesty": "approximate", "loss": false} },
  "setup": {"value": 28090, "honesty": "counted"},
  "paybackDays": {"value": 2.7, "honesty": "approximate"},
  "customers": {"value": 1459, "honesty": "approximate"},       // a week
  "limit": { "state": "held", "reason": null, "by": "registers", "hours": 47, "cap": 20, "would": 30,
             "fix": { "kind": "register", "label": "Add a second register", "note": "You can undo it, and Review shows before against after.",
                      "cost": {"value": 1370, …}, "weeklyCost": {"value": 1680, …}, "worth": {"value": 12845, …} } | null,
             "sentence": "Held at 20 customers an hour by one register, for 47 hours of the week. 30 would come. A second register ($1,370 with its cabinet) and a cashier ($1,680 a week) are worth $12,845 a week.",
             "first": "Held at 20 customers an hour by one register, for 47 hours of the week.",
             "note": "held · 47 h", "head": "Registers" },
  "missing": [{ "path": "fixtures · cash register", "text": "A gift shop needs a cash register or a checkout counter to open. Add one under Fixtures." }],
  "bar": { "week": "$73,171", "loss": null, "payback": "2.7 days", "limit": "Registers" },   // the figures bar, as the site writes it
  "change": { "label": "A second register", "delta": 12845, "sentence": "A second register · the week +$12,845", "caret": "▲" } }
  // `change` only when `previous` was sent; null when the two plans are the same
// a batch: { "game", "results": [{ "id": 12, …the same keys, without change… }] }
//          a row the engine cannot read at all is { "id", "state": null, "unreadable": true }
```

**The words are the website's.** The sentences go through the same helpers and the same `copy()` scopes as the pages, so an edit in the admin reads the same everywhere. `limit.sentence`, `note`, `head` and `fix.label` use `limit.ts` in the words of `component:WhatLimitsIt`. `limit.first` is `kept.ts firstSentence`, as a company's rows show it. `missing` is `limit.ts missingRows` in `ledger/plan`'s words. `change` is `stream.ts changeLabel` (with `component:StreamSwitch`'s `stream.ch*` labels) and `changeLine`, as the planner's switch sends it and the overlay prints it. `bar` uses `component:LedgerStats`' `unit.days` and `loss`.

**Refusals** are `{detail}` in plain words: 400 (not JSON), 413 (a plan past 64 KB, a body past 1 MB, more than 50 plans), 415 (not `application/json`), 422 (a shape the backend would refuse), 405 (not POST). **503** means the game's data is not loaded, and the answer says so in a sentence (`Retry-After: 60`). The pack is `loadPack()`'s, kept for a minute.

**Why it needs no session and no CSRF token.** It reads nothing about anybody and writes nothing. The plan arrives in the body, and the answer is arithmetic on it and the game's facts. No cookie is read. A cross-site page cannot make a browser send it anyway: `application/json` is not a simple content type, so the browser asks for a preflight, which this route never grants, and a simple `text/plain` POST is refused with 415. The app is native, so it sends no Origin and needs no CORS. None is sent, and in particular no wildcard. Astro's `checkOrigin` is off site-wide (see `astro.config.mjs`), and the site's own CSRF check is the double-submit token that forms carry. Neither applies to this route. The middleware skips it too, and mints no CSRF cookie for it.

**Section.** It is in the guides section (`SECTION_PATHS["/ledger"]`). Hidden with the section, it is a JSON 404 (`{"detail":"Not found"}`), except for the operator. The holding page does not swallow it, just as it does not swallow `/api/*`. `SECTION_MACHINES` in `middleware.ts` names it.

**For the app.** The app needs a connection to plan. When the answer does not arrive, show the last one and say that it is the last known; the endpoint keeps nothing. The address is on the site's origin (`https://shrutivtuber.com/ledger/reckon.json`), not under `/api/`. A self-hosted tracker has no Ledger and answers 404 here. The app reads its plans and ctx from Contract 3 (`GET /api/ledger/ledgers/{id}`: `keptPlan` else `plan`, and the ledger's `difficulty`, `courses`, `custom`) and posts them here.

## Next — the plan on stream (after the backend lands; design in `design/requests/ledger-overlays-addendum-plan-on-stream.md`)

Shruti plans on an iPad while chat watches an overlay. The planner's **Plan on stream** switch sends the working plan to the server as a live draft, a moment after each change. An overlay of kind `ledger-plan` polls for it, like every other overlay (about 2 s), and reckons it **with the same engine** in the browser source, so the two never disagree.

- `PUT /api/ledger/ledgers/{id}/live`: `{plan, name?, lastChange?: {path, from, to}}`. Debounced from the planner; one live plan per ledger, overwritten.
- `DELETE /api/ledger/ledgers/{id}/live`: the switch off; the overlay goes to its empty state at once.
- The overlay reads it through its token (`/api/overlay/…?t=`), never through a session. The token names the ledger and its kind. It never carries cash, notes or other businesses.
- Opt-in only. Signed out, the switch explains itself and does nothing.
