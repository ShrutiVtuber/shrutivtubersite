The app's button — one filled button per screen, at most.

```jsx
<Button variant="filled" size="lg" full onClick={cast}>Cast the chart</Button>
<Button variant="outlined" onClick={save}>Save a draft</Button>
<Button variant="text" destructive onClick={del}>Delete this reading</Button>
<Button variant="outlined" external href="https://shrutivtuber.com/support">Support her work</Button>
```

- Minimum height 48px at `md` — the tap target is the button, not the label.
- `loading` keeps the width and swaps the label for a spinner, so the layout never jumps.
