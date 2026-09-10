The default surface: 14px radius, 1px hairline, shadow-1, `--card` fill.

```jsx
<Card tone="tappable" onClick={open}>…</Card>
<Card tone="warning"><Glyph name="retrograde" tone="rose" size="sm"/> Mercury stations retrograde on Thursday.</Card>
```

- Press deepens the fill to `--veil` and strengthens the hairline. Cards never lift or scale.
- Do not nest a card in a card; use `tone="inset"` for the well inside one.
