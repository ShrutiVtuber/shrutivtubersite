# Astrolabe — design system

Design system for **Astrolabe**, Shruti's companion app: the free thing her audience installs so
they are never far from her. It is a VTuber's app before it is an astrology app — the astrology is
what it does, but being *hers* is why anyone keeps it. Flutter, Material 3, **dark-only**, and it
**works offline**: every instrument computes on the device against a bundled ephemeris.

The site's line is *"Instruments for magick, built live from Athens."* The app is the pocket
version of that.

**Register:** practitioner, not merchant. An observatory instrument, an astronomical almanac, a
well-set grimoire — with one person's hand visible on it. Never crystal-ball kitsch, never
purple-and-gold mystic cliché, never casino tarot.

## Who opens it, in the order they matter

1. **A viewer between streams** — is she live, what did she write, tap through to the site. The
   majority, and they never touch an instrument.
2. **Somebody learning astrology** — the practice room: writes a reading, puts it in front of
   others, argues about somebody else's.
3. **A practitioner** — the ephemeris, the stations, the hours, the chart. Wants density and
   accuracy, not decoration.

⚠ **The design serves (1) without insulting (3).** A Home screen with a portrait on it and a
stations table that is a wall of numbers live in the same app, and must feel like the same app.
The thing that makes them feel like one app is the ink, the two faces, and the gold hem — not a
shared amount of decoration.

## Products represented

- **Astrolabe** (this system) — the Flutter companion app. Six tabs: Home · Sky · Chart · Letters ·
  Practice · Settings, plus five pushed screens, a place picker and a full-screen sky drawer.
- **shrutivtuber.com** — the talent site and its own design system, which this one is a sibling of
  (same two faces, same night ramp; see "Relationship to the site" below).

## Sources given

- `uploads/DESIGN-BRIEF-ASTROLABE.md` — the brief (10 Sep 2026). The screen inventory, the three
  audiences, the four non-negotiables, and the night palette from `lib/theme/tokens.dart`.
- `uploads/DESIGN-BRIEF-ASTROLABE-ADDENDUM.md` — **replaces the brief's "what done looks like"**:
  the scope is the whole app, every screen and every state, at 360 × 800 and 430 × 930.
- `uploads/sh.jpeg` — **the primary visual reference.** Her astrologer design: a night-blue hooded
  cloak edged in a thin gold line, scattered with gold and white stars and crescents; a
  moon-phase hair clip; a crescent clasp; a brown book, a parchment horoscope card. Everything in
  "the brand layer" below is taken from this drawing.
- `uploads/shruti.jpg` — a second character reference (casual outfit). Not used for the app's
  palette; kept as context for who she is.
- `github.com/ShrutiVtuber/shrutivtubersite` — **read**, at `fe25a4c0`. Source of the shared night
  ramp (`design/tokens/colors.css`), the two faces, the tone rules, the real `AstroSymbols.ttf`
  binary, and the brand PNGs in `assets/`. See `github.md`.
- `github.com/ShrutiVtuber/astrolabe` (AGPL-3.0) — the app's own Flutter source. ⚠ **404 for this
  connection; not read.** Nothing here is copied from the Flutter code. The palette comes from the
  brief's verbatim quotation of `lib/theme/tokens.dart`, and the screen inventory from the brief
  and addendum. See "Caveats".

## The design decision, in one paragraph

The app was already *correct* and *plain*: a well-made utility by somebody who cares, that did not
read as **hers**. Rather than putting her face on every screen, this system adds **one colour and
three motifs**, all lifted from her own artwork: **gilt** `#C9A15B`, the cloak's gold trim, used as
a **hem** — a hairline that fades at both ends — a low-density **star scatter** on brand surfaces
only, and a **rule** that closes a section with a mark in it. Gold is ornament and never
interactive; blue keeps that job. On top of that sit the two things the app already knows and
almost no app does: **the ruling planetary hour**, computed on device, which tints the hem and one
chip and nothing else; and **live as a state the app is in**, which turns the whole shell's
ornament rose. That is the entire brand layer, and it is deliberately small enough to survive
being on a stations table.

