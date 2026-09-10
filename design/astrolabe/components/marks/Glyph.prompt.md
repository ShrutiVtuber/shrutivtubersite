One astronomical mark, set in the app's own 5.6 KB glyph font — use it anywhere a planet, sign, node or ℞ appears.

```jsx
<Glyph name="saturn" tone="gilt" size="lg" label="Saturn" />
<Glyph name="retrograde" tone="rose" size="sm" />
```

- `name` covers the 29 glyphs the font actually carries; anything else falls back to EB Garamond via `char`.
- Tone `gilt` is the ornament use (section rules, table heads); `rose` is reserved for retrograde.
- Never pair a glyph with an emoji, and never use a glyph as the only signal — the word goes beside it.
