# Licences

Two licences, deliberately. **Confirmed by Shruti, 10 September 2026.**

## Code — AGPL-3.0

Everything that is not artwork: the Flutter source, this design system's CSS and components, the
UI kit, the documentation. Published, forkable, and copyleft.

## Artwork — © Shruti, all rights reserved

**Her drawings are not under the AGPL.** This covers every hand-drawn asset in
`guidelines/artwork-spec.md`:

- the app icon (foreground and background layers), the notification icon, the splash mark
- the Home portraits, offline and live
- the wordmark and any re-cut of it
- the empty-state drawings, the motifs and dividers, the live band
- any emote, sticker, outfit sheet or character art

A fork may take the code. **It may not take her face.** A fork must replace every asset listed
above with its own, and the app is built so that it can: every placement has a designed
art-absent state and ships looking finished with no drawings at all.

### What must be in the app repository

```
LICENSE            AGPL-3.0, for the code
ASSETS-LICENCE     this file's artwork section, verbatim
assets/art/README  a one-line pointer to ASSETS-LICENCE beside the drawings
```

The readme needs one sentence near the top, so a forker learns it before they clone rather than
after:

> Astrolabe's code is AGPL-3.0. **The artwork is not** — it is © Shruti, all rights reserved. See
> `ASSETS-LICENCE`. Every art placement in the app has a designed state without art, so a fork
> builds and ships without the drawings.

## Fonts, all shipped

| | |
|---|---|
| EB Garamond | OFL-1.1 — redistribution fine |
| Commissioner | OFL-1.1 — redistribution fine |
| AstroSymbols | OFL-1.1 — the bundled 29-glyph cut |
| Material Symbols Outlined | Apache-2.0 |
| Swiss Ephemeris | AGPL-3.0 — which is why the app is AGPL rather than MIT |

All five are compatible with an AGPL repository. Nothing needs replacing.

## ⚠ Not deployed

This design system is a **handoff package**, not a commit. Nothing here has been pushed to
`ShrutiVtuber/astrolabe` or to `ShrutiVtuber/shrutivtubersite`. Hand the zip to the developer
agent; the licence files above are for them to add.
