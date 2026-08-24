# The journal, BeeRanked, and the sky

**Status:** the sky half is built and working. The BeeRanked half is the piece
we do together — this document is what I need from that conversation, written
down so neither of us has to remember it.

## What is already done

Entries live in BeeRanked. The one thing BeeRanked cannot know is what the sky
was doing when an entry was published, and that is now stored here:

| Route | What it does |
|---|---|
| `POST /api/journal/sky` | Capture and store the sky for one slug. Admin only. |
| `GET /api/journal/sky/{slug}` | Read one back. Public. |
| `GET /api/journal/skies?slugs=a,b,c` | Read many, for an index. Public. |

`JournalSky.astro` renders it, in two shapes: `panel` for the entry itself and
`line` for a card in a list.

Captured just now for a test slug, to show what it produces:

> Moon in Leo · hour of Venus · Hekatombaion ἕνη καὶ νέα · Śukla Pratipadā

Full reading is stored as JSON, so a richer rendering later needs no migration
and no re-casting.

## The three rules this follows, from theourgia

These are not implementation details; they are why the feature is worth having.

1. **The captured moment does not move.** An entry written under a Mars hour
   was written under a Mars hour. `POST` is idempotent by slug and will not
   re-cast unless explicitly told to with `recapture: true`, because the
   ordinary reason it gets called twice is a duplicate webhook, not a
   correction.
2. **It is the machine's half of the record, and is not editable.** There is a
   route to capture and a route to read. There is deliberately none to amend,
   and no admin surface for changing the values. Being able to edit it would
   make the record untrustworthy.
3. **Every absence states its reason.** A failed capture stores why, and the
   component prints it — "the ephemeris could not be reached" — rather than
   rendering a blank where the sky should be.

## What we need to decide together

### 1. How an entry announces itself

Something has to call `POST /api/journal/sky` at the moment an entry publishes.
Options, roughly in order of how much I like them:

- **A BeeRanked webhook on publish.** Best: the capture happens at the true
  moment. Needs BeeRanked to support outbound webhooks and to send the slug and
  the publish timestamp.
- **A poll.** We read BeeRanked's feed every few minutes and capture anything
  new. Works without webhook support, but the captured moment is up to a few
  minutes late — which for a planetary hour boundary can be the wrong hour.
- **Capture on first read.** Simple, but the sky recorded is the sky of whenever
  someone first opened the page, which is not what the entry was written under.
  This one is wrong and I would rather not.

### 2. How the journal is served

The design is explicit that the journal files in the bundle are **a spec that
CMS output must match**, not a page to build. `Prose.astro` is that spec and it
exists. Two ways to honour it:

- **Proxy `/journal` to BeeRanked** and restyle there, so the URL stays on this
  domain. Needs BeeRanked's templates to accept our tokens, or its output to be
  plain enough to style from outside.
- **Fetch and render here.** We pull entries over BeeRanked's API and render
  them with our own `Prose`, which guarantees the design matches exactly and
  lets us drop the sky panel in natively. Costs us BeeRanked's own editing
  preview and any SEO features that depend on its rendering.

The second is what makes the sky panel sit *inside* the article rather than
bolted above it, which is the difference between the feature reading as native
and reading as an add-on.

### 3. What the slug is

Everything here is keyed on a slug. It needs to be BeeRanked's stable
identifier, not the title, and not something that changes when a title is
edited.

### 4. Bylines

The design's rule: magickal writing signs **Soror Eu. A.**, everything else
signs **Shruti**. Whatever we do, BeeRanked has to carry a per-entry flag for
that, or we key it off a tag.

## What I need from you when we do this

- Whether BeeRanked can fire an outbound webhook on publish, and what it sends.
- Its API for listing and fetching entries, and what a slug looks like.
- Whether `/journal` should be proxied or rendered here.
- An API key or whatever it authenticates with.
