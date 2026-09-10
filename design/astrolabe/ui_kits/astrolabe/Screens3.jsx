/* Screens 9–10, 13: Practice (Read and Mine) and Settings. */

function PracticeScreen({ s, seg, setSeg, go }) {
  const A = window.AL;
  const [filter, setFilter] = React.useState('new');
  if (!s.signedIn && seg === 'mine') seg = 'read';
  return <>
    <AppBar title="Practice" large hour
      actions={<IconButton icon="edit_square" label="Write a reading" onClick={()=>go('write')}/>}/>
    <div style={{ padding:'0 12px 10px', flex:'none', display:'grid', gap:10 }}>
      <SegmentedControl label="Practice view" active={seg} onChange={setSeg}
        segments={[{id:'read',label:'Read'},{id:'mine',label:'Mine'}]}/>
      {seg === 'read' && <ChipRow>
        {[['new','Newest'],['unanswered','Unanswered'],['week','This week'],['mine-sign','My sign']].map(([id,lab])=>
          <Chip key={id} kind="filter" selected={filter===id} onClick={()=>setFilter(filter===id?'':id)}>{lab}</Chip>)}
      </ChipRow>}
    </div>
    <Body pad={12} gap={10}>
      {s.offline && <Banner tone="offline" title="The room is not reachable">
        Readings you have already opened are still here. Anything you write is kept as a draft and
        posted when you are back.</Banner>}
      {s.loading && [0,1,2].map(i => <Card key={i}><Skeleton lines={2}/></Card>)}

      {!s.loading && seg === 'read' && (s.empty
        ? <EmptyState mark={A.G.saturn} title="The room is quiet"
            body="Nobody has posted a reading this week. Yours would be the first."
            action={<Button onClick={()=>go('write')}>Write one</Button>}/>
        : <>
          {A.feed.map(w => <WorkCard key={w.id} title={w.title} author={w.author} date={w.date}
            excerpt={s.missing && w.id==='w2' ? undefined : w.excerpt} votes={w.votes} myVote={w.myVote}
            comments={w.comments} sign={w.sign} onOpen={()=>go('work')}
            onVote={s.signedIn ? ()=>{} : undefined}/>)}
          {!s.signedIn && <Card tone="inset">
            <div className="t-caption" style={{ lineHeight:1.6 }}>
              You are reading as a guest. Sign in to vote, comment, or put your own reading in front
              of the room.
            </div>
            <div style={{ marginTop:10, display:'flex', gap:8 }}>
              <Button size="sm" onClick={()=>go('account')}>Sign in</Button>
              <Button size="sm" variant="text">What signing in gets me</Button>
            </div>
          </Card>}
        </>)}

      {!s.loading && seg === 'mine' && (!s.signedIn
        ? <EmptyState mark={A.G.mercury} title="Your work would live here"
            body="Drafts are kept on this phone. Posting one needs an account, because the room needs to know who wrote it."
            action={<Button onClick={()=>go('account')}>Sign in</Button>}
            secondary={<Button variant="text" onClick={()=>go('write')}>Write a draft first</Button>}/>
        : s.empty
        ? <EmptyState mark={A.G.moon} title="Nothing written yet"
            body="A reading here is a few hundred words on one chart. It does not have to be right."
            action={<Button onClick={()=>go('write')}>Write your first</Button>}/>
        : A.mine.map(w => <WorkCard key={w.id} mine title={w.title} date={w.date} excerpt={w.excerpt}
            votes={w.votes} comments={w.comments} status={w.status} onOpen={()=>go('work')}/>))}
    </Body>
  </>;
}

