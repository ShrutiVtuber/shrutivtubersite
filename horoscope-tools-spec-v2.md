# Horoscope Writing & Presentation Toolset — Implementation Brief

**Site:** shrutivtuber.com
**Deliverable:** a self-contained page (and embeddable widget) on shrutivtuber.com providing a rotatable, steppable transit wheel plus an event-table generator, usable both as a live-stream production tool and as a public, SEO-visible reader tool. It sits alongside the astrology tools already on the site and should link to and from them.

**Licence:** code is AGPL-3.0-or-later. See §12 — this is a hard constraint that shapes the architecture, not an afterthought.

**Version 2.** All decisions previously left open have been settled; they are recorded in §11 with the reasoning, so nothing in this document needs a follow-up conversation before work starts.

---

## 1. Brief for the implementing agent

Build a whole-sign transit wheel and horoscope-authoring toolset as its own page on shrutivtuber.com. The tool has two audiences that share one codebase:

1. **The author, on stream and while writing.** She writes annual, monthly, weekly and daily horoscopes for all twelve signs. For each sign she places that sign on the Ascendant and reads the chart from there. She needs to step a wheel forward and backward through time, watch the planets move, flip between the twelve sign-rotations instantly, and pull out an exact list of every ingress, station, lunation, eclipse and aspect perfection in the period she is writing about. The same wheel is shown live on stream via OBS.

2. **The reader, on the public site.** They land on a published horoscope, see the same wheel, and everything — the wheel, the event list, and the timing statements inside the horoscope text — renders in *their* timezone, not the author's.

All astronomical computation happens in Universal Time. Local time exists only at the presentation layer. There is no birth data and no birth location involved anywhere in this tool.

**A recurring principle, stated once here because it governs many requirements below:** the practice is Hellenistic, so traditional methods are the defaults. But the tool is public and many visitors will have learned modern astrology. Wherever the two traditions disagree, both must be implemented, the traditional one is the default, the active choice is visible on screen, and switching must never require a page reload or lose the current view state.

---

## 2. Astrological model — read this before writing any code

These are not stylistic preferences. Getting them wrong makes the tool useless.

### 2.1 The wheel is a whole-sign, sign-rotated transit wheel

- **Zodiac:** tropical.
- **House system:** whole sign only. One sign = one house. No quadrant houses, no cusps inside signs.
- **No computed Ascendant or Midheaven in the default view.** The "Ascendant" here is a *chosen* sign, not a calculated degree. The UI must never display a degree of the Ascendant or MC by default, and must never imply this is a natal chart.
- **Rotation:** the selected sign occupies the 1st house sector, drawn at the 9 o'clock position (left, where the Ascendant conventionally sits). The remaining signs follow anticlockwise in zodiacal order.
- **Rotation is presentation-only.** Planetary longitudes do not change when the user switches signs. Only the house assignment changes: `house = ((planet_sign_index - ascendant_sign_index) mod 12) + 1`. Compute positions once per instant; derive all twelve rotations from that single computation. Switching signs must be instant, with no recomputation and no network call.
- **Reference location** (see §2.7): when one is active, the tool may additionally show a real Ascendant/MC as an optional overlay, clearly labelled and off by default.

### 2.2 Bodies and points

**Default set** — always shown, visually dominant:

- Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn (the seven traditional planets)
- True Node and Mean Node (toggle between them, default True)

**Optional, toggleable, off by default:**

- **Uranus, Neptune, Pluto.** Off by default because the tradition the columns are written from works with the visible seven, and because dignity, sect and rulership have no place for them. But the toggle must be prominent and its state must persist across sessions and be encodable in a share URL — a modern-trained visitor should be able to switch them on once and have the tool stay that way. When outers are enabled they participate in aspects and are listed in the data table, but they are excluded from all dignity, sect, triplicity, bound and decan calculations, and the UI should say so rather than showing blank cells.
- Chiron
- The Hermetic lots beyond Fortune and Spirit (Eros, Necessity, Courage, Victory, Nemesis)
- Selected fixed stars with proper motion (Regulus, Spica, Aldebaran, Antares, Algol, Sirius) — computed, not hardcoded
- Syzygy (the lunation preceding the displayed instant)

