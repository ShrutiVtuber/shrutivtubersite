# Handoff — station trackers and Day at a Glance

**Prepared for:** the implementing developer agent
**Source:** `brief/DESIGN_HANDOFF_02_stations.md`
**Date:** 2026-08-24
**Design system:** Shruti (this repository)

---

## 0. The mandate

**Implement the design. Do not interpret it.** Reproduce these three screens exactly, then plug real
ephemeris computation in behind them. `INSTRUCTIONS_FOR_DEVELOPER_AGENT.md` has the short form.

Read `../design_handoff_shrutivtuber/README.md` first — it carries the tokens, chrome, component
library and the seven tool pages, and everything here assumes it. Handoff 03's pack
(`../design_handoff_accounts/`) covers accounts, horoscopes and the newsletter.

**Build order matters.** These three pages come **first**, before anything in handoff 03. They need
no account, they carry no personal data beyond a location someone types, and they are what makes the
site worth returning to before there is anything to sign up for. Everything designed before them is
a brochure someone reads once; these are instruments someone uses.

**The design system does not change for these pages.** Tokens, components, Dawn/Dusk, the tradition
toggle, the cannot-compute grammar — all as built.

---

## 1. What is in this pack

| Surface | Route | Where |
|---|---|---|
| Solar stations | `/tools/solar-stations` | `ui_kits/site/Stations.jsx` (`kind="solar"`) |
| Lunar stations | `/tools/lunar-stations` | `ui_kits/site/Stations.jsx` (`kind="lunar"`) |
| Day at a Glance | `/today` | `ui_kits/site/Today.jsx` |

Four new pieces of the design system, with `.d.ts` contracts, `.prompt.md` notes and a specimen card
at `components/tables/stations.card.html`:

| Piece | Where | Why it exists |
|---|---|---|
| `NextStation` | `components/tables/` | The countdown. Reused on all three pages. |
| `StationTable` | `components/tables/` | Days down, stations across. Prints. Absent cells are the sky, not a gap. |
| `ExportBlock` | `components/tables/` | Three export routes that are not equivalent. |
| `tokens/print.css` | `tokens/` | Print is a designed medium here, not an afterthought. |

Reference build: `ui_kits/site/index.html`. The demo bar bottom-right carries **athens / polar** on
all three routes and **has birth time / no birth time** on `/today` when signed in — those drive the
cannot-compute states.

---

## 2. Solar stations

Someone enters a location and a period of **up to one month**, and gets four station times for every
day in it, exportable to their calendar.

The four stations are the structural skeleton of a daily rite: **sunrise · noon · sunset ·
midnight**. In Thelemic practice they are the Liber Resh adorations; in the Hellenic set they are
Hekate Phosphoros at dawn, Apollo at noon, Hekate Enodia at dusk, Persephone at night. **The tool
computes the times. Which deity belongs to which station is a preset the visitor may choose or
ignore** — Hellenic, Thelemic, or "none — times only". Never assume a tradition.

Built into the design:

- **Location control** — typed place or "use my location", and **the resolved coordinates and
  timezone are shown back**, with the reason: *a station table for the wrong city is
  indistinguishable from a right one until someone misses a dawn.*
- **Range control**, one day to one month. **The cap is stated in the UI** — "One month is the cap —
  ask for more and it is refused, not quietly trimmed." Do not silently truncate.
- **The table** — the primary reading, and it gets printed.
- **The current or next station called out above it.** Someone opening this at four in the afternoon
  wants "sunset in 2h 14m" before they want thirty rows.
- **Export as three distinct things** (§4).

## 3. Lunar stations

The same page for **moonrise · culmination · moonset · nadir**, plus the Moon's **phase and age** in
its own column — anyone tracking lunar stations cares about both.

**The one difference that must be designed for rather than treated as an error:** the Moon does not
rise every day. It rises roughly fifty minutes later each day and occasionally skips a civil day
entirely; at high latitude whole weeks can lack a moonrise or a moonset.

**A blank cell is wrong.** The cell reads **"no moonrise today"** in italic at `--ink-faint` — a
designed state, because it is a fact about the sky and not missing data. `StationTable` takes `null`
in the `times` array and renders `absentLabel`. The page also carries a line under the table
explaining why, so nobody files a bug.

---

## 4. The export block — three routes, one hierarchy

These are **not equivalent**, and making the difference legible before someone picks wrong is the
whole design job:

| Route | What it really is | Prominence in the design |
|---|---|---|
| **Subscribable feed** (`webcal:`) | Stays correct as the year turns. **The only one that produces notifications.** | Primary: own card, `--line-strong`, rose `stays correct · notifies` tag, accent button, URL shown in mono with a copy control |
| **`.ics` download** | A snapshot of the range shown | Secondary: outline button. Body copy says **"it will go stale"** |
| **Google Calendar links** | One event, one station | Tertiary: pills, one per station |

The feed is the one that creates the habit, so it gets the prominence. The download's staleness is
stated at the point of choice on purpose: someone who exports in September and finds wrong times in
March will blame the tool, not the snapshot.

