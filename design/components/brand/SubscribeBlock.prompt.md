# SubscribeBlock

The newsletter subscribe form, reusable across the site.

## Two things this component refuses to do

**1. It does not hide the commercial intent.** The list is meant to eventually sell astrological
courses and magickal services. That is stated in the consent wording at the point of subscription —
"including offers for courses and services when they open" — not discovered three issues later. It
is also better marketing than hiding it.

**2. It does not pin consent underneath as an afterthought.** The marketing consent is a real
checkbox inside the form, on its own inset surface, and it is part of the layout rather than fine
print below the button.

## The `sent` state is mandatory, not optional

Double opt-in is required: **an unconfirmed address is not consent.** `state="sent"` is the
"check your email" screen, and it is where subscribers are lost, so it is designed properly —
it names the address, says plainly that nothing arrives until the link is clicked, gives the
expiry, and mentions spam.

## Variants

- `panel` — the full block on `/newsletter`, card surface.
- `inline` — end-of-page strip, hairline top, no card.
- `aside` — narrow column, wraps the field under the button.

## Use

```jsx
<SubscribeBlock
  email={email} onEmailChange={…}
  consented={ok} onConsentChange={…}
  onSubmit={…}
/>
<SubscribeBlock state="sent" email="reader@example.com" />
```

## Notes

- Field is mono (it is an address, a piece of data), 44px minimum, `--accent` submit.
- Never pre-tick `consented`.
- The footnote line carries "no tracking pixels" honestly — analytics on this site are cookieless
  and the emails contain no open-tracking pixel. Do not add one.
- Do not add a "we hate spam too" joke, a social-proof count, or an incentive. None of those are
  this brand's voice.
