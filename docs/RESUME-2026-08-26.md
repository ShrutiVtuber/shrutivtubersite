# Resume note — 26 August 2026

Written because context was filling. If you are picking this up cold, read this
first, then `docs/NEXT.md`.

## Where things stand

**The website is built and deployed**, behind the holding page. 446 backend
tests, 55 bot tests. Everything below is live on production unless it says
otherwise.

**The one thing blocking launch is the imprint address** — a Greek lawyer
question, not a build. Jurisdiction is **Greece**, not Germany: the imprint
form offers `GEMI` and `VAT EL…`. Earlier legal research was commissioned
against Germany by mistake and is marked not-applicable in
`docs/MARKETING_2026-08-26.md` §0.

## Built today, in order

| What | Where |
|---|---|
| SEO audit + every correction | `docs/AUDIT_SEO_2026-08-26.md` |
| Marketing research | `docs/MARKETING_2026-08-26.md` |
| Instrument pages deepened, `/tools` hub | rows in `tool`, editable |
| `/compatible` design pass | `docs/design/HANDOFF_COMPATIBLE.md` |
| `/collab`, `/official` | new pages |
| Shop: always-open **and** windowed drops | `product.opens_at/closes_at` |
| Instruments remember your place | `site_user.place_*` |
| `/admin/growth` — her two lists | `growth_item` |
| **vcordbot** — Discord bot | `bot/`, live at bot.shrutivtuber.com |
| Twitch EventSub | `/admin/twitch` |
| Counters + counter overlay | `/admin/counters`, `/overlay/counter` |
| Alerts overlay — nine members, one queue | `/overlay/alerts` |
| Sky chart + hours strip | `/overlay/sky`, `/overlay/hours` |
| Ticker + countdown | `/overlay/ticker`, `/overlay/countdown` |
| Web variants | `SkyCard` on `/`, `CounterCard` on `/support` |
| Guard: every sitemap page must be linked | `test_every_page_is_reachable.py` |

## In flight

**The overlays.** Design handoff at `docs/design/HANDOFF_OVERLAYS.md`;
reconciliation with the schema at `docs/design/OVERLAYS_DELTAS.md`.

**The overlay set from the handoff is complete.** All six OBS surfaces, both
web variants, and sound:

| | |
|---|---|
| Counter bar (wide + compact) | `/overlay/counter` |
| Alerts — nine kinds, one queue | `/overlay/alerts` |
| Supporters ticker | `/overlay/ticker` |
| Sky chart | `/overlay/sky` |
| Planetary hours strip | `/overlay/hours` |
| Countdown | `/overlay/countdown` |
| Web variants | `SkyCard` on `/`, `CounterCard` on `/support` |
| Sound | uploaded and assigned in `/admin/counters` |

She mints the tokens herself in `/admin/counters` — there are none in either
database, by design. Each URL is one OBS Browser Source at 1920 × 1080.

Nothing from the handoff is outstanding. What is left is hers, not mine — see
the list below.

## Editing copy — where things live now

| What | Where |
|---|---|
| Sections on a page (eyebrow, heading, prose, link, art) | `/admin/blocks?kind=sections`, grouped by page |
| Every other string on a page | `/admin/copy` — the **Words** screen, grouped by page |
| Instrument name, summary, body, FAQ, reckoning | `/admin/blocks?kind=tools` |
| Journal entries | BeeRanked, not here |

**The rule.** A page ships its own words as the default and always renders
them; a `copy` row only ever overrides one. An empty table renders a complete
site. So a new page needs no migration — write it with `t("key", "the words")`,
then run `node scripts/seed-copy.mjs` and it appears in Words.

Two converters, both of which refuse rather than guess:

- `scripts/convert-to-copy.py <file> <page>` — plain text nodes.
- `scripts/convert-inline-copy.py <file> <page>` — a paragraph carrying a link
  or a bold run becomes ONE string holding inline markdown, rendered by
  `components/content/Copy.astro`. Splitting those instead would give her
  "Their hours are in" as a box to edit.

`<Copy vars={{...}} />` fills `{name}` placeholders, for a sentence built
around a value.

