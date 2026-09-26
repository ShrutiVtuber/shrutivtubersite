# Swara Studio: the API the app builds against

Swara Studio is the Carnatic music school at `https://shrutivtuber.com/carnatic`.
Its web pages, its data and its accounts are served by this repository; the
Flutter app (private repository `swara-studio/app`) is a second client of the
same API, exactly as the Astrolabe and Squirrel Guides apps are.

- **Base URL:** `https://shrutivtuber.com` (production). Locally
  `http://localhost:8200`. Every path below starts with `/api`.
- **Bodies:** JSON. Errors are `{"detail": "<a sentence meant for a person>"}`;
  show `detail` as it is. Where a client must branch, the status code says so
  (401, 403, 404, 409, 428, 429), and a few answers add `"code"`.
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
  "supporter": false,
  "limits": { "partsPerSong": null },
  "settings": { … see §3 … },
  "settingsUpdatedAt": "2026-09-26T12:00:00+00:00"
}
```

Signed out: `{"signedIn": false, "limits": {"partsPerSong": null}, "settings": null}`.

**Nothing in Swara Studio is gated** (the owner's rule of 26 Sep 2026):
every tool and every feature is free for everyone, as the site's other tools
are. `limits.partsPerSong` is always `null` (no limit) and is kept only for
clients that read it. `supporter` says whether the person is a Swaras
supporter so the website can thank them; it unlocks nothing. **The app shows
no prices, no supporter mentions and no purchase links** (App Store and Play
rules, and the design's hard rule 6).

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
arrived (54 with all four). `optional: true` items (the 8th alankaram) are off by default.

**Varnams** arrive as the set `"id": "varnams"` when the research has their
notation. Each item is a lesson item as above plus `ragaId` (the raga's id in
`ragas.json`), `raga_scale` (its arohana and avarohana) and, where the
research gives them, `composer`, `language`, `type`, `tala_note`,
`confidence` and `source_url`. Varnams are printed one **2-kalai Adi**
avartanam a line (16 + 8 + 8 units: the angas scaled, not repeated); such a
varnam carries `"kalai": 2`, `"practicalTala": "adi_2_kalai"` (16 counts in
`talas.json`) and `"unitsPerCount": 2`: two notes to a count at speed 1, four
at speed 2, eight at speed 3. Its `repeats` are computed on that 32-unit
avartanam. An item without `unitsPerCount` has one note a count at speed 1. `varnamsComing[]` lists the ones not yet in
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
  `/carnatic/sheets/{slug}`. When the person deletes their account they
  choose whether their published sheets stay up, credited to nobody, or go
  (§9); say so where they publish.
- `POST /api/carnatic/songs/{id}/unpublish`
- `GET /api/carnatic/sheets/{slug}` (no auth) → the published song and its
  author's display name, or `"author": null` for a sheet kept after its
  author deleted their account (show no credit). A sheet hidden by
  moderation is 404 for everyone except its author, who gets it with
  `"hidden": true` (say it is hidden while Shruti reviews reports).
- `POST /api/carnatic/sheets/{slug}/report` (auth) with `{"reason": "…"}`
  (optional, up to 300 characters) → `{"reported": true}`. Published sheets
  are moderated exactly like Listen posts (§6): once per person, three
  different reporters hide it until Shruti reviews it, reporters never shown.
  Offer Report on sheets that are not the person's own. Shruti may restore a
  sheet or remove it for good, whatever its author chose when leaving.

A song may have any number of parts, for everybody.

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
comment for Shruti. Each person reports a thing once (reporting again
answers `{"reported": true}` and changes nothing). When **three different
accounts** have reported it, it is **hidden automatically until she reviews
it**; she then restores it or removes it for good. A restored post is only
hidden again by three new reports. A hidden post or comment disappears for
everyone (404 on its own address; gone from the list). **Who reported is
never shown to anyone**, her included; only the count and any reasons given.
Offer Report on posts and comments that are not the person's own.

`author` is `"somebody"` on a post or comment kept after its author deleted
their account. A post's `sheetSlug` is `null` while its sheet is hidden.

Published song sheets follow the same rules (§5,
`POST /api/carnatic/sheets/{slug}/report`).

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

Prices and the support page are **web only** (`/carnatic/support`, which
invites people to become a Swaras supporter through the site's own
`/support`). The app does not link to them. There is no fund and nothing to
gift: nothing is sold or unlocked.

## 9. Deleting an account

Deleting a site account (website Account page, or `DELETE /api/account/`)
follows the owner's rule of 26 Sep 2026:

- **Deleted:** Swara Studio settings, progress and app sign-in codes.
- **Kept without a name:** Listen posts, comments, likes and reports, and
  the practice log. Posts and comments then show `"author": "somebody"`.
- **Songs, as the person chooses:** `DELETE /api/account/?songs=anonymise`
  keeps each published sheet up, credited to nobody (`"author": null`), and
  deletes the songs never published; `?songs=delete` deletes every song and
  sheet. A person who has songs and sends neither is answered, and nothing
  is deleted:

```json
409 { "code": "SONGS_CHOICE_NEEDED",
      "detail": "You have songs in Swara Studio. Keep your published sheets up, credited to nobody, or delete them with your account?",
      "songs": 3, "published": 1 }
