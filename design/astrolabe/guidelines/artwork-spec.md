# Artwork — what to draw, at what size

For Shruti. Every asset below is specified so it can be drawn once and dropped in without a
redraw. **Everything ships inside the app bundle** (it works offline) **and inside a public
AGPL-3.0 repository** — see "The licence question" at the foot, which needs an answer from you
before any of this is committed.

Densities: Android needs @1x/@2x/@3x, iOS needs @1x/@2x/@3x. Unless a piece says otherwise,
**draw once at the largest size given and export the smaller ones down from it.** Vector (SVG) is
better than raster wherever the drawing survives it.

Palette to check against: `tokens/colors.css`. The app is dark-only — everything sits on
`--page #121829`, `--card #1A2138`, or the cloak navy `--cloth #3E4A6B`. The gold is
`--gilt #C9A15B`. **No piece should have a baked-in glow, vignette, or drop shadow** — the app
adds its own, and a baked one will not match at every size.

---

## Essential — the app is not finished without these

### 1. App icon, adaptive (Android) + square (iOS)

| | |
|---|---|
| **Canvas** | Two layers, **432 × 432 px** each, exported at @1x…@4x (432 / 864 / 1296 / 1728). Plus one flattened **1024 × 1024** for iOS and the stores. |
| **Safe zone** | **264 × 264 centred.** Android crops the outer 168px to a circle, squircle, rounded square or teardrop depending on the launcher — anything outside 264 will be cut on some phones, and you cannot know which. |
| **Transparency** | Foreground: transparent. Background: **fully opaque, no transparency at all**, edge to edge. |
| **Behind it** | The launcher's wallpaper. Assume anything. |

**Foreground:** one mark, not a scene. The strongest candidate from your existing art is the
**crescent-and-star clasp** at the throat of the cloak — a waxing crescent with a single
eight-pointed star, in `--gilt`, at roughly 190px tall inside the safe zone. It reads at 48px,
which a face does not. **Background:** flat `--cloth-deep #2B3450` with the star scatter from the
cloak at the density it has on the fabric — five or six stars, none crossing into the safe zone.

*Where it appears:* the launcher, the share sheet, the app switcher, the store listing. Somebody
sees it several times a day and never looks at it for more than a fifth of a second.

### 2. Notification icon

| | |
|---|---|
| **Canvas** | **96 × 96 px** (24 dp at @4x). Also export 72 / 48 / 36 / 24. |
| **Safe zone** | 88 × 88; Android pads it. |
| **Transparency** | ⚠ **Transparent PNG, and the drawing must be pure white `#FFFFFF` at varying alpha only.** Android throws away every colour in this asset and renders the alpha channel as a flat silhouette. A gold icon here arrives as a white blob. |

Draw the same crescent-and-star as #1, but as a **solid silhouette with no interior detail** — at
24dp the clasp's inner line disappears and becomes mud. Test it by filling your artwork 100% black
and squinting: whatever is still readable is what the user will see.

*Where it appears:* the status bar, whenever she goes live. Several times a week.

### 3. Home portrait — offline

| | |
|---|---|
| **Canvas** | **800 × 1200 px**, drawn once; the app uses it at 132 × 196 logical (so ~396 × 588 @3x). Extra resolution is for the large-phone layout and for future full-bleed use. |
| **Safe area** | The **left 18% and the bottom 12% may be cropped** — she is bottom-anchored into the corner of the plate and bleeds off both edges. Keep her face and the clasp inside the top-right 70%. |
| **Transparency** | ⚠ **Transparent PNG.** Layered source too, please. |
| **Behind it** | The Home plate: a navy gradient `--cloth → --cloth-deep → --card`, with a faint gold star scatter. She must read against all three values. |

**Pose, framing, mood.** Three-quarter view, waist-up or a little lower, **turned slightly away and
looking down at something in her hands** — a book, a card, the cup. The reference cloak art is
exactly right: hood up, the gold-edged mantle, the moon-phase hair clip. Quiet, occupied,
mid-thought — *not* addressing the viewer. This is the offline state and the whole point is that
she is doing her own work while you check the sky. Palette: her existing indigo-and-gold reads
correctly on the plate as-is; if anything, push the cloak a step darker so the gold trim stays the
brightest thing in the drawing.

*Where it appears:* the top of Home, which is the first screen every single user sees, every time
they open the app. **This is the highest-leverage drawing in the project.**

### 4. Home portrait — live

Same canvas, same safe area, same transparency as #3. **A second drawing, not a recolour.**

**Pose, framing, mood.** Same character, same cloak, but **facing out and mid-speech** — looking
at the viewer, one hand raised or gesturing, hood back or pushed off so her face is fully clear.
Warmer: let the rose `--live #F07A8C` appear somewhere small and real in the drawing (a ribbon, the
inner lining catching light) so the live plate's rose hem has something to answer. Energy, not
alarm — she is talking to a room, not shouting.

*Where it appears:* the top of Home whenever she is streaming, which is the moment the app earns
its place. Everyone who opens it during a stream sees this and nothing else first.

### 5. Splash / launch mark

| | |
|---|---|
| **Canvas** | **1152 × 1152 px** (Android 12+ splash icon: 288dp canvas, **192dp = 768px visible circle**). Also a **512 × 512** flat version for the older launch screen. |
| **Safe zone** | The **centre 768 × 768 circle**. Android masks everything outside it. |
| **Transparency** | Transparent PNG. The background is `--page #121829`, set by the theme — do not draw one. |

