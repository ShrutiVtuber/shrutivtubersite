# Design request: the stream overlays

## 0. What this is for, and why it is not a widget set

Shruti currently uses StreamElements for alerts and goal bars. She wants to
stop — not because it is bad, but because **her income runs through other
people's platforms and she wants it to run through her own.** Twitch takes
half a subscription. YouTube memberships are Google's. StreamElements' tip page
is StreamElements'. She already has Stripe, a shop, memberships and a support
page; what she does not have is the part that makes her own income path
*visible on stream*, which is exactly the part that makes people use it.

So this is not decoration. **Every one of these overlays exists to move
somebody from watching to supporting through a route she controls** — or, in
the case of the instruments, to make the stream unmistakably hers.

She intends to leave Twitch and YouTube eventually and stream on her own terms.
Nothing here should assume either platform: an overlay is a browser source, and
a browser source works the same wherever the stream ends up.

---

## 1. The mistake this exists to avoid

Overlays fail in a way that no other design on this site can, and it is worth
naming before anything is drawn.

**They are composited over video nobody has seen.** The background is not a
colour — it is her, moving, in a room with lighting that changes, sometimes
bright, sometimes nearly black, sometimes with a bright window behind her.
Every design decision that assumes a background is wrong here. Text with no
plate behind it will be legible in rehearsal and illegible the moment she opens
a white IDE.

**They are watched, not read.** A viewer looks at a goal bar for under a
second, in the corner of their eye, often at 480p on a phone, often while
someone is talking. Anything that needs reading twice does not work.

**They cost CPU that the encoder needs.** OBS renders a browser source
continuously, on the same machine that is encoding video. An animation that
would be unremarkable on a web page competes directly with frame rate. This is
a real budget, not a nicety.

The first version of anything like this always has: a thin bar with no plate, a
number in the site's body face at 14px, and a shimmer animation on the fill.
All three are wrong for the reasons above.

---

## 2. Scope

**In scope — five surfaces:**

| # | Overlay | Purpose |
|---|---------|---------|
| 1 | **Goal bar** | A target she sets in the admin, filled by real Stripe money |
| 2 | **Alert** | Somebody just supported — a moment, then gone |
| 3 | **Supporters ticker** | The recent few, quietly, always on |
| 4 | **Instrument strip** | Planetary hour and today's sky — the thing only she has |
| 5 | **Countdown** | To stream start, or to a drop closing |

**Also in scope:** the admin surface where a goal is created and an overlay's
URL is copied.

**Out of scope:** the site's own pages, the Discord bot, anything to do with
chat. A chat overlay is a different problem and is not being asked for.

---

## 3. Constraints, and these are harder than the site's

**Transparent.** The page background is transparent and OBS composites it. No
overlay may paint a full-bleed background. Every plate is a deliberate,
bounded shape.

**Fixed canvas, no scrolling ever.** Each overlay is added at a stated size and
never scrolls. Content that could overflow must be designed to truncate,
marquee or collapse — a scrollbar in a stream is a visible bug.

Design at **1920×1080**, and state what happens at **2560×1440** — OBS scales a
browser source, so the choice is whether it is rendered at the larger size or
scaled up and softened. Say which.

**Legible over anything.** Assume the worst background you can: a bright white
code editor, a pale sky, her own face. Every piece of text needs either a plate
or an outline. Do not rely on drop shadow alone.

**Animation budget.** Movement is allowed where it carries meaning — a bar
filling, an alert arriving. Continuous ambient animation is not: no shimmer, no
pulsing glow, no particles, nothing that repaints when nothing has changed.
When an overlay is idle it should be composing **zero frames**.

**Zero external requests**, as everywhere on this site. Fonts are self-hosted
already. This matters more here, not less: OBS on a flaky connection must not
show a fallback face mid-stream.

**Tokens in the URL.** Each overlay URL carries an unguessable token. The design
must never display the token, and must assume the page could be seen if she
shares her screen with OBS settings open.

**Themes do not apply.** These are not read in a browser with a preference —
they are composited on her stream, and she picks the look. Design one canonical
appearance, and say which parts she can recolour from the admin.

---

## 4. The five surfaces

### 4.1 Goal bar

The centrepiece, and the reason the rest exists.

A goal has: a **name** ("A new microphone", "Keep the lights on for March"), a
**target**, a **current amount**, and optionally a **deadline**. It is filled by
real Stripe payments — one-off support, memberships, shop orders, or any
combination she chooses in the admin.

Design needs to carry:
- what the goal is for, in her words
- how far along it is — the number, and the shape
- how much is left, which is the part that actually moves people
- optionally, time remaining

