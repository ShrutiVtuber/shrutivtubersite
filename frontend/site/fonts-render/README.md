# Render fonts

Not web fonts. These three are for the **server** to draw with when it
rasterises the horoscope share cards, and they are never served to a browser —
the site delivers its faces to readers as woff2 from `public/fonts/`.

They exist because the rasteriser cannot use what the site ships:

* **woff2 is a transport wrapper**, not something a font engine opens.
* The shipped faces are **variable**, and their default instance is not the
  weight the site renders at — Commissioner's default is Thin, so a card built
  from the file as-is comes out in hairlines.
* The Latin subsets contain **no astrological glyphs at all**, and a missing
  glyph rasterises as a hollow box rather than as an error.

| file | what it is |
|---|---|
| `Commissioner.ttf` | her body face, pinned to weight 400 |
| `EBGaramond.ttf` | her display face, upright, pinned to 500 |
| `AstroSymbols.ttf` | a 5.6KB cut of DejaVu Sans — the 29 codepoints the wheel prints, and nothing else |

Do not edit these. Rebuild them:

```bash
python3 frontend/site/scripts/build-render-fonts.py
```

## Licences

Commissioner and EB Garamond are SIL Open Font License 1.1, the same files
already in `public/fonts/`. `AstroSymbols.ttf` is a subset of DejaVu Sans,
under the DejaVu Fonts License (a permissive Bitstream Vera derivative), which
permits subsetting and redistribution. None of the three is covered by this
repository's AGPL — that applies to the code.
