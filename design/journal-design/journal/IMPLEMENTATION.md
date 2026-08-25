# /journal — implementation guide

Companion to `journal.css` and the reference pages in this folder.
Everything below is decided; nothing is left to assembly.

**Date** 2026-08-25 · **Scope** the pages between `SiteHeader` and `SiteFooter`
· **Chrome** out of scope, drawn in the references as a dashed strip only.

---

## 1. The one rule that matters

Every block on a page is a **sibling inside one column**. Header, plate, prose,
record blocks, notes, next-links — all children of `.j-col`, so they share a left
edge and a width by construction, not by coincidence. If a new block appears
later, it goes inside `.j-col`. Nothing gets its own container.

```
.j-page                      max 1120 · pad clamp(16,4vw,40) · 64 top / 80 bottom
  .j-shell                   flex · gap 56 · wrap
    .j-col                   68ch — every article block lives here
    .j-rail                  208 · sticky 24 — TOC, or small print on short entries
```

Two-rail pages (docs, wiki) use the tighter set — the only intentional
difference in the section, because two rails will not fit at 56/68:

```
.j-page--docs                48 top
  .j-shell--docs             gap 40
    .j-nav-rail              208 · sticky · border-right
    .j-col--narrow           62ch  (wiki article: 64ch)
    .j-rail--toc             176 · sticky · border-left
```

Rhythm: **64** page top · **48** between page blocks · **24** inside a block ·
**12** label to content. Each section closes with a hairline (`--line`), never
with whitespace alone.

The rail is never deleted. An article with fewer than three headings gets
`.j-rail--static` carrying filed-under / published / permalink, so the reading
column's left edge is identical on every entry.

---

## 2. Page skeletons

### Hub `/journal/` — `hub.html`

```html
<main class="j-page">
  <header class="j-masthead">
    <div class="j-masthead-text"> p.j-eyebrow--rose · h1.j-h1 · p.j-lede </div>
    <nav class="j-tags">a.j-tag[aria-current=page] + b (count)</nav>
  </header>
  <a class="j-feature">                     <!-- latest entry, 2 columns -->
    <div class="j-feature-media j-plate j-plate--media">  <!-- or <img> -->
    <div class="j-feature-body">  eyebrow · .j-feature-title · .j-feature-dek · .j-card-date
  </a>
  <div class="j-section-head"><h2>Recently</h2><a class="j-more">All content →</a></div>
  <div class="j-grid"> a.j-card × n </div>
  <div class="j-next"><div class="j-next-grid"> a.j-next-card × 3 </div></div>
</main>
```

States: `hub-empty.html` (`.j-empty.j-empty--sky`), `hub-single.html`
(one `.j-feature`, full width, no "Recently" head — never a grid of one).

### All content `/journal/all/` — `all-content.html`

Same masthead. Chronological, grouped by month:
`.j-month-head > h2 + .j-rule + .j-row-date`, then `.j-grid` per month.
Each card's eyebrow carries the type glyph, so a mixed grid stays readable.

### Blog index `/journal/blog/` — `blog-index.html`

Masthead + `.j-count` + category `.j-tags` + `.j-grid` + `.j-pag-bar > .j-pag`.
First page (`blog-index-first.html`): same markup, the entry-range line reads the
total instead, and the previous-page control takes `aria-disabled="true"`.
Page N: `blog-index.html`. Empty: `blog-index-empty.html`.

### Category archive — `category.html`

Masthead (eyebrow "Category", `h1` = name, `.j-lede` = description,
`.j-count` = count), sibling categories in `.j-tags`, then `.j-grid`.

### Article `/journal/blog/<slug>/` — `article.html`, `article-cover.html`

```html
<main class="j-page"><div class="j-shell">
  <article class="j-col">
    nav.j-bc
    <!-- media: exactly one of the two -->
    div.j-plate.j-plate--entry            (no cover — the common case)
    figure.j-cover > .j-cover-frame > img + figcaption.j-caption
    h1.j-h1.j-h1--entry
    p.j-deck
    div.j-meta            byline · time · .j-tags.j-meta-end
    div.j-prose           h2–h4, pre, .j-scroll > table.j-table, blockquote, figure, sup
    aside.j-instrument    cross-link into a tool (never a filled button)
    section.j-notes       .j-note > .j-note-n + p
    section.j-record      the sky at publication  ← always last before next-links
    section.j-next
  </article>
  <aside class="j-rail">  .j-rail-group > .j-eyebrow + a.j-toc-link[.is-current|--sub]
</div></main>
```

