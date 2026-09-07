# The horoscope toolset — decisions and state

Built from `horoscope-tools-spec-v2.md`, which was written by an agent that had
not seen this project. Where the brief and the codebase disagreed, the codebase
usually won; every such decision is recorded here with the reason, so none of
them has to be argued twice.

**Two repositories.** The engine is `shruti-astro` (public, AGPL-3.0-only,
`/srv/shruti-astro/prod`, loopback 8201). The pages are here. That split already
existed and is the real boundary — not the separate application the brief
proposed, which was solving a licensing problem that does not exist.

---

## What the brief got wrong about this project

| Brief said | Actually |
|---|---|
| Deploy as a separate app, own repo, do not import AGPL into the main site | **This site is already AGPL-3.0-only.** There is no copyleft boundary to protect, and separating would duplicate auth, the copy system, the admin and the sitemap for nothing. |
| English and Greek from the start | Dropped. Not wanted. |
| Build the dignity, sect, lots and aspect engine | Mostly built already. `/chart` returns whole-sign places with rulers, sect, full essential dignity including bounds and triplicity, seven lots, configurations and a rendered wheel. |
| Implement both traditions with a labelled toggle | That is `/doctrine` plus `DisagreementControl`, which is the site's house pattern already. |
| Void of course: traditional (sign-exit) default | The daemon's default is **kenodromia** — no exact configuration within the Moon's next thirty degrees. Both exist; kenodromia stays the default because it is what the site already says. |
| Cazimi 17′ / combust 8° / under beams 15° | Those are Lilly's. The daemon's default is **Paulus, 1° / 7° / 15°**. Kept, with Lilly and the medieval set available. |
| Swiss Ephemeris in the browser as WebAssembly, plus a CI fixture proving client and server agree to 1″ | **Not doing this.** See below. |
| Event IDs as content hashes | Allocate on first reference and store, so a recomputation cannot break published text. |
| Flag events within 1 hour of a period boundary | Too narrow. Readers span UTC−11 to UTC+14; for anyone anchoring to local dates the window is about 26 hours. |
| Lots need a sign-level fallback when no location is active | The resolution chain always ends at Greenwich, so no location is never the case. Compute properly, label the provenance. |
| `/wheel` | `/tools/wheel`, matching the site's own IA, with `/wheel` redirecting. |
| `?mode=stream` | Reuse `/overlay/*`, which already works in OBS with token addressing and the CSP sorted. |

**Stations means two things.** The brief uses it for retrograde turns; this site
already uses it for risings and settings, with a live tool and an iCal feed. In
the event table the retrograde ones are written out in words — "Mercury stations
retrograde" — so the collision never reaches a reader.

---

## The one architectural change worth the argument

The brief wanted Swiss Ephemeris compiled to WebAssembly in a worker, a second
server implementation, and continuous integration proving the two agree to one
arcsecond. That is megabytes on every reader's connection and two
implementations to keep honest, bought to make a wheel step smoothly.

Instead the server samples a **dense position table** and the client
interpolates between nodes — Moon hourly, Mercury and Venus twice daily,
everything else daily.

Measured over three hundred random instants per body across a month:

```
Moon 0.007″   Mercury 0.104″   Venus 0.192″   Mars 0.060″
Sun  0.047″   Jupiter 0.042″   Saturn 0.070″  outers under 0.03″
```

Worst case **0.192 arcseconds**, five times inside the tolerance the brief set
for its alternative, at **8.6 KB per month** with the outer planets included.
One implementation, so there is nothing to disagree. This deletes acceptance
criterion 12 and most of phase 3.

---

## Done

**Engine** (`shruti-astro`, committed)

- `core/events.py` — ingresses both directions, stations, lunations, eclipses,
  exact configurations, void windows under both rules. Every instant
  root-found, reported to the second.
- `core/tables.py` — the almanac page and the interpolation table.
- `/events`, `/ephemeris`, `/positions` endpoints.
- 33 tests, checked against facts from outside the codebase: the March 2026
  equinox to the minute, all four 2026 eclipses by date and type, twelve solar
  ingresses a year, Mercury's three retrogrades, sidereal time gaining 3m56s a
  day. Full daemon suite 362 passing.

**A bug this work found in live code.** `/void-of-course` could not see an
opposition at all — the separation folds at ±180, so the sign-change test
watched −0.1 become −359.9 and found nothing. The Moon was being reported void
while she still had an opposition to perfect, which is an error in the one
direction that reading must never make. Fixed and pinned.

**Performance.** Perfections were making about fifty thousand ephemeris calls
for a month, asking for the same longitudes once per pair per target per
sample. They now scan one precomputed grid: 8.6s to 0.31s, and a month of every
event type in 1.3s.

**Pages** (this repo)

- `/tools/ephemeris` — a month as a printed page. Column per body, row per day,
  degrees and minutes, retrograde marked, declination and out-of-bounds behind
  a toggle, the day's ingresses and stations in the margin. Midnight or noon UT,
  named on the page, because Raphael's is noon and the Moon is seven degrees
  apart between them. Server-rendered; works with scripting off; prints.
