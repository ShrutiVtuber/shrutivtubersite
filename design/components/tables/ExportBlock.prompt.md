# ExportBlock

Three export routes, **which are not equivalent** — and the whole design job here is making that
difference legible before someone picks the wrong one.

| Route | What it really is | Prominence |
|---|---|---|
| **Subscribable feed** (`webcal:`) | Stays correct as the year turns. **The only one that produces notifications.** | Primary — card surface, `--line-strong`, accent button |
| **`.ics` download** | A snapshot of the range shown. Goes stale the day after. | Secondary — outline button |
| **Google Calendar links** | One event, one station, for people who keep only one of the four | Tertiary — pills |

The feed is the one that creates the habit, so it gets a card of its own, a rose
`stays correct · notifies` tag, the accent button, and the URL shown in mono with a copy control.

The download says **"it will go stale"** in the body copy. That is deliberate: someone who exports
in September and finds wrong times in March will blame the tool, not the snapshot. Saying it once,
plainly, at the point of choice, is cheaper than that.

## Use

```jsx
<ExportBlock
  feedHref="webcal://theourgia.com/stations/ical?place=athens&preset=hellenic"
  fileHref="/stations/ical?place=athens&from=2026-09-01&to=2026-09-30"
  fileName="solar-stations-athens-2026-09.ics"
  fileScope="1–30 September 2026 · 120 events"
  googleLinks={[
    { label: 'Sunrise', glyph: '☉︎', href: '…' },
    { label: 'Noon', glyph: '☉︎', href: '…' },
    { label: 'Sunset', glyph: '☉︎', href: '…' },
    { label: 'Midnight', glyph: '☾︎', href: '…' }
  ]}
  meta="Athens · Hellenic preset · your local time"
  onCopyFeed={…}
/>
```

## Notes

- Carries `className="export-block"`, which `tokens/print.css` hides — export controls earn no paper.
- The feed URL is visible as text, not hidden behind the button. Some calendar apps want it pasted,
  and a `webcal:` link that silently fails is a dead end otherwise.
- `meta` should name everything that changes the output: place, preset, timezone. A feed URL without
  those is not reproducible.
- Do not reorder these three by visual balance. The hierarchy is the information.
