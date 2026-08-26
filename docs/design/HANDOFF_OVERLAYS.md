# Developer handoff — the stream overlays

**Design source:** `Stream overlays.dc.html` (open in a browser; needs `support.js` and `_ds/` beside it)
**Design system:** Shruti — `_ds/shruti-design-system-cb687f1a-c730-4155-891e-19f81b273619/`
**Follows:** `docs/DESIGN_REQUEST_COMPATIBLE.md` house format
**Date:** 2026-08-26

Read this next to the design file. Where the two disagree, the design file wins — it is the
drawn artefact, this is the index to it.

---

## 0. The one thing that must not be lost

Every surface here exists to move somebody from watching to supporting **by a route she
controls**. The counter is not a goal bar; it is the visible half of her own income path. If an
implementation decision makes the counter less clear at a one-second glance, it is the wrong
decision regardless of what it buys.

---

## 1. Files to create

```
frontend/site/src/pages/overlay/
  counter.astro          # surface 1 — wide | compact via ?size=
  alerts.astro           # surface 2
  ticker.astro           # surface 3
  sky.astro              # surface 4
  hours.astro            # surface 5
  countdown.astro        # surface 6
  _overlay.css           # the shared plate + dusk-ramp tokens (both appearances)
  _skin.css              # [data-skin="grimoire"] token re-point
frontend/site/src/components/counters/
  CounterCard.astro      # web variant of surface 1 (themed, responsive)
  SkyCard.astro          # web variant of surface 4
frontend/site/src/pages/admin/
  counters.astro         # surface 7
backend/shruti/models/__init__.py
  Counter, CounterSource, Overlay, AlertSound
```

Each overlay page is a **separate browser source**. She adds only the ones she wants; no page
depends on another being present.

---

## 2. Data model

```python
class Unit(StrEnum):            # the unit is a first-class field, never inferred
    MONEY_EUR = "money_eur"     # renders "€184 / €300"  — symbol prefixes the numeral
    PEOPLE    = "people"        # renders "14 / 20" + eyebrow "people"
    SUBS      = "subs"          # tiers normalise to a count
    BITS      = "bits"          # never converted to money

class Counter(Model):
    id, name: str               # her words. Never templated, never truncated in the admin.
    unit: Unit
    target: Decimal
    progress: Decimal           # summed server-side, never client-side
    deadline: date | None
    appearance: Literal["almanac", "grimoire"] = "almanac"
    motion: Literal["full", "reduced", "still"] = "reduced"
    sources: set[CounterSource]  # see below
    token: str                   # unguessable, per overlay URL

class CounterSource(StrEnum):
    STRIPE_ONEOFF, STRIPE_MEMBERSHIP, STRIPE_SHOP     # arrive as money
    TWITCH_SUB, TWITCH_GIFT, TWITCH_BITS              # tiers | counts | bits
    YOUTUBE_SUPERCHAT                                 # money
    COURSE_SIGNUP, WORKSHOP_SIGNUP                    # people
    # YOUTUBE_MEMBERSHIP is deliberately absent — see §9
```

**Platform events count only when ticked, per counter.** Both Twitch and Stripe are ticked
during the move off Twitch; unticking must not touch the overlay.

**Overrun is not capped.** `progress` may exceed `target` and the API must return the true
figure. Clamping progress at 100% throws away the best moment the design has.

---

## 3. The two compute budgets — the load-bearing constraint

| | Runs on | Rule |
|---|---|---|
| Rendering | **Her streaming PC**, OBS's embedded Chromium, beside the encoder | Costs frames. Budget is a setting with three levels. |
| Computing | The server | Cheap. Everything hard goes here. |

**The client is never allowed to compute astronomy.** The server pushes finished numbers:

```json
// GET /api/overlay/sky?t=<token>   → also the WS push payload, every 60s
{
  "at": "2026-08-26T21:14:00+03:00",
  "bodies": [
    {"key":"moon","lon":102.13,"speed_per_hour":0.55,"retrograde":false},
    {"key":"sat","lon":12.13,"speed_per_hour":-0.01,"retrograde":true}
  ],
  "aspects": [{"a":"moon","b":"sat","kind":"square","exact_at":"2026-08-26T21:14:00+03:00","applying":false}],
  "ingresses": [{"key":"moon","sign":"leo","at":"2026-08-26T23:51:00+03:00"}]
}
```