**Reseeding is safe and necessary.** A row whose value still equals its seeded
default has never been edited, so a changed template updates it. Once she edits
it the two diverge and seeding leaves it alone. Without that rule, rewriting a
line in a template silently does nothing — which happened, on /press.

414 words remain in templates, all sentences wrapping an expression.

---

## Next session: the commission progress tracker

Agreed 2026-08-27. The thing from the tweet she saved — clients having to beg
for updates on a commission, no Trello, no visible progress. On the growth list
twice: build it, then use it on her own commissions first, which is the only
way to find out whether it is any good.

Everything else outstanding is on `/admin/growth` — 26 items, and that list is
the source of truth rather than this file.

**She is writing page copy in the meantime.** Do not touch content she may be
editing: `section`, `tool` (name, summary, body_md, faq_md, landing_blurb,
reckoned), and anything under `/admin/blocks`.

---

## Decisions not to re-litigate

- **The astrology engine is not changed to fit a design.** Her words: *"don't
  change the engine to fit the design but adjust the design to fit the
  engine."* The `/compatible` handoff wanted seven fixed testimonies; the
  engine bands by ratio. The page was adapted.
- **Everything user-visible is editable from the admin.** If copy is pulled
  from a row anywhere it must be that row everywhere. Guarded by
  `test_instruments_are_content.py`.
- **The bot is read-only against the website** and holds no site credential at
  all. It computes via `shruti-astro` directly.
- **The bot is free.** Discord already syncs YouTube and Twitch memberships
  natively and free, which killed the paid tier before it was built. Member
  sync is dropped — it was the only reason to hold other people's OAuth tokens.
- **Every free-tier bot message carries the attribution footer**, which also
  carries the automated-post disclosure.
- **Counters hold no running total.** A counter is a sum over `support_event`.
- **Overlay tokens are shown once**, at mint. No route returns one afterwards.

## Traps already paid for — do not rediscover

1. **CSP `form-action 'self'` governs the whole redirect chain after a form
   POST.** It silently broke Twitch authorise *and* Buy / Support / Manage
   subscription. curl cannot reproduce it. Fixed by naming the Stripe origins
   and making Twitch a link. Guarded by `test_csp_form_action.py`.
2. **OBS has no session.** Overlay paths must bypass the holding-page gate or
   every overlay renders the holding page — on stream.
3. **`ON CONFLICT` cannot use a PARTIAL unique index** unless the statement
   repeats the predicate, and SQLAlchemy emits it as a bound parameter which
   never matches. Every insert fails. Fixed by giving every event an id.
4. **A source-reading test passed while that was broken.** Guards against SQL
   behaviour belong on the migration.
5. **Comments trip their own checks** — five times now. Strip docstrings and
   comments before scanning source. `bot/tests/conftest.py` has `code_of`.
6. **Prod containers are baked images.** A new migration or module needs
   `--build` before it exists in the container.
7. **`Astro.url` reports localhost behind Caddy.** Use `SITE_URL`.
8. **A page can ship reachable by nobody.** `/collab` and `/official` were
   built, deployed and in the sitemap with zero inbound links. Guarded now —
   and the guard has to know that the instruments and the primary nav are
   linked from DATA, not from literal hrefs.

## Access facts

- Deploy: `ssh -i ~/.ssh/agents_netcup deploy@159.195.251.161`,
  then `cd /srv/shrutivtuber/prod && git pull && docker compose -f
  docker-compose.yml -f docker-compose.prod.yml --profile web --profile bot up
  -d --build`, then `alembic upgrade head`.
- Secrets go in via `./scripts/set-secret.sh NAME` — echo off, never in chat.
- `python3 bot/scripts/check-app.py` audits the Discord application.
- `/home/sophia/stopextra` stops other Claude sessions, never its own.

## Hers, not mine

Live in `/admin/growth`. The three that matter most:

1. **Change the Twitch category to Software and Game Development.** Two
   minutes, free, highest leverage on the list — Astrology has no ranked
   channels; Software and Game Development does 368,185 viewer-hours.
2. **Email a Greek lawyer about the imprint address.** The only hard blocker.
3. **Run vcordbot beside Pingcord for a week, then cancel.**

Also outstanding: `/official` is live and empty; Stripe key rotation; and
**nobody has ever completed a checkout in a browser** — worth doing now that
the CSP bug is fixed.
