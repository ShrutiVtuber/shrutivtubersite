A small selectable — sign pickers, feed filters, and the language packs with their download size.

```jsx
<Chip kind="choice" selected={sign==='scorpio'} leading={<Glyph name="scorpio" size="sm" tone="gilt"/>}
  onClick={()=>setSign('scorpio')}>Scorpio</Chip>
<Chip kind="filter" selected>Unanswered</Chip>
<Chip kind="meta" meta="2.1 MB">Greek</Chip>
```

- Filter chips show ✓ when selected, so the state survives a monochrome screen.
- 36px high; they scroll horizontally rather than wrapping to a third line.
