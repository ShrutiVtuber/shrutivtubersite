# Swara Studio: the API the app builds against

Swara Studio is the Carnatic music school at `https://shrutivtuber.com/carnatic`.
Its web pages, its data and its accounts are served by this repository; the
Flutter app (private repository `swara-studio/app`) is a second client of the
same API, exactly as the Astrolabe and Squirrel Guides apps are.

- **Base URL:** `https://shrutivtuber.com` (production). Locally
  `http://localhost:8200`. Every path below starts with `/api`.
- **Bodies:** JSON. Errors are `{"detail": "<a sentence meant for a person>"}`;
  show `detail` as it is. Where a client must branch, the status code says so
  (401, 403, 404, 409, 413, 428, 429), and a few answers add `"code"`.
- **Times:** ISO 8601 with an offset (`2026-09-26T12:05:00+00:00`).
- **No account is ever required** to read data, use the drone, tuner, tala
  trainer, raga explorer, lessons or player. An account keeps progress,
  settings and songs across devices, and is needed to publish.

## 1. Signing in

The app uses the site's own accounts (`site_user`), the same mechanism as
the other apps: the session the website keeps in its httpOnly cookie is
handed to the app as a **bearer token** and sent as
`Authorization: Bearer <token>` on every call. The cookie always wins when
both are present, so this changes nothing for browsers.

Tokens last 30 days. There is no refresh token: a **401** on any call means
"drop the token and show Sign in".

### 1a. Password

`POST /api/account/signin`

```json
{ "email": "priya@example.com", "password": "…", "bearer": true }
```

200:

```json
{ "ok": true, "signedIn": true, "id": 42, "email": "priya@example.com",
  "displayName": "Priya", "token": "eyJhbGciOi…" }
```

- 401 `that email and password do not match`
- 403 the address has not been confirmed yet (show `detail`; the person
  follows the link in their email, or asks for a new one with
  `POST /api/account/verify/resend {"email": …}`).

Without `"password"` the same endpoint emails a sign-in link, which opens the
**website**; for the app use 1b instead.

Sign-up is `POST /api/account/signup` with `bearer: true` and the consents
from `GET /api/account/consents` (the `account` consent is required). It
answers `{"ok": true, "checkEmail": true}` and gives **no** session until the
address is confirmed.

### 1b. Signing in from the website (QR code or typed code)

A person already signed in on the website opens **Settings → Sign in on the
app** (`/carnatic/settings#app`). The page shows a QR code and an
8-character code. The app scans it or types it, and receives a token.
No password crosses the phone.

**QR payload:** `swarastudio://link?t=<token>`. Accept only the scheme and
host `swarastudio://link`; take `t` as opaque (URL-safe base64, up to 200
characters). Register `swarastudio://link` as a deep link so the phone's
camera app lands in the right place.

**Typed code:** shown as `K7M4-Q9TX`. Alphabet `23456789ABCDEFGHJKMNPQRSTVWXYZ`
(no `0 O 1 I L U`). The server ignores case, spaces, dashes, dots and
underscores, so send what was typed. Enable Submit at 8 symbols.

`POST /api/carnatic/device-link/redeem` (no authentication). Send exactly one
of `token` or `code`.

```json
{ "code": "k7m4 q9tx", "device_name": "Priya's iPhone" }
```

200 (the `access_token` and `token` are the same value):

```json
{ "access_token": "eyJhbGciOi…", "token_type": "bearer", "token": "eyJhbGciOi…",
  "id": 42, "email": "priya@example.com", "displayName": "Priya" }
```

- 400 `{"code": "INVALID_LINK", "detail": "This sign-in code is not valid. Make a new one on the website."}`
  for every reason (unknown, used, expired, replaced, both or neither field).
- 429 `{"code": "TOO_MANY_ATTEMPTS", "detail": "…"}`. Do not retry
  automatically.

Rules: a link lasts **5 minutes**, is used **once**, a person has at most 3
live links (a 4th revokes the oldest), and failed redeems are limited per
client (10 per 10 minutes) and overall for typed codes (100 per 10 minutes).
The server stores only hashes of the token and the code.

Website side (cookie), for reference:

- `POST /api/carnatic/device-link` → 201
  `{ "link_id": 7, "code": "K7M4-Q9TX", "token": "…", "qr_payload": "swarastudio://link?t=…", "expires_at": "…", "expires_in": 300 }`
