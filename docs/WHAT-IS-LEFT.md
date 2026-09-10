# What is left

Written 10 September 2026. Everything she has asked for across this work is
built, tested and deployed unless it appears below.

Ordered the way she said she wanted to do it: **the wheel, then the design
hand-off, then the three setup tasks.**

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

## 2. The design hand-off — ready

Two documents, handed over together:

- `docs/DESIGN-BRIEF-ASTROLABE.md` — direction, audience, constraints.
- `docs/DESIGN-BRIEF-ASTROLABE-ADDENDUM.md` — ⚠ **the scope is the whole app**:
  eighteen screens, nine states each, the component system, motion, and the
  artwork in the shape she needs in order to start drawing.

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
- **The app ships the default Flutter icon.** The design brief covers it; until
  then it is the one thing that will make it look unfinished on a home screen.
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
- **Five site tools are not in the app**: the Attic calendar, the Hindu
  calendar, the Pañcāṅga, the ephemeris page and the geomantic shield. Nobody
  asked for them; they are a day's work each if she wants them.