---

## Content fundamentals

**Voice.** First person "I" is Shruti; "you" is the reader. Warm, competent, a little arcane, and
concrete: "Swiss Ephemeris 2.10.03", "within ninety seconds", "about one a month" — never vague
mysticism. The app talks the way she does on stream, which is why even the chrome is set in EB
Garamond.

**Casing.** Sentence case everywhere — titles, buttons, list rows, tab labels. Title Case only for
proper nouns (Astrolabe, Swiss Ephemeris, Discord). Eyebrows are written sentence case in the
source and uppercased by CSS, so a screen reader gets the sentence.

**No emoji, anywhere.** Atmosphere is astronomical glyphs set in type. (The old wordmark's hearts
are artwork, not UI — hearts never appear in chrome, copy or icons.)

**Empty states are authored, quiet and honest.** Never "No data". Real examples from the kit:

> "The room is quiet — nobody has posted a reading this week. Yours would be the first."
> "Nothing in the next forty days. The sky is quiet, and that is not an error."
> "Nothing called 'Athina' — try the local spelling, or the nearest larger city; the hours will be
> within a minute or two."

**Offline is not broken, and the copy carries the distinction.** ⚠ This is the single most
Astrolabe-specific writing rule:

> "Her half is out of reach. The instruments all still work — they compute on your phone.
> Readings, offers and the practice room will come back when you do."

**Never fake liveness.** Three states, and `unknown` is not `offline`: "Live now" · "Not live —
next: Thursday 20:00 Athens" · "Status unavailable — could not reach Twitch, check directly".

**Cannot-compute states offer an honest alternative instead of a fabricated answer.** "The angles
are not reckoned. With no birth time there is no ascendant and no midheaven, so this wheel has no
houses. Everything drawn here is true; the things that are missing are missing on purpose."

**Disagreements are stated, not defaulted.** Where two authorities disagree the app puts the choice
on the instrument and gives each option its one-line rule, with neither marked correct:
"Sunrise — the Sun's upper limb clears the horizon." / "Civil dawn — the Sun is 6° below the
horizon." followed by "Neither is the correct one. Pick the one your tradition uses."

**Times are dual.** Authored in Athens (GMT+3), always shown with the reader's local conversion
where the two differ: "04:12 Athens · 02:12 your time". Tabular figures for every time, count and
coordinate.

**Money is always leaving.** ⚠ Nothing is bought inside the app. Offer cards say "opens in your
browser" on their face, before the tap: "Support, the shop and classes open your browser, where the
address bar says whose checkout it is."

**Bylines.** Her writing in the app signs "Shruti". *Soror Eu. A.* is the site's signature on
magickal work and does not appear in the app.

---

## Visual foundations

**Colour.** One palette, one hour: **dusk**. The night ramp is verbatim from `lib/theme/tokens.dart`
— page `#121829` (deliberately not black), card `#1A2138`, inset `#0D1220`, veil `#232C48`; ink
`#E9E6F0` / soft `#B3B9D2` / faint `#8B93AF`; hairlines `#2E3752` and `#485272`. **Accent blue
`#8FBEE8` is the only colour that means "you can touch this."** Rose `#E0A4BC` is retrograde and
editorial. Live `#F07A8C` belongs to the stream state alone. **Gilt `#C9A15B` is new**, sampled
from the cloak's trim: ornament, offers, and the hem — 7.8:1 on the page, so it may carry text.
Seven **hour tints** exist for the ruling planet and touch two elements only. A light theme is
**not** required and is not provided; see "Should there be a light theme?" below.

**Type.** EB Garamond (display, titles and prose — her voice), Commissioner (UI — labels, rows,
buttons), and a bundled **AstroSymbols** cut of 29 glyphs. **No mono face ships**: data is
Commissioner with `tabular-nums lining-nums`, which saves ~40 KB in an app that must work offline.
Scale is 34 / 28 / 22 / 19 / 17 / 16 / 15 / 14 / 13 / 11, with 11 px reserved for uppercase
eyebrows.

