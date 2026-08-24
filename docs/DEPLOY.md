# Deploying shrutivtuber.com

## Where it runs

`agent-house` — Debian 13, 4 vCPU / 15 GB. Shares the box with theourgia (8190),
astropractise (8210) and daskalos (8090). This stack is **8200**.

```bash
ssh -i ~/.ssh/agent-house-access-theourgia theourgia@178.105.106.225
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
curl --resolve shrutivtuber.com:443:178.105.106.225 https://shrutivtuber.com/api/health
```

TLS already works there — the certificate was issued by DNS-01 before anything
was deployed, so cutover is a DNS change with no TLS scramble.

## Deploy an update

```bash
cd /srv/shrutivtuber/prod
git pull --ff-only
dc up -d --build
dc exec -T backend alembic upgrade head
```

## Bringing the frontend up

```bash
dc --profile web up -d --build
dc exec -T backend alembic upgrade head
```

Then set `SHRUTI_WEB_ENABLED=1` in `.env` and `dc up -d caddy-internal`, so the
internal Caddy proxies to the site instead of serving the placeholder.

Check at the origin before anyone else can see it:

```bash
curl -s --resolve shrutivtuber.com:443:178.105.106.225 https://shrutivtuber.com/ -o /dev/null -w '%{http_code}\n'
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
2. In Cloudflare, point the `A` record at `178.105.106.225` and leave it
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

## Migrations, in order

Each is applied by `alembic upgrade head`; the list is here so a failure part
way through is legible rather than mysterious.

| Revision | What it adds |
|---|---|
| `8a1c4f2b7d90` | project credits |
| `9c3e7b15a4d2` | fan art |
| `a4f81c26b9e0` | reader accounts, nativities, consents |
| `b7d2e91f4a63` | `storage_backend` on media rows |
| `c9a04e1b78f2` | stored sky for journal entries |
| `d3f16c8b52a4` | passkeys |
