An icon-only action — app bar actions, sheet close, the wheel's share and export.

```jsx
<IconButton icon="ios_share" label="Share this chart" onClick={share} />
<IconButton icon="notifications" label="Notifications" badge={3} />
```

- Never ship one without `label`.
- `ghost` in app bars; `outlined` when it sits alone on a card; `filled` only for a primary floating action.