**Spacing.** 4 px base: 4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 56 · 72. Two densities — `--gutter`
16 on reading screens, `--gutter-dense` 12 on Sky, Chart and the ephemeris. ⚠ **Density where
density belongs:** reference tables are 30 px rows and 13 px figures, and are not to be made airy.

**Backgrounds.** Flat `--page`, almost everywhere. Exactly **one** brand-coloured surface exists in
the whole app — Home's `.plate`, a navy gradient from `--cloth` to `--card`. No repeating patterns,
no photographs, no grain, no full-bleed imagery. The only texture is the **star scatter**: nine
fixed radial gradients, two sizes, gold and ink, at 50% opacity, never behind a table and never
animated.

**Corner radii.** 8 controls · 14 cards · 20 the plate and dialogs · 28 bottom sheets · pill for
badges. ⚠ Rounder than the site's 4 / 10 / 16, deliberately: this is a phone, it is Material 3, and
her line is soft. Anything shared with the site (email, share images) uses the site's radii.

**Cards.** `--card` fill, 1 px `--line`, radius 14, `--shadow-1`. Four tones only: plain, tappable,
highlighted (offers — the one place gold sells something), warning (rose, always with a mark).
**Press deepens the fill to `--veil` and strengthens the hairline. Cards never lift and never
scale.**

**Borders and shadows.** Hairlines do the structural work; on a `#121829` page a shadow barely
reads. `--shadow-1` resting, `--shadow-2` raised, `--shadow-3` for sheets and dialogs only. **No
decorative glows** — the one glow in the system is `--glow-live`, three pixels around the live dot.

**Transparency and blur.** Two uses, both protective: the `.veil` capsule for text over the plate
or over her artwork, and the sheet/dialog scrim. **Protection capsules, not gradient scrims** — a
gradient over a drawing muddies it; a blurred capsule leaves it intact.

**Hover, press, focus.** Touch first: there is no hover state in the app, and the web
recreations use it only as a courtesy. **Press** deepens the fill and sinks buttons 1 px —
never a scale-shrink. **Focus** is a 2 px `--accent` outline at 2 px offset, always visible.
**Disabled** is 38% opacity (Material 3) plus a stated reason where one exists.

**Motion.** Fades and small translates only. 120 ms for a state change, 240 ms for an enter or exit,
600 ms for atmosphere (the hour tint cross-fading, live arriving). Tab change is a **cross-fade
only** — six tabs have no left and right. Push and pop slide 240 ms from the right. No bounce, no
parallax, no spring. ⚠ Under reduced motion everything collapses to 1 ms, the live dot stops
pulsing and the word "Live" carries the meaning alone.

**Imagery.** Her artwork is twilight-hued, indigo and gold, hand-drawn with a clean outline. It is
**always a nullable reference**: every placement has a designed art-absent state, and the app
looks finished today with no drawings at all. Nothing is recoloured, and nothing arrives with a
baked-in glow or vignette. Full specification in `guidelines/artwork-spec.md`.

**Layout rules.** The app bar is sticky and 56 px, with the hour-tinted hem beneath it. The tab bar
is fixed, 64 px, and shows through everything except a full-screen dialog. Segmented controls sit
directly under the app bar. Provenance — engine, the rule in force, where it was computed — closes
every instrument screen. Touch targets are never below 48 px, and list rows are 56.

### Should there be a light theme?

**No, and the app should say so rather than half-building one.** The brief says dark-first and does
not require light; more usefully, the sibling site already carries the light hour (*dawn*) of the
same palette, so the pair reads as one sky at two junctures — the site is dawn, the app is dusk.
Adding a dawn theme to a phone that is mostly opened at night would double the surface to test for
a case the audience does not have. If it is ever wanted, the site's `--dawn-*` ramp is the answer
and nothing here needs re-picking.

### Relationship to the site's design system

