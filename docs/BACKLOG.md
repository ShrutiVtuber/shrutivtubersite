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
- **Processor agreements** with Resend, Cloudflare, Hetzner, and any analytics
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
