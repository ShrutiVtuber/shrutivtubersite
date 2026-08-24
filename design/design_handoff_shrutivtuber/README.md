# Handoff — shrutivtuber.com

**Prepared for:** the implementing developer agent
**Date:** 2026-08-24
**Design system:** Shruti (this repository)

---

## 0. The mandate — read this first

**Implement the design. Do not interpret it.**

This bundle is a finished design, not a mood board. Every colour, size, hairline, empty state and
line of copy in it was decided deliberately and reviewed. Your task is a **1:1 implementation**:
recreate these designs exactly in a production stack, and plug the real functionality in behind
them.

Concretely, this means:

**Do**
- Reproduce layout, spacing, type, colour, borders, radii, shadows, hover/focus/active states and
  motion exactly as specified here and as shown in the reference files.
- Reproduce the copy verbatim, including empty states, error messages and the "cannot be reckoned"
  text. The wording is part of the design.
- Replace the sample data in the tool pages with real computation (§7). This is the one place you
  are expected to write substantial new logic.
- Use the design tokens as tokens. Reference `var(--ink)`, not `#26304A`.
- Ask the design owner when something is genuinely unspecified. A question costs less than a
  redesign.

**Do not**
- Re-style, "modernise", tidy, or improve any part of the design. Not the palette, not the type
  scale, not the density, not the copy voice.
- Substitute your own component library's defaults for the specified components. If the codebase
  has a `Button`, it must be made to match this `Button`, not the reverse.
- Add sections, cards, icons, gradients, illustrations, animations, or statistics that are not in
  the design.
- Remove the designed art-absent states in favour of "we'll add images later". The art-absent state
  **is** the design (§4.1).
- Drop the disclosure marks, the legal imprint, or the two-name distinction. These are
  non-negotiable (§4).
- Introduce emoji anywhere.

Where you believe the design is wrong, implement it as specified and raise the issue separately.
Do not resolve it in code.

---

## 1. Overview

shrutivtuber.com is the talent site for **Shruti** — a VTuber whose subject is programming for
magickal and astrological practice. She ships real software; the site's job is to prove that.

The site has three parts:

1. **The talent site** — 13 public surfaces (home, about, work, schedule, videos, journal, press,
   fan works, guidelines, contact, support, legal, error pages).
2. **Seven tool pages** — browser-side instruments from her open-source project *Theourgia*. These
   are the site's differentiator and the only place real computation lives.
3. **A small admin SPA** — block visibility, text edit, media upload.

## 2. About the design files

The files in this bundle are **design references written in HTML**. They are prototypes that show
intended appearance and behaviour. They are not the production build and should not be shipped as-is.

Your task is to **recreate them in the target stack**, which the brief specifies as:

- **Site:** Astro 6 + Tailwind CSS v3 via PostCSS, **zero-JS by default**. Interactivity is added
  per-island only where the design requires it.
- **Admin:** a small React SPA, tokenised from the same system.
- **Journal:** content lives in an external CMS (BeeRanked) mounted at `/journal`. The journal files
  here are a **spec that CMS output must match**, not a page to build.

Two formats appear in the bundle:

| Format | Where | How to read it |
|---|---|---|
| React + Babel prototypes | `ui_kits/site/`, `ui_kits/admin/` | Interactive. Open `index.html`. A demo bar bottom-right toggles theme, art-present/absent, live state, empty states, 404 and 500. |
| Design Components (`.dc.html`) | `templates/*/` | The seven tool pages. Open directly in a browser. Each has tweakable props for theme, its disagreement control, and its instrument states. |

`components/*/*.jsx` are **reference implementations with `.d.ts` prop contracts and `.prompt.md`
usage notes**. Treat the `.d.ts` files as the component API specification — match the prop names and
variants exactly so the two codebases stay comparable.

Styling in the `.dc.html` tool pages is written inline. That is an artefact of the prototype format,
**not** an instruction: in production, use the token classes and Tailwind preset.

## 3. Fidelity

**High-fidelity.** Final colours, typography, spacing, states and copy. Recreate pixel-accurately
using the tokens in §5. Nothing here is a placeholder except:

- Bracketed imprint values (`[street, no.]`, `GEMI [000000000000]`, `VAT EL[000000000]`) — awaiting
  real company registration.
- Sample data in the tool pages — replace with real computation (§7).
- Art slots — every one has a designed art-absent state that ships as-is until artwork arrives.
- Press-kit audience figures — deliberately static sample values (§6.7).

---

## 4. Non-negotiable constraints

These five come directly from the client brief. Breaking any of them breaks the project.

