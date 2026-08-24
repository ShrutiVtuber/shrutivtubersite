const {SectionHeader,SignPicker,PeriodSwitcher,Prose,Button,Badge,EmptyState,SubscribeBlock,Breadcrumb}=window.ShrutiDesignSystem_cb687f;
const SIGNS=window.SHRUTI_SIGNS;

const READINGS={
  virgo:{title:'Virgo',glyph:'♍︎',lede:'A month for finishing, which is not the same as a month for starting.',
    body:['Mercury, your ruler, spends the first fortnight in your own sign and the second in Libra, which is the difference between thinking about your own work and thinking about someone else’s opinion of it. Do the private part first. The full moon on the 27th falls across the axis of what you own and what you owe, and it will make one of those two feel much larger than it is.',
      'The stationary retrograde of Saturn on the 9th sits in your seventh, so an agreement you have been carrying alone stops being carryable alone. That is not a failure of yours; it is a fact about the arrangement. Say the true thing about it early in the month, while there is still room to alter terms rather than only to leave.',
      'Toward the 22nd the Sun crosses into Libra and the season turns. Whatever you have been perfecting, ship it before then, imperfect. The instrument that exists is worth more than the one that would have been better.']},
  aries:{title:'Aries',glyph:'♈︎',lede:'The work comes back to you, and it comes back changed.',
    body:['Mars leaves your twelfth this month, which is the astrological equivalent of a fever breaking. Energy you could not find in August is simply available in September, and the risk is spending all of it in the first week.',
      'Saturn stations in your first. You are not being punished; you are being weighed. Answer the weighing honestly and it becomes a foundation.']}
};
const DEFAULT_READING={lede:'This month’s reading, written by hand.',body:['Twelve are written each month, one per sign, in the last week of the month before. This one is here.','A second paragraph carries the timing — a station, an ingress, a lunation — and says plainly what it asks of you.']};

