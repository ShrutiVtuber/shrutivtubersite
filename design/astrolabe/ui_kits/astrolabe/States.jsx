/* The ordered states document: every screen, in every state that applies to it,
   rendered from the same components as the interactive kit. */
const FRAMES = [
  ['1 · Home', 'home', {}, 'Signed in, not live, online'],
  ['1 · Home', 'home', { live:true }, 'Live — the plate warms, the hem and tab bar go rose'],
  ['1 · Home', 'home', { art:true }, 'Her portrait present'],
  ['1 · Home', 'home', { loading:true }, 'Loading — her half only; the sky is already computed'],
  ['1 · Home', 'home', { offline:true }, 'Offline — instruments intact, her half out of reach'],
  ['1 · Home', 'home', { error:true }, 'Error — the site answered badly'],
  ['1 · Home', 'home', { empty:true }, 'Empty — nothing written this week, no offers open'],
  ['1 · Home', 'home', { signedIn:false }, 'Signed out'],
  ['1 · Home', 'home', { member:true }, 'Member — the locked offer opens'],
  ['1 · Home', 'home', { missing:true }, 'Missing content — a reading with no opening line'],

  ['2 · Sky · Stations', 'sky', { seg:'stations' }, 'The month, dense, with ℞ printed'],
  ['2 · Sky · Stations', 'sky', { seg:'stations', offline:true }, 'Offline — unchanged, and it says so'],
  ['3 · Sky · Hours', 'sky', { seg:'hours' }, 'The twelve day hours, current hour washed'],
  ['3 · Sky · Hours', 'sky', { seg:'hours', sunrise:'civil' }, 'Civil-dawn convention in force'],
  ['4 · Sky · Coming', 'sky', { seg:'coming' }, 'Forty days ahead'],
  ['4 · Sky · Coming', 'sky', { seg:'coming', empty:true }, 'Empty — a quiet sky is not an error'],

  ['5 · Chart · form', 'chart', {}, 'Before casting'],
  ['5 · Chart · form', 'chart', { noBirthTime:true }, 'Birth time unknown — the time field stands down'],
  ['5 · Chart · form', 'chart', { longContent:true }, 'A forty-character name'],
  ['5 · Chart · form', 'chart', { error:true }, 'Error — the place could not be resolved'],
  ['6 · Chart · result', 'chart', { cast:true }, 'The wheel, houses known'],
  ['6 · Chart · result', 'chart', { cast:true, noBirthTime:true }, 'Angles undefined — no house ring, and the app says why'],

  ['7 · Letters · Reckoning', 'letters', { seg:'reckoning' }, 'Greek Milesian, letter by letter'],
  ['8 · Letters · Sigil', 'letters', { seg:'sigil' }, 'The figure drawn on the rose cross'],
  ['8 · Letters · Sigil', 'letters', { seg:'sigil', empty:true }, 'Cannot compute — nothing left to draw'],

  ['9 · Practice · Read', 'practice', { seg:'read' }, 'The feed'],
  ['9 · Practice · Read', 'practice', { seg:'read', signedIn:false }, 'Signed out — votes visible, not operable'],
  ['9 · Practice · Read', 'practice', { seg:'read', loading:true }, 'Loading — skeletons shaped like work cards'],
  ['9 · Practice · Read', 'practice', { seg:'read', empty:true }, 'Empty — the room is quiet'],
  ['9 · Practice · Read', 'practice', { seg:'read', offline:true }, 'Offline — drafts still kept'],
  ['10 · Practice · Mine', 'practice', { seg:'mine' }, 'Draft, posted and corrected'],
  ['10 · Practice · Mine', 'practice', { seg:'mine', signedIn:false }, 'Signed out'],
  ['10 · Practice · Mine', 'practice', { seg:'mine', empty:true }, 'Nothing written yet'],

  ['11 · One work', 'work', {}, 'Readings, votes, comments — hers marked'],
  ['11 · One work', 'work', { signedIn:false }, 'Signed out — no vote, no comment box'],
  ['11 · One work', 'work', { longContent:true }, 'A 2,000-word reading'],

  ['12 · Write', 'write', {}, 'The writing screen'],
  ['12 · Write', 'write', { longContent:true }, 'Long title and long body'],
  ['12 · Write', 'write', { offline:true }, 'Offline — it becomes a draft'],
  ['12 · Write', 'write', { error:true, signedIn:false }, 'Error, and signed out'],

  ['13 · Settings', 'settings', {}, 'Signed in, free'],
  ['13 · Settings', 'settings', { member:true }, 'Member'],
  ['13 · Settings', 'settings', { loading:true }, 'A language pack downloading'],
  ['13 · Settings', 'settings', { error:true }, 'A pack that did not finish'],

  ['14 · Account', 'account', { signedIn:false }, 'Signed out — the sign-in half'],
  ['14 · Account', 'account', { signedIn:false, error:true }, 'Sign-in failed'],
  ['14 · Account', 'account', {}, 'Signed in, free'],
  ['14 · Account', 'account', { member:true }, 'Member'],
  ['14 · Account', 'account', { confirmDelete:true }, 'The delete confirm'],

  ['15 · Notifications', 'notifications', {}, 'Switches and recent'],
  ['15 · Notifications', 'notifications', { empty:true }, 'Nothing yet'],
  ['15 · Notifications', 'notifications', { signedIn:false }, 'Signed out — replies unavailable'],

  ['16 · Licences', 'licences', {}, 'AGPL-3.0 and every dependency'],

  ['17 · Place picker', 'place', {}, 'Search and choose'],
  ['17 · Place picker', 'place', { loading:true }, 'Searching'],

  ['18 · Sky drawer', 'drawer', {}, 'The ephemeris as reference, full screen']
];

