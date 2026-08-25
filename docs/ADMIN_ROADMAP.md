# Admin — what is left, and the decisions behind it

**Live tracker.** Written so a compaction cannot lose the place.

## Where it stands

Done and deployed: page blocks, projects, links, profile fields, credits,
schedule, fan works, tools — all with add, edit, delete, reorder, visibility,
and in-place media upload where a template actually draws the picture.

Left, in the order agreed:

1. ~~User management~~ — done
2. **Merchandise** ← next — physical *and* digital
3. **Discount codes** — Stripe coupons and promotion codes
4. **Classes and workshops** — sold and hosted on the site, "like kotobaseed
   has". Explicitly **after the site itself is done**; not now.

## Her decisions, recorded

- **Merch is both physical and digital.** Physical brings shipping, addresses
  and customs; digital brings file delivery. Physical goods across the EU are a
  different VAT regime from the VAT-inclusive digital pricing already set up —
  that is an accountant question, not one to answer here.
- **Banning means**: the account with that email is deleted, and that email
  may never register again.
- **A ban must be GDPR-clean**: the person is told, and their data is sent to
  them, before the account goes.

## User management — the design

### What a ban actually does

In order, because the order matters:

1. Build their export — the same payload `/api/account/export` already
   returns, so there is one definition of "everything held about you".
2. Email it to them, with notice that the account is being closed. Sent
   **before** the deletion, because after it there is no address to send to.
3. Delete the account by the same path self-service deletion uses — which
   already reaches the newsletter list and anonymises the consent trail rather
   than destroying it, because that trail is the proof the deletion was lawful.
4. Record the ban.

### Why the ban list holds a hash, not an address

A list of banned addresses is a pile of personal data about people whose
accounts were just deleted — keeping it readable would undo half of what the
deletion was for. A SHA-256 of the normalised address answers the only
question ever asked of it ("is this one banned?") and cannot be read back into
a mailing list.

It is still enforceable, still liftable — she types the address to unban and
the hash matches — and the reason she wrote is kept in the clear, because that
is her note and not their data.

## Checklist

- [x] `BannedEmail` model + migration
- [x] Signup and sign-in refuse a banned address
- [x] `GET /api/admin/users` — list and search
- [x] `POST /api/admin/users/{id}/signin-link` — help someone back in
- [x] `POST /api/admin/users/{id}/ban` — export, email, delete, record
- [x] `GET/DELETE /api/admin/bans` — review and lift
- [x] `/admin/users` page
- [x] Tests
- [x] Deployed

## Gotchas this codebase has already paid for

- **Route ordering**: `/{kind}` catch-alls swallow anything declared after
  them. New `/users...` routes go **above** them. `tests/test_admin_routes.py`
  guards it.
- **A decorator applies to whatever function follows it.** Inserting a helper
  between `@router.post(...)` and its handler silently made the helper the
  route. Check what sits above an inserted function.
- **Patching must patch.** An upsert that replaced wiped the fields it was not
  given.
- **Checkboxes post nothing when unticked** — they need a hidden partner.
- **Match on content, not on indentation** copied out of a terminal dump.


## User management — done (2026-08-25)

`/admin/users`: search, a sign-in link you can send someone who cannot get in,
and closing an account. Barred addresses are listed and liftable underneath.

The ban does its four steps in order and **refuses if the mail does not go** —
nothing is deleted unless their copy was actually sent. Verified end to end:
the account went, the address could not register again (and the signup form
said nothing different to it than to anyone else), and lifting the ban with a
differently-cased version of the address worked, because the hash is of the
normalised form.

There is no password to read and none to set on their behalf. That is the
design, not a gap: the only door is a link to their own address.