### 4.1 Every block must look deliberate with no art
This is the single most important constraint. Artwork is being commissioned slowly; much of it does
not exist. Every image is a nullable reference and every block is individually hideable, so **every
placement has two designed states — art-present and art-absent — and the art-absent state must look
intentional, not broken.** It is implemented throughout this system: the sky panel, the veil, the
"screenshot pending" plate, the field-note placeholder. Preserve all of them. A build that only
looks right once a full character sheet exists is a build that cannot ship.

### 4.2 Three theme states, not two
Light (**Dawn**), dark (**Dusk**), and **un-stamped system default**. The full palette is defined on
`:root`; tokens are re-pointed under `@media (prefers-color-scheme: dark)` **and** again under
`[data-theme="dark"]`, with `[data-theme="light"]` restoring Dawn inside any scope. **No colour may
exist only inside a media query.** See `tokens/colors.css` — copy that structure exactly.

Dawn and Dusk are the same sky at its two hours, not an inversion. Do not generate the dark theme by
inverting the light one.

### 4.3 Script coverage
The site ships in EN / EL / HI / FR. `Καλώς ήρθατε` and `स्वागत` are real content. The font stacks in
`tokens/typography.css` cover Latin, Greek (including polytonic) and Devanagari by stack order — no
per-script markup is needed. Do not substitute fonts without checking Greek and Devanagari coverage.

### 4.4 Disclosure marks
Moon-phase glyphs mark what may be published, at page and section level:

| Mark | Meaning |
|---|---|
| `○` | public commentary (usually unmarked) |
| `◐` | named, not detailed |
| `●` | under seal, not published |

Set as type — an eyebrow plus hairline rules, in rose. Never a badge component, never a coloured
pill. Practitioners read this as a credential; it is a first-class typographic element.

### 4.5 The legal imprint and the two names
The footer carries a full legal imprint (entity, virtual-office address, role email, GEMI, VAT) from
day one. Pseudonymity is not in play; the imprint prevents home-address leaks. Do not defer it.

**Shruti** (Shruti Swara) is her real name and the brand: site title, nav, wordmark, socials, footer.
**Soror Eu. A.** is a signature on magickal work only — the About page and journal bylines, set as a
typographic seal (`assets/seal.css`). It is never a handle, a slug, or a second logo.
**Theourgia** is the product name, on `/work` and the tool pages.

She holds three initiatory lineages at once — Hellenic, Śākta, Thelemic. Profile rows read
`Traditions — Hellenic · Śākta · Thelemic`. Do not render her as Greek-only.

---

## 5. Design tokens

Source of truth: `styles.css` → `tokens/*.css`. A Tailwind v3 preset mapping the same values is at
`tailwind.preset.js`. **Use the tokens; do not inline hex values.**

### 5.1 Colour — Dawn (light)

| Token | Value |
|---|---|
| `--dawn-page` | `#F8F6F3` |
| `--dawn-card` | `#FFFFFF` |
| `--dawn-veil` | `#F1ECEF` |
| `--dawn-inset` | `#ECE7EB` |
| `--dawn-ink` | `#26304A` |
| `--dawn-ink-soft` | `#4A5470` |
| `--dawn-ink-faint` | `#6E7890` |
| `--dawn-line` | `#DCD6DC` |
| `--dawn-line-strong` | `#B9B3BE` |
| `--dawn-accent` | `#33639C` |
| `--dawn-accent-hover` | `#2A527F` |
| `--dawn-accent-wash` | `#E3EDF7` |
| `--dawn-rose` | `#A85A76` |
| `--dawn-rose-hover` | `#914862` |
| `--dawn-rose-wash` | `#F6E7ED` |
| `--dawn-live` | `#A62639` |
| `--dawn-live-wash` | `#F9E9EB` |
| `--dawn-sky-zenith` | `#A9CDEC` |
| `--dawn-sky-mid` | `#D9D3E8` |
| `--dawn-sky-horizon` | `#F2DCD9` |
| `--dawn-horizon-line` | `#C9A9B4` |
| `--on-accent` (Dawn) | `#FFFFFF` |

### 5.2 Colour — Dusk (dark)

| Token | Value |
|---|---|
| `--dusk-page` | `#121829` |
| `--dusk-card` | `#1A2138` |
| `--dusk-veil` | `#232C48` |
| `--dusk-inset` | `#0D1220` |
| `--dusk-ink` | `#E9E6F0` |
| `--dusk-ink-soft` | `#B3B9D2` |
| `--dusk-ink-faint` | `#8B93AF` |
| `--dusk-line` | `#2E3752` |
| `--dusk-line-strong` | `#485272` |
| `--dusk-accent` | `#8FBEE8` |
| `--dusk-accent-hover` | `#A9CDEF` |
| `--dusk-accent-wash` | `#1D2A45` |
| `--dusk-rose` | `#E0A4BC` |
| `--dusk-rose-hover` | `#EBB9CD` |
| `--dusk-rose-wash` | `#2C2338` |
| `--dusk-live` | `#F07A8C` |
| `--dusk-live-wash` | `#33202B` |
| `--dusk-sky-zenith` | `#0B1322` |
| `--dusk-sky-mid` | `#23325A` |
| `--dusk-sky-horizon` | `#6E5470` |
| `--dusk-horizon-line` | `#8A6880` |
| `--on-accent` (Dusk) | `#10182B` |