The mark from #1 again, at rest. **No text, no wordmark, no character** — the splash is on screen
for under a second and anything with detail in it flickers. If you want one moment of life here,
the app can fade the star in 200ms after the crescent; draw them on separate layers and say so.

*Where it appears:* every cold start.

### 6. Wordmark, re-cut for the night

| | |
|---|---|
| **Canvas** | **SVG**, plus PNG at **1500 × 540** (3× the current 500 × 180). |
| **Transparency** | Transparent. |
| **Behind it** | `--page #121829` and `--card #1A2138`. |

⚠ **This is a re-cut of your existing wordmark, not a new logo — and not a job for the agent.** The
one in `assets/wordmark.png` is the WordPress-era pink-and-blue with the hearts, and it does not
sit on a #121829 page: the pale pink vibrates and the outline disappears. What the app needs is
**the same letterforms and the same Devanagari, re-coloured for night** — ink `--ink #E9E6F0` with
the accents in `--gilt`, or a single-colour gilt cut. Until it exists the app sets the word
"Astrolabe" in EB Garamond and looks fine, so this is essential but not urgent.

*Where it appears:* the Settings "About" block, the licences screen, the share image, the store
listing. Occasionally, but always in a context where a wrong-looking logo is the only thing anyone
notices.

---

## Nice to have — in this order

### 7. Empty state — the practice room

**512 × 512**, transparent, drawn to sit centred above two lines of text. The app currently draws a
gilt ring with ♄ in it and it does not look broken, so this is pure upgrade.

A small vignette rather than a character: **an empty chair at a desk with a chart half-drawn on
it**, or the cup and the closed book. Line weight matching the cloak art's outline. Muted — this
sits behind a "write the first one" button and must not compete with it.

*Where it appears:* the practice room with nothing in it. Rare for an established user, common for
a new one, which makes it the first impression for exactly the people you are trying to keep.

### 8. Empty state — her half is out of reach

**512 × 512**, transparent. ⚠ **The brief for this one is the hardest and the most important to get
right: this is not an error drawing.** The instruments all still work. What is missing is *her*.
Something like **the cloak hung on a peg**, or a lit window seen from outside — an absence with a
promise in it, not a broken plug or a sad face. Nothing red, nothing with an exclamation mark.

*Where it appears:* Home and Practice, whenever the network is gone. On a commute, daily.

### 9. Empty state — nothing written yet

**512 × 512**, transparent. A blank page and a pen, in her hand or on the desk; the same vignette
language as #7. Encouraging, not empty.

### 10. Motifs and dividers

**SVG, single colour** (the app tints them), drawn on a **24 × 24** and a **120 × 24** grid.

- a **crescent** and an **eight-pointed star** as separate glyphs, matching the ones scattered on
  the cloak — these become the section rules and the empty-state ring
- one **divider**: a hairline with a small ornament at its centre, 120 × 24, that can stretch
- optionally a **three-phase moon strip** matching your hair clip, 72 × 24

*Where it appears:* section rules on Home and Settings, the empty-state ring, the sigil plate
corner. Constantly, but small — which is why they must be drawn on a pixel grid rather than
scaled down from something larger.

### 11. Live-state ornament

**1200 × 200**, transparent, designed to run across the top of the live plate behind the greeting.
A thin band of the cloak's star scatter with the gold trim line running through it, fading out at
both ends. This is the piece that makes the live state feel like an event rather than a colour
change. Test it against the rose hem — if it competes, thin it.

### 12. Emote / sticker set — 3 to 5

**512 × 512** each, transparent, but **check they read at 32 px** — that is the size Discord and
Twitch actually use. Chibi, in the cloak. On-site they would dress the 404 and the support tiers;
in the app they are optional decoration for the empty states and the notification screen.

---

## Delivery

- Transparent PNG **and** layered source for every raster piece; SVG for #6 and #10.
- **No baked shadows, glows or vignettes.**
- Check every piece against `--page #121829`, `--card #1A2138` and `--cloth #3E4A6B` — three
  different values, and something drawn for one of them can vanish on another.
- File names, so they land without renaming:
  `icon-fg.png` · `icon-bg.png` · `icon-1024.png` · `icon-notification.png` ·
  `portrait-offline.png` · `portrait-live.png` · `splash-mark.png` · `wordmark-night.svg` ·
  `empty-practice.png` · `empty-offline.png` · `empty-unwritten.png` ·
  `motif-crescent.svg` · `motif-star.svg` · `divider.svg` · `live-band.png`

## ⚠ The licence question — please answer this before anything is committed

Astrolabe is **AGPL-3.0**, and every file in the repository is published under it. That is fine for
code and for fonts licensed OFL. **It is not automatically fine for your drawings.** Three options,
and only you can choose:

1. **Licence the artwork under the AGPL too.** Simplest, and consistent. It also means anybody may
   fork the app, keep your face on it, and ship it.
2. **Dual-licence: code AGPL, artwork under a separate, restrictive licence** (e.g. all rights
   reserved, or CC BY-NC-ND). Common for exactly this reason. Needs a clear `ASSETS-LICENCE` file
   and a note in the readme; forks must then replace the art.
3. **Keep the artwork out of the public repository** and ship it only in the store build. This
   costs you the "everything is public" claim, and the app must then be designed to look finished
   without any of it — which, as it happens, it already is.

The design system assumes **(2)** until you say otherwise, because it is the only one that keeps
both the open repository and your control of your own face. Every art-absent state in the app is
built and shipped, so option (3) is genuinely available if you want it.
