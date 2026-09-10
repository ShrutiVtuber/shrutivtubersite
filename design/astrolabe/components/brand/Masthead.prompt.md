The top of Home — the only place in the app that uses the cloak navy at full area.

```jsx
<Masthead greeting="Good evening" line="A waxing gibbous moon, four days from full."
  portrait="assets/portrait-offline.png" live={false}>
  <HourChip ruler="venus" ordinal={4} />
</Masthead>
```

- Exactly one per app. Never repeat the plate on another screen — Sky, Chart and Practice are page-coloured.
- Always test it with `portrait` omitted; that is the state that ships first.