**Lots of Fortune and Spirit:** these need the Ascendant degree and the sect, neither of which exists without a location. When a reference location is active (§2.7) compute them properly. When none is active, compute a *whole-sign* Fortune from the chosen Ascendant sign at 0°, labelled explicitly as a sign-level approximation. Never silently substitute 0° Aries.

### 2.3 Essential dignity

Computed per planet per instant, for the seven traditional planets only:

- Domicile and detriment
- Exaltation and fall
- **Triplicity:** Dorothean, with day and night rulers — depends on sect, see §2.7
- **Bounds/terms:** **Egyptian by default**, with a working Egyptian ⇄ Ptolemaic toggle. Both tables must be data-driven (a JSON table, not code), so a third table can be added later without touching logic. The active table is named in the UI wherever a bound ruler is displayed.
- **Decans/faces:** Chaldean order

### 2.4 Planetary condition

- Retrograde / direct / stationary. Station detection by sign change of longitude speed, refined by root-finding to ±1 second.
- Daily motion in degrees, with fast/slow relative to mean motion.
- **Solar phase:** cazimi (within 17′ by default), combust (within 8°), under the beams (within 15°). All three thresholds configurable in settings, with a choice between longitude-only and true-distance (latitude-inclusive) measurement.
- Oriental / occidental of the Sun.
- **Phasis:** flag any planet making a heliacal rising or setting, or first/last visibility, within ±7 days of the displayed instant. Requires a latitude — see §2.7.
- Accidental placement: whole-sign house for the current rotation, and angular / succedent / cadent.

### 2.5 Aspects

Two modes, both required, switchable without losing view state:

- **Whole-sign aspect mode** (default): signs configured by the classical scheme. Aversion is a first-class concept — mark the 2nd, 6th, 8th and 12th from the selected sign visibly, since a planet there cannot see the Ascendant sign and that materially changes what gets written.
- **Degree-based mode:** Ptolemaic aspects with configurable orbs, supporting both fixed orbs and moiety-based orbs. Show applying vs separating, exact perfection time in UT, and degrees to perfection.

Minor/harmonic aspects and antiscia: optional toggles, off by default. If a modern user enables minor aspects, they appear only in degree-based mode.

### 2.6 Lunar specifics

- Phase with an accurate illuminated-fraction glyph computed from elongation, not a stock icon set.
- **Void of course**, switchable:
  - **Traditional (default):** the Moon perfects no exact Ptolemaic aspect to any of the other six traditional planets before leaving its current sign.
  - **Modern:** last exact aspect to any enabled body, outers included.
  - The active definition is labelled on screen next to every VOC readout, and the label is not truncated on mobile. The two definitions frequently disagree, and without the label users will report it as a bug.
  - Both definitions must be computable simultaneously so the author's event table can show where they diverge.
- Moon's sign transits with entry and exit timestamps in UT and the whole-sign house for the current rotation.

### 2.7 Sect and reference location

Sect (diurnal vs nocturnal) depends on whether the Sun is above or below the horizon, which needs a place. For a global horoscope no such place exists — at any instant it is day somewhere and night elsewhere. Resolve it with an explicit, visible chain:

**Resolution order for the reference location:**

1. A location the user has explicitly set (city search with a geocoder, or manual latitude/longitude entry).
2. If none, an approximate location derived from the user's IANA timezone. The tz database's `zone1970.tab` carries a representative coordinate for every zone; use it. Label the result as approximate and derived from the timezone.
3. If none, the **default: Greenwich (51.4779° N, 0° E)**, matching the UT anchor.

The location control sits next to the timezone control and behaves the same way: auto-detected, overridable, persisted, and encoded in the share URL.

**A gotcha that must be handled, not ignored.** Sect determines the triplicity rulers, and it changes the reading of benefic and malefic placements. If sect follows the reader's own location, then two readers of the same article can see different triplicity rulers — and the text the author wrote may contradict what one of them sees on the wheel.

Therefore:

- Every published horoscope stores the **authoring reference location and the resulting sect** as part of its immutable metadata, alongside the UT period anchor.
- On an article page, dignity and sect readouts are computed from the **authored** reference by default, so the wheel always agrees with the prose.
- The reader may still switch to their own location, but doing so on an article page raises a small, non-modal notice: the sect has changed relative to how the horoscope was written, and some dignity readouts will differ. Wording should be plain, not alarming.
- On the free-standing tool page (`/wheel`) there is no authored text to contradict, so the reader's own location is used without any notice.

