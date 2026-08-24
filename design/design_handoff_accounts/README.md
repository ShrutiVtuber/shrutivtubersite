# Handoff — accounts, horoscopes and the newsletter

**Prepared for:** the implementing developer agent
**Source:** `brief/DESIGN_HANDOFF_03_accounts.md`
**Date:** 2026-08-24
**Design system:** Shruti (this repository)

---

## 0. The mandate

**Implement the design. Do not interpret it.** Same rule as the first handoff pack: reproduce these
screens exactly, then plug real functionality in behind them. See
`INSTRUCTIONS_FOR_DEVELOPER_AGENT.md` for the short form of the rules.

This pack covers **the second half of the site — the parts that need a person to be known.** It sits
on top of the first pack (`../design_handoff_shrutivtuber/`), which covers the public site, the
component library and the seven tool pages. Read that one first; everything here assumes its tokens,
chrome and components.

**Build order.** Handoff 03 is the companion to **handoff 02 (stations and "Day at a Glance")**,
whose pack is at `../design_handoff_stations/`. **Build those three pages first.** They need no
account and they are what makes the site worth opening daily; handoff 03 §8 is explicit that *the
signed-out experience must not be a teaser* — handoff 02's pages have to be fully useful without an
account, or nobody will make one.

---

## 1. What is in this pack

Nine surfaces, five new components and two email templates.

| # | Surface | Where | Notes |
|---|---|---|---|
| 1 | Sign up | `ui_kits/site/Auth.jsx` | The three-consent block. Longer than a normal form, deliberately. |
| 2 | Sign in | `ui_kits/site/Auth.jsx` | Magic link or password, switchable. |
| 3 | Check your email | `ui_kits/site/Auth.jsx` | The magic-link state, designed properly — it is where people get lost. |
| 4 | Nativity form | `ui_kits/site/Account.jsx` | The most delicate form on the site. |
| 5 | Profile | `ui_kits/site/Account.jsx` | Small, and honestly so. |
| 6 | Consents & data | `ui_kits/site/Account.jsx` | Export, delete, change consent — as real controls. |
| 7 | Horoscope index | `ui_kits/site/Horoscopes.jsx` | Sign picker as the primary control. |
| 8 | Horoscope reading | `ui_kits/site/Horoscopes.jsx` | Linkable, shareable, with the period switcher. |
| 9 | Newsletter ×5 | `ui_kits/site/Newsletter.jsx` | Subscribe · confirmed · unsubscribed · preferences · archive. |
| — | Horoscope authoring | `ui_kits/admin/index.html` → Horoscopes tab | Twelve fields, progress count, live preview. |
| — | Issue email | `email/newsletter-issue.html` | Send-ready. |
| — | Opt-in email | `email/optin-confirm.html` | Send-ready. |

New components, all with `.d.ts` contracts and `.prompt.md` notes, and a shared specimen card at
`components/forms/accounts.card.html`:

| Component | Where | The rule it carries |
|---|---|---|
| `ConsentCheckbox` | `components/forms/` | Never pre-ticked, never bundled, always explains itself. |
| `SignPicker` | `components/navigation/` | Twelve signs as a primary control; marks the reader's own. |
| `PeriodSwitcher` | `components/navigation/` | Unavailable periods are **absent**, not errors. |
| `SubscribeBlock` | `components/brand/` | States the commercial intent at the point of subscription. |
| `LegalImprint` | `components/brand/` | Ships day one; virtual office, never a home address. |

Reference build: open `ui_kits/site/index.html`. The demo bar bottom-right has a **signed in /
signed out** toggle — it drives the "your sign first" behaviour on the horoscope pages.

---

## 2. Consent and rights — design constraints, not boilerplate

This is the part of the pack you must not simplify.

### 2.1 Three decisions, never one

Sign-up collects **three separate agreements**, and someone must be able to say yes to one and no to
another:

| # | Decision | Lawful basis | Required |
|---|---|---|---|
| 1 | Create the account | contract | yes |
| 2 | Store my birth data for astrological readings | **explicit consent** | **no** |
| 3 | Send me the newsletter, including offers | consent, marketing | **no** |

Birth data processed to produce an astrological reading **arguably reveals philosophical belief**,
which would make it *special category* data under GDPR Article 9. If so, the lawful basis must be
explicit consent, which means:

- A **separate, unticked checkbox** with its own clear wording. Not bundled into "I accept the
  terms", not pre-ticked, not inferred from using the form.
- **Its own explanation** of what is stored and why.
- **Withdrawable from account settings as easily as it was given.**

The newsletter consent is separate again, and because the list has commercial intent it must cover
**marketing** rather than only "updates".