**Say what happens at 100% and beyond.** A goal that is met and then keeps
receiving money is a good problem, and a bar that stops at full throws away the
best moment it will ever have. Design the overrun.

Sizes: a **wide** form (a strip along the bottom or top) and a **compact** form
(a corner block). Both, please — scenes differ.

### 4.2 Alert

Somebody just supported. This is the most-seen thing here and the most likely
to be resented if it is wrong.

It carries: **who** (a name they chose), **what** (an amount or a tier), and
optionally **a short message they wrote**.

Design the **arrival, the hold and the departure** as three separate things
with stated durations. An alert that arrives beautifully and then vanishes
abruptly reads as a glitch.

**Two things that are not negotiable:**

- **A queue.** Two supporters within a second must not overlap. Design what the
  second one does while it waits.
- **Messages are moderated before they appear.** Anything a stranger typed
  going straight onto a live stream is a hazard, and this site does not take
  that risk. The design should assume a message may be absent, and must look
  deliberate rather than broken when it is.

### 4.3 Supporters ticker

The recent few, quiet and continuous. Names only, or names and amounts — say
which you recommend and why. This is the one overlay that is always on screen,
so it has the strictest legibility and the smallest animation budget.

Design its empty state properly. A new goal with nobody in it yet is the normal
state at the start of every campaign, and "no supporters yet" written on a
stream is worse than nothing.

### 4.4 Instrument strip

**This is the one nobody else can have, and it is why this set is worth
building rather than buying.**

A small persistent strip showing the current **planetary hour** and its ruler,
and something of **today's sky**. It is on screen while she writes the software
that computes it, which is the whole joke and the whole brand in one object.

It should feel like an instrument panel rather than a widget — it belongs to
the same world as `/tools`, and it is the one place here where the site's
existing visual language should be recognisable at a glance.

Say what it shows when the hour turns over. That is the only thing it ever
does, roughly once an hour, and it should be worth noticing.

### 4.5 Countdown

To a stream start, or to a merch drop closing. Simple, but state:
- what it looks like at hours, at minutes, and at under a minute
- what it does when it reaches zero — it must not sit at 00:00 forever
- whether it is ever on screen at the same time as the goal bar

---

## 5. States every one of these needs

| State | Why it matters |
|---|---|
| **Nothing configured** | She adds the overlay before creating the goal. This is the first thing she will ever see, and "undefined" on a stream is unforgivable. |
| **Zero progress** | Every goal starts here and stays here for a while. |
| **Goal met, and overrun** | The best moment the design gets. |
| **Connection lost** | The overlay is a page; her network can drop. It must hold its last known state and never blank. Say whether it shows anything about being stale. |
| **Alert queue of several** | Design the wait. |
| **A supporter with no message** | The common case. |
| **A very long name** | Somebody will be called `xX_the_longest_possible_handle_Xx`. |

---

## 6. Deliverables

1. **Five overlays**, at 1920×1080, with the wide and compact variants of the
   goal bar. All states above.
2. **The admin surface** for creating a goal and copying an overlay URL. This
   is an ordinary page in the existing admin and should look like it.
3. **A statement of what she can recolour** from the admin, and what is fixed.
4. **Stated dimensions** for each overlay, so they can be added to OBS without
   guessing.

---

## 7. What is already settled — do not re-derive

- **Money comes through Stripe**, which is live and already handles
  `checkout.session.completed` and all three subscription events. Goals are fed
  by real payments, not by anything typed in.
- **Goals are rows**, created and edited in the admin without a deploy — the
  same rule as everything else on this site.
- **Messages from supporters are moderated before they appear on screen.**
- **No third-party requests, ever**, including fonts.
- **The instruments are computed by her own ephemeris**, exactly as the site's
  tool pages are. The strip is not decorative — the numbers are real.
- **These must not assume Twitch or YouTube.** She intends to leave both.

---

## 8. Acceptance

- Legible over a white editor, a dark room and a bright window.
- Nothing scrolls, nothing overflows, nothing shows a scrollbar.
- Idle overlays compose no frames.
- Every state above is drawn, including the ones that look like nothing.
- A stranger watching for one second knows what the goal is and how far along.
- It looks like the same hand as `/today` and `/tools`.

## 9. Files

- `frontend/site/src/pages/overlay/…` — the overlays
- `frontend/site/src/pages/admin/goals.astro` — the admin surface
- `backend/shruti/models/__init__.py` — the `Goal` rows
- `docs/DESIGN_REQUEST_COMPATIBLE.md` — the house format this follows
