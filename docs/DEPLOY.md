# Deploying shrutivtuber.com

## Where it runs

One netcup box, `159.195.251.161` (RS 8000 G12 · 16 cores · 64 GB · Debian 13),
in **Austria** — netcup's Vienna site, per the registry (`AT-NETCUP-KVM`).
It hosts the whole estate; this stack is on loopback **8200** (bot 8250), and
`/srv/PORTS.md` on the box is the authority on which ports are taken.

**The Hetzner box is gone.** Everything moved on 3 September 2026, the old
servers were deleted, and `178.105.106.225` has since been reassigned to a
stranger — SSH will refuse it on a changed host key, which is the only reason
anybody noticed this page was still pointing there. `SERVER-ACCESS.md` in the
repo root is the current record; if it and this page ever disagree, it wins.

```bash
ssh -i ~/.ssh/agents_netcup deploy@159.195.251.161
cd /srv/shrutivtuber/prod
```

The compose pair is always both files:

```bash
alias dc='docker compose -f docker-compose.yml -f docker-compose.prod.yml'
```

## Current state

**Backend deployed and serving. The frontend now exists but is not yet up
there.** `site` sits behind the `web` compose profile, so a plain `up` brings
only postgres, backend and caddy, and non-API paths get a plain-text placeholder
saying the site is unbuilt — a better thing for a stranger to meet than a 502
that reads as broken.

DNS still points at Nexcess, so the public `shrutivtuber.com` is the old
WordPress site. The new stack is reachable at the origin:

```bash
curl --resolve shrutivtuber.com:443:159.195.251.161 https://shrutivtuber.com/api/health
```

TLS already works there — the certificate was issued by DNS-01 before anything
was deployed, so cutover is a DNS change with no TLS scramble.

## Deploy an update

```bash
cd /srv/shrutivtuber/prod
git pull --ff-only
export SHRUTI_SOURCE_SHA=$(git rev-parse HEAD)
dc --profile web --profile bot up -d --build
dc exec -T backend alembic upgrade head
```

`SHRUTI_SOURCE_SHA` is the licence, not a nicety. Every file here is AGPL-3.0,
and section 13 says software people interact with over a network must offer
them the source **of the build that answered them**. Export it and the footer
link names that commit; forget it and the link points at the repository, which
stays true as long as deploys come from `main` — so this degrades honestly
rather than lying.

**Both profiles, every time.** `site` sits behind `web` and `vcordbot` behind
`bot`, so a plain `dc up -d --build` rebuilds postgres, backend and caddy and
silently leaves the other two running whatever they were built from. Nothing
looks wrong afterwards: the containers are up, healthy, and answering — with
old code. Naming both here costs nothing when they are already running, because
a profile that is up is simply rebuilt.

The bot's commands are a separate step and are NOT part of a deploy. Discord
holds its own copy of the command list, so a changed `commands.py` reaches
nobody until:

```bash
python3 bot/scripts/register-commands.py
```

which registers globally and clears any guild-scoped list that would otherwise
shadow it. Only needed when commands are added, removed, or their options or
descriptions change — not for a change to what a command *does*.

## Bringing the frontend up

```bash
dc --profile web up -d --build
dc exec -T backend alembic upgrade head
```

Then set `SHRUTI_WEB_ENABLED=1` in `.env` and `dc up -d caddy-internal`, so the
internal Caddy proxies to the site instead of serving the placeholder.

Check at the origin before anyone else can see it:

```bash
curl -s --resolve shrutivtuber.com:443:159.195.251.161 https://shrutivtuber.com/ -o /dev/null -w '%{http_code}\n'
```

---

# Go-live

## 1. Claim the admin

The operator's email and password live in the database, not in `.env`, and are
set **once, from the browser**. An unclaimed site shows a setup screen rather
than a sign-in form; claiming it needs a token the backend writes to its own
log. Reading that log means having the server, which is exactly the fact being
proven — otherwise an unclaimed admin on a public site is a takeover waiting for
whoever loads the page first.

```bash
dc logs backend | grep "setup token"
```