**Do not reorder these by visual balance. The hierarchy is the information.**

`meta` must name everything that changes the output — place, preset, timezone. A feed URL without
those is not reproducible.

---

## 5. Day at a Glance — `/today`

The page most likely to be someone's daily open. **One screen, no scrolling on a laptop**, answering:
*what is the sky doing right now, here.*

Six blocks, in this weight order:

1. **Sun and Moon** — sign and degree of each, right now, in both zodiacs. The Moon moves visibly
   over a day and the Sun does not, so the Moon carries its daily motion and a progress rule through
   its current sign.
2. **Stations** — the solar and lunar station in force, the next with a countdown, and links to both
   trackers.
3. **Planetary hour — current and next.** Ruler, when it began, when it ends. **The "next" half is
   the point** — people plan against the coming hour, not the present one — so it carries a rose
   "plan against this" badge.
4. **The sky over their location** — the visible chart for here and now. An art-absent sky plate in
   the design; implement as a real rendered SVG.
5. **Transits** — only with a saved nativity. See §5.1.
6. **Today's date in every reckoning kept** — Gregorian, Attic, Hindu, Thelemic, each linking to the
   instrument that reckons it with the rule it used.

### 5.1 The two states, and the first one matters more

**Without an account**, entering a location gives everything except transits, and **this must be
genuinely useful on its own — if the page is a teaser for signing up, nobody signs up.**

The signed-out transits block is therefore **a quiet, honest invitation, not a locked panel with a
blur over it.** Its copy: *"Everything else on this page works without an account, and always will.
This one block needs to know where you were born — nothing else does."* followed by *"No account? The
page above is the whole page. This is an invitation, not a wall."*

**Do not** add a blur, a lock icon, a fake preview, a count of what they are missing, or a modal.

**With a saved nativity**, the block fills in with planetary transits.

### 5.2 Cannot-compute states, all real and all reachable in the reference build

- **Polar latitude** — no sunrise, so no solar stations and **no planetary hours** (the hours divide
  sunrise to sunset; with no sunrise there is nothing to divide). The page still shows Sun, Moon, sky
  and reckonings. Both tracker pages carry the matching whole-table state.
- **No moonrise today** — per §3.
- **No birth time** — transits to the angles and houses are undefined, because the ascendant moves a
  degree every four minutes. **Show the planetary transits and mark the angular ones undefined.**
  **Never guess a time.** The design shows the three planetary transits, then a `◐ Angular transits
  undefined` block explaining why, with a link to add a birth time.

---

## 6. Printing

`tokens/print.css` owns the medium — **do not write page-break or print CSS in the pages.** It:

- forces Dawn on paper whatever the screen theme is, and flattens all shadows;
- drops chrome, controls, the demo bar, `.export-block` and anything `.no-print`;
- prints a sky panel as a ruled block rather than a grey wash that eats toner;
- repeats `thead` per page (`display: table-header-group`) and keeps rows `break-inside: avoid`;
- prints the destination of real links once, small, after the text;
- sets `@page { margin: 14mm }`.

The station table is designed to be **read on a phone, outdoors, at dawn, in poor light**: times are
mono, tabular and larger than surrounding body text, and in dusk they use `--ink`, never
`--ink-soft`. **The dark theme matters more than usual on these pages** — check it first, not last.

---

## 7. What already exists behind this

| Endpoint | What it returns |
|---|---|
| `GET /today` | luminaries in both zodiacs, stations with countdowns, current **and next** planetary hour, sky, every reckoning, transits when a nativity is given |
| `GET /stations`, `/stations/next`, `/stations/ical` | four daily stations, up to a month, subscribable feed |
| `GET /chart` | full natal chart, both traditions, SVG figure |

`/today` already accepts an optional nativity, so **the signed-out and signed-in states differ by
parameters, not by a different page.** Build them as one page.

---

## 8. Please do not

- Leave a blank cell where a station does not occur.
- Silently truncate a range longer than a month.
- Blur, lock or tease the signed-out transits block.
- Guess a birth time, or a location.
- Show a zeroed countdown at polar latitude instead of the designed "nothing to count to" state.
- Give the `.ics` download the prominence that belongs to the feed.
- Write print CSS in the pages.
- Assume a tradition — the preset defaults to Hellenic in the demo but "none — times only" is a
  first-class choice.

## 9. Files

```
<project root>/
├── design_handoff_stations/                 ← this pack
│   ├── README.md
│   ├── INSTRUCTIONS_FOR_DEVELOPER_AGENT.md
│   └── brief/DESIGN_HANDOFF_02_stations.md
├── design_handoff_shrutivtuber/             ← the first pack: read it first
├── design_handoff_accounts/                 ← handoff 03: build after these three pages
├── components/tables/                       ← NextStation · StationTable · ExportBlock + specimen card
├── ui_kits/site/Stations.jsx, Today.jsx
└── styles.css, tokens/ (incl. print.css)
```

Everything opens and runs offline with no setup. Start at `ui_kits/site/index.html`, go to
**Today** in the nav, and use the demo bar's **athens / polar** and **birth time** toggles.
