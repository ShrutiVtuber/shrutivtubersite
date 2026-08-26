# Marketing research — 26 August 2026

Companion to `AUDIT_SEO_2026-08-26.md`. Two research passes: how VTubers
actually get discovered, and the business mechanics underneath it.

**Read the confidence notes at the end.** Some of this is measured, some is from
vendor blogs with an interest, and some widely-repeated numbers turned out to
trace back to AI content farms and are excluded.

---

## 0. A correction I have to make first

**I briefed the legal research for Germany. This codebase says Greece.**

The imprint form in the admin offers `GEMI 123456789012` as the registry
example and `VAT EL123456789` as the VAT example — those are the Greek business
registry and the Greek VAT prefix. Athens is the default location in every
instrument, and the schedule says streams are "authored in Athens".

So the returned material on § 5 DDG, the Medienstaatsvertrag and the German
Kleinunternehmerregelung is **probably not your law**, and I am not going to
present it as though it were. That was my error in the brief, not the
researcher's.

**Two things from it survive regardless of country**, because both come from EU
law that every member state implements:

1. **The imprint address has to be a real, physical, geographic address** — the
   place the provider is actually established. This comes from the E-Commerce
   Directive, not from German law.

   The admin form currently tells you the opposite: the Street field's help text
   reads **"The VIRTUAL OFFICE — never a home address"**. That advice is good
   for your safety and may not satisfy the legal requirement, and those two
   things being in tension is exactly the sort of thing you want a lawyer for
   rather than a search engine. **It is also the one open item genuinely
   blocking launch, so it is worth asking properly and soon.**

2. **All your revenue streams aggregate for the small-business VAT threshold.**
   Merch, memberships, class fees, commissions and sponsorship count together,
   not separately. Whatever Greece's threshold is, it is not per-activity.

I can re-run the legal pass against Greek law if you confirm the jurisdiction.
I did not do it unasked, because guessing a second time is worse than asking.

---

## 1. The finding that should change where you stream

This is measured, today, and it is the most important thing in either report.

| Twitch category | Top-50 viewer hours, 30 days |
|---|---|
| Science & Technology | 965,478 — **but NASA alone is 694,699**; ~270,000 without it |
| **Software and Game Development** | **368,185** |
| Tarot | **9,552** |
| **Astrology** | **"No results found."** The category exists. Zero ranked channels. |

Tarot's *entire* top fifty does less than half what the third-place coding
streamer does alone. Astrology returns nothing at all.

> **You cannot be found by browsing an astrology category, because nobody is
> browsing it.** The technical categories are roughly thirty-eight times
> larger, and Twitch actively promotes them — its VTuber Club and VTuber Week
> features have gone to tech-flavoured indies.

**The read for your channel:** stream in **Software and Game Development**,
where both the traffic and your peers are, and let the magick and astrology be
*the subject matter of what gets built* rather than the category you compete in.

That is not a repositioning. It is what you already do — "programming for
magickal practice" is a software stream whose domain happens to be astrology.
This just says the category tag should match the format, not the topic.

---

## 2. The two precedents, and they point the same way

### Vedal / Neuro-sama — a solo programmer out-scaling every agency

- **One pseudonymous programmer.** Began 2018 as an *osu!* bot with no voice,
  no model and no personality.
- Relaunched 19 December 2022 with an LLM, TTS, and a **free generic Live2D
  avatar**. In the next ten days: 2,000+ average viewers, and subscribers went
  from 2,825 to roughly 40,000 between the 19th and the 31st.
- **The original avatar came in May 2023. The 3D model came in November 2025.**
  The model followed the audience, not the other way round.
- Now the **third most-subscribed Twitch channel of all time.**
- **The format is developer streams** — debugging code on stream, planning the
  schedule, taking change suggestions from chat. He appears as a turtle.
- Won **Best Tech VTuber at both the 2023 and 2024 VTuber Awards.**

**The content *is* the build. The audience watches the engineering, not around
it.**

### CodeMiko — what the expensive route costs

Built alone in Unreal Engine with an Xsens suit, Manus gloves and a mocap
helmet. **Early Twitch income was about $300 a month, which did not cover
rent. She went more than $20,000 into debt**, and has said her success came
partly from that debt and her own poor risk management. The breakthrough came in
2021 from a viral tweet and a Reddit clip. The team came *after* the success.

