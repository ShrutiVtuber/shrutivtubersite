# SignPicker

The twelve signs as the **primary control** on `/horoscopes`, not a filter tucked in a sidebar.

Someone arriving from a search wants their own sign fast. That is the whole job of this component,
so it is the loudest thing on the index page and it **remembers the choice**.

## Two layouts

- `grid` — the index page. Twelve tiles, glyph + name + date range.
- `row` — a compact pill strip on a reading page, so a reader can move sideways between signs
  without going back.

## `ownSign`

A signed-in reader with a saved nativity has their sign marked `YOURS` in rose, and it is
preselected so they never have to pick. That is the reward for having an account, and it is the only
personalisation this component does.

## Use

```jsx
<SignPicker hrefFor={s => `/horoscopes/${s}/2026-09`} current="virgo" ownSign="virgo" />
<SignPicker layout="row" current={sign} onChange={setSign} ownSign={reader?.sign} />
```

`SIGNS` is exported alongside — `{ key, name, glyph, dates }` — so pages can reuse the same data
without redeclaring it.

## Notes

- Sign glyphs are **type in EB Garamond**, in rose, `aria-hidden`. They are ornaments; the name
  carries the meaning.
- Date ranges are mono and tabular.
- Selected state is `--accent` border + `--accent-wash`, never a fill. Minimum 44px targets.
- No hover lift, no scale — the house rule.