```

  Ask with those two choices, then call again with `songs`. A person with no
  songs is deleted at once, as before.

An account **banned** by Shruti is deleted the same way, except that its
songs and sheets are always deleted (the owner's rule of 26 Sep 2026); the
choice is only for somebody deleting their own account.

The account export (`GET /api/account/export`) is unchanged and includes all
of it.

---

# Part II: the full school (v2)

Everything below is the v2 contract: the course, exercises, Test yourself,
ear training, the Listening room and community feedback. Same conventions
as Part I (base `/api`, JSON, `{"detail": …}` errors, ISO times, bearer
token or cookie). **Nothing is gated**: every read works signed out; an
account only keeps things across devices and is needed to post.

## 10. The course (content, for reading and offline)

The course text lives in the private course repository and is imported
into the site's database, where Sophia edits it in the Swara Studio admin.
The site and the app read the **published** version only. A lesson is
published when its `status` is `published`; until then it is absent from
every public answer (the operator sees drafts on the website only).

### 10a. Knowing when to download

`GET /api/carnatic/course/version` →
`{"digest": "…16 hex…", "lessons": 12, "exercises": 40, "updatedAt": "…"}`,
`ETag: "<digest>"`, 304 on `If-None-Match`. The digest changes whenever
any published lesson, exercise, glossary entry, drill definition or the unit
list changes.

### 10b. The whole course in one download (offline)

`GET /api/carnatic/course/bundle` (ETag as above) →

```json
{ "format": 1, "digest": "…", "updatedAt": "…",
  "units":     [Unit, …],          // all 21, always
  "lessons":   [Lesson, …],        // published lessons, full text
  "exercises": [Exercise, …],      // exercises of published lessons, plus checkpoints
  "glossary":  [Term, …],
  "drills":    {"families": […], "levels": […], "ragaFlags": {…}},
  "tala_keeping": [TalaTask, …] }  // K.01-K.16
```

Or piecewise, same shapes:

- `GET /api/carnatic/course/units` → `{"items": [Unit]}`
- `GET /api/carnatic/course/lessons/{idOrSlug}` → `Lesson` (404 if unknown or not published)
- `GET /api/carnatic/course/exercises?unit=9` or `?lesson=U09.L03` → `{"items": [Exercise]}`;
  `GET /api/carnatic/course/exercises/{id}` → `Exercise`
- `GET /api/carnatic/course/glossary` → `{"items": [Term]}`
- `GET /api/carnatic/course/drills` → the drill definitions (§13)

**Unit**

```json
{ "n": 9, "title": "The melakarta system", "level": "intermediate",
  "levelLabel": "Intermediate", "intro": "2-3 sentences",
  "lessons": [ { "id": "U09.L01", "slug": "…", "order": 1, "title": "…",
                 "minutes": 15, "level": "intermediate",
                 "available": true,             // a published lesson exists
                 "hasListening": true, "hasPractice": false } ],
  "checkpoint": "CP.U09" }                      // or null
