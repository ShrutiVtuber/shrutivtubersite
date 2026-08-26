# shrutivtuber.com /compatible — full page design request

**For:** the design agent who built the Shruti design system
**From:** Shruti
**Date:** 2026-08-26
**Deliverable:** one complete page, ready to implement, plus the share-card art
**Live now:** `/compatible` — built by engineers, works correctly, looks like it

---

## 0. What this page is for, and why it is different

Every other page on this site is for somebody who already arrived. **This one
is the front door for people who have never heard of her.**

It exists because of a specific loop she wants to run:

> Two VTubers compare their birth charts → they get an image worth posting →
> they post it and tag each other → their audiences click through → some of
> them make one → repeat.

So this page has one job that no other page on the site has: **make a stranger
want to do the thing within about eight seconds, and make the result worth
posting.** It is the only page where being *delightful* outranks being
*restrained*.

**It must not stop being the same site.** The instruments are exact, the
horoscopes are hand-written, and nothing here claims predictive validity. This
page is the same voice being playful — not a different site wearing a costume.
If it reads like a BuzzFeed quiz we have lost the thing that makes it worth
sharing in the first place.

---

## 1. The mistake this request exists to avoid

The current page was assembled by engineers. Every piece is styled with the
right tokens; **the page is not designed.** It is five stacked sections of
equal weight in a single column, and it opens with a form.

Concretely wrong today:

- **No hero.** The first thing is a standard `SectionHeader` and then a form
  card. There is no moment.
- **The form is the hero by default**, because it is the first solid object.
  Asking a stranger for their birth time before showing them why is backwards.
- **The two sample cards are a 1×2 grid of `<img>`** with a caption under each.
  They are the most persuasive thing on the page and they are laid out like a
  documentation figure.
- **The five bands are an `<ol>`.** They are the fun part — five verdicts with
  real names — and they read like a changelog.
- **Everything is the same width, the same card, the same gap.** Nothing leads.

---

## 2. Scope

**In scope**

- The whole of `/compatible`, top to bottom, every state
- The **share card artwork** — see §6, this is a real deliverable
- Anything you want to add: an illustration, a motif, a device that carries
  across the card and the page

**Out of scope**

- `SiteHeader` / `SiteFooter` — real components, unchanged, do not design chrome
- The comparison result page (`/chart/compare/…`) and the invite landing
  (`/chart/invite/…`). **Note them as follow-ups if you think they need you** —
  they probably do, and the invite page especially is where a stranger lands.
- The natal instrument. Different job, already designed.

---

## 3. Constraints

These are the site's, not this page's, and they are not negotiable.

**Tokens only, never a hardcoded colour** — `--surface-page/card/veil/inset`,
`--ink/-soft/-faint`, `--line/-strong`, `--accent/-hover/-wash`,
`--rose/-hover/-wash`, `--live/-wash`, `--focus-ring`, `--text-*`,
`--leading-*`, `--tracking-*`, `--space-1..9`, `--radius-*`, `--shadow-1..3`,
`--dur-*`, `--ease-*`, `--measure-prose`, `--measure-ui`, three font families.

**One exception, and only one:** the share card art in §6 is drawn server-side
with Pillow and takes literal hex. That is deliberate and already built — card
designs are database rows. Everything on the *page* is tokens.

**Two themes, no switch.** Dawn canonical, Dusk follows the OS. Tokens make
Dusk free; a hardcoded colour breaks it.

**Fonts self-hosted and fixed** — EB Garamond, Commissioner, JetBrains Mono.
**No external requests of any kind.** This site makes zero third-party requests
on every page and that is a property worth more than any font.

**Tiers:** <640, 640–1024, 1024+, 1440+. **WCAG AA in both themes**, visible
focus, ≥44px targets. Body never scrolls sideways, down to 320px.

**No engagement patterns.** No countdown, no popup, no fake scarcity, no "1,247
people compared today" unless we are actually counting and willing to show the
query. Not doing this is why the site is credible, and credibility is the thing
being shared.

**Motion:** welcome here, more than anywhere else on the site — but everything
behind `prefers-reduced-motion` and nothing that delays the form.

---

## 4. The page, section by section

Design all of it. Widths, alignments, gaps, order — yours.

### 4.1 Hero — **the thing that does not exist yet**

The moment. A stranger has landed from a tweet and knows nothing.

Must carry: what it is (compare two birth charts), that it is free and needs no
account, and that it takes seconds. Must feel: playful, celestial, a little
mischievous — not clinical, not mystical-woo.

You have the sky motif, the horizon rule and the seal already in the system.
There is also a real chart wheel available as an SVG if you want the raw
material — it draws in `currentColor` and follows the theme.

**Open question for you:** should the hero show a *filled-in example card*
rather than describe anything? Showing the output first is often the strongest
possible pitch. Your call.

