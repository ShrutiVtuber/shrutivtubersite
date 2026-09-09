# Where the site is, 9 September 2026

The August note is kept beside this one as `RESUME-2026-08-26.md` — it covers
the cutover and the design pass, which are done.

Written before a compaction.

## Live

`https://shrutivtuber.com`, deployed from `/srv/shrutivtuber/prod` on
159.195.251.161 as `deploy`, with `~/.ssh/agents_netcup`. **The holding page is
still up** — she is signed in as owner, so she sees the real site and anonymous
visitors do not.

⚠ **Pushing is not deploying.** Three times this session she was looking at
work that had never left this machine. The site's footer prints the deployed
commit; that is the fastest way to settle "is this live".

```bash
cd /srv/shrutivtuber/prod && git pull --ff-only
export SHRUTI_SOURCE_SHA=$(git rev-parse HEAD)
dc --profile web --profile bot up -d --build
dc exec -T backend alembic upgrade head
```

⚠ **Then seed the copy**, or new strings render fine and are missing from the
admin. `docs/DEPLOY.md` has the command. Forgetting it stranded 61 strings.

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

## Next, in her order

Read **`docs/PLAN-horoscope-practice.md`** first: eleven requirements, two
decisions taken, and the one real constraint — her bot is HTTP-interactions
only and the bridge she chose needs a gateway, which is a new long-running
process rather than a permission.

Outstanding on the site specifically:

1. **Supporters give a name to be read on stream** — asked at the point of
   donating or subscribing, optional, custom names allowed.
   ⚠ **Monthly only. One-offs are not read out.**
2. **Practice readings**: drafts kept to an account rather than to a browser,
   and a **series** as a first-class thing — twelve signs for a week is one
   piece of work.
3. **A Discord slash command** handing back the material to write from. The
   cheap half: the bot already answers signed interactions and already talks to
   the ephemeris.
4. **The standing compatibility test** — a fixed one against her chart, and
   per-VTuber ones with a tier-set lifetime (5 days / 10 / permanent). It is
   the only item that touches billing, and the expiry is what will go wrong
   quietly.

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

Each has a test. Every one of them looked completely fine.
