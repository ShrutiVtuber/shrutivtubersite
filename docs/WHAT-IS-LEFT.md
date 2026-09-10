# What is left

Written 10 September 2026, updated the same night after the design system came
back. Everything she has asked for across this work is built, tested and
deployed unless it appears below.

⚠ **The Astrolabe design system is in and implemented.** It arrived as a zip,
is unpacked at `design/astrolabe/`, and the app has been rebuilt on it —
foundations, brand layer, every screen, and the motion. See §2.

---

## 1. The period wheel — done, and where it might still go

Rebuilt on the transit wheel's geometry after the first attempt came out
smaller, fainter and unfinished-looking. What it now does:

- each body on its own band, **colour-coded**, from where it starts to where it
  ends, with a hollow mark at the start and its glyph at the end
- a tick where it crosses a sign, a marked station where it turns (℞ or D)
- **the Moon answered twice**, as she asked: its glyph on a track so its SIGN
  reads like everything else's, and the **inner ring as a clock of the period's
  days** — one drawn phase disc per day, so the waxing and waning is a shape
  taken in at a glance
- glyphs nudged apart along their own tracks where two bands end at the same
  longitude, with a leader line so a nudge never lies about a position

⚠ Two things a designer should look at, not me:

- **February is honest but cramped.** When every planet is in Aquarius, every
  track is a short arc in one corner. That is what the sky did; whether it
  should be drawn that way is a design question.
- **The inner ring is TIME and the outer is LONGITUDE.** Two angular meanings
  in one figure. It is labelled, but it is the kind of thing a designer should
  either make obvious or change.

Fixed on the way, and worth knowing: **the sector lines on every wheel on this
site were invisible.** An SVG `<line>` defaults to `stroke: none`, and the CSS
set only a width and an opacity. Nobody noticed because a wheel without sector
lines still looks like a wheel.

## 2. The design system — delivered, and built

The two briefs went out and came back as a full system. It is unpacked at
`design/astrolabe/` — tokens, thirty-three components, twenty-one foundation
cards, a Flutter theme mapping, a UI kit of every screen in every state, and an
artwork spec with exact dimensions.

**What is now in the app:**

- the gilt layer and the cloak's two flats; seven hour tints
- the four motifs — the hem, the star scatter, the rule, the veil — and the
  plate, which is the ONE brand-coloured surface in the app
- the ruling planetary hour, computed on device and scheduled to the hour's own
  end rather than polled, tinting exactly two things
- live as a shell state that re-points the ornament colour, so one hairline
  says both what hour it is and whether she is streaming
- the whole component set: card in four tones, list rows and groups, chips in
  three kinds, buttons, fields, switches, choice rows, the dense reference
  table, the almanac's dotted fact row, content and work and offer cards, the
  vote control, prose with a gilt drop capital, empty states, notices,
  skeletons
- every screen rebuilt to the kit's structure, and the sky drawer that was
  missing entirely — a month of ephemeris, retrogrades marked, the month drawn
- the motion: 240 ms push from the right, a cross-fade between tabs, and
  everything collapsing to a millisecond under reduced motion

**Three defects the work turned up, all fixed:**

- ⚠ **The zodiac marks were rendering as colour emoji** — the ephemeris table
  came back as a grid of green and orange circles. Commissioner has no ♈, so
  the platform fell through to the emoji font, which ignores `color`. Fixed
  with AstroSymbols in every fallback stack, and a test that reads the source
  for it.
- ⚠ **A hang that killed the app.** The dotted leader loops across its own
  width; handed an unbounded width it never ends, and Android kills the
  process. Found by three integration tests "not completing".
- ⚠ **`liveStatus()` reported OFFLINE when the site was unreachable** — telling
  the people who care most that she is not streaming, several times a week,
  whenever the network hiccuped. It now has a third state and says so.

**Still hers to answer, from the spec:**

- ⚠ `guidelines/artwork-spec.md` lists twelve drawings in priority order, with
  canvas sizes, safe areas and transparency. **Six are essential**, and the
  Home portrait is called the highest-leverage drawing in the project.
- The wordmark needs a night re-cut. The current one is the WordPress-era
  pink-and-blue with hearts and it does not sit on `#121829`.
- The licence question is **answered and in the repository**: code AGPL,
  artwork © Shruti all rights reserved. `ASSETS-LICENCE` in the app repo, a
  sentence in its readme, a README beside the drawings.

## 3. The three setup tasks — hers

`docs/SETUP-THREE-THINGS.md` walks through them. Firebase (~15 min), the
Discord MESSAGE_CONTENT intent (~5 min), and casting and keeping her own chart
so `/compatible-with/shruti` has something behind it (~2 min).

⚠ All three features are built and dormant. Unconfigured is a working state in
every case — nothing errors, nothing 500s, they are simply quiet.

## 4. Known gaps, honestly

Not asked for, but real, and better said than discovered:

- **No iOS build.** Android only. iOS needs an Apple developer account, APNs,
  and a pass over anything that assumes Android.
- **The launcher icon is a stand-in.** No longer Flutter's blue logo: an
  adaptive icon in two layers, a crescent and an eight-pointed star built from
  geometry in gilt on the cloak's navy. ⚠ The artwork spec reserves this for
  her to draw — when the clasp arrives it is a file swap, because the XML
  already points at the right names.
- **The site is still behind the holding page.** A switch, not work.
- **Nobody outside has used any of it.** No stranger has written a practice
  reading, redeemed an offer, or received a notification. The tests say the
  parts work; they cannot say the thing is good. ⚠ Ten people from the Discord
  before a public launch would be worth more than another week of building.
- **Two compliance decisions are hers**: whether an age gate is needed, and
  whether the terms want a line about user content now that people post writing
  others read. See `LAUNCH-READINESS.md`.

## 5. Things deliberately not built

Named so nobody wonders whether they were forgotten:

- **The Discord bridge's inbound half runs but is not started.** It waits on
  the intent; the outbound half works today.
- **`_registrationToken()` in the app returns null.** The five lines that
  replace it are written in the comment above it. The app is deliberately not
  built against `firebase_messaging` yet, because adding the plugin without a
  `google-services.json` does not compile and would leave the app un-buildable.
- **Lunar stations are not in the app.** Her instruction: solar adorations, no
  lunar.
- **No tablet layout**, and the design system says it should stay that way:
  every instrument is a single column of dense figures, so a two-pane layout
  would be a different information design rather than a wider version of this
  one.
- **Five site tools are not in the app**: the Attic calendar, the Hindu
  calendar, the Pañcāṅga, the ephemeris page and the geomantic shield. Nobody
  asked for them; they are a day's work each if she wants them.
