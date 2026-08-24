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

## The festival calendars are DONE — audited, verified, packed

All three gaps closed, the audit applied, both corpora shipped as MBF:

- `shruti-hindu-festivals-v0.1.0.mbf` — **72 entries**, 242 dated occurrences
  in 2026, 2 undated and both correct (a container, and one entry whose lunar
  month falls outside the civil year).
- `shruti-attic-festivals-v0.2.0.mbf` — **45 entries**.

Both CC-BY-SA-4.0, both verify, both rebuild byte-identically from
`scripts/pack_festivals.py`, which refuses to pack a corpus not marked
verified. Interop with theourgia is verified in both directions;
`practiseapp/NOTE_FROM_SHRUTI_2026-08-24_*.md` has the reader's notes.

### What the audit actually turned up

Three of its source corrections **had never been applied** — they were written
into the corpus as instruction text and splatted character by character, so 269
of 525 "sources" were single letters and three entries had no sources at all
while appearing to have hundreds. Executed properly now.

The audit itself read 42 entries with **19,005 characters of nirṇaya reasoning
missing**, because the export handed to it was truncated at 900 characters.
That was our bug, not the corpus's. Treat its findings as indicative, not
final — at least one (a `pan-indian` contradiction on `dhanteras`) does not
survive contact with the full note.

### Bugs the gaps hid

RESUME used to record "4 legitimately kṣaya" failures. **They were not
legitimate.** A kṣaya opening tithi was deleting festivals outright: 37
occurrences across 19 entries between 2026 and 2040, with Śāradīya Navarātri
simply absent from 2027. A kṣaya tithi does not cancel a rite; it is kept on
the day the tithi was current. All 37 recovered.

Also fixed, each of them user-visible:

- **Multi-day festivals rendered as one day.** `lasts` counts TITHIS. Navarātri
  runs 8, 9 or 10 civil days by year; Pitṛ Pakṣa 15–17.
- **`kind:"solar"` was never implemented**, so Makara Saṅkrānti — Pongal,
  Lohri, Magh Bihu — was absent. And `recurrence` was being stripped as
  "provenance", turning twelve saṅkrāntis into one.
- **No `kind:"nakshatra"`**, so Onam and Kārttikai Dīpam could not be entered
  at all. Malayalam and Tamil months are solar; no lunar anchor can state them.
- **Six festivals were missing entirely** — Onam, Kārttikai Dīpam, Chhaṭh Pūjā,
  Skanda Ṣaṣṭhī, Vaṭa Sāvitrī, Hanumān Jayantī. Skanda Ṣaṣṭhī's key had been
  squatted by the monthly ṣaṣṭhī, so it printed twelve times a year and never
  on the festival.

### Rules that now hold, and are tested

- **Location is not decoration.** Five of seven major Hindu festivals fall on a
  different day in Sydney than Ujjain. Both `/festivals` and `/attic-calendar`
  take `lat`/`lon` and say when they defaulted.
- **Where traditions disagree, both are returned labelled.** smārta/vaiṣṇava on
  ekādaśī, north/deccan on Vaṭa Sāvitrī, north/tamil on Hanumān Jayantī
  (**seven months apart**), conjunction/visibility on the Attic month.
- **Cross-check:** Vaṭa Sāvitrī (north) and Phalahārinī Kālikā Pūjā resolve to
  the same day from independent anchors. That is a test.
- **`restriction` on every entry** — `none`, `detail-withheld`, `initiatory`.
  No closed material in either pack.

### Deliberately unmodelled — flagged, not faked

**candrodaya** (Karva Chauth, Saṅkaṣṭī Caturthī) carries
`dayRuleUnmodelled`; it is longitude-dependent enough to split one festival
across two civil days for two cities, which needs a surface that can show two
answers with the place attached. **Saṅkrānti puṇyakāla** day-attribution
differs between Tamil, Bengali and northern practice and is not applied.
**14 citations** name a real work with no page locus — `locus` is null on
exactly those, so a consumer can tell them apart programmatically.

### One limit that belongs in the UI, not just a file

The report says plainly: *"every date here is a festival-calendar date, and the
archon's civil calendar demonstrably diverged from it — a crescent-anchored
computation approximates an ancient date, it does not reproduce one."* The Attic
tool should say that where people read it.

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
surfaces in the three handoffs. All three came back and are extracted to
`design/` — 35 components with `.d.ts` prop contracts and `.prompt.md` notes,
20 pages, 7 tool-page templates, 2 emails, a print stylesheet. The reference
build is `design/ui_kits/site/index.html`; its demo bar drives the signed-in,
polar/no-sunrise and missing-birth-time states.

The design already expects the failures the daemon models — there is an
athens/polar toggle for the no-sunrise case, which is `SunNeverRose`.
