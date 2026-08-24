const {SectionHeader,TextField,SelectField,Button,ConsentCheckbox,Badge,Modal,Toast,EmptyState,ProfileFieldTable}=window.ShrutiDesignSystem_cb687f;

function NativityForm({onSaved}){
  const [f,setF]=React.useState({date:'1996-06-21',time:'04:12',place:'Athens, GR'});
  const [unknown,setUnknown]=React.useState(false);
  const [resolved,setResolved]=React.useState({name:'Athens, Attica, Greece',lat:'37.9838°N',lon:'23.7275°E',tz:'Europe/Athens · EEST (GMT+3)'});
  const set=k=>e=>setF(s=>({...s,[k]:e.target.value}));
  return <form onSubmit={e=>{e.preventDefault();onSaved&&onSaved()}} style={{display:'grid',gap:'var(--space-5)',maxWidth:620}}>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))',gap:'var(--space-4)'}}>
      <TextField label="Birth date" type="date" required value={f.date} onChange={set('date')}/>
      <TextField label="Birth time" type="time" optionalLabel disabled={unknown} value={unknown?'':f.time} onChange={set('time')}
        hint={unknown?'Left out — see below.':'Local clock time at the place of birth.'}/>
    </div>

    <div style={{background:'var(--surface-card)',border:'1px solid var(--line)',borderRadius:'var(--radius-md)',padding:'var(--space-4)',display:'grid',gap:10}}>
      <label style={{display:'grid',gridTemplateColumns:'20px 1fr',gap:'2px 10px',cursor:'pointer'}}>
        <input type="checkbox" checked={unknown} onChange={e=>setUnknown(e.target.checked)} style={{width:17,height:17,margin:'2px 0 0',accentColor:'var(--accent)',cursor:'pointer'}}/>
        <span style={{font:'500 var(--text-body)/1.5 var(--font-body)',color:'var(--ink)'}}>I don’t know my birth time</span>
      </label>
      <p style={{margin:0,font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)',maxWidth:'62ch'}}>
        That is a perfectly ordinary answer, and it is not an error. Here is what it costs: the ascendant moves a degree every four minutes, so without a time the <strong style={{fontWeight:600,color:'var(--ink)'}}>ascendant, midheaven, houses and sect are undefined</strong>. Planets stay where they were, give or take the Moon, which can cross half a sign in a day.
      </p>
      <p style={{margin:0,font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-faint)'}}>
        You still get: sign positions, aspects, your horoscope sign. You do not get: houses, angles, sect, anything timed to the ascendant.
      </p>
    </div>

    <div style={{display:'grid',gap:'var(--space-3)'}}>
      <TextField label="Birth place" required value={f.place} onChange={set('place')} hint="Search a town or city — this resolves to coordinates and the timezone that applied on that date."/>
      <div style={{background:'var(--surface-inset)',borderRadius:'var(--radius-sm)',padding:'var(--space-3) var(--space-4)',display:'grid',gap:6}}>
        <span className="t-eyebrow" style={{margin:0}}>Resolved to</span>
        <span style={{font:'500 var(--text-sm) var(--font-body)',color:'var(--ink)'}}>{resolved.name}</span>
        <span className="t-tabular" style={{font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-soft)'}}>{resolved.lat} {resolved.lon} · {resolved.tz}</span>
        <span style={{font:'400 var(--text-xs)/1.6 var(--font-body)',color:'var(--ink-faint)'}}>Check this. A chart cast for the wrong city is indistinguishable from a right one. <a href="#nativity" style={{color:'var(--accent)'}}>Not this place?</a></span>
      </div>
    </div>

    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))',gap:'var(--space-4)'}}>
      <SelectField label="Preferred tradition" options={[{value:'hel',label:'Hellenistic'},{value:'ved',label:'Vedic'}]} defaultValue="hel"/>
      <SelectField label="House system" options={['Whole sign','Placidus','Equal','Porphyry','Regiomontanus','Campanus']} defaultValue="Whole sign"/>
      <SelectField label="Ayanāṁśa" hint="Used when you read sidereally." options={['Lahiri · Chitrapakṣa','B. V. Raman','Krishnamurti','Fagan–Bradley','Yukteshwar','True Citrā']} defaultValue="Lahiri · Chitrapakṣa"/>
    </div>

    <p style={{margin:0,font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-faint)',maxWidth:'70ch'}}>
      This is everything the ephemeris needs and nothing more. No address, no phone number, no gender field — the calculation does not use them, so they are not asked for.
    </p>
    <div style={{display:'flex',gap:10,flexWrap:'wrap'}}><Button type="submit">Save nativity</Button><Button variant="ghost" href="#account">Cancel</Button></div>
  </form>;
}

function AccountScreen({tab,go}){
  const [toast,setToast]=React.useState(null);
  const [confirmDelete,setConfirmDelete]=React.useState(false);
  const [c,setC]=React.useState({birth:true,letter:true});
  const T=[['profile','Profile'],['nativity','Nativity'],['consents','Consents & data']];
  return <main className="site-main page">
    <SectionHeader as="h1" glyph="☾" eyebrow="Your account" title="Settings"
      body="Small on purpose. There are no public profiles here and nothing to decorate — this holds how you read, and what you have agreed to."/>

    <div style={{display:'flex',gap:8,flexWrap:'wrap',paddingBottom:'var(--space-4)',borderBottom:'1px solid var(--line)'}}>
      {T.map(([k,l])=><Button key={k} variant={tab===k?'secondary':'ghost'} onClick={()=>go(k)}>{l}</Button>)}
    </div>

    {tab==='profile'&&<div style={{display:'grid',gap:'var(--space-5)',maxWidth:620}}>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(200px,1fr))',gap:'var(--space-4)'}}>
        <TextField label="Display name" defaultValue="Ariadne" hint="Only ever shown back to you."/>
        <TextField label="Email" type="email" defaultValue="reader@example.com"/>
        <SelectField label="Timezone" options={['Europe/Athens (GMT+3)','Europe/London (GMT+1)','America/New_York (GMT−4)','Asia/Kolkata (GMT+5:30)']} defaultValue="Europe/Athens (GMT+3)"/>
        <SelectField label="Reading language" options={['English','Ελληνικά','हिन्दी','Français']} defaultValue="English"/>
      </div>
      <div style={{display:'flex',gap:10}}><Button onClick={()=>setToast('Profile saved.')}>Save</Button></div>
      <div style={{borderTop:'1px solid var(--line)',paddingTop:'var(--space-4)'}}>
        <p style={{font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)',margin:0,maxWidth:'60ch'}}>
          There is no profile picture, no bio, no follower count and no public page. This is not that kind of site, and adding those is scope it does not have.
        </p>
      </div>
    </div>}

    {tab==='nativity'&&<div style={{display:'grid',gap:'var(--space-5)'}}>
      <div style={{display:'flex',alignItems:'center',gap:12,flexWrap:'wrap'}}>
        <h2 style={{font:'600 var(--text-h3) var(--font-display)',color:'var(--ink)',margin:0}}>Saved nativity</h2>
        <Badge tone="rose">stored with your explicit consent</Badge>
      </div>
      <NativityForm onSaved={()=>setToast('Nativity saved. Your chart and horoscope now use it.')}/>
      <div style={{borderTop:'1px solid var(--line)',paddingTop:'var(--space-4)',display:'grid',gap:8,maxWidth:620}}>
        <span className="t-eyebrow" style={{margin:0}}>More than one</span>
        <p style={{font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)',margin:0}}>One saved chart is enough to begin. If you keep more later, each one is named — this slot is “Mine”.</p>
      </div>
    </div>}

    {tab==='consents'&&<div style={{display:'grid',gap:'var(--space-6)',maxWidth:680}}>
      <div style={{display:'grid',gap:'var(--space-3)'}}>
        <div>
          <h2 style={{font:'600 var(--text-h3) var(--font-display)',color:'var(--ink)',margin:'0 0 6px'}}>What you have agreed to</h2>
          <p style={{font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)',margin:0,maxWidth:'62ch'}}>The same three decisions from sign-up, revisitable. Withdrawing is exactly as easy as giving — untick and save.</p>
        </div>
        <ConsentCheckbox basis="contract" required checked
          label="My account exists" meta="Given 12 Aug 2026"
          explanation="Withdrawing this means deleting the account — the control for that is below."/>
        <ConsentCheckbox basis="explicit consent · GDPR Art. 9" checked={c.birth} onChange={e=>setC(s=>({...s,birth:e.target.checked}))}
          label="Store my birth data for astrological readings" meta="Given 12 Aug 2026 · withdraw any time"
          explanation="Untick and save, and the saved nativity is deleted with it. Your account stays; your horoscope goes back to whichever sign you pick by hand."/>
        <ConsentCheckbox basis="consent · marketing" checked={c.letter} onChange={e=>setC(s=>({...s,letter:e.target.checked}))}
          label="Send me the monthly letter, including offers" meta="Given 12 Aug 2026 · withdraw any time"
          explanation="Untick to come off the list entirely. To keep it but hear less, pause it instead in the letter’s preference centre."/>
        <div style={{display:'flex',gap:10,flexWrap:'wrap'}}><Button onClick={()=>setToast('Consents updated.')}>Save consents</Button><Button variant="ghost" href="#newsletter-preferences">Letter preferences</Button></div>
      </div>

      <div style={{display:'grid',gap:'var(--space-3)'}}>
        <h2 style={{font:'600 var(--text-h3) var(--font-display)',color:'var(--ink)',margin:0}}>Your data</h2>
        <div style={{background:'var(--surface-card)',border:'1px solid var(--line)',borderRadius:'var(--radius-md)',boxShadow:'var(--shadow-1)',padding:'var(--space-4)',display:'grid',gap:8}}>
          <span style={{font:'600 var(--text-body) var(--font-body)',color:'var(--ink)'}}>Export everything</span>
          <p style={{margin:0,font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)',maxWidth:'58ch'}}>A JSON file with your profile, your saved nativity, your consent history and the dates, and which letters were sent to you. It downloads here — no email, no waiting on a request.</p>
          <div><Button variant="secondary" onClick={()=>setToast('Export ready — check your downloads.')}>Download my data</Button></div>
        </div>
        <div style={{background:'var(--surface-card)',border:'1px solid var(--line)',borderRadius:'var(--radius-md)',boxShadow:'var(--shadow-1)',padding:'var(--space-4)',display:'grid',gap:8}}>
          <span style={{font:'600 var(--text-body) var(--font-body)',color:'var(--ink)'}}>Delete my account</span>
          <p style={{margin:0,font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)',maxWidth:'58ch'}}>Everything above goes, including the saved nativity, and your address comes off the letter list at the same time — not just the account.</p>
          <div><Button variant="secondary" onClick={()=>setConfirmDelete(true)}>Delete my account</Button></div>
        </div>
      </div>
    </div>}

    <Modal open={confirmDelete} onClose={()=>setConfirmDelete(false)} title="Delete your account"
      footer={<div style={{display:'flex',gap:10,justifyContent:'flex-end',flexWrap:'wrap'}}>
        <Button variant="ghost" onClick={()=>setConfirmDelete(false)}>Keep my account</Button>
        <Button variant="live" onClick={()=>{setConfirmDelete(false);setToast('Account deleted. The letter list has been updated too.')}}>Delete everything</Button>
      </div>}>
      <div style={{display:'grid',gap:14}}>
        <p style={{margin:0,font:'400 var(--text-body)/1.6 var(--font-body)',color:'var(--ink)'}}>Plainly, so there is no surprise afterwards:</p>
        <div style={{display:'grid',gap:6}}>
          <span className="t-eyebrow" style={{margin:0}}>What goes</span>
          <ul style={{margin:0,paddingLeft:18,display:'grid',gap:4,font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)'}}>
            <li>Your email, display name and preferences</li>
            <li>Your saved nativity — date, time, place, coordinates</li>
            <li>Your subscription to the monthly letter</li>
          </ul>
        </div>
        <div style={{display:'grid',gap:6}}>
          <span className="t-eyebrow" style={{margin:0}}>What is kept, and why</span>
          <ul style={{margin:0,paddingLeft:18,display:'grid',gap:4,font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)'}}>
            <li>A record that consent was given and withdrawn, with dates and nothing else — that record is the proof the law asks for, and it holds no birth data</li>
            <li>Any invoice, if you ever bought something, for as long as tax law requires</li>
          </ul>
        </div>
        <p style={{margin:0,font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-faint)'}}>Immediate and not reversible. There is no thirty-day grace period holding your data hostage.</p>
      </div>
    </Modal>
    {toast&&<div style={{position:'fixed',right:18,bottom:70,zIndex:60}}><Toast tone="success" title={toast} onDismiss={()=>setToast(null)}/></div>}
  </main>;
}
Object.assign(window,{AccountScreen,NativityForm});