### 5.3 Semantic roles
`--surface-page` · `--surface-card` · `--surface-veil` · `--surface-inset` · `--ink` · `--ink-soft` ·
`--ink-faint` · `--line` · `--line-strong` · `--accent` · `--accent-hover` · `--accent-wash` ·
`--on-accent` · `--rose` · `--rose-hover` · `--rose-wash` · `--live` · `--live-wash` ·
`--sky-zenith` · `--sky-mid` · `--sky-horizon` · `--horizon-line` · `--sky` · `--focus-ring`

Usage rules, strictly:
- **Blue (`--accent`) is interactive.** Links, buttons, focus rings.
- **Rose (`--rose`) is editorial.** Highlights, seals, the horizon, disclosure marks. Never a button.
- **Live red (`--live`) belongs to the live badge alone.** Nowhere else.
- AA contrast in both themes. Never encode meaning in colour alone.

`--sky` is `linear-gradient(180deg, var(--sky-zenith) 0%, var(--sky-mid) 58%, var(--sky-horizon) 100%)`.

### 5.4 Type

```
--font-display: "EB Garamond", "Noto Serif Devanagari", Georgia, "Times New Roman", serif
--font-body:    "Commissioner", "Mukta", -apple-system, "Segoe UI", system-ui, sans-serif
--font-mono:    "JetBrains Mono", "Noto Sans Devanagari", ui-monospace, "SF Mono", Menlo, monospace
```

Sizes: `--text-hero` `clamp(2.5rem,6vw,3.75rem)` · `--text-h1` `2.25rem` · `--text-h2` `1.75rem` ·
`--text-h3` `1.375rem` · `--text-h4` `1.125rem` · `--text-prose` `1.1875rem` · `--text-body` `1rem` ·
`--text-sm` `.875rem` · `--text-xs` `.8125rem` · `--text-micro` `.75rem`

Leading: display `1.08` · heading `1.2` · prose `1.72` · body `1.55` · tight `1.3`
Weights: display `500` · heading `600` · body `400` · medium `500` · strong `600`
Tracking: display `-0.01em` · eyebrow `.14em` · caps `.08em`

Roles: display and prose in EB Garamond; UI in Commissioner; **all times, counts, coordinates and
code in JetBrains Mono with `font-variant-numeric: tabular-nums`** (`.t-tabular`). Eyebrows are
Commissioner 12px / 600 / `.14em` / uppercase. Prose measure is `66ch`.

Fonts load from Google Fonts (`tokens/fonts.css`). No binaries were licensed. If binaries arrive,
swap in `@font-face` there and keep the stacks.

### 5.5 Spacing, radius, borders
Base 4px: `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96` (`--space-1` … `--space-9`).
Radii: `--radius-sm` `4px` (controls) · `--radius-md` `10px` (cards) · `--radius-lg` `16px`
(modals, sky panels) · `--radius-full` `999px` (pills, seals).
Borders: `--border-w` `1px`, `--border-w-strong` `1.5px`. **Hairlines do the structural work.**
Page: `--page-max` `1120px`, `--page-pad` `clamp(16px,4vw,40px)`.

### 5.6 Elevation and motion

```
--shadow-1: 0 1px 2px rgba(18,24,41,.06)                                        /* resting cards */
--shadow-2: 0 2px 8px -2px rgba(18,24,41,.12)                                   /* hover */
--shadow-3: 0 12px 32px -8px rgba(18,24,41,.26), 0 2px 8px rgba(18,24,41,.10)   /* floating only */
--blur-veil: blur(10px)
--ease-out: cubic-bezier(.2,.7,.3,1)   --ease-in-out: cubic-bezier(.45,0,.25,1)
--dur-1: 120ms   --dur-2: 240ms   --dur-3: 600ms
```

Dusk overrides all three shadows to black-based values — see `tokens/effects.css`.

Motion rules: fades and small translates only. No bounce, no parallax, no scale. Hover deepens
colour and strengthens underlines. Press darkens and applies `translateY(1px)` — **never**
scale-shrink. Focus is a permanent `2px solid var(--focus-ring)` at `outline-offset: 2px`. The sky
cross-fades over `--dur-3` on theme change. `prefers-reduced-motion` collapses everything to 1ms
(already implemented in `tokens/effects.css`). The live badge pulses via opacity only, pauses under
reduced motion, and the **word** carries the meaning.

Shadow is reserved for floating layers — modals, toasts, menus. Never a decorative glow.

