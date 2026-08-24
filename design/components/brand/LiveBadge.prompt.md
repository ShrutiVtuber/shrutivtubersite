Stream-status badge with three designed states — live (red wash, pulsing dot, title/game/viewers), offline (next stream if known), unknown (dashed dot, "Status unavailable" — never falsely live). Fixed min-height, so swapping states causes no layout shift.

```jsx
<LiveBadge status="live" title="Building the sigil compiler" game="Software & Game Dev" viewers={214} href="https://twitch.tv/…" />
<LiveBadge status="offline" nextStream="Thu 21:00 EEST" />
<LiveBadge status="unknown" />
```

`compact` renders dot + word only (header use). Pulse pauses under reduced motion; the word carries the meaning.
