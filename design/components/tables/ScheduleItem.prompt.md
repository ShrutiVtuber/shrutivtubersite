Schedule row: almanac date plate, serif title, and both times — the visitor's local time and Athens (GMT+3), converted via Intl. `tz` flips which leads; pair with `TimezoneToggle`.

```jsx
const [tz,setTz]=React.useState('local');
<TimezoneToggle value={tz} onChange={setTz}/>
<ScheduleItem tz={tz} title="Theourgia dev — offerings ledger" topic="Software & Game Dev" durationMin={150} startISO="2026-08-27T21:00:00+03:00" status="upcoming"/>
```

States: `upcoming`, `live` (red wash + "● Live now"), `past` (dimmed). Empty schedules use `EmptyState`, never a bare gap.