Same two faces, same night ramp, same glyph rule, same "colour is never the only signal" law — so
the two feel related without the app being a phone-shaped website. **Different on purpose:** the
app is dark-only, its radii are rounder, it ships no mono face, and it has the gilt layer and the
ruling hour, which the site does not. Where an artefact is shared (an email, a share image), it
follows the **site's** system, not this one.

---

## Iconography

**UI icons: Material Symbols Outlined — kept, not substituted.** It is what the Flutter app already
draws (`Icons.*_outlined`), it is Apache-2.0 so it is AGPL-safe, and it costs the app bundle
nothing. Web recreations load it from Google Fonts in `tokens/fonts.css`; the app does not load
anything. Outlined at rest; **filled only for the selected tab**. 24 px default, 20 px in rows,
22 px in the tab bar. Wrapped by `Icon`.

**Astronomical marks: the bundled `AstroSymbols` cut.** `assets/fonts/AstroSymbols.ttf`, 5.6 KB,
copied from the repository — the real binary, not a substitute. It carries **exactly 29 glyphs** and
nothing else:

```
° ′ ″ ℞ ☉ ☊ ☋ ☽ ☾ ☿ ♀ ♂ ♃ ♄ ♅ ♆ ♇ ♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓
```

⚠ **Marks are type, not emoji.** Every glyph is emitted with **U+FE0E**, and the `.t-glyph` class
pins the family — a colour-emoji font ignores `color` and destroys the palette. Wrapped by `Glyph`.
Note what the cut does *not* contain: the moon-phase circles ○ ◐ ●, which fall back to EB Garamond,
and which the drawn `MoonDisc` component replaces wherever the phase matters.

**Platform marks: the site's own SVGs**, copied into `assets/icons/` — Twitch, YouTube, Discord, X,
GitHub, Ko-fi, Bluesky, Mastodon, Instagram, LinkedIn. Tinted to the current ink.

**No emoji. No icon font beyond Material Symbols. No hand-drawn approximations of her brand marks** —
where the wordmark cannot be used, the word is set in EB Garamond.

---

## Components

Thirty-four, grouped by concern. Every one is traceable to a screen in the brief or a line in the
addendum's §3 list; the "intentional additions" are named at the end.

**`components/marks/`** — `Glyph` · `Icon` · `MoonDisc`
**`components/brand/`** — `AppBar` · `LiveBanner` · `HourChip` · `SectionHeader` · `Masthead` · `DayArc`
**`components/navigation/`** — `TabBar` · `SegmentedControl` · `ListRow` (with `ListGroup`)
**`components/forms/`** — `Button` · `IconButton` · `TextField` · `Chip` · `Switch` · `ChoiceRow`
**`components/surfaces/`** — `Card` · `Sheet` · `Dialog`
**`components/data/`** — `DataTable` · `DataRow` · `ChartWheel` · `CodeBlock`
**`components/feedback/`** — `EmptyState` · `Banner` · `Snackbar` · `Progress` (with `Skeleton`)
**`components/content/`** — `ContentCard` · `WorkCard` · `VoteControl` · `OfferCard` · `Prose`

Each has a sibling `.d.ts` (the props contract) and `.prompt.md` (what and when), and each
directory carries one `@dsCard` specimen.

**Intentional additions**, and why each earns its place:

- `Glyph` and `Icon` are wrappers over the two glyph sets. Without them the U+FE0E rule and the
  filled/outlined rule get dropped in the first screen somebody writes by hand.
- `MoonDisc` exists because the phase circles are not in the font cut and a drawn disc is correct
  at any fraction of the cycle, which ○ ◐ ● are not.
- `HourChip`, `Masthead` and `DayArc` are the brand layer made concrete — the components a
  developer could not infer from the brief. `DayArc` also does the work of keeping the tabs from
  looking alike: Home has the plate, Sky has the arc, and neither borrows the other's surface.
- `ListGroup` and `Skeleton` ship inside their siblings' files rather than as separate families.
- `Provenance` and `FactCard` live in the UI kit, not the component library — they are compositions
  of `DataRow`, not new primitives.

---

## Index

- `styles.css` → `tokens/` — `fonts` · `colors` · `typography` · `spacing` · `effects` ·
  **`motifs`** (the hem, scatter, rule, veil, plate and card) · `base`
