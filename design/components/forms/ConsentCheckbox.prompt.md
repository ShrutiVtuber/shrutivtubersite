# ConsentCheckbox

One consent decision, designed as a decision. This component exists because the sign-up on this
site collects **three separate agreements** and the law — and the design — require that they stay
separate.

## The three decisions

| # | Decision | `basis` | `required` |
|---|---|---|---|
| 1 | Create the account | `contract` | yes |
| 2 | Store my birth data for astrological readings | `explicit consent · GDPR Art. 9` | **no** |
| 3 | Send me the newsletter, including offers | `consent · marketing` | **no** |

Birth data processed to produce an astrological reading arguably reveals philosophical belief,
which would make it **special category data**. If so the lawful basis must be explicit consent.

## Hard rules

- **Never pre-ticked.** `checked` starts `false`, always.
- **Never bundled.** One checkbox per decision. Do not fold consent into "I accept the terms".
- **Never inferred** from using the form.
- Each carries **its own explanation** of what is stored and why.
- Someone must be able to say yes to one and no to another, and the form should make that feel
  normal rather than obstructive.
- Withdrawable in account settings **as easily as it was given** — the same three checkboxes,
  revisitable, with `meta` showing when consent was given.

## Use

```jsx
<ConsentCheckbox
  basis="explicit consent · GDPR Art. 9"
  label="Store my birth data so my chart and horoscope can be calculated"
  explanation="Your birth date, time and place are kept on your account and used only to compute your chart and to pick your horoscope. Nothing is shared, sold, or used to train anything. You can withdraw this and delete the data at any time."
  checked={c.birth} onChange={…}
/>
```

## Notes

- `required` renders "· required" and greys the basis eyebrow; optional consents render "· optional"
  in rose, so the difference is visible before reading a word.
- The error state is only ever for the *contract* consent. A special-category consent is never
  required, so it can never error.
- Only the checkbox is `--accent`; the card is a plain hairline. This is a form control, not a
  call-to-action.
