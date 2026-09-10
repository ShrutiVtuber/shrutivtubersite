The sunrise convention, the house system, the three sign-up consents — anywhere the app asks the user to settle a disagreement.

```jsx
<ChoiceRow type="radio" label="Sunrise" rule="The Sun's upper limb clears the horizon." checked={c==='sunrise'} value="sunrise" onChange={set} />
<ChoiceRow type="radio" label="Civil dawn" rule="The Sun is 6° below the horizon." checked={c==='civil'} value="civil" onChange={set} />
<ChoiceRow type="checkbox" label="Email me her newsletter" rule="About one a month. Unsubscribe in one tap." checked={n} onChange={setN} />
```

- Always give `rule`. A convention with no stated rule is a preference, and this app does not have preferences about facts.
- Never pre-tick a consent, and never put two consents behind one box.
