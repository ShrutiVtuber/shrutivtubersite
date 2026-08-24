# Design handoff 03 — accounts, horoscopes, newsletter

**For:** the design agent
**Date:** 2026-08-24
**Read with:** handoff 02 (stations and Day at a Glance), which these build on.

This is the second half of the site: the parts that need a person to be known.
Handoff 02 covers the free tools, and those come first deliberately — they work
for anyone, they carry no personal data beyond a location someone types, and
they are what makes the site worth returning to before there is anything to sign
up for.

**Everything here processes personal data, and some of it may be special
category data.** §6 is not boilerplate; please read it before designing the
sign-up.

---

## 1. Accounts — the smallest thing that works

Not a social platform. One person keeping their own chart and their own
horoscope. Design for **someone who signs up once and comes back to read**, not
someone who wants a profile to decorate.

**Sign up / sign in.** Email and password, or a magic link if you prefer — but if
magic link, design the "check your email" state properly, because it is where
people get lost. **The sign-up form is where consent is collected**, so it is
longer than a normal one and that is correct. See §6.

**Profile — small, and honestly so.** Display name, timezone, preferred
tradition (Hellenistic/Vedic), preferred house system and ayanāṁśa. Nothing
public: there are no public profiles and no follower counts. Anything that looks
like a social graph is scope this site does not have.

**Saved nativity.** Birth date, birth time, birth place. The most delicate form
on the site.

- **Birth time is optional and the form must say why.** Without it the ascendant,
  midheaven, houses and sect are undefined — the ascendant moves a degree every
  four minutes. Offer "I don't know my birth time" as a first-class choice with
  a plain explanation of what it costs, not a validation error.
- **Place is a search, resolving to coordinates and a historical timezone.** Show
  the resolved result back. A chart cast for the wrong city is indistinguishable
  from a right one.
- **Data minimisation is a design constraint here.** Do not ask for a street
  address because the ephemeris would accept one.
- One saved chart is enough to start. If more later, they are named.

**Account settings must carry the rights in §6** as real controls: export my
data, delete my account, change consent. Not a support email address.

---

## 2. Horoscopes

Written by hand — twelve a month, one per sign — with the infrastructure built
now for daily, seasonal and yearly so turning those on is a switch rather than a
rebuild.

**Reading surfaces:**

- `/horoscopes` — the month, twelve signs, one page. Someone arriving from a
  search wants their own sign fast: the sign picker is the primary control and
  should remember the choice.
- `/horoscopes/<sign>/<period>` — one reading, linkable and shareable. This is
  the page that gets posted in a Discord, so it needs an OG preview image.
- **Design the period switcher now even though only monthly exists.** If daily
  and seasonal arrive later into a layout that assumed one period, the layout
  gets rebuilt. Show unavailable periods as absent, not as errors.

**A signed-in reader with a saved nativity should see their own sign first**,
without picking. That is the whole reward for having an account.

**An authoring surface** in the admin: twelve fields, a period selector, a
publish state, and a preview that looks exactly like the reading page. Writing
twelve of anything monthly is a chore, and a bad editor is how a monthly feature
becomes a quarterly one.

---

## 3. Newsletter

Monthly. Each issue carries:

- **Their horoscope**, automatically, if they have a saved nativity
- Videos posted since the last issue
- Livestreams since the last issue
- Summaries of articles posted to the site
- **A message written by Sophia** — the part people actually subscribe for

**The commercial intent is real and must be visible.** This list is meant to
eventually sell astrological courses and magickal services. That has to be said
at the point of subscription, in the consent text, not discovered later. Design
the subscribe form to say it plainly — it is also better marketing than hiding it.

**Design needed:**

- **Subscribe block**, reusable across the site, with the consent wording as part
  of the design and not an afterthought pinned underneath
- **Double opt-in confirmation email and its landing page.** An unconfirmed
  address is not consent, so this flow is mandatory, and it is where subscribers
  are lost — design it well
- **The email template itself.** Plain, robust, readable in a dark-mode client
  that will ignore half your CSS. Assume images are blocked
- **Unsubscribe**, one click, no login, and a landing page that does not try to
  argue
- **Preference centre** — which sections they want, and a pause option. A pause
  keeps more people than an unsubscribe loses
- **An archive page** — past issues, public. Good for SEO and it shows a
  prospective subscriber what they are getting

---

## 4. Selling, later

Courses and services are the eventual purpose. **Do not design a shop yet** — but
leave a slot for it in the navigation and the newsletter template so it does not
have to be squeezed in later.

---

## 5. What is already built behind all this

So the design can be concrete rather than hypothetical:

| | |
|---|---|
| `GET /today` | luminaries in both zodiacs, stations with countdowns, current **and next** planetary hour, sky, every reckoning, transits when a nativity is given |
| `GET /stations`, `/stations/next`, `/stations/ical` | four daily stations, up to a month, subscribable feed |
| `GET /chart` | full natal chart, both traditions, SVG figure |
| contact / question box | wired to real email |
| admin | auth, CRUD, media upload, visibility toggles |

`/today` already accepts an optional nativity, so the signed-out and signed-in
states differ by parameters, not by a different page.

---

## 6. Consent and rights — design constraints, not legal boilerplate

Two facts make this heavier than a normal sign-up.

**Birth data processed to produce an astrological reading arguably reveals
philosophical belief**, which would make it *special category* data under GDPR
Article 9. If so, the lawful basis must be **explicit consent** — meaning:

- A **separate, unticked checkbox** with its own clear wording. Not bundled into
  "I accept the terms", not pre-ticked, not inferred from using the form
- Its own explanation of what is stored and why
- **Withdrawable** from account settings as easily as it was given

**The newsletter needs its own separate consent**, and because the list has
commercial intent, that consent must cover marketing rather than only "updates".

**Design these as three distinct decisions**, not one blanket agreement:

1. Create the account *(contract)*
2. Store my birth data for astrological readings *(explicit consent)*
3. Send me the newsletter, including offers *(consent, marketing)*

Someone must be able to say yes to one and no to another, and the form should
make that feel normal rather than obstructive.

**Rights that need real screens**, not an email address:

- **Export my data** — a download, including the saved chart
- **Delete my account** — with a plain statement of what goes and what is kept,
  and a confirmation that is careful without being obstructive. Deletion must
  reach the newsletter list too, not only the account
- **Change my consents** — the same three decisions, revisitable

**The footer needs a legal imprint** from day one: entity name, a **virtual
office address — never her home**, role email, company and VAT number.
Pseudonymity is off, so the imprint is the exposure. Retrofitting one is how
home addresses leak.

**Cookieless analytics**, so no consent banner is needed at all. The cheapest
compliance win available and the first bundle already assumes it. **Do not add a
cookie banner** — if one becomes necessary, something has gone wrong upstream.

---

## 7. What I need from you

1. Sign-up and sign-in, including the three-consent block designed as three
   decisions.
2. The nativity form, with **birth time optional and the cost of omitting it
   explained** in the design.
3. Profile and account settings, including export, delete and consent controls.
4. Horoscope reading page, index with sign picker, and the period switcher built
   for periods that do not exist yet.
5. Horoscope authoring surface for the admin.
6. Newsletter: subscribe block, double opt-in email and landing, the issue
   template, unsubscribe, preference centre, archive.
7. The legal imprint as a footer component.

## 8. Please do not

- Add public profiles, follower counts, or anything social. Not this site.
- Pre-tick a consent box, or bundle consents together.
- Make the signed-out experience a teaser. Handoff 02's pages must be fully
  useful without an account, or nobody will make one.
- Design a cookie banner.
