# Resume here

Written 2026-08-25, after the site went live. Read this first.

## Where things actually stand

**shrutivtuber.com is LIVE on the new stack.** DNS is cut over, TLS is valid,
the holding page is serving, and Shruti has claimed the admin. The old
WordPress is no longer what the domain resolves to.

```bash
curl -s https://shrutivtuber.com/ | grep "The sky is not waiting"   # the holding page
curl -s https://shrutivtuber.com/api/admin/claim                     # {"claimed":true}
```

Everyone gets the holding page. **She gets the real site**, because the
middleware bypasses the gate for a signed-in operator — and the site shows a
bar at the top saying so, since the header only reflects a *reader* session and
an admin cookie is otherwise invisible. That invisibility cost an evening once;
don't remove the bar.

The switch is **Admin → Settings → "Who can see the site"**. One button.

### The boxes

| | |
|---|---|
| Server | `agent-house`, 178.105.106.225, `theourgia@`, key `~/.ssh/agent-house-access-theourgia` |
| Site | `/srv/shrutivtuber/prod` — compose pair, `--profile web` |
| Ephemeris daemon | `/srv/shruti-astro/prod` — **separate repo, deploy it too** |
| Local | `~/Documents/development/shurtiwebsite`, `~/Documents/development/shruti-astro` |

`docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile web`
is the incantation. Tests: `./scripts/test.sh` in either repo — **not**
`docker compose exec`, which runs the prod image and produces phantom failures
(that mistake cost real time; the script exists to prevent it).

## THE NEXT TASK — BeeRanked at /journal

She asked for this and then stepped away to connect the MCP. **It is not
started.** Nothing has been built.

### What she asked for, in her words

> set it up with the mcp please to be at /journal — all we will want to show
> are the changelogs as posts as well as actual posts from beeranked. It should
> read like a nice blog — look at rebetichord and try to make something that is
> nice like that but will blend with our theme, and a link to the changelogs
> etc on the side or somewhere that looks nice.

So: **posts and changelog entries, both as posts, in one blog at /journal**,
wearing Shruti's theme, with the changelog reachable from somewhere tasteful.

### The MCP

`beeranked` is an HTTP MCP at `https://studio.beeranked.online/api/mcp` with an
`Authorization` header. It was configured for her other projects and **I added
it to this project's entry in `~/.claude.json`** (backup of that file is in the
session scratchpad). MCP servers only load at session start, so it appears
after a restart — which is why she exited.

**Check it is actually connected before planning around it.** If it is not,
say so rather than improvising.

She has already made "the Shruti VTuber company thing" in BeeRanked Studio and
done nothing else, so expect an empty org.

### How rebetichord does the same thing — study this first

`~/Documents/development/bouzouki-project` is the working precedent, and it is
worth an hour before writing anything:

- `BEERANKED_DESIGN_REQUEST.md` — the design brief for their `/news`. Reads as
  a specification of every page type a BeeRanked section can have.
- `news-chrome/server.py` — their injector. **The key architectural fact**: a
  `beeranked-agent` on the VPS polls `…/api/agent/manifest` every ~30s and
  writes rendered content into a directory (`/home/rebetichord/beeranked/content`,
  mounted read-only). The injector reads those FILES, extracts the data, and
  re-emits the site's own page skeletons. BeeRanked's own chrome and CSS are
  stripped.
- `frontend/Caddyfile` — `handle /news*` → strip prefix → the injector.

**Do not copy their architecture wholesale.** Theirs exists because their site
is a React SPA that has to be booted to render its chrome. Shruti's site is
Astro SSR, so an Astro route can read the synced content and render it inside
`BaseLayout` directly — real header, real footer, real tokens, no sidecar, no
second service. That is simpler and better here.

### The shape to aim for

1. A `beeranked-agent` (or equivalent sync) on the server writing content into
   a directory the site container can read.
2. `frontend/site/src/pages/journal/[...slug].astro` reading that content,
   rendering inside `BaseLayout`.
3. `/journal` itself as the index: posts and changelog entries interleaved,
   changelog entries marked as what they are.
4. Styling in the site's own tokens. The design system is in `design/` —
   `design_handoff_shrutivtuber/` has the component library.

**Security note, taken seriously by rebetichord and worth repeating**:
BeeRanked output is remote-controlled content served on the same origin as the
auth cookie. Their injector escapes and sanitises every extracted fragment
before re-emitting it. Whatever renders BeeRanked HTML here must do the same —
`set:html` on untrusted markup is an XSS hole on a site with sessions.

### One thing already built for this

`POST /api/journal/sky` and friends exist (migration `c9a04e1b78f2`). Each
journal entry can have the sky at publication stored against its slug, so a
post can carry what the sky was doing without recasting the chart on every
read. `docs/JOURNAL_BEERANKED.md` has the four decisions that were left open.
That is the "keep all the astro benefits" half of what she asked for months ago
and it should not be dropped on the floor.

## What else is outstanding

**Hers, and only hers:**

- **Live Stripe.** Test mode is proven end to end — subscription created,
  cancelled, webhooks watched, emails sent. Live mode is a separate world:
  separate keys, separate products, separate prices, and nothing copies. Two
  things must be right at creation because neither can be changed after: tax
  code `txcd_10000000`, and tax behaviour **inclusive**. Prices are €5 and €11.
  `SHRUTI_STRIPE_*` is deliberately blank on prod, so /support says "not open
  yet" rather than half-working.
- **An attorney** on the withdrawal paragraph in /terms (the immediate-
  performance one), and **an accountant** on the VAT classification.
- **Schedule and horoscopes** — both pages render designed absent states, and
  the homepage keeps its horoscope section standing with nothing published, but
  a stream on the schedule and one set of twelve readings is the difference
  between "new" and "abandoned".
- **The imprint.** Hidden until filled in and switched on. No invented registry
  numbers anywhere — that rule is enforced by a test that walks every email
  template.
- **Cancel Nexcess.** Not yet. Keep the final WordPress export offline for a
  year.

**Deferred by decision:** candrodaya and saṅkrānti puṇyakāla remain
deliberately unmodelled rather than guessed — Dīpāvalī shows as undated on the
Hindu calendar for exactly that reason, and that is correct behaviour.

## Things that will bite you

- **`.env` is not in git.** Prod's copy has Twitch, YouTube and R2 set, Stripe
  blank. `./scripts/set-secret.sh KEY` prompts with the echo off and checks the
  prefix — it exists because a Twitch *stream* key was once handed over as if
  it were an API credential.
- **Route order in `backend/shruti/api/routes/admin.py`.** `/{kind}` swallows
  anything declared after it. This bit three times; the catch-alls now sit
  behind a banner at the end of the file and `tests/test_admin_routes.py`
  asserts the property. Do not move them.
- **A `<=` inside JSX breaks the Astro build** with an error pointing at a line
  nowhere near it. Keep operators in the frontmatter.
- **Festival years are cached and warmed at boot** from middleware, sequentially.
  Resolving 72 Hindu entries takes 12–15s in the daemon, and four parallel
  requests to a two-worker daemon starve each other. Don't parallelise the warm.
- **Admin sessions carry a stamp** of the operator's email and password hash,
  checked on every request, so changing either ends every existing session.
  Tokens are not valid on signature alone any more.

## The go-live checklist artifact

https://claude.ai/code/artifact/911cc2c1-60e4-46d5-ba3f-43bd71cf9806 —
her remaining items, with tick state saved in her browser. Update it in place
with `url`, never republish to a new one.
