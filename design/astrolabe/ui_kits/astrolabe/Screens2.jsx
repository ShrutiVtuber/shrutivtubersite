/* Screens 5–8: Chart (form and result), Letters (reckoning and sigil). */

function ChartScreen({ s, cast, setCast, go }) {
  const A = window.AL;
  const known = !s.noBirthTime;
  if (!cast) return <>
    <AppBar title="Cast a chart" hour={false}/>
    <Body pad={16} gap={16}>
      {s.error && <Banner tone="error" title="That place could not be resolved" action="Choose from the list"
        onAction={()=>go('place')}>The name matched four places and none of them was obvious.</Banner>}
      <div style={{ display:'grid', gap:14 }}>
        <TextField label="Name" placeholder="Whose chart is this?" defaultValue={s.longContent?'Anastasía Papadopoúlou-Georgiádis':''}/>
        <TextField label="Date of birth" mono placeholder="14 · 03 · 1996"/>
        <TextField label="Time of birth" mono placeholder="14:05" disabled={!known}
          helper={known ? 'Local clock time at the place of birth.' : 'Left unknown — the angles will not be reckoned.'}/>
        <ChoiceRow type="checkbox" label="The time of birth is unknown"
          rule="The chart is still cast. The ascendant, the midheaven and the houses are not."
          checked={!known} onChange={()=>s.set('noBirthTime', known)}/>
        <ListGroup>
          <ListRow label="Place of birth" value={s.place} onClick={()=>go('place')}/>
          <ListRow label="Zodiac" value="Tropical" onClick={()=>{}}/>
          <ListRow label="Houses" value={known ? 'Whole sign' : 'Not reckoned'} disabled={!known} onClick={()=>{}}/>
        </ListGroup>
      </div>
      <Card tone="inset">
        <div className="t-eyebrow" style={{ marginBottom:8 }}>Two authorities, two charts</div>
        <div className="t-caption" style={{ lineHeight:1.6 }}>
          Tropical and sidereal disagree by about 24° and neither is a setting you should have to
          find. Change it here, on the chart, and it recomputes.
        </div>
      </Card>
      <Button size="lg" full onClick={()=>setCast(true)} loading={s.loading}>Cast the chart</Button>
      {s.empty && <EmptyState compact mark={A.G.mercury} title="No saved charts"
        body="Charts you cast are kept on this phone until you delete them."/>}
    </Body>
  </>;

  return <>
    <AppBar title="Anastasía" subtitle={`14 March 1996 · ${known ? '14:05' : 'time unknown'} · ${s.place}`}
      back onBack={()=>setCast(false)} hour={false}
      actions={<><IconButton icon="ios_share" label="Share this chart"/>
        <IconButton icon="bookmark" label="Save this chart"/></>}/>
    <Body pad={12} gap={14}>
      {!known && <Banner tone="caution" title="The angles are not reckoned">
        With no birth time there is no ascendant and no midheaven, so this wheel has no houses.
        Everything drawn here is true; the things that are missing are missing on purpose.</Banner>}
      <div style={{ padding:'4px 0 0' }}>
        <ChartWheel size={300} asc={214.3} mc={128.9} cusps={known ? A.cusps : undefined}
          housesKnown={known} bodies={A.bodies} aspects={A.aspects}/>
      </div>
      <ChipRow>
        <Chip kind="choice" selected>Tropical</Chip>
        <Chip kind="choice">Sidereal · Lahiri</Chip>
        <Chip kind="choice" disabled={!known}>Whole sign</Chip>
        <Chip kind="choice" disabled={!known}>Placidus</Chip>
      </ChipRow>
      <Card>
        <div className="t-eyebrow" style={{ marginBottom:8 }}>Positions</div>
        {A.chartTable.map((r,i) => <DataRow key={i} mark={r.mark} label={r.label} value={r.value}
          tone={r.rose ? 'rose' : 'ink'}/>)}
        <div style={{ marginTop:10, paddingTop:10, borderTop:'1px solid var(--line)' }}>
          <DataRow label="Ascendant" value={known ? '04\u00b0 18\u2032 \u264F' : 'Not reckoned'}
            tone={known ? 'ink' : 'faint'}/>
          <DataRow label="Midheaven" value={known ? '08\u00b0 54\u2032 \u264C' : 'Not reckoned'}
            tone={known ? 'ink' : 'faint'}/>
        </div>
      </Card>
      <Card>
        <div className="t-eyebrow" style={{ marginBottom:8 }}>Aspects</div>
        <DataRow mark={A.G.sun} label="Sun opposite Saturn" value="3\u00b0 06\u2032 \u00b7 separating"/>
        <DataRow mark={A.G.moon} label="Moon trine Venus" value="1\u00b0 12\u2032 \u00b7 applying"/>
        <DataRow mark={A.G.venus} label="Venus square Uranus" value="2\u00b0 00\u2032 \u00b7 applying"/>
        <DataRow mark={A.G.mercury} label="Mercury sextile Jupiter" value="2\u00b0 48\u2032 \u00b7 separating"/>
      </Card>
      <Provenance rule={known ? 'Tropical zodiac, whole-sign houses' : 'Tropical zodiac, no houses reckoned'}/>
    </Body>
  </>;
}