function HoroscopeIndex({sign,setSign,ownSign,signedIn}){
  return <main className="site-main page">
    <SectionHeader as="h1" glyph="☉" eyebrow="Horoscopes" title="September 2026"
      body="Twelve readings, written by hand in the last week of August. Pick your sign — the choice is remembered."/>
    {signedIn&&ownSign
      ?<div style={{display:'flex',alignItems:'center',gap:12,flexWrap:'wrap',padding:'var(--space-4)',background:'var(--accent-wash)',borderRadius:'var(--radius-md)'}}>
        <span className="t-glyph" style={{font:'400 1.5rem var(--font-display)',lineHeight:1,color:'var(--rose)'}} aria-hidden="true">♍︎</span>
        <span style={{font:'400 var(--text-body)/1.5 var(--font-body)',color:'var(--ink)',flex:'1 1 240px'}}>You read as <strong style={{fontWeight:600}}>Virgo</strong>, from your saved nativity — so it is open below without asking.</span>
        <Button variant="secondary" href="#horoscope">Read mine</Button>
      </div>
      :<div style={{display:'flex',alignItems:'center',gap:12,flexWrap:'wrap',padding:'var(--space-4)',border:'1px solid var(--line)',borderRadius:'var(--radius-md)'}}>
        <span style={{font:'400 var(--text-sm)/1.5 var(--font-body)',color:'var(--ink-soft)',flex:'1 1 240px'}}>With an account and a saved nativity, your sign opens first and arrives in the monthly letter. Reading without one works exactly the same otherwise.</span>
        <Button variant="ghost" href="#signup">Make an account</Button>
      </div>}
    <SignPicker layout="grid" current={sign} onChange={setSign} ownSign={ownSign}/>
    <div style={{borderTop:'1px solid var(--line)',paddingTop:'var(--space-5)',display:'grid',gap:'var(--space-4)'}}>
      <div style={{display:'flex',alignItems:'baseline',gap:12,flexWrap:'wrap'}}>
        <h2 style={{font:'600 var(--text-h3) var(--font-display)',color:'var(--ink)',margin:0}}>The sky this month</h2>
        <span className="t-tabular" style={{font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-faint)'}}>the same for everyone, whatever your sign</span>
      </div>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(200px,1fr))',gap:'var(--space-3)'}}>
        {[['♄','Saturn stations retrograde','9 Sep · 04:12 EEST'],['☉','Sun enters Libra','22 Sep · 20:05 EEST'],['☾','Full moon in Pisces','27 Sep · 05:49 EEST'],['☿','Mercury enters Libra','14 Sep · 11:38 EEST']].map(([g,n,t])=>
          <div key={n} style={{background:'var(--surface-card)',border:'1px solid var(--line)',borderRadius:'var(--radius-md)',boxShadow:'var(--shadow-1)',padding:'var(--space-4)',display:'grid',gap:4}}>
            <span aria-hidden="true" className="t-glyph" style={{font:'400 1.25rem var(--font-display)',lineHeight:1,color:'var(--rose)'}}>{g}</span>
            <span style={{font:'600 var(--text-sm) var(--font-body)',color:'var(--ink)'}}>{n}</span>
            <span className="t-tabular" style={{font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-soft)'}}>{t}</span>
          </div>)}
      </div>
      <p style={{font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-faint)',margin:0}}>Times from the ephemeris, in Athens, converted to your zone. <a href="#" style={{color:'var(--accent)'}}>Reckon it yourself</a></p>
    </div>
    <SubscribeBlock variant="inline" heading="Get it by email" body="Your sign, monthly, with what I published and streamed and a letter written by hand."/>
  </main>;
}

function HoroscopeReading({sign,setSign,period,setPeriod,ownSign}){
  const r=READINGS[sign]||{...DEFAULT_READING,title:(SIGNS.find(s=>s.key===sign)||{}).name||'Reading',glyph:(SIGNS.find(s=>s.key===sign)||{}).glyph||'✶'};
  const mine=ownSign===sign;
  return <main className="site-main page">
    <Breadcrumb items={[{label:'Horoscopes',href:'#horoscopes'},{label:r.title}]}/>
    <PeriodSwitcher current={period} available={['monthly']} onChange={setPeriod} label="September 2026"/>
    <div style={{display:'flex',alignItems:'flex-start',gap:'var(--space-4)',flexWrap:'wrap'}}>
      <span aria-hidden="true" className="t-glyph" style={{font:'400 clamp(2.5rem,7vw,3.5rem) var(--font-display)',lineHeight:1,color:'var(--rose)'}}>{r.glyph}</span>
      <div style={{flex:'1 1 260px',minWidth:0}}>
        <div style={{display:'flex',alignItems:'baseline',gap:10,flexWrap:'wrap'}}>
          <h1 style={{font:'500 var(--text-h1) var(--font-display)',letterSpacing:'var(--tracking-display)',color:'var(--ink)',margin:0}}>{r.title}</h1>
          {mine&&<Badge tone="rose">your sign</Badge>}
        </div>
        <p style={{font:'400 var(--text-prose)/1.6 var(--font-display)',color:'var(--ink-soft)',margin:'8px 0 0',maxWidth:'44ch'}}>{r.lede}</p>
      </div>
    </div>
    <Prose byline="Soror Eu. A.">
      {r.body.map((p,i)=><p key={i}>{p}</p>)}
    </Prose>
    <div style={{display:'flex',gap:10,flexWrap:'wrap',alignItems:'center',paddingTop:'var(--space-4)',borderTop:'1px solid var(--line)'}}>
      <Button variant="secondary" href="#horoscopes">All twelve</Button>
      <Button variant="ghost" href="#">Copy link</Button>
      <span style={{font:'400 var(--text-xs)/1.6 var(--font-mono)',color:'var(--ink-faint)',flex:'1 1 200px'}}>Shareable, with a preview card for Discord and elsewhere.</span>
    </div>
    <div style={{display:'grid',gap:'var(--space-3)'}}>
      <span className="t-eyebrow" style={{margin:0}}>Another sign</span>
      <SignPicker layout="row" current={sign} onChange={setSign} ownSign={ownSign}/>
    </div>
    <SubscribeBlock variant="inline"/>
  </main>;
}
Object.assign(window,{HoroscopeIndex,HoroscopeReading});