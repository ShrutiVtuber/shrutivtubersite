# Charts, wheels, sharing and paper

Live since 2026-08-26. Her five requirements, and where each one landed.

| She asked for | Where it is |
|---|---|
| Wheels in a few places | `components/chart/ChartFigure.astro` — the natal tool, a kept chart, a shared chart, the Today page |
| A wheel **or** a Vedic chart, and **both** Vedic styles | Tradition toggle picks wheel/square; a Figure select picks North or South Indian |
| Look at their chart whenever they want | Owner token; `/account` lists them for account holders |
| PDF with watermarks **not over the chart or any useful information** | `/chart/print/[token]`, marks in the outer margins and footer, measured by `scripts/check-print.sh` |
| A chart on the Today page, keeping the written-out text | `today.astro` — figure drawn for `today.at`, positions list untouched |

## The two tokens

The one thing here not to simplify.

- `owner_token` — how a person gets back to their own chart.
- `share_token` — what they hand to a friend. Minted on request, nulled on
  revoke.

With **one** token, sharing would give away the owner's own way in, and
revoking would lock the owner out along with everybody else. Every test that
shares once would pass.

Neither carries birth data, so the moment stays out of the URL and the browser
history. `_shared_view()` also withholds the **place name** — the one part of a
nativity that cannot be read back out of the drawing.

## The limit that must keep being said out loud

A chart is birth data, drawn. The ascendant gives birth time to within a few
minutes; the planets give the date. Hiding the moment from the link and the
page stops the ordinary case completely and an astrologer not at all.

The share panel says exactly that **before** the link is made. If that copy is
ever trimmed for brevity, the feature starts implying a privacy it does not
have. `test_share_links.py` pins the mechanical parts; the sentence is on you.

## Consent

Birth data for an astrological reading is treated as Article 9
special-category data — the position `Nativity` already took. So:

- Signed in: the consent lives on the account. **Not asked twice** — asking
  twice for the same permission teaches people to click past permissions.
- Signed out: consent is stored on the chart row, verbatim, under
  `CONSENT_VERSION`, using `NATIVITY.wording` — not a paraphrase, or the record
  does not say what the person read.
- No account ⇒ **expires after 365 days**, clock reset on every open. Consent
  that cannot be renewed by asking must not be relied on forever.
- Claiming a chart into an account clears the expiry: there is somebody to ask.

## Conversion, without a wall

Keeping works signed out, in one press. The account is offered because it is
better — a list instead of a link to mind, no expiry, any device — never as a
gate. A chart kept anonymously is **claimed** on sign-up rather than recast, so
"sign up to keep your chart" is not a lie. The newsletter is a link on both
chart pages, deliberately not a second subscribe form: one copy of the consent
handling.

## Paper

A print view, not a server-built PDF. The reason is fonts — a PDF library would
need a typeface with the whole astrological range embedded, and the browser
already has the site's. The figure stays vector and every glyph renders.

`scripts/check-print.sh` measures every readable box in **print** media and
fails if a mark touches one. It also fails if it measures nothing, which is how
this kind of check usually lies.

## Things that will bite

- **`Astro.url` says `localhost` behind Caddy.** Use `SITE_URL` from
  `lib/api.ts`. For a canonical tag this is invisible; for a **share link** it
  produces a link that works for nobody. Now pinned by a test.
- **Hellenistic returns `aspects.configurations`, Vedic returns
  `aspects.drishti`.** Not an inconsistency to smooth over — they are different
  claims. Reading the absent one is `undefined.map`, which was a 500 on every
  Vedic chart for as long as the page existed.
- **South Indian cell centres are only 14, 38, 62, 86.** Two signs were drawn
  at x=50 and x=74, on the grid lines, belonging to no house. Every existing
  test passed: still a square, still unlike North, still fixed against the
  lagna. None asked *where* anything was.
- **The backend and daemon run from built images.** `git pull` does not give
  alembic a new migration and does not give the daemon new drawing code. Build,
  `up -d`, then migrate. `scripts/build-backend.sh` exists for this.
- **Production serves the holding page for `/chart/*`.** Not in the allowlist,
  and correctly so while the site is held — but it means these pages cannot be
  smoke-tested on production until the holding page comes down.
- **Playwright's `extraHTTPHeaders.cookie` is dropped** once the site sets a
  cookie of its own. Use `context.addCookies()`, or every probe silently falls
  behind the holding page from the second navigation.

## Not done

- **Transits on the Today page.** The block exists and the signed-in branch
  renders a placeholder `—`; `signedIn` is hard-coded false in `today.astro`.
  It was never built, rather than switched off. Now that a person can have a
  saved chart, it is buildable.
- A **sidereal wheel** — a Vedic chart drawn round rather than square. Nobody
  asked; some will.
- No sweep of expired ownerless charts. They stop opening at 410 on their own,
  but the rows stay. `ix_saved_chart_expires_at` is there for when that matters.
