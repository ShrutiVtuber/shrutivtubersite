/* Screens 1–4: Home, and the three Sky segments. */

function HomeScreen({ s, go }) {
  const A = window.AL;
  const live = s.live;
  const greeting = live ? 'She is live' : 'Good evening';
  const line = live ? 'Casting charts for the chat, since 20:04 Athens.'
    : 'A waxing gibbous moon, four days from full.';
  return <>
    <AppBar title="Astrolabe" hour actions={<>
      <IconButton icon="notifications" label="Notifications" badge={s.signedIn?2:undefined} onClick={()=>go('notifications')}/>
    </>}/>
    <Body pad={16} gap={16}>
      {s.offline && <Banner tone="offline" title="Her half is out of reach">
        The instruments all still work — they compute on your phone. Readings, offers and the
        practice room will come back when you do.</Banner>}
      {s.error && <Banner tone="error" title="The site answered badly" action="Try again" onAction={()=>{}}>
        Her readings could not be loaded. Everything below the sky line is still yours.</Banner>}

      <div style={{ display:'grid', gap:10 }}>
        <Masthead greeting={greeting} line={line} live={live}
          portrait={s.art ? '../../assets/reference-astrologer.jpeg' : undefined}
          fit="plate" portraitAlt=""/>
        <div style={{ display:'flex', gap:8, flexWrap:'wrap', alignItems:'center' }}>
          <HourChip ruler={s.hour} ordinal={7} diurnal ends="14:12" onClick={()=>go('sky','hours')}/>
          <span style={{ display:'inline-flex', alignItems:'center', gap:7 }}>
            <MoonDisc phase={0.38} size={22}/>
            <span className="t-caption" style={{ color:'var(--soft)' }}>Waxing gibbous</span>
          </span>
        </div>
      </div>

      <LiveBanner status={s.offline ? 'unknown' : live ? 'live' : 'offline'}
        title="Casting charts for the chat" game="Just Chatting" viewers={412}
        nextStream="Thursday 20:00 Athens" onOpen={()=>{}}/>

      <section>
        <SectionHeader eyebrow="From Shruti" title="Latest readings" action="All twelve" onAction={()=>{}}/>
        {s.loading ? <div style={{ display:'grid', gap:10 }}>
            {[0,1].map(i=><Card key={i}><Skeleton lines={2}/></Card>)}
          </div>
        : s.offline || s.error || s.empty ? <Card tone="plain" pad={0}>
            <EmptyState compact mark={A.G.moon} title={s.empty ? 'Nothing written yet this week' : 'Kept from last time'}
              body={s.empty ? 'She writes the twelve on Sunday night. They will be here when she has.'
                : 'These are the readings you already had. New ones arrive when her side is reachable.'}/>
          </Card>
        : <div style={{ display:'grid', gap:10 }}>
            {A.readings.slice(0, s.longContent?4:3).map(r =>
              <ContentCard key={r.id} kind="reading" sign={r.sign} signMark={r.mark} date={r.date}
                readingTime={r.time} unread={r.unread} excerpt={s.missing && r.id==='r1' ? undefined : r.excerpt}
                onOpen={()=>go('work')}/>)}
          </div>}
      </section>

      <section>
        <SectionHeader eyebrow="Longer" title="Latest articles" action="All" onAction={()=>{}}/>
        <div style={{ display:'grid', gap:10 }}>
          {A.articles.slice(0,2).map(a =>
            <ContentCard key={a.id} kind="article" title={a.title} date={a.date} readingTime={a.time}
              excerpt={a.excerpt} onOpen={()=>go('work')}/>)}
        </div>
      </section>

      <section>
        <SectionHeader eyebrow="Hers" title="Offers" rule mark={A.G.sun}/>
        {s.empty ? <EmptyState compact mark={A.G.jupiter} title="Nothing open just now"
            body="Classes run in terms. The next one is announced on Discord first."/>
          : <div style={{ display:'grid', gap:10 }}>
            {A.offers.slice(0, 2).map(o =>
              <OfferCard key={o.id} title={o.title} body={o.body} price={o.price} cadence={o.cadence}
                mark={o.mark} membersOnly={o.membersOnly} locked={o.membersOnly && !s.member}
                soldOut={o.soldOut} href={o.href} onOpen={o.membersOnly && !s.member ? (e)=>{e.preventDefault();} : undefined}/>)}
          </div>}
      </section>

      <section style={{ display:'grid', gap:10 }}>
        <SectionHeader eyebrow="Elsewhere" title="Her site"/>
        <ListGroup>
          <ListRow label="shrutivtuber.com" description="Instruments for magick, built live from Athens."
            href="https://shrutivtuber.com" external/>
          <ListRow label="Watch on Twitch" href="https://twitch.tv" external
            leading={<img src="../../assets/icons/twitch.svg" alt="" width="18" height="18" style={{ opacity:.72 }}/>}/>
          <ListRow label="Discord" description="Streams are announced here first" href="#" external
            leading={<img src="../../assets/icons/discord.svg" alt="" width="18" height="18" style={{ opacity:.72 }}/>}/>
        </ListGroup>
        <p className="t-caption" style={{ margin:'2px 4px 0', color:'var(--faint)' }}>
          Support, the shop and classes open in your browser, where the address bar says whose they are.
        </p>
      </section>
    </Body>
  </>;
}