Implementation notes:
- `ConsentCheckbox` takes `basis` and `required` so the difference
  between a contract and a consent is visible before a word is read. Required renders "· required";
  optional renders "· optional" in rose.
- Only the *contract* consent can ever show an error. A special-category consent is never required,
  so it can never block a submit.
- Record **consent version, wording, timestamp and source** per decision. The settings screen shows
  "Given 12 Aug 2026 · withdraw any time" from that record.
- Withdrawing consent 2 **deletes the saved nativity with it**. The account survives.

### 2.2 Rights that need real screens

Not a support email address.

- **Export my data** — a download, in-page, including the saved chart. The design promises JSON with
  profile, nativity, consent history with dates, and which letters were sent. No email round-trip,
  no "we will get back to you within 30 days".
- **Delete my account** — a confirmation modal that is careful without being obstructive. It states
  plainly **what goes** (email, name, preferences, nativity, subscription) and **what is kept and
  why** (a consent-given/withdrawn record with dates and no birth data, because that record is the
  proof the law asks for; invoices for as long as tax law requires). **Deletion must reach the
  newsletter list too**, not only the account. Immediate, not reversible, no hostage grace period.
- **Change my consents** — the same three decisions, revisitable.

### 2.3 Cookieless analytics — do not add a banner

Analytics are cookieless, so no consent banner is needed at all. It is the cheapest compliance win
available. **Do not design or build a cookie banner.** If one becomes necessary, something has gone
wrong upstream and it is a conversation, not a component.

### 2.4 The imprint

Footer imprint from day one: entity, **virtual office address — never her home**, role email,
company and VAT number. Pseudonymity is off, so the imprint is the exposure. It is now a component
(`LegalImprint`) and it also appears in the footer of **both** email templates, because a marketing
email legally must carry it.

---

## 3. Accounts

**Not a social platform.** One person keeping their own chart and their own horoscope. Design for
someone who signs up once and comes back to read.

- **Sign up / sign in** — email and password, or magic link. Both are built; the method switcher is
  in the design. If you ship magic link, the **"check your email" state is mandatory** and is
  already designed: it names the address, gives the expiry, says the link works once, mentions spam,
  and offers both "different address" and "send it again".
- **Profile** — display name, timezone, reading language, preferred tradition, house system,
  ayanāṁśa. **Nothing public.** No avatar, no bio, no follower count, no public page. The design
  says so out loud on the profile screen, because that sentence is what stops the feature creeping.
- **Saved nativity** — one is enough to start; if more later, they are named.

### 3.1 The nativity form — the delicate one

Three things are load-bearing:

**Birth time is optional and the form says why.** "I don't know my birth time" is a first-class
checkbox, not a validation error. When ticked, the design states the cost plainly: the ascendant
moves a degree every four minutes, so **ascendant, midheaven, houses and sect become undefined**,
while planets stay put give or take the Moon. It then lists what the reader still gets and what they
do not. Do not turn this into an error, a warning triangle, or a nag.

**Place is a search that resolves to coordinates and a historical timezone, and the resolution is
shown back.** The design displays the resolved place name, latitude, longitude and the timezone that
applied *on that date*, with the line "A chart cast for the wrong city is indistinguishable from a
right one" and a "Not this place?" escape. Historical timezone matters: Greece's offset in 1996 is
not a lookup of today's rules.

**Data minimisation is a design constraint.** Ask for nothing the ephemeris does not use. No street
address, no phone number, no gender field. The design states this on the form.

---

## 4. Horoscopes

Written by hand — **twelve a month, one per sign** — with the infrastructure built now for daily,
seasonal and yearly so turning those on is a switch rather than a rebuild.

- `/horoscopes` — the month, twelve signs, one page. The **sign picker is the primary control** and
  **remembers the choice**.
- `/horoscopes/<sign>/<period>` — one reading, linkable and shareable. This is the page that gets
  posted in a Discord, so it **needs an OG preview image** — generate it per sign and period.
- **The period switcher is designed and placed now**, even though only monthly exists. Periods that
  do not exist render as **absent**, never as errors or disabled-with-a-tooltip.
- **A signed-in reader with a saved nativity sees their own sign first, without picking.** That is
  the whole reward for having an account. The index shows an accent-wash band naming their sign; the
  picker marks it `YOURS`; the reading page badges it "your sign".
- Readings are bylined **Soror Eu. A.** — magickal writing signs with the motto, per the naming
  rules in the first pack.

### 4.1 Authoring surface

In the admin, `Horoscopes` tab. Twelve fields, a period selector, a month selector, a publish state,
and **a preview that looks exactly like the reading page**. Writing twelve of anything monthly is a
chore, and a bad editor is how a monthly feature becomes a quarterly one — so the sign row, the
progress count ("5 of 12 written"), the editor and the preview are all on one screen with no
navigating away and back. Publishing is blocked until all twelve exist; the empty preview says
"an empty reading is worse than a late one".

