# Backlog — agreed, not yet built

Recorded 2026-08-24 so none of it is lost. Nothing here is started.

Ordered roughly by dependency, not by priority: accounts underpin most of the
rest, and GDPR underpins accounts.

---

## 1. Station trackers — solar and lunar

**Free public tools.** Enter a location, get the station times for a period up
to a month, export to iCal so people can set their own notifications.

**Why it matters:** this is the return-visit hook. Someone who keeps solar or
lunar adorations needs these times *every day*, and a subscribable feed puts the
site in their calendar rather than in their bookmarks.

- Solar stations: sunrise · noon · sunset · midnight
- Lunar stations: moonrise · culmination · moonset · nadir
- Range: a day up to **one month maximum** (cap it — a year of station times is
  a different product and a much heavier computation)
- Export: **iCal** (`.ics` download *and* a subscribable `webcal:` feed, which
  is the one that actually generates notifications), plus Google Calendar links
- Display: see the design handoff (`docs/DESIGN_HANDOFF_02_stations.md`)

**Reuse:** Theourgia has `core/resh/adorations.py` (the four-station daily rite,
with Hellenic and Thelemic presets), `core/astro/sun_times.py`, and a 213-line
`core/calendar/ical_serializer.py`. All AGPL, none of it needs the commercial
ephemeris licence — port the logic, rewrite the ephemeris calls against
shruti-astro's AGPL binding.

**Backend:** `shruti-astro` already computes sun and moon rise/set/culmination.
The gap is the nadir/anti-culmination, the range walk, and the iCal serializer.

---

## 2. Day at a glance

One page answering "what is the sky doing right now, here".

- Sun sign and Moon sign at this moment
- The solar and lunar station in force, and the next one
- The current planetary hour **and the one coming next**
- The sky over the visitor's location
- **Their transits, if they have a saved nativity**

**Works without an account** — a visitor who only gives a location gets
everything except the transits. That matters: the page has to be useful before
anyone signs up, or nobody will.

---

## 3. Accounts

The smallest thing that supports the above.

- Create an account, small profile page
- **Create and save a nativity chart** (birth date, time, place)
- The day-at-a-glance page then adds their transits

**This is the piece that changes the legal posture of the whole site** — see §6.
Birth data is personal data, and in an astrological context it plausibly reveals
philosophical belief, which is a *special category* under GDPR Art. 9. Do not
build accounts before reading that section.

---

## 4. Horoscopes

- **Monthly, per sign** — written by hand, twelve a month
- Infrastructure for **yearly, seasonal and daily** built at the same time, so
  turning them on later is a config change and not a migration
- Model it as `horoscope(scope, sign, period_start, period_end, body)` from the
  start; retrofitting a period type onto a monthly-only table is the kind of
  thing that forces a rewrite

---

## 5. Newsletter

Subscribe, and receive monthly:

- **Their horoscope**, automatically, if they have a saved nativity — whatever
  is available for them that month
- A summary of videos posted
- A summary of livestreams
- Summaries of articles posted to the site
- **A monthly message written by Sophia**

**Commercial intent, stated plainly:** this list is meant to eventually sell
astrological courses and magickal services. That is a legitimate purpose and it
must be disclosed at the point of subscription — it also means the consent
collected has to cover marketing, not merely "updates".

**Resend is already wired** (`shruti/core/mail.py`, domain verified). What is
missing is list management, double opt-in, unsubscribe, and the digest builder.

---

## 6. GDPR — fully compliant, and this is not the usual checklist

Sophia asked for 100% compliance on everything that could apply. Two facts make
this heavier than a normal site:

**(a) Birth data in an astrological context may be Article 9 special category
data.** Not because a birth date is sensitive on its own, but because processing
it *to produce an astrological reading* arguably reveals philosophical or
religious belief. If it is Art. 9, the lawful basis must be **explicit consent**
(Art. 9(2)(a)) — a checkbox with its own clear wording, separate from the
account terms, and revocable. Get this decided before writing the schema, because
it determines whether birth data can be stored at all under the current basis.

