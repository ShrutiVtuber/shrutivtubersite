# Instructions for the implementing agent — pack 2

You are implementing a finished design. Read `README.md` in this folder in full, then
`brief/DESIGN_HANDOFF_03_accounts.md`.

**Read the first pack first:** `../design_handoff_shrutivtuber/`. It carries the tokens, the chrome,
the component library and the seven tool pages. Everything here builds on it and assumes it.

The design itself is at the root of this bundle. Start at `ui_kits/site/index.html` and use the demo
bar's **signed in / signed out** toggle.

## Your mandate

**Implement the design 1:1. Do not interpret it.** Every colour, dimension, state and line of copy
was decided deliberately and reviewed. Reproduce those decisions exactly, and plug real
functionality in behind them.

## What counts as done

- The nine surfaces match the reference build, in both themes, at mobile and desktop.
- Copy is verbatim — especially the consent wording, the birth-time explanation, and the deletion
  modal's "what goes / what is kept" lists. That wording is the design.
- Three consents are recorded separately, with version, wording, timestamp and source.
- Export, delete and change-consent all work as in-page controls.
- Double opt-in works end to end: form → email → landing page.
- Unsubscribe works in one click with no login.
- The horoscope period switcher is in place with only monthly available.
- A signed-in reader with a saved nativity sees their own sign without picking.

## Hard rules

1. **Do not pre-tick a consent box, and do not bundle consents.** Three decisions, three checkboxes,
   yes to one and no to another must be possible.
2. **Do not turn "I don't know my birth time" into an error.** It is a first-class choice with an
   explanation of what it costs.
3. **Do not ask for data the ephemeris does not use.** No street address, no phone, no gender field.
4. **Do not build a cookie banner.** Analytics are cookieless; there is nothing to consent to.
5. **Do not add an open-tracking pixel** to either email. The copy says there is none.
6. **Do not add anything social** — no public profiles, no avatars, no follower counts, no public
   pages.
7. **Do not build a shop.** Leave the held slot in the newsletter template and the nav.
8. **Do not make the signed-out experience a teaser.** The free tools must be fully useful without an
   account.
9. **Do not soften the commercial disclosure.** "Including offers for courses and services" stays at
   the point of subscription, not in a tooltip or the privacy policy.
10. **Deletion must reach the newsletter list**, not only the account.

## Emails

Assume a hostile client: images blocked, `<style>` stripped, dark mode forced. The templates already
use tables, inline every critical style, ship no images and no webfonts, and handle dark mode with
`prefers-color-scheme` overrides. Keep all four of those properties. Test in a dark-mode client
before calling either one done.

## When the design is silent

Ask. `README.md` §8 lists the three open questions already known — the newsletter byline is the one
that needs an answer before launch. Do not resolve it in code.