---

## 6. Surfaces

Reference build: `ui_kits/site/index.html` (all routes, both themes, all toggles).
Layout shell: `ui_kits/site/site.css` and `Chrome.jsx`.

Global rules for every page:
- Max width `1120px`, fluid padding.
- Header is sticky and gains a compact scrolled state (page-tinted, `--blur-veil`) past 8px.
- Below 960px the primary nav collapses to a **Menu** button opening a hairline-ruled panel; hit
  targets ≥ 44px.
- **Exactly one sky panel per page** — the hero or header panel. Everything around it stays quiet.
  No repeating patterns, no textures, no grain, no full-bleed photos.
- Text over sky always sits on a veil capsule (`.sky-veil`) or below the horizon line. Protection
  capsules, not gradient scrims.
- Horizon hairlines close each section. Data blocks use dotted leaders like an almanac index.
- Footer carries socials, sitemap, the Soror Eu. A. seal, copyright and the legal imprint.

| # | Surface | File | Notes |
|---|---|---|---|
| 1 | Home | `Home.jsx` | Ten-second conversion: hero (art present + absent), one-line thesis, live badge, primary CTA, socials row, latest videos strip, next stream, `/work` teaser, journal teaser. |
| 2 | About / lore | `About.jsx` | **Two visually distinct voices**: a practitioner Description block and a separate character Lore block. Conflating them is the failure mode this page exists to avoid. Plus profile field table, credits list, the two-names section, costume gallery. |
| 3 | Work | `Work.jsx` | The page that makes her different. Per project: name, tagline, description, status, repo, live link, screenshot slot, **and a credit table — Name · Role · Stack · Licence · Status**. Also links the seven runnable instruments. Reads as a portfolio of instruments, never an app-store listing. |
| 4 | Schedule | `Schedule.jsx` | Authored in Athens (GMT+3), always shown with the visitor's local conversion, tabular numerals. Timezone toggle. Designed empty state — that is the current reality. |
| 5 | Videos | `Videos.jsx` | Auto-pulled grid, platform badges, hover state, loading skeletons, empty state. |
| 6 | Journal | `Journal.jsx` | **A spec, not a build** — BeeRanked must match it. Index, article, tags, pagination, byline (Soror Eu. A. for magickal writing, Shruti otherwise), language-variant switcher. Must not read as a bolted-on blog. |
| 7 | Press / media kit | `Press.jsx` | Audience stats, brand-safety statement, past collaborations, downloadable asset pack with clear-space rules and hex codes, business route. **See §6.7.** |
| 8 | Fan works | `FanWorks.jsx` | Grid with artist credit as the loudest text, lightbox, pagination, submission CTA. |
| 9 | Guidelines | `Guidelines.jsx` | Permitted `○` / ask first `◐` / not permitted `●` treatment across fan art, commercial use, AI, clips, voice and likeness. |
| 10 | Contact | `Contact.jsx` | Split routes: business vs everything else. Form with validation, error and success states. |
| 11 | Support | `Support.jsx` | Ko-fi one-off plus two membership tiers; authored no-merch empty state. |
| 12 | Privacy · Terms | `Legal.jsx` | Long-form legal, anchored subheadings, readable measure. |
| 13 | 404 / 500 | `App.jsx` | In character. 404 = "This page is in another sky." 500 = "The instrument slipped." |
| — | Admin | `ui_kits/admin/index.html` | List view, edit form, media uploader. Functional over beautiful, same tokens. |

### 6.7 Press kit — a specific warning
The audience figures on this page are **deliberately static sample values** with "live numbers on
request" stated in the page, and nothing wired to an API.

This is a design decision, not an omission. The client's reference case was an indie press kit that
rendered **nine zeroes** for its follower stats because the automation broke and nobody noticed — a
sponsor reading nine zeroes concludes the audience is zero. If you later wire these to live APIs,
you must also implement a failure mode that hides the block entirely rather than rendering zero.
Never render a zero here.

### 6.8 Live badge
Three states, `min-height: 40px` fixed so there is **no layout shift** between them:

- **live** — title, game, viewer count, opacity pulse.
- **offline** — next scheduled stream if known.
- **unknown** — the API failed. Says "Stream status unavailable". It must **never** claim live, and
  never falsely claim offline. Degrade gracefully.

---

## 7. The tool pages — where you plug the functionality in

Seven pages, **one layout**. `templates/tool-page/` (planetary hours) is the reference; the other six
repeat its structure exactly. Read one carefully and the rest follow.

**All data in these files is plausible authored sample data.** It is internally consistent so the
layouts can be judged. Your job is to replace it with real computation while leaving the layout,
copy and states untouched.

### 7.1 The shared layout, top to bottom

