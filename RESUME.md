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

## FIRST TASK — close the three festival gaps

Output is in `~/Documents/development/shruti-research/` (outside the repo:
working material, partly unverified). Read its `README.md` first.

**71 Hindu entries and 45 Attic entries**, all cited, confidence graded
`attested` / `disputed` / `reconstructed`. Sourcing quality is good — real loci
(Plutarch *Theseus* 24, Harpokration s.v. εἰρεσιώνη, Demosthenes 24.26) and the
agents recorded disagreement rather than resolving it.

Three gaps, all diagnosed, in the order to fix them.

### Gap 1 — CLOSED and verified

Day rules applied to **18 entries**, each carrying a cited reason in its own
note. Everything else keeps the sunrise default. **Twelve festivals now resolve
to their published 2026 almanac dates exactly**, including the four the sunrise
rule got wrong: Mahā Śivarātri and Janmāṣṭamī (niśītha), Gaṇeśa Caturthī and
Rāma Navamī (madhyāhna), Vijayadaśamī (aparāhṇa), Lakṣmī Pūjā (pradoṣa).

One moment the engine cannot model is recorded rather than forced: **Karva
Chauth is kept until moonrise**, and there is no moonrise day-rule. It resolves
to the sunrise answer, which is usually but not always the same day.

The original diagnosis, kept for context:

**Cause: the schema handed to the agents predated the discovery.** Day-ownership
is not one rule — most observances go to the tithi at sunrise, but Dīpāvalī is
kept at *pradoṣa*, Mahā Śivarātri and Janmāṣṭamī at *niśītha*, Vijayadaśamī at
*aparāhṇa*, Gaṇeśa Caturthī at *madhyāhna*.

Measured against published 2026 almanacs:

| festival | resolved | almanac | |
|---|---|---|---|
| Vasant Pañcamī | 23 Jan | 23 Jan | ✓ |
| Holikā Dahan | 3 Mar | 3 Mar | ✓ |
| Holi | 4 Mar | 4 Mar | ✓ |
| **Mahā Śivarātri** | **16 Feb** | **15 Feb** | ✗ needs `nishitha` |

The sunrise default is right for most and wrong for a known handful. **Do not
add `dayRule` to everything** — add it only where the tradition actually uses a
different moment, and cite why in the entry's note. `DAY_RULES` in
`shruti_astro/core/festivals.py` has the five.

Verify by resolving a year and diffing against a published pañcāṅga, not by
inspection.

### Gap 2 — the Hindu entries never went through the audit pass

The assembly agent's report contains **only the Attic corpus**. The 71 Hindu
entries were recovered from `journal.jsonl`, where each agent's structured
result is recorded — so they exist and are complete, but they skipped the
adversarial verification the Attic set received.

Run them through the same audit: anchor correctness, the amānta/pūrṇimānta trap,
citations that do not actually support the date, anything graded `attested` that
is really `disputed`, and initiatory material reproduced in detail rather than
merely named. The six raw corpora are in `shruti-research/corpora/`.

### Gap 3 — CLOSED

All 68 lunar anchors resolve: **50 annual, 14 recurring, 4 legitimately kṣaya,
0 failing** — 206 dated occurrences across 2026.

Three things were built. `month: "*"` returns **every** occurrence in the year,
with a return type that genuinely differs from an annual anchor's. `month:
"adhika"` resolves only inside intercalary months, so an empty list in an
ordinary year is the right answer. And a doubled tithi is **marked, not
deduped** — on a vṛddhi Ekādaśī the Smārta and Vaiṣṇava traditions fast on
different days, and dropping one would make that ruling for the practitioner.

The original diagnosis:

### Gap 3 — four causes, two already fixed

The 17 break down as: **13×** `month: "*"`, **2×** `Caitra` (a spelling variant
of `Chaitra` — **fixed**, original recorded), **1×** `Mārgaśīrṣa or Pauṣa`
(Vaikuṇṭha Ekādaśī genuinely differs by region — record as regional variants,
do not resolve), **1×** `adhika (intercalary)` (Padminī and Paramā Ekādaśī occur
only in an intercalary month and need an anchor kind that says so).

`Śāradīya Navarātri` also appears twice under different keys, from two corpora.

The remaining thirteen are the real work:

**All 13 use `"month": "*"`.** They are the *recurring* observances —
Ekādaśī twice a lunation, Pradoṣa, Sankaṣṭī Caturthī, Amāvāsyā, Pūrṇimā. The
agents encoded "every month" sensibly; `resolve_lunar` simply rejects a wildcard.

These matter more than the annual festivals for daily practice, so this is worth
doing properly:

- Accept `month: "*"` and return **every** occurrence in the year, not one date
- The return type changes — a recurring anchor yields a list, an annual one a
  single date. Decide that shape before writing it
- They also need `dayRule`: Pradoṣa is kept at *pradoṣa* by definition, and
  Ekādaśī has its own conventions
- 49 of 68 resolve today; 2 are legitimately kṣaya (a tithi owning no civil day)

Then pack both corpora as MBF via `shruti_astro/packs/mbf.py` and resolve a full
year of each against the engine before shipping.

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
surfaces in the three handoffs.
