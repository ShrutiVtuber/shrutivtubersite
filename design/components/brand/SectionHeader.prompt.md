Section opener with eyebrow / display title / body / action — use it to start every page section instead of a bare heading.

```jsx
<SectionHeader glyph="☾" eyebrow="The work" title="A portfolio of instruments"
  body="Software for astrology, theurgy and divination." action={<Button variant="ghost">See all work</Button>} />
```

Variants: `align="center"` for page intros; `as="h1"` on page titles; `glyph` adds a rose astronomical ornament before the eyebrow.
