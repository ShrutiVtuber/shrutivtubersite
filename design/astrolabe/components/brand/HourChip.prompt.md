The planetary hour now in force — the app's ambient signal, and the reason Home feels different at 03:00 than at noon.

```jsx
<HourChip ruler="venus" ordinal={4} diurnal ends="14:38" onClick={openHours} />
```

- Names the planet in words as well as the mark; the colour is never the only signal.
- Sets `data-hour`, so `--hour` re-points for anything nested. Cross-fades over `--dur-hour` (600ms).
- One per screen, at most. It belongs on Home and on Sky · Hours.
