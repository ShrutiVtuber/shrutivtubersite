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
| Server | netcup, 159.195.251.161, `deploy@`, key `~/.ssh/agents_netcup` — see `SERVER-ACCESS.md` |
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

And, added just after:

> we'll also need documentation when we have it for our products etc as well
> from beeranked so we should be able to display nicely all the stuff — we
> should make a few to act as placeholders so we can see how it will display
> with various types of content.

So the section handles **at least four content types**: blog posts, changelog
entries, documentation for her products (Theourgia, shruti-astro, the mobile
app), and whatever reference/wiki pages follow. All from BeeRanked, all wearing
Shruti's theme.

**Build placeholder content of each type via the MCP first**, before styling
anything. She asked for this explicitly and she is right: a stylesheet written
against one sample post is a stylesheet that breaks on the first doc page with
a code block, a table and four heading levels. Make one of each — a post with
a cover, a post without, a changelog entry, a doc page with headings and code,
a reference page — then design against the real spread.

### An open question, for her, not for code

Blog and changelog read chronologically. **Documentation does not** — it reads
by structure, and wants a sidebar, a version, and a stable URL per topic.
Putting product docs under `/journal` may be wrong: `/journal` for the writing
and the changelog, `/docs` for the manuals, both from BeeRanked, is the obvious
alternative and probably the better one.

Ask her. Do not resolve it in code.

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

### rebetichord is a REFERENCE FOR HOW IT LOOKS, not a template to follow

She was explicit: *"We don't have to do what rebetichord does please don't do
that actually."* She pointed at it because `/news` reads like a nice blog and
she wants that quality — **not** because its architecture should be copied.

So: look at the rendering and the page inventory for ideas about what a good
content section contains. Then build it the way this site is built.

`~/Documents/development/bouzouki-project` holds it, if you want the reference:

- `BEERANKED_DESIGN_REQUEST.md` — the design brief for their `/news`. Reads as
  a specification of every page type a BeeRanked section can have.
- `news-chrome/server.py` — a sidecar that boots their React SPA to get the
  site chrome around the content. **We need none of this.** Astro renders on
  the server, so a route can render BeeRanked content inside `BaseLayout` and
  get the real header, footer and tokens for free.

### The shape to aim for

**Ask the MCP what it offers first.** It may expose content directly, which
would mean no file sync at all — a route that queries BeeRanked and renders.
Do not assume the agent-and-directory arrangement is required just because
rebetichord uses it; find out, then choose.

Then, roughly:

1. Astro routes under `frontend/site/src/pages/journal/`, rendering inside
   `BaseLayout`.
2. `/journal` as the index: posts and changelog interleaved, changelog entries
   marked as what they are.
3. The site's own tokens throughout. The design system is in `design/` —
   `design_handoff_shrutivtuber/` has the component library, and the tools
   pages are the closest existing example of long-form content in this theme.

**BeeRanked is trusted here** — it is her partner's product and she owns the
content in it. Rendering its HTML directly is the normal thing to do, the same
way any site renders its own CMS's output. Do not build a sanitising pipeline
around it; that was rebetichord's answer to a different situation and it is not
this one.

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
