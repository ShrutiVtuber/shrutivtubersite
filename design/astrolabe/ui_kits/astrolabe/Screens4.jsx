/* Screens 11–12, 14–18: one work, the writing screen, account, notifications,
   licences, the place picker and the sky drawer. */

function WorkScreen({ s, go }) {
  const A = window.AL;
  const [vote, setVote] = React.useState(1);
  return <>
    <AppBar title="A reading" back onBack={()=>go(null)} hour={false}
      actions={<><IconButton icon="ios_share" label="Share"/><IconButton icon="more_vert" label="More"/></>}/>
    <Body pad={16} gap={16}>
      <header style={{ display:'grid', gap:10 }}>
        <span className="t-eyebrow">Practice · Capricorn</span>
        <h1 style={{ margin:0, font:'500 26px/1.22 var(--font-display)', color:'var(--ink)', textWrap:'pretty' }}>
          Saturn on the descendant, and what it asked of me</h1>
        <div style={{ display:'flex', alignItems:'center', gap:10 }}>
          <span aria-hidden="true" style={{ width:24, height:24, borderRadius:99, background:'var(--veil)',
            border:'1px solid var(--line)' }}/>
          <span className="t-caption" style={{ color:'var(--soft)' }}>korax</span>
          <span className="t-caption" aria-hidden="true">·</span>
          <span className="t-caption t-tabular">9 September, 18:20 Athens</span>
        </div>
      </header>
      <div style={{ display:'flex', alignItems:'center', gap:16, padding:'12px 14px',
        background:'var(--inset)', border:'1px solid var(--line)', borderRadius:'var(--radius-md)' }}>
        <VoteControl value={14 + (vote===1?0:vote===-1?-2:-1)} mine={s.signedIn?vote:0}
          onVote={s.signedIn?setVote:undefined} disabled={!s.signedIn}/>
        <div style={{ flex:1, minWidth:0 }}>
          <div className="t-caption" style={{ color:'var(--soft)' }}>
            {s.signedIn ? 'Your vote is counted and can be changed.' : 'Sign in to vote or comment.'}</div>
        </div>
        <Button size="sm" variant="outlined" onClick={()=>{}}>Comment</Button>
      </div>
      <Prose drop>
        <p>I have had this transit for eleven months and I have spent most of them arguing with it.
          Saturn came to the seventh by whole sign last November, and the first thing it did was
          make every conversation take twice as long.</p>
        <p>What changed was not the transit. What changed was that I stopped treating the descendant
          as a place where other people happen to me.</p>
        <blockquote>Saturn does not ask. It invoices — and then it asks whether you were going to
          pay in instalments.</blockquote>
        <p>The chart is tropical, whole sign, cast for 14:05 in Thessaloniki. I am not confident
          about the seventh-house ruler and I would like to be argued with about it.</p>
        {s.longContent && <>
          <h2>The method, at length</h2>
          <p>What follows is the part nobody asked for. I looked at every ingress into the seventh
            for the last four years, and I logged what I noticed within the week either side.</p>
          <p>The pattern that survived the log is not the one I expected, and it is the only reason
            I am posting this rather than keeping it in the notes app where it has lived since March.</p>
        </>}
      </Prose>
      <div className="rule">{A.G.saturn}{'\ufe0e'}</div>
      <section style={{ display:'grid', gap:12 }}>
        <SectionHeader eyebrow={`${A.comments.length} comments`} title="The room"/>
        {A.comments.map(c => <div key={c.id} style={{ display:'grid', gridTemplateColumns:'auto 1fr',
          gap:12, alignItems:'start' }}>
          <VoteControl value={c.votes} compact disabled={!s.signedIn}/>
          <div style={{ minWidth:0, display:'grid', gap:5 }}>
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <span className="t-caption" style={{ color: c.her ? 'var(--gilt)' : 'var(--soft)',
                fontWeight: c.her ? 600 : 400 }}>{c.author}</span>
              {c.her && <span className="t-eyebrow" style={{ color:'var(--gilt)' }}>Hers</span>}
              <span className="t-caption t-tabular">{c.date}</span>
            </div>
            <div style={{ font:'400 15px/1.6 var(--font-body)', color:'var(--soft)', textWrap:'pretty' }}>{c.body}</div>
          </div>
        </div>)}
        {s.signedIn
          ? <TextField label="Add a comment" multiline rows={3} placeholder="Argue with it."/>
          : <Card tone="inset"><div className="t-caption">Sign in to reply. The room keeps its own
              guidelines; they are two paragraphs long and worth reading.</div></Card>}
      </section>
    </Body>
  </>;
}