```

Units come from the syllabus, so all 21 units and all 173 lessons are
listed from day one; `available: false` lessons (not yet written or not
published) are shown as "coming", never as a link. Level labels:
units 1-7 Foundations, 8-15 Intermediate, 16-21 Advanced (unit 18 is
"any time" in the syllabus); they are labels only and unlock nothing.

**Lesson**

```json
{ "id": "U01.L01", "slug": "sa-your-home-note", "lang": "en",
  "revision": 3, "unit": 1, "order": 1,
  "title": "…", "summary": "…", "level": "beginner", "minutes": 15,
  "goals": ["…"], "prerequisites": ["U00.L00"], "tools": ["drone", "sargam"],
  "ragas": ["mohanam"], "talas": ["adi"],
  "recordings": [ {"id": "form-tanpura-02", "why": "…",
                   "available": true} ],        // false until Sophia approves it
  "sources": [ {"key": "ins-sa", "n": 1, "cite": "…", "url": null,
                "confidence": "high"} ],        // n: footnote number, in order of first use
  "exercises": ["U01.L01.Q1", "U01.L01.P1"],
  "body": "markdown exactly as FORMAT.md §3 (editor notes removed)",
  "words": 1834,
  "translation": null }       // or {"lang": "ta", "status": "published", "outOfDate": false}
```

`body` is the lesson markdown with `<!-- -->` editor notes already stripped.
Render it by FORMAT.md §3 (the same rules the website uses): YAML is
already split out; `{{kind k=v}}` lines and ```` ```sargam ```` fences are
embeds; `> [!listen]`, `> [!schools]`, `> [!sources]` quote blocks are the
three boxes; `[^key]` are footnote markers numbered by `sources[].n`.

Tolerated extensions (until format 2 lands): a tap task embedded with
`{{quiz id=U04.L02.T1}}` (render it as a tap task: look the id up in the
exercises); `{{tap id=…}}` means the same. Unknown tags render as a quiet
grey box naming the tag, never as an error and never hiding text.

Translations: lessons are English only at launch. When a published
translation exists for the requested `?lang=ta|te|kn`, it is returned with
`"translation": {…}`; otherwise the English is returned and the client
shows the quiet "not yet translated" line.

**Exercise**: the exercise as FORMAT.md §4 defines it, converted to JSON,
with the writers' extensions kept as they are (`also`, `also_recordings`,
`recordings_also`, `recording_choices`, `pool`, `comparison` on listening
exercises; `speed: [1,2,3]`, `nadai: [4,3,5]` or `nadai_sequence`,
`plays`, `eduppu`, `line`, `targets: entry`, `tempo_range` on taps;
`line` and `raga`/`tala` on fill and sargam items; `checkpoint: true`,
`includes`/`drills`, `skills` on checkpoints). Clients should treat
unknown fields as absent. Answers are included (the app checks offline).

**Term** (glossary): `{ "term": "vakra", "slug": "vakra", "definition":
"one line", "lesson": "U07.L05", "aliases": ["vakra raga"] }`.

## 11. Lesson progress (synced)

Kept on the device when signed out; synced when signed in.

- `GET /api/carnatic/me/lessons` → `{"items": {"U01.L01": {"openedAt": "…",
  "completedAt": "…" | null, "position": {"heading": "choosing-your-sa",
  "fraction": 0.42}, "updatedAt": "…"}}}`
- `PUT /api/carnatic/me/lessons/{id}` with any of `openedAt`, `completedAt`
  (`null` un-marks), `position`, and `updatedAt` (the device's time of the
  change). Merge rule: `openedAt` keeps the earliest; `completedAt` and
  `position` follow the most recent `updatedAt`. Returns the merged row.

Completion is manual ("Mark as complete"). Nothing is marked for the
learner, nothing is locked, and there is no streak.

## 12. Attempts, personal bests and review cards (synced)

### 12a. Attempts