**(b) An EU-resident controller selling to consumers.** ShrutiVTuber LLC, an
operator in Athens, a newsletter with commercial intent, and accounts. The full
set applies.

What that means concretely:

- **Lawful bases, written down per purpose** — account (contract), newsletter
  (consent), horoscope-by-birthchart (explicit consent if Art. 9 applies),
  analytics (consent, or none if the analytics are genuinely cookieless)
- **Double opt-in on the newsletter**, with the confirmation recorded — an
  unconfirmed address is not consent
- **Unsubscribe in every email**, one click, no login required
- **Right of access, erasure, rectification, portability, objection** — build
  the export and the delete as real endpoints, not a support inbox. Erasure must
  reach the newsletter list and Resend, not only the database
- **Records of processing (Art. 30)** — a real document
- **Processor agreements** with Resend, Cloudflare, netcup, and any analytics
- **Privacy policy** naming every processor and every purpose. Theourgia has a
  template with placeholders
- **Legal imprint** — EU e-Commerce Directive Art. 5 requires it the moment
  anything is sold. **A virtual office address, never her home**; pseudonymity is
  already off, so the imprint is the exposure
- **Cookieless analytics** so no consent banner is needed at all — the cheapest
  compliance win available, and the design brief already assumes it
- **Data minimisation** — do not collect a birth time to the second and a
  precise home address because the ephemeris will accept them
- **Retention limits**, written and enforced by a job, not by intention
- **Breach procedure** — 72 hours, and knowing that in advance is the only way
  it happens

**A DPIA is likely required** (Art. 35) given special-category data plus
profiling-adjacent processing. Doing it early is much cheaper than doing it after
the schema exists.

---

## Cross-cutting note

Items 1 and 2 are free public tools and need no account. Items 3–5 need accounts
and therefore need §6 settled first. **Build 1 and 2 first**: they are the
return-visit hook, they carry no personal data beyond a location the visitor
types, and they make the site worth coming back to before there is anything to
sign up for.

## Festival rules deliberately not modelled — revisit

Both are flagged in the corpus rather than faked, and both need a surface
before they can be answered honestly. Neither is a bug.

### candrodaya — moonrise-anchored observances

Karva Chauth and Saṅkaṣṭī Caturthī are kept **until moonrise**, and moonrise is
longitude-dependent enough to put one festival on **two different civil days for
two cities**. A single `dayRule` value cannot express that — the honest answer
needs two dates with the place attached to each.

The entries carry `dayRuleUnmodelled: "candrodaya"` and currently resolve to the
sunrise answer, which is usually but not always the same day.

**What it needs:** `swe.rise_trans` for the Moon (the same call the solar
stations use, with `swe.CALC_RISE`), plus a results surface that can show a
per-location answer rather than one date. The `/today` page and the station
trackers are exactly that surface, so this is worth revisiting **once handoff
02's three pages exist** — not before.

### saṅkrānti puṇyakāla — which civil day owns an ingress

`resolve_solar` takes the civil day containing the ingress instant. Regional
nirṇaya can defer it to the following day when the Sun crosses after sunset, and
the rule **differs between Tamil, Bengali and northern practice** — so this is a
`variants`/`school` problem, not a single missing calculation.

`/festivals` already returns labelled variants where traditions disagree
(smārta/vaiṣṇava, north/deccan), so the mechanism exists; what is missing is the
sourced rule per school. **Do not pick one and call it the default.**

### Also open, lower stakes

- **14 citations name a work with no page or section locus.** `locus` is null on
  exactly those, so they are machine-distinguishable from pinned ones. Real
  works, not fabrications — but they could be pinned properly.
- **The Hindu audit read 42 entries with ~19,000 characters of nirṇaya reasoning
  missing**, because our own export truncated at 900 chars. Its findings are
  indicative, not final. Re-running it against the full notes would likely
  retire some and surface others.

