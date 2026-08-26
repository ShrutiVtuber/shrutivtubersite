# Design request: the stream overlays

## 0. What this is for, and why it is not a widget set

Shruti uses StreamElements for alerts and goal bars and wants to stop — not
because it is bad, but because **her income runs through other people's
platforms and she wants it to run through her own.** Twitch takes half a
subscription. YouTube memberships are Google's. StreamElements' tip page is
StreamElements'. She already has Stripe, a shop, memberships, classes and a
support page. What she does not have is the part that makes her own income path
*visible on stream*, which is the part that makes people use it.

So this is not decoration. **Every surface here exists to move somebody from
watching to supporting by a route she controls** — or, for the sky chart and
the planetary hours, to make the stream unmistakably hers.

She intends to leave Twitch and YouTube eventually and stream on her own terms.
Nothing here may assume either platform: an overlay is a browser source, and a
browser source works wherever the stream ends up.

---

## 1. The three ways this fails, and only one is a taste question

**It is composited over video nobody has seen.** The background is not a colour
— it is her, moving, in a room whose lighting changes, sometimes with a bright
window behind her, sometimes with a white code editor filling the screen. Every
decision that assumes a background is wrong. Text without a plate or an outline
is legible in rehearsal and gone the moment she opens an IDE.

**It is watched, not read.** Under a second, in the corner of an eye, often at
480p on a phone, often while somebody is talking. Anything needing a second
look does not work.

**And there are two compute budgets, not one — this is the part that is
usually got wrong.**

| | Where it runs | Can she buy her way out? |
|---|---|---|
| Rendering the overlay — animation, redraw | **Her streaming PC**, in OBS's embedded Chromium, beside the encoder | **No.** It costs frames on the stream. |
| Computing positions, processing events, pushing updates | The server | Yes, and it is cheap |

**She wants animation and has agreed to pay for it — so put the expensive half
on the machine that can afford it.** Sky positions are computed on the server
and pushed as finished numbers; the client interpolates cheaply between them.
The client should never be recomputing astronomy sixty times a second.

---

## 2. Scope, locked

**Seven surfaces:**

| # | Surface | OBS | On the site |
|---|---------|-----|-------------|
| 1 | **Counter bar** — wide and compact | ✓ | ✓ |
| 2 | **Alerts** | ✓ | — |
| 3 | **Supporters ticker** | ✓ | — |
| 4 | **Sky chart, ticking** | ✓ | ✓ |
| 5 | **Planetary hours strip** | ✓ | — |
| 6 | **Countdown** | ✓ | — |
| 7 | **Admin** — creating counters, copying overlay URLs, motion settings | — | ✓ |

**An OBS overlay and a website widget are different designs**, not one design
resized: transparent, fixed-size and single-appearance versus themed,
responsive and working in both light and dark. Same data, two treatments. Two
earn the second treatment; the rest do not.

**Out of scope:** chat overlays, the site's existing pages, the Discord bot.

---

## 3. The counter — and it is not only money

The centrepiece, and it generalises further than "goal bar" suggests.

**A counter is a target, a unit, and a chosen set of sources.** She creates it
in the admin and picks what feeds it:

| Source | Arrives as |
|---|---|
| Stripe — one-off support, memberships, shop orders | money |
| Twitch — subscriptions, gifts, bits | tiers, counts, bits |
| YouTube — Super Chats | money |
| **Course signups** | people |
| **Workshop signups** | people |

So "€300 for a microphone" and "20 people on the December workshop" are the
same object with different units. **Design the unit as a first-class thing**,
not as a euro sign that sometimes says something else. A bar reading `14 / 20
people` and one reading `€184 / €300` must both look deliberate.

Platform events count toward totals when she says so — that is her choice per
counter, because during the move off Twitch she wants both visible.

A counter carries: a **name in her words**, a **target**, **progress**, **what
remains** — which is the part that actually moves people — and optionally a
**deadline**.

