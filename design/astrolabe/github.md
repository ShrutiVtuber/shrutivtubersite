# github.md

repo: ShrutiVtuber/shrutivtubersite
branch: main
path: design, frontend/site, backend/shruti/assets

## Last sync
date: 2026-09-10T01:07:16Z
commit: (not recorded — only a tree hash was resolved: fe25a4c0b646)

### Updated in this project
- Copied the real `AstroSymbols.ttf` (5.6 KB, 29 glyphs) into `assets/fonts/`.
- Copied brand PNGs (wordmark, avatar, icons, social card) and ten platform SVGs into `assets/`.
- Took the shared night ramp, the two type faces and the tone rules from `design/tokens/` and
  `design/readme.md` as the basis for this app system.
- Diverged deliberately: dark-only, rounder radii, no mono face, plus the gilt layer and the
  ruling-hour tint, none of which the site has.

## Related repository — not readable
repo: ShrutiVtuber/astrolabe
status: 404 on `main` and `master` for this connection (private, or not yet pushed)
impact: nothing in this design system is derived from the Flutter source. The palette is the
  design brief's verbatim quotation of `lib/theme/tokens.dart`; the screen inventory is the brief
  and its addendum. If access is granted, re-check the wheels, the ephemeris columns and the real
  screen structure against it.

## Screen map
| Screen | Built from |
|---|---|
| All 18 app screens | `uploads/DESIGN-BRIEF-ASTROLABE.md`, `uploads/DESIGN-BRIEF-ASTROLABE-ADDENDUM.md` |
| Colour tokens | brief §"What we have now" (verbatim `lib/theme/tokens.dart`) + `design/tokens/colors.css` (dusk ramp) |
| Type tokens | `design/tokens/typography.css`, `design/tokens/fonts.css` |
| Glyph font | `frontend/site/fonts-render/AstroSymbols.ttf` |
| Brand layer (gilt, hem, scatter, rule) | `uploads/sh.jpeg` — her astrologer artwork |
| Tone and copy rules | `design/readme.md` → Content fundamentals |
| Platform icons | `frontend/site/src/icons/*.svg` |
