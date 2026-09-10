# Design brief — Astrolabe

For the design agent. Written 10 September 2026, after the app was feature
complete and named.

---

## What it is

**Astrolabe** is Shruti's companion app: the free thing her audience installs so
they are never far from her. It is a VTuber's app before it is an astrology app
— the astrology is what it does, but being *hers* is why anyone keeps it.

The site's line is **"Instruments for magick, built live from Athens."** The app
is the pocket version of that.

Live: <https://shrutivtuber.com> · Source: `ShrutiVtuber/astrolabe` (AGPL-3.0)

## Who opens it, and why

Three people, in the order they matter:

1. **A viewer between streams.** Opens it to see if she is live, reads a
   horoscope, taps through to something she has written. This is the majority
   and they never touch an instrument.
2. **Somebody learning astrology.** Uses the practice room — writes a reading,
   puts it in front of others, argues about somebody else's. Comes back weekly.
3. **A practitioner.** Uses the ephemeris, the stations, the planetary hours,
   the chart. Wants density and accuracy, not decoration.

⚠ **The design must serve (1) without insulting (3).** A home screen that is
all sparkle and a stations table that is a wall of numbers can live in the same
app, and should — but they must feel like the same app.

## The screens as they stand

| Tab | What is on it |
|---|---|
| **Home** | Live status · her latest readings · her latest articles · offers · links to the site |
| **Sky** | Stations · planetary hours · what is coming (three segments) |
| **Chart** | Cast a natal chart, wheel and table |
| **Letters** | Isopsephy · sigils (two segments) |
| **Practice** | The community feed: read, vote, comment · write your own |
| **Settings** | Account · notifications · place · sunrise convention |

Plus, pushed from Home and Practice: one work with its comments, the writing
screen, the account screen, the notifications screen.

## What we have now

**Colour** (`lib/theme/tokens.dart`) — a night palette, deliberately not black:

```
page   #121829   card  #1A2138   inset #0D1220
ink    #E9E6F0   soft  #B3B9D2   faint #8B93AF
line   #2E3752   lineStrong #485272
accent #8FBEE8   accentWash #1D2A45     (a cold blue)
rose   #E0A4BC   live  #F07A8C          (rose marks retrogrades; live is the stream dot)
```

**Type** — EB Garamond for display, Commissioner for body, plus a 5.6 KB
`AstroSymbols` cut carrying 29 glyphs. The site uses the same two faces, which
is most of why the two feel related.

It is *correct* and it is *plain*. It reads as a well-made utility by somebody
who cares. It does not yet read as **hers**.

---

## The brief

### 1. Make it feel like her, not like an astrology app

The single biggest gap. Right now nothing on screen says a person made this
except the words. We want somebody to open it and recognise it the way they
recognise her stream overlay.

⚠ **Not by putting her face on every screen.** By the things a VTuber brand is
actually made of: a consistent palette, a mark, a texture, a way headings sit,
one or two recurring motifs used sparingly enough to stay special.

### 2. Immersion, earned rather than applied

She asked for it to "really take advantage of the VTuber nature and make it
immersive". Some directions worth considering, and the agent should choose
rather than do all of them:

- **The app knows what the sky is doing.** It computes sunrise, sunset, the
  planetary hour and the Moon's phase for wherever the user is, on device,
  offline. That is a real signal almost no app has — the whole thing could
  shift with the time of day, or with the ruling planet of the hour, without a
  single network call.
- **She is either live or she is not**, and the app knows within ninety
  seconds. Live is a *state the app can be in*, not a badge on a card.
- **A chart is a drawing.** The wheels are already SVG/Canvas and correct;
  they could be beautiful.

### 3. Artwork she will draw herself

⚠ **This is the part the agent must specify precisely.** She is drawing it by
hand, so vagueness costs her a redraw. For every asset, give her:

- exact pixel dimensions, and for what density (@1x/@2x/@3x, or the largest
  needed with a note that it scales down)
- the safe area, and what may be cropped
- transparent or not; what sits behind it
- a one-paragraph description of pose, framing, mood and palette fit
- where it appears, and how often somebody sees it

A first guess at what is wanted, for the agent to revise:

- an **app icon** (adaptive: foreground + background, 432×432 safe zone 264×264)
- a **launch/splash** mark
- one **portrait** for Home, probably reacting to live/offline
- a set of small **motifs** or dividers
- an **empty-state** drawing or two — the practice room with nothing in it, the
  offline state
- something for the **live state** that is worth seeing

She will also want to know which of these are *nice to have*, so she can draw
the important ones first.

### 4. Polished and premium, on a free app

Where the polish should go, in order:
1. **Home**, because everyone sees it and it sets the whole impression.
2. **The live state**, because it is the moment the app earns its place.
3. **The wheels**, because they are the thing worth screenshotting.
4. Everything else can stay quiet and correct.

---

## Constraints that are not negotiable

- ⚠ **It works offline.** Every instrument computes on the device against a
  bundled ephemeris. No design may assume a network — including the artwork,
  which ships in the bundle.
- ⚠ **Density where density belongs.** The ephemeris and the stations are
  reference tables. Do not make them airy; a practitioner reading a month wants
  it all on one screen.
- ⚠ **Colour is never the only signal.** Retrograde is marked ℞ *and* tinted,
  because the mark survives being printed, being read aloud, and being read by
  somebody who cannot tell the colours apart. This holds everywhere.
- ⚠ **Marks are type, not emoji.** Every glyph carries U+FE0E. A colour emoji
  font ignores the palette entirely.
- ⚠ **Nothing takes money inside the app.** Support, shop and classes open her
  own checkout in a browser, where the address bar says whose it is.
- **AGPL-3.0.** Every asset ships in a public repo. Fonts must be licensed for
  that, and her artwork is hers — the licence question for the drawings is
  worth raising with her explicitly.
- **Flutter, Material 3, dark-first.** A light theme is not required.

## What "done" looks like

⚠ **Superseded — see `DESIGN-BRIEF-ASTROLABE-ADDENDUM.md`**, which is handed
over with this document. The scope is the WHOLE app: every screen, every state,
every variation, not a direction and one worked sample.
