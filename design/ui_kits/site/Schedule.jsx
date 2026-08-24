const {SectionHeader,ScheduleItem,TimezoneToggle,EmptyState,Button}=window.ShrutiDesignSystem_cb687f;
function ScheduleScreen({tz,setTz,empty}){
  return <main className="site-main page">
    <div className="section-head">
      <SectionHeader as="h1" glyph="☾" eyebrow="Schedule" title="Upcoming streams" body="Authored in Athens (GMT+3); times shown in your zone."/>
      <TimezoneToggle value={tz} onChange={setTz}/>
    </div>
    {empty
      ?<EmptyState glyph="○" title="The sky is quiet" body="Nothing scheduled yet — streams are announced on Discord first, and the calendar fills at the new moon." action={<Button variant="secondary">Join the Discord</Button>}/>
      :<div style={{display:'grid',gap:'var(--space-3)'}}>
        <ScheduleItem tz={tz} status="live" title="Building the sigil compiler" topic="Software & Game Dev" durationMin={150} startISO={new Date(Date.now()-35*60000).toISOString()} href="#videos"/>
        <ScheduleItem tz={tz} status="upcoming" title="Theourgia dev — offerings ledger" topic="Software & Game Dev" durationMin={150} startISO="2026-08-27T21:00:00+03:00"/>
        <ScheduleItem tz={tz} status="upcoming" title="Gematria deep-dive with viewers" topic="Just Chatting · bilingual EN/ΕΛ" durationMin={120} startISO="2026-08-30T20:00:00+03:00"/>
        <ScheduleItem tz={tz} status="past" title="Planetary hours, computed properly" topic="Talk" startISO="2026-08-18T20:00:00+03:00"/>
      </div>}
    <p style={{font:'400 var(--text-xs)/1.6 var(--font-body)',color:'var(--ink-faint)',margin:0}}>Subscribe: <a href="#">iCal</a> · <a href="#">Google Calendar</a> — conversions use your system timezone.</p>
  </main>;
}
Object.assign(window,{ScheduleScreen});
