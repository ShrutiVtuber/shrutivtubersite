# Are we ready to launch?

Written 10 September 2026, in answer to her asking directly. Honest rather than
reassuring: the things that are settled are named as settled, and the things
that are not are named as not.

**Short answer: the licence position is sound, the compliance position is
strong, and it is not feature complete until three things she is doing and one
design pass are finished.**

---

## 1. The ephemeris licence — settled

Swiss Ephemeris is dual-licensed: AGPL, or a paid professional edition. We take
the AGPL option, which requires **the whole project** to be AGPL with source
available. That is true in all three places it runs:

| | repo | public | licence |
|---|---|---|---|
| The app | `ShrutiVtuber/astrolabe` | yes | AGPL-3.0 |
| The site | `ShrutiVtuber/shrutivtubersite` | yes | AGPL-3.0 |
| The astronomy daemon | `ShrutiVtuber/shruti-astro` | yes | AGPL-3.0 |

The daemon is the one that matters most and is easiest to forget — it is what
actually links Swiss Ephemeris server-side, and an AGPL obligation follows the
network use, not just the download.

Also now done:

- ⚠ **The notice is preserved in the app.** Settings → Licences carries the
  Swiss Ephemeris copyright notice verbatim, states which of the two licences
  was chosen, and offers the source. A compiled APK is a "copy", so the
  repository alone was not enough.
- ⚠ **Astrodienst and the authors are named ONLY in that notice.** Their licence
  says the copyright notice is the only place their names may legally appear,
  and forbids using them to promote anything. So: **no "powered by" line in a
  store listing, on stream, or on the site.** Naming the *software* is fine —
  the site's provenance block says "Swiss Ephemeris 2.10.03" and that is
  correct. A test enforces the rest.

## 2. Compliance — strong, with two things to decide

Done, and better than most sites of this size:

- **Three separate consents**, versioned, with the exact wording stored
  alongside each record — so a record says what that person actually read.
  Only the contract consent may be required.
- **Special-category data handled as such.** Birth data used for a reading
  arguably reveals philosophical belief; it gets explicit consent, is refusable
  without losing the account, and withdrawing it deletes the nativity.
- **Export and deletion** both exist and work.
- **Cookies**: a sign-in session and a CSRF token, nothing else. No third
  parties, no advertising, first-party page counting that can be turned off.
- **A ban follows a deletion by hash**, so the deletion is not quietly undone
  by keeping a list of the addresses just deleted.

Two decisions that are hers, not mine:

1. ⚠ **Age.** There is no age gate anywhere. Whether one is needed depends on
   her audience and where they are; the app stores will ask her to declare an
   age rating regardless.
2. ⚠ **Terms for the practice room.** People now post writing that others read.
   The guidelines page exists; whether the terms need a line about user content,
   moderation and takedown is worth ten minutes with someone who knows.

## 3. Feature complete — not yet, and the gaps are named

Everything she has asked for across this work is built, tested and deployed.
What stands between here and launch:

### Hers (see `SETUP-THREE-THINGS.md`)

1. **Firebase** — until then notifications are built and silent.
2. **MESSAGE_CONTENT** — until then the Discord bridge only goes outward.
3. **Her own chart**, so `/compatible-with/shruti` has something behind it.

### The design pass — done (see `design/astrolabe/`)

The system came back on 10 September and is implemented: the gilt layer, the
ruling hour, the four motifs, the whole component set, every screen rebuilt to
the kit, and the motion. The launcher icon is no longer Flutter's.

⚠ **What is left of it is the artwork, and only she can make that.**
`design/astrolabe/guidelines/artwork-spec.md` lists twelve pieces in priority
order with exact canvases and safe areas; six are essential. Every placement
has a designed art-absent state and the app ships looking finished without
them — but the Home portrait is called the highest-leverage drawing in the
project, and the launcher icon is a geometric stand-in until she draws the
clasp.

### Still open, and honest about it

- **iOS does not exist.** Android only. iOS needs an Apple developer account,
  APNs, and a pass over anything that assumes Android.
- **The site is behind the holding page.** That is a switch, not work.
- **Nobody but her has used any of it.** No practice reading has been written
  by a stranger, no offer redeemed, no notification received by somebody who
  did not build it. The tests say the parts work; they cannot say the thing is
  good.

## What I would do first

1. The three setup tasks — they unlock features that are already paid for.
2. Put it in front of ten people from the Discord before a public launch. Not
   for bugs — for the things a test cannot see. ⚠ This is now the long pole:
   the design pass is done and nobody outside has touched any of it.
3. The artwork, at her own pace. Six essential pieces, and the app looks
   finished while it waits for them.