**Design the overrun.** A counter that is met and keeps receiving is the best
moment the design will ever have, and a bar that stops at full throws it away.

---

## 4. Alerts — a family, not one thing

The most-seen surface here and the most likely to be resented.

**Support arrives through several doors and they are not interchangeable:**

| Source | What arrives | The unit is |
|---|---|---|
| **Stripe** | one-off support, a membership starting | money — €5 |
| **Twitch subscription** | new, renewed, or **gifted** | a tier — T1/T2/T3 — and months |
| **Twitch gift bomb** | one person gifting many at once | a count of recipients |
| **Twitch cheer** | bits | bits — "1,000 bits", which is *not* money |
| **Twitch raid** | a streamer arriving with their audience | viewers — "42 viewers" |
| **YouTube Super Chat** | a paid, pinned, coloured message | money, and its own colour tier |
| **Course or workshop signup** | somebody has joined a thing she teaches | a person, and which course |

**Follows do not raise an alert.** They are constant and worth almost nothing,
and alerting on them is the single most common way a stream becomes
unwatchable. They may feed a counter instead.

**Four things the design has to answer:**

1. **The amount is not one type.** €5, 1,000 bits, three months, 42 viewers and
   a person's name in a course all occupy the same slot. All five must read
   correctly and none may look like a mistake.
2. **A gift is three people** — giver, recipient, sometimes a count. A gift bomb
   is a giver and a number. The giver is the one being thanked.
3. **A raid is not a donation.** Somebody arrived with a crowd. It probably
   differs in kind rather than degree.
4. They must read as **one family** — a viewer should know instantly that
   something good happened, and only then which kind.

Each carries **who**, **what**, and optionally **a short message**.

Design the **arrival, the hold and the departure** as three things with stated
durations. An alert that arrives beautifully and vanishes abruptly reads as a
glitch.

**Two non-negotiables:**

- **A queue.** Two supporters within a second must not overlap. Design what the
  second does while it waits.
- **Messages are moderated before they appear.** A stranger's text going
  straight onto a live stream is a hazard this site will not take. Assume a
  message may be absent, and make that look deliberate rather than broken.

---

## 5. The instruments — the reason to build this rather than buy it

### 5.1 Sky chart, ticking

A live chart of the day's sky, on screen while she writes the software that
computes it. **Nobody else can have this**, and it is the whole brand in one
object.

It ticks. Say what that means: what moves, how often, and how a viewer can tell
it is live rather than a picture. The Moon moves about half a degree an hour —
visible over a stream, invisible over a minute — so the honest answer may be
that the *time* ticks and the bodies drift.

Positions come from her own ephemeris, computed on the server. The client is
given numbers and draws them.

Design the moment a body changes sign, and the moment an aspect comes exact.
Those are the events worth noticing in three hours of streaming.

### 5.2 Planetary hours strip

Small, persistent: the current planetary hour and its ruler.

It does exactly one thing, roughly once an hour — **the hour turns over.** That
moment should be worth seeing, and it is the only animation this surface ever
needs.

Both of these should feel like an instrument panel rather than a widget. They
belong to the same world as `/tools`, and this is the one place where the
site's existing visual language should be recognisable at a glance.

---

## 6. Motion — a setting, not a constant

**Because she streams from more than one machine**, motion is configurable per
overlay in the admin, and the design must cover each level rather than
degrading into one.

| Level | Intent |
|---|---|
| **Full** | What you would draw with no budget. Her strong machine. |
| **Reduced** | Transitions kept, ambient motion dropped. The everyday setting. |
| **Still** | No animation at all. State changes appear between frames. |

**"Still" must not look broken.** It is the setting she will use on the weaker
machine and possibly on a bad night, and an alert that only makes sense while
moving is unusable there. Every surface must be legible and complete at Still.

Even at Full: **an idle overlay should compose no frames.** Nothing repaints
when nothing has changed. Motion is for things happening.