1. Header (site chrome).
2. **Sky hero** — eyebrow `Theourgia · instrument`, instrument name, native-script subtitle where
   one exists, one-sentence description in EB Garamond.
3. **Meta bar** — hairline-bordered mono strip: date · place · the rule currently in force · "shown
   in your local time" · the page's disclosure mark, right-aligned.
4. **Parameter card** — two blocks separated by a hairline:
   - the **disagreement control** (§7.2), and
   - the **parameter panel**: place, date, time, and per-tool options.
5. **Results column** (flex `1 1 520px`) — instrument output, then the share row.
6. **Aside** (flex `1 1 280px`, max `440px`) — "How it is reckoned" prose, the **provenance block**,
   the disclosure note, and the Theourgia link.
7. "Other instruments" hairline row.
8. Footer with imprint.

### 7.2 The disagreement control — the most important pattern here
Each instrument opens with a **first-class control over a real scholarly disagreement**. Requirements,
all mandatory:

- It sits at the **top of the page**, inside the parameter card. It is **never** a settings-page
  preference or a hidden default.
- Each option shows its **one-line rule** in plain language, plus the concrete consequence
  (a time, a degree, a month name).
- **Neither option is presented as the correct one.** No "recommended", no asterisk, no default
  styling that implies primacy. The selected option is marked `✓ in use`.
- Selecting an option **genuinely recomputes the results** — not a label swap.
- The choice travels in the URL, and appears in the provenance block.

| Page | Control | The two answers |
|---|---|---|
| Planetary hours | Definition of sunrise | Hellenistic: upper limb of the visible disc, **with** refraction (06:52 in Athens) · Vedic: centre of the disc, **without** refraction (06:57). **4.6 minutes apart** — enough to move an hour boundary. |
| Pañcāṅga | Definition of sunrise | Same pair. The vāra begins at sunrise, so it moves the whole day. |
| Hindu calendar | Where the month begins | Amānta (new moon to new moon; south/west, Śaka) · Pūrṇimānta (full moon to full moon; north, Vikrama). They agree through the bright fortnight and diverge in the dark one — the demo date is deliberately in the dark fortnight so the divergence is visible. |
| Attic calendar | When the month begins | Observed first crescent (as Athens kept it) · true conjunction (reproducible, unhistorical). Up to two days apart. |
| Natal chart | Which sky, whose houses | Hellenistic: tropical zodiac from the equinox, whole-sign houses, sect and rulership, no orbs · Vedic: sidereal zodiac, bhāva houses, graha dṛṣṭi. ~24° apart — the same birth moves the Sun from Cancer to Gemini. |
| Isopsephy | Which reckoning | Six scripts (§7.4). |
| Sigil generator | Method | Letter collapse (after Spare) · rose cross (Golden Dawn) · planetary square (Agrippa). |

### 7.3 Per-page functional specification

**Planetary hours** — `templates/tool-page/`
Divide sunrise→sunset into twelve equal hours and sunset→next sunrise into twelve more, so hour
length varies with season. Hour 1 belongs to the day's planetary ruler; the rest follow the Chaldean
order `♄ ♃ ♂ ☉ ♀ ☿ ☾`. Highlight the hour containing "now". Show each column's mean hour length.
Compute sunrise/sunset from Swiss Ephemeris **using the selected limb-and-refraction definition**.
Cannot-compute: polar latitude where the Sun does not rise. Offer equal clock hours (labelled as a
substitution), or the nearest date the Sun clears the horizon, or nothing — "the answer stays
undefined, which is itself the answer".

**Pañcāṅga** — `templates/pancanga/`
The five limbs, each with its ending time: tithi (Moon gaining 12° on the Sun), vāra (sunrise to
sunrise), nakṣatra (one of 27 equal sidereal quarters), yoga (summed longitudes), karaṇa (half a
tithi — two often fall in one day). Plus an almanac strip (sunrise/sunset, moonrise/moonset, lunar
month and pakṣa, ayana and ṛtu) and the windows of the day (Rāhu kāla, Yamaghaṇṭa, Gulika kāla,
Abhijit muhūrta) — **reported, not prescribed**. Six ayanāṁśas: Lahiri/Chitrapakṣa, B. V. Raman,
Krishnamurti, Fagan–Bradley, Yukteshwar, True Citrā; the panel states the current shift and that it
can move a nakṣatra boundary. Cannot-compute: no sunrise, so the day has no beginning — the four
Moon-and-Sun limbs can still be given while the vāra is marked undefined.