## Payments — Stripe on /support, and one-click cancellation

Requested 2026-08-24. Not started; the Support page currently ships the
designed tiers with a Ko-fi route and no payment integration.

**Two halves, and the second is a legal requirement, not a nicety.**

### Stripe

Ko-fi is what the design assumes today (`Join on Ko-fi`, `Open Ko-fi`), and the
page already says "Memberships are Ko-fi-hosted; cancel any time". Moving to
Stripe changes that copy, so it is a design change as well as an integration —
the tier cards, the button labels and that line all have to move together. Raise
it with the design owner rather than swapping the buttons and leaving the
sentence.

Needs: Stripe account and keys, products/prices for the two membership tiers
(€4 Lamplighter, €9 Almanac) plus a one-off, webhook endpoint for
`checkout.session.completed` / `customer.subscription.deleted`, and a customer
record joined to the site account.

### One-click cancellation — this is the law, not a preference

The EU's Consumer Rights Directive as amended (and Germany's
*Kündigungsbutton*, and California's click-to-cancel rule) require that a
subscription entered into online can be cancelled **as easily as it was
started** — a plainly labelled control, reachable without logging a support
ticket, without a retention flow, and without a phone call.

The design already takes this position for the newsletter: unsubscribe is one
click, no login, and the landing page "does not argue — no survey, no 'are you
sure', no win-back offer". The same rule has to hold for a paid membership.
Concretely:

- a **Cancel membership** control in the account, at the same level as the
  thing that started it;
- **no** retention interstitial, no discount offer, no multi-step confirm;
- it must reach **Stripe**, not just the local record — a cancelled account
  that keeps billing is the worst possible failure here;
- confirmation by email, and the period already paid for runs out rather than
  being clawed back.

This lands alongside the account deletion flow, which has the same shape and the
same rule: deletion must reach the newsletter list too, not only the account.

## The API cannot express a date before 1 CE

Found while wiring the Attic calendar tool page, 2026-08-24.

Every endpoint takes its instant as a Python `datetime`, and `datetime` has no
year below 1 — `replace(year=-490)` raises. So a BCE date cannot be asked for
anywhere, and `/attic-calendar?when=-0490-09-12` returns a stated refusal.

**Why it matters more here than elsewhere.** The Attic calendar's whole subject
is classical Athens. Someone wanting the Attic date of Marathon, or of the
first Panathenaia, cannot ask. That is the obvious question for this
instrument and it is the one question it will not take.

**It also makes a designed cannot-compute state unreachable.** The handoff
lists "before 432 BCE the Metonic cycle was not in use" as a state that must be
reachable. `_attic_year` raises `BeforeTheCycle` correctly and that is tested
directly — but 432 BCE sits on the far side of a floor at 1 CE, so no request
can trigger it. The check is right; the path to it does not exist.

**What fixing it takes.** `swe.julday` accepts negative years without
complaint, so the ephemeris is not the constraint — the datetime-shaped seam
through the core is. The change is to carry a Julian Day (or a
year/month/day/hour tuple) through `ephemeris`, `attic`, `hindu_calendar` and
the API layer instead of a `datetime`, keeping `datetime` only at the edges
where a real timezone matters. That is a real refactor across most of the core,
not a patch, which is why it is written down here rather than half-done.

Until then the limit is stated in `_moment`'s docstring, in the API's error
message, and on the Attic tool page itself.

## Location search by city and country, everywhere

Requested 2026-08-24. Every surface that takes a place currently takes raw
latitude and longitude — `/today`, both station trackers, and all five
ephemeris tool pages. Typing coordinates is not how anyone knows where they
are.

**Match theourgia's mobile behaviour**: type a city, get a resolved place with
its coordinates and the timezone that applied *on that date*, shown back before
anything is computed.

Two design rules already written down that this has to honour:

