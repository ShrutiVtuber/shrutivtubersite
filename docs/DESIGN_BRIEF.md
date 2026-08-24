# Design brief — shrutivtuber.com

**For:** a Claude design agent
**Deliverable:** a complete visual design system and mockups for every surface below
**Quality bar:** must stand next to a hololive / VShojo talent page without flinching

---

## 1. Who this is for

**Shruti** — a VTuber whose niche is **programming: building applications and tools
for magickal and astrological practice.** Not a variety streamer with an occult
aesthetic. She genuinely ships the software.

Her published work, which is the proof behind the brand:

- **Theourgia** (<https://theourgia.com>) — a large open-source magickal journal CMS
  and practitioner's toolkit. Attic lunar calendar, Swiss Ephemeris astrology,
  planetary hours, six divination systems, sigil generation, gematria, offerings
  ledger, federation. Authored under her magickal motto.
- **BeeRanked** (<https://beeranked.online>) — a commercial SEO CMS SaaS.

She is a practising Greek theurgist under Hekate and an OTO member. Based in
Athens (GMT+3). Secondary texture, not the thesis: polyglot — the current site
greets in English, Greek and Hindi, and the old archive is French study notes.

### The two names — settled, please don't reinterpret

**Shruti is the brand, and it is her real name.** Shruti Swara. She is part
Indian and part Greek, so the Sanskrit name and the Greek theurgy are not two
themes in tension — they are one person. Treat that as an asset the design can
lean on, not a contradiction to smooth over.

Her magickal motto **Soror Eu. A.** is the *signature* on magickal work — never
a handle, a slug, or a second logo. It should read like a seal or a mark at the
foot of a page.

| Layer | Name | Where it appears |
|---|---|---|
| Person / brand | **Shruti** (Shruti Swara) | Site title, hero, nav, socials, footer |
| Signature | **Soror Eu. A.** | Byline on magickal writing; the About page |
| Product / house | **Theourgia** | The software, on `/work` and the tool pages |

**Two voices, two sections.** She has a genuine practitioner biography *and* a
character layer. Keep them visually and typographically distinct on the About
page — a real Description block and a separate Lore block. Conflating them is
exactly what makes occult-adjacent creators read as performance rather than
practice, and avoiding that is the central craft problem of this brand.

**Pseudonymity is not in play.** The avatar is aesthetic, not protective —
people already know both names. So the footer must carry a proper legal imprint
(entity name, a *virtual office* address, role email, company and VAT number).
Design the footer to hold it from day one; retrofitting an imprint is how home
addresses leak.

### Tone

Practitioner, not merchant. Competent, warm, a little arcane — a working
instrument-maker's bench, not a fortune-teller's booth. Avoid: crystal-ball
kitsch, purple-and-gold "mystic" clichés, Nordic-rune-fantasy, and casino-tarot
imagery. The register to aim for is closer to a beautifully made observatory
instrument, an astronomical almanac, or a well-set grimoire — precision with
atmosphere.

---

## 2. Existing assets — all fetchable right now

The old WordPress site is still live, so you can pull these directly:

| Asset | URL | Size / notes |
|---|---|---|
| Wordmark (hi-res, transparent) | <https://shrutivtuber.com/wp-content/uploads/2024/01/Logo.png> | 2778×1000 RGBA — **the primary reference** |
| Wordmark (small, transparent) | <https://shrutivtuber.com/wp-content/uploads/2024/01/Logo-500px-by-100px-transparent.png> | 500×180 RGBA |
| Clouds / sky motif | <https://shrutivtuber.com/wp-content/uploads/2024/01/Clouds.png> | 2026×2837 — twilight sky |
| Character avatar | <https://shrutivtuber.com/wp-content/uploads/2024/07/Profile-Picture.png> | 467×467 RGBA |
| Avatar (square crop) | <https://shrutivtuber.com/wp-content/uploads/2024/07/cropped-Profile-Picture.png> | 512×512 RGBA |
| The current site (being replaced) | <https://shrutivtuber.com> | WordPress, dormant since Aug 2024 — **do not use as design reference**, only as content reference |

### Palette sampled from those assets

Not a suggestion — this is what her existing art actually is. Treat it as the
seed and refine it into a real system.

**Wordmark** — a blue→pink gradient:
`#70B0E0` `#A0D0F0` `#60B0E0` sky blues · `#E0A0D0` `#F080A0` pinks · `#F0E0F0` pale lilac

**Clouds** — twilight sky:
`#305080` `#306080` `#406090` deep blues · `#B07080` `#C08090` `#E0B0B0` rose/mauve · `#505070` slate

**Avatar** — `#306080` deep blue · `#A02030` red accent · `#D0B0A0` skin · `#F0C0D0` pink

The coherent story across all three is **dusk / dawn sky** — deep blue through
sky blue into rose. That is a genuinely good fit for an astrology-and-magick
brand and it is already hers. Build from it rather than replacing it, and note
that it gives you a natural light theme (dawn) and dark theme (dusk) that are
the *same palette at different hours* rather than an inversion.

---

## 3. Hard constraints — please read before designing

1. **Every block must look deliberate with NO art.** Art is being commissioned
   slowly and much of it is physically in Athens. The content model makes every
   image a nullable reference and every block individually hideable. So each
   component needs **two designed states: art-present and art-absent** — and the
   art-absent state must look intentional, not broken. This is the single most
   important constraint in this brief. A design that only works once a full
   character sheet exists is a design that cannot ship.

2. **Three theme states, not two.** Light, dark, and *system-default*
   (un-stamped). Define the complete palette on `:root`, redefine tokens under
   `@media (prefers-color-scheme: dark)`, and again under an explicit dark
   selector. Never let a colour exist only inside a media query.

3. **Type must cover Latin + Greek + Devanagari.** The site ships in EN / EL /
   HI / FR. `Καλώς ήρθατε` and `स्वागत` are real content, not decoration. Pick
   faces that genuinely support all three, or specify a deliberate fallback per
   script. Greek coverage in particular rules out many display faces.

4. **Deliver tokens as CSS custom properties**, plus a Tailwind v3 preset. The
   build is Astro 6 + Tailwind via PostCSS. Name tokens semantically
   (`--surface`, `--ink`, `--accent`) not literally (`--blue-500`).

5. **Performance is a brand attribute.** The homepage's job is a ten-second
   conversion. Zero-JS by default; animation must respect
   `prefers-reduced-motion`; no layout shift on the live badge.

6. **Accessibility**: visible focus states on everything interactive, AA contrast
   in both themes, real landmarks, and don't encode meaning in colour alone
   (the live indicator especially).

---

## 4. Surfaces to design

Every one of these needs a full mockup. Mobile and desktop.

### Global chrome
- **Header / nav** — wordmark, primary nav, live badge, language switcher. Needs
  a scrolled/compact state.
- **Footer** — socials, legal links, the Soror Eu. A. seal, copyright
  (© ShrutiVTuber, LLC), sitemap links.
- **Live badge** — three states: **live** (with title + game + viewer count),
  **offline** (with next scheduled stream if known), **unknown** (the API failed;
  must degrade gracefully and never falsely claim live).
- **Language switcher** — EN / EL / HI / FR.
- **404 and 500 pages** — in character.

### 1. Home
The ten-second conversion. Needs: hero (character art present *and* absent
variants), one-line thesis, live badge, primary CTA, social links row, a strip
of latest videos, next stream, a teaser for `/work`, and a journal teaser.

### 2. About / lore
The agency-tier surface. Bio and lore prose; a **profile field block** using the
canonical VTuber vocabulary — birthday, height, debut date, fan name, oshi mark,
stream tag, fan-art tag; a **credits list** (illustrator, rigger, 3D, logo, BGM —
each a name plus link); and the two-names section where Shruti and Soror Eu. A.
are explained. Costume/outfit gallery — design it, even though art will fill in
later.

### 3. Work ← *the page that makes her different*
Theourgia, BeeRanked, and whatever follows. Per project: name, tagline,
description, status (active / maintained / archived), repo link, live link,
screenshot slot. This page carries more weight than the VOD strip does. It should
feel like a portfolio of instruments, not an app store listing.

### 4. Schedule
Upcoming streams with **timezone conversion** — she authors in Athens time
(GMT+3) and the visitor sees their own. Needs a designed empty state ("no
upcoming streams") because that is the current reality and may recur.

### 5. Videos / VODs
Auto-pulled grid. Card design, hover state, platform badges (Twitch / YouTube),
loading skeletons, empty state.

### 6. Journal
Content lives in BeeRanked and is mounted at `/journal`, so **you are designing a
spec that a separate system must match** — index, article page, tags, pagination,
author byline (Soror Eu. A. for magickal writing), and the language-variant
switcher. Keep it visually continuous with the rest of the site; it must not read
as a bolted-on blog.

### 7. Press / media kit
How sponsorships actually happen. Audience stats block, brand-safety statement,
past collaborations, downloadable asset pack (transparent PNGs, logo variants,
clear-space rules, hex codes), and a business enquiry route.

### 8. Fan works gallery
Curated fan art with prominent artist credit and links. Grid, lightbox,
submission CTA.

### 9. Derivative work guidelines
The fan-art policy — commercial use, NSFW stance, **AI-training stance**,
clipping and streaming permission, merch rules. Dry legal content that still
needs to feel like part of the site. A clear permitted/not-permitted visual
treatment would earn its place here.

### 10. Contact
Split routes: **business enquiries** vs **everything else**. Form with validation,
error and success states.

### 11. Support
Ko-fi / memberships / merch. Tier cards if memberships happen.

### 12. Privacy · Terms
Long-form legal. Readable typography, anchored subheadings.

### 13. Admin (low priority, but tokenised)
A small React SPA where she toggles blocks visible/hidden, edits text and uploads
art. Functional over beautiful, but it must use the same tokens. Design the list
view, the edit form, and the media uploader.

---

## 5. Components to specify

`SectionHeader` (eyebrow / title / body) · `Hero` (art-present + art-absent) ·
`LiveBadge` (live / offline / unknown) · `SocialLinkRow` · `ProfileFieldTable` ·
`CreditList` · `ScheduleItem` + `TimezoneToggle` · `VideoCard` · `ProjectCard` ·
`FanArtCard` · `StatBlock` · `AssetDownloadCard` · `Button` (primary / secondary /
ghost) · `Form` fields + validation · `Toast` · `Modal` / lightbox · `Tag` /
`Badge` · `Pagination` · `Prose` (rendered markdown) · `EmptyState` ·
`Skeleton` · `LanguageSwitcher` · `Breadcrumb`.

For each: default, hover, focus-visible, active, disabled, loading, empty, error
— in both themes.

---

## 6. What "professional VTuber quality" means here

Concretely, the things that separate an agency page from a Carrd:

- The character art is **composed with** the layout, not pasted on top of it.
- Credits are typographically dignified, not a footnote.
- The live state is a designed moment, not a red dot.
- Empty states are authored, not default.
- There is one memorable motion or atmosphere idea — the twilight sky is right
  there, and a sky that shifts with the site's theme is an obvious, earned move.
  One orchestrated idea, executed well, beats scattered effects.
- It loads instantly.

Spend the boldness in one place and keep everything around it quiet.

---

## 7. Deliverables requested

1. A **design canvas / mockup set** covering every surface in §4, mobile + desktop,
   both themes.
2. A **token sheet** — CSS custom properties + a Tailwind v3 preset, semantically
   named.
3. **Type specification** — faces, scale, weights, and per-script coverage for
   Latin / Greek / Devanagari with fallbacks.
4. **Component specs** per §5 with all states.
5. An **art shot-list** — a prioritised list of exactly what to commission, in the
   order it should arrive, so the site can be filled in incrementally. Mark which
   pieces unlock which surfaces.
6. A short note on the **motion/atmosphere idea** and where it is used.

Where a decision depends on art that does not exist yet, design the art-absent
state first and treat the art-present state as the enhancement.
