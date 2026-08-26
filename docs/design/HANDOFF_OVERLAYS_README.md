# Stream overlays — handoff package

**For:** the developer implementing shrutivtuber.com's stream overlays
**From:** design, 2026-08-26

## What is in here

| Path | What it is |
|---|---|
| `handoff/DEVELOPER_HANDOFF.md` | **Start here.** The implementation spec — data model, API shape, geometry, states, motion, sound, security, acceptance. |
| `Stream overlays.dc.html` | The drawn design. Open it in a browser. Interactive. |
| `support.js` | Runtime the design file needs. Keep it beside the HTML. |
| `_ds/shruti-design-system-.../` | The Shruti design system — tokens, styles, component bundle. |
| `uploads/DESIGN_REQUEST_OVERLAYS.md` | The original client request, for reference. |

## Opening the design

Unzip and open `Stream overlays.dc.html` in a browser. Everything is local except the three
fonts, which load from the Google Fonts CDN because no licensed binaries exist yet — see §13 of
the handoff, production overlays must self-host them.

## What to try in it

The composite at the top is live:

- **Backdrop** — white editor, dark room, bright window, her face. The first acceptance test.
- **Appearance** — Almanac (default) or Grimoire (the playful, violet one).
- **Motion budget** — Full, Reduced, Still. Still must be complete and legible.
- **Counter state** — nothing configured, zero, in progress, met + overrun, connection lost.
- **Fire an alert** — all nine types, plus *Four at once* to see the queue.

Below the composite, every surface is drawn again at rest with its states, plus the motion
matrix, the two web variants (light and dark), and the admin.

## The three things most likely to get lost

1. **The unit is a field, not a euro sign.** `14 / 20 people` and `€184 / €300` are one object.
2. **The follow is the quietest member by a wide margin** — no plate, no sound, 1.8s.
3. **The client never computes astronomy.** The server pushes finished degrees; the client eases
   between them.

## Open item

Sound files are hers to upload. The back end needs upload + per-type assignment + per-type gain
+ global mute, served from her own origin and preloaded on connect. Handoff §7.
