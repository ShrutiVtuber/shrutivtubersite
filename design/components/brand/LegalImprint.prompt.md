# LegalImprint

The footer's legal identity block. **Ships from day one** — it is not a "later" item.

Pseudonymity is not in play for this brand: both her names are already public. The imprint is
therefore the *exposure surface*, and the whole point of designing it early is that the address in
it is a **virtual office, never her home**. Retrofitting an imprint is how home addresses leak.

## Use

Footer column (`layout="stacked"`, the default), or a paragraph on Privacy/Terms
(`layout="inline"`).

```jsx
<LegalImprint />
<LegalImprint layout="inline" />
```

## Notes

- Values default to the real entity name with **bracketed placeholders** for street, postcode,
  registry and VAT, awaiting company registration. Render the brackets as-is — they are a visible
  to-do, not a bug.
- Mono type, `--ink-faint`, tabular by nature. It should read like a colophon, not a banner.
- The email is the only link; it uses `--accent` like every other link in the system.
- Do not centre it, box it, or give it a background. It sits quietly at the foot of the footer.