- `assets/` — the real brand files: `fonts/AstroSymbols.ttf`, wordmark, avatar, app icons, the
  platform SVGs in `assets/icons/`. Manifest and usage rules in `assets/README.md`.
- `components/<group>/` — 33 components, each with `.d.ts`, `.prompt.md`, and a group specimen card
- `guidelines/` — 21 foundation cards, plus:
  - **`guidelines/artwork-spec.md`** — ⚠ **what she draws, with exact dimensions, safe areas,
    transparency, mood, placement, frequency, and essential-vs-nice-to-have order.** Also the
    AGPL licence question about her drawings, which needs her answer.
  - **`guidelines/theme-flutter.md`** — the `lib/theme/` mapping: `ColorScheme`, text theme,
    `pubspec` font declarations, component themes, elevation, and every motion duration and curve.
- `ui_kits/astrolabe/index.html` — the app, interactive: six tabs, five pushed screens, the place
  picker, the sky drawer and the sunrise sheet, with every state as a switch and both phone sizes.
- **`ui_kits/astrolabe/artwork.html`** — **where your art goes**: every drawing the app asks for,
  at its real size, inside the real screen, with a drop target in it. Drag a PNG onto any slot and
  the app themes around it immediately — the visual companion to `guidelines/artwork-spec.md`.
- `ui_kits/astrolabe/states.html` — **every screen in every state, in order**, as live renders.
- `templates/app-screen/` — a starting template for consuming projects: the phone shell with the
  hour-tinted app bar, a scrolling body and the six-tab bar, with tweaks for the tab, the ruling
  hour and the live state.
- `github.md` — the repository this was read from, and what was taken.
- `SKILL.md` — agent-skill entry point.

---

## Licence — settled

**Dual, confirmed by Shruti on 10 September 2026.** Code AGPL-3.0; **her artwork is © Shruti, all
rights reserved** and is not covered by it. A fork may take the code and must replace every
drawing — which the app is built to survive, because every art placement has a designed
art-absent state. Full terms and the three files the app repository needs:
`ASSETS-LICENCE.md`.

⚠ **This is a handoff package, not a commit.** Nothing here has been pushed to any repository.

## Caveats

- ⚠ **`ShrutiVtuber/astrolabe` was not readable from this connection** (404 on `main` and
  `master` — private, or not yet pushed). Nothing here is derived from the Flutter source: the
  palette is the brief's verbatim quotation of `lib/theme/tokens.dart`, and the screens follow the
  brief and addendum. **If the repository can be shared, the wheels, the ephemeris columns and the
  real screen structure should be checked against it** — that is the one thing that would move this
  from faithful to exact.
- **The wordmark is off-palette.** `assets/wordmark.png` is the pink-and-blue WordPress-era mark
  with hearts; it does not sit on `#121829`. It has not been redrawn or approximated — the app sets
  "Astrolabe" in EB Garamond where a mark would go, and a night re-cut is item 6 in the artwork
  spec.
- **No app icon exists.** The `icon-192.png` copied from the site is the site's, not the app's.
  Item 1 in the artwork spec.
- **EB Garamond and Commissioner load from Google Fonts here**, because no licensed binaries were
  provided to this project; the repository has TTFs at `backend/shruti/assets/fonts/` and the app
  bundles its own. `AstroSymbols.ttf` **is** the real binary and is bundled here.
- **The kit's data is plausible sample data, not live computation.** Positions, hours, stations and
  isopsephy sums are authored to be realistic and internally consistent so the layouts can be
  judged. The reckoning a developer must write is described in each screen's provenance block.
- **Tablet is out of scope**, as the addendum allows — and it should stay out. Every instrument in
  the app is a single column of dense figures; a two-pane tablet layout would be a different
  information design, not a wider version of this one. Worth doing when there is a reason, not
  before.
- **The sigil and the wheels are drawn by the system**, because they are instrument output, not
  brand art. Nothing else is drawn: no logo, no character, no icon has been invented here.
