# Design update 01 — what changed since the brief you have

**For:** the design agent
**Date:** 2026-08-24
**Read this instead of re-reading the whole brief.** Everything below is new or
changed since the copy you were sent. Nothing else has moved.

---

## 1. Answer to your question: build the tool page template next

Not the press kit — that one is actively cut, and the reason is worth knowing:
the only indie VTuber press kit we could find renders **nine zeroes** for its
live follower statistics, because the automation breaks and nobody notices. A
sponsor reading nine zeroes concludes the audience is zero. It does more harm
than having no page. Contact is worth building, but it is a form and an
afternoon.

**The tool pages are the site's only real differentiator.** Six pages off one
template, each a working instrument running in the browser:

`planetary hours` · `today in the Attic calendar` · `pañcāṅga` ·
`isopsephy` · `natal chart` · `sigil generator`

They are simultaneously the SEO surface, the return-visit hook, the landing
destination for short-form clips, and a live demonstration of the software she
actually builds. No other VTuber can ship this.

### What the template needs that you could not guess from outside

- **A tradition toggle, as a first-class control.** She practises Hellenistic
  *and* Vedic astrology, and the two genuinely disagree on something as basic as
  when the Sun rises — the Hellenistic definition is the upper limb of the
  visible disc *with* refraction, the Indian one is the centre of the disc
  *without* it. Measured difference in Athens: **4.6 minutes**, which is enough
  to change the answer the tool gives.
  **Neither is the default-correct one.** This is a control the visitor operates,
  not a settings-page preference, and each option needs a one-line explanation
  sitting next to it. The backend already serves both and refuses to merge them.

- **A parameter panel** — location, date and time, and per-tool options. The
  pañcāṅga alone offers six ayanāṁśas, because practitioners disagree and the
  disagreement is legitimate rather than a bug to resolve.

- **A designed "cannot compute" state.** At polar latitudes the Sun does not
  rise, and the tool says so rather than inventing an answer. This state will be
  seen and it must look deliberate, not like a failure.

- **Results that can be linked and shared.** Parameters belong in the URL.

- **A source link, treated as a credibility mark rather than fine print.** These
  tools are AGPL and the licence obliges an offer of source for the running
  version. The developer audience reads "here is the engineering" as the reason
  to trust the astrology — so the link is a feature of the design, not a footer
  obligation.

If you want a second surface after this: **`/work`**, with a real per-project
credit structure (Name · Role · Stack · Licence · Status).

---

## 2. Correction: her practice is three traditions, not one

The brief you have describes Greek theurgy only. That was wrong and would have
led you to a Greek-only visual identity that misrepresents her.

She is a **multi-tradition initiate** — three distinct initiatory lineages held
at once:

- **Hellenic** — Greek theurgy under Hekate; the Attic lunisolar calendar
- **Śākta Tantra** — initiated into the Mahāvidyā; tarpaṇam, mantra japa
- **Thelema** — O.T.O.

Profile rows should therefore read **Traditions (Hellenic · Śākta · Thelemic)**,
not a single tradition and patron.

---

## 3. The design thesis, which the brief did not have

The three traditions converge on one thing, and it is already in her existing
art: **the twilight junctures.**

*Sandhyā* literally means the junctures — dawn and dusk — and is when tarpaṇam
and mantra practice are performed. Greek practice anchors to dawn, dusk and the
lunar stations. Her phone app is built around moonrise, culmination, moonset and
nadir. And `Clouds.png`, independently, is a dusk sky.

So **dawn and dusk are the subject, not the decoration.** The palette sampled
from her own art is not a decorative choice. This also gives light and dark
themes real meaning: the same sky at its two junctures, rather than one inverted
into the other.

---

## 4. The naming is settled — please do not reinterpret it

**Shruti is her real name** (Shruti Swara — it is the name on her OCI card, as
Sophia is the name on her Greek passport). She is part Indian and part Greek, so
the Sanskrit name and the Greek theurgy are not two themes in tension. They are
one person. Lean on it; do not smooth it over.

| Layer | Name | Where |
|---|---|---|
| Person / brand | **Shruti** | Site title, hero, nav, socials, footer |
| Signature | **Soror Eu. A.** | Byline on magickal writing; the About page |
| Product | **Theourgia** | The software, on `/work` and the tool pages |

The motto is a *signature* — a seal at the foot of a page. Never a handle, a
slug, or a second logo.

---

## 5. Two things that are now load-bearing

**Pseudonymity is off.** The avatar is aesthetic, not protective — people
already know both names. So the footer must carry a proper legal imprint (entity
name, a **virtual office** address, role email, company and VAT number). Design
the footer to hold it from day one; retrofitting an imprint is how home
addresses leak.

**Description and Lore need two distinct sections, in two distinct voices.** She
has a genuine practitioner biography *and* a character layer. Conflating them is
exactly what makes occult-adjacent creators read as performance rather than
practice, and keeping them apart is the central craft problem of this brand.

**Restricted material.** She holds initiations that carry real limits on what may
be published. The site needs a visible, consistent content-marking convention
distinguishing public commentary from restricted practice material — designed as
a typographic element, not a badge bolted on. Practitioners read "this person
knows what may not be said" as a credential.
