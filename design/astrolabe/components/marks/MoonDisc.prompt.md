The moon's phase as a small drawing — Home's sky line, the stations table, the period wheel's outer ring.

```jsx
<MoonDisc phase={0.63} size={28} />
<MoonDisc phase={0.5} size={20} showLabel />
```

- Sizes in use: 16 (table cell), 20 (list row), 28 (Home), 44 (Sky header).
- The lit limb is `--gilt-bright` on `--inset`; the rim is a gilt hairline.
- Always announces its phase name, so it survives being read aloud.
