# The Ledger — how it is built

A business planner and account book for Big Ambitions, inside Squirrel Guides at `/ledger`. Design: `shrutisgametracker/design/design_handoff_ledger/` (README.md and SPEC.md are the spec; `prototype/` is the reference, not code to copy). Game research: `~/Documents/development/bigambitions/research/`.

This page holds the three contracts the parts are built against. Change a contract here first, then in the code.

## Decisions

- **The reckoning runs in the browser.** Every change re-reckons at once (handoff: "no debounce is needed"), and planning works signed out. `frontend/site/src/lib/ledger/engine.ts` is a pure module: no DOM, no fetch. It is tested with `node --test` against figures worked out from the research. The server stores plans and weeks; it does not compute them.
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

The formulas come from the research (`01-businesses-and-products.md` §1 and §5, `03-real-estate-investments.md` §2, `04-employees-operations-demand.md` §4–5). **Not** from the prototype's stand-in. The sample check comes from the brief: Acorn Gifts at 12 2nd Avenue, one register, open 09–21, Normal, satisfaction 80, demand 80, gives **1,459** customers a week, **47** hours held, and a week of **$73,171**.

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

## Next — the plan on stream (after the backend lands; design in `design/requests/ledger-overlays-addendum-plan-on-stream.md`)

Shruti plans on an iPad while chat watches an overlay. The planner's **Plan on stream** switch sends the working plan to the server as a live draft, a moment after each change. An overlay of kind `ledger-plan` polls for it, like every other overlay (about 2 s), and reckons it **with the same engine** in the browser source, so the two never disagree.

- `PUT /api/ledger/ledgers/{id}/live`: `{plan, name?, lastChange?: {path, from, to}}`. Debounced from the planner; one live plan per ledger, overwritten.
- `DELETE /api/ledger/ledgers/{id}/live`: the switch off; the overlay goes to its empty state at once.
- The overlay reads it through its token (`/api/overlay/…?t=`), never through a session. The token names the ledger and its kind. It never carries cash, notes or other businesses.
- Opt-in only. Signed out, the switch explains itself and does nothing.
