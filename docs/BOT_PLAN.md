# The Discord bot — plan and settled decisions

Agreed 26 August 2026. The readable version is the artifact; this is the copy
that lives with the code, and it exists because the decisions below are the
kind that get quietly reversed six months later by somebody who does not know
why they were made.

**The pitch, in her words:** *"VTubers have to pay a lot of different services
to get what they actually need. If our discord bot could handle it for them in
one place with one payment that would be amazing — and I would use it as well
which would be helpful to reduce my vtuber costs."*

---

## Settled, and not to be casually revisited

### 1. Multi-server from day one

Single-tenant now means a rewrite later. **Every table carries a guild id from
the first migration**, and the gateway client is written as though sharded even
while it runs one shard.

### 2. Read-only against the website

The bot never writes to shrutivtuber.com. It holds **no admin credential at
all** — a stronger guarantee than a promise, because there is nothing to
misuse.

The consequence, which has to be designed for rather than discovered: casting a
chart *stores* a chart, so the bot does not ask the website to do it. It calls
**`shruti-astro` directly**, computes, and answers with nothing persisted.
Anything that genuinely needs storing hands off to the site in the person's own
browser.

That is also the right answer for a second reason. **Birth data does not belong
in someone else's Discord channel.** Chart commands reply ephemerally.

### 3. Every free-tier message carries a clickable attribution footer

One line, never its own embed, never twice in a message. It does three jobs:

- **Growth.** The bot sits in servers full of the exact people who would want
  it, and every announcement is an advertisement in front of them.
- **The reason to pay.** Removing branding is a real thing a server owner
  wants, rather than a feature held hostage.
- **The disclosure.** The same line carries the automated-post marker, so
  labelling is structural rather than an afterthought — the only way that sort
  of thing survives a redesign.

Labelling was flagged by the German MStV research. Probably not her
jurisdiction — see `docs/MARKETING_2026-08-26.md` §0 — but it is cheap and the
direction of travel everywhere is toward requiring it.

### 4. Answer in chat, do not link out

Clicks matter less than being useful where people already are. A bot that only
posts links is annoying.

### 5. A generic, marketable name, on a domain that can move

It is sold to other VTubers; it is not "Shruti's bot". Its own domain
eventually, a subdomain first.

**The requirement is that moving is cheap, and that is not achieved by choosing
a good subdomain.** It is achieved by never writing the domain down:

- Every URL is configuration from the first commit. The website already learned
  this the hard way when `Astro.url` reported `localhost` behind Caddy.
- **The thing that actually makes a domain move painful is OAuth redirect
  URIs.** Discord, Twitch and Google each hold a registered list in *their*
  developer consoles, and each has to be updated by hand.
- So: **register both the temporary and the eventual domain as valid redirects
  as soon as the eventual one is bought**, even if nothing points at it. That
  turns the move into a config change rather than a flag day.

### 6. Free is more generous than the incumbents; sync is the gate

All nine instruments, live announcements, the collab and comparison commands,
scheduling and roles are free. The gate is **membership sync** — the thing with
real per-server operating cost and real support burden — plus branding removal.

This has a happy property: the free tier is what carries the attribution footer
into other people's servers, so being generous with it *is* the marketing
spend.

### 7. A subscription is owned by a billing account, not by a guild

Either a person or a server can be the payer, so **guilds are linked to a
billing account through a join table** rather than a subscription hanging off
the guild row.

- One person can pay for several servers — agencies and collectives will want
  this immediately.
- A server keeps its subscription when the person who added the bot leaves,
  which is the single most common way this goes wrong.
- Ownership transfers without cancelling and re-subscribing.

Modelling it the other way round is a migration later, which is the class of
decision the multi-server rule exists to avoid.

---

## Shape

| Piece | State |
|---|---|
| `shruti-bot` — gateway client, commands, jobs | new |
| Its own database — guild config, entitlements, OAuth tokens | new, deliberately separate from the site's |
| A dashboard for server owners | new |
| `shruti-astro` — computes every instrument, speaks HTTP | exists |
| The site's public API — live, schedule, journal, horoscopes | exists, public endpoints only |
| Stripe — subscriptions, portal, webhooks | exists |

## Phases

1. **A bot in her server that other servers can add.** Instruments, live
   announcements to *the server's own channel*, per-guild config, attribution
   footer. No money, no OAuth, no sync. Run it daily and find what is missing.
2. **Dashboard and the free/paid split.** Config moves out of chat. Stripe,
   entitlements checked in one place, graceful downgrade that says so rather
   than going quiet.
3. **Twitch member sync.** Two OAuth flows — the streamer once, each viewer
   once. Tokens encrypted at rest. A reconcile job, because webhooks get missed
   and a role that never expires is a paid perk given away.
4. **YouTube sync, and the collab commands.** Gated on Google access.

---

## Open, being researched

Both gate the pricing page:

1. **Is YouTube membership sync available to a solo developer at all?** The
   scope, whether it is restricted, whether there is an application beyond
   ordinary OAuth verification, and whether a paid third-party security
   assessment applies. That last one alone could decide the feature.
2. **What the incumbents actually charge.** "More generous than them" is not a
   plan until there is a them.

Also being checked: **whether Discord permits external billing at all**, or
requires its own App Subscriptions and takes a cut. That is not a detail — it
changes the business model.

---

## Known hard parts

- **Discord verification** past a threshold of servers: a review, a privacy
  policy and terms. Both already exist, which is unusually lucky.
- **It is an operational commitment**, not a project with an end.
- **Storing other people's OAuth tokens** raises the stakes of a breach a lot.
  Separate database, encrypted at rest, documented revocation.
- **Support is the hidden cost.** Most of it will be somebody's permissions.
