#!/usr/bin/env python3
"""
Seed the privacy policy and terms.

**This is legal text and it needs a lawyer's eye before launch.** What it is
not is invented: every clause below describes something the code actually does,
and was written by reading the code rather than a template. Where the site does
not do a thing, the policy says so rather than reserving the right.

It is seeded as editable sections like everything else, so corrections happen
in the admin rather than in a deploy.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select                                    # noqa: E402
from shruti.core.db import SessionLocal                          # noqa: E402
from shruti.models import Section                                # noqa: E402

PRIVACY = [
    ("what", "What this covers", 10, """
This policy covers shrutivtuber.com and **Shruti's Astrolabe**, the app for
Android and iPhone. The tools on this site compute against an ephemeris server
run by the same person, and the journal is served from BeeRanked; both are
named below where they apply.

**The controller** is the entity named in the imprint at the foot of every
page. Contact for anything in this policy: business@shrutivtuber.com.
"""),
    ("without-account", "If you never make an account", 20, """
Most of this site needs nothing from you. The calendars, the station trackers,
the pañcāṅga, the natal chart, the letter-reckoning and the sigil generator all
work without an account, and they always will.

What happens when you use them:

- **A place you type is sent to a gazetteer** to turn a city into coordinates.
  That request is made by this server, not by your browser, so the gazetteer
  never sees your IP address — it sees this site's. The provider is Open-Meteo,
  over the GeoNames dataset.
- **Times and charts are computed on the server** and returned to you. The
  parameters are in the URL so a reckoning can be shared or re-opened. Nothing
  is stored — unless you press **Keep this chart**, which is a decision you
  make, needs its own consent, and has a section of its own below.
- **Two instruments compute in your browser instead**: the isopsephy page and
  the sigil generator. What you type into those never reaches this server at
  all — no request is made — and the sigil's share link carries the reduced
  letter set, never the statement it came from.

Server logs record ordinary request information — the page, the time, the
response code. They are not used to build a profile and are not shared.
"""),
    ("counting", "What is counted, and how to say no", 25, """
This site counts how much it is used. It does this itself, on its own server,
and no other company is involved — no Google Analytics, no advertising network,
no pixel from anywhere.

What is recorded, when you open a page or press a tool's button: the page, the
date, which tool, the site you arrived from if there was one, and **a number
that stands in for you**. That number is a one-way hash of your IP address,
your browser's identifying string, the date, and a secret held on the server.

Read that last part slowly, because it is the whole of the design:

- **Your address is never written down.** It goes into the hash and stops there.
  It is not in a column, not in an export, not in a backup.
- **The number cannot be turned back into you.** A hash does not run backwards,
  and there is no table matching numbers to people, here or anywhere.
- **The number changes at midnight**, because the date is inside it. So the
  same person on Tuesday and on Wednesday are two different numbers, and
  nothing on this site can tell they were the same visit. Following anybody
  across days is not something that is declined here — it is something that
  cannot be done.
- **Nothing you type is ever sent.** A tool reports that it was used. It does
  not report your birth time, your city, your question or your statement.

That is why there is no consent banner for this. Consent is required for
personal data, and a number that changes daily, cannot be reversed, and is
never joined to anything is not personal data. Asking anyway would be theatre —
and worse than theatre, because a count that only includes the third of people
who click "yes" is a misleading count, which is a worse thing to run a website
on than no count at all.

**If you would rather not be counted, you can refuse, and the refusal is
honoured.** Three ways, all of which work before anything is sent:

- Turn on **Global Privacy Control** or **Do Not Track** in your browser. Both
  are respected here. Neither is legally binding on this site; both are obeyed.
- Use the switch on this page. It writes one word into your own browser's
  storage. It never reaches the server, and it does not identify you.
- Block the request to `/api/insight/beacon`. It will fail quietly and the
  page will work normally, because nothing on this site depends on being
  counted.
"""),
    ("cookies", "Cookies, and why there is no consent banner", 30, """
This site sets **only strictly necessary cookies**, which under the ePrivacy
rules do not require consent — but do require telling you about. There is no
analytics cookie, no advertising cookie, and no third-party script setting
anything. The counting described in the section above sets no cookie either,
and writes nothing to your browser unless you use the switch to turn it off.

| Name | What it is for | How long |
|---|---|---|
| `shruti_csrf` | A form-security token. Without it, a form on another site could submit here as you. | 8 hours |
| `shruti_reader` | Your sign-in session, if you have an account. | 30 days |
| `shruti_session` | The site owner's admin session. Never set for readers. | 12 hours |