Long entry: `article.html`. Short entry with cover art: `article-cover.html`.

### Documentation index `/journal/docs/` — `docs-index.html`

`.j-grid--sections` of `.j-group-card`, each: eyebrow "Section NN", `h2`,
one-line description, `.j-list` of `a.j-row` (dotted leaders + date).

### Documentation page — `docs-page.html`

Three rails as in §1. Two states: `docs-page.html` (three or more headings — TOC rail) and
`docs-page-no-toc.html` (fewer — the rail carries applies-to, last-reviewed and
the source repo instead, and the body column does not move). Sidebar: `.j-nav-group` per section,
`a.j-nav-link[aria-current=page]` for the current page, `.j-nav-sub` for its
in-page anchors (this is the "deep nesting" case). Body ends with
`section.j-record.j-record--prov` — the provenance block — then `.j-next`.

### Wiki index — `wiki-index.html`

Deliberately **not** cards: `.j-legend` then `.j-az` (A–Z columns of
`a.j-row` with a leading `.j-grade`). Encyclopedic navigation weight.

### Wiki article — `wiki-article.html`

Article skeleton at 64ch, plus the graded corpus table:
`.j-legend` above, `.j-scroll.j-scroll--framed > table.j-table.j-table--framed`,
grade cell = `<span class="j-grade j-grade--attested">●</span>` +
`<span class="j-sr">attested</span>` (the word, for screen readers and for
anyone who has not learned the glyph).

### Changelog — `changelog.html`, `changelog-entry.html`

List: `a.j-log-row` = `.j-log-v` (108px) + `.j-log-body` (summary +
`.j-log-counts`) + `.j-log-date` (84px). Hairline rows, not cards — GitHub
gives us many terse entries and cards would waste the page.

Entry: `h1.j-h1--version` (mono) + repo, `.j-meta` with tag and commit,
`.j-lede`, then `.j-groups > .j-group` × 6 in fixed order —
**Added · Changed · Fixed · Deprecated · Removed · Security** — label column
132px. Only `.j-group--security` takes rose; live-red is never used here.

### Sitemap — `sitemap.html` · Not found — `404.html`

Sitemap: `.j-az` grouped by type with counts, `+ n more →` links.
404: `.j-404` (sky) > `.j-veil` — the one full-bleed sky in the section,
because a dead end is the one place atmosphere helps.

---

## 3. Components the section adds

| Block | Class | Rule it carries |
|---|---|---|
| Sky plate | `.j-plate` | The art-absent state. Gradient from `--sky`, closed by a 1px `--horizon-line`. Never a grey box, never a stretched logo. |
| Sky at publication | `.j-record` | Stored per entry, never recomputed. Rose hairline on top, `--text-sm` labels, mono figures. Ends the article; never above the prose. |
| Provenance | `.j-record--prov` | Engine · rule in force · licence · running build. A number without its rule is not an answer. |
| Grades | `.j-grade--*` | `●` attested · `◐` reconstructed · `○` disputed · `—` not dated by us. Always with `.j-legend` on the same page and an `.j-sr` word in the cell. |
| Instrument link | `.j-instrument` | Hairline card, text link, mono path. An invitation, not an ad: no filled button, no "Try now". |
| Scroll box | `.j-scroll` | Wide tables and code scroll here. The page never scrolls sideways at any width. |

Type marks: `☾` writing · `♄` documentation · `☿` wiki · `♃` changelog.
Set as type in EB Garamond via `.j-glyph`, always followed by `&#xFE0E;` in the
data. Zodiac signs (`♈`–`♓`) **must** carry the variation selector or the
browser substitutes a colour emoji font that ignores `color`.

---

## 4. Constraints, restated as checks

- **Tokens only.** `journal.css` contains no colour literal. Dusk needs no rules.
- **WCAG AA, measured.** `_audit.html` also composites every text node against
  its real backdrop — including the sky gradient's three stops and translucent
  veils — in both themes. Currently zero failures across all 19 pages. Two rules
  came out of that pass and must hold:
  **small print is `--ink-soft`, never `--ink-faint`** (ink-faint measures
  3.78–4.44 on the Dawn paper surfaces at 12–13px; it survives only on
  information-free marks — plate glyph, list markers, breadcrumb separators,
  leader rules, disabled pagination), and **small rose text takes
  `--rose-hover`** (plain rose is 4.44 at 12–14px in Dawn; rose-hover is deeper
  at dawn and lighter at dusk, so one token passes both). Rose hairlines,
  borders and the record's top rule are unaffected — they are not text.
