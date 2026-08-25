# /journal implementation — working notes

**Live progress tracker. Update the checklist as work lands.**
Companion to `docs/DESIGN_REQUEST_JOURNAL.md` (the brief we sent) and
`design/journal-design/journal/` (the designer's answer).

---

## The job in one paragraph

BeeRanked's agent syncs published pages to `/srv/journal` as static HTML. An
Astro route reads them and renders inside the site's own `BaseLayout`, so the
section gets the REAL `SiteHeader`/`SiteFooter`. The designer has replaced the
content markup entirely: their skeleton is `.j-page` / `.j-shell` / `.j-col` /
`.j-rail` with `.j-*` classes throughout. So the implementer must **extract the
DATA from BeeRanked's HTML and re-emit it in the designer's skeleton** — not
pass their markup through. That is what rebetichord's injector does and what we
promised the designer in the brief.

## Where things live

| | |
|---|---|
| Designer package | `design/journal-design/journal/` |
| Their guide | `design/journal-design/journal/IMPLEMENTATION.md` — read §1 and §2 first |
| Their stylesheet | `design/journal-design/journal/journal.css` (31KB, zero colour literals) |
| Their references | 19 HTML files in that folder; `index.html` is the front door |
| Their audit tool | `_audit.html` — tier sweep + contrast. A TOOL, not shipped |
| Synced source | `/srv/journal` in the `site` container (volume `journal`) |
| Our route | `frontend/site/src/pages/journal/[...slug].astro` |
| Our reader | `frontend/site/src/lib/journal.ts` |

## Decisions already made (do not relitigate)

- **Their `fonts.css` is NOT used.** We self-host the same faces already, split
  by `unicode-range`, so a Latin reader never downloads Devanagari. Verified
  our EB Garamond includes `greek-ext` (U+1F00–1FFF) so polytonic renders.
  Their eleven-file scheme would be a regression.
- **`.j-*` namespacing accepted** over the `[data-journal]` scoping the brief
  asked for. Checked: zero unprefixed selectors, so nothing can leak.
- **Their sample data is invented and disclosed** in `SAMPLE-DATA.md`. One
  value is impossible: `Anno IVxxxiv` — cycles are 22 years so year 34 cannot
  exist. Real value today is `Vxii`. Use the engine, never their figures.
- The sky-at-publication block is stored per entry (`/api/journal/sky`,
  migration `c9a04e1b78f2`) and never recomputed.
- Links out of the section must be absolute; root-relative gets rewritten into
  the section and 404s.

## Parsing approach

Regex over HTML is what produced the "rendered my own CSS comment as the
article" bug. Use a real parser (`node-html-parser`, small, no jsdom) and
extract structured data per page type, then render Astro components.

## Checklist

- [x] `node-html-parser` added to the site package
- [x] `journal.css` copied into the site and imported by the route
- [x] Type detection: which page type is this path?
- [x] Shared: `.j-page` / `.j-shell` / `.j-col` / `.j-rail` layout components
- [x] Card + row components (`.j-card`, `.j-row`, `.j-feature`)
- [x] Hub (populated / empty / single)
- [x] All content
- [x] Blog index (first / empty) — pagination waits for a second page of entries
- [x] Category archive
- [x] Article (cover / no cover) + TOC rail + static rail fallback
- [ ] Sky-at-publication block, from the stored record
- [x] Docs index
- [x] Docs page (TOC / no TOC) + sidebar + provenance
- [x] Wiki index (A–Z) + wiki article — **no grade dots**: the designer's
      legend (attested / reconstructed / disputed) has no source in BeeRanked,
      and inventing one would be inventing scholarship. Add when there is data.
- [x] Changelog list + entry (six groups, fixed order)
- [x] Sitemap
- [x] 404 inside the section
- [x] Type marks carry `&#xFE0E;` or zodiac glyphs go colour-emoji
- [~] No horizontal scroll at 320 — checked statically, not in a browser:
      the only rule that can exceed 320 is `.j-table{min-width:520px}`, and
      every table is wrapped in `.j-scroll` (`overflow-x:auto`) by the
      parser — verified in the rendered HTML. No headless browser is
      installed here, so the designer's `_audit.html` has not been run.
- [x] Deployed — see the note on verifying it below

## Gotchas already paid for

- Caddy's `/journal/*` also matches bare `/journal`; `handle_path` then strips
  everything and `file_server` answers 200 with an empty body. Fixed with a
  `redir` — do not turn it back into a `handle` block.
- `upsert_plugin` REPLACES rather than patches; send css + slots + flags
  together or the omitted ones are cleared.
- Never put angle-bracket tag syntax in the BeeRanked plugin CSS — it is
  injected into the page and the extractor used to match it.


## Where it got to (2026-08-25)

Every route the section can serve today answers 200 with the real site header
and footer, and a miss answers 404 with the section's own page:

    /journal/            /journal/all/         /journal/sitemap/
    /journal/blog/       /journal/docs/        /journal/<kind>/<slug>/

Built but unverified against real content, because none is synced yet:
**changelog list**, **changelog entry**, **category**, **wiki index**. The
changelog source is GitHub and she has still to wire it in Studio; categories
appear when she files something. `releasesFrom` and `changeGroups` are written
against the general shape of a release list rather than a specific markup —
check them against the first real release.

Not done: **pagination** (nothing has a second page yet) and the
**sky-at-publication** record (`/api/journal/sky` exists; nothing reads it).

### Two bugs found on the way

- `node-html-parser` was left external by Vite, so it resolved at build and was
  missing at run time — 500 on every journal URL. It is in `noExternal` now,
  beside `@astrojs/markdown-remark`, which was there for exactly this reason.
- **All 47 `@font-face` rules were malformed** — `url(url('…'))` — in both
  `frontend/shared/src/tokens/fonts-local.css` and
  `frontend/site/public/fonts/faces.css`. Nothing to do with the journal; the
  font-localisation commit shipped it and prod had been falling back to system
  fonts ever since. Fixed and verified: the faces parse and the woff2 serves as
  `font/woff2`.


## Verifying it on production

The holding page stands in front of every journal URL, so from outside they all
answer 200 with the coming-soon page — including a path that should 404. That
is the holding page working, not the journal failing.

Getting through the gate needs her admin session; the middleware bypass is a
valid operator cookie and nothing else. So the render check on production is
hers to do: sign in, then walk

    /journal/  /journal/all/  /journal/sitemap/  /journal/blog/  /journal/docs/
    /journal/blog/nothing-was-ever-retrograde/  /journal/docs/casting-a-chart/
    /journal/nope/   ← should be the section's 404

What was verified from here: the containers are healthy, production carries the
same nine synced pages the local run was checked against, and the font fix is
live and public (0 malformed faces, woff2 served as `font/woff2`).