Three things are kept in your browser's local storage rather than in a cookie:
your **light/dark preference**, so the page does not flash white before it
loads, a note that you have **seen the cookie notice**, so it is not shown
again, and — only if you set it — your **choice not to be counted**. None of
them leave your device and none are readable by this server.

There is no consent banner because there is nothing to consent to. A banner
asking permission for cookies that are not optional would be asking about a
choice that does not exist.
"""),
    ("account", "If you make an account", 40, """
An account stores your email address, a password hash if you set one, and the
preferences you choose. **Nothing about an account is public** — there is no
profile page, no avatar, no follower count, and no way for another reader to
see that you exist.

**Three separate decisions** are recorded at sign-up, and you can say yes to
one and no to another:

1. **The account itself.** Lawful basis: contract. Required, because there is
   nothing to sign in to without it.
2. **Storing your birth data for astrological readings.** Lawful basis:
   explicit consent. Never required. Birth data processed to produce an
   astrological reading arguably reveals philosophical belief, which makes it
   special-category data — so it gets its own decision, and **withdrawing that
   consent deletes the saved birth data**. The account survives.
3. **The monthly letter.** Lawful basis: consent, for marketing — the letter
   carries offers for courses and services when those open, and that is said at
   the point of subscription rather than here.

For each, the exact wording you agreed to is stored with the record, along with
the version, the time and where it was given. If the wording changes later, your
record still says what you actually read.
"""),
    ("charts", "If you keep a chart", 45, """
A chart you keep stores your **birth date, birth time and birth place**, and
those are the reason this section exists rather than being a line in the one
above. Birth data used to produce an astrological reading arguably reveals
something about your philosophical beliefs, which makes it **special-category
data** under Article 9. Its lawful basis here is your **explicit consent**, and
that consent is stored word for word, under the version you were shown, next to
the chart it justifies.

**You do not need an account to keep one.** If you do not have one, the consent
is recorded against the chart itself, because there is no account to record it
against.

**Two links, and they are not the same link.**

- The one you land on when you keep a chart is **yours**. It is how you get
  back to it. Nothing about it is guessable and it carries no birth data, so it
  can sit in your browser history without your birth details sitting there too.
- If you choose to share the chart, a **second** link is made. You can revoke
  that one at any time, and revoking it does not disturb yours.

**What somebody with a share link can see, and what they cannot.** The page
they land on does not print your birth date, your birth time or your birth
place. It shows the chart.

A chart is your birth data, drawn. Anybody who can read a chart can get your
birth time to within a few minutes from the ascendant, and the date from the
positions of the planets. Keeping it out of the link and off the page is worth
doing and it stops the ordinary case completely — but it does not, and cannot,
hide it from an astrologer. You are told this at the moment you make the link,
because a protection with a hard limit should be described with the limit.

**How long it is kept.**

- On an account: until you delete it, or delete your account.
- Without an account: **one year**, and the year starts again every time you
  open it. That is not tidying up. The consent behind it cannot be renewed by
  asking, because there is nobody to ask, so it is not relied on indefinitely.

**Deleting one takes one press**, on the chart's own page, with no email and no
waiting. It deletes the birth data with it. If you later make an account, a
chart you already kept can be moved onto it rather than cast again, and the
expiry lifts.
"""),
    ("app", "If you use the app", 47, """
The app is the same tools, on a phone. It talks to **this site and nowhere
else**, apart from the notification services named below, and it has no
analytics, no advertising and no tracking in it of any kind.

**The sky is computed on the phone.** A chart, a station table, the planetary
hours — the arithmetic happens on the device, from tables built into the app.
What you type to cast a chart is used there and then and is **not sent to any
server**, including this one.

**What the app keeps on your phone**, and nowhere else:

- the place you chose, so it does not have to ask again
- whether you count sunrise by the disc's edge or its centre
- whether you asked for notifications, and this phone's notification address
- if you signed in, the token that keeps you signed in

All of it goes when the app does. Deleting the app deletes the lot; there is
no copy of it here.

**If you sign in**, the app uses the account you already have, under the
section above. It is the same account and the same data — there is not a
separate app one.

**If you turn notifications on**, the phone is given an address by Google's
Firebase Cloud Messaging, and that address is registered here so a notice can
be sent to it. Turning notifications off deletes the registration, and so does
signing out. Nothing is sent to a phone that has not asked.

**The limit of that, said plainly.** A phone can only be woken by Google's
service or Apple's, and using either means that service knows this app is
installed on your phone and holds the address notices go to. That is inherent
in push notifications rather than a choice made here, and the only way to
avoid it entirely is to leave notifications off — which costs you nothing else
in the app.
"""),
    ("newsletter", "The monthly letter", 50, """