**Hindu calendar** — `templates/hindu-calendar/`
Year-level companion to pañcāṅga's day view. Today's month, pakṣa and tithi under the selected
scheme; era line in Vikrama Saṁvat / Śaka Saṁvat / Kali Yuga / Bengali San; the 60-year Jovian
saṁvatsara; the solar month. Then the year as a table of months with Gregorian spans and festival
column. **Adhika māsa** (intercalary month, inserted when a lunar month contains no solar
transition) is marked and **carries no festivals — they wait for the *nija* month.** That rule is
authentic; keep it. Note kṣaya māsa as the rarer opposite. Authority selector: Dṛk gaṇita (modern
ephemeris) vs Sūrya Siddhānta (classical tables). Second state — **not an error**: authorities
disagree on a festival date (the tithi ends near sunset and the day-ownership rule is regional).
Show **both** dates with their authorities rather than choosing. Third option in that state is
"ask the people you keep the festival with — this is the answer the software cannot give."

**Attic calendar** — `templates/attic-calendar/`
Month opens at the noumenia, runs full (30) or hollow (29). Twelve months fall ~11 days short of the
solar year, so a thirteenth is inserted 7 times in 19 (Metonic). Days after the twentieth are counted
**backwards** as days remaining. Show today in Greek and transliteration, day number, decad, moon
age, next noumenia; a day table with festivals; an intercalation note. City calendars: Athens
festival, Delos, Delphi, Athens conciliar (prytany) — the conciliar calendar is deliberately out of
step with the festival one. Day begins at sunset or dawn. Cannot-compute: before 432 BCE the Metonic
cycle was not in use and Athens' actual intercalations are not recoverable — give the astronomical
lunation only, or jump inside the attested range. **Never fabricate an archon year.**

**Natal chart** — `templates/natal-chart/`
Positions table: body · longitude · house · dignity, for Sun through Saturn plus node, ascendant and
midheaven. Aspects/configurations list. House systems: whole sign, Placidus, equal, Porphyry,
Regiomontanus, Campanus. Aspect logic **changes with the tradition**: Hellenistic is sign-based
first then by degree, and aspects between non-aspecting signs are not listed however close the
degrees; Vedic graha dṛṣṭi is whole-sign and asymmetric, by rule not by orb — **no orbs invented to
lengthen the list**. Nothing is rounded before display and nothing is interpreted. The chart wheel
is an **art-absent plate** in the design: a sky panel with a mono caption. Implement it as a real
rendered SVG (signs, houses, planets, aspect lines, downloadable as SVG and PNG) drawn from the same
numbers as the tables — but the tables remain the primary reading. Cannot-compute: unknown birth
time. The ascendant moves a degree every four minutes, so houses, angles and sect are undefined.
Offer noon sign positions with the Moon as a range, or manual rectification. **The tool must not
guess a time — a fabricated ascendant is worse than an absent one.**

**Isopsephy** — `templates/isopsephy/` — see §7.4.

**Sigil generator** — `templates/sigil-generator/`
Statement of intent → upper case → letters only → vowels struck (or kept) → repeats struck → the
letter set. **Show every step**; a sigil you cannot reconstruct is one you have to trust someone
else about. Options: vowels, line weight (hairline / broad pen / engraved), enclosure (none /
circle / vesica), timing to the next hour of Venus, Mercury or the Moon. Export SVG, PNG at 2048px,
save to journal. Geometry must be **deterministic** — same input, same figure — and the statement
must **not** be written into file metadata. The drawn sigil is an art-absent plate in the design;
implement as a real SVG path. Cannot-compute: the reduction consumed the sentence (all vowels or
repeats). Offer keeping vowels, a longer statement, or drawing it by hand — "the tool is a
convenience, never a requirement".

### 7.4 Isopsephy — the six scripts

Six systems, six letter tables, **no conversion between them**. Matches are only ever found within
one system: a Greek 598 and a Hebrew 598 are not a correspondence, and the page says so.

| System | Table | Notes |
|---|---|---|
| **Greek** | Milesian numerals | Must include the numeral-only letters: digamma 6, koppa 90, sampi 900. Omitting them silently produces wrong sums for many words. |
| **Hebrew** | Absolute gematria | Aleph 1 … tav 400. Final forms take ordinary values. Mispar gadol / ordinal / katan are separate reckonings, not corrections. |
| **Arabic** | Abjad ḥisāb, eastern order | Alif 1 … ghayn 1000. Abjad order is not alphabet order. Maghrebi order swaps sīn, ṣād, shīn, ḍād — a value quoted without its order is half a value. |
| **Coptic** | Alphabetic numerals | The Greek scheme plus soou 6, fai 90, shai 900. Demotic-derived letters beyond those carry no value — a fact about the system, not an omission. |
| **Devanagari** | **Kaṭapayādi** | See below. |
| **English** | Ordinal A=1…Z=26 | A modern convention with no manuscript behind it, included because it is what people use. Agrippa's Latin table differs — say so. |