### 2.8 Events the engine must detect

For any requested date range, produce a complete, exact list of:

- Sign ingresses for every enabled body
- Stations, retrograde and direct
- Lunations: new, first quarter, full, last quarter
- Eclipses, solar and lunar, with type, magnitude, sign and degree
- Aspect perfections between enabled bodies
- Void-of-course windows, computed under both definitions
- Cazimi, combustion and under-the-beams entry and exit
- Heliacal phenomena, when a reference latitude is available
- Solar ingresses into the cardinal signs, and the **Aries ingress** flagged specially (see §3.3)

All timestamps in UTC to second precision, found by root-finding (Brent or bisection on the relevant angular function), never by sampling at fixed intervals and taking the nearest hit.

---

## 3. Time model — the single most important non-negotiable

### 3.1 Internal representation

- The canonical instant is a **Julian Day in Universal Time**, or equivalently a UTC instant stored as ISO-8601 with `Z`. Never store a naive local datetime anywhere — not in the database, not in URLs, not in JSON payloads, not in cache keys.
- Delta-T handling belongs to the ephemeris library; do not hand-roll it.
- The UT1/UTC distinction is sub-second and can be ignored, but note the assumption in a code comment.

### 3.2 Presentation

- Detect the reader's zone with `Intl.DateTimeFormat().resolvedOptions().timeZone`; allow override from a searchable IANA zone list; persist in `localStorage` and encode in the URL so a shared link carries it.
- Convert using a real tz database (Temporal where available, otherwise Luxon). **Never** fixed UTC offsets — DST rules change and historical rules differ.
- A "show UT" toggle displaying both zones side by side, for use on stream.
- Every timestamp renders through one shared formatting function. No ad-hoc date formatting anywhere in the codebase.

### 3.3 Period boundaries

Every published horoscope is anchored to a **UT period** with explicit UTC start and end instants. That anchor is immutable and is what the URL identifies.

