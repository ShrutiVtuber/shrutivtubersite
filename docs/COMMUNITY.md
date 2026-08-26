# Sponsors, and the site as a hub

Live 2026-08-26.

## Sponsors

| Where | What |
|---|---|
| `models/__init__.py` → `Sponsor` | name, tagline, body, url, cta label, **background + ink**, two logos, featured, since/until |
| `/admin/blocks?kind=sponsors` | full CRUD, in-place logo upload, colour picker + hex box |
| `SponsorRow.astro` | the landing-page row, after the instruments |
| `/partners` | everyone, at length, with the disclosure |

**Colours are columns.** A sponsor's brand is theirs. This is the one table on
the site where storing a hex is correct rather than a way around the tokens.
Anything not exactly `#RRGGBB` is dropped at the API, so a typo produces a plain
card instead of a broken one.

**Three on the home page, capped in the route** — not the database, so ticking a
fourth shows her the result rather than throwing an error. A sponsor whose
`until` has passed is dropped from the featured row automatically.

**Every link carries `rel="sponsored"`.** Not saying so gets expensive.

### What she still has to do

- Upload the BeeRanked logo in the admin. Until then the card shows a wordmark,
  which is a real fallback rather than a gap.
- `SHRUTI_DISCORD_GUILD_ID` on production, if she wants the live member count.
  The invite already works without it.

## The four community features

**Discord** — `/api/community/discord`. The server asks, caches 60s, returns a
count and an invite. Deliberately **not** the embed widget: an iframe means
every reader's browser talks to Discord. Zero third-party requests on every page
is rarer than any feature on this site and trivially easy to lose. The widget's
member list (usernames, avatars) is **not shown**.

**Polls** — one vote each, enforced by a unique index rather than by the route
remembering to check. Changing a vote moves it. Answers are immutable once the
poll exists. Results refresh every 6s while the tab is visible; voting works
with scripting off, posting to `/community`.

**Push** — payload-less Web Push. The push carries nothing; the service worker
wakes and fetches `/api/community/push/notice`. No aes128gcm, no new dependency,
and nothing readable transits Mozilla or Google. VAPID is an ES256 JWT signed
with `pyjwt[crypto]`, which was already here. Never account-gated.

**The glyph trainer** — 21 symbols, entirely client-side. Deliberately **not** a
fortune-telling toy: every instrument here says what it cannot compute and
`/terms` says nothing on the site is predictive.

## Things that will bite

- **Never regenerate the VAPID keys.** A browser binds its subscription to the
  key it saw. New keys silently unsubscribe everybody — they keep the permission
  and simply stop receiving anything, which is the worst kind of broken.
- **`.page` inside `.site-main` needs `min-width: 0`** when its content contains
  anything `white-space: nowrap`. The live badge's meta line is nowrap with an
  ellipsis, and without `min-width: 0` the card cannot shrink below that one
  line — it pushed `/community` 24px wide at 360px. The ellipsis exists to be
  used; `min-width: 0` is what lets it.
- **A regex's `{6}` inside an Astro template attribute** closes the expression
  early — the braces are counted, not parsed. Same trap as a TypeScript
  annotation in a template arrow function. Put it in the frontmatter.
- **The test container now mounts `frontend/site/public` and `backend/alembic`.**
  Neither was readable there, so any guard touching the service worker or a
  migration would have passed on an empty string.
- **Headless Chromium cannot subscribe to push** ("Registration failed -
  permission denied") — it has no push-service connection. The server side is
  verifiable and was: Mozilla accepted the VAPID signature and returned "gone"
  for a fake endpoint, which pruned itself. **End-to-end delivery has not been
  tested in a real browser.**

## Not done

- No automatic "she went live" trigger. The notification is sent by hand from
  `/admin/community`. Wiring it to the Twitch poller is a small next step and
  deliberately not guessed at — a false "live" notification is expensive.
- No web-push for new journal entries yet; the `wants_writing` flag exists and
  the audience selector is built.
