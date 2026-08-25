# Classes and workshops — the plan

From her brief in `coursesclassesworkshops`, plus the Teachable-style reference
(`2026-08-25_18-08.png`, The Astrology School).

**Live tracker.** Update as work lands.

## What she asked for, condensed

### Classes — pre-recorded, on the site

- Videos, PDFs, written lessons, quizzes.
- Structured like Teachable: sections → lessons, each lesson typed, a tick per
  lesson, a count per section (`13/15`), search, and "complete & continue".
- Sold **per class, kept forever** — or **included with one or more membership
  tiers**.
- **Access through a membership ends when the membership does. Progress does
  not.** They come back to exactly where they were if they resubscribe.
- One-off series, not an ongoing programme.

### Workshops — live, then sold again

- Live, with a **limited number of tickets**, varying per workshop.
- A ticket buys: attendance while live, **and their recording, for good** —
  emailed as something they can download.
- The **edited on-demand version is a separate purchase**, sold like a class:
  bought outright or included with a tier.
- Live platform needs **raised hands and chat**.

## The shape

Two entitlements and one progress record, kept apart on purpose:

    Course ── Module ── Lesson ── (video | text | pdf | audio | quiz)
      │
      ├── Entitlement   who may open it, and why  ← can be revoked
      └── Enrolment     how far they got          ← never revoked

**That split is the whole of the membership rule.** Losing a membership deletes
an entitlement and touches no progress, so resubscribing is not starting again.
Writing progress into the entitlement would make "keep their progress"
impossible to honour without special cases.

An entitlement records **why** access exists — `purchase` or `tier` — because
the two expire differently and a single "has access" flag cannot say which one
just ended.

### Workshops reuse it

A workshop is a `Course` with a live date and a ticket count. A ticket is an
entitlement to attend plus a permanent entitlement to that session's recording.
The edited on-demand version is a **separate** course, sold separately, exactly
as she described — so nothing needs a special case.

## What has to be decided (hers)

### 1. Where the video lives — the one that costs money

Product files cap at 512 MB and are served whole. A 285-minute lecture is not
that. Real video needs transcoding, adaptive streaming, and a way to stop a
paid course being one shared link from free.

#### Why YouTube does not work here, even privately

She asked, and it is the right question to ask before paying for anything.

- **Unlisted** means anyone holding the link can watch, forever, with no
  account. One student pasting it into a Discord is the whole course gone.
  There is no access control — that is what unlisted *means*.
- **Private** means only Google accounts she has individually invited, capped
  at 100, and private videos cannot be embedded for anyone outside that list.
  It does not scale and it forces every student to have a Google account.
- Either way, every student's viewing goes to Google, on a site that
  [self-hosts its fonts specifically so it stops sending visitors to Google].

So: unlisted is free and leaks; private does not work at all. Worth knowing
rather than assuming, and the honest version is that YouTube is not built to
sell access to something.

#### The four that are

| | Access control | Adaptive | Cost shape | Work |
|---|---|---|---|---|
| **Cloudflare Stream** | signed tokens, expiring | yes | per minute stored + delivered | small |
| **Bunny Stream** | token auth, referrer lock | yes | storage + bandwidth, cheapest | small |
| **Vimeo** | domain-locked embeds | yes | flat monthly tier | smallest |
| **Mux** | signed playback | yes | per minute, dearest | small |

- **Cloudflare Stream** — already her provider for R2 and DNS, so one account
  fewer and one bill fewer. Signed playback tokens expire, so a shared link
  dies. <https://developers.cloudflare.com/stream/> ·
  <https://developers.cloudflare.com/stream/pricing/> ·
  <https://developers.cloudflare.com/stream/viewing-videos/securing-your-stream/>
- **Bunny Stream** — reliably the cheapest of the four and genuinely good.
  A separate account and a separate bill. <https://bunny.net/stream/> ·
  <https://bunny.net/pricing/stream/>
- **Vimeo** — flat monthly rather than per-minute, which is easier to predict
  when she does not know her audience yet. Domain-locked embedding is built
  for exactly this. Least work of the four. <https://vimeo.com/features/video-privacy>
- **Mux** — best tooling, dearest, and aimed at people with more video than
  she has. <https://www.mux.com/pricing/video>

#### The numbers, on a real course

