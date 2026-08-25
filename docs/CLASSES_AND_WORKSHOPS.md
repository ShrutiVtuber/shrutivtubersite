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
that. Real video needs transcoding, adaptive streaming, and a signed URL so a
paid course is not one right-click from being redistributed.

**Recommendation: Cloudflare Stream.** She is already on Cloudflare for R2 and
DNS, it transcodes and serves adaptive HLS, and it does signed playback tokens
without extra machinery. Priced per minute stored and per minute delivered —
**check the current rate before committing**, because it is the one running
cost this feature adds.

The alternatives, briefly: **Bunny Stream** is cheaper and perfectly good;
**Mux** is the best tooling and the most expensive; **plain R2** is cheapest and
means no adaptive streaming, no signed playback, and one enormous file per
lecture, which is the option that looks fine until somebody watches on a train.

### 2. The live platform

**Recommendation: Daily.co**, which is what she already had in mind. Chat and
raised hands come with their prebuilt call UI rather than needing to be built,
cloud recording is a flag, and the API is small enough to wire in a day.

**LiveKit Cloud** is the strong alternative and the one that fits her ethos
better — open source, self-hostable later if she ever wants to. It costs more
work up front because more of the room UI is hers to assemble.

**Zoom** is not recommended: it works, and it puts a third party's branding and
account requirements between her and the people who paid her.

### 3. Quizzes — what are they for?

Two honest options, and they build differently:

- **Self-check.** Answers revealed, nothing recorded beyond "attempted". Good
  for "did that land?". Simple.
- **Graded, with a pass mark.** A score is stored, a lesson can require a pass
  before continuing, and someone can fail. More to build, and it changes what a
  class *is* — a thing you can get wrong.

Default if she does not care: self-check, because it cannot make somebody feel
they failed a class they paid for.

### 4. One check on her own words

*"they get a copy of their session in email"* — read here as **the recording of
the workshop they attended**, one recording shared by everyone in that session.
Not a per-attendee recording of their own camera. Worth confirming, because the
second is a very different feature.

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