The client interpolates between two known longitude sets over 600ms and does nothing else.
No ephemeris library ships to the browser.

**Transport:** one WebSocket per overlay, authenticated by the URL token, server-push only.
Poll fallback at 30s if the socket cannot open. On disconnect the client **holds last known
state** (§8) and retries with backoff; it must never blank and never zero.

---

## 4. Geometry — authored at 1920 × 1080

The page is a fixed 1920 × 1080 canvas. **No viewport units, no media queries, no `rem`.** In a
2560 × 1440 scene OBS scales the browser source by 1.333 and the design is identical, larger.

| Surface | Size | Position (1920×1080) |
|---|---|---|
| Planetary hours strip | 620 × 76 | left 64, top 64 |
| Countdown | 340 × auto | right 64, top 64 |
| Alerts zone | 920 wide, bottom-anchored | centred, top 64 |
| Sky chart | 428 × auto | right 64, top 392 |
| Supporters ticker | 1360 × 48 | left 64, top 848 |
| Counter bar — wide | 1360 × auto | left 64, top 916 |
| Counter bar — compact | 620 × 76 | her choice |

The spec page scales this canvas with a `ResizeObserver` purely so it can be reviewed in a
browser window. **Production overlays do not scale — they render at 1:1.** Do not port that code.

### The plate — the thing that makes it legible over video

```css
background: color-mix(in srgb, var(--dusk-card) 94%, transparent);
border: 1px solid var(--dusk-line);
border-radius: 10px;
box-shadow: 0 12px 34px rgba(6, 9, 18, .5);
```

93–94% opacity, a 1px hairline, and a soft cast shadow so the **edge** survives a white
background. A drop shadow on bare text does not survive a white editor; a plate does. No
surface paints a full-bleed background — OBS composites the page.

---

## 5. The two appearances

Both are dusk; a light overlay on a light stream is unreadable. They are **not themes in the
site's sense** — sizes, positions, hierarchy, hold durations, truncation rules and every state
are identical. Only the ramp moves, via one scoped block:

```css
[data-skin="grimoire"] {
  --dusk-card:#241B33; --dusk-veil:#332545; --dusk-inset:#170F22;
  --dusk-line:#42314F; --dusk-line-strong:#61476C;
  --dusk-ink:#F3E9F3; --dusk-ink-soft:#C8B4CB; --dusk-ink-faint:#9C87A4;
  --dusk-accent:#DDB6C9; --dusk-rose:#B98BC6; --dusk-horizon-line:#8A6880;
}
```

Set `data-skin` on the canvas root from `Counter.appearance`. Every plate follows; there is no
second set of markup to keep in sync — **do not fork the components per appearance.**

- **Almanac** — observatory ink over navy. Default. Coding sessions, long builds.
- **Grimoire** — the violet end of the same dusk sky, plus nine hairline astronomical glyphs
  scattered in the canvas **margins** at 22–34% opacity. Ritual and divination streams.

**Ornament rules (non-negotiable):** margins only — never over a plate, never over her face.
At Full, three of the nine breathe on a 6s opacity cycle; at Reduced and Still they are static.
That cycle is the only ambient motion in the entire set.

**Recolourable from the admin:** `--dusk-accent` (bar fill, amounts, marks) and `--dusk-rose`
(overrun, events, hold rule). Nothing else. Live-red stays reserved for the site's live badge.

---

## 6. Alerts

One skeleton, nine members: bounded glyph mark · eyebrow naming the door · headline naming the
person · unit slot behind a hairline · optional moderated message below a hairline.

| Kind | Glyph | Amount slot | Unit | Hold | Sound |
|---|---|---|---|---|---|
| Stripe one-off | ♀ | `€5` | euro | 4.2s | assigned |
| Membership begins | ♀ | `€12` | per month | 4.8s | assigned |
| Twitch sub (new/renewed) | ♃ | `T2` | 3 months | 4.2s | assigned |
| Gift subs / gift bomb | ☿ | `5` | recipients | 6.0s | assigned, louder |
| Cheer | ☉ | `1,000` | bits · not money | 4.2s | assigned |
| Raid | ♂ | `42` | viewers | 5.4s | optional |
| Super Chat | ♀ | `€20` | euro | 4.8s | assigned |
| Course / workshop signup | ☾ | `1` | seat · 14 of 20 | 4.8s | assigned |
| **Follow** | ○ | — | — | **1.8s** | **silent** |

