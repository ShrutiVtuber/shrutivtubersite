# Admin — what is left, and the decisions behind it

**Live tracker.** Written so a compaction cannot lose the place.

## Where it stands

Done and deployed: page blocks, projects, links, profile fields, credits,
schedule, fan works, tools — all with add, edit, delete, reorder, visibility,
and in-place media upload where a template actually draws the picture.

Left, in the order agreed:

1. ~~User management~~ — done
2. ~~Merchandise~~ — infrastructure done — physical *and* digital
3. **Discount codes** ← next
4. ~~Memberships as data~~ — done, see below — Stripe coupons and promotion codes
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


## Merchandise — the plan

### On "doesn't Stripe handle the tax?"

It handles the part a program can. Stripe Tax works out the right VAT for each
customer from their location and the product's tax code, and applies the EU
one-stop-shop rules for digital goods. What it cannot do is **register** her
where she owes, or **file** the returns — those stay hers, and physical goods
can create obligations digital ones do not.

So it is not a blocker. Her call, recorded: build the infrastructure now and
adjust the tax setup when there are real products to sell.

What that means for the build: the tax code is **per product**, not a constant,
and `tax_behavior` is a setting rather than baked in. Digital pricing is
inclusive today; physical may want exclusive, and that must be changeable
without a migration.

### Shape

Two kinds, one table. `physical` collects a shipping address at checkout and
has stock; `digital` delivers a file and does not. Everything else — name,
price, picture, description — is common, and splitting them into two tables
would mean writing every screen twice.

Mirrored to Stripe rather than owned by it: a row here, a Product and a Price
there, kept in step on save. The site needs to render a shop from its own
database without a network call per page, and Stripe needs to be the thing that
takes the money.

### Order of work

1. `Product` model, migration, Stripe sync on save
2. Admin: list, create, edit, activate — with the picture in place
3. Public shop and product pages
4. Checkout: shipping collected for physical, not for digital
5. `Order` from the webhook, and the digital download
6. Discount codes — Stripe coupons and promotion codes, after the above

### Known gap to solve on the way

Media uploads are **images only** (`ALLOWED_IMAGE`). A digital product is a PDF
or a zip or audio, so product files need their own allow-list and must not be
servable from the public media path — a paid file behind a guessable URL is not
a paid file.


### Managed Payments — the thing that actually decides the tax answer

Her account has **Managed Payments** on, which was switched on for the
memberships. It makes Stripe the merchant of record: Stripe owes the VAT, files
it, and is the name on the buyer's statement. That is why the memberships need
no registration of her own — a better answer than the one first given here.

**It does not support shipping.** A checkout session with
`shipping_address_collection` is refused outright while it is on.

So the shop splits along a line that is real rather than convenient:

| | Digital | Physical |
|---|---|---|
| Managed Payments | on | **off**, per session |
| Merchant of record | Stripe | **her** |
| VAT registration | Stripe's problem | **hers** |
| Shipping address | not collected | collected |

Physical sales pass `managed_payments: {enabled: false}`, because they cannot
work otherwise. That is the piece worth an accountant's attention **before the
first physical thing sells** — not the digital pricing, which is handled.


## Merchandise — where it got to (2026-08-25)

Working infrastructure, verified against the real Stripe account:

- `/admin/shop` — add, edit, delete, put on sale. The picture goes in in place.
  A product that cannot be bought says why rather than looking fine.
- Prices are typed in euros and stored in cents. Changing one makes a new
  Stripe price and retires the old, so anything already sold keeps what it was
  sold at.
- `/shop` and `/shop/<slug>` — the shop, rendered from this database. Buying
  posts to our own API, which makes the session; nothing touching a card runs
  on this box.
- Physical: address collected, stock counted down at the webhook, order lands
  as "to post" with the address and a button to mark it posted.
- Digital: a file, uploaded separately from media, delivered by a link in the
  receipt that does not expire.
- Orders are written from the webhook and keyed on the session, so a retry
  changes nothing.

### Since then

- **Several photographs per product.** Add, remove, and "make it lead" —
  which also moves `product.media_id`, so the card and the page never disagree
  about the same product.
- **Product files can be deleted**, and are refused while a product still
  delivers one: taking it away would leave every buyer of that product with a
  link to nothing, and they would be the ones to find out.
- **Shipping is worldwide** — 235 countries, everything Stripe accepts an
  address for, with the handful it refuses excluded so one bad code cannot
  fail a whole checkout. Narrowing it is now a deliberate act rather than a
  default left alone.
- **Tax codes are a picker, and follow the kind.** Real codes read off
  Stripe's own list: tangible goods, printed books, clothing, jewellery for
  physical; electronically supplied services, digital books, audiobooks for
  digital. Choosing "physical" no longer leaves a digital code sitting on it.

### Still to do here

- **Refunds** are done in the Stripe dashboard; nothing here reflects them.

### Not a code problem: Stripe is not configured on production

`/api/billing/tiers` answers `configured: false` there, because **all five
Stripe values are missing from production's `.env`** — the secret key, the
publishable key, the webhook secret, and both tier price IDs.

That is why the support page shows no prices and no "any amount" box: with no
`oneOff` in the payload the input is not rendered at all. Both of those
complaints are one cause. Locally, where the test keys are set, the page shows
€3 / €5 / €11 and the amount box.

Setting them is hers — they are live keys. `scripts/set-secret.sh` is the way.


## Memberships are rows now (2026-08-25)

`/admin/memberships` adds, edits and takes them off offer. The name, the perks,
the words on the button and the badge all come from the row, so a new tier is a
row rather than a page edit and a deploy. Verified by adding a third (€33/month)
and watching it appear on /support, priced, with its perks, and buyable.

**Nobody's subscription moved.** The two original tiers adopted the price IDs
that were already in the environment rather than being given fresh ones, so a
subscription taken out before this goes on billing against exactly the price it
was taken out against. Changing an amount makes a new Stripe price and retires
the old — which is the only honest way to change a price under a standing
arrangement.

A tier nobody is on can be removed; one people are paying for can only be taken
off offer, because their subscription lives at Stripe whether or not the row
does.

### The money rule got stronger, not weaker

`_line_items` had to become async to look a tier up, which broke the tests
guarding *"a subscription amount can never come from the client"*. Rather than
loosen them, the builders were split: `_one_off_line_items(amount)` is the only
one that takes an amount, and `_subscription_line_items(price_id, tier)` has
nowhere to put one. The test is now a signature assertion — a future edit
cannot re-introduce the bug by passing an amount through, because passing it is
a TypeError.

## Going live, when she is ready

She writes the three values into a file and says where; they are installed from
it without passing through a terminal or a chat, and the file is deleted.

    SHRUTI_STRIPE_SECRET_KEY       sk_live_…
    SHRUTI_STRIPE_PUBLISHABLE_KEY  pk_live_…
    SHRUTI_STRIPE_WEBHOOK_SECRET   from a live webhook endpoint

Once the live secret key is in, the live webhook endpoint and the live tier
prices are API-creatable from here. Only the account keys have to come from her
hands — Stripe shows a secret key once and never again.