Subscribing is **double opt-in**: an address that has not confirmed is never
sent to. Every issue carries a one-click unsubscribe that needs no login, and
the page it leads to does not argue with you.

The emails contain **no tracking pixel**. There is no open tracking, no click
tracking and no image of any kind. Delivery is by Resend, which processes the
address in order to send.

You can also **pause** rather than unsubscribe. A pause deletes nothing and
leaves your consent intact.
"""),
    ("rights", "Your rights, and how to use them", 60, """
These are controls in your account, not an address to write to:

- **A copy of your data** — a JSON file, downloaded from your account page
  immediately. It contains your profile, your saved nativity, your full consent
  history with dates, and your newsletter state.
- **Deletion** — immediate and irreversible, from your account page. It removes
  the account, the email address, the preferences, the nativity and the
  newsletter subscription. There is no grace period and no retention attempt.
- **Withdrawing a consent** — one control, as easy as giving it was.
- **Correction** — edit your profile and nativity directly.

**What is kept after deletion**, and why: a record that a consent was given and
withdrawn, with dates and **no birth data**, stripped of the email address that
identified it. That record is the evidence that the processing was lawful and
that the deletion happened; deleting it would remove the proof of both.

You also have the right to complain to a supervisory authority.
"""),
    ("processors", "Who else touches this", 70, """
- **Resend** — sends the email. Sees the recipient address and the message.
- **Open-Meteo / GeoNames** — turns a typed city into coordinates. Sees the
  search term, and this server's IP rather than yours.
- **netcup** — hosts the server, in Austria.
- **Cloudflare** — DNS, and object storage for images.
- **BeeRanked** — serves the journal at /journal.
- **Google Fonts** — serves the typefaces. This is a request your browser makes
  directly, so it does see your IP; self-hosting the fonts would remove that and
  is a known open item.
- **Google (Firebase Cloud Messaging)** — carries notifications to Android
  phones, and holds the address of the phone each one goes to.
- **Apple (Push Notification service)** — the same, for iPhones.

**No analytics company is on this list**, and that is not an omission. How much
the site is used is counted by the site itself, on the same server, and the
figures never leave it. There is no advertising network and no social tracking
pixel either.
"""),
    ("changes", "Changes", 80, """
This page is edited in place rather than replaced. Material changes will be
noted in the monthly letter.
"""),
]

TERMS = [
    ("use", "Using this site", 10, """
The tools here are provided as they are, and they are free to use. They compute
what they say they compute; where a thing cannot be reckoned they say so rather
than guessing, and where two traditions disagree they show both rather than
picking one.

**They are not advice.** Nothing here is medical, legal, financial or
psychological advice, and no claim of predictive validity is made for any of it.
"""),
    ("accounts", "Accounts", 20, """
One account per person. Keep your sign-in details to yourself. You can delete
your account at any time from the account page, immediately and without asking.
"""),
    ("content", "What is yours and what is mine", 30, """
The writing, the software and the brand on this site are mine unless stated
otherwise. The astrology engine is open source under AGPL-3.0 and the link to
its exact running version is on every tool page.

**Fan works** have their own page — see the derivative work guidelines, which
are more permissive than this section and take precedence for that purpose.

What you type into the tools is yours. The two that compute in your browser
never send it anywhere; the rest send it to compute an answer and do not store
it.
"""),
    ("liability", "Liability", 40, """
This site is run by one person. It may go down, be wrong, or change. I am not
liable for decisions taken on the basis of anything computed here — see the
first section: it is not advice.
"""),
]


async def main(force: bool) -> None:
    created = updated = skipped = 0
    async with SessionLocal() as session:
        for page, rows in (("privacy", PRIVACY), ("terms", TERMS)):
            for key, title, position, body in rows:
                row = (
                    await session.execute(
                        select(Section).where(Section.page == page, Section.key == key)
                    )
                ).scalar_one_or_none()
                body = body.strip()
                if row is None:
                    session.add(Section(
                        page=page, key=key, kind="prose", position=position,
                        title=title, body_md=body, visible=True,
                    ))
                    created += 1
                elif force or not row.body_md:
                    row.title, row.body_md, row.position = title, body, position
                    updated += 1
                else:
                    skipped += 1
        await session.commit()

    print(f"  {created} created, {updated} updated, {skipped} left alone")
    print("  NOTE: legal text. Every clause describes what the code actually does,")
    print("  but it needs a lawyer's read before launch.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    asyncio.run(main(ap.parse_args().force))
