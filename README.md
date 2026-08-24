# shrutivtuber.com

Rebuild of shrutivtuber.com off Nexcess-managed WordPress onto Astro + FastAPI,
deployed beside Theourgia on the same Hetzner box but sharing nothing with it.

Full plan: <https://claude.ai/code/artifact/415a0a11-5ddf-4bad-94c4-a4974f966a8c>

## Shape

```
Cloudflare (DNS + proxy)
  ├── /journal/*  →  BeeRanked (edge, R2)      content + auto-translation EL/HI/FR
  └── everything else  →  Hetzner VPS
                            host Caddy :443  →  127.0.0.1:8200
                              └── internal Caddy
                                    ├── /            → Astro (SSR, node)
                                    ├── /admin       → admin SPA (React)
                                    ├── /api/*       → FastAPI (uvicorn)
                                    └── /media/*     → uploaded art
                                          └── Postgres 17 (dedicated)
```

## Decisions, and why

**Postgres, dedicated.** Its own instance, its own volume, its own backup
lifecycle. Explicitly *not* Theourgia's postgres: `deploy-prod.sh` dumps the main
DB on every deploy, and a Theourgia restore drill must never touch this site.
Same box, separate blast radius.

**Port 8200.** Theourgia holds 8190 (apex) and 8193 (plugin registry). Dev
postgres binds 5433, never 5432.

**Resource limits on everything.** `docker-compose.prod.yml` sets `mem_limit`,
`cpus` and log rotation per service (~1.4 GB total). The 2026-08-18 Theourgia
prelaunch audit flagged their absence across the box; adding a second public
property is when that stops being theoretical.

**Content lives in Postgres, not in the repo.** Every display record carries
`visible` and `position`; every art reference is a *nullable* FK to `media`. The
site renders correctly with no art at all — pages ship hidden, and you unhide
them as art arrives. Astro fetches server-side per render, so an admin edit is
live immediately with no rebuild and no deploy.

**Live status fails closed.** `core/live.py` caches the Twitch app token and the
stream result, and reports offline on any error. A site that falsely claims you
are live sends people to an empty channel — worse than saying nothing. The
client secret never leaves the backend; that is the main reason it exists.

## Layout

| Path | What |
|---|---|
| `backend/` | FastAPI, SQLModel, alembic |
| `frontend/site/` | Astro 6, SSR via node adapter |
| `frontend/admin/` | React 19 + Vite admin SPA |
| `frontend/shared/` | design tokens shared by both |
| `deploy/` | Caddy drop-in for `/etc/caddy/Caddyfile.d/` |
| `assets/rescued/` | salvaged from the old WordPress site |

## Production host

`agent-house` — Debian 13, 4 vCPU / 15 GB RAM, 150 GB disk. Already runs
theourgia (8190), astropractise (8210) and daskalos (8090); this stack takes
**8200**. Host Caddy terminates TLS and imports per-tenant drop-ins from
`/etc/caddy/Caddyfile.d/`.

```bash
ssh -i ~/.ssh/agent-house-access-theourgia theourgia@178.105.106.225
```

Deploy root: `/srv/shrutivtuber/prod`.

## Local

```bash
cp .env.example .env          # fill secrets
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Site on <http://localhost:8200>, API docs on <http://localhost:8200/api/docs>.

## Deploy

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Install the Caddy drop-in on the host:

```bash
sudo install -m 644 deploy/shrutivtuber.caddy /etc/caddy/Caddyfile.d/
sudo caddy-reload
```

## Status

- [x] DNS moved to Cloudflare (NS live; A still on Nexcess, site up, ProtonMail intact)
- [x] Assets rescued from WordPress
- [x] Compose + Caddy + Postgres wiring
- [x] Content model, live status, public routes
- [ ] Alembic baseline migration
- [ ] Admin auth + CRUD
- [ ] Astro site + design system
- [ ] BeeRanked mount at `/journal`
- [ ] Cutover, then cancel Nexcess
