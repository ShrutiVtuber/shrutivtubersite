const {SectionHeader,NextStation,StationTable,ExportBlock,SelectField,TextField,Button,Badge}=window.ShrutiDesignSystem_cb687f;

const SOLAR={
  stations:['Sunrise','Noon','Sunset','Midnight'],
  glyphs:['☉︎','☉︎','☉︎','☾︎'],
  presets:{
    hellenic:['Hekate Phosphoros','Apollo','Hekate Enodia','Persephone'],
    thelemic:['Liber Resh — Ra','Liber Resh — Ahathoor','Liber Resh — Tum','Liber Resh — Khephra'],
    none:null
  },
  times:[['06:52','13:29','20:05','00:29'],['06:53','13:29','20:03','00:28'],['06:54','13:28','20:02','00:28'],
    ['06:55','13:28','20:00','00:28'],['06:56','13:28','19:58','00:27'],['06:57','13:27','19:57','00:27'],
    ['06:58','13:27','19:55','00:26'],['06:59','13:27','19:53','00:26']]
};
const LUNAR={
  stations:['Moonrise','Culmination','Moonset','Nadir'],
  glyphs:['☾︎','☽︎','☾︎','●'],
  // The Moon rises ~50 min later each day and skips a civil day now and then — nulls are real sky.
  times:[['17:41','22:14','03:22','10:48'],['18:29','23:02','04:11','11:36'],['19:14','23:51','05:02','12:25'],
    ['19:57',null,'05:55','13:15'],['20:38','00:41','06:49','14:06'],['21:19','01:33','07:44','14:58'],
    ['22:01','02:26','08:41','15:51'],[null,'03:21','09:39','16:45']],
  phases:['◐ 11.4 d','◐ 12.4 d','○ 13.4 d','○ 14.4 d','● 15.4 d','● 16.4 d','◑ 17.4 d','◑ 18.4 d']
};
const DATES=['7 Sep','8 Sep','9 Sep','10 Sep','11 Sep','12 Sep','13 Sep','14 Sep'];
const WEEKDAYS=['Mon','Tue','Wed','Thu','Fri','Sat','Sun','Mon'];

