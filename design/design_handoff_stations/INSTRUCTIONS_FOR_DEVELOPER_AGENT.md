# Instructions for the implementing agent — stations pack

You are implementing a finished design. Read `README.md` in this folder in full, then
`brief/DESIGN_HANDOFF_02_stations.md`.

**Read the first pack first:** `../design_handoff_shrutivtuber/`. It carries the tokens, chrome,
component library and tool pages. Everything here assumes it and changes none of it.

**Build these three pages before anything in `../design_handoff_accounts/`.** They need no account,
they carry no personal data beyond a typed location, and they are what makes the site worth opening
daily. The account-bound half is worth nothing if these are not there first.

Start at `ui_kits/site/index.html` → **Today**, and use the demo bar's **athens / polar** and
**birth time** toggles to reach the cannot-compute states.

## Your mandate

**Implement the design 1:1. Do not interpret it.** Reproduce the screens exactly and plug real
ephemeris computation in behind them.

## What counts as done

- Three pages match the reference build, in both themes, at mobile and desktop.
- The station table prints correctly — header repeats, rows do not split, no grey washes.
- Copy is verbatim, especially "no moonrise today", the range-cap line, the polar states, and the
  signed-out transits invitation.
- Every cannot-compute state is reachable and correct: polar (no solar stations, no planetary
  hours), no moonrise, no birth time.
- The subscribable feed keeps working as the year turns; the `.ics` snapshot does not pretend to.
- `/today` is genuinely useful with no account.

## Hard rules

1. **Never a blank cell.** A station that does not occur renders "no moonrise today". It is the sky,
   not missing data.
2. **Never silently truncate a range.** The one-month cap is stated and enforced with a refusal.
3. **Never blur, lock or tease the signed-out transits block.** Invitation, not paywall. No lock
   icon, no fake preview, no modal, no "you're missing N transits".
4. **Never guess a birth time or a location.** Mark angular transits undefined and say why.
5. **Never show a zeroed countdown** where there is no station — use the designed state.
6. **Do not demote the subscribable feed.** It is the only route that notifies and stays correct, so
   it keeps the primary styling. The hierarchy is the information.
7. **Do not write print CSS in the pages.** `tokens/print.css` owns print geometry.
8. **Do not assume a tradition.** Hellenic, Thelemic and "times only" are equal choices; the tool
   computes times, the preset only labels them.
9. **Check the dark theme first.** These pages are read outdoors at dawn on a phone. Times use
   `--ink` in dusk, never `--ink-soft`.
10. **Do not change the design system** to fit these pages. Tokens, components and the
    cannot-compute grammar stay as built.

## When the design is silent

Ask. Do not resolve it in code.
