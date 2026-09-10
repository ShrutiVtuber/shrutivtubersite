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

11. **One reading, three places.** A person writing horoscopes should be able
    to keep what they write and share it, whether they started on the website,
    in the app, or in Discord — and a series should be as natural as a single
    reading.

    - **Website**: drafts are kept to their account rather than to the browser.
    - **App**: submit for others to read, comment on and vote.
    - **Discord**: a slash command that hands back the material to write from —
      the sky for a period rotated to a sign, and the events inside it. The
      same thing the desk shows, in a message.

    A **series** is a first-class thing, not twelve loose readings: somebody
    writing all twelve signs for a week is doing one piece of work, and it
    should be submitted, read and voted on as one.

    ⚠ The slash command is the cheap half — her bot already answers signed
    interactions and already talks to the ephemeris. The expensive half is the
    same gateway the bridge needs, so build the command first and let it stand
    alone until the socket exists.

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

## The bridge, as built

**Outbound works now.** A submission tells the bot over `POST /internal/practice`
(shared secret, refuses without one), and the bot posts it to the channel. No
gateway, no intent, nothing to switch on.

**Inbound is written and dormant.** `bot/vcordbot/gateway.py` holds the socket,
identifies, heartbeats, resumes from the last sequence, refuses its own messages
and de-duplicates redelivery. It is not started yet, because:

⚠ **MESSAGE_CONTENT is a privileged intent and only she can switch it on** —
Discord developer portal → the application → Bot → Privileged Gateway Intents.
Until then Discord sends every message with EMPTY content: no error, no warning,
a channel that simply looks quiet. The reader counts blanks and says so in the
log rather than sitting silent, which is the one thing that makes this
diagnosable.

Also needed from her, in `.env`:

```
SHRUTI_DISCORD_PRACTICE_CHANNEL=<the #horoscope-practise channel id>
SHRUTI_INTERNAL_SECRET=<any long random string, same value both services>
VCORDBOT_INTERNAL_URL=http://bot:8000
```

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

## Notifications: what is built, and the two things only she can do

Built and tested:

- `app_device` — one row per phone, five switches, pruned when a token dies.
- `core/notify.tell(kind, …)` — the ONE place that decides who hears about
  what. Every trigger calls it; nothing else reads a preference flag.
- `core/fcm.py` — FCM HTTP v1, service-account JWT, cached access token.
- Triggers: readings published, somebody replied to your practice reading, and
  she went live (the bot calls the site at the transition, once per sweep
  however many servers are watching).
- The app's switches, where they are kept, and taking the phone off the list.

⚠ **Unconfigured is a working state.** With no service account nothing is sent
and nothing raises — publishing a horoscope must not 500 because a Google
credential is missing.

### 1. Firebase (her, ~15 minutes)

1. Make a Firebase project; add an Android app with the id
   `com.shrutivtuber.astrolabe` (renamed from `shruti_tools`).
2. Download `google-services.json` into `shruti-tools/android/app/`.
3. Add `firebase_core` and `firebase_messaging` to the app's pubspec.
4. Fill in `_registrationToken()` in `lib/services/notifications.dart` — the
   five lines are written out in the comment above it.
5. On the site, set `SHRUTI_FCM_SERVICE_ACCOUNT` to the service account JSON
   (the whole thing, or a path to it).

⚠ The app is deliberately not built against Firebase yet. Adding the plugin
against a project that does not exist does not compile, and would leave the app
un-buildable until step 1 is done.

### 2. iOS, when there is an iOS build

APNs needs an Apple developer account and a key uploaded to the same Firebase
project. The backend already sends the `apns` block; nothing changes there.

### 3. The Discord bridge's inbound half

See above — MESSAGE_CONTENT in the developer portal, plus three environment
variables.

## Reading her horoscopes in the app — asked for 10 September 2026

Her words: readers "need to be able to read all my horoscopes for the current
cycle in the app itself — if they want to see an archive one (for a previous
month or week) then they can be redirected to the website."

**The line is the CURRENT period, not the sign.** Everything for the sky the app
is already showing — all twelve signs of this week, this month, today — is read
in the app. Anything dated earlier opens the website.

⚠ This is the same rule as the five tools that stayed off the app, and for the
same reason: the app carries what somebody wants *now*, and the site is where
the archive, the search and the back-catalogue live. It is a decision about
where traffic goes, not a technical limit — the endpoint would serve any period
just as happily, which is exactly why the boundary has to be deliberate and
written down.

What it needs:
- a screen listing the twelve signs for the current period, reading from the
  same `/api/horoscopes/…` the site uses
- the period picker limited to what `currentCovers()` says is now
- an "earlier readings" link that opens the site, saying so plainly — a link
  that silently leaves the app is worse than one that says where it goes
