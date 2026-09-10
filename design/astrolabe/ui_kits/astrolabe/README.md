# Astrolabe — app UI kit

A recreation of the whole app: six tabs, five pushed screens, a place picker, a full-screen sky
drawer and a bottom sheet, composed from the design system's own components.

| File | What it is |
|---|---|
| `index.html` | **The interactive app.** Pick a tab or a pushed screen, flip any state, switch phone size, change the ruling hour. |
| `artwork.html` | **Where your art goes.** Every drawing the app asks for, at real size, inside the real screen, with a drop target in it — drag a PNG on and the app themes around it. |
| `states.html` | **Every screen in every state, in order** — the addendum's §6 deliverable, as live renders rather than images. |
| `Kit.jsx` | Frame pieces: the scrolling body, the status bar, the provenance block. Not design-system components. |
| `Screens1.jsx` | Home · Sky (Stations, Hours, Coming) |
| `Screens2.jsx` | Chart (form, result) · Letters (Reckoning, Sigil) |
| `Screens3.jsx` | Practice (Read, Mine) · Settings |
| `Screens4.jsx` | One work · Write · Account · Notifications · Licences · Place picker · Sky drawer |
| `App.jsx` | The shell, the phone, and the state switches |
| `States.jsx` | The ordered states document |
| `Artwork.jsx` | The artwork placement document |
| `image-slot.js` | The drop target used by `artwork.html` |
| `data.js` | Sample data |

## The eighteen screens

1 Home · 2 Sky · Stations · 3 Sky · Hours · 4 Sky · Coming · 5 Chart · the form ·
6 Chart · the result · 7 Letters · Reckoning · 8 Letters · Sigil · 9 Practice · Read ·
10 Practice · Mine · 11 Practice · one work · 12 Practice · Write · 13 Settings · 14 Account ·
15 Notifications · 16 Licences · 17 Place picker · 18 Sky drawer

## The states

`live` · `offline` · `loading` · `empty` · `error` · `signedIn` · `member` · `longContent` ·
`missing` (content) · `noBirthTime` · `art` (her drawings present) · `reduceMotion`, plus the
ruling hour and the sunrise convention. Every screen renders in each state that applies to it;
`states.html` is the ordered catalogue.

## ⚠ Sample data, not computation

Positions, hours, stations, phases and isopsephy sums are authored to be realistic and internally
consistent so the layouts can be judged. They are **not** computed. What a developer must
actually write is described in each screen's provenance block and in
`../../guidelines/theme-flutter.md`.

## Sizes

360 × 800 (the common Android size) and 430 × 930 (a large phone), switchable in `index.html`.
Tablet is deliberately out of scope — see the caveat in the root `readme.md`.
