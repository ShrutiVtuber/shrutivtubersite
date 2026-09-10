/* The Astrolabe kit shell: a phone, its six tabs, its pushed screens, and the
   switches that put every screen into every state the addendum asks for. */
const DEVICES = { small:{ w:360, h:800, name:'360 × 800' }, large:{ w:430, h:930, name:'430 × 930' } };
const HOURS = ['sun','moon','mars','mercury','jupiter','venus','saturn'];
const STATE_KEYS = [
  ['live','Live'], ['offline','Offline'], ['loading','Loading'], ['empty','Empty'],
  ['error','Error'], ['signedIn','Signed in'], ['member','Member'],
  ['longContent','Long content'], ['missing','Missing content'], ['noBirthTime','No birth time'],
  ['art','Her artwork present'], ['reduceMotion','Reduce motion']
];

function App() {
  const [device, setDevice] = React.useState('small');
  const [tab, setTab] = React.useState('home');
  const [pushed, setPushed] = React.useState(null);
  const [skySeg, setSkySeg] = React.useState('stations');
  const [lettersSeg, setLettersSeg] = React.useState('reckoning');
  const [practiceSeg, setPracticeSeg] = React.useState('read');
  const [cast, setCast] = React.useState(false);
  const [st, setSt] = React.useState({ live:false, offline:false, loading:false, empty:false,
    error:false, signedIn:true, member:false, longContent:false, missing:false, noBirthTime:false,
    art:false, reduceMotion:false, place:'Athens, Greece', sunrise:'limb', hour:'venus',
    confirmDelete:false });
  const s = { ...st, set:(k,v)=>setSt(p=>({ ...p, [k]:v })) };
  const d = DEVICES[device];

  const go = (dest, seg) => {
    if (dest === null) return setPushed(null);
    if (dest === 'sky') { setTab('sky'); if (seg) setSkySeg(seg); return setPushed(null); }
    if (dest === 'sunrise') return setPushed('sunrise');
    setPushed(dest);
  };

  const screen = () => {
    if (pushed === 'work') return <WorkScreen s={s} go={go}/>;
    if (pushed === 'write') return <WriteScreen s={s} go={go}/>;
    if (pushed === 'account') return <AccountScreen s={s} go={go}/>;
    if (pushed === 'notifications') return <NotificationsScreen s={s} go={go}/>;
    if (pushed === 'licences') return <LicencesScreen go={go}/>;
    if (pushed === 'place') return <PlacePickerScreen s={s} go={go}/>;
    switch (tab) {
      case 'sky': return <SkyScreen s={s} seg={skySeg} setSeg={setSkySeg} go={go}/>;
      case 'chart': return <ChartScreen s={s} cast={cast} setCast={setCast} go={go}/>;
      case 'letters': return <LettersScreen s={s} seg={lettersSeg} setSeg={setLettersSeg}/>;
      case 'practice': return <PracticeScreen s={s} seg={practiceSeg} setSeg={setPracticeSeg} go={go}/>;
      case 'settings': return <SettingsScreen s={s} go={go}/>;
      default: return <HomeScreen s={s} go={go}/>;
    }
  };

  return (
    <div style={{ display:'flex', gap:28, alignItems:'flex-start', flexWrap:'wrap',
      padding:24, minHeight:'100vh', boxSizing:'border-box' }}>
      <Controls {...{ device, setDevice, tab, setTab, pushed, setPushed, s, st, setSt, cast, setCast,
        skySeg, setSkySeg, lettersSeg, setLettersSeg, practiceSeg, setPracticeSeg }}/>
      <div style={{ display:'grid', gap:10, justifyItems:'center' }}>
        <Phone w={d.w} h={d.h} s={s}>
          <StatusBar live={s.live}/>
          {screen()}
          {!pushed && <TabBar active={tab} badges={s.signedIn?{ practice:2 }:{}}
            onChange={t=>{ setTab(t); setPushed(null); }}/>}
          {pushed === 'drawer' && <SkyDrawer s={s} onClose={()=>setPushed(null)}/>}
          <Sheet open={pushed === 'sunrise'} title="Sunrise convention" onClose={()=>setPushed(null)}
            actions={<Button full onClick={()=>setPushed(null)}>Done</Button>}>
            <p className="t-caption" style={{ margin:'0 0 6px', lineHeight:1.6 }}>
              Which moment begins the day. The two answers differ by about half an hour, and every
              planetary hour moves with them.</p>
            <ChoiceRow type="radio" label="Sunrise" rule="The Sun’s upper limb clears the horizon."
              checked={s.sunrise==='limb'} value="limb" onChange={()=>s.set('sunrise','limb')}/>
            <ChoiceRow type="radio" label="Civil dawn" rule="The Sun is 6° below the horizon."
              checked={s.sunrise==='civil'} value="civil" onChange={()=>s.set('sunrise','civil')}/>
            <p className="t-caption" style={{ margin:'8px 0 0', lineHeight:1.6, color:'var(--faint)' }}>
              Neither is the correct one. Pick the one your tradition uses.</p>
          </Sheet>
        </Phone>
        <span style={{ font:'400 11px/1 var(--font-body)', color:'var(--faint)',
          fontVariantNumeric:'tabular-nums' }}>{d.name}</span>
      </div>
    </div>
  );
}

