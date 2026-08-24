---
name: shruti-design
description: Use this skill to generate well-branded interfaces and assets for Shruti (shrutivtuber.com — VTuber who builds software for magickal and astrological practice), either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the README.md file within this skill, and explore the other available files.
If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.
If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

Key files: `readme.md` (brand guide + index) · `styles.css` → `tokens/` (dawn/dusk/system theming) ·
`tailwind.preset.js` · `components/<group>/` (JSX + .d.ts + .prompt.md) · `ui_kits/site/` and
`ui_kits/admin/` (full-screen recreations) · `guidelines/` (specimens + art shot-list) ·
`assets/README.md` (hotlinked brand asset URLs + usage rules).

Non-negotiables: dawn/dusk are one palette at two hours (never an inversion); every image slot has
a designed art-absent state; Soror Eu. A. is a byline seal, never a second logo; no emoji; blue is
interactive, rose is editorial, red means live; sentence case; EB Garamond / Commissioner /
JetBrains Mono with Devanagari fallbacks.
