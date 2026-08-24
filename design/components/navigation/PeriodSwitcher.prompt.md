# PeriodSwitcher

**Built now for periods that do not exist yet.** Only monthly readings ship at launch; daily,
seasonal and yearly are authored later. If those arrive into a layout that assumed one period, the
layout gets rebuilt — so the switcher is designed and placed from the start.

## The rule about unavailable periods

Periods not in `available` are **absent**. Not disabled, not greyed with a tooltip, not an error
page. A reader who has never seen a daily horoscope should not be told one is missing; they should
simply see the periods that exist.

```jsx
{/* launch: one period, switcher still present */}
<PeriodSwitcher current="monthly" available={['monthly']} label="September 2026" />

{/* later: turning daily on is a data change, not a redesign */}
<PeriodSwitcher current="daily" available={['daily','monthly','seasonal']} label="7 September 2026" />
```

## Notes

- Renders even with a single available period. The switcher **is** the layout; its presence is what
  makes adding periods a switch rather than a rebuild.
- Selected is a card-surface chip with a `--line-strong` hairline — quiet, since the reading is the
  loud thing on the page.
- `label` is the dateline, mono and tabular, pushed to the right edge.
- Closed by a hairline, like every other section in the system.
