const {SectionHeader,SubscribeBlock,Button,Badge,EmptyState,Toast,Pagination,LegalImprint}=window.ShrutiDesignSystem_cb687f;

const ISSUES=[
  {no:'08',date:'2026-08-01',title:'What the retrograde actually asks',blurb:'Mercury back through Leo, the Attic month turning, and why I rewrote the sigil compiler twice.'},
  {no:'07',date:'2026-07-01',title:'Building the calendar that argues with itself',blurb:'Intercalation, two authorities, one date — and a stream schedule that finally held.'},
  {no:'06',date:'2026-06-01',title:'On being weighed',blurb:'Saturn, the offerings ledger, and the first six divination systems shipped.'},
  {no:'05',date:'2026-05-01',title:'The hours are not sixty minutes',blurb:'Planetary hours went live. Also: what I got wrong about sunrise.'}
];

function NewsletterScreen({view,go}){
  const [email,setEmail]=React.useState('');
  const [ok,setOk]=React.useState(false);
  const [err,setErr]=React.useState(null);
  const [sent,setSent]=React.useState(false);
  const [prefs,setPrefs]=React.useState({horoscope:true,videos:true,streams:true,articles:true,letter:true});
  const [cadence,setCadence]=React.useState('monthly');
  const [toast,setToast]=React.useState(null);
  const submit=e=>{e.preventDefault();
    if(!/^\S+@\S+\.\S+$/.test(email)){setErr('That address doesn’t look complete.');return}
    if(!ok){setErr('The consent box needs ticking — without it there is no lawful way to send you anything.');return}
    setErr(null);setSent(true)};

  if(view==='confirm')return <main className="site-main page">
    <EmptyState glyph="☾" title="You’re on the list"
      body="Confirmed. The next letter goes out on the first of the month, in the morning, Athens time. If you have an account with a saved nativity, your horoscope rides along with it."
      action={<div style={{display:'flex',gap:10,flexWrap:'wrap'}}><Button href="#newsletter-archive">Read a past issue</Button><Button variant="secondary" href="#newsletter-preferences">Choose what you get</Button></div>}/>
    <p style={{font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-faint)',margin:0,textAlign:'center'}}>Confirmed 24 Aug 2026 · this is the record of your consent, and you can withdraw it in one click from any letter.</p>
  </main>;

  if(view==='unsubscribed')return <main className="site-main page">
    <EmptyState glyph="○" title="Unsubscribed"
      body="Done, immediately, and no sign-in was needed. You will get nothing further. If it was the frequency rather than the letter itself, a pause keeps your place instead."
      action={<div style={{display:'flex',gap:10,flexWrap:'wrap'}}><Button variant="secondary" href="#newsletter-preferences">Pause instead</Button><Button variant="ghost" href="#home">Back to the site</Button></div>}/>
    <p style={{font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)',margin:'0 auto',maxWidth:'52ch',textAlign:'center'}}>No survey, no “are you sure”, no offer to win you back. If you want to return, the subscribe form is where it always was.</p>
  </main>;

  if(view==='preferences')return <main className="site-main page">
    <SectionHeader as="h1" glyph="◐" eyebrow="The monthly letter" title="What you get"
      body="Turn sections off rather than the whole letter off. A pause keeps your place — it is not the same as leaving."/>
    <div style={{display:'grid',gap:'var(--space-5)',maxWidth:620}}>
      <div style={{display:'grid',gap:'var(--space-2)'}}>
        {[['horoscope','Your horoscope','Pulled from your saved nativity. Needs an account.'],
          ['videos','Videos since the last letter','Twitch and YouTube.'],
          ['streams','Streams since the last letter','What happened, and what got built in them.'],
          ['articles','Article summaries','A paragraph each, with links.'],
          ['letter','The letter itself','Written by hand. This is the part people subscribe for.']].map(([k,n,d])=>
          <label key={k} style={{display:'grid',gridTemplateColumns:'20px 1fr',gap:'2px 12px',padding:'var(--space-3) var(--space-4)',background:'var(--surface-card)',border:'1px solid var(--line)',borderRadius:'var(--radius-md)',cursor:'pointer'}}>
            <input type="checkbox" checked={prefs[k]} onChange={e=>setPrefs(s=>({...s,[k]:e.target.checked}))} style={{width:17,height:17,margin:'2px 0 0',accentColor:'var(--accent)',cursor:'pointer'}}/>
            <span style={{display:'grid',gap:2}}>
              <span style={{font:'500 var(--text-body) var(--font-body)',color:'var(--ink)'}}>{n}</span>
              <span style={{font:'400 var(--text-sm)/1.5 var(--font-body)',color:'var(--ink-soft)'}}>{d}</span>
            </span>
          </label>)}
      </div>
      <div style={{display:'grid',gap:'var(--space-3)'}}>
        <span className="t-eyebrow" style={{margin:0}}>Cadence</span>
        <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
          {[['monthly','Monthly'],['quarterly','Every third letter'],['paused','Paused']].map(([k,l])=>
            <Button key={k} variant={cadence===k?'secondary':'ghost'} onClick={()=>setCadence(k)}>{l}</Button>)}
        </div>
        {cadence==='paused'&&<p style={{font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)',margin:0,maxWidth:'56ch'}}>Paused indefinitely. Nothing is sent, nothing is deleted, and one click here starts it again whenever you want it. Your address stays on the list with consent intact.</p>}
      </div>
      <div style={{display:'flex',gap:10,flexWrap:'wrap',alignItems:'center'}}>
        <Button onClick={()=>setToast('Preferences saved.')}>Save preferences</Button>
        <Button variant="ghost" href="#newsletter-unsubscribed">Unsubscribe completely</Button>
      </div>
    </div>
    {toast&&<div style={{position:'fixed',right:18,bottom:70,zIndex:60}}><Toast tone="success" title={toast} onDismiss={()=>setToast(null)}/></div>}
  </main>;

  if(view==='archive')return <main className="site-main page">
    <SectionHeader as="h1" glyph="⁂" eyebrow="The monthly letter" title="Past issues"
      body="Every letter, public, so you can see exactly what you would be getting before you give an address."/>
    <div>
      {ISSUES.map(i=><a key={i.no} href="#newsletter-archive" style={{display:'grid',gridTemplateColumns:'86px 1fr auto',gap:'var(--space-4)',alignItems:'baseline',padding:'18px 0',borderBottom:'1px solid var(--line)',textDecoration:'none',color:'inherit'}}>
        <span className="t-tabular" style={{font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-faint)'}}>{i.date}</span>
        <span>
          <h3 style={{font:'600 var(--text-h4) var(--font-display)',color:'var(--ink)',margin:0}}>{i.title}</h3>
          <p style={{font:'400 var(--text-sm)/1.55 var(--font-body)',color:'var(--ink-soft)',margin:'4px 0 0'}}>{i.blurb}</p>
        </span>
        <span className="t-tabular" style={{font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-faint)'}}>№ {i.no}</span>
      </a>)}
    </div>
    <div style={{display:'flex',justifyContent:'center'}}><Pagination page={1} pageCount={2} onChange={()=>{}}/></div>
    <SubscribeBlock variant="inline" heading="Start with the next one" body="Once a month. You have just seen four of them, so there are no surprises."/>
  </main>;

  return <main className="site-main page">
    <SectionHeader as="h1" glyph="☾" eyebrow="The monthly letter" title="Once a month, from Athens"
      body="Your horoscope, the videos and streams since the last one, a paragraph on anything I published, and a letter written by hand. That last part is the reason to subscribe."/>
    <div style={{display:'grid',gridTemplateColumns:'1.1fr 1fr',gap:'var(--space-6)',alignItems:'start'}} className="about-cols">
      <SubscribeBlock email={email} onEmailChange={e=>{setEmail(e.target.value);setErr(null)}}
        consented={ok} onConsentChange={e=>{setOk(e.target.checked);setErr(null)}}
        onSubmit={submit} error={err} state={sent?'sent':'idle'}/>
      <div style={{display:'grid',gap:'var(--space-4)'}}>
        <div style={{display:'grid',gap:8}}>
          <span className="t-eyebrow" style={{margin:0}}>What is in it</span>
          <ul style={{margin:0,paddingLeft:18,display:'grid',gap:6,font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)'}}>
            <li><strong style={{fontWeight:600,color:'var(--ink)'}}>Your horoscope</strong>, automatically, if you have a saved nativity</li>
            <li>Videos posted since the last issue</li>
            <li>Streams since the last issue</li>
            <li>Summaries of anything written on the site</li>
            <li><strong style={{fontWeight:600,color:'var(--ink)'}}>A letter written by hand</strong></li>
          </ul>
        </div>
        <div style={{background:'var(--surface-inset)',borderRadius:'var(--radius-md)',padding:'var(--space-4)',display:'grid',gap:6}}>
          <span className="t-eyebrow" style={{margin:0}}>Said plainly</span>
          <p style={{margin:0,font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)'}}>This list will eventually carry offers for astrological courses and magickal services. I would rather tell you that now than have you find out in issue four.</p>
        </div>
        <div style={{display:'flex',gap:'8px 14px',flexWrap:'wrap',alignItems:'center'}}>
          <Badge tone="faint">double opt-in</Badge><Badge tone="faint">one click out</Badge><Badge tone="faint">no tracking pixels</Badge>
        </div>
        <p style={{font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-faint)',margin:0}}>
          <a href="#newsletter-archive" style={{color:'var(--accent)'}}>Read past issues</a> · <a href="#newsletter-preferences" style={{color:'var(--accent)'}}>Preferences</a> · <a href="#privacy" style={{color:'var(--accent)'}}>What is stored</a>
        </p>
      </div>
    </div>
    <div style={{borderTop:'1px solid var(--line)',paddingTop:'var(--space-5)',display:'flex',gap:'var(--space-5)',flexWrap:'wrap',alignItems:'flex-start'}}>
      <div style={{flex:'1 1 280px'}}>
        <span className="t-eyebrow" style={{margin:'0 0 8px',display:'block'}}>Who is sending it</span>
        <p style={{font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)',margin:0,maxWidth:'46ch'}}>Every letter carries the same imprint as this site, because a marketing email legally must.</p>
      </div>
      <LegalImprint/>
    </div>
  </main>;
}
Object.assign(window,{NewsletterScreen});