- `/tools/events` — every moment in a day, ISO week, month or year, with the
  twelve sign rotations. Switching rotation recomputes only the whole-sign
  house, never the positions. Aversion marked, because a planet in the 2nd,
  6th, 8th or 12th cannot see the rising sign and that changes what gets
  written.

---

## Next, in order

1. ~~The wheel~~ — **done.** `components/chart/TransitWheel.astro`, drawn on the
   server, whole-sign, sign-rotated, degree ring, house numbers, aversion
   marked, deterministic glyph spreading with leader lines, and the rising
   sign's ruler and house called out in words. Wired into `/tools/events`.
2. **Stepping** — client interpolation over `/positions`, snap-to-event. The
   endpoint and the accuracy are already proven; what is left is the browser
   side: read the table, interpolate, repaint, and the keyboard scheme.
3. ~~The writing desk~~ — **done.** `/admin/horoscopes`. Sign rail showing
   which of the twelve are written, events and wheel rotated to the sign being
   written for, click-to-insert, autosave on a pause, ⌘/Ctrl + arrows to move
   sign and S to save, an unsaved-work warning, and publish that stays disabled
   until all twelve exist. Works with scripting off. **The token layer
   (`{{event:…}}`) is not built yet** — that is what makes the prose itself
   shift with the reader's timezone, and it is the next thing.
4. ~~Periods~~ — **done.** daily · weekly · monthly · yearly, weeks ISO-8601
   with `2026-W38` as the key. `covers` is validated per period, because an
   unchecked typo saved a row that never appeared in the list it was meant for.
   Still to do: the public `/horoscopes/<sign>/<period>/<id>` URL shape.
5. **Bounds** — Egyptian ⇄ Ptolemaic. **Blocked on you, deliberately.**

   The daemon computes Egyptian bounds and does not offer a choice. Adding the
   toggle is half an hour; the table is the problem. I wrote out Ptolemy's
   terms from memory and checked them against the per-planet totals he gives
   in the *Tetrabiblos* — Saturn 57, Jupiter 79, Mars 66, Venus 82, Mercury 76,
   summing to 360. Mine came out **Venus 83 and Mercury 75**: one degree
   misplaced between them, in a sign I cannot identify without the text.

   Structurally it was sound — five distinct planets per sign, every sign
   ending at 30 — which is exactly what makes it dangerous. It would have
   looked right in every dignity readout on the site and been wrong for one
   degree of the zodiac.

   §12.2 rules out copying a table off astrology software or a website, and
   that is the correct rule. So this needs the reading YOU use — Robbins,
   Schmidt, whichever edition you work from — and then it is quick.

   The validator is worth having either way: any table that goes in should be
   checked for five distinct planets per sign, every sign closing at 30, and
   the published per-planet totals.
6. ~~Stream overlay~~ — **done.** `/overlay/wheel`, the seventh, sharing the
   component rather than redrawing it. Transparent by default, key colour on
   request, everything in the URL for an OBS scene.
7. ~~Embed~~ — **done.** `/embed/wheel` with a copy-paste snippet on the tool.
   `/embed/*` is the one path where `frame-ancestors` is opened; everything
   else stays `'self'` and the admin `'none'`.
8. ~~Exports~~ — **done.** CSV, Markdown and JSON off the event table, SVG and
   PNG off the wheel.

**Left, and worth doing next:** the horoscope URL shape
(`/horoscopes/<sign>/<period>/<id>`), an oEmbed endpoint, per-sign feeds, and
the OG image endpoint.

## Still open for her

- Whether weekly replaces seasonal or joins it.
- Whether the writing desk's twelve-up screen is one page or twelve tabs — a
  question better answered by pushing a rough one around than by specifying it.


---

## Bugs this work found in code that was already live

Recorded because each was invisible from the outside and each would have been
found later by somebody reading a wrong answer.

1. **`/void-of-course` could not see an opposition at all.** The separation
   folds at ±180, so testing `sep − 180` for a sign change watched −0.1 become
   −359.9 and found nothing. The Moon was reported void while she still had an
   opposition to perfect — wrong in the one direction that reading must never
   be wrong, since its entire claim is "she completes nothing more". The same
   listing also counted 180 and −180 as two oppositions where there is one.

2. **Perfections asked the ephemeris for the same longitudes tens of thousands
   of times.** Once per pair, per aspect, per target, per sample. A month took
   8.6 seconds; it now scans one precomputed grid and takes 0.31.

3. **Period ranges were closed where they should have been half-open.** A month
   ending "2026-09-30" dropped everything on the thirtieth after midnight, and
   a single day was a zero-length span the engine refused — so the day view
   showed nothing and blamed the ephemeris.

4. **`test_every_instrument_page_has_a_row` could not pass for a new
   instrument.** It read one named migration, and you do not edit an applied
   migration — a new tool's row lands in a new one the test was not looking at.
   Widening it naively then swept up projects and link groups, which are not
   tools; and the row-needs-a-page direction has to read only rows seeded
   VISIBLE, because `seed.py` seeds placeholders hidden on purpose. Both
   directions now read the set they actually mean.

5. **Neither new tool page reported its own use**, so both would have read as
   unused on the dashboard for ever. The suite caught it; I had not.
