# journal/fonts/ — the binaries this section needs

`../fonts.css` expects these eleven files here. Nothing else in the package
makes a network request; once these exist, `/journal` loads from your own
origin only.

| File | Family | Weight | Style | Scripts to subset |
|---|---|---|---|---|
| `eb-garamond-400.woff2` | EB Garamond | 400 | normal | Latin, Latin-ext, Greek, Greek-ext |
| `eb-garamond-400-italic.woff2` | EB Garamond | 400 | italic | Latin, Latin-ext, Greek, Greek-ext |
| `eb-garamond-500.woff2` | EB Garamond | 500 | normal | Latin, Latin-ext, Greek, Greek-ext |
| `eb-garamond-600.woff2` | EB Garamond | 600 | normal | Latin, Latin-ext, Greek, Greek-ext |
| `commissioner-400.woff2` | Commissioner | 400 | normal | Latin, Latin-ext, Greek |
| `commissioner-500.woff2` | Commissioner | 500 | normal | Latin, Latin-ext, Greek |
| `commissioner-600.woff2` | Commissioner | 600 | normal | Latin, Latin-ext, Greek |
| `jetbrains-mono-400.woff2` | JetBrains Mono | 400 | normal | Latin, Latin-ext, Greek |
| `jetbrains-mono-500.woff2` | JetBrains Mono | 500 | normal | Latin, Latin-ext, Greek |
| `noto-serif-devanagari-400.woff2` | Noto Serif Devanagari | 400 | normal | Devanagari |
| `noto-serif-devanagari-600.woff2` | Noto Serif Devanagari | 600 | normal | Devanagari |
| `mukta-400.woff2` | Mukta | 400 | normal | Devanagari |
| `mukta-600.woff2` | Mukta | 600 | normal | Devanagari |

All four families are **SIL Open Font License 1.1** — self-hosting is
permitted; ship the licence text alongside.

## Do not drop the Latin-only Google subsets in

The default `latin` subset has **no polytonic Greek**. `Μεταγειτνιῶνος`,
`οὐ λογίζεται` and every month name in the corpus need `greek-ext`
(U+1F00–1FFF). A page that looks right in English and falls back mid-word on a
Greek month is the exact failure this section cannot have.

## Subsetting

Keep Latin + Greek in one file per face — never split Greek into a second
request, or a polytonic word inside an English sentence arrives late.

```sh
pyftsubset EBGaramond-Regular.ttf \
  --output-file=eb-garamond-400.woff2 --flavor=woff2 --layout-features='*' \
  --unicodes="U+0000-00FF,U+0100-024F,U+0259,U+1E00-1EFF,U+2000-206F,\
U+2070-209F,U+20A0-20BF,U+2100-214F,U+2150-218F,U+2190-21FF,U+2200-22FF,\
U+25A0-25FF,U+2600-26FF,U+0370-03FF,U+1F00-1FFF"
```

The ranges above cover, in order: Latin, Latin-ext, ə, Latin additional,
punctuation, super/subscripts, currency, letterlike (℞), number forms, arrows,
maths, geometric shapes (● ◐ ○), **miscellaneous symbols — the astronomical
glyphs ☉ ☾ ☿ ♄ ♃ and the zodiac ♈–♓ live here**, then Greek and Greek-ext.

Drop `U+2600-26FF` and the type marks stop rendering in the display face and
fall through to a colour emoji font, which ignores `color`. Keep it.

Devanagari faces need `U+0900-097F,U+1CD0-1CFA,U+200C-200D,U+A8E0-A8FF` and
`--layout-features='*'` for conjuncts.

## Variable alternative

EB Garamond and Commissioner both ship variable. If you prefer two files to
seven, replace the static `@font-face` blocks with a variable one and
`font-weight:400 600;` — the design uses 400/500/600 only, and the section's
CSS asks for weights, never file names.
