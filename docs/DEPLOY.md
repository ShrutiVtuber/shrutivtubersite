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

Deployed and serving. **Backend only — there is no frontend yet.**

`site` and `admin` sit behind the `web` compose profile, so a plain `up` brings
postgres, backend and caddy. Non-API paths return a plain-text placeholder that
says the site is unbuilt, rather than a 502 that reads as broken.

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

## Bringing the frontend up, when it exists

```bash
dc --profile web up -d --build
```

Then set `SHRUTI_WEB_ENABLED=1` in `.env` so the internal Caddy proxies to the
site instead of serving the placeholder.

## Two things deliberately not done

**Admin login is off.** `SHRUTI_ADMIN_EMAIL` and `SHRUTI_ADMIN_PASSWORD_HASH`
are empty, so `/api/admin/login` returns 401 for every attempt. Turn it on with
a password only you have chosen:

```bash
dc run --rm backend python -c \
  "from argon2 import PasswordHasher; import getpass; \
   print(PasswordHasher().hash(getpass.getpass('password: ')))"
# then put the email and the hash into .env and: dc up -d backend
```

Set it by hand rather than letting anything generate it — the admin password is
the only thing between the internet and the ability to rewrite the site.

**Twitch credentials are unset**, so `/api/live` reports offline. That is the
correct failure: it fails closed rather than claiming a stream that is not
running. Add `SHRUTI_TWITCH_CLIENT_ID` and `SHRUTI_TWITCH_CLIENT_SECRET` from
dev.twitch.tv when you want the live badge to be real.

## Cutover, when the site is ready

1. Bring up the `web` profile and check the origin with `--resolve`.
2. In Cloudflare, point `A` at the server and leave it proxied.
3. Watch, then cancel Nexcess. Keep the final WordPress export offline for a year.

Redirects to add at cutover: `/blog` → `/journal`, `/events/` → `/schedule`,
`/french-notes-*` → `/journal`, `/sample-page` → 410.
