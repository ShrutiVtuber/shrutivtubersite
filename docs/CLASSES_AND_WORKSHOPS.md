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

**Recommendation: Cloudflare Stream**, on the grounds that it is one fewer
account and one fewer bill and the signed-token model is exactly right for a
paid course. **Bunny if the bill matters more than the tidiness**, which at
launch it might. Either is a small integration and the choice is not
irreversible — the player is behind one component and one field on a lesson.

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
