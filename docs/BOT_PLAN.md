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

## What the research changed — 26 August 2026

Four findings, in order of how much they cost us. Full report in the
conversation; the load-bearing ones are recorded here because two of them
invalidate decisions written above.

### 1. Discord already does member sync. Natively. Free. Since 2015.

A YouTube Partner with memberships enabled, or a Twitch Affiliate/Partner,
connects their channel in **Server Settings → Integrations** and Discord
auto-creates a member role plus one role per tier, syncs in near real time with
a weekly reconciliation pass, and offers a configurable grace period and
kick-on-expiry.

**The feature we planned to charge for is a free first-party feature**, serving
exactly the same population — there is no segment we could sync for that
Discord cannot. "Membership sync" cannot be the paid hook. The decision above
that sync is the gate is therefore **void and needs replacing**.

What is *not* commoditised: the nine instruments, the collab planner, the
comparison loop, and VTuber-tuned everything-else. **There is no
VTuber-specific bot on the market at all** — which is either a real gap or a
market too small to have attracted anyone, and this research cannot tell which.

### 2. The YouTube members API is closed to us anyway

Both endpoint pages now read: *"Reach out to your Google or YouTube
representative to request access."* The self-serve application form was
withdrawn — the 2022 archived page linked one, and that URL now returns 401.
There is **no public record of any independent developer being granted access**,
and five years of Stack Overflow questions from developers holding the correct
scope and receiving 403s sit unanswered.

One worry turned out to be unfounded: **no security assessment applies.** The
scope is *sensitive*, not *restricted*, so the multi-thousand-pound annual CASA
audit is not in play. Moot, given the above, but worth not fearing.

### 3. Discord's cut is 15%, not 10% — and price parity is mandatory

From the Developer Policy, in force since **7 October 2024**: any developer
offering paid features that Discord's Premium Apps products support **must**
also sell them through Discord, at a price no higher than anywhere else.
External Stripe billing is not banned; it can no longer be the only channel.

The fee is **15% to the first $1M cumulative, then 30%**, plus about 6%
processing. Do not confuse it with the 10% Server Subscriptions fee — that is
the creator selling their own server, is US-only, and is a different product.

**And it breaks decision 7 above.** Discord's own docs: *"You can offer either
user subscription SKUs or guild subscription SKUs, but not both
simultaneously."* Billing a person *or* a server is not available on Discord's
rail — one or the other. Monthly only, too: no annual option, while every
competitor discounts annually.

### 4. A role-sync bot needs no privileged intents — build REST-first

This one is free money. Gateway intents govern *events*; REST calls are
governed by *permissions*.

- `GET /guilds/{id}/members` (**List**) requires the Guild Members intent
- `GET /guilds/{id}/members/{user.id}` (**Get**) requires none
- `PUT/DELETE .../roles/{role.id}` needs only `MANAGE_ROLES`
- Interaction payloads already carry the member object, no intent required

So: user links their account → backend assigns the role by REST → the bot needs
`MANAGE_ROLES` and a role positioned above the target, and **nothing
privileged**. Since Discord rejects intent requests where *"an alternative
approach would work"*, asking for Guild Members would be both unnecessary and a
likely rejection. Review triggers at **10,000 users** (not 100 servers);
verification triggers at **100 servers**.

**Turn Server Members Intent OFF.**

## What the incumbents charge

Per **server** is the norm. Verified from official pages: **Streamcord Pro
$2.99/mo** (and it bills through Discord's own Premium Apps, not Stripe).
Corroborated but not primary-verified: **MEE6 ~$11.99/mo**, **Dyno
$4.17–8.33/mo**, **Carl-bot $7.99/mo** for one server.

Sync, meanwhile, is free everywhere — Discord native, Patreon (10% of income,
integration included), Ko-fi (0–5%, and **no longer requires Gold**).

---

## Reopened by the research

1. **What is the paid tier, if not sync?** The instruments and the collab and
   comparison commands are the only things nobody else has.
2. **Person or server billing — pick one.** Discord permits only one kind of
   SKU, and parity pricing means we cannot simply route around it.
3. **Is this still worth building?** Honestly asked. The differentiators are
   real and unique; the commodity half is free. That may still be a product,
   but it is a different one from the plan above.

---

## Previously open, now answered

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