**Read together:** the cheap-avatar / expensive-software path produced the
bigger, faster, far less capital-intensive outcome. The expensive-hardware path
produced two years of near-zero income before a viral accident.

### And the thing both have in common

**Neither was discovered through a category.** Vedal went viral off a novel
artefact; CodeMiko off a tweet and a clip.

> Discovery came from **the artefact** — not the topic tag, and not the persona.

Which is the strongest available argument that the nine instruments, the charts
and the compatibility cards are correctly positioned. They are artefacts that
travel. That is the mechanism that demonstrably worked for both verified
precedents in this niche.

---

## 3. Agencies stopped being the ceiling

**VShojo — one of the three companies that defined Western VTubing — ceased
operations on 24 July 2025.** Ironmouse left on the 21st, accusing it of
withholding streaming residuals including roughly $500,000 raised for the Immune
Deficiency Foundation. Within three days effectively every talent had resigned.
It had raised $11M in 2022 and had no independent board. Smaller outfits keep
repeating the pattern — Luminara collapsed in May 2026.

**Consequence:** the top of the Western scene is now high-profile independents,
and collab circles in 2026 are **peer networks, not booking departments.**

Indies now form their own named collectives — The Wildcard Club (Ironmouse,
Dokibird, AmaLee, Rin Penrose), Densetsu.EXE, Aegis-Link. The producer of
Densetsu.EXE gave a panel on forming the group **in sixty days**, covering
planning, budgets and legal.

### What an agency actually provides, and which parts you already have

ANYCOLOR (Nijisanji) publishes its own service list. One line stands out:

> "CREATIVE: We create Live2D and 3D models, and develop products for Liver
> fans (**site creation, web and smartphone applications, in-company systems**,
> etc.)"

**The agency's creative division is a web engineering team.** That is the part
of the agency offer you already have and most indies do not.

Of the rest: the model is money rather than access; music is replicable at cost;
3D concerts are proven replicable by indies; merch and logistics are fully
replicable. **The two real gaps are legal counsel and sponsorship brokerage.**
And management has inverted — after VShojo it is a risk as much as a service.

---

## 4. How an indie actually gets into the room

The etiquette is documented and consistent, and it is not "DM people":

- Be an active member of someone's community **before** reaching out.
- Use public channels — email, business enquiries, a manager. Closed DMs are a
  boundary, not a challenge.
- **Offer value first: art, resources, feedback.**

That last one is the builder's entry ticket, and it leads to the most actionable
finding in the whole pass:

### Ship tools other VTubers use

The **VTuber Industry Awards** — first held February 2025, 39 creatives across
10 categories — exist to honour riggers, asset makers, editors and **tooling
developers**. Real categories awarded:

- **Technical Excellence** — for "creating practical stream widgets which
  enhance VTubers' setups."
- **Why Have You Done This?** — for a toggle-based Stream Deck setup.
- **VTuber Jumpstart** — for editable Live2D assets.

The host said the awards exist to "foster relationships between content creators
and artists," and judging explicitly weighs **whether the work was done for
other clients too.**

> **Shipping tools other VTubers use enters you as a supplier and a peer rather
> than as a supplicant** — and there is a nomination-based circuit that makes it
> visible.

The compatibility feature is already exactly this shape. It is a tool other
creators use, with your name on it.

### One gap nobody has filled

**There is no timezone-coordination tool for collabs.** The research looked and
found none, and the main VTuber networking guide does not cover it.

You have this problem yourself — Athens collaborating with North America. A
small, shareable "when can we all stream" tool aimed at VTubers is a genuinely
unoccupied slot, and it is the kind of artefact that travels.

### Panels are the cheapest route onto a stage

OffKai Expo's programme is overwhelmingly **indie-submitted panels**, and they
reward specific competence rather than follower count — a linguist VTuber got
one on the etymology of VTuber slang; there were panels on songwriting, on law
for creatives, on internet safety.

**"Programming for magickal practice" is exactly that kind of proposal.**

Verified dates worth knowing: **VeXpo 2026**, 18–20 September 2026, NEC
Birmingham — the closest one to you, and non-profit. **OffKai Gen 5** was
24–26 July 2026 in San Jose. **VTUBER EXPO 2026**, 3–4 May, Akihabara.

