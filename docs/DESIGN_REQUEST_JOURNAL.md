# shrutivtuber.com /journal — full page design request

**For:** the design agent who built the Shruti design system
**From:** Shruti
**Date:** 2026-08-25
**Deliverable:** complete pages, ready to implement — not a component set

You already have the design system, the tokens, the fonts and the site's voice.
This document adds only what is new: a content section, its page types, its
markup, and the constraints that come with the engine behind it.

---

## 0. The mistake this request exists to avoid

RebetiChord ran this same job as two rounds. Round one delivered an excellent
component system — tokens, cards, typography, a TOC rail — and the live pages
still read amateurish, because nobody designed the **pages**. Their own
post-mortem:

> The author card and the promo band sit at the article column's width; the
> "Continue reading" block below sits in a DIFFERENT, wider container with a
> different left edge. Nothing aligns. Vertical rhythm collapses… Each
> individual piece is styled; the PAGE is not designed.

So: **every page designed top to bottom, with every width, alignment and gap
decided by you.** The implementer re-renders the markup server-side and can
emit any structure you specify, so specify all of it. Nothing is left to
assembly.

---

## 1. What the section is

`shrutivtuber.com/journal` is served by **BeeRanked**, a content engine that
renders blog posts, documentation, wiki articles and changelogs. It carries:

- **Writing** — notes on practice, and on software written as practice
- **Documentation** for the instruments: the ephemeris API, the four calendars,
  the mobile app
- **Changelogs** for the public tools, pulled from their GitHub repositories
- More content types later

It must read like the rest of the site: exact, unhurried, honest about
uncertainty. The instruments already say which rule produced a number and
refuse to guess when they cannot know. The journal is the same hand writing.

---

## 2. Architecture — what it means for you

BeeRanked syncs published pages to the server as static HTML. **An Astro route
takes the `<main>` out of them and renders it inside the site's own layout.**

- **The header and footer are the REAL components.** The same `SiteHeader` and
  `SiteFooter` as every other page — live badge, mobile drawer, session state.
  **Out of scope. Do not design chrome.** Your pages sit between them.
- **No sanitizer, no CSS-only limit.** The markup is transformed before
  rendering, so you may specify any structure you want. This is more freedom
  than a normal BeeRanked plugin has.
- **Their stylesheet is discarded.** Do not build on it or assume any of its
  defaults survive. (It was injected once and brought its own `:root` with it —
  `--accent` is a name both systems use, and the site's header links turned
  rose.)
- Section-internal links are `/journal/…`. Links out to the site must be
  **fully qualified** (`https://shrutivtuber.com/today`) — root-relative hrefs
  get rewritten into the section and 404.

---

## 3. Deliver

1. **One self-contained reference HTML file per page and per major state**,
   opening correctly in a browser against the design system's tokens. These are
   the acceptance ground truth.
2. **One stylesheet**, `journal.css`, styling every reference page, every
   selector scoped under `[data-journal]`. If a page needs a rule, it is in
   your file — no implementer glue.
3. **An implementation guide** with the exact markup skeleton per page,
   wrappers included.
4. **An OG image template spec** for article social cards.

---

## 4. Constraints

**Tokens only, never a hardcoded colour.** The section inherits the site's
system — `--surface-page/card/veil/inset`, `--ink/-soft/-faint`,
`--line/-strong`, `--accent/-hover/-wash`, `--rose/-hover/-wash`,
`--live/-wash`, `--focus-ring`, the `--text-*`, `--leading-*`, `--tracking-*`,
`--space-1..9`, `--radius-*`, `--shadow-1..3`, `--dur-*`, `--ease-*`,
`--measure-prose`, `--measure-ui`, and the three font families.

**Two themes, no switch.** Dawn canonical, Dusk following the visitor's OS.
Everything through tokens means Dusk works for free; anything hardcoded breaks
it. There is deliberately no theme control on this site.

**Fonts are self-hosted and fixed** — EB Garamond (display, Latin + polytonic
Greek), Commissioner (body, Latin + Greek), JetBrains Mono, Noto Serif
Devanagari + Mukta. **No external requests of any kind.** The site proxies even
its video thumbnails rather than let a third party see its readers.

