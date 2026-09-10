Where the app shows working rather than prose — a letter-by-letter reckoning, a code, an SVG export.

```jsx
<CodeBlock label="Milesian" copyable onCopy={copy}>{'Σ 200\nο  70\nφ 500\nί  10\nα   1\n─────\n     781'}</CodeBlock>
```

- Right-align a column of figures with `align="right"`.
- Never use it for prose; long lines scroll horizontally and that is correct for data only.