For the two web variants, `prefers-reduced-motion` applies as it does
everywhere else on the site, independently of this setting.

---

## 7. Constraints, harder than the site's

**Transparent.** OBS composites the page. No overlay paints a full-bleed
background; every plate is a deliberate, bounded shape.

**Fixed canvas, never scrolls.** Each overlay is added at a stated size.
Content that could overflow must truncate, marquee or collapse — a scrollbar on
a stream is a visible bug. Design at **1920×1080** and say what happens at
**2560×1440**.

**Legible over anything.** Assume a white editor, a dark room, a bright window,
her own face. Plate or outline; drop shadow alone is not enough.

**Zero external requests**, as everywhere here — fonts included. It matters
more on a stream, not less: a fallback face appearing mid-broadcast is worse
than a slow page.

**Tokens in the URL.** Overlay URLs carry an unguessable token. Never display
it, and assume the page may be seen if she shares a screen with OBS settings
open.

**One appearance, not two themes** — for the OBS surfaces. She picks the look;
say which parts she may recolour from the admin. The two web variants follow
the site's normal light and dark rules.

---

## 8. States every surface needs

| State | Why |
|---|---|
| **Nothing configured** | She will add the overlay before creating the counter. It is the first thing she ever sees, and "undefined" on a stream is unforgivable. |
| **Zero progress** | Every counter starts here and stays a while. |
| **Met, and overrun** | The best moment available. |
| **Connection lost** | Her network can drop. Hold the last known state, never blank. Say whether staleness is shown. |
| **A queue of several alerts** | Design the wait. |
| **A supporter with no message** | The common case. |
| **A very long name** | Somebody is called `xX_the_longest_possible_handle_Xx`. |
| **An anonymous cheer or gift** | Twitch permits both. "Anonymous" is a name and should look deliberate. |
| **Empty ticker** | The normal state at the start of every campaign. "No supporters yet" on a stream is worse than nothing. |

---

## 9. What is settled — do not re-derive

- **Money comes through Stripe**, live, already handling
  `checkout.session.completed` and all three subscription events.
- **Platform events count when she says so**, per counter.
- **Counters count people as readily as money** — course and workshop signups
  are first-class.
- **Counters are rows**, created and edited in the admin without a deploy.
- **Supporter messages are moderated before they reach the screen.**
- **The instruments are computed by her own ephemeris.** The numbers are real.
- **Motion is a per-overlay setting** with three levels, all designed.
- **Follows do not alert.**
- **No third-party requests, ever.**
- **Nothing may assume Twitch or YouTube.**

**One gap, and it is not ours to close.** YouTube *memberships* cannot be read:
the API is gated behind a Google partner relationship, the self-serve
application was withdrawn, and no independent developer has publicly been
granted access. **New YouTube members will not raise an alert**, and the design
must not imply a completeness that does not exist. Super Chats are unaffected.

---

## 10. Acceptance

- Legible over a white editor, a dark room and a bright window.
- Nothing scrolls, overflows, or shows a scrollbar.
- Every alert type drawn, reading as one family.
- €5, 1,000 bits, three months, 42 viewers and `14 / 20 people` all sit
  correctly in the same slot.
- All three motion levels drawn. **Still is complete and legible.**
- Idle overlays compose no frames.
- Every state above drawn, including the ones that look like nothing.
- A stranger watching for one second knows what the counter is for and how far
  along it is.
- It looks like the same hand as `/today` and `/tools`.

## 11. Files

- `frontend/site/src/pages/overlay/…` — the OBS surfaces
- `frontend/site/src/components/counters/…` — the two web variants
- `frontend/site/src/pages/admin/counters.astro` — the admin surface
- `backend/shruti/models/__init__.py` — `Counter` and its sources
- `docs/DESIGN_REQUEST_COMPATIBLE.md` — the house format this follows