**Three scripts run inline, constantly.** This is central and unusual:

- polytonic Greek — Μεταγειτνιών, δωδεκάτη ἱσταμένου
- Devanagari — पञ्चाङ्ग, Śrāvaṇa Śukla Trayodaśī
- diacritic-heavy Latin — nakṣatra, aṣṭamī, Soror Eu. A.

A heading, a body line and a table cell must all stay level and legible when a
Greek month name sits beside an English sentence.

**Figures are tabular.** Dates, degrees, versions, times.

**Wide content scrolls in its own box.** Tables, code, diagrams. The page body
never scrolls sideways, at any width, down to 320px.

**Tiers:** <640, 640–1024, 1024+, 1440+. **WCAG AA in both themes**, visible
focus, ≥44px targets.

**No engagement patterns.** No countdowns, no popups, no fake scarcity, no
reading-time unless we actually compute it. Not doing that is part of why this
site is credible.

---

## 5. Every page, with its states

If BeeRanked can render it, it needs a reference file.

1. **Hub** `/journal/` — featured item + latest. States: populated, **empty**,
   single item.
2. **All content** `/journal/all/` — combined chronological index, type shown
   per row.
3. **Blog index** `/journal/blog/` — first page, page N with pagination, empty.
4. **Category archive** — name, description, count, listing; empty.
5. **Article** `/journal/blog/<slug>/` — the flagship; most traffic lands here
   from search. Headings to four levels, code blocks, GFM tables, blockquotes,
   lists, inline code, captioned images, embedded video, footnotes.
   States: **with and without a cover image** — most posts have none, and the
   placeholder is an SVG gradient that must look deliberate — very long, very
   short.
6. **Documentation index** `/journal/docs/` — grouped by section.
7. **Documentation page** `/journal/docs/<slug>/` — sidebar nav, body, TOC
   rail. States: with and without TOC, deep nesting, current-page marking, and
   how both rails collapse on small screens.
8. **Wiki index and article** — same prose engine, different navigation weight.
9. **Changelog** — version list and single entry. Version, date, and notes
   grouped added / changed / fixed / removed / deprecated / security. Sourced
   from GitHub, so expect terse machine-ish text and many entries.
10. **Sitemap page** `/journal/sitemap/`.
11. **Not found**, inside the section.

---

## 6. Components this site needs that a blog does not

**The sky at publication.** Every entry can carry what the sky was doing when
it was published — already built and stored per entry, so it never recomputes.
Design a block for it: Sun and Moon by sign and degree in **both zodiacs**,
tithi and nakṣatra, the Attic and Thelemic dates. It is the most distinctive
thing this journal can carry. A record, not a decoration, and it must not shout
over the writing.

**Provenance.** The tool pages carry a card naming the engine, the rule in
force, the licence and the running commit. Documentation should be able to
carry the same: a number without its rule is not an answer.

**Grading.** The festival corpora mark days *attested*, *reconstructed* or
*disputed*, and list entries they deliberately will not date. Where
documentation shows such a table, the grade needs a treatment that is legible
without being alarming — it is scholarship, not a warning.

**Cross-links into the instruments.** An article about the Attic calendar
should link into `/tools/attic-calendar` as an invitation to try it, not an ad.

---

## 7. The markup you are replacing

What BeeRanked emits today, inside `<main>`, with text truncated. **You are not
obliged to keep any of this** — the implementer emits whatever your guide
specifies. It is here so nothing in the current output goes unnoticed.

### Hub