function WriteScreen({ s, go }) {
  const [saved, setSaved] = React.useState(false);
  return <>
    <AppBar title="Write a reading" back onBack={()=>go(null)} hour={false}
      actions={<Button size="sm" variant="text" onClick={()=>setSaved(true)}>Save draft</Button>}/>
    <Body pad={16} gap={14}>
      {s.offline && <Banner tone="offline" title="You are writing offline">
        Drafts live on this phone. This one will be posted when the room is reachable again.</Banner>}
      {s.error && <Banner tone="error" title="That draft did not post" action="Try again">
        The room answered, but not with a receipt. Nothing was lost.</Banner>}
      <TextField label="Title" placeholder="What is this reading about?"
        defaultValue={s.longContent ? 'A very long title that runs on past the width of a phone and keeps going' : ''}
        maxLength={120} counter value={s.longContent ? undefined : ''}/>
      <div style={{ display:'grid', gap:8 }}>
        <span className="t-eyebrow">The chart it is about</span>
        <ListGroup>
          <ListRow label="Attach a chart" description="One of yours, or cast a new one" onClick={()=>{}}/>
        </ListGroup>
      </div>
      <TextField label="The reading" multiline rows={s.longContent ? 14 : 10} maxLength={4000} counter
        placeholder="A few hundred words on one chart. It does not have to be right."
        defaultValue={s.longContent
          ? 'I have had this transit for eleven months and I have spent most of them arguing with it. Saturn came to the seventh by whole sign last November, and the first thing it did was make every conversation take twice as long.\n\nWhat changed was not the transit.'
          : ''}/>
      <div style={{ display:'grid', gap:8 }}>
        <span className="t-eyebrow">Before you post</span>
        <ChoiceRow type="checkbox" label="This is my own work"
          rule="Readings are argued with by name. Quoting somebody else is fine; passing it off is not."/>
        <ChoiceRow type="checkbox" label="Show my sign on it"
          rule="Optional. It changes how the room reads you, which is sometimes the point."/>
      </div>
      <div style={{ display:'flex', gap:10 }}>
        <Button variant="outlined" full onClick={()=>setSaved(true)}>Save draft</Button>
        <Button full disabled={!s.signedIn} onClick={()=>go(null)}>Post it</Button>
      </div>
      {!s.signedIn && <p className="t-caption" style={{ margin:0, textAlign:'center' }}>
        Drafts are kept without an account. Posting needs one.</p>}
      <Snackbar open={saved} action="Undo" onAction={()=>setSaved(false)}>Draft saved.</Snackbar>
    </Body>
  </>;
}

function AccountScreen({ s, go }) {
  if (!s.signedIn) return <>
    <AppBar title="Account" back onBack={()=>go(null)} hour={false}/>
    <Body pad={16} gap={16}>
      <div style={{ display:'grid', gap:8, marginTop:8 }}>
        <h2 style={{ margin:0, font:'500 24px/1.25 var(--font-display)', color:'var(--ink)' }}>
          An account is only for the practice room</h2>
        <p className="t-body" style={{ margin:0, textWrap:'pretty' }}>
          Everything else — the sky, the hours, the chart, the letters — works without one, offline,
          and always will.</p>
      </div>
      {s.error && <Banner tone="error" title="Sign-in failed" action="Try again">
        The site answered, but not with a token.</Banner>}
      <TextField label="Email" type="email" placeholder="you@example.com"/>
      <Button size="lg" full loading={s.loading} onClick={()=>s.set('signedIn', true)}>Send me a link</Button>
      <p className="t-caption" style={{ margin:'-4px 0 0' }}>
        No password. A link arrives, you tap it, you are in. The link works once and lasts an hour.</p>
      <div className="rule rule-plain">·</div>
      <div style={{ display:'grid', gap:4 }}>
        <span className="t-eyebrow">If you make an account</span>
        <ChoiceRow type="checkbox" label="Email me her newsletter"
          rule="About one a month. Unsubscribe in one tap, from any of them."/>
        <ChoiceRow type="checkbox" label="Tell me when somebody replies to my work"
          rule="Only replies to you. Never a digest."/>
        <ChoiceRow type="checkbox" label="I have read the room’s guidelines"
          rule="Two paragraphs. Required, and not bundled with anything else."/>
      </div>
    </Body>
  </>;
  return <>
    <AppBar title="Account" back onBack={()=>go(null)} hour={false}/>
    <Body pad={16} gap={16}>
      <Card>
        <div style={{ display:'flex', gap:14, alignItems:'center' }}>
          <span aria-hidden="true" style={{ width:48, height:48, borderRadius:99, background:'var(--veil)',
            border:'1px solid var(--line)', display:'grid', placeItems:'center' }}>
            <Glyph name="moon" tone="gilt" size="lg"/></span>
          <div style={{ minWidth:0 }}>
            <div style={{ font:'500 18px/1.3 var(--font-display)', color:'var(--ink)' }}>soror@shrutivtuber.com</div>
            <div className="t-caption" style={{ marginTop:2 }}>
              {s.member ? 'Member since March · renews 4 October' : 'Free account · joined March'}</div>
          </div>
        </div>
      </Card>
      {!s.member && <OfferCard title="Become a member" price="€6" cadence="a month" mark={window.AL.G.venus}
        body="The chart clinic, the members’ readings, and the archive." href="https://shrutivtuber.com/support"/>}
      <section style={{ display:'grid', gap:8 }}>
        <span className="t-eyebrow">Your data</span>
        <ListGroup>
          <ListRow label="Your sign" value="Capricorn" onClick={()=>{}}/>
          <ListRow label="Saved charts" value="3 on this phone" onClick={()=>{}}/>
          <ListRow label="Export everything" description="A single JSON file, sent to your email" onClick={()=>{}}/>
        </ListGroup>
      </section>
      <section style={{ display:'grid', gap:8 }}>
        <span className="t-eyebrow">Consents</span>
        <Card pad={0}><div style={{ padding:'2px 16px' }}>
          <Switch label="Her newsletter" description="About one a month" checked onChange={()=>{}}/>
          <div style={{ borderTop:'1px solid var(--line)' }}/>
          <Switch label="Replies to my work" description="Only replies to you" checked onChange={()=>{}}/>
        </div></Card>
      </section>
      <ListGroup>
        <ListRow label="Sign out" onClick={()=>s.set('signedIn', false)} chevron={false}/>
        <ListRow label="Delete this account" danger description="The readings you posted stay, without your name"
          onClick={()=>s.set('confirmDelete', true)} chevron={false}/>
      </ListGroup>
    </Body>
    <Dialog open={s.confirmDelete} title="Delete this account?"
      subtitle="Your drafts go with it. Posted readings stay, without your name."
      onClose={()=>s.set('confirmDelete', false)}
      actions={<><Button variant="text" onClick={()=>s.set('confirmDelete', false)}>Keep it</Button>
        <Button variant="outlined" destructive onClick={()=>{s.set('confirmDelete',false);s.set('signedIn',false);}}>Delete</Button></>}>
      This cannot be undone, and it is not the same as signing out.
    </Dialog>
  </>;
}