function SettingsScreen({ s, go }) {
  const A = window.AL;
  return <>
    <AppBar title="Settings" large hour={false}/>
    <Body pad={16} gap={16}>
      <ListGroup>
        <ListRow label="Account" description={s.signedIn ? 'soror@shrutivtuber.com' : 'Not signed in'}
          value={s.signedIn ? (s.member ? 'Member' : 'Free') : undefined} onClick={()=>go('account')}/>
        <ListRow label="Notifications" value={s.signedIn ? '3 on' : 'Live only'} onClick={()=>go('notifications')}/>
      </ListGroup>

      <section style={{ display:'grid', gap:8 }}>
        <span className="t-eyebrow">The sky, where you are</span>
        <ListGroup>
          <ListRow label="Place" description="Used for sunrise, sunset and the hours" value={s.place}
            onClick={()=>go('place')}/>
          <ListRow label="Sunrise convention" description="Which moment starts the day"
            value={s.sunrise === 'civil' ? 'Civil dawn' : 'Upper limb'} onClick={()=>go('sunrise')}/>
          <ListRow label="Zodiac" value="Tropical" onClick={()=>{}}/>
          <ListRow label="Show times in" value="Athens and yours" onClick={()=>{}}/>
        </ListGroup>
      </section>

      <section style={{ display:'grid', gap:8 }}>
        <span className="t-eyebrow">On this phone</span>
        <Card pad={0}>
          <div style={{ padding:'4px 16px' }}>
            <Switch label="Reduce motion" description="Follows your system setting unless you change it here"
              checked={s.reduceMotion} onChange={v=>s.set('reduceMotion', v)}/>
            <div style={{ borderTop:'1px solid var(--line)' }}/>
            <Switch label="Keep readings offline" description="About 4 MB. They are already downloaded."
              checked onChange={()=>{}}/>
          </div>
        </Card>
        <ChipRow>
          <Chip kind="meta" meta="2.1 MB">Greek</Chip>
          <Chip kind="meta" meta="1.8 MB">Devanagari</Chip>
          <Chip kind="meta" meta="1.4 MB">Hebrew</Chip>
          <Chip kind="meta" meta="0.9 MB">Coptic</Chip>
        </ChipRow>
        {s.loading && <div style={{ display:'grid', gap:6 }}>
          <Progress kind="bar" value={62} label="Greek pack"/>
          <span className="t-caption">Greek pack · 1.3 of 2.1 MB</span>
        </div>}
        {s.error && <Banner tone="error" title="The Hebrew pack did not finish" action="Try again">
          1.1 of 1.4 MB arrived. Nothing else was affected.</Banner>}
        {s.empty && <Banner tone="note" title="No packs installed">
          Reckoning works in Greek and English without a pack.</Banner>}
      </section>

      <section style={{ display:'grid', gap:8 }}>
        <span className="t-eyebrow">Hers</span>
        <ListGroup>
          <ListRow label="Support her work" description="Opens your browser" href="https://shrutivtuber.com/support" external/>
          <ListRow label="The shop" href="https://shrutivtuber.com/shop" external/>
          <ListRow label="Classes" href="https://shrutivtuber.com/classes" external/>
          <ListRow label="shrutivtuber.com" href="https://shrutivtuber.com" external/>
        </ListGroup>
        <p className="t-caption" style={{ margin:'0 4px' }}>
          Nothing is bought inside Astrolabe. These open your browser, where the address bar says
          whose checkout it is.
        </p>
      </section>

      <section style={{ display:'grid', gap:8 }}>
        <span className="t-eyebrow">About</span>
        <ListGroup>
          <ListRow label="Licences" description="AGPL-3.0 · every asset ships in the public repo"
            onClick={()=>go('licences')}/>
          <ListRow label="Source" description="ShrutiVtuber/astrolabe" href="#" external/>
        </ListGroup>
        <div style={{ padding:'2px 4px' }}>
          <DataRow label="Astrolabe" value="1.0.0 (214)" small tone="faint"/>
          <DataRow label="Ephemeris" value="Swiss Ephemeris 2.10.03" small tone="faint"/>
        </div>
        <div className="rule" style={{ marginTop:6 }}>{A.G.moon}{'\ufe0e'}</div>
      </section>
    </Body>
  </>;
}
Object.assign(window, { PracticeScreen, SettingsScreen });
