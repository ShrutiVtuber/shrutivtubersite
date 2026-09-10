# Addendum — the scope is the WHOLE app

Hand this over with `DESIGN-BRIEF-ASTROLABE.md`. That document sets the
direction and asks for one worked screen. **This one replaces its "what done
looks like" section.**

⚠ **Design every screen, every state and every variation listed below.** Not a
direction and a sample. Not "Home plus a component library and we'll extrapolate
the rest". Every surface a user can reach, in every state it can be in, so that
nothing is left to be invented later by somebody who is not a designer.

If something in this list turns out not to be worth designing, say so and why —
but do not silently skip it.

---

## 1. Screens

Every one, at 360×800 (the common Android size) **and** 430×930 (a large phone).
Tablet is out of scope unless you think it should not be, in which case say so.

| # | Screen | Where it is |
|---|---|---|
| 1 | **Home** | first tab |
| 2 | **Sky · Stations** | second tab, first segment |
| 3 | **Sky · Hours** | second tab, second segment |
| 4 | **Sky · Coming** | second tab, third segment |
| 5 | **Chart · the form** | third tab, before casting |
| 6 | **Chart · the result** | third tab, wheel and table |
| 7 | **Letters · Reckoning** | fourth tab, first segment |
| 8 | **Letters · Sigil** | fourth tab, second segment |
| 9 | **Practice · Read** | fifth tab, the feed |
| 10 | **Practice · Mine** | fifth tab, own work |
| 11 | **Practice · one work** | pushed — readings, votes, comments |
| 12 | **Practice · Write** | pushed — the writing screen |
| 13 | **Settings** | sixth tab |
| 14 | **Account** | pushed from Settings |
| 15 | **Notifications** | pushed from Settings |
| 16 | **Licences** | pushed from Settings |
| 17 | **Place picker** | pushed — search and choose a city |
| 18 | **Sky drawer** | a full-screen dialog: the ephemeris as reference |

## 2. States — for every screen above

Draw each screen in each state that applies to it. These are where an app
actually gets judged, and they are the ones that get left as a grey box.

- **Loading** — first open, and refreshing something already on screen.
- **Empty** — no practice submissions, no offers, no saved charts, no language
  packs, nothing written yet.
- **Offline** — ⚠ this app WORKS offline. Every instrument still computes. Only
  her side of it (live status, readings, articles, offers, the practice room)
  is missing. That distinction must be visible: not a dead app, an app whose
  friend is temporarily out of reach.
- **Error** — the site answered badly, a sign-in failed, a pack download broke.
- **Signed out vs signed in** — Practice, Account, Notifications, and offers.
- **Live vs not live** — Home, and anywhere else you decide it should show.
- **Member vs not** — some offers exist only for members.
- **Long content** — a 2,000-word practice reading, a name that is forty
  characters, a stream title that runs on.
- **Missing content** — a reading with no title, an article with no opening, a
  chart with no birth time (⚠ a real state: the angles are then undefined and
  the app says so rather than guessing).

## 3. Components

The system, not just its use. For each: every size, every state
(rest / pressed / focused / disabled / error), and the rule for when to use it.

- bottom navigation (6 tabs) · segmented controls (2 and 3 segments)
- cards — plain, tappable, highlighted (offers), warning
- buttons — filled, outlined, text, icon; and destructive
- chips — choice, filter, and the language chips with a size on them
- text fields — single line, multiline, with helper text, with an error
- switches, checkboxes (the consents), radios (the sunrise convention)
- dialogs — full-screen (the sky drawer) and small (confirm)
- snackbars, the pull-to-refresh indicator, progress
- lists and list rows, section headings ("eyebrows"), dividers
- tables — ⚠ **dense on purpose.** The stations, the hours and the ephemeris
  are reference tables and a practitioner wants a month on one screen. Do not
  make them airy.
- the two **wheels** — the transit wheel (one instant) and the period wheel
  (movement across a span, with the Moon's phase ring)
- the drawn **moon phase disc**, at every size it appears
- code/monospace treatment — the isopsephy tables, the offer codes, the SVG

## 4. The system

- **Colour tokens**, named, with the reason for each. Dark is the default; say
  whether a light theme should exist and design it if so.
- **Type scale** — every size in use, with line height and letter spacing.
  Currently EB Garamond for display and Commissioner for body; change them if
  you have a better pair, but say what it costs (they are shared with the site).
- **Spacing and corner scales.**
- **Elevation / depth** — what is raised, what is inset, what is flat.
- **Motion** — durations and curves for: tab change, segment change, push and
  pop, dialog open, pull to refresh, a vote landing, a draft saving. ⚠ And what
  happens with reduced-motion on.
- **Iconography** — currently Material outlined. Keep, replace, or draw.
- **Focus and touch targets** — every interactive thing, at accessible sizes.

## 5. Artwork she is drawing by hand

⚠ **She draws these herself, so vagueness costs her a redraw.** For each asset
give her:

1. exact pixel dimensions, at which density, and the largest size needed
2. the safe area, and what may be cropped
3. transparent or not, and what sits behind it
4. a paragraph on pose, framing, mood, and how it fits the palette
5. where it appears and how often somebody sees it
6. **whether it is essential or nice to have**, so she can draw in that order

At minimum: the app icon (adaptive — foreground and background layers), the
notification icon (⚠ Android requires a flat white silhouette), the splash, at
least one portrait for Home, the live state, empty-state drawings, and any
motifs or dividers the system uses.

## 6. What to hand back

- A `lib/theme/` the app can adopt without rewriting screens — tokens, text
  styles, component themes.
- **Every screen and state above**, as renders, in a single ordered document.
- The artwork list, in the shape set out in §5.
- A short note on anything you changed from the main brief, and why.

## 7. Things you must not change without saying so

- ⚠ **Colour is never the only signal.** Retrograde is ℞ *and* tinted. This
  holds everywhere, so it survives printing, being read aloud, and being read
  by somebody who cannot tell the colours apart.
- ⚠ **Marks are type, not emoji.** Every glyph carries U+FE0E.
- ⚠ **Nothing takes money inside the app.** Support, shop and classes open her
  own checkout in a browser.
- ⚠ **It works offline**, and the artwork ships in the bundle.
- **AGPL-3.0** — everything ships in a public repo. Fonts must be licensed for
  that. Her drawings are hers; raise the licence question with her explicitly.
