# `lib/theme/` — adopting this without rewriting screens

The app is Flutter, Material 3, dark-first. This maps every token in `tokens/` onto a `ThemeData`
the existing screens can take as-is. Where a value here differs from today's `tokens.dart`, the
difference is called out.

## What is unchanged

The whole night ramp — `page card inset line lineStrong ink soft faint accent accentWash rose
live` — is **exactly** today's `lib/theme/tokens.dart`. Nothing that already references those
constants needs touching.

## What is added

```dart
// lib/theme/tokens.dart — additions
class Gilt {
  static const gilt       = Color(0xFFC9A15B); // ornament. 7.8:1 on page, so it may carry text
  static const giltBright = Color(0xFFE0BE7E); // star fill, lit limb of the phase disc
  static const giltDim    = Color(0xFF7A6238); // hairlines only — never text
  static const giltWash   = Color(0xFF241E13);
  static const cloth      = Color(0xFF3E4A6B); // the cloak — the Home plate only
  static const clothDeep  = Color(0xFF2B3450);
  static const parchment  = Color(0xFFEDE4CE); // share images and print only
}

/// The ruling planetary hour. Computed on device from the place and the clock,
/// so it is always available, offline included.
enum HourRuler { sun, moon, mars, mercury, jupiter, venus, saturn }

const hourTint = <HourRuler, Color>{
  HourRuler.sun:     Color(0xFFC9A15B),
  HourRuler.moon:    Color(0xFFB9C2DA),
  HourRuler.mars:    Color(0xFFD08A7C),
  HourRuler.mercury: Color(0xFF8FBEE8),
  HourRuler.jupiter: Color(0xFF9FC2A8),
  HourRuler.venus:   Color(0xFFE0A4BC),
  HourRuler.saturn:  Color(0xFF8B93AF),
};
```

⚠ **`hourTint` colours exactly two things: the hem under the app bar, and the hour chip.** Do not
feed it into `ColorScheme`. A practitioner reading a table must not watch it change colour every
sixty-odd minutes.

## ColorScheme

```dart
final scheme = ColorScheme.dark(
  primary:            Tokens.accent,        // #8FBEE8 — the only "you can touch this" colour
  onPrimary:          const Color(0xFF10182B),
  primaryContainer:   Tokens.accentWash,    // #1D2A45 — today's row, selected
  onPrimaryContainer: Tokens.accent,
  secondary:          Gilt.gilt,            // ornament; never a button fill
  onSecondary:        Gilt.giltWash,
  tertiary:           Tokens.rose,          // retrograde and editorial
  onTertiary:         const Color(0xFF2C2338),
  error:              Tokens.live,          // #F07A8C
  onError:            const Color(0xFF2A0F16),
  errorContainer:     const Color(0xFF33202B),
  surface:            Tokens.page,          // #121829
  onSurface:          Tokens.ink,
  surfaceContainerLow:     Tokens.card,     // #1A2138
  surfaceContainerLowest:  Tokens.inset,    // #0D1220
  surfaceContainerHigh:    const Color(0xFF232C48), // veil — pressed, sheet
  onSurfaceVariant:   Tokens.soft,
  outline:            Tokens.line,          // #2E3752 — every hairline
  outlineVariant:     Tokens.lineStrong,    // #485272
);
```

## Text theme

Two families and one glyph cut. `AstroSymbols` is declared as a family so a `TextSpan` can switch
into it mid-line — that is how ℞ and the sign marks get set without an emoji font stealing them.

```yaml
# pubspec.yaml
fonts:
  - family: EBGaramond
    fonts: [{asset: assets/fonts/EBGaramond-Regular.ttf},
            {asset: assets/fonts/EBGaramond-Medium.ttf, weight: 500},
            {asset: assets/fonts/EBGaramond-SemiBold.ttf, weight: 600},
            {asset: assets/fonts/EBGaramond-Italic.ttf, style: italic}]
  - family: Commissioner
    fonts: [{asset: assets/fonts/Commissioner-Regular.ttf},
            {asset: assets/fonts/Commissioner-Medium.ttf, weight: 500},
            {asset: assets/fonts/Commissioner-SemiBold.ttf, weight: 600}]
  - family: AstroSymbols
    fonts: [{asset: assets/fonts/AstroSymbols.ttf}]   # 5.6 KB, 29 glyphs
```