const SCRIPTS = ['Greek','Hebrew','Arabic','Coptic','Devanagari','English'];

function LettersScreen({ s, seg, setSeg }) {
  const A = window.AL;
  const [script, setScript] = React.useState('Greek');
  const [method, setMethod] = React.useState('rose');
  const kata = script === 'Devanagari';
  const sum = A.isopsephy.reduce((n,r)=>n+r.v,0);
  return <>
    <AppBar title="Letters" hour/>
    <div style={{ padding:'0 12px 10px', flex:'none' }}>
      <SegmentedControl label="Letters view" active={seg} onChange={setSeg}
        segments={[{id:'reckoning',label:'Reckoning'},{id:'sigil',label:'Sigil'}]}/>
    </div>
    <Body pad={12} gap={13}>
      {seg === 'reckoning' && <>
        <ChipRow>
          {SCRIPTS.map(x => <Chip key={x} kind="choice" selected={script===x} onClick={()=>setScript(x)}>{x}</Chip>)}
        </ChipRow>
        <TextField label="Word or phrase" mono defaultValue={kata ? '\u0915\u091f\u092a\u092f\u093e\u0926\u093f' : '\u03a3\u03bf\u03c6\u03af\u03b1'}
          helper={kata ? 'Kaṭapayādi is place-value, so this is read right to left.' : 'Greek Milesian, with digamma, koppa and sampi.'}/>
        {kata
          ? <Card tone="warning">
              <div style={{ display:'flex', gap:9, alignItems:'flex-start' }}>
                <Glyph char={A.G.mercury} tone="rose" size="md"/>
                <div>
                  <div style={{ font:'600 var(--size-label)/1.35 var(--font-body)', color:'var(--rose)' }}>
                    There is no sum to give you</div>
                  <div className="t-caption" style={{ marginTop:4, lineHeight:1.6 }}>
                    Kaṭapayādi is a place-value notation, not a gematria. The app gives the digits,
                    read right to left, and refuses to add them — a Greek sum and a Devanagari
                    reading of equal value are not a correspondence.</div>
                </div>
              </div>
            </Card>
          : <CodeBlock label={script + ' \u00b7 letter by letter'} align="right" copyable>
              {A.isopsephy.map(r => r.ch + '   ' + String(r.v).padStart(4,' ')).join('\n')
                + '\n\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n    ' + sum}
            </CodeBlock>}
        {!kata && <Card>
          <DataRow label="Total" value={String(sum)} tone="gilt"/>
          <DataRow label="Digital root" value="7"/>
          <DataRow label="Matches in this system" value="4 words"/>
        </Card>}
        <Provenance engine="Isopsephy tables 1.2" rule={kata ? 'Kaṭapayādi, place-value, right to left'
          : 'Milesian, finals unvalued'} extra={<DataRow label="Matching" value="Within one system only" small tone="faint"/>}/>
      </>}

      {seg === 'sigil' && <>
        <TextField label="Statement of intent" multiline rows={3}
          defaultValue="It is my will to finish the ephemeris before the equinox"
          helper="Repeated letters are struck out before the figure is drawn."/>
        <div style={{ display:'flex', gap:8 }}>
          {[['rose','Rose cross'],['kamea','Kamea'],['letters','Letter path']].map(([id,lab]) =>
            <Chip key={id} kind="choice" selected={method===id} onClick={()=>setMethod(id)}>{lab}</Chip>)}
        </div>
        <Card tone="inset" pad={12}>
          {s.empty
            ? <EmptyState compact mark={A.G.saturn} title="Nothing left to draw"
                body="Every letter in that statement repeats. Strike fewer, or write it another way."/>
            : <SigilPlate method={method}/>}
        </Card>
        <div style={{ display:'flex', gap:10 }}>
          <Button variant="outlined" full iconLeft={<Icon name="download" size={18} tone="accent"/>}>Save as SVG</Button>
          <Button variant="outlined" full iconLeft={<Icon name="ios_share" size={18} tone="accent"/>}>Share</Button>
        </div>
        <Provenance engine="Sigil generator 1.0" rule={method==='rose' ? 'Rose cross, Latin ring'
          : method==='kamea' ? 'Kamea of Saturn, 3×3' : 'Letter path, struck repeats'}/>
      </>}
    </Body>
  </>;
}

