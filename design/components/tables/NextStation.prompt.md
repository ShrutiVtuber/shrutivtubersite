# NextStation

The countdown, reused across all three station surfaces: the solar tracker, the lunar tracker, and
Day at a Glance.

**Why it exists.** Someone opening the solar tracker at four in the afternoon wants *"sunset in
2h 14m"* before they want a table of thirty days. So this sits above the table, and the countdown is
the largest number on the page.

## Anatomy

- **Now** — the station currently in force, with the time it began. Quiet; it is context.
- **Next** — glyph, name, optional preset attribution, and the countdown.
- A 2px hairline progress rule between the two, in rose.

## Use

```jsx
<NextStation glyph="☉︎" name="Sunset" at="20:05" inLabel="2h 14m"
  currentName="Noon" currentSince="13:29" attribution="Hekate Enodia" progress={0.62} />

{/* inside Day at a Glance */}
<NextStation size="block" glyph="☾︎" name="Moonrise" at="17:41" inLabel="41m" progress={0.88} />

{/* polar latitude — nothing to count to */}
<NextStation name="Sunrise" at="—" inLabel="—"
  undefinedReason="The Sun does not rise here today, so there are no solar stations to count toward. The lunar stations below still hold." />
```

## Notes

- `undefinedReason` renders the designed cannot-compute variant with the `○` mark. Use it at polar
  latitudes rather than showing a zeroed countdown — a countdown to nothing is a lie.
- `inLabel` and `at` are **preformatted strings**. This component does no time maths; the page owns
  the clock and re-renders it.
- Times are mono and tabular, and the countdown is deliberately oversized: this is read on a phone,
  outdoors, at dawn, in poor light.
- `attribution` carries the preset's deity for that station (Hekate Phosphoros, Apollo, Hekate
  Enodia, Persephone; or the Liber Resh adorations). It is omitted entirely when the preset is
  "none — times only".
- Glyphs are type. Pass U+FE0E on any character that defaults to colour emoji, and the component
  applies `.t-glyph`.