| Role | Family | Size / height / spacing | Where |
|---|---|---|---|
| `displayLarge` | EB Garamond 500 | 34 / 1.12 / −0.41 | Home masthead only |
| `displayMedium` | EB Garamond 500 | 28 / 1.12 / −0.34 | screen titles |
| `titleLarge` | EB Garamond 600 | 22 / 1.24 / 0 | section titles, a work's title |
| `titleMedium` | EB Garamond 500 | 19 / 1.3 / 0 | card titles |
| `titleSmall` | Commissioner 600 | 17 / 1.32 / 0 | list headings |
| `bodyLarge` | EB Garamond 400 | 17 / 1.65 / 0 | readings and articles (prose only) |
| `bodyMedium` | Commissioner 400 | 16 / 1.5 / 0 | rows, sheets, banners |
| `labelLarge` | Commissioner 500 | 14 / 1.4 / 0 | field labels, button text |
| `bodySmall` | Commissioner 400 | 13 / 1.4 / 0 | helper, meta, provenance |
| `labelSmall` | Commissioner 600 | 11 / 1.0 / +1.54 | eyebrows, uppercased in the widget |

Data uses `bodyMedium` at 15 (or 13 dense) with
`fontFeatures: [FontFeature.tabularFigures(), FontFeature.liningFigures()]`.
**No mono family ships** — a third face costs the offline bundle ~40 KB for figures Commissioner
already sets correctly.

```dart
// Every astronomical mark, everywhere.
TextSpan glyph(String mark, {Color? color, double size = 16}) => TextSpan(
  text: '$mark\uFE0E',                       // ⚠ the variation selector is not optional
  style: TextStyle(fontFamily: 'AstroSymbols', fontSize: size, color: color, height: 1),
);
```

## Shape, spacing, targets

```dart
const radiusSm = 8.0;   // chips, buttons, inputs
const radiusMd = 14.0;  // cards, list groups
const radiusLg = 20.0;  // the Home plate, dialogs
const radiusXl = 28.0;  // bottom sheets
// space: 4 8 12 16 20 24 32 40 56 72 — gutter 16, dense gutter 12
// targets: 48 minimum, 56 comfortable (rows), 64 tab bar, 56 app bar
```

⚠ **Divergence from the site**, which uses 4 / 10 / 16. The app is rounder on purpose: it is a
phone, it is Material 3, and her line is soft. Anything shared between app and site — an email, a
share image — follows the **site's** radii, not these.

## Component themes

```dart
cardTheme: CardThemeData(
  color: Tokens.card, elevation: 0,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(radiusMd),
    side: const BorderSide(color: Tokens.line)),        // the hairline does the work
),
filledButtonTheme: /* height 48, radius 8, no elevation; pressed = translate 1px, never scale */
navigationBarTheme: NavigationBarThemeData(
  height: 64, backgroundColor: Tokens.card,
  indicatorColor: Colors.transparent,                   // the gilt hem marks selection instead
  labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
),
bottomSheetTheme: const BottomSheetThemeData(
  backgroundColor: Tokens.card, showDragHandle: true,
  shape: RoundedRectangleBorder(borderRadius:
    BorderRadius.vertical(top: Radius.circular(radiusXl))),
),
```

## Elevation

On a `#121829` page a Material shadow barely reads, so the system uses **fill and hairline** for
depth and keeps shadow for things that genuinely float.

| | Flutter | Used by |
|---|---|---|
| flat | `elevation: 0`, no border | the scaffold |
| resting | `elevation: 0` + 1px `line` | every card |
| pressed | fill → `veil`, border → `lineStrong` | tappable card, list row |
| inset | fill `inset` + 1px `line` | tables, code, field interiors |
| floating | `elevation: 3` + `shadowColor: Colors.black` | sheets, dialogs, snackbar |

## Motion

| Transition | Duration | Curve |
|---|---|---|
| press, tint, chip | 120 ms | `Cubic(.2,.7,.3,1)` |
| segment slide, card enter, snackbar, **a vote landing** | 240 ms | `Cubic(.2,.7,.3,1)` |
| **tab change** | 240 ms | cross-fade **only** — six tabs have no left and right |
| **push / pop** | 240 ms | slide from the right, `Cubic(.32,.72,0,1)` |
| **dialog open**, sheet rise | 240 ms | `Cubic(.32,.72,0,1)` |
| **pull to refresh** | continuous | gilt arc, 900 ms per turn |
| **draft saving** | none | the snackbar is the feedback; no spinner |
| **hour tint cross-fade**, live arriving | 600 ms | `Cubic(.45,0,.25,1)` |

⚠ **`MediaQuery.disableAnimationsOf(context)`** (or `accessibleNavigation`) collapses all of the
above to 1 ms, stops the live dot pulsing — **the word "Live" carries the meaning on its own** —
and stops the refresh arc turning. Nothing in the app is only legible in motion.

## The three rules a developer must not quietly drop

1. **Colour is never the only signal.** Retrograde is `℞` *and* rose. Today is a wash *and* the
   word "today". A selected tab is a filled icon *and* a gilt hem *and* full-ink label.
2. **Marks are type, not emoji.** Every glyph carries `\uFE0E` and the `AstroSymbols` family.
3. **Nothing takes money in-app.** Offers open `url_launcher` in an external browser, and the card
   says so on its face before it is tapped.