```html
<div class="container-wide">
  <section class="hero" data-hero="cover" style="--c:#f59e0b">
    <div class="cover-media">
      <svg>
        gradient placeholder
      </svg>
    </div>
    <a class="cover-card" href="/journal/blog/the-month-that-would-not-open">
      <span class="cover-kicker">
        Latest &middot; Blog
      </span>
      <span class="cover-title">
        The month that would not open
      </span>
      <span class="cover-date">
        Aug 25, 2026
      </span>
    </a>
  </section>
  <div class="hub-body">
    <section class="block hub-latest">
      <div class="section-head">
        <div>
          <h2>
            The latest from Shruti
          </h2>
        </div>
        <a class="more" href="/journal/all">
          All content &rarr;
        </a>
      </div>
      <div class="tthumbs">
        <a href="/journal/blog/nothing-was-ever-retrograde" class="tt-row" style="--c:#f59e0b">
          <span class="tt-thumb">
            <svg>
              gradient placeholder
            </svg>
          </span>
          <span class="tt-body">
            <span class="tt-kicker">
              Blog
            </span>
            <span class="tt-title">
              Nothing was ever retrograde
            </span>
            <span class="tt-date">
              Aug 25, 2026
            </span>
          </span>
        </a>
        <a href="/journal/docs/the-four-reckonings" class="tt-row" style="--c:#14b8a6">
          <span class="tt-thumb">
            <svg>
              gradient placeholder
            </svg>
          </span>
          <span class="tt-body">
            <span class="tt-kicker">
              Documentation
            </span>
            <span class="tt-title">
              The four reckonings
            </span>
            <span class="tt-date">
              Aug 25, 2026
            </span>
          </span>
        </a>
        <a href="/journal/docs/casting-a-chart" class="tt-row" style="--c:#14b8a6">
          <span class="tt-thumb">
            <svg>
              gradient placeholder
            </svg>
          </span>
          <span class="tt-body">
            <span class="tt-kicker">
              Documentation
            </span>
            <span class="tt-title">
              Casting a chart
            </span>
            <span class="tt-date">
              Aug 25, 2026
            </spa
  …
```

### Blog index

```html
<div class="container-wide" style="padding-top: 3.5rem; padding-bottom: 5rem;">
  <div style="max-width: 520px; margin-bottom: 2.5rem;">
    <h1 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.035em; color: var(--text); margin-bottom: 0.5rem;">
      Blog
    </h1>
    <p style="color: var(--text-muted); font-size: 1rem;">
      Articles, guides, and updates, 2 posts.
    </p>
  </div>
  <h2 class="sr-only">
    All entries
  </h2>
  <div class="tthumbs">
    <a href="/journal/blog/the-month-that-would-not-open" class="tt-row" style="--c:#f59e0b">
      <span class="tt-thumb">
        <svg>
          gradient placeholder
        </svg>
      </span>
      <span class="tt-body">
        <span class="tt-kicker">
          Article
        </span>
        <span class="tt-title">
          The month that would not open
        </span>
        <span class="tt-date">
          August 25, 2026
        </span>
      </span>
    </a>
    <a href="/journal/blog/nothing-was-ever-retrograde" class="tt-row" style="--c:#f59e0b">
      <span class="tt-thumb">
        <svg>
          gradient placeholder
        </svg>
      </span>
      <span class="tt-body">
        <span class="tt-kicker">
          Article
        </span>
        <span class="tt-title">
          Nothing was ever retrograde
        </span>
        <span class="tt-date">
          August 25, 2026
        </span>
      </span>
    </a>
  </div>
</div>
```

### Article

