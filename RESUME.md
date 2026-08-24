# Resume here

Written 2026-08-24 for a fresh session. Read this first.

## What this is

Rebuilding **shrutivtuber.com** off Nexcess-managed WordPress onto Astro +
FastAPI, deployed beside theourgia on the same Hetzner box. Sophia is a VTuber
whose niche is **building software for magickal and astrological practice**.

Two repos, both on the **ShrutiVtuber** GitHub account (not SAntonopoulou —
that separation is deliberate, see below):

| | |
|---|---|
| `ShrutiVtuber/shrutivtubersite` | private — the site: FastAPI backend, content model, admin |
| `ShrutiVtuber/shruti-astro` | **public, AGPL** — the astrology engine, 202 tests |

Local: `~/Documents/development/shurtiwebsite` and `~/Documents/development/shruti-astro`.

## State right now

**The API is live in production.** No frontend exists.

```bash
curl --resolve shrutivtuber.com:443:178.105.106.225 https://shrutivtuber.com/api/health
```

DNS still points at Nexcess, so the public site is still the old WordPress one.
The TLS certificate is already issued and cached at the origin, so cutover will
be a DNS change with no TLS scramble. Runbook: `docs/DEPLOY.md`.

## Decisions that must not be relitigated

**The name.** Shruti (Shruti Swara) is her **real name** — the name on her OCI
card, as Sophia is the name on her Greek passport. She is part Indian and part
Greek, so the Sanskrit name and the Greek theurgy are one person, not two themes.
Her O.T.O. motto **Soror Eu. A.** is a *byline* on magickal writing — never a
handle, slug or username, because dotted mottos serialise inconsistently. A
research pass recommended dropping "Shruti"; its premise was false and the
finding is void.

**Three traditions, not one.** Hellenic theurgy under Hekate · Śākta Tantra
(Mahāvidyā initiate) · Thelema. Any design that reads as Greek-only is wrong.

**The two accounts stay apart.** The repos were created fresh on ShrutiVtuber —
*not* transferred — so there is no redirect from SAntonopoulou. Git history was
rewritten so every commit is authored `Shruti Swara <110264778+ShrutiVtuber@
users.noreply.github.com>`, with zero identity strings in any blob or message.
**Do not re-link the accounts.** Theourgia's repo URL is deliberately blank in
the seed data.

**The licence boundary.** `shruti-astro` links Swiss Ephemeris under the **AGPL
arm** and must stay public. Theourgia will use the commercial licence. But — see
the amendment in `docs/adr/0001-astrology-licensing.md` — my original claim that
*no* code may cross was **wrong and over-broad**. Theourgia is AGPL-3.0-only and
Sophia owns the copyright, so her own non-ephemeris code (ciphers, calendars)
copies across freely. Only the ephemeris linkage is constrained.

## Credentials

`~/.config/shruti/` — `github.env` (ShrutiVtuber PAT, near-total scope),
`resend.env` (verified for shrutivtuber.com), `git-credential-shruti` (helper, so
the PAT stays out of `.git/config`). Dir 0700, files 0600.

The **server** uses a read-only deploy key, not the PAT.

Server: `ssh -i ~/.ssh/agent-house-access-theourgia theourgia@178.105.106.225`,
deploy root `/srv/shrutivtuber/prod`, port **8200** (8090 daskalos, 8190
theourgia, 8210 astropractise).

## Deliberately unset

- **Admin login is off.** `SHRUTI_ADMIN_EMAIL` / `SHRUTI_ADMIN_PASSWORD_HASH` are
  empty so `/api/admin/login` 401s. Sophia should choose the password herself.
- **Twitch and YouTube credentials are unset**, so `/api/live` reports offline on
  both. That is the correct failure — it fails closed rather than claiming a
  stream that is not running.

## What exists

**shruti-astro** — planetary hours · pañcāṅga with ending times, almanac strip
and the day's windows · natal charts in both traditions with SVG figures ·
Vimśottarī · aspects (sign-based, Vedic dṛṣṭi asymmetric) · Hindu calendar day
and year views · **Sūrya Siddhānta as a real second authority** · Attic calendar
· isopsephy across six scripts · kaṭapayādi as positional · sigil generator ·
solar phase and void-of-course doctrines · festival anchor resolution · MBF pack
writer verified against all 50 of theourgia's packs.

**shrutivtubersite** — content model (everything carries `visible`+`position`,
every art reference nullable, sections default hidden), admin auth and CRUD with
media upload, contact form and question box with Resend wired, multi-platform
live status.

**Design system** — delivered by the designer, extracted at `/tmp/ds` (re-extract
from `Shruti Design System.zip` in the repo root). 41 components, 7 tool
templates, Dawn/Dusk themes. **Not implemented yet.**

## Read these next

- `docs/BACKLOG.md` — **everything agreed and not built**: station trackers, Day
  at a Glance, accounts, horoscopes, newsletter, and the GDPR analysis. Includes
  the finding that birth data in an astrological context may be Article 9
  special category data, which must be settled *before* the schema exists.
- `docs/DESIGN_HANDOFF_02_stations.md` — ready to hand to the designer.
- `docs/DEPLOY.md` — the runbook.
- `docs/adr/0001-astrology-licensing.md` — the licence boundary and its amendment.

## The festival research finished — with gaps

Output is in `~/Documents/development/shruti-research/` (outside the repo:
working material, partly unverified). **Read its `README.md` first.**

**71 Hindu entries and 45 Attic entries**, all cited, confidence graded. Three
things need doing before any of it is packed:

1. **No entry carries `dayRule`** — the schema given to the agents predated that
   discovery. Verified for 2026: Vasant Pañcamī, Holikā Dahan and Holi resolve
   exactly right on the sunrise default; **Mahā Śivarātri comes back a day late
   because it needs `nishitha`**. A pass adding the rule to the handful that
   need it is required.
2. **The assembly agent dropped the Hindu half** — its report is Attic only. The
   Hindu entries were recovered from `journal.jsonl` and are therefore
   *unverified by the audit pass* that the Attic set received.
3. **17 of 68 Hindu anchors error on resolve.** 49 resolve, 2 are legitimately
   kṣaya. The rest need triage.

The resolver, the MBF writer and the anchor validation all work — this is a data
problem, not an engine problem.

## Still pending

**The BeeRanked MCP** was installed but needs a fresh session to be usable.
shrutivtuber.com is already connected to BeeRanked; `/journal` is the intended
mount.

## The site now renders

An Astro 6 SSR scaffold is up and serving through the origin: pnpm workspace,
the **designer's own tokens copied in verbatim**, Dawn/Dusk with all three theme
states, a no-flash first-paint script, and server-side fetches to both backends
so nothing leaks to the browser and there is no CORS surface.

It is a scaffold, not the design. The homepage renders real data — live status,
projects, grouped links — in plain markup awaiting the design implementation.
`SHRUTI_WEB_ENABLED=1` switches Caddy from the placeholder to the site.

**The largest remaining piece is implementing the design system** across the
surfaces in the three handoffs.