/* The sigil is the instrument's own output — a figure drawn over the chosen
   grid, not artwork. Kamea and letter-path draw a real polyline; the rose cross
   is a ring with the path chorded across it. */
function SigilPlate({ method }) {
  const pts = { kamea:[[1,0],[2,2],[0,1],[2,0],[1,2],[0,0],[2,1]],
    letters:[[0,0],[2,1],[1,2],[0,2],[2,0],[1,1]] }[method];
  const size = 240, m = 34, step = (size - m*2)/2;
  const xy = ([c,r]) => [m + c*step, m + r*step];
  if (method === 'rose') {
    const cx = size/2, r1 = 96, r2 = 74;
    const ring = Array.from({length:22},(_,i)=>{
      const a = (i/22)*2*Math.PI - Math.PI/2;
      return [cx + r1*Math.cos(a), cx + r1*Math.sin(a)];
    });
    const path = [0,7,3,15,11,19,2].map(i=>ring[i]);
    return <svg viewBox={`0 0 ${size} ${size}`} width="100%" style={{ maxWidth:size, display:'block', margin:'0 auto' }}
      role="img" aria-label="Sigil drawn on the rose cross">
      <circle cx={cx} cy={cx} r={r1} fill="none" stroke="var(--gilt-dim)" strokeWidth="1"/>
      <circle cx={cx} cy={cx} r={r2} fill="none" stroke="var(--line)" strokeWidth="1"/>
      {ring.map(([x,y],i)=><circle key={i} cx={x} cy={y} r="2" fill="var(--line-strong)"/>)}
      <polyline points={path.map(p=>p.join(',')).join(' ')} fill="none" stroke="var(--gilt)"
        strokeWidth="1.8" strokeLinejoin="round" strokeLinecap="round"/>
      <circle cx={path[0][0]} cy={path[0][1]} r="4" fill="none" stroke="var(--gilt-bright)" strokeWidth="1.6"/>
      <rect x={path[path.length-1][0]-4} y={path[path.length-1][1]-4} width="8" height="8"
        fill="none" stroke="var(--gilt-bright)" strokeWidth="1.6"/>
    </svg>;
  }
  return <svg viewBox={`0 0 ${size} ${size}`} width="100%" style={{ maxWidth:size, display:'block', margin:'0 auto' }}
    role="img" aria-label={'Sigil drawn on the ' + method + ' grid'}>
    {[0,1,2].map(r=>[0,1,2].map(c=>{
      const [x,y] = xy([c,r]);
      return <circle key={r+'-'+c} cx={x} cy={y} r="2.5" fill="var(--line-strong)"/>;
    }))}
    {method==='kamea' && [0,1,2].map(i=><g key={i}>
      <line x1={m} y1={m+i*step} x2={size-m} y2={m+i*step} stroke="var(--line)" strokeWidth="0.8"/>
      <line x1={m+i*step} y1={m} x2={m+i*step} y2={size-m} stroke="var(--line)" strokeWidth="0.8"/>
    </g>)}
    <polyline points={pts.map(p=>xy(p).join(',')).join(' ')} fill="none" stroke="var(--gilt)"
      strokeWidth="2" strokeLinejoin="round" strokeLinecap="round"/>
    <circle {...(()=>{const [x,y]=xy(pts[0]);return {cx:x,cy:y};})()} r="5" fill="none"
      stroke="var(--gilt-bright)" strokeWidth="1.6"/>
    {(()=>{const [x,y]=xy(pts[pts.length-1]);return <rect x={x-5} y={y-5} width="10" height="10"
      fill="none" stroke="var(--gilt-bright)" strokeWidth="1.6"/>;})()}
  </svg>;
}
Object.assign(window, { ChartScreen, LettersScreen, SigilPlate });
