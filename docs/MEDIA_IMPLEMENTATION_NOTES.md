# Media management — working notes

**Live tracker. Update as work lands.** Written so a compaction cannot lose the
place, the way the journal notes were.

## The job

Managing page content is blocked on media, and it is the last thing between the
site and launch. Her words, condensed:

1. **Upload in place.** On projects and the like, upload right there — not go to
   Media, copy an id, come back and paste it.
2. **Delete.** Something uploaded cannot be removed at all. It must be.
3. **In-place uploads belong to the library** like any other.
4. **Tags, and search** on the media page.
5. **Rename on upload**, so files have meaningful names.

## What exists now

- `Media` model: `filename` (content hash + extension, unique), `mime_type`,
  `width`/`height`, `size_bytes`, `storage_backend` (local | r2), `alt_text`,
  `credit`, `credit_url`. **No title, no tags.**
- `POST /api/admin/media` — one file, hash-named, deduped, R2 with disk
  fallback. **No title or tags accepted.**
- `GET /api/admin/media` — everything, newest first. **No search, no filter.**
- **No DELETE, no PATCH.**
- `core/storage.py` has `put`, `fetch`, `public_url`. **No delete.**
- `/api/media/{filename}` proxies reads so R2 objects resolve.
- Four tables carry `media_id`: **section, project, tool, fan_art**.
- `admin/blocks.astro` is a generic editor — every field becomes a text input,
  so `media_id` is a box you type a number into. That is the cumbersome flow.

## Decisions

- **Filenames stay content-hashed.** Dedupe and stable URLs depend on it. The
  human name is a new `title` column; renaming never touches the file or URL.
- **Tags as a string column, not a join table.** ILIKE search and a distinct
  list in Python cover filtering at this scale (dozens to low hundreds). A
  join table is the more correct shape and is the thing to reach for if tags
  ever need renaming, merging or counting properly.
- **Deleting something in use is refused, not cascaded.** Nulling a reference
  silently blanks a picture on a live page. The error names what uses it.
- **In-place upload posts to the same endpoint**, so item 3 is true by
  construction rather than by a second code path.

## Checklist

- [x] Migration: `media.title`, `media.tags`
- [x] Upload accepts title + tags
- [x] `PATCH /api/admin/media/{id}` — rename, retag, alt text, credit
- [x] `DELETE /api/admin/media/{id}` — refuses when referenced, says by what
- [x] `storage.delete()` for disk and R2
- [x] `GET /api/admin/media?q=&tag=` — search and filter
- [x] `MediaField.astro` — in-place upload, used wherever `media_id` is edited
- [x] `blocks.astro` renders `media_id` with it, for all four kinds
- [x] Media page: search, tag filter, rename/retag/delete per item
- [x] Tests
- [x] Deployed and checked

## Gotchas already paid for on this codebase

- **Route ordering.** `/{kind}` catch-alls swallow anything declared after
  them; this has bitten three times, all silent. `tests/test_admin_routes.py`
  guards it — new `/media/...` routes must sit above the catch-alls.
- **`upsert` semantics.** Patching must patch, not replace: an earlier bug sent
  one field and wiped the rest.
- **Indentation when scripting edits.** Matching a line copied out of a
  prefixed terminal dump silently matches nothing. Match on content.


## Where it got to (2026-08-25)

All five asks are done and verified against the running stack, not only by
reading the code:

- Upload in place on projects, tools, page blocks and fan works — one field,
  `MediaField.astro`, wherever `media_id` is edited. It posts to the same
  endpoint the media page uses, which is why item 3 needed no work of its own.
- The library picker sits beside it, with its own search, so reusing an
  existing image is also not an id-paste.
- Delete works, file and row together. **Refused while something still points
  at it**, naming what: *"still in use by project “Theourgia”"*. Verified for
  both storage backends — the R2 object is genuinely gone from the bucket,
  checked by fetching it afterwards, not just absent from the database.
- Name and tags at upload, and editable afterwards without touching the file.
- Search over name, tags and alt text; a tag row that filters. Tag matching is
  padded (`,tag,`) so "art" cannot match "fan-art".

112 backend tests pass, 10 of them new. Typecheck is back to its pre-existing
60 errors — none in any of this.

### Two things worth knowing

- The **filename is still the content hash** and always will be. Renaming
  changes a column, never a file or a URL, so nothing that already points at an
  image can break by renaming it.
- Uploading a file that is **already in the library** returns the existing row
  and fills in a name or tags if it had none — it never overwrites what is
  there. So re-uploading to "rename" quietly does nothing, which is why rename
  is its own control.