```html
<div class="container" style="padding-top: 3rem; padding-bottom: 5rem;">
  <nav style="margin-bottom: 2.5rem; font-size: 0.8rem; color: var(--text-muted); display: flex; align-items: center; gap: 0.5rem;">
    <a href="/journal/blog" style="color: var(--text-muted);">
      Blog
    </a>
    <span style="color: var(--text-muted);">
      /
    </span>
    <span style="color: var(--text);">
      Nothing was ever retrograde
    </span>
  </nav>
  <article>
    <header style="margin-bottom: 2.25rem;">
      <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.09em; color: var(--brand-mid); margin-bottom: 0.7rem;">
        Article
      </div>
      <h1 style="font-size: clamp(1.75rem, 4vw, 2.5rem); font-weight: 800; letter-spacing: -0.04em; line-height: 1.2; color: var(--text); margin-bottom: 0.75rem;">
        Nothing was ever retrograde
      </h1>
      <p style="font-size: 0.825rem; color: var(--text-light);">
        By
        <a href="https://shrutivtuber.com" rel="author" class="byline-author">
          Shruti
        </a>
        · August 25, 2026
      </p>
    </header>
    <div class="prose">
      <p>
        A chart was coming out right in every particular except one. Every planet was direct. All of them, always, at every date I tried.
      </p>
      <h2 id="the-shape-of-the-bug">
        The shape of the bug
      </h2>
      <p>
        Swiss Ephemeris fills the speed slot
        <strong>
          only when it is asked to
        </strong>
        . Ask for a position without
        <code>
          FLG_SPEED
        </code>
        and you get a position, correctly, along with a 
      </p>
      <p>
        Retrograde is derived from speed:
      </p>
      <p>
        ```python
      </p>
      <p>
        retrograde = speed &lt; 0.0
      </p>
      <p>
        ```
      </p>
      <p>
        Zero is not less than zero. So nothing was ever retrograde — not because the arithmetic was wrong, but because the input was a plausible-looking zero rather than a missing value.
      </p>
      <h2 id="why-it-survived">
        Why it survived
      </h2>
      <p>
        Nothing threw. No test failed, because the tests asserted positions and the positions were right. The Moon's daily motion read 
        <code>
          0.00°/day
        </code>
        , which looks like a formatting problem rather
  …
```

### Documentation page

```html
<div class="docs-shell">
  <aside class="docs-sidebar">
    <a href="/journal/docs" class="docs-sidebar-home">
      Documentation
    </a>
    <nav class="docs-nav" aria-label="Documentation">
      <div class="docs-nav-group">
        <p class="docs-nav-section">
          Documentation
        </p>
        <ul class="docs-nav-list">
          <li>
            <a href="/journal/docs/casting-a-chart" class="docs-nav-link is-active" aria-current="page">
              Casting a chart
            </a>
          </li>
          <li>
            <a href="/journal/docs/the-four-reckonings" class="docs-nav-link">
              The four reckonings
            </a>
          </li>
        </ul>
      </div>
    </nav>
  </aside>
  <article class="docs-main">
    <nav class="docs-breadcrumb" aria-label="Breadcrumb">
      <a href="/journal/docs">
        Docs
      </a>
      <span class="docs-breadcrumb-sep">
        /
      </span>
      <span>
        Documentation
      </span>
      <span class="docs-breadcrumb-sep">
        /
      </span>
      <span class="docs-breadcrumb-current">
        Casting a chart
      </span>
    </nav>
    <header class="docs-header">
      <h1 class="docs-title">
        Casting a chart
      </h1>
      <p class="docs-meta">
        By
        <a href="https://shrutivtuber.com" rel="author" class="byline-author">
          Shruti
        </a>
        · Updated August 25, 2026
      </p>
    </header>
    <div class="docs-body wiki-body">
      <p>
        The ephemeris is a small HTTP service. Every instrument on this site is a page over it, and it answers the same questions for anyone who asks.
      </p>
      <h2 id="what-you-need">
        What you need
      </h2>
      <p>
        A moment and a place. The moment is a date and a time; the place is a latitude and a longitude. Nothing else is required, and nothing else is stored.
      </p>
      <p>
        ```
      </p>
      <p>
        GET /chart?date=1990-05-04&amp;time=14:20&amp;lat=37.9838&amp;lon=23.7275
      </p>
      <p>
        ```
      </p>
      <h2 id="what-comes-back">
        What comes back
      </h2>
      <p>
        Both traditions, side by side and unranked. The tropical zodiac and the sidereal one are not two attempts at the same answer — they are two different questions, and the response says so by giving you both rather than choosing.
      </p>
 
  …
```

---

## 8. Acceptance

- Every page in §5 has a reference file, both themes, all four tiers.
- `journal.css` renders all of them with no additional rules.
- No hardcoded colours; Dusk works with no extra declarations.
- No external network request from any page.
- No horizontal page scroll at 320px with a wide table present.
- Greek, Devanagari and diacritic-heavy Latin sit correctly in headings, body
  and table cells.
- **The article reads well without a cover image**, because most will not have
  one.
