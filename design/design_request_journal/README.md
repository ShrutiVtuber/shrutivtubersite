# shrutivtuber.com /journal — full page design request

**For:** the design agent
**From:** Shruti
**Date:** 2026-08-25
**Deliverable:** complete, implementable pages — not a component set

---

## 0. The one thing to take from a previous round on a sister project

RebetiChord ran this exact job as two rounds. Round one delivered an excellent
component system — tokens, cards, typography, a TOC rail — and the live pages
still read amateurish, because nobody had designed the **pages**. Their own
post-mortem is worth quoting:

> The author card and the promo band sit at the article column's width; the
> "Continue reading" block below sits in a DIFFERENT, wider container with a
> different left edge. Nothing aligns. Vertical rhythm collapses… Each
> individual piece is styled; the PAGE is not designed.

So: **every page, designed top to bottom, with every width, alignment and gap
decided by you.** The implementer can produce any markup you specify — the
content is re-rendered server-side, not patched with CSS over someone else's
HTML — so specify all of it and leave nothing to assembly.

---

## 1. What this section is

`shrutivtuber.com/journal` is a content section served by **BeeRanked**, a
content engine that renders blog posts, documentation, wiki/reference articles
and changelogs. It carries:

- **Writing** — notes on practice, and on software written as practice
- **Documentation** for the instruments (the ephemeris API, the four calendars,
  the mobile app)
- **Changelogs** for the public tools, sourced from their GitHub repositories
- Whatever content types get added later

The site it sits inside is an astrology and magick practice site: an ephemeris,
four calendars, planetary hours, letter-reckoning. Its posture is exact,
unhurried, and honest about uncertainty — the instruments say which rule
produced a number and refuse to guess when they cannot know. **The journal must
read like the same hand made it.**

---

## 2. The architecture, so you know what you can ask for

BeeRanked syncs published pages as static HTML to the server. An **Astro route
reads them, takes the `<main>` out, and renders that inside the site's own
layout.** Consequences:

- **The site header and footer are the REAL components** — the same
  `SiteHeader` and `SiteFooter` every other page uses, with the live badge, the
  mobile drawer and the session state. **They are out of scope. Do not design
  chrome.** Your pages sit between them.
- **There is no sanitizer and no CSS-only limit.** The implementer transforms
  the markup before rendering, so you may specify any structure you want.
- **BeeRanked's own stylesheet is discarded.** Do not build on it, and do not
  assume any of its visual defaults survive.
- Section-internal links are `/journal/…`. Links out to the site must be
  **fully qualified** — `https://shrutivtuber.com/today` — because
  root-relative hrefs get rewritten into the section and 404.

---

## 3. Delivery format

1. **One self-contained reference HTML file per page and per major state**,
   opening correctly in a browser. These are the acceptance ground truth.
2. **One stylesheet**, `journal.css`, that styles every reference page. No
   "the implementer adds glue" — if a page needs a rule, it is in your file.
   Every selector scoped under `[data-journal]`.
3. **An implementation guide** giving the exact markup skeleton for every page,
   wrappers included, so no structural decision is left to us.
4. **An OG image template spec** for social cards on articles.

`reference/` beside this file contains:

| | |
|---|---|
| `hub.html`, `all.html`, `blog.html`, `docs.html` | the four index pages as they render today |
| `blog-nothing-was-ever-retrograde.html` | an article with code, a blockquote and headings |
| `docs-casting-a-chart.html` | a documentation page with a table and a sidebar |
| `preview-tokens.css` | the site's real tokens, flattened — link this and a reference file renders exactly as it will in situ |
| `preview-fonts.css` | the five faces, from the live domain |
| `CLASS_INVENTORY.md` | every class the current markup uses, and how widely |

Treat the HTML as the input you are replacing, not as a constraint on
structure. The four content pieces in it are real and true — they are about
this site's actual ephemeris API, its actual calendars and two real bugs — so
they are the right length and register to design against.

---

## 4. Fixed constraints

**Tokens, and nothing but tokens.** The section inherits the site's design
system. Never hardcode a colour. Available:

- Surfaces — `--surface-page --surface-card --surface-veil --surface-inset`
- Ink — `--ink --ink-soft --ink-faint`
- Lines — `--line --line-strong --border-w --border-w-strong`
- Accent — `--accent --accent-hover --accent-wash`
- Rose (the secondary, used for marks and grading) — `--rose --rose-hover --rose-wash`
- Live/alert — `--live --live-wash`, `--focus-ring`
- Type — `--font-display --font-body --font-mono`,
  `--text-hero --text-h1 --text-h2 --text-h3 --text-h4 --text-prose --text-body --text-sm --text-xs --text-micro`,
  `--leading-display --leading-heading --leading-prose --leading-body --leading-tight`,
  `--tracking-display --tracking-caps --tracking-eyebrow`
- Space — `--space-1` … `--space-9`; radii `--radius-sm --radius-md --radius-lg --radius-full`
- Depth — `--shadow-1 --shadow-2 --shadow-3`; motion `--dur-1..3 --ease-out --ease-in-out`
- Measure — `--measure-prose --measure-ui`