function NotificationsScreen({ s, go }) {
  const A = window.AL;
  const icons = { live:'sensors', reply:'mode_comment', sky:'clear_night', reading:'auto_stories' };
  return <>
    <AppBar title="Notifications" back onBack={()=>go(null)} hour={false}/>
    <Body pad={16} gap={16}>
      <section style={{ display:'grid', gap:8 }}>
        <span className="t-eyebrow">Tell me about</span>
        <Card pad={0}><div style={{ padding:'2px 16px' }}>
          <Switch label="When she goes live" description="Within ninety seconds" checked onChange={()=>{}}/>
          <div style={{ borderTop:'1px solid var(--line)' }}/>
          <Switch label="New readings" description="Sunday nights, twelve at once" checked onChange={()=>{}}/>
          <div style={{ borderTop:'1px solid var(--line)' }}/>
          <Switch label="Stations and ingresses" description="Computed here, so these arrive offline too"
            checked={s.signedIn} onChange={()=>{}}/>
          <div style={{ borderTop:'1px solid var(--line)' }}/>
          <Switch label="Replies to my work" description="Needs an account" checked={false}
            disabled={!s.signedIn} onChange={()=>{}}/>
        </div></Card>
        <p className="t-caption" style={{ margin:'0 4px' }}>
          The sky notifications are worked out on this phone, so they still arrive with no network.
        </p>
      </section>
      <section style={{ display:'grid', gap:10 }}>
        <SectionHeader eyebrow="Recent"/>
        {s.empty
          ? <EmptyState compact mark={A.G.moon} title="Nothing yet"
              body="When she goes live, or the sky does something worth knowing, it will be here."/>
          : A.notifications.map(n => <Card key={n.id} tone="tappable" onClick={()=>go(n.kind==='reply'?'work':null)}>
              <div style={{ display:'grid', gridTemplateColumns:'auto 1fr auto', gap:12, alignItems:'start' }}>
                <Icon name={icons[n.kind]} size={20} tone={n.kind==='live'?'live':'gilt'}/>
                <div style={{ minWidth:0 }}>
                  <div style={{ font:'500 15px/1.35 var(--font-body)', color:'var(--ink)' }}>{n.title}</div>
                  <div className="t-caption" style={{ marginTop:3, textWrap:'pretty' }}>{n.body}</div>
                  <div className="t-caption t-tabular" style={{ marginTop:5, opacity:.8 }}>{n.date}</div>
                </div>
                {n.unread && <span aria-label="unread" style={{ width:7, height:7, borderRadius:99,
                  background:'var(--accent)', marginTop:6 }}/>}
              </div>
            </Card>)}
      </section>
    </Body>
  </>;
}