function SkyScreen({ s, seg, setSeg, go }) {
  const A = window.AL;
  return <>
    <AppBar title="Sky" subtitle={s.place} hour actions={
      <IconButton icon="menu_book" label="Sky drawer" onClick={()=>go('drawer')}/>}/>
    <div style={{ padding:'0 12px 10px', flex:'none' }}>
      <SegmentedControl label="Sky view" active={seg} onChange={setSeg}
        segments={[{id:'stations',label:'Stations'},{id:'hours',label:'Hours'},{id:'coming',label:'Coming'}]}/>
    </div>
    <Body pad={12} gap={12}>
      <DayArc sunrise="06:58" sunset="19:51" now="13:42" phase={0.38} ruler={s.hour}/>
      {s.offline && <Banner tone="note" title="Still computing, still correct">
        The sky does not need the network. Only her readings do.</Banner>}
      {s.loading && <Refreshing/>}

      {seg === 'stations' && <>
        <DataTable columns={A.stations.columns} rows={A.stations.rows}
          caption={`${s.place} · GMT+3 · geocentric, apparent · ${s.sunrise === 'civil' ? 'civil dawn' : 'sunrise'} convention`}/>
        <Card tone="warning">
          <div style={{ display:'flex', gap:9, alignItems:'flex-start' }}>
            <Glyph name="retrograde" tone="rose" size="md"/>
            <div>
              <div style={{ font:'600 var(--size-label)/1.35 var(--font-body)', color:'var(--rose)' }}>
                Mercury is retrograde until Thursday</div>
              <div className="t-caption" style={{ marginTop:3 }}>
                Every affected figure carries ℞ as well as the tint.</div>
            </div>
          </div>
        </Card>
        <Provenance rule="Tropical zodiac, apparent positions"/>
      </>}

      {seg === 'hours' && <>
        <Card>
          <div style={{ display:'grid', gap:12 }}>
            <HourChip ruler={s.hour} ordinal={7} diurnal ends="14:12"/>
            <DataRow mark={A.G.sun} label="Sunrise" value="06:58"/>
            <DataRow mark={A.G.sun} label="Sunset" value="19:51"/>
            <DataRow label="Day hour" value="62 minutes"/>
            <DataRow label="Night hour" value="58 minutes"/>
            <div style={{ paddingTop:8, borderTop:'1px solid var(--line)' }}>
              <button type="button" onClick={()=>go('sunrise')} style={{ appearance:'none', background:'none',
                border:0, padding:0, color:'var(--accent)', font:'500 var(--size-caption)/1 var(--font-body)',
                cursor:'pointer' }}>
                Sunrise convention: {s.sunrise === 'civil' ? 'civil dawn' : 'upper limb'} — change
              </button>
            </div>
          </div>
        </Card>
        <DataTable columns={A.hours.columns} rows={A.hours.rows} caption="Day hours · 9 September"/>
        <Provenance rule={s.sunrise === 'civil' ? 'Civil dawn: the Sun is 6° below the horizon'
          : 'Sunrise: the Sun’s upper limb clears the horizon'}/>
      </>}

      {seg === 'coming' && <>
        {s.empty ? <EmptyState mark={A.G.saturn} title="Nothing in the next forty days"
            body="The sky is quiet. That happens, and it is not an error."/>
          : <div style={{ display:'grid', gap:10 }}>
            {A.coming.map((c,i) => <Card key={i} tone={c.tone === 'caution' ? 'warning' : 'plain'}>
              <div style={{ display:'grid', gridTemplateColumns:'auto 1fr', gap:12, alignItems:'start' }}>
                <span style={{ display:'grid', placeItems:'center', width:34, height:34,
                  borderRadius:'var(--radius-full)', background:'var(--inset)',
                  border:'1px solid ' + (c.tone==='caution'?'color-mix(in srgb,var(--rose) 40%,transparent)':'var(--line)') }}>
                  <Glyph char={c.mark} tone={c.tone==='caution'?'rose':'gilt'} size="md"/>
                </span>
                <div style={{ minWidth:0 }}>
                  <div className="t-eyebrow" style={{ color: c.tone==='caution'?'var(--rose)':'var(--faint)' }}>{c.when}</div>
                  <div style={{ font:'500 17px/1.3 var(--font-display)', color:'var(--ink)', marginTop:4 }}>{c.title}</div>
                  <div className="t-caption" style={{ marginTop:3 }}>{c.detail}</div>
                </div>
              </div>
            </Card>)}
          </div>}
        <Provenance rule="Times in Athens, with your local conversion where they differ"/>
      </>}
    </Body>
  </>;
}
Object.assign(window, { HomeScreen, SkyScreen });
