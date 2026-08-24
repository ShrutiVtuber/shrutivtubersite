# Design handoff 02 — station trackers and Day at a Glance

**For:** the design agent
**Date:** 2026-08-24
**Status:** new pages. Not a revision of anything in the first bundle.

These are **three new surfaces**, and they share a job: give someone a reason to
open the site every day. Everything designed so far is a brochure someone reads
once. These are instruments someone uses.

Please keep the design system exactly as built — tokens, components, Dawn/Dusk
themes, the tradition toggle, the cannot-compute states. Nothing here changes it.

---

## 1. Solar stations · `/tools/solar-stations`

**What it does.** Someone enters a location and a period of up to one month, and
gets the four solar station times for every day in it, exportable to their
calendar.

The four stations are the structural skeleton of a daily rite: **sunrise · noon ·
sunset · midnight**. In Thelemic practice these are the Liber Resh adorations; in
the Hellenic set they are Hekate Phosphoros at dawn, Apollo at noon, Hekate
Enodia at dusk, Persephone at night. The tool computes the *times*; which deity
belongs to which station is a preset the visitor may choose or ignore.

**The page needs:**

- **A location control.** Typed place or "use my location". Show the resolved
  coordinates and timezone back to them — a station table for the wrong city is
  indistinguishable from a right one until someone misses a dawn.
- **A range control**, one day to one month. **The cap is real** — say so in the
  UI rather than silently truncating.
- **The table.** Rows are days, columns are the four stations. This is the
  primary reading and it will be printed, so it needs the same print stylesheet
  care as the chart.
- **The current or next station, called out** at the top. Someone opening this at
  four in the afternoon wants "sunset in 2h 14m" before they want a table.
- **Export, as three distinct things**, because they are not equivalent:
  - `.ics` **download** — a snapshot; it will go stale
  - **Subscribable feed** (`webcal:`) — *this is the one that produces
    notifications*, and it stays correct as the year turns. Make it the
    prominent option
  - **Add to Google Calendar** links per station
- **A preset selector** — Hellenic, Thelemic, or none (times only).

## 2. Lunar stations · `/tools/lunar-stations`

The same page for **moonrise · culmination · moonset · nadir**.

**One difference that must be designed for, not treated as an error:** the Moon
does not rise every day. At any latitude there are days with no moonrise or no
moonset, because the Moon rises roughly fifty minutes later each day and
occasionally skips a civil day entirely. At high latitude whole weeks can lack
one or the other.

A blank cell is wrong. The cell should say **"no moonrise today"** as a designed
state — it is a fact about the sky, not missing data.

Also show the **Moon's phase and age** alongside, since anyone tracking lunar
stations cares about both.

---

## 3. Day at a Glance · `/today`

The page most likely to be someone's daily open. One screen, no scrolling on a
laptop, answering: **what is the sky doing right now, here.**

Six blocks. Suggested weight in that order:

1. **Sun and Moon** — sign and degree of each, right now. The Moon moves visibly
   over a day; the Sun does not. Consider showing the Moon's motion.
2. **Stations** — the solar and lunar station now in force, and the next one with
   a countdown. Links to the two tools above.
3. **Planetary hour — current and next.** Ruler, when it began, when it ends.
   The "next" half is the point: people plan against the coming hour, not the
   present one.
4. **The sky over their location** — the visible chart for here and now.
5. **Transits** — *only if they have a saved nativity*. See the two states below.
6. **Today's date in every reckoning kept** — Gregorian, Attic, Hindu, Thelemic.

### The two states, and the first one matters more

**Without an account**, entering a location gives everything except transits.
**This must be genuinely useful on its own** — if the page is a teaser for
signing up, nobody signs up. The transits block in that state should be a quiet,
honest invitation, not a locked panel with a blur over it.

**With a saved nativity**, the transits block fills in.

### Cannot-compute states, all real

- Polar latitude: no sunrise, so no solar stations and no planetary hours. The
  page still shows Sun, Moon, sky and reckonings.
- No moonrise today (above).
- **No birth time**: transits to the angles and houses are undefined, because the
  ascendant moves a degree every four minutes. Show the planetary transits and
  mark the angular ones undefined. **Never guess a time.**

---

## 4. What I need from you

1. Mockups of the three pages, both themes, mobile and desktop.
2. **The export block** as a component — three routes with different meanings,
   and the subscribable feed given the prominence, since it is the one that
   actually creates the habit.
3. **A station table** that prints well, and reads at a glance on a phone at dawn
   in poor light. Dark theme matters more than usual here.
4. **The "next station" countdown** as a component, reused across all three pages.
5. **The no-moonrise and polar states**, designed rather than empty.
6. **The signed-out transits block** — an invitation, not a paywall.

## 5. What is deliberately not here

No account pages, no newsletter, no horoscopes. Those are coming
(`docs/BACKLOG.md`) but they carry personal-data obligations that are not settled
yet, and these three pages are worth building first because they need no account
at all.