The glyph carries the **kind of event**, not the platform — the platform is named in the
eyebrow. This is why nothing here assumes Twitch or YouTube.

**Amount rules.** `€5`, `1,000 bits`, `T2 · 3 months`, `42 viewers` and `1 seat` all occupy the
same right-hand slot in JetBrains Mono, tabular. Bits are **never** converted to euro. A gift
names the **giver** in the headline — the giver is the one being thanked. A raid differs in
kind, not degree: rose mark, longer hold, "a crowd arrived".

**The follow is the design problem.** No plate, no glyph mark, no unit slot, no sound: a 40px
capsule, 1.8s, opacity only. Switching follows off is ordinary configuration — the ticker's left
cell becomes `Follows: quiet · 34 today`, so the family loses a capsule, not a member.

**Phases:** arrival 240ms (fade + 10px up) · hold 1.8–6.0s (a 2px rose rule drains
left-to-right) · departure 420ms (fade + 5px up). The draining rule announces the departure so
it never reads as a glitch.

**Queue.** One plate at a time, never two. Waiting alerts are hairline ticks with a count.
Sound plays on arrival only — never stacked.

**Messages are moderated before they reach the screen.** Assume absent by default: the message
section only exists when there is one, so the plate is two lines instead of three. There is no
empty capsule to look broken. An unmoderated alert fires **without** its message rather than
waiting.

**Truncation.** The headline is one line, always — ellipsis at the plate edge. Never wraps,
never shrinks the type, never pushes the unit slot. `Anonymous` is set in italic display type: a
name, deliberately, not a failed lookup.

---

## 7. Sound — she uploads her own *(client requirement, 2026-08-26)*

**The back end must let her upload her own sound files and assign one per alert type.**

- Upload into her existing admin media store, beside the uploader that already exists.
- WAV or OGG, ≤ 512 KB each.
- Per-type assignment, per-type gain (dB), and a global mute.
- **Served from her own origin** and **preloaded with the overlay on connect** — nothing may be
  fetched when an alert fires, and no request may leave the machine mid-stream.
- Follows default to silent and stay silent unless she assigns a file.
- Unassigned type = silent, not a fallback beep.
- A queued alert plays its sound on arrival only.

---

## 8. States — every one is designed, including the ones that look like nothing

| State | Behaviour |
|---|---|
| Nothing configured | Authored line: *"Overlay connected · pick a counter in the admin."* Never `undefined`, never blank. This is the first thing she ever sees. |
| Zero progress | Empty track is a designed shape; target and what-remains carry the message. |
| Met, and overrun | Fill hits 100%, a 1px tick marks where the target was, everything past it is rose. Remaining flips to `+€40 over · thank you`. Mark and plate edge turn rose once and stay. At Full, one 600ms rose sweep at the moment it is met. |
| Connection lost | **Hold last known numbers.** Values drop to ink-soft, the fill gains a rose dashed "as of" edge, and staleness is stated in words once it passes 90s. Never blank, never zero. |
| Queue | One plate, waiting alerts as ticks + count. |
| No message | Two-line plate. No placeholder. |
| Very long name | Single-line ellipsis at the plate edge. |
| Anonymous | Italic display type. |
| Empty ticker | The ticker does **not** say "no supporters yet". Its left cell becomes the standing line about where support goes, so the row still earns its space at the start of a campaign. |

---

## 9. The gap — do not paper over it

**YouTube memberships cannot be read.** The API is gated behind a Google partner relationship
and the self-serve application was withdrawn. New YouTube members raise **no alert**.

The admin source list must show that row as **unavailable**, not unticked — the absence is
stated, not disguised as a setting she forgot. Super Chats are unaffected.

---

## 10. Security

- Overlay URLs carry an unguessable token: `/overlay/counter?t=<token>`.
- **Never render the token**, even to her — the admin shows `••••••••` and copies the full URL
  to the clipboard. OBS settings get screen-shared.
- One token per overlay, revocable and regenerable per row without touching OBS layout.
- Tokens are read-only credentials scoped to one counter. No mutation from an overlay page.

---

## 11. Motion — a per-overlay setting, three levels