- **Two themes, no switch.** Dawn canonical; Dusk from `prefers-color-scheme`.
- **No external request.** Satisfied. The pages link the design system's token
  files individually — never `styles.css`, which imports the CDN
  `tokens/fonts.css` — plus the local `fonts.css` in this folder. Drop the
  binaries listed in `fonts/README.md` into `fonts/` and the section loads from
  your origin only. **Until they are there the references render in the fallback
  stack** (Georgia / system-ui), so judge type with the files in place. Subset
  Latin + Greek into one file per face: the default Google `latin` subset has no
  polytonic Greek, and `U+2600-26FF` must stay in or the type marks fall through
  to a colour emoji font.
- **Three scripts inline.** Greek, Devanagari and diacritic Latin sit in
  headings, body and table cells at the same optical size; the display face
  covers polytonic Greek, the Devanagari fallback is in the stack, and no
  per-script markup is needed beyond `lang`.
- **Figures tabular.** `.j-mono` / `.j-num` set `tabular-nums lining-nums`.
- **Tiers.** 1024 collapses both rails under the body (the docs nav moves above
  via `order:-1` and becomes a multi-column band); 640 tightens padding, drops
  the prose to `--text-body`, stacks the changelog label column; 1440 adds
  margin, not measure. Every auto-fill track minimum is `min(Xpx,100%)` — the
  bare floor pushed the A–Z columns sideways at 320.
- **No horizontal page scroll.** Verified, not asserted: `_audit.html` loads all
  19 pages at 320 · 375 · 640 · 1024 · 1440 in real iframes and reports any page
  whose document scrolls sideways, naming the widest offender. Re-run it after
  any change to a grid or a fixed width. It also renders every page in both
  themes for the visual pass. It is a tool, not a deliverable — do not ship it.
- **Targets ≥44px.** Pagination cells and buttons are 44px minimum.
- **No engagement patterns.** No countdown, no popup, no reading time.
- **Links out are absolute** (`https://shrutivtuber.com/tools/...`);
  section-internal links stay `/journal/…`.

---

## 5. OG image template

1200×630, rendered at publish time and stored beside the entry — same
discipline as the sky block, and no third party learns who asked for the card.

- Safe area 56px top/bottom, 64px sides. Dawn palette always: the card is seen
  on other people's surfaces.
- Sky gradient background, horizon line on the bottom edge.
- Top row: type glyph (44px, rose) + type name (22px Commissioner, caps,
  `.14em`) + date (22px mono, right).
- Title in a veil capsule: EB Garamond 500, **64px**, dropping to 48px past 46
  characters, max 3 lines. Deck 28px, one line, omitted when the title takes 3.
- Bottom row: "Shruti" (28px display) + `shrutivtuber.com/journal` (20px mono).
- Cover art present: art occupies the right 440px, hairline `--horizon-line` at
  the seam, title block reflows to the remaining 760.
- The `Soror Eu. A.` seal appears **only** on magickal writing — never on
  documentation or changelog cards.

---

## 6. Files

```
index.html               front door — every page and state, linked
journal.css              the whole section, scoped under [data-journal]
SAMPLE-DATA.md           every invented figure, and the file it lives in
_audit.html              tier sweep + both-theme thumbnails (tool, not shipped)
fonts.css                self-hosted @font-face — the only font source
fonts/README.md          the eleven binaries to drop in, with subset ranges
hub.html                 hub · populated
hub-empty.html           hub · nothing published
hub-single.html          hub · one entry
all-content.html         /journal/all/
blog-index-first.html    blog index · first page
blog-index.html          blog index · page N + pagination
blog-index-empty.html    index · empty
category.html            category archive
article.html             article · no cover · long · TOC rail
article-cover.html       article · cover art · short · small-print rail
docs-index.html          documentation index
docs-page.html           documentation page · sidebar + TOC + provenance
docs-page-no-toc.html    documentation page · under three headings, no TOC
wiki-index.html          wiki index · A–Z
wiki-article.html        wiki article · graded corpus table
changelog.html           version list
changelog-entry.html     single release · six groups
sitemap.html             /journal/sitemap/
404.html                 not found, inside the section
cover-*.png              generated stand-ins — commission and replace
attic-two-authorities.png  screenshot stand-in
```

The live design document (all pages side by side, with the theme, tier and
chrome switches) is `../Journal.dc.html`.