function Frame({ title, note, screen, over }) {
  const base = { live:false, offline:false, loading:false, empty:false, error:false, signedIn:true,
    member:false, longContent:false, missing:false, noBirthTime:false, art:false, reduceMotion:false,
    place:'Athens, Greece', sunrise:'limb', hour:'venus', confirmDelete:false };
  const [st, setSt] = React.useState({ ...base, ...over });
  const s = { ...st, set:(k,v)=>setSt(p=>({ ...p, [k]:v })) };
  const seg = over.seg;
  const go = () => {};
  const noop = () => {};
  let inner;
  switch (screen) {
    case 'home': inner = <HomeScreen s={s} go={go}/>; break;
    case 'sky': inner = <SkyScreen s={s} seg={seg} setSeg={noop} go={go}/>; break;
    case 'chart': inner = <ChartScreen s={s} cast={!!over.cast} setCast={noop} go={go}/>; break;
    case 'letters': inner = <LettersScreen s={s} seg={seg} setSeg={noop}/>; break;
    case 'practice': inner = <PracticeScreen s={s} seg={seg} setSeg={noop} go={go}/>; break;
    case 'settings': inner = <SettingsScreen s={s} go={go}/>; break;
    case 'work': inner = <WorkScreen s={s} go={go}/>; break;
    case 'write': inner = <WriteScreen s={s} go={go}/>; break;
    case 'account': inner = <AccountScreen s={s} go={go}/>; break;
    case 'notifications': inner = <NotificationsScreen s={s} go={go}/>; break;
    case 'licences': inner = <LicencesScreen go={go}/>; break;
    case 'place': inner = <PlacePickerScreen s={s} go={go}/>; break;
    case 'drawer': inner = <><HomeScreen s={s} go={go}/><SkyDrawer s={s} onClose={noop}/></>; break;
    default: inner = null;
  }
  const showTabs = ['home','sky','chart','letters','practice','settings','drawer'].includes(screen);
  const active = screen === 'drawer' ? 'home' : screen;
  return (
    <figure style={{ margin:0, display:'grid', gap:10, justifyItems:'start' }}>
      <figcaption style={{ display:'grid', gap:3, maxWidth:360 }}>
        <span style={{ font:'600 11px/1 var(--font-body)', letterSpacing:'.13em',
          textTransform:'uppercase', color:'var(--gilt)' }}>{title}</span>
        <span style={{ font:'400 13px/1.45 var(--font-body)', color:'var(--faint)', textWrap:'pretty' }}>{note}</span>
      </figcaption>
      <div data-live={st.live?'true':undefined} data-hour={st.hour} style={{ width:360, height:800,
        position:'relative', display:'flex', flexDirection:'column', background:'var(--page)',
        borderRadius:30, border:'1px solid var(--line-strong)', overflow:'hidden',
        boxShadow:'0 18px 48px -18px rgba(0,0,0,.65)' }}>
        <StatusBar live={st.live}/>
        {inner}
        {showTabs && <TabBar active={active} badges={{ practice:2 }} onChange={noop}/>}
      </div>
    </figure>
  );
}

function StatesDoc() {
  const groups = [];
  FRAMES.forEach(f => {
    const g = groups.find(x => x.title === f[0]);
    (g || groups[groups.push({ title:f[0], items:[] }) - 1]).items.push(f);
  });
  return (
    <div style={{ padding:'32px 28px 80px', display:'grid', gap:44 }}>
      <header style={{ display:'grid', gap:10, maxWidth:'62ch' }}>
        <span style={{ font:'600 11px/1 var(--font-body)', letterSpacing:'.14em',
          textTransform:'uppercase', color:'var(--faint)' }}>Astrolabe · the whole app</span>
        <h1 style={{ margin:0, font:'500 38px/1.1 var(--font-display)', color:'var(--ink)',
          letterSpacing:'-0.012em' }}>Every screen, every state</h1>
        <p style={{ margin:0, font:'400 16px/1.6 var(--font-body)', color:'var(--soft)', textWrap:'pretty' }}>
          Eighteen screens at 360 × 800, in the states the addendum asks for: loading, empty,
          offline, error, signed out, live, member, long content and missing content. Frames are
          live components, not images — the interactive version, with a large-phone size, is in
          <a href="index.html" style={{ marginLeft:4 }}>index.html</a>.
        </p>
        <div className="rule" style={{ maxWidth:420 }}>{'\u263E\ufe0e'}</div>
      </header>
      {groups.map(g => (
        <section key={g.title} style={{ display:'grid', gap:16 }}>
          <h2 style={{ margin:0, font:'600 22px/1.25 var(--font-display)', color:'var(--ink)' }}>{g.title}</h2>
          <div style={{ display:'flex', gap:28, flexWrap:'wrap' }}>
            {g.items.map((f,i) => <Frame key={i} title={f[0]} screen={f[1]} over={f[2]} note={f[3]}/>)}
          </div>
        </section>
      ))}
    </div>
  );
}
Object.assign(window, { StatesDoc, Frame, FRAMES });
