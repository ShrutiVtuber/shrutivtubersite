# Handoff — for the developer agent

⚠ **Nothing in this package has been committed or pushed.** It was produced as a zip for you to
work from. Do not treat any of it as already present in `ShrutiVtuber/astrolabe`.

## Licence — settled, and it changes what you commit

**Dual.** Code AGPL-3.0; **the artwork is © Shruti, all rights reserved** and is *not* under the
AGPL. Read `ASSETS-LICENCE.md` — it names the three files the app repository needs and the one
sentence the readme needs. The app is built so a fork can ship with no drawings at all.

## Read in this order

1. **`readme.md`** — the design guide. Content fundamentals, visual foundations, iconography,
   the component index, and the caveats. Read the caveats before you trust anything.
2. **`guidelines/theme-flutter.md`** — `lib/theme/`, ready to adopt: `ColorScheme`, text theme,
   `pubspec` font declarations, component themes, elevation, every motion duration and curve.
   The night ramp is unchanged from today's `tokens.dart`, so existing screens keep working.
3. **`guidelines/artwork-spec.md`** — the drawings, with exact dimensions and safe areas.
   **Do not implement placeholders for these.** Every placement already has a designed
   art-absent state; build that state, and drop art in later.
4. **`ui_kits/astrolabe/states.html`** — every screen in every state, in order. This is the spec
   for what you build. Open it in a browser.
5. **`ui_kits/astrolabe/index.html`** — the same screens, interactive, with the states as
   switches.
6. **`ui_kits/astrolabe/artwork.html`** — where each drawing lands, at real size, in situ.

## What is new versus the app as it stands

Everything in `lib/theme/tokens.dart` is **unchanged**. Added on top:

- **`--gilt` `#C9A15B`** and its ramp — ornament, never interactive. Blue keeps that job.
- **Seven `hourTint` colours**, one per planetary ruler. ⚠ They colour exactly two things: the hem
  under the app bar and the hour chip. Never a table, never a `ColorScheme` slot.
- **Four motifs** — the hem, the star scatter, the rule, the veil. `tokens/motifs.css` is the
  reference; they are trivial to port to Flutter (a gradient line, a `CustomPainter` dot field,
  a `Row` with two dividers, a `BackdropFilter`).
- **Two brand surfaces, one per tab that needs one** — Home's `Masthead` plate and Sky's `DayArc`.
  They are deliberately different surfaces so the tabs do not all read as one stack of cards.
- **Live as a shell state**, not a badge: `data-live` in the web kit, an `InheritedWidget` in
  Flutter. It re-points the ornament colour, so the tab-bar hem and the masthead follow.

## Three rules that must not quietly disappear

1. **Colour is never the only signal.** Retrograde is `℞` *and* rose. Today is a wash *and* the
   word. A selected tab is a filled icon *and* a gilt hem *and* a full-ink label.
2. **Marks are type, not emoji.** Every glyph carries `\uFE0E` and the `AstroSymbols` family.
   The web system does this by putting AstroSymbols at the front of both font stacks with a
   `unicode-range` of just its 29 codepoints — do the equivalent with a `TextSpan` helper
   (`glyph()` in `theme-flutter.md`), not by remembering.
3. **Nothing takes money in-app.** Offers open `url_launcher` externally, and the card says so on
   its face before it is tapped.

## Two more, from the addendum

- ⚠ **Reference tables fit.** The stations, hours and ephemeris tables must not scroll sideways
  and must not be made airy. If a month will not fit, cut a column — never the density.
- ⚠ **No scrollbars, and no horizontal scrolling anywhere.** Vertical overflow is indicated by a
  fade at the foot of the scroller. Chip rows wrap; they never scroll.

## What is sample data

Positions, hours, stations, phases and isopsephy sums in `ui_kits/astrolabe/data.js` are authored
to be realistic and internally consistent so the layouts can be judged. **They are not computed.**
Every instrument screen carries a provenance block naming the engine and the rule in force; that
block is where the real reckoning is described.

## Not verified against the app source

`ShrutiVtuber/astrolabe` returned 404 to the design agent, so nothing here was checked against the
Flutter code. The palette is the design brief's verbatim quotation of `lib/theme/tokens.dart`; the
screen inventory is the brief and its addendum. **Check the wheels, the ephemeris columns and the
real screen structure against the repository before you rely on them.**