Twenty videos of an hour and a half — **1,800 minutes, 30 hours**. Rates below
are the published ones as understood here; **check the pricing pages before
committing**, because they move and this is the one recurring bill this feature
adds.

The two bill on different axes, which is the whole story:

- **Cloudflare charges per minute watched.** Quality is irrelevant to the bill.
  $5 per 1,000 minutes stored per month, $1 per 1,000 delivered.
- **Bunny charges per gigabyte.** So what somebody watches it at changes the
  bill, and storage counts *every rendition* it transcodes, not just the master.

|  | Cloudflare Stream | Bunny Stream |
|---|---|---|
| Storage | **$9.00 / month** | ~84 GB → **$0.84 / month** |
| One full watch | **$1.80** | **$0.24** at 720p · **$0.34** at 1080p |
| Four full watches | **$7.20** | **~$1.16** |

First year of one course, storage included:

| students | CF, watched once | CF, watched 4× | Bunny, once | Bunny, 4× |
|---:|---:|---:|---:|---:|
| 10 | $126 | $180 | $13 | $22 |
| 100 | $288 | $828 | $39 | $126 |
| 500 | $1,008 | $3,708 | $155 | $590 |

**Whether that matters depends entirely on what a course costs.** Per student,
worst case, the difference is about $6:

| course price | Cloudflare takes | Bunny takes |
|---|---|---|
| €30 | **24%** | 3.9% |
| €80 | 9.0% | 1.4% |
| €150 | 4.8% | 0.8% |

At €150 the difference is noise and the tidier bill wins. At €30 Cloudflare is
eating a quarter of the sale.

**Two honest caveats.** Bunny's bandwidth is cheapest in Europe and North
America and dearer elsewhere — a mostly-Asian audience narrows the gap. And
Cloudflare Stream has a monthly minimum, so the $9 above is a floor rather than
a starting point.

#### Switching later is a field, not a migration

The lesson carries **which provider** and **which video id**, and the player
switches on the first. So both can be live at once and a course can move one at
a time, or never.

What switching actually costs is **re-uploading 30 hours** from her own
masters — time, not code, and she keeps those masters regardless. It is built
provider-agnostic from the start whichever she picks, because that costs
nothing now and buys the freedom later.

### 2. The live platform

**Settled: Daily.co**, which is what she already had in mind, and she will
price workshops against its per-participant cost. Chat and
raised hands come with their prebuilt call UI rather than needing to be built,
cloud recording is a flag, and the API is small enough to wire in a day.

**LiveKit Cloud** is the strong alternative and the one that fits her ethos
better — open source, self-hostable later if she ever wants to. It costs more
work up front because more of the room UI is hers to assemble.

**Zoom** is not recommended: it works, and it puts a third party's branding and
account requirements between her and the people who paid her.

### 3. Quizzes — self-check. Settled.

**Her answer: self-check.** Nothing graded, nothing gateable, no pass mark.

Certification, where she runs one, happens outside the quiz entirely: a written
lesson explains how the examination works, and the examination itself is a live
reading watched by her or an assistant, or a written test sent to her. So the
quiz never has to carry the weight of deciding whether somebody passed
something — which is what makes it small.

### 4. The workshop recording. Settled.

**Confirmed:** the recording of the workshop they attended — one recording, the
same for everyone in that session. Not a per-attendee camera recording.

**And delivered as one package at the end of the whole workshop**, not after
each day. A three-day workshop sends one thing once, so somebody has all of it
in one place rather than three emails to keep track of.

## For her accountant, before the first sale

**Live tuition and recorded courses are not always the same thing for VAT.** A
recorded course is an electronically supplied service — the same treatment as
the memberships, handled by Managed Payments. **Live interactive teaching may
not be**, which would mean it cannot sit under Managed Payments either, exactly
as physical goods cannot.

This does not block building. It decides which tax code a workshop ticket
carries and whether that checkout opts out of Managed Payments, both of which
are one line each.

## Order of work

1. **The LMS itself** — courses, modules, lessons, progress, the reader.
   Video is a reference at this stage, so nothing waits on decision 1.
2. **Entitlements** — buy a class, include it with tiers, revoke on cancel.
3. **Video hosting** — needs decision 1.
4. **Quizzes** — needs decision 3.
5. **Workshops** — tickets, capacity, the live room, recording delivery.

## Design

