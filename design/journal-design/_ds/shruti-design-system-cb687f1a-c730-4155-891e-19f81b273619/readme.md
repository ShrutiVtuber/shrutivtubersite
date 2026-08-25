# Shruti — design system

Design system for **shrutivtuber.com**: Shruti, a VTuber whose niche is **programming for
magickal and astrological practice**. She ships real software; the brand's proof is the work.
Register: *practitioner, not merchant* — an observatory instrument, an astronomical almanac, a
well-set grimoire. Precision with atmosphere. Never crystal-ball kitsch, purple-and-gold mystic
clichés, rune-fantasy, or casino tarot.

**Products represented**
- **shrutivtuber.com** — the talent site (home, about/lore, work, schedule, videos, journal spec,
  press kit, fan works, guidelines, contact, support, legal). Astro 6 + Tailwind, zero-JS by default.
- **Theourgia** (https://theourgia.com) — open-source magickal journal CMS & practitioner toolkit
  (Attic lunar calendar, Swiss Ephemeris astrology, planetary hours, six divination systems, sigil
  generation, gematria, offerings ledger, federation). Authored under her motto. The tool pages also
  cover the Hindu lunisolar calendar and letter-reckoning in six scripts.
- **BeeRanked** (https://beeranked.online) — commercial SEO CMS SaaS; also hosts `/journal`.
- **Admin** — small tokenised React SPA (block visibility, text edit, media upload).

**Sources given**
- `uploads/DESIGN_BRIEF-57bec309.md` — the authoritative brief. Supersedes `DESIGN_BRIEF.md`:
  multi-tradition identity, real-name naming, footer imprint, restricted-material marks.
- `uploads/DESIGN_UPDATE_01.md` — update 01 (2026-08-24). Priority answer: **build the tool page
  template**, then `/work` with per-project credits (Name · Role · Stack · Licence · Status). Press
  kit **deferred, not deleted** — the risk it names is auto-broken follower stats rendering as zeroes,
  so the built page uses sample figures with an explicit "live numbers on request" note and no
  automation. Adds: Sophia is the name on her Greek passport as Shruti is the name on her OCI card
  (context for the naming section — both are real; only Shruti is public brand).
- Old WordPress site https://shrutivtuber.com (content reference only, not design reference).
- Brand assets in `assets/` (wordmark, clouds motif, avatar — salvaged from the old site; provenance in `uploads/README.md`).
- No Figma, no codebase, no font binaries, no icon set were provided.

**The two names (settled — don't reinterpret).** *Shruti* is the brand and her **real name** — Shruti
Swara, part Indian and part Greek; site title, nav, wordmark, socials, footer. Never frame it as an
adopted or initiatory name. *Soror Eu. A.* is the signature on magickal work only: About page and
journal byline, a typographic seal (`assets/seal.css`) — never a handle, slug, or second logo.
*Theourgia* is the product/house name, on `/work` and the tool pages.

**Multi-tradition, not Greek-only.** Three initiatory lineages held at once — Hellenic theurgy under
Hekate, Śākta Tantra (Mahāvidyā), Thelema (O.T.O.). A purely Hellenic read misrepresents her; the
Sanskrit and Greek layers are one person. About keeps **two voices**: a Description block
(practitioner) visually distinct from a Lore block (character).

**Disclosure marks** (brief §9a): moon-phase glyphs mark what may be said, at page and section level —
○ public commentary (usually unmarked) · ◐ named, not detailed · ● under seal, not published. Set as
type (eyebrow + hairlines in rose), never an afterthought badge.

**Footer carries a legal imprint** from day one — entity, virtual-office address, role email,
registry + VAT. Pseudonymity is not in play; the imprint prevents home-address leaks.

**The one atmosphere idea: dawn/dusk sky.** Light theme is dawn, dark theme is dusk — the *same
palette at different hours*, not an inversion. This is doctrine, not decoration: her traditions
converge on the twilight junctures (*sandhyā* — dawn and dusk; see `uploads/README.md`), so the two
themes are the two junctures of one sky. Each page gets exactly one sky: the hero/header panel
(`assets/sky.css`), a pure-CSS gradient from zenith to a rose horizon, closed by a 1px horizon line.
Everything around it stays quiet. Clouds art, when present, layers into the sky panel at low opacity;
the sky is fully designed without it.

---

## Content fundamentals

- **Voice**: first person "I" for Shruti; "you" for the visitor. Warm, competent, a little arcane.
  Claims are concrete ("Swiss Ephemeris", "six divination systems"), never vague mysticism.
- **Casing**: sentence case everywhere — headings, buttons, nav ("Watch live", "Read the journal").
  Title Case only for proper nouns (Theourgia, BeeRanked). Eyebrows/labels render uppercase via CSS.
- **No emoji.** Atmosphere comes from astronomical glyphs set in type (☾ ☿ ♄ ○ ◐ ●), used sparingly
  as ornaments, never as information. (The wordmark's hearts are art, not UI — hearts live only
  inside commissioned artwork, never in chrome, copy, or icons.)
- **Multilingual is content, not decoration**: the greeting "Welcome · Καλώς ήρθατε · स्वागत" is real
  copy from her old site; EN/EL/HI/FR variants are first-class.
- **Times are dual**: authored in Athens (GMT+3), always shown with the visitor's local conversion.
  Tabular numerals for all times, counts, coordinates.
- **Empty states are authored**, quiet, and honest. Example (schedule): "The sky is quiet — nothing
  scheduled yet. Streams are announced on Discord first." Never fake liveness; the unknown state of
  the live badge says "Stream status unavailable", never "offline" (and never falsely "live").
- **Bylines**: magickal writing signs "Soror Eu. A."; everything else "Shruti".
- Example hero thesis: "I build instruments for magick." Subline: "Software for astrology, theurgy
  and divination — built live on stream from Athens."

## Visual foundations

- **Colour**: one sky, two hours. Dawn (light): paper `#F8F6F3`, ink `#26304A`, accent blue
  `#33639C`, rose `#A85A76`, live red `#A62639`. Dusk (dark): page `#121829`, ink `#E9E6F0`, accent
  `#8FBEE8`, rose `#E0A4BC`, live `#F07A8C`. Semantic tokens only (`--surface-*`, `--ink*`,
  `--accent*`, `--rose*`, `--live*`, `--sky-*`); three theme states (light / dark / un-stamped
  system) per `tokens/colors.css`. Rose is editorial (highlights, seals, horizon); blue is
  interactive; live-red belongs to the live badge alone. AA contrast in both themes.
- **Type**: EB Garamond (display + prose; Latin/Greek incl. polytonic), Commissioner (UI;
  Latin/Greek), JetBrains Mono (data, times, code; Latin/Greek). Devanagari falls back to Noto
  Serif Devanagari / Mukta by stack order — no per-script markup needed. Scale in
  `tokens/typography.css`; prose measure 66ch; eyebrows are Commissioner 12px/600/+.14em uppercase.
- **Spacing**: 4px base, steps 4·8·12·16·24·32·48·64·96. Page max 1120px, fluid pad.
- **Backgrounds**: flat `--surface-page`; exactly one sky panel per page. No repeating patterns, no
  textures, no grain, no full-bleed photos. Clouds image is an optional low-opacity layer inside sky.
- **Borders**: 1px hairlines (`--line`) do the structural work; hover strengthens to `--line-strong`.
- **Radii**: 4px controls · 10px cards · 16px modals/sky panels · pills for badges and seals.
- **Shadows**: `--shadow-1` resting cards, `--shadow-2` hover, `--shadow-3` floating layers
  (modal, toast, menus) only. Never decorative glows.
- **Cards**: `--surface-card` + 1px `--line` + radius 10 + shadow-1. Hover: line-strong + shadow-2 +
  accent-tinted title. No lift/scale.
- **Hover**: colour deepens (`--accent-hover`), underlines appear/strengthen. **Press**: darken +
  translateY(1px) — never scale-shrink. **Focus**: 2px `--accent` outline, offset 2, always visible.
- **Motion**: fades and small translates only, `--ease-out`, 120/240ms; the sky cross-fades over
  600ms on theme change. No bounces, no parallax. `prefers-reduced-motion` collapses all to 1ms.
  Live badge pulses via opacity (paused under reduced motion; the word "Live" carries the meaning).
- **Transparency/blur**: only the scrolled header (page-tinted, `--blur-veil`) and text capsules
  over the sky (`.sky-veil`). Text over sky always sits on a veil or below the horizon line —
  protection capsules, not gradient scrims.
- **Imagery**: twilight-hued brand art; fan art and screenshots are never recoloured. Screenshot
  slots and art slots are nullable — **every placement has a designed art-absent state** (sky
  panel, veil, or field-note placeholder), the single most important constraint in the brief.
- **Layout**: sticky compact header after scroll; horizon-line hairlines close each section; data
  blocks (profile fields, schedule) use dotted leaders like an almanac index.

## Iconography

No icon assets exist in the sources (the old site used none beyond social logos). Approach:
- **UI glyphs**: [Lucide](https://lucide.dev) via CDN (`lucide@0.454.0` UMD; `<i data-lucide="…">`
  replaced with inline SVG, 1.5px stroke, inherits `currentColor`). Chosen to match the
  precision-instrument register. **This is a CDN substitution, flagged** — if a bespoke set is
  commissioned, swap here.
- **Platform marks** (Twitch, YouTube, Discord, X, GitHub, LinkedIn, Ko-fi): Simple Icons CDN as
  `<img src="https://cdn.simpleicons.org/<slug>/<hex>">`, tinted to the current ink/accent.
- **Astronomical glyphs as type**: ☾ ☽ ☿ ♀ ☉ ♂ ♃ ♄ and moon phases ○ ◐ ● set in EB Garamond —
  brand ornaments (section markers, seals, empty states). Typographic, not emoji; never load an
  emoji font for them.
- **No emoji anywhere.** No icon font. Never hand-drawn SVG approximations of brand marks.

## Component inventory

Exactly the brief's §5 list, grouped by directory under `components/`, plus the accounts set from
handoff 03:
- `brand/` — SectionHeader · Hero (art present/absent) · LiveBadge (live/offline/unknown) ·
  SocialLinkRow · LanguageSwitcher · **LegalImprint** · **SubscribeBlock**
- `cards/` — VideoCard · ProjectCard · FanArtCard · StatBlock · AssetDownloadCard
- `tables/` — ProfileFieldTable · CreditList · ScheduleItem · TimezoneToggle · **NextStation** ·
  **StationTable** · **ExportBlock**
- `forms/` — Button · TextField · TextArea · SelectField · **ConsentCheckbox**
- `feedback/` — Toast · Modal · EmptyState · Skeleton
- `navigation/` — Tag · Badge · Pagination · Breadcrumb · **SignPicker** · **PeriodSwitcher**
- `content/` — Prose (rendered-markdown styles; the journal spec)

**Intentional additions**: TextField/TextArea/SelectField realize "Form fields"; TimezoneToggle
ships beside ScheduleItem as specified. The five bold names above come from handoff 03 and each
carries a rule that must not be diluted — ConsentCheckbox is never pre-ticked or bundled,
SignPicker marks the reader's own sign, PeriodSwitcher renders periods that do not exist yet as
absent rather than errors, SubscribeBlock states the commercial intent at the point of subscription,
LegalImprint ships from day one with a virtual-office address.

## Index

- `styles.css` → `tokens/` (fonts · colors · typography · spacing · effects · print · base)
- `tailwind.preset.js` — Tailwind v3 preset mapping the same tokens
- `assets/` — asset manifest + `sky.css` (sky panel) + `seal.css` (Soror Eu. A. seal)
- `components/<group>/` — JSX + `.d.ts` + `.prompt.md` per component, one specimen card per group
- `uploads/DESIGN_HANDOFF_02_stations.md` — handoff 02 (2026-08-24): solar stations, lunar stations,
  Day at a Glance. Three instruments meant to give someone a reason to open the site daily, and all
  three work with no account.
- `uploads/DESIGN_HANDOFF_03_accounts.md` — handoff 03 (2026-08-24): accounts, horoscopes,
  newsletter, and the consent/rights constraints.
- `ui_kits/site/` — shrutivtuber.com recreation, all §4 surfaces (Home · About · Work · Schedule ·
  Videos · Journal · Press kit · Fan works · Derivative guidelines · Contact · Support ·
  Privacy/Terms · 404/500) plus handoff 02's daily instruments (Day at a glance · solar stations ·
  lunar stations) and handoff 03's signed-in half (sign up with the three-consent block ·
  sign in · magic-link check-your-email · nativity form · profile · consents, export and delete ·
  horoscope index and reading · newsletter subscribe, confirm, unsubscribe, preferences, archive),
  interactive, theme-switchable, responsive
- `email/` — the two send-ready templates: `newsletter-issue.html` and `optin-confirm.html`.
  Table-based, dark-mode safe, readable with images blocked, no tracking pixel
- `ui_kits/admin/` — admin SPA (list · edit · uploader)
- `templates/coming-soon/` — the holding page for the domain while the rest is under construction.
  Refuses to be a placard: the sky panel is the page, and the station countdown is a **real clock**
  (a `setInterval` in the logic class, not a mocked string), so the page is already an instrument on
  the day it goes up. Today in four reckonings underneath it, the rule it used stated in mono, then
  double-opt-in subscribe with the commercial intent named at the point of consent, then where she
  actually is in the meantime. Says what it is — *“the site is being built”* — instead of teasing.
  Tweaks: theme · phase (building / opening) · preset (Hellenic attributions or times only)
- `templates/` — **seven tool pages off one layout**, the site's differentiator. `tool-page/` is the
  reference layout (planetary hours); `pancanga/`, `hindu-calendar/`, `attic-calendar/`,
  `natal-chart/`, `isopsephy/`, `sigil-generator/` are the rest. Every one carries the same five
  moves required by update 01:
  a **first-class disagreement control** at the top (never a settings-page preference, each option
  with its one-line rule, neither defaulted-correct, and the results genuinely recompute) — sunrise
  definition for planetary hours and pañcāṅga, amānta vs pūrṇimānta month naming for the Hindu
  calendar, tropical/whole-sign vs sidereal/Lahiri for the chart, observed crescent vs conjunction
  for the Attic calendar, six scripts for isopsephy, three methods for sigils; a **parameter panel**
  (six ayanāṁśas, six house systems, four eras, four city calendars, classical vs modern authority);
  a designed **cannot-compute state** (no sunrise at the pole · the day with no beginning · unknown
  birth time · outside the attested range · two authorities, two dates · characters with no numeral
  value · nothing left to draw) — each offering honest alternatives instead of a fabricated answer;
  a **shareable URL** row; and **provenance as a credibility mark** (engine, the rule in force,
  licence, version, offer of source for the running build). The chart wheel and the sigil are
  art-absent plates by design.
  Tweaks on each: theme · the disagreement control · instrument state
- **Isopsephy covers six scripts** — Greek (Milesian, with digamma/koppa/sampi), Hebrew (absolute
  gematria, finals unvalued), Arabic (abjad ḥisāb, eastern order, ghayn 1000), Coptic (soou/fai/shai),
  Devanagari (kaᚭapayādi) and English (ordinal). RTL input and tiles for Hebrew and Arabic.
  Devanagari is deliberately **not** forced into the Greek shape: kaṭapayādi is place-value, so the
  page gives digits read right-to-left and no sum, states why, and only ever matches within one
  system — a Greek sum and a Hebrew sum of equal value are not a correspondence.
- `guidelines/` — foundation specimen cards; `guidelines/art-shot-list.md` (commissioning order)
- `SKILL.md` — agent-skill entry point

## Caveats

- **Press kit is built but held back** — deferred at the client's request, to ship with the developer
  handoff. It deliberately avoids the failure mode update 01 names (automated follower stats going to
  zero when the automation breaks): figures are sample values with "live numbers on request" stated
  in the page, and nothing is wired to an API.
- **Tool-page data is plausible sample data**, not live computation — the ephemeris values, tithi
  endings, chart positions and Attic dates are authored to be realistic and internally consistent so
  the layouts can be judged. The reckoning logic a developer must write is described in each page's
  "how it is reckoned" and provenance blocks.
- **Fonts load from Google Fonts CDN** (`tokens/fonts.css`); no binaries were provided. Faces were
  chosen for real Greek coverage; swap files in and add `@font-face` when licensed binaries exist.
- **Brand PNGs now live in `assets/`** (copied from `uploads/`); canonical origin URLs are kept in
  `assets/README.md` in case re-export is ever needed.
- **The avatar is a square painted image** — Hero composes it as a framed plate on the horizon.
  Full-body transparent art (shot-list #1) unlocks the true composed art-present hero.
- No oshi mark exists yet — sample copy marks it "to be chosen", never invents one.
- **No drawn seal/sigil exists**; Soror Eu. A. is typographic until one is commissioned (shot-list #6).
- The journal is a **spec** for BeeRanked to match, not a build.
- Footer imprint values (street, GEMI, VAT) are bracketed placeholders awaiting the real registration.