| Surface | Full | Reduced | Still |
|---|---|---|---|
| Counter bar | Fill eases 240ms; one rose sweep when met | Fill eases 240ms; no sweep | Fill jumps between frames; met state drawn, not announced |
| Alerts | Fade + 10px in, rule drains, fade out | Same — transitions are the point | Plate appears/disappears; rule at full width; the words carry it |
| Ticker | Marquee, 34s per lap | Static: four most recent + `+14 more` | Identical to Reduced |
| Sky chart | Bodies ease 600ms on push | Bodies jump on push | Everything jumps; seconds digit still ticks |
| Hours strip | Shift 240ms + glyph cross-fade + 600ms sweep | Shift 240ms; no sweep | New ruler is simply there |
| Countdown | 120ms digit cross-fade | Digits swap outright | Digits swap outright |
| Grimoire ornament | 3 of 9 breathe, 6s | Static | Static |

**Still must be complete and legible** — it is the weaker machine and a bad night.

**An idle overlay composes no frames.** No ambient loops at any level except the Grimoire
ornament at Full. The only per-second repaint is the sky chart's and countdown's seconds digit,
each a single text node, both stopped when the surface is not in the scene
(`document.visibilityState`, and stop the interval when the socket is idle).

The two **web variants** ignore this setting and obey `prefers-reduced-motion` like the rest of
the site. The overlay setting is about her encoder; the media query is about her reader.

---

## 12. The instruments

**Sky chart.** What ticks: the clock, every second, one text node. Positions arrive on a 60s
push; the client eases 600ms between two known degree sets. The Moon moves about half a degree
an hour, so a moving dot is a lie at stream length — **the honest liveness tell is the drift
readout** (`+0°33′ / h` beside the Moon) plus a seconds digit that never stops.

Two events worth noticing:
- **Ingress** — the entered sector fills rose at 12% over 600ms, settles to a 1px rose boundary
  that stays for the rest of the stream. Event line: `☾ enters Leo · 23:51`.
- **Exact aspect** — the chord goes 1px dotted ink-faint → 2px solid rose over 240ms, holds 20s
  with `☾ □ ♄ exact 21:14`, then settles to a 1px rose chord. Applying aspects are dotted;
  separating ones are dropped.

**Planetary hours strip.** Past · current · next as three cells, with the current cell carrying
a 2px rose progress rule. **The turnover is the only animation this surface ever needs**: the
row shifts one cell left over 240ms, the new ruler's glyph fades up over 240ms, one rose sweep
crosses the current cell over 600ms. Total 1.1s, then nothing composes for an hour.

Both instruments must read as `/tools` — same plates, same mono, same dotted almanac leaders.
Times are Athens-authored; the site's dual-time rule does not apply on the overlay (it is her
screen, in her timezone) but **does** apply to the two web variants.

---

## 13. Fonts — harder than the site

**Zero external requests, fonts included.** Self-host EB Garamond, Commissioner and JetBrains
Mono with the overlay bundle and declare them with `@font-face` + `font-display: block`. The
spec page loads them from the CDN only because no binaries exist yet.

A fallback face appearing mid-broadcast is worse than a slow page. `font-display: swap` is
wrong here.

---

## 14. Acceptance

- [ ] Legible over a white editor, a dark room, a bright window and her own face.
- [ ] Nothing scrolls, overflows, or shows a scrollbar at 1920×1080 or 2560×1440.
- [ ] Every alert type drawn, reading as one family — the follow unmistakably the smallest.
- [ ] `€5`, `1,000 bits`, `three months`, `42 viewers` and `14 / 20 people` all sit correctly in
      the same slot.
- [ ] All three motion levels work. **Still is complete and legible.**
- [ ] Idle overlays compose no frames (verify in DevTools' rendering panel).
- [ ] Every state in §8 drawn, including the ones that look like nothing.
- [ ] Both appearances work from one set of components.
- [ ] Her own uploaded sounds assign per alert type; follows silent.
- [ ] Token never rendered anywhere.
- [ ] Zero network requests to any origin but hers.
- [ ] A stranger watching for one second knows what the counter is for and how far along it is.
- [ ] It looks like the same hand as `/today` and `/tools`.

---

## 15. Sample data is sample data

Positions, hours, totals and names in the design file are authored values, internally consistent
for **2026-08-26 21:14 Athens**, so the layouts can be judged. In production every number comes
from her own ephemeris and her own Stripe, computed on the server and pushed as finished
numbers. Do not port the sample arrays.