**No design handoff.** The tokens and the existing components cover this: it is
a sidebar, a list with ticks, and a content pane. It will be built in the
site's own language rather than as a copy of Teachable's, and if that lands
wrong a designer pass can follow — but a handoff before anything exists would
be designing in the dark.


## What she needs to get, and what only she can get

Everything below is an account or a key that has to come from her hands. The
plan does not wait on any of it — the LMS is built against a video reference
and a room id, so both slot in at the end.

**Video** — whichever of the four she picks:

| | What is needed |
|---|---|
| Cloudflare Stream | account id (already held, same as R2) + an API token with Stream:Edit |
| Bunny Stream | account, a video library, its library id + API key |
| Vimeo | a plan that allows domain-locked embedding + an access token |
| Mux | access token id + secret |

**Daily.co** — an account and an API key.
<https://docs.daily.co/reference/rest-api> · <https://www.daily.co/pricing>

**Nothing else.** Stripe already has everything it needs for selling classes
and tickets; the live keys are the same swap already planned, not a new one.
Resend already sends the mail that will carry a workshop recording.

Same handling as always: she writes them into a file, says where, they are
installed without passing through a terminal or a chat, and the file is deleted.

## Design — no handoff

The tokens and the existing components cover this. It is a sidebar, a list with
ticks, and a content pane, and the site already has buttons, badges, prose,
empty states, cards and a type scale. It will be built in the site's own
language rather than as a copy of Teachable's.

If it lands wrong when she sees it, a designer pass can follow — but a handoff
before anything exists would be designing in the dark, and the journal is the
evidence that a handoff is worth it when the thing is a new visual world. This
is not that.


## Settled: Bunny, for now

**Her call, and the reasoning is right.** Courses start around €30–50, where
Cloudflare would take between a tenth and a quarter of each sale. As courses
grow toward €150 the difference becomes noise and she moves to Cloudflare to
keep one provider and one bill.

Which makes provider-agnosticism a requirement rather than a nicety: it is a
planned migration, not a hypothetical one. Every lesson carries its provider
and its id, and both can be live at once.

## Implementation checklist

### Done

- [x] Models: Course, CourseTier, Module, Lesson, QuizQuestion, Entitlement,
      Enrolment, LessonProgress — migrated
- [x] The access rule: bought outright is permanent, a tier lasts as long as
      the tier does, revoking keeps every tick of progress
- [x] Reader API: the outline is public, the content is not, one door
- [x] Progress: recorded for anybody who may open a lesson, never removed
- [x] Video: provider and id on the lesson, Bunny signed, four-hour tokens
- [x] Admin API: courses, modules, lessons, questions, tier inclusion
- [x] Bunny and Daily configured and answering

### Left

**The LMS proper**

- [ ] Admin screens — building a course is API-only today
- [ ] Uploading video from the admin, straight to Bunny rather than through us
- [ ] The reader — sidebar, ticks, complete & continue, the player
- [ ] Re-fetch a stale playback token instead of showing an error
- [ ] `/lessons/{id}/file` — **referenced by the reader API and not yet
      written**, so an audio or PDF lesson currently promises a download that
      404s
- [ ] Quiz UI — answer, reveal, explain
- [ ] `/classes` catalogue and a sales page per course

**Selling it**

- [ ] Stripe checkout for a course, and the webhook that grants entitlement
- [ ] Call `sync_tier_entitlements` when a subscription starts, changes or ends
      — the rule is written and nothing calls it yet
- [ ] The email somebody gets when they buy a class

**Workshops**

- [ ] Seats, and a ticket that counts against them
- [ ] **RSVP for free workshops** — no charge, still a ticket, so she knows
      how many are coming
- [ ] **Launch the room** — one button, creates the Daily room
- [ ] **Invite everyone holding a ticket** — one action, one email each,
      whether they paid or RSVPed
- [ ] Recording delivered as one package after the whole workshop, not per day

## Gotchas this codebase has already paid for

- Route ordering: `/{kind}` catch-alls swallow what follows them.
- A decorator applies to whatever function comes next — do not insert a helper
  between one and its handler.
- Astro: a ternary branch holds ONE expression; two siblings need a fragment.
  Arrow functions with type annotations inside a template do not parse.
- Checkboxes post nothing when unticked; they need a hidden partner.
- Match on content, not on indentation copied from a terminal dump.
- The media-in-use guard is hand-written: a new model with a `media_id` must be
  added to `MEDIA_USERS` or the test fails, correctly.