**Devanagari is deliberately not additive, and this must not be "fixed".**
Sanskrit has no additive gematria of the Greek kind. The system used is **kaṭapayādi**: four
consonant series run against digits 1–9 and 0 (ka, ṭa, pa and ya all mean 1), standalone vowels are
0, and **in a cluster only the last consonant counts**. The digits are then read **right to left**
(*aṅkānāṁ vāmato gatiḥ*). So the page gives a **place-value encoding, not a sum**: digit tiles, the
assembled number, the rule quoted in Devanagari, and an explicit note that no total is offered
because kaṭapayādi does not make one. Do not add a fake additive total. If the client later asks for
a simple additive Devanagari scheme, it is added **alongside** kaṭapayādi as a separate option.

RTL: Hebrew and Arabic set `dir="rtl"` on both the input and the letter-tile row.

Unreckonable characters: a letter from another script is **not zero — it is outside the system**.
Mark it with a dash, exclude it from the total, and show the `◐ Partly reckonable` state explaining
that transliteration is a decision for the user. **The tool never guesses which letter was meant.**

### 7.5 Shared tool-page requirements

**Results must be linkable.** Every control writes to the URL — place, date, time, and crucially the
disagreement control, ayanāṁśa, house system, era and authority. Without them a reckoning is not
reproducible. The share row shows the URL in mono with a Copy button that confirms "Copied" for
~1.6s. Two privacy carve-outs already designed in: the natal chart warns that birth data in a link
is birth data in a browser history; the sigil page puts the letter set in the link but **not** the
statement, since many practitioners consider it spent once drawn.

**Provenance is a credibility mark, not fine print.** A bordered card in the aside listing engine
(Swiss Ephemeris 2.10.03), the rule in force, licence (AGPL-3.0), version and commit, and
"computed on your device · nothing stored" — closed by a prominent accent link, **"Source for this
running version →"**. These tools are AGPL and the licence obliges an offer of source for the running
build; the developer audience reads visible engineering as the reason to trust the astrology. Wire
the link to the exact build, not to the repo root.

**Every instrument has at least one designed cannot-compute state**, listed per page above. Each one
follows the same shape: the `○` or `◐` mark, a plain-language heading, an explanation of *why* the
answer is undefined rather than zero, and a numbered list of honest alternatives. These states
**will** be seen. They must look deliberate. Never invent a value to fill the space.

**Computation is client-side** and nothing is stored or transmitted. Where the design says "nothing
leaves your device", that is a functional requirement.

---

## 8. Components

`components/<group>/<Name>.jsx` + `<Name>.d.ts` + `<Name>.prompt.md`. The `.d.ts` is the API
contract — match prop names and variant values exactly. One specimen card per group renders the
states side by side in both themes.

| Group | Components |
|---|---|
| `brand/` | SectionHeader · Hero (art present/absent) · LiveBadge (live/offline/unknown) · SocialLinkRow · LanguageSwitcher |
| `cards/` | VideoCard · ProjectCard · FanArtCard · StatBlock · AssetDownloadCard |
| `tables/` | ProfileFieldTable · CreditList · ScheduleItem · TimezoneToggle |
| `forms/` | Button · TextField · TextArea · SelectField |
| `feedback/` | Toast · Modal (panel + lightbox) · EmptyState · Skeleton |
| `navigation/` | Tag · Badge · Pagination · Breadcrumb |
| `content/` | Prose (the rendered-markdown / journal spec) |

Every component needs **default, hover, focus-visible, active, disabled, loading, empty and error**
states in **both** themes. Cards are `--surface-card` + 1px `--line` + `--radius-md` + `--shadow-1`;
hover goes to `--line-strong` + `--shadow-2` + accent-tinted title, **with no lift or scale**.

## 9. Iconography

- **UI glyphs:** Lucide (`lucide@0.454.0`), 1.5px stroke, inheriting `currentColor`. **This is a
  flagged CDN substitution** — no icon set was provided. If a bespoke set is commissioned, swap here.
- **Platform marks:** Simple Icons, tinted to current ink/accent.
- **Astronomical glyphs are type**, not icons: `☾ ☽ ☿ ♀ ☉ ♂ ♃ ♄` and phases `○ ◐ ●`, set in
  EB Garamond. Never load an emoji font for them.
- **No emoji anywhere. No icon font. Never hand-drawn approximations of brand marks.**

## 10. Content rules

- First person "I" for Shruti, "you" for the visitor. Warm, competent, a little arcane. Claims are
  concrete ("Swiss Ephemeris", "six divination systems"), never vague mysticism.
- **Sentence case everywhere** — headings, buttons, nav ("Watch live", "Read the journal"). Title
  Case only for proper nouns. Eyebrows uppercase via CSS, never in the source string.
- Times are dual: authored in Athens, always shown with the visitor's local conversion. Tabular
  numerals for all times, counts and coordinates.
- **Empty states are authored, quiet and honest.** Example: "The sky is quiet — nothing scheduled
  yet. Streams are announced on Discord first." Never fake liveness.
