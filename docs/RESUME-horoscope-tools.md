# Resume note — the horoscope toolset, 7 September 2026

Written because context was filling. If you are picking this up cold, read
`docs/HOROSCOPE_TOOLS.md` first — it holds every decision and why — then this.

## In one paragraph

The toolset from `horoscope-tools-spec-v2.md` is built and deployed except for
four items listed at the bottom. Two repositories: the engine is
**`shruti-astro`** (public, AGPL, `/srv/shruti-astro/prod`, loopback 8201), the
pages are here. The brief was written by an agent that had not seen this
project and got several things wrong about it; those are all recorded in
`HOROSCOPE_TOOLS.md` with the reasoning, and should not be reopened.

## Settled, do not reopen

- **No separate application.** The brief wanted one for licensing reasons that
  do not exist — this site is already AGPL-3.0-only.
- **No i18n.** Not wanted.
- **No Swiss Ephemeris in the browser.** The server samples a span of
  longitudes and the client interpolates. Measured against real charts with the
  exact code the browser runs: **worst error 0.004 arcseconds**, a few kilobytes
  a week. This deletes the brief's second implementation and its CI fixture.
- **Tokens carry the instant, not an event id.** `{{instant:…Z}}`, not
  `{{event:<id>}}`. An id derived from a computed instant breaks when the
  ephemeris is recomputed; an instant cannot.
- **Bounds are Egyptian only.** Her decision, 7 September. The Ptolemaic toggle
  is dropped, not deferred — do not add it without a table she has supplied and
  that passes Ptolemy's own per-planet totals (Saturn 57, Jupiter 79, Mars 66,
  Venus 82, Mercury 76).
- **Periods are daily, weekly, monthly, yearly.** Weeks are ISO-8601, id
  `2026-W38`, and that id is the database key and the URL.
- **Void of course defaults to kenodromia** (`thirtyDegrees`), which is what the
  daemon already used. `signExit` is the alternative.
- **Solar phase defaults to Paulus** (1° / 7° / 15°), not Lilly.

## What exists

**Engine** (`shruti-astro`) — `core/events.py` (ingresses, stations, lunations,
eclipses, perfections, void windows, all root-found to the second),
`core/tables.py` (the almanac page, the interpolation table). Endpoints
`/events`, `/ephemeris`, `/positions`. 33 tests of its own, 362 in the suite.

**Pages** — `/tools/ephemeris` (the printed-ephemeris replacement),
`/tools/events` (the event table, twelve rotations, wheel, stepping, exports,
embed snippet), `/admin/horoscopes` (the writing desk), `/overlay/wheel` (the
seventh OBS surface), `/embed/wheel`.

**Components** — `chart/TransitWheel.astro`, `chart/WheelStepper.astro`,
`chart/WheelExport.astro`, `content/LocalTimes.astro`, `lib/tokens.ts`.

## Traps found the hard way — all fixed, all pinned by tests

1. `/void-of-course` could not see an **opposition** at all. The separation
   folds at ±180, so the sign-change test watched −0.1 become −359.9. The Moon
   was reported void with an opposition still to perfect.
2. **Two wheels drew the zodiac backwards.** `180 - lon` mirrors it. Both files
   carried a comment saying "anticlockwise" above the line doing the opposite.
3. **`SIGNS` in `lib/signs.ts` is NOT zodiacal** — it runs Capricorn-first for
   the calendar-month lookup. Indexing it as though it began at Aries drew a
   Leo reading as Scorpio. Use `ZODIAC`.
4. **A migration passed locally because it never ran** — its idempotence guard
   skipped the insert on the only database that had the rows already. Five
   NOT NULL columns were missing. Downgrade, check, upgrade is the only test
   that means anything.
5. **Period ranges were closed, not half-open**, dropping the last day.
6. `import.meta.env` is **build-time**; the deployed commit is not knowable
   then. Everything configurable goes through `lib/env.ts`.
7. A test grepping for a forbidden string keeps matching the comment that
   explains why it is forbidden. Strip comments first — `code_of` in the test
   files.

## Deploying

Both profiles, every time, or the site and bot silently keep old code:

```bash
cd /srv/shrutivtuber/prod
git pull --ff-only
export SHRUTI_SOURCE_SHA=$(git rev-parse HEAD)
dc --profile web --profile bot up -d --build
dc exec -T backend alembic upgrade head
```

The **engine deploys separately**: `/srv/shruti-astro/prod`, same pattern.

A change to the public CSP needs `deploy/shrutivtuber.caddy` copied to
`/etc/caddy/Caddyfile.d/` and `systemctl reload caddy` — diff first, and do not
run `caddy validate` by hand. See `docs/DEPLOY.md`.

## Left to do

1. `/horoscopes/<sign>/<period>/<id>` as the canonical URL shape. Today the
   period id is a query parameter. **Production has zero published horoscopes,
   so this is still free.**
2. An **oEmbed** endpoint, so a pasted link expands in Discord or WordPress.
3. **Per-sign feeds**, RSS and JSON.
4. The **OG image** endpoint — a shared horoscope previewing with its own wheel.

Then: she reviews the writing desk in one pass and I fix what is awkward. She
asked specifically that the desk not be iterated on before the rest was
finished, to avoid fixing the same thing twice.
