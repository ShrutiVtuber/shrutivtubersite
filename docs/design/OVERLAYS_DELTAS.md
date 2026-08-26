# Overlay handoff — where it meets the code that already exists

Read with `docs/design/HANDOFF_OVERLAYS.md`. Everything below is a place the
handoff's §2 sketch and the tables already built differ, decided once here so
it is not re-decided per file.

The handoff's own rule applies throughout: **where the drawn design and the
written spec disagree, the design wins.**

## 1. `progress` is not a column, and this is not a disagreement

§2 sketches `Counter.progress: Decimal` with the note *"summed server-side,
never client-side"*. The built model has **no progress column** — a counter is
a sum over `support_event` computed on read.

That satisfies the note exactly, and it buys three things a stored total does
not: a counter created today counts what already happened rather than starting
at nought; its sources can change with nothing to recompute; and a
double-delivered webhook cannot corrupt a total that does not exist. The API
returns `progress` as the handoff expects. Nothing above the API can tell.

**Overrun is uncapped**, as §2 requires — the sum is returned as it is.

## 2. Motion and appearance live on the overlay, not the counter

§2 puts `appearance` and `motion` on `Counter`; §11 calls motion *"a
per-overlay setting"*, and §5 sets `data-skin` per canvas. §11 is right and the
built `overlay_token` row carries both.

The reason is hers: she streams from more than one machine, and the same
counter shown on both wants different motion. A counter-level setting cannot
express that.

## 3. Tokens are rows, one per overlay

§2 hangs `token` off `Counter`; §10 asks for *"one token per overlay, revocable
and regenerable per row without touching OBS layout"*. The built
`overlay_token` table does that, with a nullable `counter_id` — the sky chart,
the hours strip and the alert surface reference no counter at all.

## 4. Sources are already recorded, and `YOUTUBE_MEMBERSHIP` is genuinely absent

`support_event.source` carries the strings §2 lists. The Twitch half is live:
subscriptions, gifts, cheers, raids and follows arrive by EventSub, verified by
HMAC, deduplicated on Twitch's own message id, and a gifted subscription is
counted once rather than twice.

`youtube.membership` does not exist as a source — not unticked, absent — which
is what §9 asks the admin to show as **unavailable**.

## 5. Still to build

- `alert_sound` — upload, per-type assignment, per-type gain, global mute (§7)
- The WebSocket push and its 30s poll fallback (§3)
- Self-hosted font binaries with `font-display: block` (§13). **The design file
  loads three faces from the Google CDN and says not to** — this is the single
  easiest thing to carry across by accident, and it would put a third-party
  request on every overlay and a fallback face mid-broadcast.
- The six overlay pages, the two web variants, the admin (§1)

## 6. The thing worth reading twice

§12 answers a question the brief asked and could not answer itself: what does a
"ticking" sky chart actually tick?

Not the bodies. The Moon moves about half a degree an hour, so **an animated
dot would be a lie at stream length**. The honest liveness tell is the drift
readout beside it (`+0°33′ / h`) and a seconds digit that never stops — one
text node repainting, which is also the cheapest thing on the client.
