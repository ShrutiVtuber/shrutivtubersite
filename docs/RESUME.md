# Where the site is, 9 September 2026

The August note is kept beside this one as `RESUME-2026-08-26.md` — it covers
the cutover and the design pass, which are done.

Written before a compaction.

## ⚠ Read this first if it is the morning of 10 September 2026

She asked, last thing, for a note so she could **ask to be walked through the
three things that need her**. That walkthrough is `docs/SETUP-THREE-THINGS.md`
— Firebase, the Discord MESSAGE_CONTENT intent, and pointing her own
compatibility test at her chart. It is written for somebody starting cold: what
she does, what I do, and how we know each one worked.

Offer it. She is expecting to be asked about it rather than to have to remember
which three.

## Is it ready to launch?

`docs/LAUNCH-READINESS.md` answers it properly. Briefly: the ephemeris licence
is settled (all three repos public and AGPL, and the notice is now inside the
app), compliance is strong with two decisions that are hers, and it is not
feature complete until the three setup tasks and one design pass are done.

## Live

`https://shrutivtuber.com`, deployed from `/srv/shrutivtuber/prod` on
159.195.251.161 as `deploy`, with `~/.ssh/agents_netcup`. **The holding page is
still up** — she is signed in as owner, so she sees the real site and anonymous
visitors do not.

⚠ **Pushing is not deploying.** Three times this session she was looking at
work that had never left this machine. The site's footer prints the deployed
commit; that is the fastest way to settle "is this live".

⚠ **Run it as `theourgia`, not as `deploy`.** The checkout and `.env` belong to
uid 1008 and `deploy` is not in that group, so a plain `git pull` fails on
FETCH_HEAD and compose fails on `.env` — both with permission errors that read
like a broken box rather than a wrong user. `deploy` has passwordless sudo.

```bash
ssh -i ~/.ssh/agents_netcup deploy@159.195.251.161
sudo -u theourgia -H bash -lc '
  cd /srv/shrutivtuber/prod && git pull --ff-only
  export SHRUTI_SOURCE_SHA=$(git rev-parse HEAD)
  docker compose -f docker-compose.yml -f docker-compose.prod.yml \
    --profile web --profile bot up -d --build
  docker compose -f docker-compose.yml -f docker-compose.prod.yml \
    exec -T backend alembic upgrade head
'
```

(First time only: `git config --global --add safe.directory /srv/shrutivtuber/prod`.)

⚠ **Then seed the copy**, or new strings render fine and are missing from the
admin. Forgetting it stranded 61 strings once already.

```bash
node scripts/seed-copy.mjs --json > /tmp/copy.json      # locally
scp -i ~/.ssh/agents_netcup /tmp/copy.json deploy@159.195.251.161:/tmp/
ssh … 'sudo -u theourgia -H bash -lc "cd /srv/shrutivtuber/prod && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec -T backend python scripts/seed_copy.py < /tmp/copy.json"'
```

⚠ The seeder reads **stdin**, not an argument. A path is silently a JSON parse
error on the empty string.

## Done this session

- **Horoscopes**: canonical dated URLs, per-sign feeds, oEmbed, share cards
  drawn server-side with resvg. Weekly now surfaces everywhere — the backend
  always had it, only the site's archive and index hardcoded monthly.
- **The editor**: preview links no longer navigate, component words are
  editable there, images can be set from it, and **every visible string on the
  site is editable** — a sweep that names no element types is a test now.
- **The writing desk**, public at `/tools/horoscope-writing`. Its card comes
  from a `tool` row, so its words are editable like every instrument's.
- **Language packs** served from `/packs/*` and listed at `/api/packs`, on
  production, digests verified. All Rights Reserved — a test refuses any `.mbf`
  committed anywhere.

667 tests pass. `astro check` sits at **143 errors — that is the baseline**, not
a regression.

## The app signs in against this site

`GET /api/account/consents` serves the three decisions with the exact wording
that gets filed, so Shruti's Tools has no copy of its own. `current_user` reads
`Authorization: Bearer` when there is no cookie, and `signup`/`signin` return
the session token **only when the body says `bearer: true`** — the website never
sends it, so browser replies are unchanged.

⚠ **The cookie wins when both are present.** A request carrying a cookie is a
browser, and its cookie was issued httpOnly; letting a header override it would
let a script that cannot read the cookie still choose whose account the request
runs as. `tests/test_the_app_signs_in.py` holds that.

## The ephemeris and the writing desks

`components/tools/SkyReference.astro` is the sky for a span of days — phases
with sign and degree, eclipses, planetary ingresses, stations, void-of-course,
the daily table and the aspectarian. **One component, three places**: the
ephemeris page, the public writing desk and hers. `SkyDrawer` wraps it in a
`<dialog>` so it opens beside the writing without pushing it around, and
remembers being open across the reloads the desk does on every change.

