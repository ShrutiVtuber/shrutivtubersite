Switches between the segments of one screen — it never navigates anywhere else.

```jsx
<SegmentedControl segments={[{id:'stations',label:'Stations'},{id:'hours',label:'Hours'},{id:'coming',label:'Coming'}]}
  active={seg} onChange={setSeg} label="Sky view" />
```

- The pill slides over `--dur-2`; the labels never move.
- Sits directly under the AppBar with 12px of air, full width of the gutter.