---

## 5. Newsletter

Monthly. Each issue carries: **their horoscope** automatically if they have a saved nativity; videos
since the last issue; streams since the last issue; summaries of articles; and **a letter written by
hand** — the part people actually subscribe for.

Built here:

- **Subscribe block** (`SubscribeBlock`), reusable across the site, with the consent wording **inside**
  the form rather than pinned underneath.
- **Double opt-in.** Mandatory: an unconfirmed address is not consent. The confirmation email is
  `email/optin-confirm.html`; its landing page is the `confirm` view; the in-form "check your email"
  state is `SubscribeBlock state="sent"`. This flow is where subscribers are lost, so all three
  pieces are designed rather than implied.
- **The issue template** (`email/newsletter-issue.html`) — plain, robust, readable in a dark-mode
  client that ignores half your CSS. **Assume images are blocked**: there are no images at all, no
  webfonts, every critical style is inlined as well as in `<style>`, and layout is tables. Dark mode
  is handled by `prefers-color-scheme` overrides on utility classes plus `color-scheme` meta.
- **Unsubscribe** — one click, **no login**, and a landing page that does not argue. No survey, no
  "are you sure", no win-back offer. It does mention pause, once.
- **Preference centre** — which sections they want, plus cadence including **pause**. A pause keeps
  more people than an unsubscribe loses, and the paused copy says plainly that nothing is deleted and
  consent stays intact.
- **Archive** — past issues, public. Good for SEO and it shows a prospective subscriber exactly what
  they are getting before they hand over an address.

**The commercial intent is visible at the point of subscription**, in the consent text, on the
`/newsletter` page, and in the opt-in email: "including offers for astrological courses and magickal
services when those open". This is deliberate and is not to be softened, moved to a tooltip, or
deferred to the privacy policy.

**No tracking pixel.** The emails carry no open-tracking image and the footnote says so. Do not add
one — it would contradict both the copy and the cookieless-analytics position.

### 5.1 The slot for selling

Courses and services are the eventual purpose. **Do not design or build a shop yet.** A slot is held
in the newsletter template ("Nothing open yet… this is the slot, held deliberately so it does not
have to be squeezed in later") and the site nav has room for it. Leave both in place.

---

## 6. What already exists behind this

From handoff 03 §5, so your integration work is concrete rather than hypothetical:

| Endpoint | What it returns |
|---|---|
| `GET /today` | luminaries in both zodiacs, stations with countdowns, current **and next** planetary hour, sky, every reckoning, transits when a nativity is given |
| `GET /stations`, `/stations/next`, `/stations/ical` | four daily stations, up to a month ahead, subscribable feed |
| `GET /chart` | full natal chart, both traditions, SVG figure |
| contact / question box | wired to real email |
| admin | auth, CRUD, media upload, visibility toggles |

`/today` already accepts an optional nativity, so **the signed-out and signed-in states differ by
parameters, not by a different page.** Build them as one page.

---

## 7. Please do not

Straight from handoff 03 §8, plus what follows from it:

- Add public profiles, follower counts, or anything social. Not this site.
- Pre-tick a consent box, or bundle consents together.
- Make the signed-out experience a teaser.
- Design a cookie banner.
- Add an open-tracking pixel to the emails.
- Build a shop.
- Turn "I don't know my birth time" into an error state.
- Guess a birth time, or a place, when the reader has not given one.

---

## 8. Open questions for the design owner

1. **The newsletter letter's byline — settled.** Handoff 03 §3 says "a message written by Sophia";
   the client has confirmed it is signed **Shruti**. The letter signs Shruti; the horoscope readings
   sign **Soror Eu. A.** No further action.
2. **Handoff 02** — supplied; see `../design_handoff_stations/`. Build it first.
3. Imprint values (street, GEMI, VAT) remain bracketed placeholders until the company is
   established. The client will supply them; ship the brackets.

## 9. Files

```
<project root>/
├── design_handoff_accounts/                 ← this pack
│   ├── README.md
│   ├── INSTRUCTIONS_FOR_DEVELOPER_AGENT.md
│   └── brief/DESIGN_HANDOFF_03_accounts.md
├── design_handoff_shrutivtuber/             ← the first pack: read it first
├── components/                              ← incl. the five new components
├── ui_kits/site/                            ← Auth · Account · Horoscopes · Newsletter
├── ui_kits/admin/                            ← + the Horoscopes authoring tab
├── email/                                    ← the two templates
└── styles.css, tokens/, tailwind.preset.js
```

Everything opens and runs offline with no setup. Start at `ui_kits/site/index.html` and use the demo
bar's **signed in / signed out** toggle.