- Retrograde is a **band** down the column, not just a mark on each row.
- The ephemeris page is `wide` — aside underneath, no horizontal scrollbar. That
  scrollbar is what put the eclipses off the right edge.
- ⚠ Past ~70 days the daily detail is not offered. A year is 365 rows and some
  twelve hundred aspects, and the page says so rather than rendering half.

**Corrections.** `horoscope_revision` keeps what a published reading used to
say; `Horoscope.edited_at` marks that it changed. The reading shows a quiet
"Edited …" linking to `/horoscopes/<sign>/<period>/<covers>/history`.
⚠ `is_a_correction()` decides what is filed: published AND actually different.
Drafting is writing, and the desk autosaves — filing either would bury the one
correction anybody came to see.

## Everything on her list is built

Outstanding items from the practice plan, all done:

1. **Supporters give a name to be read on stream** — asked at the SUBSCRIPTION
   checkout as a Stripe custom field. ⚠ The one-off builder has no such field,
   so a gift cannot carry a name and there is nothing to filter later. Names to
   read are listed at `/admin/memberships`.
2. **Practice readings** — `practice_work` / `_reading` / `_vote` / `_comment`.
   ⚠ A WORK is the unit: twelve signs is one piece of work. The site's desk
   keeps drafts to the account, so a reading started on a phone finishes at a
   desk. In the app: the Practice tab.
3. **The Discord slash command** — `/horoscope` hands back the material to
   write from and interprets nothing.
4. **The standing compatibility test** — hers permanent at
   `/compatible-with/shruti`; anybody else's runs 5/10/permanent by tier.
   ⚠ An expired one still HAS a page saying what would keep it up.
5. **Notifications** — `core/notify.tell(kind, …)` is the only thing that
   decides who hears what. Triggers wired for readings published, replies to
   your practice reading, and going live.

### ⚠ Her own compatibility test needs her chart

`/compatible-with/shruti` has no test behind it on production yet, because
setting one up means naming a chart — and inventing a birth moment for her would
be worse than leaving it empty. One call once she has cast and kept hers:

```bash
# the owner token of a chart on her account
curl -X POST https://shrutivtuber.com/api/standing/admin \
  -H "Content-Type: application/json" -b "shruti_session=<her admin session>" \
  -d '{"chart":"<owner token>","slug":"shruti","host_name":"Shruti",
       "blurb":"For fun. It means nothing, and it is quite fun."}'
```

It is permanent, and re-running it repoints the existing one rather than
refusing.

### ⚠ Three things only she can do

**Firebase**, for notifications to actually leave the building, and
**MESSAGE_CONTENT** in the Discord developer portal for the bridge's inbound
half. Both are written, tested and dormant; `docs/PLAN-horoscope-practice.md`
has the exact steps. Unconfigured is a WORKING state in both — nothing raises,
nothing 500s, the features are simply quiet.

## Traps this session paid for

- **A trailing comma** in `say(…,…,)` made the seeder skip the string entirely.
  The page rendered its default and the admin had no row. One character.
- **`{/* … */}` cannot open an expression that returns an element.** Astro
  drops the comment AND the element's attributes, silently. Made twice.
- **`{say(…)}` inside a template literal** is four characters and a function
  name. Two pages shipped it as visible text.
- **NOT NULL columns not on the model's face** — `tool` has `locale`,
  `landing_blurb`, `faq_md`.
- **Marks need U+FE0E** or a browser may draw them from a colour emoji font.
- **Migration filenames must not share a revision prefix**: `rm d4a71b*`
  deleted a second migration.
- **Astro INLINES small client scripts** — no `src=` on the tag. Grepping for
  `<script type="module" src=` says a page has no script when it has one, and
  looks exactly like a site-wide breakage. It is not one.
- **Interleaved builds leave a broken `dist/`.** A build run while a `git stash`
  was active left the manifest naming client scripts that were not on disk.
  `rm -rf dist` before trusting a strange build.
- **A guard nobody invokes is a comment.** `scripts/check_consent_wording.py`
  said "run in CI" and grep found its name nowhere else. It runs in the suite
  now.
- **A test that asks the machine instead of saying.** `test_storage` read the
  real R2 configuration: green on a laptop without a bucket, red on one with
  `.env` filled in.
- **The deploy checkout belongs to `theourgia`, not `deploy`.** As `deploy` the
  pull fails on FETCH_HEAD and compose on `.env`, both reading like a broken box
  rather than a wrong user. See the Live section.

Each has a test. Every one of them looked completely fine.
