# Counting how much the site is used

Live since 2026-08-25. First-party, cookieless, no third party anywhere in it.

She asked for two things: how much each tool gets used, and how people move
through the site. This answers both without holding personal data, which is
what lets it run without a consent banner.

## What a visitor is

A visitor is `sha256(secret | date | address | user-agent)[:32]`.

Three properties follow from that, and they are the whole design:

- **The address is never stored.** It goes into the hash and stops. It is not
  in a column, an export or a backup.
- **The hash does not run backwards**, and no table maps numbers to people.
- **The date is inside it**, so the number changes at midnight. The same person
  on Tuesday and Wednesday are two numbers. Following anybody across days is
  not declined here — it cannot be done, including by whoever holds the
  database.

That last point is the one that costs something. "Visitors this month" is not
available and never will be; `byDay.visitors` is per-day and must not be summed.
The dashboard says so on the page, because a number whose meaning is hidden gets
read as a different number.

## The pieces

| Where | What |
|---|---|
| `backend/shruti/models/__init__.py` | `Visit` — day, path, event, props, visitor, referrer |
| `backend/alembic/versions/c48e1f7b3d05_visits.py` | the table |
| `backend/shruti/api/routes/insight.py` | `POST /beacon`, `GET /summary`, `GET /journeys`, `DELETE /all` |
| `frontend/site/src/components/insight/Beacon.astro` | mounted once in `BaseLayout`, and again in `coming-soon.astro` |
| `frontend/site/src/components/insight/CountingChoice.astro` | the switch, on `/privacy#counting` |
| `frontend/site/src/pages/admin/insight.astro` | the dashboard, linked from the bar as **Use** |
| `backend/tests/test_insight.py` | 12 tests: no cookie, no address stored, hash rotates, robots ignored |
| `backend/tests/test_counting_is_wired.py` | every tool reports itself; the beacon is mounted; a refusal is read first |

## Adding a tool

Put this on whatever the visitor presses to make it compute:

```html
data-track="tool:used" data-track-tool="<slug>"
```

One delegated listener in `Beacon.astro` picks it up — nothing to wire.
`test_counting_is_wired.py` fails if a new page under `pages/tools/` forgets,
because a forgotten tool reads as an unused tool, which is the most misleading
answer a usage figure can give.

**Never put anything the visitor typed into `data-track-tool` or props.**
Which tool, not what they asked it.

## Refusing

Honoured before the first beacon, in this order: Global Privacy Control, Do Not
Track, then `localStorage.shruti_counting === "no"` (the switch). None are
legally required of this site. All are obeyed.

A browser-level refusal disables the switch rather than appearing to override
it — offering a button that seems to turn counting back on while the browser
still says no would be a lie in the other direction.

## Things that will bite

- **The holding page is counted too**, and records the path the visitor asked
  for rather than `/coming-soon`, because the middleware rewrites rather than
  redirects. While the holding page is up this is nearly every row.
- **Form submits produce a second pageview.** A tool whose button submits shows
  roughly twice the pageviews of one whose button does not. Compare tools by
  `tool:used`, not by pageviews.
- **`seed_legal.py --force` overwrites her edits** to the privacy and terms
  sections. Check `updated_at` before running it; if the timestamps differ from
  the original seed, she has edited something and `--force` will destroy it.
- **The prod backend runs from a built image**, so `git pull` alone does not
  give `alembic` a new migration. Build, `up -d`, then `alembic upgrade head` —
  in that order, or alembic reports the old head and nothing looks wrong.
- **Playwright's `extraHTTPHeaders.cookie` is dropped** once the site sets a
  cookie of its own, so a probe silently falls back behind the holding page
  from the second navigation onwards. Use `context.addCookies()`. This cost an
  hour and looked exactly like a beacon bug.

## Not done

- No retention limit. Rows accumulate. A day older than N could be collapsed to
  counts, but at this volume there is nothing to solve yet.
- The dashboard reads every row in the window into Python and counts there.
  Fine at this size; if it stops being fine, it becomes `GROUP BY`.