- The stations handoff: *"the resolved coordinates and timezone are shown back
  — a station table for the wrong city is indistinguishable from a right one
  until someone misses a dawn."* Both tracker pages already print the
  coordinates back; a search has to keep doing that, plus the resolved name.
- The accounts handoff, on the nativity form: place *"is a search that resolves
  to coordinates and a historical timezone, and the resolution is shown back"*,
  with *"A chart cast for the wrong city is indistinguishable from a right one"*
  and a **"Not this place?"** escape.

**Historical timezone matters and is the hard half.** Greece's offset in 1996 is
not a lookup of today's rules, and a nativity is exactly the case where that
bites. A geocoder that returns only lat/lon is not enough on its own.

Where it goes, once built as one component: `/today`, `/tools/solar-stations`,
`/tools/lunar-stations`, `/tools/planetary-hours`, `/tools/pancanga`,
`/tools/hindu-calendar`, `/tools/attic-calendar`, `/tools/natal-chart`, and the
nativity form when accounts land. The tool pages share one parameter panel, so
this is one component and one retrofit pass rather than nine.

Open question for the owner: which gazetteer. Theourgia already solved this on
mobile — reuse its source and its data shape rather than picking a second one,
so a place resolved in one product means the same thing in the other.

## Cloudflare R2 — what to create

The storage layer is built and tested; it uses R2 the moment four settings are
present and falls back to local disk otherwise. Nothing is blocked, but images
are currently on the server's own disk.

**The existing Cloudflare token cannot do this.** It was scoped for DNS-01 ACME
and lives on the server in `/etc/caddy/caddy.env`. R2 needs its own credential.

### In the Cloudflare dashboard

1. **R2 → Create bucket.** Name it `shrutivtuber-media`. Location: automatic,
   or hint EU since the server is in Germany.
2. **R2 → Manage API tokens → Create API token.** Permission: *Object Read &
   Write*, scoped to that one bucket. Copy the **Access Key ID** and **Secret
   Access Key** — the secret is shown once.
3. **Public access.** Either enable the bucket's `r2.dev` subdomain (fine to
   start), or connect a custom domain such as `media.shrutivtuber.com`, which is
   better: it survives a bucket rename and keeps the URLs on your own domain.
4. Note the **Account ID** from the R2 overview page.

### Then set, in `.env`

```
SHRUTI_R2_ACCOUNT_ID=…
SHRUTI_R2_BUCKET=shrutivtuber-media
SHRUTI_R2_ACCESS_KEY_ID=…
SHRUTI_R2_SECRET_ACCESS_KEY=…
SHRUTI_R2_PUBLIC_BASE=https://media.shrutivtuber.com
```

**Escape any `$` in those values as `$$`** — docker compose interpolates `$VAR`
inside `.env` values, which is what shredded the argon2 admin hash earlier.

### What happens then

New uploads go to R2 and are served from `SHRUTI_R2_PUBLIC_BASE`. Files already
on disk keep resolving to `/media/*`, because each row records the backend it
used — without that, switching R2 on would repoint every existing URL at a
bucket that does not contain those files and every image would 404 at once.

Moving the existing files across is a separate, small job: upload each, flip
`storage_backend` to `r2`. Not worth doing before there is much to move.

### Not yet done

- **Signed URLs.** Everything stored is public art, so public read is right for
  now. If private media ever appears — an unpublished commission, a member-only
  file — it needs presigned GETs, and the signer for that is already here.
- ~~**Deleting from the bucket.**~~ Done. Deleting a media row deletes the
  object, and has since that route was written — this note was stale. What was
  genuinely missing was any way to FIND an orphan, since every way one appears
  is outside that route: an upload that stored the file and then failed to
  commit, a database restored from before an upload, or rows cleared in SQL.
  `/admin/media` now lists both directions of disagreement and can sweep.

  **The trap that surfaced while building it:** development and production
  share one bucket, so a laptop's database calls every production image an
  orphan. The check run locally listed four live project thumbnails. The
  listing is safe to read anywhere; sweeping is refused outside production.
