# Handoff — the coming-soon page

**Prepared for:** the implementing developer agent
**Date:** 2026-08-25
**Design system:** Shruti

---

## 0. The mandate

**Implement the design. Do not interpret it.** This one is unusual: `index.html` in this folder is
**already the implementation** — a single self-contained file with no build step, no framework and no
dependencies but Google Fonts. Deploy it, then replace one mock with a real API call (§3).

Do not rebuild it in a framework. Do not "modernise" it. There are four small jobs, listed in §3.

---

## 1. What this page is for

It sits at the domain while the rest of the site is under construction.

**The idea worth protecting:** a holding page that only says *coming soon* gives a visitor nothing
and no reason to come back. So this page **is an instrument on day one**. The centrepiece is a live
station countdown — a real clock, ticking every second — with today in all four reckonings under it.
That is the thesis of the entire site delivered before any other page exists.

The headline says what is true rather than teasing: *The site is being built. The sky is not
waiting.*

**Do not** replace that with "Coming soon", a launch countdown to a date, or a percentage-complete
bar. **Do not** add a splash animation, a mailing-list modal, or a full-screen video.

## 2. Files

```
design_handoff_coming_soon/
├── index.html      ← the deployable page. Self-contained. This is the deliverable.
├── README.md       ← this file
└── INSTRUCTIONS_FOR_DEVELOPER_AGENT.md
```

The design also exists as a Design Component in the design-system repository at
`templates/coming-soon/ComingSoon.dc.html`, with tweaks for theme, phase and preset. That copy is
the **design source of truth** if you need to check intent; `index.html` here is the deploy artifact
and the two are the same design.

`index.html` opens straight from disk — no server needed to review it.

## 3. The four jobs

**1. Plug in real station times.** The `S` array at the bottom of `index.html` holds four Athens
times as placeholders. Replace it with a fetch of `GET /stations/next` (or `/stations` for the day)
and geolocate the visitor if they allow it, falling back to Athens. **The countdown maths is already
real** — it needs correct inputs, not new logic.

**2. Wire the subscribe form.** It posts to `/newsletter/subscribe` and already degrades without
JavaScript. The double opt-in is **mandatory** — the confirmation email exists at
`email/optin-confirm.html` in the design system. Nobody joins a list before clicking the link, and
the page says so.

**3. Fill in the real links.** The five pills (Twitch, YouTube, Bluesky, Discord, the code) and the
four language links are `href="#"`. The language switcher can be dropped entirely if only English
ships at first — better than four links that go nowhere.

**4. Reckonings.** Gregorian is computed live. Attic, Hindu and Thelemic are static strings; point
them at `GET /today`, which already returns all of them. If that is not ready, **leave the static
values and set them per deploy** — a wrong date is worse than a stale one.

## 4. Things that are deliberate

- **The status pill reads "offline · building"**, not "live". Change it to reflect reality, or wire
  it to the stream API. Never leave it saying live when she is not.
- **The fine print under the reckonings names the rule used** — ephemeris, amānta, and the sunrise
  definition. The whole brand rests on stating which reckoning produced a number. Keep it.
- **Consent copy names the commercial intent** ("the occasional paid thing") at the point of
  collection. This is a legal position, not a tone choice. Do not soften it.
- **Imprint values are bracketed placeholders** — `[street, no.]`, GEMI, VAT — pending company
  registration. **Ship the brackets.** The client fills them in. Do not invent them, and do not
  delete the block: it is a Greek legal requirement once trading.
- **`noindex` is set.** Remove it when the real site launches, not before.
- **Dawn and dusk both work**, following the visitor's OS. Stars appear only at dusk. There is no
  theme switch on this page on purpose — one control on a holding page is one too many.
- **No artwork.** None is commissioned yet, and the page is designed to look finished without it.
  Do not add stock art or an AI-generated portrait.

## 5. What counts as done

- Deployed at the domain, loading in under a second on a phone.
- The countdown ticks and is correct for the visitor's location, or honestly labelled Athens.
- Subscribing sends the confirmation email and adds nobody before it is clicked.
- Every link goes somewhere real, or is removed.
- Dawn and dusk both look deliberate; the page reads at 320px wide.
- The imprint block is present, with its placeholders intact.

## 6. When the site launches

This page comes down; nothing here needs migrating. The design it previews is already built in the
design system — the real `/today` page (`ui_kits/site/Today.jsx`) is the fuller version of the
instrument this page teases.