`POST /api/carnatic/me/attempts` with `{"attempts": [Attempt, …]}` (up to
200; the client's `id` makes it idempotent) → `{"stored": 3, "bests": [Best…]}`
(the bests this batch improved).

```json
{ "id": "client uuid", "itemId": "U01.L01.Q1" | "CP.U09" | "K.02" | "SW.04" | "mixed",
  "kind": "quiz" | "checkpoint" | "tap" | "drill" | "review" | "guess",
  "startedAt": "…", "seconds": 184,
  "result": { … } }
```

`result` by kind:
- quiz, review: `{"items": [{"key": "U01.L01.Q1#3", "right": true}], "right": 5, "of": 6}`
- checkpoint: as quiz plus `"skills": {"melakarta": {"right": 4, "of": 5}}`
- tap: `{"tempo": 60, "perfect": 12, "onTime": 3, "early": 1, "late": 0, "missed": 0, "of": 16}`
- drill: `{"level": "SW.04", "items": [{"card": "SW.04:G2-G3", "right": true, "ms": 2100}]}`

`GET /api/carnatic/me/attempts?item=CP.U09&kind=checkpoint&limit=50` →
`{"items": [Attempt]}` newest first (for the charts).

### 12b. Personal bests

`GET /api/carnatic/me/bests` → `{"items": [{"itemId": "CP.U09", "skill":
"melakarta", "best": {"right": 5, "of": 5, "word": "comfortable"},
"achievedAt": "…"}]}`. The server keeps one row per item and skill:
checkpoint skills by share right (**new** under 50 %, **getting there**
50-79 %, **comfortable** 80 % and over; these three words are the only
scale shown), taps by perfect + on time out of targets at the highest
tempo, drills by the highest level with 16 of the last 20 right. Results
are never shown to anyone else.

### 12c. Review cards (spaced repetition, EAR_TRAINING.md §6)

- `GET /api/carnatic/me/cards` → `{"items": [Card], "due": 12}`
- `PUT /api/carnatic/me/cards` with `{"cards": [Card, …]}` → the merged
  cards. Merge: per `key`, the card with the latest `lastSeen` wins.

```json
{ "key": "SW.04:G2-G3" | "U01.L01.Q1#3" | "gen:mela_scale_from_number:chakra-4",
  "box": 0..6, "lastSeen": "…", "nextDue": "…", "recent": [true, false, true] }
```

Boxes 0-6 = this session, 1, 3, 7, 16, 35, 75 days. Right: up one box (two
if under the item's fluent time); wrong: box 1, and again later in the same
session. The dashboard says "12 cards ready to review", never how long it
has been.

## 13. Ear training and tala keeping (definitions)

`GET /api/carnatic/course/drills` →

```json
{ "families": [ {"id": "SW", "title": "Swaras against the drone", "answerBy": "swara buttons"} … ],
  "levels": [ {"id": "SW.04", "family": "SW", "title": "The pairs that matter",
               "unlockedBy": "U02.L05", "answer": "choice",
               "audio": {"kind": "synth"}, "ladder": ["3 options", "5 options", "all"],
               "fluentMs": 3000, "note": null} … ],
  "ragaFlags": { "todi": {"synthOk": false}, "mohanam": {"synthOk": true} … },
  "confusable": [ {"set": "C1", "ragas": ["mohanam", "shivaranjani"], "mode": "synth",
                   "unlockedBy": "U12.L03"} … ] }
```

`unlockedBy` is advice: a level whose lesson isn't complete is shown
dashed with the lesson named, and can be opened anyway. MS levels carry
`"note": "a scale, not a raga"`. Ragas with `synthOk: false` (Todi,
Sahana, Begada, Anandabhairavi, Varali, Saveri, Kanada, Atana, and the
pairs EAR_TRAINING.md §3 names) are drilled only from recordings; Sophia
changes the flags in the admin.

Tala keeping: `tala_keeping` in the bundle holds K.01-K.16 as tap tasks
(`{"id": "K.02", "title": "…", "tala": "adi", "tempoRange": [50, 80],
"targets": "claps", "fade": ["all", "claps", "samam", "none"],
"unlockedBy": "U04.L02"}`). Timing: perfect ±30 ms, on time ±80 ms,
shrinking to 40 % of the gap at dense targets.

## 14. The Listening room

### 14a. Recordings

Only recordings Sophia has **approved** are ever returned.

- `GET /api/carnatic/listening/recordings?raga=mohanam` or `?form=varnam`
  → `{"items": [Recording]}`
- `GET /api/carnatic/listening/recordings/{id}` → `Recording` (404 if not
  approved; a retired recording returns `"status": "retired"` and no `url`)

```json
{ "id": "mohanam-02", "status": "approved" | "retired",
  "provider": "youtube", "url": "https://…", "title": "…", "channel": "…",
  "artists": ["…"], "instrument": "voice", "composition": "…", "composer": "…",
  "form": "kriti", "raga": "mohanam", "tala": "adi",
  "listenFor": "…", "clips": [{"id": "a", "start": "1:10", "end": "1:40", "label": "…"}],
  "sections": [{"t": "2:14", "label": "anupallavi"}],     // Sophia's marks (answer keys: see below)
  "beatMap": {"clip": "a", "samam": [12.40, 20.41, …]} | null,
  "analyses": 14 }
```

Guess mode: clients must not show `title`, `channel`, `raga` or
`composition` until the learner has committed a guess (§14b). `sections`
are only returned to clients for recordings the learner has guessed or
that are not used in guess mode; auto-checking of analyses happens on the
server (§15).

### 14b. Guess the raga

`POST /api/carnatic/listening/guesses` with `{"recording": "mohanam-02",
"guess": "mohanam", "confidence": "hunch" | "fairly" | "sure",
"phrases": "optional text"}` → `{"right": true, "close": false, "raga":
"mohanam", "ragaName": "Mohanam", "composition": "…", "artists": […],
"listenFor": "…", "lessons": ["U12.L03"]}`. Signed out, the guess is
checked and nothing is stored. Stored guesses: `GET
/api/carnatic/me/guesses`. Analyses of a recording stay hidden from a
learner until they have guessed it (`GET …/analyses` answers `{"locked":
true}` until then, for recordings in guess mode).

### 14c. Suggesting a recording

`POST /api/carnatic/listening/suggestions` (auth, not suspended) with
`{"url", "raga", "composition", "why"}` → 201 `{"id", "title", "channel",
"status": "pending"}` (the site fetches the provider's oEmbed and shows
back what it found). 422 if the link isn't YouTube, SoundCloud, Vimeo or
Bandcamp; 429 `{"code": "TOO_MANY_PENDING"}` over 5 pending.
`GET /api/carnatic/me/suggestions` → `{"items": [{…, "status": "pending"
| "approved" | "rejected" | "held", "reason": "…"}]}`.

## 15. Community: practice pieces and listening analyses

Both are **works** in the site's practice model, in two rooms:
`carnatic-practice` (subject `exercise:U10.L04.P1`) and
`carnatic-analysis` (subject `recording:mohanam-02`). The same votes,
comments, reports, strikes and blocks serve the horoscope practice room,
so a suspension or a block applies everywhere.

### 15a. Reading

- `GET /api/carnatic/community/works?room=carnatic-practice&subject=exercise:U10.L04.P1&sort=new|discussed&before=<id>`
  → `{"items": [WorkSummary], "next": id | null}`. Hidden works and works
  by people the viewer blocked are absent.
- `GET /api/carnatic/community/works/{id}` → `Work`; 404 `{"code":
  "NOT_AVAILABLE"}` for a hidden work unless it is the viewer's own, which
  comes back with `"hidden": true, "hiddenBy": "reports"` ("Hidden while
  Shruti reviews reports").

```json
{ "id": 41, "room": "carnatic-analysis", "subject": "recording:mohanam-02",
  "title": "…", "author": "Priya" | "somebody", "authorId": 7 | null, "mine": false,
  "submittedAt": "…", "votes": 3, "voted": false, "comments": 5,
  "parts": [ {"key": "sargam", "body": "G3 D2 P G3 R2", "data": {"raga": "mohanam", "tala": "adi", "speed": 2}},
             {"key": "text", "body": "…"},
             {"key": "link", "body": "https://youtu.be/…"},
             {"key": "note:1", "body": "…", "data": {"t": "2:14", "category": "phrase", "notation": "G3 D2 P G3 R2"}},
             {"key": "summary", "body": "…"},
             {"key": "guess", "data": {"raga": "mohanam", "confidence": "sure", "at": "…"}} ],
  "rubric": {"questions": [{"id": "idiom", "ask": "…", "scale": ["not yet", "partly", "yes"]}],
             "totals": {"idiom": {"not yet": 0, "partly": 2, "yes": 5}}, "mine": {"idiom": "yes"}},
  "private": {"sectionsFound": 5, "sectionsMarked": 6} | null,   // author only
  "hidden": false }
```

Deleted accounts show as `"author": "somebody"`, `"authorId": null`
(works and comments are kept, anonymised; Sophia's rule).

### 15b. Writing

- `POST /api/carnatic/community/works` with `{"room", "subject", "title",
  "parts": [...]}` → 201 draft. `PUT …/works/{id}` replaces a draft's
  parts. `POST …/works/{id}/submit` makes it public (it runs the
  exercise's `prechecks` and returns them as `"hints"`: they never block).
  First submission needs the site's publish agreement: 428
  `{"code": "PUBLISH_AGREEMENT_NEEDED"}` until the person agrees (the same
  agreement as the rest of the site's public writing).
- `POST …/works/{id}/withdraw` hides one's own work.
- `DELETE …/works/{id}` deletes one's own draft.
- Word ranges come from the exercise definition (`submission.text.words`).

### 15c. Feedback

- `PUT /api/carnatic/community/works/{id}/vote` and `DELETE …/vote`
  ("This helped me"; one per person, never on one's own work).
- `PUT /api/carnatic/community/works/{id}/rubric` with `{"answers": {"idiom":
  "yes", "tip": "free text"}}` (one set per person; shown only as totals).
- `GET /api/carnatic/community/works/{id}/comments` →
  `{"items": [{"id", "author", "authorId", "mine", "part": "note:1" | null,
  "partLabel": "the 2:14 phrase", "body", "createdAt"}]}`;
  `POST` with `{"body", "part"}`; `DELETE /api/carnatic/community/comments/{id}` (own).

### 15d. Reports, blocks, suspension

- `POST /api/carnatic/community/works/{id}/report` and
  `POST /api/carnatic/community/comments/{id}/report` with `{"reason":
  "abuse" | "hate" | "sexual" | "spam" | "self-harm" |
  "not-about-this-exercise" | "other", "detail"}` → `{"reported": true}`.
  One per person per thing; three distinct reporters hide it until Sophia
  reviews it; reporters are never shown.
- `GET /api/carnatic/community/blocks`, `POST` with `{"userId"}`,
  `DELETE /api/carnatic/community/blocks/{userId}`: blocks work both ways
  and nobody is told.
- `GET /api/carnatic/me/community` → `{"suspended": null | {"until": "…" |
  null, "reason": "…"}}`. A suspension pauses posting only (403 with the
  sentence on any write); reading, lessons and drills stay available.
  Lengths and appeals follow the site's practice-room strikes (Sophia sets
  the length when she upholds a report; 0 is indefinite; replying to the
  notice reaches her).

## 16. Drills data offline, and what needs a connection

Works offline from the bundle: lessons, exercises, quizzes, checkpoints,
ear-training drills with synthesised audio, tala keeping and the review
queue. Needs a connection: recordings (and RR/GM/TL/FM drills that play
them), the Listening room, community, sync. Queue attempts, cards and
lesson progress offline and send them when back online.

## 17. The Swara Studio admin (web only)

`/carnatic/studio` on the website, for the operator: lessons tree and
editor (form, text, live preview, checks, editor notes, revision history),
exercises, recordings queue and annotation, balance, moderation, glossary,
review. Its API lives under `/api/carnatic/studio/*` and is not for the app.
