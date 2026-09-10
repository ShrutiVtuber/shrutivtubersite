Every text input in the app: the nativity form, the writing screen, the place search, sign-in.

```jsx
<TextField label="Time of birth" mono placeholder="14:05" helper="Local clock time. Leave blank if unknown." />
<TextField label="Your reading" multiline rows={10} maxLength={4000} counter value={draft} onChange={set} />
<TextField label="Email" error="That address was not recognised." value={email} onChange={set} />
```

- `mono` for anything with digits in it.
- The unknown-birth-time case is a blank field with helper text, never a validation error.