Go to `https://shrutivtuber.com/admin/signin` (through the origin, before
cutover), paste the token, choose an email and a password of twelve characters
or more. The token is spent on success and the route closes for good.

**Do this before DNS moves.** A site that is publicly reachable and unclaimed is
the one genuinely dangerous window in this whole process.

Then add a passkey from **Settings → Passkeys**, so the phone can sign in with
Face ID instead of a password typed on a phone keyboard.

## 2. Environment that must be set before launch

| Key | Why it matters on day one |
|---|---|
| `SHRUTI_SECRET_KEY` | Signs sessions and CSRF tokens. Must be long and random, and changing it signs everyone out. |
| `SHRUTI_ENV=prod` | Turns on `Secure` cookies and turns off the localhost passkey allowance. |
| `SHRUTI_SITE_URL=https://shrutivtuber.com` | The canonical URL, the link base in emails, **and the domain passkeys are scoped to.** |
| `SHRUTI_RESEND_API_KEY` / `SHRUTI_RESEND_FROM` | Without these, no sign-in link, no newsletter confirmation and no password reset can be sent — every account flow dead-ends silently. |
| `SHRUTI_WEB_ENABLED=1` | Otherwise the placeholder is what the world sees. |

Optional, and honest when absent: Twitch and YouTube keys (the live badge fails
closed and reports offline rather than claiming a stream that is not running),
and the R2 keys (uploads fall back to disk).

## 3. Cutover

1. Bring up the `web` profile, check the origin with `--resolve`, and walk the
   site there: sign up, sign in, add a passkey, save a nativity, post a journal
   entry from the admin, and send yourself the newsletter confirmation.
2. In Cloudflare, point the `A` record at `159.195.251.161` and leave it
   proxied.
3. Watch, then cancel Nexcess. **Keep the final WordPress export offline for a
   year** — a year is long enough to discover what was on a page nobody
   remembers.

Redirects to add at cutover: `/blog` → `/journal`, `/events/` → `/schedule`,
`/french-notes-*` → `/journal`, `/sample-page` → 410.

## 4. What is deliberately not automated

**The password.** Set by hand, in a browser, by the person it belongs to. Not
generated, not written to a file, not passed through anything that logs.

**The DNS change.** One command flips the public site, and nothing here should
be able to do it on its own.

**The Nexcess cancellation.** After DNS has been watched, not before.

## Migrations

`alembic upgrade head` applies whatever is outstanding. To see the order before
running it, or to work out where a part-way failure stopped:

```bash
dc exec -T backend alembic current      # where this database is
dc exec -T backend alembic history      # every revision, newest first
```

There used to be a table of them here. It listed six of the forty-eight that
exist and had been wrong for weeks — a hand-kept copy of something Alembic
already knows is a second source that goes stale silently, which is the exact
failure it was written to prevent.

## Stripe went live — 2026-08-26

Live keys installed on production; both membership tiers rebuilt in live mode
by `backend/scripts/stripe-golive.py --confirm`.

Verified at the time: `charges_enabled` and `payouts_enabled` both true, account
in GR with EUR default, nothing outstanding in Stripe's requirements, and a real
`cs_live_…` checkout session created for €5.00 and then expired.

**Test and live are separate worlds.** Anything created against a test key —
products, prices, coupons, webhook endpoints — does not exist in live mode. The
tiers' stored ids were rebuilt; **discount codes were not**, and any that are
wanted live must be made again in the admin.

`shop.sync` treats an id that this Stripe mode does not recognise as "create a
new one" rather than letting `Product.modify` raise. Without that, the first
save after a key swap is a 500 on a perfectly good row.

The test-mode banner on /support is driven by the API's `testMode` flag, so it
took itself down when the keys changed. No deploy was needed for it.

### Still to do by hand

- **Rotate the live secret key and the webhook signing secret.** Both were sent
  through a chat transcript. Stripe → Developers → API keys → roll; and
  Developers → Webhooks → the endpoint → roll signing secret. Then the new
  values go into `.env` the same way and the backend restarts. Rotating the
  secret key does NOT disturb the prices or products already created.
- The publishable key needs no rotation — it ships in the page source by design.