- `GET /api/carnatic/device-link/{link_id}/status` →
  `{ "status": "pending" | "used" | "expired", "expires_at": "…", "used_at": null }`

### 1c. Who is signed in

`GET /api/account/me` is the site's own profile (email, display name,
consents). For the school, use:

`GET /api/carnatic/me` (optional auth; never 401)

```json
{
  "signedIn": true,
  "displayName": "Priya",
  "limits": { "partsPerSong": 2 },
  "settings": { … see §3 … },
  "settingsUpdatedAt": "2026-09-26T12:00:00+00:00"
}
```

Signed out: `{"signedIn": false, "limits": {"partsPerSong": 2}, "settings": null}`.

`limits.partsPerSong` is `null` when unlimited. **The app shows no prices, no
supporter perks and no purchase links** (App Store and Play rules, and the
design's hard rule 6): when a song is at its limit the app simply does not
offer another part. The web explains the limit; the app does not.

## 2. The school's data (offline download)

The facts (ragas, melakartas, talas, lessons, instruments, gamakas) are a
compilation kept in a private research repository and published to the site
by `scripts/sync-carnatic-data.sh`. The app bundles a copy for the first run
and downloads the published files to stay current. **The published layout
below is the contract**; a bundled copy should be these same files, so the
app reads one shape whether it came from the bundle or the network.

### Asking whether anything changed

`GET /api/carnatic/data/version` → 200

```json
{ "format": 1, "digest": "3aeab04d10dedc6b", "built_at": "2026-09-26T19:18:21+00:00" }
```

The cheapest call: one small object, `ETag: "<digest>"`, `Cache-Control:
no-cache`. Send `If-None-Match: "<digest you hold>"`; **304** means nothing
changed and nothing else needs asking. 404 means nothing is published yet
(keep the bundled data).

### The manifest

`GET /api/carnatic/data/manifest` → 200 (404 as above; `ETag` and 304 as for
`/version`)

```json
{
  "format": 1,
  "digest": "3aeab04d10dedc6b",
  "built_at": "2026-09-26T19:18:21+00:00",
  "research": { "commit": "b7716d1", "uncommitted_changes": false },
  "files": [
    { "name": "ragas.json",       "digest": "0a173ec187ddba2d", "bytes": 475352 },
    { "name": "talas.json",       "digest": "5a29cb333ae126dd", "bytes": 66813 },
    { "name": "lessons.json",     "digest": "04325f015e611924", "bytes": 59752 },
    { "name": "instruments.json", "digest": "6bbc888827518522", "bytes": 64645 },
    { "name": "featured.json",    "digest": "8482c79f55b399f3", "bytes": 15078 },
    { "name": "gamakas.json",     "digest": "a6b384ba04beca6e", "bytes": 5388 }
  ],
  "counts": { "melakartas": 72, "janyas": 62, "performed": 12 },
  "license": "LicenseRef-All-Rights-Reserved (compilation); facts are facts"
}
```

- **`format`** is the layout version. It changes only when a file's shape
  changes in a way an older app cannot read; an app that does not know the
  `format` keeps what it has. Adding a key is not a format change: ignore keys
  you do not know.
- **A file's `digest`** is the first 16 hex characters of the SHA-256 of the
  file's bytes exactly as served (UTF-8 JSON, no whitespace). Check it after
  downloading; a mismatch means a partial download, so discard it.
- **The manifest's `digest`** is the first 16 hex characters of the SHA-256
  of the files' digests concatenated in the order listed. The same digest
  means the same set of files.
- The file list can grow. Download every file named; a file you do not use
  can be ignored.

### The files

`GET /api/carnatic/data/{name}` → the file, `Content-Type: application/json`,
`ETag: "<file digest>"`, `Cache-Control: public, max-age=300`;
`If-None-Match` → 304. Only names in the manifest are served.

**Updating:** ask `/version` (on launch and at most daily); if the digest
differs, fetch the manifest, download each file whose digest differs from
yours, verify each digest, and swap the whole set in at once, so the app
never mixes files from two builds.

| File | What it holds |
|---|---|
| `ragas.json` | `melakartas[]` (72), `janyas[]` (the explorer's janya ragas), `performed[]` (melakarta ragas as performed: Todi, Kalyani…), `aliases` (spelling → id), `meta` |
| `talas.json` | `practical[]` (11 talas plus Deshadi as Adi with `eduppu: 1.5`), `suladi[]` (the 35), `jatis`, `angas`, `nadai`, `kalai`, `konnakol`, `fingerOrder`, `alankaramTalas` |
| `lessons.json` | the beginner path: `path[]` (item ids in order), `sets[]` of `items[]`, `defaultRaga`, `speeds`, `attribution`, `varnamsComing[]` |
| `instruments.json` | `venu` (flutes, fingerings), `veena`, `violin`, `mridangam` (strokes, lessons), `voice`, `tanpura` (drone synthesis) |
| `featured.json` | the three fully written raga pages (Mohanam, Bhairavi, Begada): phrases, roles, gamaka character, attributions |
| `gamakas.json` | the gamaka library: `gamakas[]` with SSP signs, `vali`, `meta` |

Every key and type of every file is listed in
[DATA-SCHEMA.md](DATA-SCHEMA.md), generated from a build by
`scripts/carnatic/describe_data.py` and regenerated whenever the build
changes what it writes.

`GET /api/carnatic/reviews` → which script names and flagged facts a native
reader or consultant has checked in the review queue. Apply it over the data:

```json
{ "items": { "script:janya:mohanam:ta": { "status": "confirmed", "text": null },
             "script:mela:28:te": { "status": "corrected", "text": "హరికాంభోజి" },
             "fact:raga:dhanyasi": { "status": "confirmed", "text": null } },
  "updatedAt": "…" }
```

A `script:` key absent from `items` is **unverified**: draw the dotted
underline and the faint "unverified" label. `confirmed` clears the marker;
`corrected` replaces the text and clears it. A confirmed or corrected
`fact:raga:<id>` clears that raga's confidence notes, and
`fact:venu:<sthayi>-<swara>-<kind>` that fingering's "varies by flute" note.

### Shapes worth knowing

Notation tokens everywhere (data, songs): `S R1 R2 R3 G1 G2 G3 M1 M2 P D1 D2 D3 N1 N2 N3`,
octave marks `S'` (tara), `S''` (ati-tara), `.P` (mandra), `..P` (anumandra),
holds `,` (one unit) and `;` (two units). **Never show the ASCII to people**:
draw dots above and below the glyph. In lessons a bare letter (`R`) takes its
variant from the item's scale (`raga_scale`, else `defaultRaga`); a written
variant (`N2`) always wins, and is shown with its subscript.

Readers' text in the data (notes, reasons, attributions) is written for
readers: abbreviations in the research are spelled out by the build (PPN →
P. P. Narayanaswami every time; SSP, CDP, JMA, RTP, GNB and SAWF in full at
their first mention in a note). Show the text as it comes.

`ragas.json`:

```json
{ "melakartas": [ { "number": 28, "id": "harikambhoji", "name": "Harikambhoji",
    "iso": "Harikāmbhoji", "chakra": {"number": 5, "name": "Bana", "position": 4},
    "madhyama": "M1", "swaras": ["S","R2","G3","M1","P","D2","N2"],
    "arohana": "S R2 G3 M1 P D2 N2 S'", "avarohana": "S' N2 D2 P M1 G3 R2 S",
    "vivadi": [], "katapayadi": {"aksharas": ["ha","ri"], "digits": [8,2], "note": null},
    "dikshitar": "Harikedaragaula",
    "scripts": { "ta": {"grantha": "ஹரிகாம்போஜி", "pure": null},
                 "te": "హరికాంభోజి", "kn": "ಹರಿಕಾಂಭೋಜಿ" },
    "confidence": {"swaras_and_number": "high", "name": "high", "dikshitar_school_name": "high", "scripts": "low"},
    "janyas": ["mohanam", "kambhoji", …] } ],
  "janyas": [ { "id": "mohanam", "name": "Mohanam", … "tier": 1, "confidence": "high", … } ],
  "performed": [ … ],
  "aliases": { "thodi": "todi", … } }
```

`dikshitar` is `null` where both schools use the same name (show nothing).
`scripts.ta` has a `grantha` and a `pure` form; `pure` is `null` where only
one spelling is sourced. The person's Tamil style setting (§3) picks one,
falling back to the other. A missing script is `null`: show nothing, never a
transliteration of your own.

`lessons.json`: `sets[]` of `items[]`; each item has `sections[]` (a geetham's
or varnam's named sections; `section: null` for an exercise) of `lines[]` of
`segments[][]` (segments are the tala's angas, one token per unit) with an
optional `sahitya`, and `repeats: {"1": 1, "2": 1, "3": 2}`, the number of
times the item is sung at each speed so it ends on samam (the "×2" badge).
`path[]` is the order: the 50 default items, then the varnams that have
arrived. `optional: true` items (the 8th alankaram) are off by default.

**Varnams** arrive as the set `"id": "varnams"` when the research has their
notation. Each item is a lesson item as above plus `ragaId` (the raga's id in
`ragas.json`), `raga_scale` (its arohana and avarohana) and, where the
research gives them, `composer`, `language`, `type`, `tala_note`,
`confidence` and `source_url`. `varnamsComing[]` lists the ones not yet in
the data (`{title, raga, tala?}`, `raga` being an id): show them as "coming";
the list empties as they arrive. A varnam whose notation does not check out
(a note outside its raga, a line that does not fit the tala) is left out of
the data and stays "coming".

`talas.json`: `practical[]` (11 talas plus Deshadi as Adi with
`"eduppu": 1.5`), each with `counts[]` of `{"n":1,"action":"clap"|"finger"|"wave"|"silent","finger":"little"|…,"anga":0,"samam":true}`,
plus `variants[]` ("some schools", attributed), `suladi[]` (the 35) and
`konnakol` per nadai.

## 3. Settings (synced)

`GET /api/carnatic/me/settings` (auth) → `{ "settings": {…}, "updatedAt": "…" }`

`PUT /api/carnatic/me/settings` (auth) with the whole object, and
`"baseUpdatedAt"` = the `updatedAt` you last read (or `null` the first time).
409 `{"code": "CONFLICT", "settings": {…}, "updatedAt": "…"}` means another
device saved in between: show theirs, or merge field by field and PUT again
with the new `updatedAt`. Unknown keys are kept (so a newer app does not lose
an older one's fields); values are checked.

```json
{
  "lang": "en",                 "swaraLetters": "interface",     "tamilStyle": "grantha",
  "theme": "system",            "instrument": "venu",        "hand": "right",
  "sa": "E5",                   "flute": "E",                "droneTuning": "pa",
  "playbackTuning": "just",     "subscripts": "info",        "otherScripts": "show",
  "tempo": 60,                  "fourthSpeed": false,        "eighthAlankaram": false
}
```

| Key | Values | Default |
|---|---|---|
| `lang` | `en` `ta` `te` `kn` | `en` |
| `swaraLetters` | `latin`, `interface` (letters of `lang`; Latin when `lang` is `en`) | `interface` |
| `tamilStyle` | `grantha` (ஸ, ஸ்ரீ), `pure` (ச, சிறீ) | `grantha` |
| `theme` | `dawn` `dusk` `system` | `system` |
| `instrument` | `voice` `venu` `veena` `violin` `mridangam` | `voice` |
| `sa` | scientific pitch, `C3`…`B5` with `#` | voice `C3`, venu the flute's Sa (`E5`), veena `E3`, violin `E4`, mridangam `C3` |
| `flute` | a flute name from `instruments.json` (`E`, `E bass`, …) | `E` |
| `hand` | `right` `left` (left-handed mirror of the venu) | `right` |
| `droneTuning` | `pa` `ma` `ni` `mute` | `pa`; ragas without Pa suggest `ma`, ragas with M2 and no Pa suggest `mute` |
| `playbackTuning` | `just` `equal` | `just` |
| `subscripts` | `info` (only where they add information), `always` | `info` |
| `otherScripts` | `show` `hide` | `show` |
| `tempo` | 40–70 counts per minute at speed 1 | 60 |
| `fourthSpeed`, `eighthAlankaram` | booleans | `false` |

Drone and playback are synthesised in **just intonation relative to Sa**
(S 1, R1 16/15, R2 9/8, G2 6/5, G3 5/4, M1 4/3, M2 45/32, P 3/2, D1 8/5,
D2 5/3, N2 9/5, N3 15/8; labelled "textbook just-intonation values;
performers vary"). The tuner's cents are measured **against equal
temperament** and labelled so.

## 4. Progress and the practice log

`GET /api/carnatic/me/progress` (auth)

```json
{ "items": { "sarali_01": { "speeds": [1, 2, 3], "updatedAt": "…" },
             "sarali_04": { "speeds": [1],       "updatedAt": "…" } } }
```

`PUT /api/carnatic/me/progress/{itemId}` with `{"speeds": [1, 2]}`. Speeds
only ever merge upwards on the server (a stale phone cannot un-finish
anything); to reset, send `{"speeds": [], "reset": true}`.

`POST /api/carnatic/me/practice` with `{"day": "2026-09-26", "seconds": 600}`
adds time to that day (the day is the person's local date).
`GET /api/carnatic/me/practice?month=2026-09` →
`{"days": {"2026-09-01": 600, …}, "totalSeconds": 15000, "sessions": 12}`.

The log counts time; it never counts days missed. There are no streaks.

## 5. Songs (the composer) and public sheets

All song routes need auth except reading a published sheet.

- `GET /api/carnatic/songs` → `{"items": [ {id, slug, title, raga, tala, published, updatedAt} ]}`
- `POST /api/carnatic/songs` with a song body → 201 `{id, slug, updatedAt, …}`
- `GET /api/carnatic/songs/{id}` → the song
- `PUT /api/carnatic/songs/{id}` with the body and `"baseUpdatedAt"`; 409 as for settings
- `DELETE /api/carnatic/songs/{id}` → 204
- `POST /api/carnatic/songs/{id}/publish` → the sheet is public at
  `/carnatic/sheets/{slug}`. A published sheet is the person's own and goes
  with their account if they delete it (§9); say so where they publish.
- `POST /api/carnatic/songs/{id}/unpublish`
- `GET /api/carnatic/sheets/{slug}` (no auth) → the published song and its
  author's display name.

**413** `{"code": "PART_LIMIT", "limit": 2}` when a song carries more parts
than the account allows. Free accounts have 2 parts per song (the melody
counts as one); Swaras supporters have no limit. Songs saved by a supporter
keep their parts if the support ends; they become read-only for parts
beyond the limit (a PUT that does not add parts is accepted).

Song body (format 1):

```json
{
  "format": 1,
  "title": "Kaalai isai",
  "titleScript": "காலை இசை",
  "raga": "mohanam",
  "tala": "adi",
  "sahityaScript": "ta",
  "parts": [
    { "id": "melody", "kind": "melody", "instrument": "venu" },
    { "id": "p2", "kind": "strokes", "instrument": "mridangam" }
  ],
  "sections": [
    { "id": "pallavi", "name": "Pallavi", "repeat": 2, "notesPerCount": 2,
      "lines": [
        { "counts": [
            { "notes": ["kampita:G3", ","], "sahitya": "காலை", "parts": { "p2": ["tha"] } },
            { "notes": ["G3", "P"],         "sahitya": "இசை",  "parts": { "p2": ["dhi"] } }
          ] }
      ] }
  ]
}
```

- A line has exactly as many counts as the tala (Adi 8); each count exactly
  `notesPerCount` notes (1, 2 or 4). `,` and `;` are holds.
- A note is `[<gamaka>:]<swara><variant?><octave marks>`: `kampita:G3`,
  `.P`, `S'`. Gamaka names: `kampita`, `jaru-up`, `jaru-down`, `nokku`,
  `sphurita`, `pratyahata`, `ravai`, `khandippu`, `odukkal`, `orikkai`.
  Printed signs (after Subbarama Dikshitar's SSP, 1904): ∿ kampita · / and \
  jaru (before the note) · w nokku · ∴ sphurita · ∵ pratyahata · ∧ ravai ·
  ✓ khandippu · × odukkal · ⋎ orikkai.
- A note outside the raga is kept, never corrected: the sheet marks it with a
  dotted underline so the composer can decide.
- `strokes` parts hold mridangam syllables (`tha dhi thom nam ki ta mi chapu
  arai-chapu dheem tham dhom gumki`).
- Limits: 64 KB per song, 200 songs per account.

## 6. Listen (the concert hall)

The same room on the website and in the app, with the same rules. Reading
needs no account; sharing, liking, commenting and reporting need a signed-in
site account (a cookie on the web, a bearer token in the app).

- `GET /api/carnatic/listen?raga=&tala=&instrument=&before=<id>` →
  `{"items": [Post…], "next": 123 | null}`, newest first, 25 at a time; pass
  `next` as `before` for the next page. A post is
  `{id, title, author, mine, instrument, raga, tala, player: {"kind": "youtube"|"soundcloud"|"vimeo"|"bandcamp", "url": "…"}, sheetSlug, likes, liked, comments, createdAt}`
  (`raga` is a raga id; `sheetSlug` is set only when the linked sheet is
  published; `liked` and `mine` are for the person asking).
- `GET /api/carnatic/listen/{id}` → one Post; 404 if it does not exist or was
  hidden.
- `POST /api/carnatic/listen` (auth) with
  `{title (1–120), instrument?, raga?, tala?, url, sheetSlug?}` → 201 and the
  Post. The URL must be a YouTube, SoundCloud, Vimeo or Bandcamp link (422
  with a sentence otherwise); `sheetSlug` must be one of the person's own
  songs. **There is no upload**: the website does not host audio or video, so
  a performance is shared as a link to one of the four players.
- `DELETE /api/carnatic/listen/{id}` (the author) → 204
- `PUT /api/carnatic/listen/{id}/like` and `DELETE …/like` (auth) →
  `{"liked": true|false}`
- `GET /api/carnatic/listen/{id}/comments` → `{"items": [{id, author, mine, body, createdAt}]}`, oldest first
- `POST /api/carnatic/listen/{id}/comments` (auth) with `{"body": "…"}` (1–1000
  characters) → 201 and the comment; `DELETE /api/carnatic/listen/comments/{id}` (the author) → 204
- `POST /api/carnatic/listen/{id}/report` and
  `POST /api/carnatic/listen/comments/{id}/report` (auth) with
  `{"reason": "…"}` (optional, up to 300 characters) → `{"reported": true}`.

**Moderation, the same for both clients.** A report flags the post or
comment for Shruti; it hides nothing by itself. Each person reports a thing
once (reporting again answers `{"reported": true}` and changes nothing). The
review queue lists reported things first; hiding is her decision, and a
hidden post or comment disappears for everyone (404 on its own address). Offer
Report on posts and comments that are not the person's own.

**Limits**, per account: 10 shares an hour, 30 comments in 10 minutes, 30
reports an hour. Past them: **429** `{"code": "SLOW_DOWN", "detail": "…"}`;
show the sentence and let the person try later.

**Nothing third-party loads before a tap.** Show the "Load YouTube player"
card; embed only after the person presses it. The app may open the link in
the platform's own app instead.

## 7. The journal (the school's articles)

The journal at `/journal` is written with BeeRanked and synced to the site.
The school's articles are the ones about Carnatic music (the same selection
the school's landing page shows). These two are served by the website itself,
so their paths do **not** start with `/api`:

- `GET /carnatic/journal.json` →
  `{"items": [{slug, href, url, title, deck, date, updated, cover}]}`, newest
  first; `date` is `YYYY-MM-DD`, `cover` an image URL or `null`, `url` the
  article's full address.
- `GET /carnatic/journal/{slug}.json` → the same fields plus `body` (the
  article as HTML, as the journal page shows it: headings, paragraphs, lists,
  tables, images, links) and `toc` (`[{id, text, level}]` of its headings);
  404 `{"code": "NOT_FOUND"}` for anything that is not one of the school's
  articles.

Both are cacheable: `Cache-Control: public, max-age=600` and an `ETag`; send
`If-None-Match` and a 304 means keep your copy. Links inside `body` are
site-relative (`/journal/…`, `/carnatic/…`): resolve them against
`https://shrutivtuber.com`. Like the rest of `/carnatic`, both answer 404
while the school is not yet published.

## 8. Data the app never shows

Prices, the support page, the open fund and gifts are **web only**
(`/carnatic/support`). The app does not link to them.

## 9. Deleting an account

Deleting a site account (website Account page, or `DELETE /api/account/`)
deletes the person's settings, progress, practice log, device links, songs,
sheets, Listen posts, likes, comments and reports with it. The account export
(`GET /api/account/export`) includes all of them.
