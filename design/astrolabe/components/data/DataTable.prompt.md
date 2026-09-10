Stations, planetary hours and the ephemeris — the screens a practitioner opens the app for.

```jsx
<DataTable caption="Athens · GMT+3 · sunrise convention"
  columns={[{key:'date',label:'Day'},{key:'sun',label:'Sun',mark:'☉',numeric:true},{key:'moon',label:'Moon',mark:'☾',numeric:true}]}
  rows={[{ id:'9', date:'9 Sep', today:true, sun:'16°♍', moon:{ value:'02°♑', retro:true } }]} />
```

- Never pad it out. If it does not fit, cut a column, not the density.
- `retro` on a cell prints ℞ next to the figure — the tint alone is not enough.
