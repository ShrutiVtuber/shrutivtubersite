# StationTable

Days down, stations across. The primary reading on both tracker pages.

## Three things it is designed around

**1. It is read on a phone, outdoors, at dawn, in poor light.** So the times are mono, tabular, and
larger than the surrounding body text — they are the reason the table exists. The dusk theme matters
more than usual here: times use `--ink`, never `--ink-soft`.

**2. It gets printed and pinned up.** `tokens/print.css` handles the medium: Dawn forced on paper,
chrome and controls dropped, `thead` repeated per page via `display: table-header-group`, rows
`break-inside: avoid`. Do not add page-break CSS in the page — the token sheet owns it.

**3. A missing station is never a blank cell.** Pass `null` for a station that does not occur and it
renders `absentLabel` in italic at `--ink-faint`:

```jsx
{ date: '14 Sep', times: ['—', '02:41', null, '14:18'] }
```

The Moon rises roughly fifty minutes later each day and occasionally skips a civil day entirely; at
high latitude whole weeks can lack a moonrise or a moonset. **That is a fact about the sky, not
missing data**, so the lunar table passes `absentLabel="no moonrise today"`. A blank cell would read
as a bug.

## Use

```jsx
<StationTable
  stations={['Sunrise','Noon','Sunset','Midnight']}
  glyphs={['☉︎','☉︎','☉︎','☾︎']}
  attributions={['Hekate Phosphoros','Apollo','Hekate Enodia','Persephone']}
  rows={rows}
  caption="Athens · 37.98°N 23.73°E · your local time · Swiss Ephemeris"
/>

<StationTable
  stations={['Moonrise','Culmination','Moonset','Nadir']}
  absentLabel="no moonrise today"
  rows={lunarRows}   /* each row may carry phase: '◐ 11.4 d' */
/>
```

## Notes

- `today` tints the row `--accent-wash` and labels it; `currentIndex` bolds the station in force and
  marks it with a `·` in accent. Both are quiet — the table is a reference, not a dashboard.
- A `phase` on any row adds a Moon column automatically. Lunar only.
- `attributions` carries the preset (Hellenic or Thelemic); omit the prop entirely for
  "times only".
- `undefinedReason` renders the whole-table cannot-compute state for polar latitudes, with the `○`
  mark and the same shape as the tool pages' states.
- Horizontal scroll below `460px` rather than a card-per-day rewrite: a table of times reads as a
  table, and reflowing it into stacked cards loses the column comparison that makes it useful.
