Sky's header — the day as an arc, with the Sun on it and the Moon's phase beside it.

```jsx
<DayArc sunrise="06:58" sunset="19:51" now="13:42" phase={0.38} ruler="venus" />
```

- One per app, at the top of Sky. It is the counterpart to Home's Masthead: each tab gets one
  surface of its own, and they are never the same surface.
- Every value is computed on device, so it is correct offline — which is the whole point.
- Outside daylight the Sun is not drawn and the arc reads as night; do not fake a position.