One cautionary note: guests withdrew from VirtuaCon 2025 days beforehand once
its Web3 links surfaced. **Vetting an event's funding is now standard practice.**

---

## 5. Money mechanics, with real numbers

### Membership platforms

| Platform | You keep |
|---|---|
| Discord paid roles | 90% (≈87% after Stripe) |
| YouTube memberships | 70% |
| Fourthwall memberships | 95% |
| Ko-fi memberships | 95% free plan, 100% on Gold |
| Patreon (new pages after 4 Aug 2025) | **90%** — the flat fee rose |
| Twitch subs | 50% default |

**Self-hosting on Stripe keeps roughly ten more points of every euro than
Patreon**, and it keeps the customer list. On €1,000/month that is about
€100/month — that is the return on having built it yourself.

### What tiers should actually contain

**hololive's own channel runs exactly two tiers, not six.** The top one rests on
**questionnaire participation** — surveys that steer content — and
**downloadable artefacts**.

Both of those are cheap to produce and **both are delivered better by a website
than by YouTube.** You already have polls and a media library. That is the tier
design, and it is one you can actually staff.

### Merch: start with acrylics, not plush

- **Acrylic stands and keychains: $12–25, 50–100 unit minimums.** That is the
  correct first drop for a channel this size.
- Plush needs **200 units** (Makeship's floor, and the industry MOQ). Makeship
  runs a **21-day campaign and refunds everyone if it does not fund** — no
  upfront cost, but a public failure if it misses.
- Bundles lift average order value from about $35 to $65+.

**The convention worth copying is the calendar, not the product.** Japanese
VTuber merch is pinned to **identity events** — birthday, debut anniversary,
outfit reveal, subscriber milestone. Fixed annual cadence, built-in urgency, and
a natural reason to reveal it live on stream.

A real verified drop for shape: a one-month order window, shipping about four
months later, with a bonus digital wallpaper for orders of three or more items.

### Numbers I am deliberately not giving you

The widely-quoted "VTubers average $6,840/month, 42% subscriptions / 28% ads /
15% merch" traces back to an unnamed survey of 2,500 VTubers that could not be
located, republished across several AI content farms. **Excluded.** Likewise
VTuber sponsorship rate cards.

The one defensible planning figure, and it is a practitioner's estimate rather
than data: meaningful income around **$500/month at six to twelve months with
1,000–5,000 engaged followers**; full-time needs one to two years; over half
quit within three years.

**One conversion datapoint does favour you.** Discord-to-paid conversion runs
3–8% typically, and reaches 10%+ only in what the source calls
"problem-solving niches" — and it names **coding** as one of them. A teaching
and practice membership converts better than a pure entertainment one.

---

## 6. What I would actually do, in order

1. **Change the Twitch category to Software and Game Development.** Free, today,
   and it is the difference between a category nobody browses and one that is
   thirty-eight times larger.
2. **Ask a Greek lawyer about the imprint address.** It is the only hard blocker
   left, and the admin's own help text currently points the wrong way.
3. **Keep building artefacts, and put your name on them.** That is the verified
   discovery mechanism in this niche, and the site is already the thing most
   indies do not have.
4. **Build the collab timezone tool.** Unoccupied slot, you have the problem
   yourself, and it enters you into the peer network as a supplier.
5. **Design memberships as two tiers**, with participation and downloadables at
   the top — copying hololive's actual structure rather than the six-tier
   maximum.
6. **First merch drop is acrylics on a birthday or anniversary**, not plush.
7. **Submit a panel to VeXpo 2026** (Birmingham, September). Panels reward
   expertise over follower count, and this is expertise nobody else has.

---

## 7. Confidence notes

**Measured or primary:** all four Twitch category figures; Fourthwall's fee
table; Patreon's post-August-2025 rate; Makeship's campaign mechanics; the
VShojo collapse; ANYCOLOR's own service description; Vedal's and CodeMiko's
histories; the Industry Awards categories; event dates.

**Secondary but reputable:** Twitch's Plus Program terms; YouTube membership
price floors; Ko-fi Gold pricing.

**Vendor sources — attribute, do not assert:** Makeship's revenue share
(a competitor's claim); all merch campaign averages; Discord conversion bands.

**Excluded as unverifiable:** every "average VTuber earns $X" statistic;
sponsorship rate cards; study-with-me growth data.

**Not applicable until confirmed:** all German legal material, per §0.