function StationsScreen({kind,polar}){
  const solar=kind==='solar';
  const S=solar?SOLAR:LUNAR;
  const [preset,setPreset]=React.useState('Hellenic');
  const [range,setRange]=React.useState('One month');
  const [copied,setCopied]=React.useState(false);
  const PRESET_KEY={'Hellenic':'hellenic','Thelemic':'thelemic','None — times only':'none'};
  const attributions=solar?SOLAR.presets[PRESET_KEY[preset]]:null;
  const rows=S.times.map((t,i)=>({date:DATES[i],weekday:WEEKDAYS[i],times:t,today:i===0,
    currentIndex:i===0?(solar?1:0):undefined,phase:solar?undefined:LUNAR.phases[i]}));

  return <main className="site-main page">
    <SectionHeader as="h1" glyph={solar?'☉︎':'☾︎'} eyebrow={'Theourgia · '+(solar?'solar':'lunar')+' stations'}
      title={solar?'Solar stations':'Lunar stations'}
      body={solar
        ?'Sunrise, noon, sunset, midnight — the four hinges a daily practice hangs on, for every day in the range you choose. The tool computes the times; which deity belongs to which station is yours to set or ignore.'
        :'Moonrise, culmination, moonset, nadir. The Moon keeps its own calendar: it rises about fifty minutes later each day, and some days it does not rise at all.'}/>

    <div style={{background:'var(--surface-card)',border:'1px solid var(--line)',borderRadius:'var(--radius-md)',boxShadow:'var(--shadow-1)',padding:'var(--space-5)',display:'grid',gap:'var(--space-4)'}} className="no-print">
      <p className="t-eyebrow" style={{margin:0}}>Where and when</p>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(190px,1fr))',gap:'var(--space-4)'}}>
        <TextField label="Place" defaultValue={polar?'Longyearbyen, SJ':'Athens, GR'} hint="Type a town, or use your location."/>
        <TextField label="From" type="date" defaultValue="2026-09-07"/>
        <SelectField label="Range" value={range} onChange={e=>setRange(e.target.value)}
          options={['One day','One week','One month']}/>
        {solar&&<SelectField label="Preset" value={preset} onChange={e=>setPreset(e.target.value)}
          options={['Hellenic','Thelemic','None — times only']}/>}
      </div>
      <div style={{display:'flex',gap:'8px 16px',flexWrap:'wrap',alignItems:'center'}}>
        <Button>Reckon</Button>
        <Button variant="secondary">Use my location</Button>
        <span style={{font:'400 var(--text-xs)/1.6 var(--font-mono)',color:'var(--ink-faint)'}}>One month is the cap — ask for more and it is refused, not quietly trimmed.</span>
      </div>
      <div style={{background:'var(--surface-inset)',borderRadius:'var(--radius-sm)',padding:'var(--space-3) var(--space-4)',display:'grid',gap:4}}>
        <span className="t-eyebrow" style={{margin:0}}>Resolved to</span>
        <span className="t-tabular" style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink)'}}>
          {polar?'Longyearbyen · 78.2232°N 15.6267°E · Arctic/Longyearbyen (GMT+2)':'Athens · 37.9838°N 23.7275°E · Europe/Athens · EEST (GMT+3)'}
        </span>
        <span style={{font:'400 var(--text-xs)/1.6 var(--font-body)',color:'var(--ink-faint)'}}>Check it. A station table for the wrong city is indistinguishable from a right one until someone misses a dawn.</span>
      </div>
    </div>

    {polar&&solar
      ?<NextStation name="Sunrise" at="—" inLabel="—"
        undefinedReason="The Sun does not rise here today, so there is no solar station to count toward. The lunar stations still hold, and the sky and the reckonings below are unaffected."/>
      :<NextStation glyph={solar?'☉︎':'☾︎'} name={solar?'Sunset':'Moonrise'} at={solar?'20:05':'17:41'} inLabel={solar?'2h 14m':'41m'}
        currentName={solar?'Noon':'Nadir'} currentSince={solar?'13:29':'10:48'}
        attribution={solar&&attributions?attributions[2]:undefined} progress={solar?0.62:0.88}/>}

    <div style={{display:'grid',gap:'var(--space-4)'}}>
      <div style={{display:'flex',alignItems:'baseline',gap:12,flexWrap:'wrap'}}>
        <h2 style={{font:'600 var(--text-h3) var(--font-display)',color:'var(--ink)',margin:0}}>{range==='One day'?'Today':range==='One week'?'This week':'The month'}</h2>
        <Badge tone="faint">prints on one sheet</Badge>
        <Button variant="ghost" className="no-print" onClick={()=>window.print()}>Print</Button>
      </div>
      {polar&&solar
        ?<StationTable stations={SOLAR.stations} rows={[]}
          undefinedReason={<>At <span className="t-tabular" style={{fontFamily:'var(--font-mono)',fontSize:'var(--text-sm)'}}>78.22°N</span> the Sun neither rises nor sets on these dates, so sunrise, noon, sunset and midnight have no times to give. They are undefined here, not zero — and the planetary hours that divide them are undefined with them. The lunar stations are unaffected: the Moon still rises, most days.</>}/>
        :<StationTable stations={S.stations} glyphs={S.glyphs} attributions={attributions||[]} rows={rows}
          absentLabel={solar?'none today':'no moonrise today'}
          caption={(polar?'Longyearbyen · 78.22°N 15.63°E':'Athens · 37.98°N 23.73°E')+' · shown in your local time · Swiss Ephemeris 2.10.03'}/>}
      {!solar&&<p style={{font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-faint)',margin:0,maxWidth:'74ch'}}>
        A cell reading “no moonrise today” is the sky, not a gap in the data. The Moon rises about fifty minutes later each day, so now and then it skips a civil day entirely — and at high latitude whole weeks can pass without one.
      </p>}
    </div>

    <ExportBlock
      feedHref={'webcal://theourgia.com/stations/ical?kind='+kind+'&place=athens'+(solar?'&preset='+PRESET_KEY[preset]:'')}
      fileHref={'/stations/ical?kind='+kind+'&place=athens&from=2026-09-07&to=2026-10-06'}
      fileName={kind+'-stations-athens-2026-09.ics'}
      fileScope="7 Sep – 6 Oct 2026 · 120 events"
      googleLinks={S.stations.map((s,i)=>({label:s,glyph:S.glyphs[i],href:'#'}))}
      meta={'Athens · '+(solar?(preset==='None — times only'?'times only':preset.toLowerCase()+' preset'):'lunar')+' · your local time'}
      onCopyFeed={()=>{setCopied(true);setTimeout(()=>setCopied(false),1600)}}
      copyLabel={copied?'Copied':'Copy feed URL'}/>

    <div style={{borderTop:'1px solid var(--line)',paddingTop:'var(--space-4)',display:'flex',gap:'8px 22px',flexWrap:'wrap',fontSize:'var(--text-sm)'}} className="no-print">
      <a href="#today" style={{color:'var(--accent)',textDecoration:'none'}}>◐ Day at a glance</a>
      <a href={solar?'#lunar-stations':'#solar-stations'} style={{color:'var(--accent)',textDecoration:'none'}}>{solar?'☾︎ Lunar stations':'☉︎ Solar stations'}</a>
      <a href="#" style={{color:'var(--accent)',textDecoration:'none'}}>☉ Planetary hours</a>
      <a href="#work" style={{color:'var(--accent)',textDecoration:'none'}}>All instruments</a>
    </div>
  </main>;
}
Object.assign(window,{StationsScreen});