**Two themes, no switch.** Dawn and Dusk follow the visitor's operating system.
Design Dawn as canonical and check Dusk; every value through tokens means both
work for free, and anything hardcoded breaks one of them. There is deliberately
no theme control on the site and there must not be one here.

**Fonts are self-hosted and fixed.** EB Garamond (display; Latin **and
polytonic Greek**), Commissioner (body; Latin and Greek), JetBrains Mono
(figures and code), Noto Serif Devanagari + Mukta (Devanagari). No external
requests of any kind — no CDN, no Google Fonts, no remote images. The site
proxies even its video thumbnails rather than let a third party see its
readers, and that rule holds here.

**Three scripts run inline, constantly.** This is unusual and it is central:

- Greek, including polytonic — Μεταγειτνιών, δωδεκάτη ἱσταμένου
- Devanagari — पञ्चाङ्ग, Śrāvaṇa Śukla Trayodaśī
- Latin with heavy diacritics — nakṣatra, aṣṭamī, Soror Eu. A.

A heading, a table cell and a body paragraph must all stay level and legible
when a Greek month name sits beside an English sentence. Test with real strings
from `reference/`, not lorem.

**Figures are tabular.** Dates, degrees, versions and times use
`font-variant-numeric: tabular-nums` and the mono face where they align.

**Wide content scrolls inside its own box.** Tables, code blocks and diagrams
get `overflow-x: auto` on their own container. The page body must never scroll
sideways at any width.

**Responsive tiers:** <640, 640–1024, 1024+, 1440+. Readable at 320px.

**Accessibility:** WCAG AA contrast in both themes, visible focus via
`--focus-ring`, ≥44px targets, honest heading order.

**No engagement patterns.** No countdowns, no "X min read" unless we actually
compute it, no popups, no newsletter modal, no fake scarcity. This site's whole
credibility is that it does not do that.

---

## 5. Design every page. The inventory

For each: full-page composition from below the site header to above the site
footer, all tiers, both themes, and every state listed. If BeeRanked can render
it, it needs a reference file.

1. **Section hub** `/journal/` — featured item + latest; states: populated,
   **empty** (nothing published yet), single-item.
2. **All content** `/journal/all/` — the combined chronological index across
   every type, with type shown per row.
3. **Blog index** `/journal/blog/` — first page, page N with pagination, empty.
4. **Category archive** — header with name, description and count; the same
   listing; empty state.
5. **Article** `/journal/blog/<slug>/` — the flagship, most traffic lands here
   from search. Title, standfirst, byline, date, updated date, body. Must
   handle: headings to four levels, code blocks, GFM tables, blockquotes,
   lists, inline code, images with captions, embedded video, footnotes.
   States: with cover image, **without** (most posts have none — the current
   placeholder is an SVG gradient and it must look deliberate), very long, very
   short.
6. **Documentation index** `/journal/docs/` — grouped by section.
7. **Documentation page** `/journal/docs/<slug>/` — sidebar navigation, body,
   and a table-of-contents rail. States: with and without TOC, deep nesting,
   current-page marking, and the small-screen collapse for both rails.
8. **Wiki index and article** — reference material; same prose engine,
   different navigation emphasis.
9. **Changelog** — list of released versions and a single entry. Entries carry
   a version, a date and notes grouped as added / changed / fixed / removed /
   deprecated / security. These come from GitHub for the public tools, so
   expect terse machine-ish text and many entries.
10. **Sitemap page** `/journal/sitemap/`.
11. **Not found**, inside the section.

---

## 6. Components this site needs that a normal blog does not

**The sky at publication.** Every journal entry can carry what the sky was
doing when it was published — this is already built and stored per entry
(`/api/journal/sky`), so it never recomputes. Design a block for it: Sun and
Moon by sign and degree in **both zodiacs**, the tithi and nakṣatra, the Attic
and Thelemic dates. It belongs on an article, and it is the single most
distinctive thing about this journal. It must read as a record, not a
decoration, and it must not shout over the writing.

**Provenance.** Tool pages on the main site carry a card naming the engine,
the rule in force, the licence and the running commit. Documentation pages
should be able to carry the same, because the same honesty applies: a number
without its rule is not an answer.

**Grading.** The festival corpora mark days as *attested*, *reconstructed* or
*disputed*, and list entries they deliberately will not date. If documentation
shows such a table, the grade needs a visual treatment that is legible without
being alarming — it is scholarship, not a warning.

**Cross-links into the instruments.** An article about the Attic calendar
should be able to link into `/tools/attic-calendar` in a way that reads as an
invitation to try it, not an ad.

---

## 7. Voice, for any copy you write

Plain, exact, unhurried. Say what is true including what is not known. No
exclamation marks, no hype, no "unlock" or "supercharge". The empty states
matter most: a section with nothing published should say so plainly and offer
one useful exit, never a fake skeleton or a countdown.

---

## 8. Acceptance

- Every page in §5 has a reference file, in both themes, at all four tiers.
- `journal.css` renders every one of them with no additional rules.
- Nothing hardcodes a colour; Dusk works without a single extra declaration.
- No external network request from any page.
- No horizontal page scroll at 320px, with a wide table present.
- Greek, Devanagari and diacritic-heavy Latin sit correctly in headings, body
  and table cells.
- The article page reads well **without** a cover image, because most posts
  will not have one.