function Phone({ w, h, s, children }) {
  return (
    <div data-live={s.live ? 'true' : undefined} data-hour={s.hour} style={{
      width:w, height:h, flex:'none', position:'relative', display:'flex', flexDirection:'column',
      background:'var(--page)', borderRadius:34, border:'1px solid var(--line-strong)',
      boxShadow:'0 24px 70px -20px rgba(0,0,0,.7)', overflow:'hidden',
      transition:'width var(--dur-2) var(--ease-out),height var(--dur-2) var(--ease-out)' }}>
      {s.reduceMotion && <style>{'*{animation-duration:1ms!important;transition-duration:1ms!important}'}</style>}
      {children}
    </div>
  );
}

function Controls(p) {
  const { s, st, setSt } = p;
  const box = { background:'var(--card)', border:'1px solid var(--line)',
    borderRadius:'var(--radius-md)', padding:14, display:'grid', gap:10 };
  const eyebrow = { font:'600 10px/1 var(--font-body)', letterSpacing:'.14em',
    textTransform:'uppercase', color:'var(--faint)' };
  const tabs = [['home','Home'],['sky','Sky'],['chart','Chart'],['letters','Letters'],
    ['practice','Practice'],['settings','Settings']];
  const pushes = [['work','One work'],['write','Write'],['account','Account'],
    ['notifications','Notifications'],['licences','Licences'],['place','Place picker'],
    ['drawer','Sky drawer'],['sunrise','Sunrise sheet']];
  return (
    <aside style={{ width:288, flex:'none', display:'grid', gap:12, position:'sticky', top:24 }}>
      <header style={{ display:'grid', gap:6 }}>
        <h1 style={{ margin:0, font:'500 26px/1.1 var(--font-display)', color:'var(--ink)',
          letterSpacing:'-0.012em' }}>Astrolabe</h1>
        <p style={{ margin:0, font:'400 13px/1.5 var(--font-body)', color:'var(--faint)' }}>
          Her companion app. Eighteen screens, every state.</p>
      </header>

      <div style={box}>
        <span style={eyebrow}>Tab</span>
        <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
          {tabs.map(([id,lab]) => <Chip key={id} kind="choice" selected={p.tab===id && !p.pushed}
            onClick={()=>{ p.setTab(id); p.setPushed(null); }}>{lab}</Chip>)}
        </div>
        {p.tab === 'sky' && !p.pushed && <>
          <span style={eyebrow}>Sky segment</span>
          <SegmentedControl active={p.skySeg} onChange={p.setSkySeg} label="Sky segment"
            segments={[{id:'stations',label:'Stations'},{id:'hours',label:'Hours'},{id:'coming',label:'Coming'}]}/>
        </>}
        {p.tab === 'letters' && !p.pushed && <>
          <span style={eyebrow}>Letters segment</span>
          <SegmentedControl active={p.lettersSeg} onChange={p.setLettersSeg} label="Letters segment"
            segments={[{id:'reckoning',label:'Reckoning'},{id:'sigil',label:'Sigil'}]}/>
        </>}
        {p.tab === 'practice' && !p.pushed && <>
          <span style={eyebrow}>Practice segment</span>
          <SegmentedControl active={p.practiceSeg} onChange={p.setPracticeSeg} label="Practice segment"
            segments={[{id:'read',label:'Read'},{id:'mine',label:'Mine'}]}/>
        </>}
        {p.tab === 'chart' && !p.pushed && <>
          <span style={eyebrow}>Chart</span>
          <SegmentedControl active={p.cast?'result':'form'} onChange={v=>p.setCast(v==='result')}
            label="Chart stage" segments={[{id:'form',label:'The form'},{id:'result',label:'The result'}]}/>
        </>}
      </div>

      <div style={box}>
        <span style={eyebrow}>Pushed and dialogs</span>
        <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
          {pushes.map(([id,lab]) => <Chip key={id} kind="choice" selected={p.pushed===id}
            onClick={()=>p.setPushed(p.pushed===id?null:id)}>{lab}</Chip>)}
        </div>
      </div>

      <div style={box}>
        <span style={eyebrow}>States</span>
        <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
          {STATE_KEYS.map(([k,lab]) => <Chip key={k} kind="filter" selected={!!st[k]}
            onClick={()=>setSt(prev=>({ ...prev, [k]:!prev[k] }))}>{lab}</Chip>)}
        </div>
      </div>

      <div style={box}>
        <span style={eyebrow}>Ruling hour</span>
        <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
          {HOURS.map(h => <Chip key={h} kind="choice" selected={s.hour===h}
            onClick={()=>s.set('hour',h)}>{h}</Chip>)}
        </div>
        <span style={eyebrow}>Device</span>
        <SegmentedControl active={p.device} onChange={p.setDevice} label="Device"
          segments={[{id:'small',label:'360 × 800'},{id:'large',label:'430 × 930'}]}/>
      </div>

      <p style={{ margin:0, font:'400 11px/1.6 var(--font-body)', color:'var(--faint)' }}>
        Sample data is plausible and internally consistent, not live computation. The reckoning a
        developer must write is described in the design system’s readme.
      </p>
      <div style={{ display:'grid', gap:6 }}>
        <a href="artwork.html" style={{ font:'500 13px/1.5 var(--font-body)' }}>Where your art goes →</a>
        <a href="states.html" style={{ font:'500 13px/1.5 var(--font-body)' }}>Every screen, every state →</a>
      </div>
    </aside>
  );
}
Object.assign(window, { App, Phone, Controls });
