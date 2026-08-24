# ADR 0001 — Astrology code licensing and the AGPL boundary

**Status:** accepted · 2026-08-24
**Decided by:** Sophia

## Context

Swiss Ephemeris is dual-licensed **AGPL-3.0 or commercial**. Sophia will buy the
commercial licence for **Theourgia** and **astropractise**. She will *not* buy
one for the shrutivtuber.com public tools, so anything on this site that touches
Swiss Ephemeris must live under the **AGPL arm** of that dual licence.

The site is also to carry **Vedic and Hellenistic astrology side by side**, so
this is not a marginal feature — it is a whole surface of the product.

## The thing that makes this strict

AGPL-3.0 §13 (the network clause) requires that users interacting with the
software **over a network** be offered the *Corresponding Source of the whole
combined work*. If the site backend links `pyswisseph` in-process, then:

- the entire shrutivtuber.com backend becomes a work based on the Program, and
- its complete source must be offered to every visitor of every page.

**A separate repository does not create separation.** Licence boundaries follow
the *program* boundary, not the repo boundary. Two things in one process are one
work regardless of which git remote they came from.

## Decision

1. **A separate program, not just a separate repo.** All Swiss Ephemeris use
   lives in its own service — its own repo, own container, own process — talking
   to the site over an **HTTP JSON API**. Arm's-length data exchange between
   independent programs keeps them separate works.

2. **That service is AGPL-3.0**, wholly and explicitly. `LICENSE` at the root,
   SPDX headers on every source file, and the licence stated on the service's
   own index.

3. **Every public tool page carries a visible Source link** pointing at the
   public repo **at the commit actually running**. AGPL §13 requires the source
   of the *running* version, so the service exposes its build SHA and the page
   links to that tree — not to `main`.

4. **No shared code with Theourgia.** Not a shared package, not a vendored
   module, not a copied file. Theourgia's engine runs under a commercial licence;
   copying between the two contaminates one side or the other. If logic must
   exist twice, it exists twice, deliberately.

5. **Ephemeris data files ship with the AGPL service**, under the same AGPL arm.

6. **The main site backend stays non-AGPL** and never imports an astrology
   module. Its only access is the HTTP call.

## Implemented

`shruti-astro` — https://github.com/ShrutiVtuber/shruti-astro — **public**, as
AGPL §13 requires. Runs on `127.0.0.1:8201` beside the website stack. Ships the
§13 source offer in a response header and via `GET /version`, which reports the
build SHA so consuming pages link the tree actually running.

## The obligation is an asset, not a cost

Worth stating plainly, because it reframes the whole decision: publishing this
source is the **distribution channel**, not a tax on it.

The research measured the audience response precisely. Show HN submissions
matching "astrology" max out at 5 points across all 61 of them. Occult-adjacent
*engineering* is a different story entirely — the Ritman Library digitisation hit
504 points, DeployTarot 206, a spellbook-syntax esolang 176. **The rule is: ship
the history and the engineering, never the belief.** A public AGPL repo doing
correct calendrical astronomy — unequal planetary hours, the irregular karaṇa
cycle, polar-latitude refusals — is the version that lands with developers.

And the tool pages are where short-form clips should land. Never send a Short to
a homepage; send it to a thing the viewer can immediately use.

## Consequences

- The compose stack gains one service and one internal hostname.
- Tool pages take a network hop. These are second-scale computations against a
  cached ephemeris, so this is not a performance concern.
- Publishing that service's source is an *obligation*, not a nicety. It should
  be public from the first commit, not retro-fitted at launch.
- If Sophia ever wants the public tools under a permissive licence, the engine
  must be swapped, not relicensed — see "Alternative considered".

## Alternative considered — a permissive engine

`skyfield` (MIT) over JPL DE440 gives planetary positions with no copyleft
obligation at all, and is at least as accurate for the outer planets. What it
does not ship, and what would have to be written: house systems, ayanāṁśas,
dignities, lots, and the astrological convenience layer.

That work is real but bounded, and it would remove this entire class of problem
permanently — no AGPL obligations, no source-offer requirement, no boundary
judgment, and no future need for a commercial licence for anything public.

**Not chosen for now.** Revisit if the AGPL source-offer becomes awkward, or if
a public tool ever needs to be embedded somewhere that copyleft is unwelcome.

## Uncertainty worth naming

The "separate programs communicating at arm's length" boundary is the standard
reading and is widely relied upon, but it is a legal judgment, not a settled
certainty. Astrodienst are the licensor, they sell the commercial licence, and
they answer email. **One message to them converts this from a reasoned position
into a documented one** — worth sending before the tools go public.
