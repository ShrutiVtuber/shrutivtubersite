# Instructions for the implementing agent

You are implementing a finished design. Read `README.md` in this folder in full before writing code,
then `../readme.md` (the design system's own decision record) and `brief/DESIGN_BRIEF.md` plus
`brief/DESIGN_UPDATE_01.md`.

The design itself is at the root of this bundle: `styles.css`, `tokens/`, `components/`, `ui_kits/`,
`templates/`, `guidelines/`, `assets/`. Start the tour at `ui_kits/site/index.html`.

## Your mandate

**Implement the design 1:1. Do not interpret it.**

Every colour, dimension, hairline, state and line of copy in this bundle was decided deliberately
and reviewed with the client. Your job is to reproduce those decisions exactly in a production
stack, and to plug real functionality in behind them.

## What counts as done

- Layout, spacing, type, colour, borders, radii, shadows, hover/focus/active states and motion match
  the reference files and the token tables in `README.md` §5.
- Copy is reproduced verbatim — including empty states, error messages and the "cannot be reckoned"
  text. The wording is part of the design.
- All three theme states work: light (Dawn), dark (Dusk), and un-stamped system default. No colour
  exists only inside a media query.
- Every art-absent state is intact and looks deliberate.
- The seven tool pages compute real answers, with every designed cannot-compute state reachable.
- Disclosure marks, the legal imprint, and the two-name distinction are all present.

## Hard rules

1. **Do not restyle anything.** Not the palette, type scale, density, spacing, or copy voice. If it
   looks unusual, it is deliberate.
2. **Do not substitute your component library's defaults.** If the codebase has a `Button`, make it
   match this `Button` — not the reverse. `components/*/*.d.ts` is the API contract; match prop
   names and variant values exactly.
3. **Do not add anything.** No extra sections, cards, icons, gradients, illustrations, animations or
   statistics. No emoji, anywhere.
4. **Do not remove the art-absent states.** They are not placeholders waiting for images; they are
   the shipping design. This is the single most important constraint in the brief.
5. **Do not invent data.** Where a value is unknown — an oshi mark, a VAT number, a birth time, an
   archon year, an ayanāṁśa the source did not state — ship the designed absent or undefined state
   and raise the question.
6. **Do not merge the traditions.** Where the design offers two or six incompatible reckonings, keep
   them separate and unranked. Never pick a "sensible default" and hide the other.
7. **Inline styles in the `.dc.html` tool pages are a prototype artefact, not an instruction.** Use
   tokens and the Tailwind preset in production.

## Where you are expected to write substantial new logic

Only the seven tool pages. All their data is plausible authored sample data; replace it with real
computation per `README.md` §7.3 and §7.4, leaving layout, copy and states untouched. Everything
else in the bundle is presentation to be reproduced.

## When the design is silent

Ask the design owner. A question costs less than a redesign. If you are blocked and must proceed,
choose the option most consistent with the nearest existing pattern in the bundle, and flag it in
your notes as an assumption — never as a decision.

## When you think the design is wrong

Implement it as specified and raise the issue separately. Do not resolve it in code.