- Bylines: magickal writing signs "Soror Eu. A."; everything else "Shruti".
- Multilingual strings are real content, not decoration.

## 11. Accessibility

Visible focus on everything interactive (already in `tokens/effects.css`). AA contrast in both
themes. Real landmarks. Meaning never in colour alone — the live badge carries its state in the word.
No layout shift on the live badge. Hit targets ≥ 44px on mobile. `prefers-reduced-motion` honoured.
`lang` attributes on non-English runs (`el`, `hi`, `fr`, `sa`, `he`, `ar`) so the right font and
voice are selected.

## 12. Assets

`assets/` — wordmark (2778×1000 transparent, the primary reference), wordmark small, clouds/sky
motif, avatar; plus `sky.css` (the sky panel) and `seal.css` (the Soror Eu. A. typographic seal).
Provenance and original URLs in `assets/README.md`.

Notes: the avatar is a **square painted image** — Hero composes it as a framed plate on the horizon.
Full-body transparent art unlocks the true art-present hero. No oshi mark exists yet; sample copy
marks it "to be chosen" and **must not invent one**. No drawn seal exists; Soror Eu. A. is
typographic until one is commissioned. Fan art and screenshots are **never recoloured**.

`guidelines/art-shot-list.md` is the prioritised commissioning order and states which piece unlocks
which surface. Read it before deciding any art-present path is blocked.

## 13. Files in this bundle

The zip is the design-system project itself. The handoff docs sit in `design_handoff_shrutivtuber/`;
everything else is the design, at the project root.

```
<project root>/
├── design_handoff_shrutivtuber/
│   ├── README.md                             ← this file
│   ├── INSTRUCTIONS_FOR_DEVELOPER_AGENT.md   ← the mandate, in short form
│   └── brief/
│       ├── DESIGN_BRIEF.md                   ← the client's authoritative brief
│       └── DESIGN_UPDATE_01.md               ← corrections; read both
├── styles.css, tokens/, tailwind.preset.js
├── assets/  components/  ui_kits/  templates/  guidelines/
└── readme.md, SKILL.md
```

| Path | What it is |
|---|---|
| `readme.md` | The design system's own overview and decision record. Read after this file. |
| `styles.css`, `tokens/` | Global CSS and all tokens. The source of truth. |
| `tailwind.preset.js` | Tailwind v3 preset mapping the same tokens. |
| `assets/` | Brand art, `sky.css`, `seal.css`, provenance notes. |
| `components/` | 29 components: JSX + `.d.ts` contract + `.prompt.md` notes, with specimen cards. |
| `ui_kits/site/` | The 13-surface interactive site reference. **Start at `index.html`.** |
| `ui_kits/admin/` | Admin SPA reference. |
| `templates/*/` | The seven tool pages (`.dc.html`). Open each directly in a browser. |
| `guidelines/` | Foundation specimen cards (colour, type, spacing, motion, glyphs) + `art-shot-list.md`. |
| `SKILL.md` | Agent-facing entry point to the design system. |
| `_ds_bundle.js` | Compiled component bundle the reference files load. Do not port it — it exists so the references run. |

Every reference file opens and runs offline with no setup — relative paths resolve against the
project root.

**Read `design_handoff_shrutivtuber/brief/DESIGN_UPDATE_01.md` as well as the brief** — it corrects
the brief on the multi-tradition identity, settles the naming, and is the source of the tool-page
priority.

## 14. Suggested order of work

1. Port `tokens/` and `tailwind.preset.js`; verify all three theme states, including un-stamped
   system default, before building any page.
2. Build the chrome — header (with scrolled and mobile states), footer with imprint, live badge with
   its three states and fixed height.
3. Build the component library against the `.d.ts` contracts; check every state in both themes.
4. Build the site surfaces in the §6 order. Home, About and Work carry the most weight.
5. Build the tool pages last, one at a time, starting from `templates/tool-page/` (planetary hours).
   Get the shared layout right once, then vary only the results body and the disagreement control.
6. Wire real computation per §7.3 and §7.4, replacing sample data. Verify each cannot-compute state
   reachable and correct.
7. Audit: contrast in both themes, focus visibility, reduced motion, keyboard paths, no layout
   shift, and every art-absent state still intact.

## 15. Open items — do not invent answers

- Font binaries are unlicensed; Google Fonts CDN is in use and flagged.
- Icon set is a flagged CDN substitution (Lucide).
- Imprint values (street, GEMI, VAT) are bracketed placeholders awaiting registration.
- No oshi mark, no drawn seal, no full-body character art yet.
- Commissioned art arrives incrementally — see `guidelines/art-shot-list.md`.

For any of these, ship the designed absent state and raise the question. Do not fill the gap with an
invention.