- The reader sees the period rendered in their zone, which may appear as e.g. "Mon 15 Sep 09:00 – Tue 16 Sep 09:00" at UTC+9. Display an explicit local range rather than a bare weekday name whenever the local rendering does not align to local midnight.
- Reader preference: *anchor to UT dates* (default) or *anchor to my local dates* (the tool selects the UT period whose midpoint falls in the reader's local day), with a one-sentence explanation.
- Events falling within one hour of a period boundary are flagged in the author's event table, because they land in a different period for some readers.

**Weeks: ISO-8601 by default** — Monday start, week 1 contains the first Thursday, IDs like `2026-W38`. A **Sunday-start option** is required for US visitors. This is not a cosmetic switch:

- The ISO week ID is the URL and the database key. It does not change with the display preference. Sunday-start is a *rendering* choice: the same underlying week is displayed shifted, with its date range shown explicitly so there is no ambiguity about which seven days are covered.
- Do not generate a parallel set of Sunday-anchored articles. One article, two ways of labelling its span.
- The preference persists and is encoded in the URL.

**Months:** calendar months in UT.

**Years: calendar years in UT** for publishing and URLs, because that is what people search for and when they search for it. But the astrological year does not begin on 1 January, and the tool should make that visible rather than hide it:

- The **Aries ingress** is flagged as a distinct event type, rendered prominently on the annual wheel and timeline.
- Every annual horoscope page carries a short standing note, authored once and reused, explaining that the solar year turns at the equinox and that January and February belong to the cycle that began the previous March. The exact wording is the author's; the system just needs a place to put it and to render the ingress date through the normal token mechanism so it localizes.
- The annual event table is generated for the calendar year but **additionally marks** which events fall before the Aries ingress, so the author can structure the column accordingly.
- Build in support for an alternative annual anchor (ingress-to-ingress) as a period type, even if it is not used at launch — it is a small amount of work now and a rewrite later.

### 3.4 The horoscope text itself must be timezone-aware

This is the requirement most likely to be missed. The prose has to shift with the reader.

- Horoscope bodies are stored as Markdown with an **inline token syntax**, resolved at render time against the reader's zone.
- Required tokens:
  - `{{event:<event_id>}}` — localized date and time of a computed event
  - `{{event:<event_id>|date}}` / `|time` / `|weekday` / `|relative` — format variants
  - `{{instant:2026-09-15T18:42:00Z|long}}` — an arbitrary UT instant, localized
  - `{{range:<event_a>..<event_b>}}` — a window, e.g. a void-of-course period
  - `{{daypart:<event_id>}}` — "in the morning" / "in the afternoon" / "in the evening" / "overnight", computed from the reader's local clock
  - `{{tz}}` — the reader's zone name, for "all times shown in {{tz}}"
- The author editor provides insert-token controls from the event table, and a lint pass that warns on any hardcoded weekday name, clock time, or phrase like "tonight" or "this morning" in the body text.
- If a token's localized value falls outside the horoscope's own period for a given reader, render the full date and add a subtle marker.
- Unresolvable tokens render a visible placeholder in preview and fail the publish check — never silently empty.

---

## 4. The wheel component

### 4.1 Rendering

- **SVG** in the DOM (not canvas), so it is inspectable, styleable, exportable and accessible.
- Packaged as a **framework-agnostic custom element** (`<transit-wheel>`), droppable into any page of shrutivtuber.com and into the embed widget without dragging in a framework.
- Responsive: legible at 360px wide and at 1920×1080 as a stream source, from one implementation via viewBox scaling.
- Rings, outside in: sign ring with glyphs and boundaries → optional degree ring (5° ticks, 10° labels) → optional bounds/decan ring, honouring the active bounds table → planet ring with glyphs, degree/minute labels and retrograde markers → aspect lines in the centre → optional inner data panel.
- Deterministic collision handling for close planet glyphs: spread along the ring with leader lines to true positions, with no jitter while stepping.
- House numbers 1–12 in the sectors, recalculated on rotation.
- The selected sign's ruler is highlighted and its house called out prominently — the single most useful readout for writing a column.
- Signs in aversion to the selected sign are visually marked.
- Themes: light, dark, high-contrast stream. Colours from CSS custom properties only.

### 4.2 Time stepping

- Steps of ±1 minute, hour, day, week, month, year, plus a configurable custom step.
- A scrubber across the period with clickable event markers that jump to the exact instant.
- Play/pause animation with speed control and looping over the current period.
- **Keyboard:** left/right = ±1 step, shift+arrow = ±1 larger unit, space = play/pause, a documented scheme for jumping to signs 1–12, `t` = now, `u` = toggle UT. These are used live, so they must work without focus fiddling and appear in an on-screen help overlay.
- **Trails:** optional ghosting across the stepped range with opacity falloff, for showing movement rather than snapshots.
- **Snap-to-event:** next/previous event controls that jump to exact perfection instants.
- Stepping must feel instantaneous: recompute and repaint within one animation frame (≤16 ms) on a mid-range laptop. Precompute the visible range into a typed-array cache, run the ephemeris in a Web Worker, never block the main thread.

### 4.3 Sign rotation UI

- Twelve tabs plus a click target on each sign sector.
- The current selection is unmistakable — this is where mistakes happen on stream.
- **Grid mode:** all twelve rotations as mini-wheels in a 4×3 grid, for scanning before writing a full set of columns; clicking one opens it full size.
- **Diff readout:** a compact table of every enabled body with sign, degree, speed, condition, dignity and whole-sign house for the current rotation.

### 4.4 Stream mode

- `?mode=stream` renders the wheel alone: no site chrome, transparent or chroma-key background (configurable colour), enlarged typography, optional lower-third strip showing the current UT instant and selected sign.
- Full state in the URL so OBS browser-source scenes can open directly to a given date, sign and option set.
- Optional companion control surface at `?mode=control`, driving the display window via `BroadcastChannel`, so the wheel can be stepped from a second monitor without the control UI being on camera.
- Must render correctly in OBS's embedded Chromium with transparency enabled.

### 4.5 Accessibility

- The wheel is never the only representation: an equivalent data table is always present, visible or toggleable, and is what screen readers announce. `aria-hidden` on decorative SVG, meaningful labels elsewhere.
- Full keyboard operation, visible focus rings, logical tab order.
- Respect `prefers-reduced-motion`: trails and animation off by default, manual stepping retained.
- No information by colour alone — retrograde, applying/separating and dignity each need a glyph or text marker.
- WCAG 2.2 AA contrast in all themes except the stream theme, which may opt out with a note.

---

## 5. The event table / writing desk (author-facing)

A protected area of the same page, behind authentication.

- Choose period type (year / month / week / day), period, and sign rotation; generate the complete event list from §2.8.
- Columns: UT timestamp, author-local timestamp, event type, bodies, sign and degree, whole-sign house for the current rotation, and a one-click "insert token" dropping the matching `{{event:...}}` into the draft.
- Filter by event type, body, or house.
- Divergence markers: events where the two VOC definitions disagree, events within an hour of a period boundary, and (on annual tables) events before the Aries ingress.
- **Split view:** wheel left; event table and Markdown editor right; live preview switchable between "as UT", "as my zone" and "as a reader in Tokyo / New York / Sydney" for proofreading.
- **Twelve-up drafting:** one screen holding twelve drafts for a period, with shared intro/outro fields and per-sign bodies.
- Draft → review → publish workflow with autosave, revision history, and scheduled publication (scheduled in UT).
- Publish-time validation: no unresolved tokens, no hardcoded time expressions, all twelve signs present, period anchor set, authoring reference location and sect recorded, slug and metadata complete.
- Export the event table as CSV, JSON and Markdown; export the wheel as PNG (2× and 4×) and SVG.

**No third-party interpretive text anywhere in this system.** Any keyword or significations library is authored by the site owner, stored as content separate from the code, and licensed separately from the AGPL code. Do not import, scrape, or embed interpretation text from any astrology software, book, or website. See §12.2.

---

## 6. Reader-facing pages and traffic

- Routes, stable and human-readable:
  - `/horoscopes/<sign>/<period-type>/<period-id>` — e.g. `/horoscopes/aries/weekly/2026-W38`, `/horoscopes/scorpio/daily/2026-09-15`, `/horoscopes/leo/annual/2026`
  - `/wheel` — the standalone interactive tool, all state in query parameters
- Server-side rendered or statically pre-rendered so content is indexable; the wheel hydrates progressively and the page is readable and useful before JavaScript loads (server-rendered SVG for the anchor instant, then interactive).
- **On an article page the wheel is locked to the horoscope's anchor instant**, so the wheel always agrees with the prose. A prominent, clearly-labelled control opens the same moment, sign and option set in `/wheel`, where the reader can step freely. That link carries full state in the URL and is one of the main paths from article traffic into the interactive tool and the rest of the site's tools.
- Canonical URLs, `sitemap.xml` covering all published periods, `Article` structured data with `datePublished`, per-page OG/Twitter cards.
- **Dynamic OG image endpoint** rendering the wheel for that sign and period as a PNG.
- Cross-linking: each horoscope links to the other eleven signs for the same period, to adjacent periods, and to the existing astrology tools on shrutivtuber.com.
- **Embeddable widget:** `/embed/wheel?...` in an iframe, with a copy-paste snippet, an oEmbed endpoint, and required attribution back to shrutivtuber.com. Other astrologers embedding the wheel is the highest-value backlink source here.
- RSS/JSON feed per sign and per period type.
- i18n-ready from the start (English and Greek at minimum): externalized strings, `hreflang`, locale-aware date formatting. Glyphs are language-neutral; sign and planet names are not.

---

## 7. Architecture

### 7.1 Ephemeris engine

- **Swiss Ephemeris.** WebAssembly build client-side in a Web Worker for interactive stepping, so scrubbing costs no round-trips and no server CPU.
- Server-side, the same library (pyswisseph or the C library via FFI, matching the existing stack) for pre-rendered pages, OG images and the event cache.
- **Both sides must agree.** A shared fixture of instants and expected positions runs against both in CI; divergence beyond 1 arcsecond fails the build.
- Fall back to the built-in Moshier ephemeris if a data file is missing, and surface that fallback in a debug readout rather than silently degrading precision.

### 7.2 Date range

Operational range: **1 January of the previous calendar year through five years ahead**, rolling, extended automatically by the build rather than hardcoded. This is a forecasting tool, not a natal one; historical depth is not needed here.

Two implementation notes:

- Swiss Ephemeris data files are segmented in 600-year blocks, so restricting the operational range does **not** proportionally reduce the download — the practical minimum is one block covering the present era. The real saving from a narrow range is in the size of the precomputed event cache (§7.3) and in build time, which is where it should be optimised.
- Requests outside the operational range must fail gracefully with a clear message, not silently clamp to the boundary or render a wrong chart. If a natal feature is ever added it will need a wider range and its own data files; keep the range a configuration value, not a constant scattered through the code.

### 7.3 Event cache

Ingresses, stations, lunations and eclipses are identical for every reader — compute them once.

- A build-time or nightly job precomputes all events from §2.8 across the operational range into a static JSON or SQLite artifact keyed by UTC instant.
- Event IDs must be **stable and content-derived** (a hash of event type + bodies + rounded UTC instant), because published horoscope text references them by ID. A recomputation that changes IDs breaks published articles — add a CI check that no published article's referenced IDs have disappeared.
- Aspect perfections between fast bodies are numerous; generate those on demand client-side rather than caching them all.

### 7.4 State and URLs

Every meaningful piece of state lives in the query string: instant, sign, timezone, reference location, enabled bodies, aspect mode, orb set, bounds table, VOC definition, week start, theme, mode. Deep links must reproduce a view exactly. Keep parameter names short and documented, and version the parameter schema so old links keep working.

### 7.5 Data protection

No birth data and no accounts for readers. The reference location is optional, client-side, and never transmitted or stored server-side unless the user explicitly saves a preference — if a geocoder is used for city search, prefer one that does not log queries, and document the choice. This keeps the tool essentially outside personal-data handling. Any future feature that stores a user's location or birth data triggers GDPR obligations (lawful basis, retention, subject access); flag it rather than quietly adding it.

---

## 8. Accuracy and testing requirements

- Golden-file tests: planetary longitudes at fixed instants across the operational range, matched to published Swiss Ephemeris values to 1 arcsecond.
- Event-detection tests: known ingress, station, lunation and eclipse timestamps matched to within 1 second.
- Rotation tests: for every sign and a set of instants, assert the whole-sign house of every body.
- Dignity tests: bound rulers asserted against both the Egyptian and Ptolemaic tables at degrees near table boundaries; triplicity rulers asserted for both sects.
- VOC tests: at least ten instants where the traditional and modern definitions disagree, asserting both.
- Timezone tests including a DST spring-forward gap, a fall-back repeated hour, a historical offset change, a half-hour zone (Kolkata), a 45-minute zone (Kathmandu), a recently changed DST rule (Cairo, Santiago), and the antimeridian (Kiritimati, Samoa).
- Boundary tests: events at 23:59 UT and 00:01 UT rendered for readers at UTC−11 and UTC+14.
- Week-labelling tests: the same ISO week rendered Monday-start and Sunday-start resolves to the same article and the same UT span.
- Token-rendering snapshot tests across at least six representative zones.
- Visual regression on the wheel SVG at three viewport widths and all themes.
- CI performance budget: step-to-repaint under 16 ms, first contentful paint under 1.5 s throttled, wheel bundle under 150 KB gzipped excluding ephemeris data.

---

## 9. Acceptance criteria

1. Selecting any of the twelve signs re-rotates the wheel instantly with correct whole-sign house assignments, with no network request and no recomputation of positions.
2. Arrow-key stepping moves the wheel by one day and repaints within one frame, with trails enabled.
3. A stream-mode URL opens with transparent background, no site chrome, and the exact date, sign and options encoded in the link, and renders correctly as an OBS browser source.
4. Toggling outer planets, bounds table, VOC definition, aspect mode and week start each takes effect immediately, is labelled on screen, persists across sessions, and survives being shared as a URL.
5. Generating a weekly event table for a given ISO week produces every ingress, station, lunation, eclipse, VOC window and aspect perfection in that week, with UT timestamps matching reference values to the second.
6. A horoscope authored with tokens, viewed by readers set to UTC, Asia/Tokyo, America/Los_Angeles and Pacific/Kiritimati, displays correct localized dates, times and time-of-day phrases in all four, with no hardcoded time expressions surviving the lint pass.
7. On an article page the wheel is locked to the anchored instant, and the "open in tool" link reproduces that exact view in `/wheel`.
8. Changing the reference location on an article page raises the sect-divergence notice; doing the same on `/wheel` does not.
9. A published horoscope page is fully readable and shows a correct static wheel with JavaScript disabled.
10. The public page passes WCAG 2.2 AA, is fully keyboard-operable, and exposes an equivalent data table to screen readers.
11. The embed widget renders in a third-party page with attribution and correct timezone detection.
12. Client and server ephemeris implementations agree within 1 arcsecond across the full test fixture.
13. The AGPL source-offer link is present in the UI and resolves to the complete corresponding source of the deployed version.

---

## 10. Suggested phasing

1. **Engine.** Swiss Ephemeris both sides, positions, dignity tables, conditions, aspects, event detection, test fixtures green.
2. **Wheel.** SVG custom element, rotation, glyph collision, themes, data table equivalent.
3. **Stepping.** Worker, cache, keyboard, scrubber, trails, snap-to-event.
4. **Time layer.** Timezone and location detection and override, token syntax, renderer, boundary handling, full timezone test suite.
5. **Writing desk.** Event table, split-view editor, twelve-up drafting, validation, publishing.
6. **Public pages.** Routing, SSR/prerender, locked article wheel, structured data, OG images, feeds, cross-linking to existing site tools.
7. **Stream mode and embed.** Chroma key, control surface, iframe widget, oEmbed.
8. **Polish.** i18n, performance budget, visual regression, accessibility audit.

---

## 11. Confirmed decisions

Recorded with reasoning so they are not reopened mid-build.

| # | Decision | Setting |
|---|---|---|
| 1 | Outer planets | Off by default, toggle available, persisted and shareable. Excluded from dignity and sect calculations even when enabled. |
| 2 | Bounds table | Egyptian default, Ptolemaic toggle, both data-driven, active table always named on screen. |
| 3 | Void of course | Traditional default, modern toggle, active definition always labelled, both computable at once for the author's table. |
| 4 | Annual anchor | Calendar year for publishing and URLs. Aries ingress flagged as a distinct event, marked on annual wheels and event tables, with a standing explanatory note on annual pages. Ingress-to-ingress supported as a period type for later use. |
| 5 | Week start | ISO/Monday default for keys and URLs; Sunday-start as a display preference only, never a second set of articles. |
| 6 | Sect / reference location | User-set location first, timezone-derived approximation second, Greenwich default third. Article pages default to the authored reference so wheel and prose agree; switching to reader-local raises a divergence notice. `/wheel` uses reader-local silently. |
| 7 | Date range | Previous calendar year through five years ahead, rolling, configurable. Graceful failure outside the range. |
| 8 | Article wheel | Locked to the anchored instant, with a prominent link opening the same view in `/wheel`. |

---

## 12. Licensing constraints — architectural, not cosmetic

### 12.1 Swiss Ephemeris and AGPL

Swiss Ephemeris is dual-licensed: AGPL, or a paid commercial licence. Releasing this toolset under **AGPL-3.0-or-later** satisfies the free option, which is the intended route. Consequences to design for:

- AGPL §13 applies to network use. Users interacting with the deployed tool over the network must be offered the **complete corresponding source of the running version**. Put a persistent "Source" link in the UI footer and in the embed widget, pointing at a repository tag matching the deployed build, and automate the tag so it cannot drift.
- SPDX headers on every source file; REUSE-compliant repository with a `LICENSES/` directory.
- Dependencies licence-audited in CI; anything incompatible with AGPL is rejected at build time.
- Swiss Ephemeris data files carry their own terms — bundle their licence text alongside them and do not strip attribution.

### 12.2 Keeping the copyleft boundary clean

- Deploy the toolset as a **separately deployable application** with a clear boundary from the rest of shrutivtuber.com: its own repository, its own build, communicating with the main site only over HTTP or as an iframe embed. Do not import AGPL modules directly into the main site codebase.
- **No AGPL code from this project may be linked into any separate, non-AGPL project.** If a shared component is wanted later it must be written independently and licensed permissively from the outset — not extracted from this repository. Keep the repositories, the dependency graphs and the build pipelines separate so this stays obvious rather than relying on anyone's memory.
- **Content is licensed separately from code.** Horoscope text, keyword libraries and significations tables are the author's copyright under whatever terms she chooses, stored outside the code repository (database or a separate content repository) and explicitly excluded from the AGPL grant. Make that separation structural, not a note in a README.
- No interpretive text, glyph sets, chart layouts or data tables copied from commercial astrology software or from third-party websites, whether or not a licence to that software is held. Glyphs must come from an openly licensed font (e.g. an OFL astrological font) or be drawn as original SVG paths, with the source documented.
