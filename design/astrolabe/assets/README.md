# Brand assets

Real files, copied from `ShrutiVtuber/shrutivtubersite@fe25a4c0`. Nothing here was drawn,
reconstructed or approximated.

| File | What it is | Use |
|---|---|---|
| `fonts/AstroSymbols.ttf` | **5.6 KB, 29 glyphs.** The app's own astronomical cut. | Every planet, sign, node, ℞ and degree mark. Declared in `tokens/fonts.css`. |
| `wordmark.png` | 2778 × 1000, transparent | ⚠ Off-palette — see below. |
| `wordmark-small.png` | 500 × 180, transparent | Same caveat. |
| `avatar.png` | 467 × 467, painted sky background | Author chip, share images. Not a cutout. |
| `avatar-square.png` | 512 × 512 | Square crop of the same. |
| `icon-192.png`, `apple-touch-icon.png`, `favicon-32.png` | the **site's** icons | Reference only — the app has no icon yet. |
| `social-card.png` | 1200 × 630 | The site's share card; useful as a colour reference. |
| `card-backdrop-horizon.png` | the site's generated-card backdrop | Reference for share-image composition. |
| `icons/*.svg` | Twitch · YouTube · Discord · X · GitHub · Ko-fi · Bluesky · Mastodon · Instagram · LinkedIn | Platform marks. Tint to the current ink. |

## Rules

- ⚠ **The wordmark is pink-and-blue on transparent, from the WordPress era.** The pale pink
  vibrates on `--page #121829` and the outline disappears. **Never redraw or approximate it.**
  Where a mark is needed, set "Astrolabe" in `--font-display`. A night re-cut is item 6 in
  `../guidelines/artwork-spec.md`.
- **The avatar is a painted square, not a cutout.** Compose it as a framed plate; never try to
  silhouette it.
- **Every image is a nullable reference.** Each placement has a designed art-absent state, and the
  app ships looking finished with none of these present.
- **No app icon, splash, portrait, emote or costume art exists yet.** Do not invent them — the
  drawings are hers, and every one of them is specified in `../guidelines/artwork-spec.md`.
- `AstroSymbols.ttf` carries **exactly** `° ′ ″ ℞ ☉ ☊ ☋ ☽ ☾ ☿ ♀ ♂ ♃ ♄ ♅ ♆ ♇` and the twelve signs.
  Anything else — including the moon-phase circles ○ ◐ ● — falls back to EB Garamond, or should
  use the drawn `MoonDisc` component.

Canonical origins remain at `https://shrutivtuber.com/wp-content/uploads/…` if re-export is needed.
