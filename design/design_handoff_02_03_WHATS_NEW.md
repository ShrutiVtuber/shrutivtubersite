# What's new — handoffs 02 and 03

**Read with:** `design_handoff_stations/README.md` (handoff 02) and
`design_handoff_accounts/README.md` (handoff 03). This file is only the manifest — it lists exactly
what was added or changed for those two handoffs, so you can see the delta without diffing.

**Build order:** handoff 02's three pages first (they need no account), then handoff 03.

---

## New components

All carry `.d.ts` prop contracts and `.prompt.md` usage notes alongside the `.jsx`.

| Component | Path | Handoff |
|---|---|---|
| `NextStation` | `components/tables/NextStation.*` | 02 |
| `StationTable` | `components/tables/StationTable.*` | 02 |
| `ExportBlock` | `components/tables/ExportBlock.*` | 02 |
| `ConsentCheckbox` | `components/forms/ConsentCheckbox.*` | 03 |
| `SignPicker` | `components/navigation/SignPicker.*` | 03 |
| `PeriodSwitcher` | `components/navigation/PeriodSwitcher.*` | 03 |
| `SubscribeBlock` | `components/brand/SubscribeBlock.*` | 03 |
| `LegalImprint` | `components/brand/LegalImprint.*` | 03 |

Specimen cards: `components/tables/stations.card.html` (02),
`components/forms/accounts.card.html` (03).

## New pages

| Route | File | Handoff |
|---|---|---|
| `/today` | `ui_kits/site/Today.jsx` | 02 |
| `/tools/solar-stations` | `ui_kits/site/Stations.jsx` (`kind="solar"`) | 02 |
| `/tools/lunar-stations` | `ui_kits/site/Stations.jsx` (`kind="lunar"`) | 02 |
| `/signup`, `/signin` | `ui_kits/site/Auth.jsx` | 03 |
| `/account`, `/nativity` | `ui_kits/site/Account.jsx` | 03 |
| `/horoscopes`, `/horoscopes/<sign>/<period>` | `ui_kits/site/Horoscopes.jsx` | 03 |
| `/newsletter` + confirm · unsubscribed · preferences · archive | `ui_kits/site/Newsletter.jsx` | 03 |

## New emails

| File | What |
|---|---|
| `email/newsletter-issue.html` | The monthly issue. Table-based, dark-mode safe, no images, no tracking pixel. |
| `email/optin-confirm.html` | The mandatory double opt-in confirmation. |

## New foundations

| File | What |
|---|---|
| `tokens/print.css` | Print as a designed medium — Dawn on paper, repeating table headers, no toner-eating washes. Imported by `styles.css`. |
| `.t-glyph` in `tokens/typography.css` | Forces text presentation on glyphs that otherwise resolve to colour emoji. Pair with U+FE0E in the data. |
| `ui_kits/signs.js` | The twelve signs as a plain global, for pages that need the data outside the component bundle. |

## Changed

| File | Change |
|---|---|
| `ui_kits/site/App.jsx` | Routes for all twelve new surfaces; demo toggles for signed in/out, athens/polar, birth time. |
| `ui_kits/site/Chrome.jsx` | `Today` and `Horoscopes` in the nav; Sign in / Account link; station and letter links in the mobile menu and footer; `LegalImprint` in the footer. |
| `ui_kits/site/site.css` | Mobile menu styles, `.acct-link`; fixed `.site-main` padding shorthand that was killing horizontal page padding on every route. |
| `ui_kits/site/index.html` | Loads the new page scripts and `signs.js`. |
| `ui_kits/admin/index.html` | New **Horoscopes** tab — twelve fields, progress count, live preview. |
| `styles.css` | Imports `tokens/print.css`. |
| `tailwind.preset.js` | `module.exports` guarded so it evaluates in a browser context too. |
| `readme.md` | Component index and surface list updated. |

## Reference build

Open `ui_kits/site/index.html`. The demo bar bottom-right drives every new state:

- **signed in / signed out** — the "your sign first" behaviour and the transits block
- **athens / polar** — the no-sunrise states on `/today` and both trackers
- **has birth time / no birth time** — the undefined-angles state on `/today`

## Settled since the packs were written

- The newsletter letter signs **Shruti**. The horoscope readings sign **Soror Eu. A.**
- Imprint values stay bracketed until the company is established; the client supplies them. Ship
  the brackets.
