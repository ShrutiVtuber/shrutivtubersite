# Brand assets

Local copies (from `uploads/`, salvaged off the old WordPress site — the **only** brand assets
that exist; see `uploads/README.md` for the full provenance and palette sampling):

| File | Size | What it is |
|---|---|---|
| `wordmark.png` | 2778×1000, transparent | **Primary reference.** Full wordmark, hi-res. |
| `wordmark-small.png` | 500×180, transparent | Header-sized wordmark. |
| `clouds.png` | 2026×2837 | Dusk sky motif — layer into sky panels (`.sky-clouds`, Hero `clouds` prop). |
| `avatar.png` | 467×467 | Character avatar (chibi, painted sky background). |
| `avatar-square.png` | 512×512 | Square crop of the same. |

Canonical origin URLs remain at `https://shrutivtuber.com/wp-content/uploads/…` if re-export is needed.

Usage rules
- Every image is a **nullable reference**: each placement has a designed art-absent state.
- The wordmark is the only rendered logo — never redraw or approximate it. Where it can't be used,
  render "Shruti" in `--font-display`.
- The avatar is a **square painted image**, not a cutout — compose it as a framed plate
  (Hero does this automatically), never try to silhouette it. Full-body transparent art is
  shot-list #1 (`guidelines/art-shot-list.md`).
- The **Soror Eu. A. seal is typographic** (`seal.css`) until a sigil is commissioned.
- No oshi mark, icon set, costume art, or expression sheet exists yet — do not invent them.

Local files: `seal.css` (typographic seal) · `sky.css` (CSS-only sky panel).