### 4.2 The start form

Fields: name/handle (optional), birth date (required), birth time (optional,
with an "I don't know it" toggle), place (an existing `PlaceField` component —
typeahead, do not redesign it), and a **required consent checkbox** whose
wording is legally load-bearing and must not be shortened or restyled into
invisibility. It may be quiet. It may not be hidden.

Design the "I don't know my birth time" branch as a real state, not an
afterthought — a large share of people genuinely do not know theirs, and the
site's whole character is that it says what it cannot compute rather than
guessing.

### 4.3 Done state — invitation ready

Currently a card with two read-only inputs. This is the **hand-off moment** and
it should feel like being given something.

Must carry: the invitation link, suggested post text, and a clear warning that
their *own* chart link is the only way back. Losing that link loses their chart.

**Consider:** share-to buttons. If you specify them they must be plain links
with no third-party scripts — `https://twitter.com/intent/tweet?…` style, no
SDKs, no pixels.

### 4.4 The card showcase

Two sample cards, and more when she adds designs — **it must not break at three
or five.** These are the most persuasive objects on the page. Give them the
weight that deserves.

### 4.5 The five answers

> Contrary to sect · Hard going · Mixed testimony · Well aspected · Written in
> the same sky

The fun *and* the credibility live here together: they are real terms of art —
testimonies are how a horary astrologer weighs a question, sect is the
day-or-night division. Design them as five distinct things with character, not
as a list. This is the section most likely to be screenshotted on its own.

### 4.6 The honest note

What it is, and what it is not: no prediction, no percentage, authorities have
disagreed for two millennia. **Do not bury this and do not make it an
apology.** On this site, saying what a thing cannot do is part of the appeal.
Design it as confidence, not as small print.

### 4.7 Admin-editable blocks

Prose blocks she writes in the admin render at the bottom. Unknown length,
unknown headings, possibly images. Specify how they sit against everything
above so the page does not fall apart when she adds one.

---

## 5. States you must design

- **First load** — nothing filled
- **Validation failure** — a real error message above the form
- **Done** — invitation ready
- **Unknown birth time selected**
- **Signed in** — no consent checkbox (the account carries it); the form is
  one field shorter and must not look broken
- **One design / three / five** in the showcase
- **No admin blocks** and **several**
- **Both themes, all four tiers**

---

## 6. The share card — a real deliverable

The card is what actually travels. It is generated server-side at 1200×630 and
currently looks correct and plain: avatars either side, the verdict centred,
the count beneath, the top marker below that, the disclaimer, the site name.

**What we need from you:**

- **Two to four finished designs.** Named. Each is a background colour, five
  text colours, and optionally a full-bleed 1200×630 backdrop image. She uploads
  them and adds more herself — they are database rows, not code.
- **Backdrop artwork**, if you want it. There is a scrim option that lays the
  background colour softly behind the text band only, so a busy image can still
  carry legible type.
- **A view on the layout itself.** Element positions are code and can change —
  tell us if the avatars want to be bigger, if the verdict wants to be the whole
  card, if the count belongs somewhere else.

**Non-negotiable on the card:** the disclaimer line stays. A card travels
without its page and must not read as a verdict about two people's
relationship.

**Constraint:** the renderer is Pillow. It can do flat fills, images, circle
masks, lines, rectangles and TrueType text. **No gradients, no blend modes, no
blur, no shadow, no rounded rectangles.** Design within that or tell us exactly
what you need and we will assess it — do not deliver a card that needs a
compositor.

---

## 7. What is already true (do not re-derive)

- Casting, keeping and inviting happen in **one submit**. Do not add steps.
- Avatars are **uploaded by each chart's own owner**, never fetched from a
  social account. Both faces on a card were put there by the people on them.
- The verdict is **one of five bands, never a percentage**, and the count that
  produced it is always displayed beside it. This is settled and is not a
  design decision.
- The page is server-rendered and works with **scripting off**. Anything you
  specify that needs JavaScript must degrade to something usable.
- Sample cards use invented people ("Someone", "Someone else").

---

## 8. Acceptance

- Every section designed, not styled: widths, alignments and gaps decided.
- Both themes, four tiers, no sideways scroll at 320px, AA contrast throughout.
- Zero hardcoded colours on the page; zero external requests.
- The consent checkbox is legible and unmissable.
- The disclaimer is present on both the page and the card.
- A stranger who lands from a tweet understands what this is before scrolling.
- It looks like the same site as `/today` — playful, not different.

---

## 9. Files

- Live page: `frontend/site/src/pages/compatible.astro`
- Card renderer: `backend/shruti/core/sharecard.py`
- Card designs: `card_design` table, admin at Page blocks → Share card designs
- Tokens: `frontend/shared/src/tokens/`
- Sample cards, live: `/api/charts/card-sample.png?design=light` and `…=dark`