function LicencesScreen({ go }) {
  const A = window.AL;
  return <>
    <AppBar title="Licences" back onBack={()=>go(null)} hour={false}/>
    <Body pad={16} gap={14}>
      <Prose size="small">
        <p>Astrolabe is AGPL-3.0. Every asset in it — including her artwork — ships in a public
          repository, so anything that cannot be published cannot be in the app.</p>
      </Prose>
      <Card>
        {A.licences.map((l,i) => <DataRow key={i} label={l.name} value={l.licence} small/>)}
      </Card>
      <Card tone="inset">
        <div className="t-eyebrow" style={{ marginBottom:8 }}>Versions</div>
        {A.licences.map((l,i) => <DataRow key={i} label={l.name} value={l.version} small tone="faint"/>)}
      </Card>
      <ListGroup>
        <ListRow label="The full AGPL-3.0 text" onClick={()=>{}}/>
        <ListRow label="Source for this build" description="ShrutiVtuber/astrolabe · 1.0.0 (214)" href="#" external/>
      </ListGroup>
    </Body>
  </>;
}

function PlacePickerScreen({ s, go }) {
  const A = window.AL;
  const [q, setQ] = React.useState('Athens');
  const results = A.places.filter(p => (p.name + p.region).toLowerCase().includes(q.toLowerCase()));
  return <>
    <AppBar title="Place" back onBack={()=>go(null)} hour={false}/>
    <div style={{ padding:'0 16px 12px', flex:'none' }}>
      <TextField placeholder="Search for a city" value={q} onChange={e=>setQ(e.target.value)}
        prefix={<Icon name="search" size={18} tone="faint"/>}/>
    </div>
    <Body pad={16} gap={14}>
      <Card tone="inset">
        <div className="t-caption" style={{ lineHeight:1.6 }}>
          The place decides sunrise, sunset and the planetary hours. It is stored on this phone and
          never sent anywhere.
        </div>
      </Card>
      {s.loading && <Refreshing/>}
      {!s.loading && (results.length === 0
        ? <EmptyState compact mark={A.G.saturn} title={'Nothing called “' + q + '”'}
            body="Try the local spelling, or the nearest larger city — the hours will be within a minute or two."
            action={<Button size="sm" variant="outlined">Enter coordinates instead</Button>}/>
        : <ListGroup>
            {results.map(p => <ListRow key={p.id} label={p.name} description={p.region + ' · ' + p.coords}
              value={p.tz} onClick={()=>{ s.set('place', p.name + ', ' + p.region.split(',').pop().trim()); go(null); }}/>)}
          </ListGroup>)}
      <div style={{ display:'grid', gap:8 }}>
        <span className="t-eyebrow">Recent</span>
        <ListGroup>
          <ListRow label="Athens, Greece" value="GMT+3" onClick={()=>go(null)}/>
          <ListRow label="Thessaloniki, Greece" value="GMT+3" onClick={()=>go(null)}/>
        </ListGroup>
      </div>
      <ListGroup>
        <ListRow label="Use my location" description="Asked once, kept on this phone"
          leading={<Icon name="my_location" size={20} tone="accent"/>} chevron={false} onClick={()=>{}}/>
      </ListGroup>
    </Body>
  </>;
}

function SkyDrawer({ s, onClose }) {
  const A = window.AL;
  return <Dialog size="fullscreen" title="Sky drawer" subtitle="Ephemeris · September 2026 · Athens"
    onClose={onClose}>
    <div style={{ display:'grid', gap:12 }}>
      <ChipRow>
        <Chip kind="choice" selected>September</Chip>
        <Chip kind="choice">October</Chip>
        <Chip kind="choice">November</Chip>
        <Chip kind="filter">Show ℞ only</Chip>
      </ChipRow>
      <DataTable columns={A.stations.columns} rows={A.stations.rows} zebra
        caption="Geocentric, apparent · 00:00 Athens · tropical"/>
      <div style={{ display:'grid', gap:10, gridTemplateColumns:'1fr' }}>
        <Card>
          <div className="t-eyebrow" style={{ marginBottom:10 }}>The month, drawn</div>
          <ChartWheel mode="period" size={240} span="1–30 Sep" housesKnown={false}
            bodies={A.bodies.slice(0,6)}
            phases={Array.from({length:10},(_,i)=>({ lon:i*36+12, phase:(i/10+0.35)%1 }))}/>
        </Card>
      </div>
      <Provenance rule="Tropical zodiac, apparent positions, 00:00 Athens"/>
    </div>
  </Dialog>;
}
Object.assign(window, { WorkScreen, WriteScreen, AccountScreen, NotificationsScreen,
  LicencesScreen, PlacePickerScreen, SkyDrawer });
