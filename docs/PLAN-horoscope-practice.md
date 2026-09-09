# Horoscope practice, the app, and the Discord bridge

Written down because this arrived as eight requirements across six messages and
losing one of them is the likely failure.

## What she asked for

1. **Isopsephy and the sigil generator in the app.** Isopsephy uses theourgia's
   **pack** method — reuse the packs, serve them from shrutivtuber.com, and let
   people choose which languages they want, so the app is not a huge download.
2. **The horoscope writing tools as a public tool on the website** — usable by
   anyone, but they cannot publish to her site.
3. **The same tools in the app**, where people can submit a reading, and others
   can read it, comment and vote. She reads the highest-voted ones on stream.
4. **Weekly horoscopes on the website everywhere**, not only monthly. Monthly
   stays the newsletter's; weekly is what she reads on stream and makes a video
   of.
5. **A Discord bridge** to a `#horoscope-practise` channel, so app-only and
   Discord-only people can talk to each other without either knowing the other
   exists.
6. **A site account is required to post**, and it must be possible to **sign up
   from inside the app**, not by being sent to the website.
7. **One account, both places.**

8. **The horoscope tool goes on the tools page** and everywhere else the
   tools are mentioned — including a card in the admin so its wording is
   editable like every other instrument.
9. **Supporters can give a name to be read on stream.** Asked at the point of
   donating or taking a membership, optional, and a custom name is allowed.
   ⚠ **Monthly supporters only — one-offs are not read on stream.**

10. **A standing compatibility test.** Two things, and the second is the
    business one:

    - **"Are you compatible with Shruti?"** — a fixed one anybody can take for
      fun, against her own chart. No account, no setup; it is a share hook.
    - **Other VTubers can set one up against their chart**, for a limited run:

      | | how long it stays up |
      |---|---|
      | not a member | 5 days |
      | lower tier | 10 days |
      | higher tier | permanent |

    Which makes it a **membership feature with an expiry**, not a page. It
    needs: a chart stored per host, a public URL per host, an expiry the tier
    sets, something that stops serving an expired one, and a path from
    "expired" back to the tier that would keep it. The expiry is the part that
    will be got wrong quietly — an expired test that keeps answering is a
    feature given away, and one that 404s with no explanation is a VTuber who
    thinks the site is broken.

    **Later, and deliberately after the practice work.** It touches billing
    tiers, which nothing else here does.

## Decisions she made

- **The bridge is a gateway.** Truly seamless: someone types normally in
  Discord and it reaches the app. Costs a new always-connected process and the
  MESSAGE_CONTENT intent, which for one server is a toggle rather than an
  approval.
- **An account to post.** Identity, banning and traceability, at the price of
  fewer submissions.

## What already exists, and does not need building

- `PERIODS = ("daily", "weekly", "monthly", "yearly")` — the backend has
  handled weekly since the horoscope tools were built. Only the site's
  **archive** and **index** pages hardcode `monthly`, and the writing desk
  already defaults to weekly.
- `/api/accounts/{signup,signin,me}` are JSON already. They set a signed
  session in an httpOnly cookie; the app needs the same token returned in the
  body so it can send it as a bearer. One account, both places, small change.
- The packs exist and are already the right shape:

  | | size | what it is |
  |---|---|---|
  | `numbers-greek`, `-hebrew`, `-arabic`, `-coptic`, `-sanskrit` | 4–9 KB each | the letter values |
  | `words-greek-diorisis` | 4.3 MB | the corpus matches are found in |
  | `words-arabic-ayaspell` | 2.0 MB | |
  | `words-hebrew-wlc`, `-wikidata` | ~260 KB | |
  | `words-sepher-sephiroth` | 45 KB | |

  The letter values are small enough to bundle. **The corpora are the weight**
  and are what "choose your languages" is really about.

## ⚠ The bot has no gateway today

`bot/vcordbot` is HTTP interactions only — signed slash commands at
`/interactions`, no socket, no privileged intent. Its own comment says the
choice is "cheap to reverse", and reversing it is what the bridge needs:

- **app → Discord** is easy either way; the backend posts a webhook.
- **Discord → app** needs to READ the channel, which needs the gateway and the
  message-content intent.

A gateway consumer is a **new long-running process** that must reconnect and
resume. That is the real cost, not the permission.

## Order

1. Weekly everywhere on the site — small, and it unblocks her stream plan.
2. Isopsephy and the sigil generator in the app, with packs served from the
   site and chosen by the reader.
3. Accounts in the app: bearer token, sign-up in-app.
4. Practice readings — model, API, submitting, reading, voting, commenting.
5. The Discord bridge, webhook out first, gateway in second.

Moderation is not optional at step 4: an account makes abuse traceable, it does
not make it impossible, and this content reaches her Discord.
